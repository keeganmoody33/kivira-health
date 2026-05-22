from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.extract_from_search_snippets import parse_snippet  # noqa: E402
from scripts.spider_query_runner import (  # noqa: E402
    call_spider_search,
    load_env_local,
)
from tam_builder.josh_pilot.col4 import normalize_linkedin_url
from tam_builder.josh_pilot.constants import ENV_FILE, FIXTURE_DIR
from tam_builder.josh_pilot.message_lane import classify_message_lane
from tam_builder.persona_rules import tag_persona_keyword

SPIDER_SCRAPE_URL = "https://api.spider.cloud/scrape"
SCRAPE_TIMEOUT = 90
PROFILE_PHOTO_RE = re.compile(
    r"(profile-displayphoto|profile-picture|media\.licdn\.com/.*/profile|pv-top-card.*photo)",
    re.IGNORECASE,
)


def _load_apollo_urls(path: Path) -> dict[tuple[str, str], str]:
    """Merge key: (lower name, lower org) -> linkedin url."""
    if not path.exists():
        return {}
    out: dict[tuple[str, str], str] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (
                row.get("name")
                or row.get("contact_name")
                or row.get("Name")
                or ""
            ).strip()
            org = (
                row.get("organization_name")
                or row.get("org_name")
                or row.get("Company")
                or row.get("company")
                or ""
            ).strip()
            url = normalize_linkedin_url(
                row.get("linkedin_url")
                or row.get("linkedin_profile_url")
                or row.get("Person Linkedin Url")
                or ""
            )
            if name and url:
                out[(name.lower(), org.lower())] = url
    return out


def _discover_url_spider(name: str, org: str, api_key: str) -> tuple[str, str, str]:
    boolean = f'"{name}" "{org}"'
    results = call_spider_search(boolean, api_key, search_limit=5)
    if not results:
        return "", "", ""
    hit = results[0]
    return hit.linkedin_profile_url, hit.title, hit.snippet


def _scrape_profile(url: str, api_key: str) -> dict[str, str]:
    body = json.dumps(
        {
            "url": url,
            "request": "chrome",
            "return_format": "markdown",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        SPIDER_SCRAPE_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=SCRAPE_TIMEOUT) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
        return {"error": str(e)}

    content = raw
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            content = (
                data.get("content")
                or data.get("markdown")
                or data.get("data")
                or raw
            )
            if isinstance(content, list):
                content = "\n".join(str(x) for x in content)
        elif isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                content = first.get("content") or first.get("markdown") or raw
    except json.JSONDecodeError:
        pass

    if not isinstance(content, str):
        content = str(content)

    has_photo = bool(PROFILE_PHOTO_RE.search(content))
    # Headline often in first line or after name
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    headline = lines[0][:240] if lines else ""
    about = ""
    for i, ln in enumerate(lines):
        if ln.lower().startswith("about") and i + 1 < len(lines):
            about = " ".join(lines[i + 1 : i + 6])[:800]
            break

    return {
        "linkedin_headline": headline,
        "linkedin_about": about,
        "has_profile_photo": "true" if has_photo else "false",
        "scrape_chars": str(len(content)),
    }


def enrich_row(
    row: dict[str, str],
    *,
    api_key: str,
    apollo_index: dict[tuple[str, str], str],
    do_scrape: bool,
    sleep_s: float,
) -> dict[str, str]:
    row = dict(row)
    flags: list[str] = []

    url = normalize_linkedin_url(row.get("linkedin_profile_url") or "")
    if not url:
        url = normalize_linkedin_url(row.get("linkedin_profile_url_hint") or "")
    source = row.get("enrichment_source", "")

    if not url:
        key = (
            (row.get("contact_name") or "").lower().strip(),
            (row.get("org_name") or "").lower().strip(),
        )
        url = apollo_index.get(key, "")
        if url:
            source = "apollo_manual"
            flags.append("apollo_url")

    headline = row.get("linkedin_headline") or ""
    about = row.get("linkedin_about") or row.get("snippet_or_quote") or ""
    has_photo = (row.get("has_profile_photo") or "").lower() == "true"

    if not url and api_key and row.get("contact_name"):
        time.sleep(sleep_s)
        url, title_snip, snippet = _discover_url_spider(
            row.get("contact_name", ""),
            row.get("org_name", ""),
            api_key,
        )
        if url:
            source = "spider_search"
            parsed = parse_snippet(title_snip)
            headline = headline or parsed.get("role_title") or title_snip
            about = about or snippet
            row["snippet_or_quote"] = snippet[:280]
            flags.append("spider_discovered")

    if url and do_scrape and api_key and not has_photo:
        time.sleep(sleep_s)
        scraped = _scrape_profile(url, api_key)
        if scraped.get("error"):
            flags.append("scrape_blocked")
        else:
            headline = scraped.get("linkedin_headline") or headline
            about = scraped.get("linkedin_about") or about
            has_photo = scraped.get("has_profile_photo") == "true"
            if source:
                source = f"{source}+spider_scrape"
            else:
                source = "spider_scrape"
            flags.append("scraped")

    if url and headline and not has_photo:
        # Search snippets often lack photo signal; allow inferred when headline present
        has_photo = True
        flags.append("photo_inferred_with_headline")

    position = row.get("linkedin_position") or headline or row.get("title_raw", "")

    if headline or about:
        tag = tag_persona_keyword(
            f"{headline} {about}",
            row.get("org_name", ""),
        )
        if tag["persona"] != "unknown":
            row["persona"] = tag["persona"]
            row["persona_confidence"] = tag["confidence"]
            row["persona_rationale"] = tag["rationale"]
        lane, lane_r = classify_message_lane(
            row.get("title_raw", ""),
            persona=row.get("persona", ""),
            headline=headline,
            about=about,
        )
        row["message_lane"] = lane
        row["lane_rationale"] = lane_r

    row["linkedin_profile_url"] = url
    row["linkedin_headline"] = headline
    row["linkedin_position"] = position
    row["linkedin_about"] = about
    row["has_profile_photo"] = "true" if has_photo else "false"
    row["enrichment_source"] = source or row.get("enrichment_source", "")
    row["enrichment_confidence"] = "high" if url and headline else ("medium" if url else "low")
    if flags:
        prev = (row.get("validation_flags") or "").strip()
        row["validation_flags"] = ",".join(filter(None, [prev, *flags]))

    return row


def run_enrich(
    *,
    in_csv: Path = FIXTURE_DIR / "pilot_finalists_pre_linkedin.csv",
    out_csv: Path = FIXTURE_DIR / "pilot_linkedin_master.csv",
    log_path: Path = FIXTURE_DIR / "enrichment_log.jsonl",
    apollo_csv: Path = FIXTURE_DIR / "apollo_enriched.csv",
    max_rows: int | None = None,
    skip_scrape: bool = False,
    sleep_s: float = 0.5,
) -> dict[str, int]:
    if not in_csv.exists():
        raise FileNotFoundError(in_csv)

    load_env_local(ENV_FILE)
    api_key = os.environ.get("SPIDER_API_KEY", "").strip()
    apollo_index = _load_apollo_urls(apollo_csv)

    rows: list[dict[str, str]] = []
    with in_csv.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if max_rows is not None and i >= max_rows:
                break
            enriched = enrich_row(
                dict(row),
                api_key=api_key,
                apollo_index=apollo_index,
                do_scrape=not skip_scrape and bool(api_key),
                sleep_s=sleep_s,
            )
            rows.append(enriched)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as logf:
                logf.write(
                    json.dumps(
                        {
                            "contact_id": enriched.get("contact_id"),
                            "url": enriched.get("linkedin_profile_url"),
                            "source": enriched.get("enrichment_source"),
                            "flags": enriched.get("validation_flags"),
                        }
                    )
                    + "\n"
                )

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        fields: list[str] = []
        for r in rows:
            for k in r:
                if k not in fields:
                    fields.append(k)
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    with_url = sum(1 for r in rows if r.get("linkedin_profile_url"))
    with_photo = sum(1 for r in rows if r.get("has_profile_photo") == "true")
    return {"rows": len(rows), "with_url": with_url, "with_photo": with_photo}


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="Enrich Josh pilot finalists with LinkedIn data")
    p.add_argument("--max-rows", type=int, default=None)
    p.add_argument("--skip-scrape", action="store_true")
    p.add_argument("--sleep", type=float, default=0.5)
    args = p.parse_args(argv)

    if FIXTURE_DIR.joinpath("enrichment_log.jsonl").exists():
        FIXTURE_DIR.joinpath("enrichment_log.jsonl").unlink()

    try:
        stats = run_enrich(
            max_rows=args.max_rows,
            skip_scrape=args.skip_scrape,
            sleep_s=args.sleep,
        )
    except FileNotFoundError as e:
        sys.stderr.write(f"{e}\n")
        return 2
    sys.stdout.write(f"Enrich: {stats}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
