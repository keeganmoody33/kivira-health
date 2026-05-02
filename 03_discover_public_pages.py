#!/usr/bin/env python3
"""
03_discover_public_pages.py

Discover and rank high-value public web pages for each classified healthcare account.

Inputs (defaults under ./output/):
- output/accounts_classified_GA.csv
- output/accounts_classified_NC.csv

Outputs (under output_dir/output/):
- public_pages_GA.csv
- public_pages_NC.csv
- public_pages_all.csv
- public_pages_review_queue.csv
- crawl_errors.csv

Constraints:
- Respect robots.txt
- Stay on root domain (allow same-org subdomains only when explicitly linked)
- Shallow crawl only (max depth 2 from seed pages)
- Never use headless browser; never scrape LinkedIn directly

Dependencies: requests, pandas, beautifulsoup4, lxml, python-dateutil, urllib.parse, stdlib
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import random
import re
import time
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import ParseResult, urljoin, urlparse, urlunparse

import pandas as pd
import requests
from dateutil.parser import isoparse

from tam_builder.pilot_filters import (
    default_output_subdir_if_pilot,
    filter_classified_pilot,
    pilot_mode_active,
    read_full_classified_for_state,
    resolve_output_dir,
)

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception as e:  # noqa: BLE001
    raise RuntimeError("beautifulsoup4 is required for 03_discover_public_pages.py") from e


LOGGER = logging.getLogger("kivira.discover")


OUTPUT_COLUMNS: List[str] = [
    "account_id",
    "org_name",
    "website_root",
    "discovered_url",
    "page_type",
    "page_priority",
    "discovery_method",
    "source_domain",
    "http_status",
    "crawl_allowed",
    "title_hint",
    "snippet_hint",
    "likely_person_page",
    "likely_directory_page",
    "likely_contact_page",
    "likely_program_page",
    "likely_leadership_page",
    "linkedin_company_url",
    "linkedin_profile_url_candidates",
    "discovery_confidence",
    "review_flag",
    "review_reason",
    "evidence_notes",
    "last_verified_at",
]


SEED_PATHS: List[str] = [
    "/about",
    "/leadership",
    "/team",
    "/our-team",
    "/providers",
    "/find-a-doctor",
    "/physicians",
    "/medical-staff",
    "/staff",
    "/contact",
    "/locations",
    "/behavioral-health",
    "/primary-care",
    "/population-health",
    "/quality",
    "/value-based-care",
    "/care-management",
    "/news",
    "/press",
    "/blog",
    "/executives",
    "/management",
    "/company",
    "/partners",
    "/integrations",
    "/product",
    "/solutions",
]


PAGE_TYPE_KEYWORDS: List[Tuple[str, Tuple[str, ...]]] = [
    ("leadership", ("leadership", "executive", "executives", "management", "board")),
    ("bio", ("bio", "biography", "leadership/", "team/", "/people", "/person")),
    ("provider_directory", ("providers", "find-a-doctor", "physicians", "provider-directory", "medical-staff")),
    ("provider_profile", ("provider/", "physician/", "doctor/", "/profile", "/providers/")),
    ("contact", ("contact", "get-in-touch", "locations", "location")),
    ("about", ("about", "company", "who-we-are", "our-story")),
    ("program_page", ("behavioral-health", "primary-care", "population-health", "quality", "care-management", "value-based-care")),
    ("newsroom", ("news", "press", "blog", "newsroom", "media")),
    ("payer_program", ("stars", "hedis", "medical-management", "utilization-management", "quality-program")),
    ("partnership", ("partners", "partnership", "alliances")),
    ("integrations", ("integrations", "integration", "api", "ehr", "epic", "cerner")),
]


LINKEDIN_COMPANY_RE = re.compile(r"^https?://([a-z]+\.)?linkedin\.com/company/[^/?#]+/?", re.IGNORECASE)
LINKEDIN_PROFILE_RE = re.compile(r"^https?://([a-z]+\.)?linkedin\.com/in/[^/?#]+/?", re.IGNORECASE)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso_or_none(value: str | None) -> Optional[datetime]:
    if not value:
        return None
    try:
        return isoparse(value)
    except Exception:
        return None


# ---------------------------
# Pure / mostly pure helpers
# ---------------------------
def canonicalize_url(url: str) -> str:
    """
    Remove fragments, tracking params, normalize scheme/host/path trailing slash.
    Keeps only "safe" query params (rarely used here; default drops all).
    """
    url = (url or "").strip()
    if not url:
        return ""
    try:
        pr = urlparse(url)
    except Exception:
        return ""
    scheme = pr.scheme.lower() if pr.scheme else "https"
    netloc = pr.netloc.lower()
    path = pr.path or "/"
    # Trim trailing slash except root
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    # Drop query by default (avoid tracking params)
    query = ""
    fragment = ""
    return urlunparse(ParseResult(scheme, netloc, path, "", query, fragment))


def normalize_domain(website: str) -> Tuple[str, str, List[str]]:
    """
    Returns (website_root_url, root_domain, warnings)

    website_root_url is like https://example.org
    root_domain is netloc (example.org)
    """
    warnings: List[str] = []
    raw = (website or "").strip()
    if not raw:
        return "", "", ["missing_website"]
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    try:
        pr = urlparse(raw)
    except Exception:
        return "", "", ["invalid_website_url"]
    if not pr.netloc:
        return "", "", ["missing_netloc"]
    netloc = pr.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    root = urlunparse(ParseResult("https", netloc, "", "", "", ""))
    return root, netloc, warnings


@dataclass(frozen=True)
class RobotsRules:
    allowed: bool
    disallow_prefixes: Tuple[str, ...]
    sitemap_urls: Tuple[str, ...]


def fetch_robots_rules(session: requests.Session, website_root: str, *, timeout_s: int = 15) -> Tuple[RobotsRules, Optional[int], str]:
    """
    Fetch robots.txt and extract Disallow + Sitemap.
    Very conservative: if robots can't be fetched, treat as allowed (but note).
    """
    robots_url = canonicalize_url(urljoin(website_root.rstrip("/") + "/", "robots.txt"))
    try:
        resp = session.get(robots_url, timeout=timeout_s, headers={"User-Agent": "kivira-public-pages/1.0"})
        status = int(resp.status_code)
        if status >= 400:
            return RobotsRules(allowed=True, disallow_prefixes=tuple(), sitemap_urls=tuple()), status, "robots_missing_or_error"
        text = resp.text or ""
    except Exception as e:  # noqa: BLE001
        return RobotsRules(allowed=True, disallow_prefixes=tuple(), sitemap_urls=tuple()), None, f"robots_fetch_error:{e}"

    disallow: List[str] = []
    sitemaps: List[str] = []
    current_user_agent: Optional[str] = None
    applies = False
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            current_user_agent = value
            applies = value == "*"  # only parse "*" block (simple)
        elif key == "disallow" and applies:
            if value:
                disallow.append(value)
        elif key == "sitemap":
            if value:
                sitemaps.append(value)

    return RobotsRules(allowed=True, disallow_prefixes=tuple(disallow), sitemap_urls=tuple(sitemaps)), status, ""


def is_crawl_allowed(robots: RobotsRules, path: str) -> bool:
    p = path or "/"
    for dis in robots.disallow_prefixes:
        if dis == "/":
            return False
        if p.startswith(dis):
            return False
    return True


def discover_sitemaps(robots: RobotsRules, website_root: str) -> List[str]:
    out: List[str] = []
    for u in robots.sitemap_urls:
        cu = canonicalize_url(u)
        if cu and cu not in out:
            out.append(cu)
    # common fallbacks
    for p in ["/sitemap.xml", "/sitemap_index.xml", "/sitemap-index.xml", "/sitemap/sitemap.xml"]:
        cu = canonicalize_url(urljoin(website_root.rstrip("/") + "/", p.lstrip("/")))
        if cu and cu not in out:
            out.append(cu)
    return out


def classify_page_type(url: str, title: str, snippet: str) -> str:
    u = (url or "").lower()
    t = (title or "").lower()
    s = (snippet or "").lower()
    hay = " ".join([u, t, s])
    for page_type, keys in PAGE_TYPE_KEYWORDS:
        for k in keys:
            if k in hay:
                return page_type
    return "unknown"


def score_page_priority(page_type: str, subtier_primary: str) -> int:
    """
    Priority 1 (best) ... 5 (worst).
    Base on page_type + subtier hints.
    """
    pt = page_type
    st = (subtier_primary or "").strip().upper()

    # universally high
    if pt in {"leadership", "bio", "provider_directory", "provider_profile"}:
        return 1
    if pt in {"about", "contact", "program_page", "payer_program", "integrations", "partnership"}:
        return 2
    if pt in {"newsroom"}:
        return 3
    if pt == "unknown":
        return 5

    # subtier adjustments (minor)
    if st in {"2B"} and pt in {"integrations", "partnership"}:
        return 1
    if st in {"3C"} and pt in {"payer_program", "leadership"}:
        return 1
    return 4


def extract_linkedin_links(html: str, base_url: str) -> Tuple[str, List[str]]:
    """
    Extract exact LinkedIn company URL and any profile URL candidates found as direct links on the page.
    Does not crawl LinkedIn.
    """
    if not html:
        return "", []
    soup = BeautifulSoup(html, "lxml")
    company = ""
    profiles: List[str] = []
    for a in soup.find_all("a", href=True):
        href = str(a.get("href") or "").strip()
        if not href:
            continue
        abs_url = canonicalize_url(urljoin(base_url, href))
        if LINKEDIN_COMPANY_RE.match(abs_url):
            if not company:
                company = abs_url
        elif LINKEDIN_PROFILE_RE.match(abs_url):
            if abs_url not in profiles:
                profiles.append(abs_url)
    return company, profiles


def snippet_from_html(html: str) -> str:
    soup = BeautifulSoup(html or "", "lxml")
    # prefer meta description
    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content"):
        return str(md.get("content")).strip()[:220]
    text = " ".join(soup.get_text(" ").split())
    return text[:220]


def title_from_html(html: str) -> str:
    soup = BeautifulSoup(html or "", "lxml")
    t = soup.find("title")
    if t and t.get_text():
        return " ".join(t.get_text(" ").split())[:140]
    # fallback to first h1
    h1 = soup.find("h1")
    if h1 and h1.get_text():
        return " ".join(h1.get_text(" ").split())[:140]
    return ""


# ---------------------------
# Crawling
# ---------------------------
@dataclass(frozen=True)
class CrawlConfig:
    rate_limit_s: float = 0.50
    retry_count: int = 2
    timeout_s: int = 15
    max_pages_per_domain: int = 30
    max_depth: int = 2


class RateLimiter:
    def __init__(self, min_interval_s: float) -> None:
        self.min_interval_s = max(0.0, float(min_interval_s))
        self._last_at = 0.0

    def wait(self) -> None:
        if self.min_interval_s <= 0:
            return
        now = time.time()
        delta = now - self._last_at
        if delta < self.min_interval_s:
            time.sleep(self.min_interval_s - delta)
        self._last_at = time.time()


def request_with_retry(
    session: requests.Session,
    url: str,
    *,
    retry_count: int,
    limiter: RateLimiter,
    timeout_s: int,
) -> Tuple[Optional[requests.Response], Optional[str]]:
    last_err: Optional[str] = None
    for attempt in range(retry_count + 1):
        limiter.wait()
        try:
            resp = session.get(url, timeout=timeout_s, headers={"User-Agent": "kivira-public-pages/1.0"})
            return resp, None
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
            backoff = (2**attempt) + random.random()
            time.sleep(backoff)
    return None, last_err


def same_root_domain(root_domain: str, candidate_netloc: str) -> bool:
    rd = (root_domain or "").lower()
    cn = (candidate_netloc or "").lower()
    if cn.startswith("www."):
        cn = cn[4:]
    if rd == cn:
        return True
    # allow explicit subdomains of same root
    return cn.endswith("." + rd)


def extract_internal_links(html: str, base_url: str, root_domain: str) -> List[str]:
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    out: List[str] = []
    for a in soup.find_all("a", href=True):
        href = str(a.get("href") or "").strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        abs_url = canonicalize_url(urljoin(base_url, href))
        if not abs_url:
            continue
        pr = urlparse(abs_url)
        if not pr.netloc:
            continue
        if not same_root_domain(root_domain, pr.netloc):
            continue
        # skip obvious low-value assets
        if pr.path.lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".zip")):
            continue
        if abs_url not in out:
            out.append(abs_url)
    return out


def looks_high_value_path(path: str) -> bool:
    p = (path or "").lower()
    if not p or p == "/":
        return True
    for seed in SEED_PATHS:
        if seed in p:
            return True
    # Heuristic: avoid deep query-like paths
    depth = len([x for x in p.split("/") if x])
    if depth <= 2:
        return True
    return False


def discover_for_account(
    account: Dict[str, Any],
    crawl_cfg: CrawlConfig,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Returns (discovered_rows, crawl_errors_rows)
    """
    account_id = str(account.get("account_id") or "").strip()
    org_name = str(account.get("org_name") or "").strip()
    subtier = str(account.get("subtier_primary") or "").strip().upper()
    website = str(account.get("website") or "").strip()
    evidence_urls = str(account.get("evidence_urls") or "").strip()

    last_verified_at = str(account.get("last_verified_at") or "").strip()
    dt = parse_iso_or_none(last_verified_at)
    last_verified_at = (dt.astimezone(timezone.utc).replace(microsecond=0).isoformat() if dt else utc_now_iso())

    website_root, root_domain, warnings = normalize_domain(website)
    if warnings:
        return (
            [
                _row(
                    account_id=account_id,
                    org_name=org_name,
                    website_root="",
                    discovered_url="",
                    page_type="unknown",
                    page_priority=5,
                    discovery_method="website_input",
                    source_domain="",
                    http_status="",
                    crawl_allowed="",
                    title_hint="",
                    snippet_hint="",
                    likely_person_page="false",
                    likely_directory_page="false",
                    likely_contact_page="false",
                    likely_program_page="false",
                    likely_leadership_page="false",
                    linkedin_company_url="",
                    linkedin_profile_url_candidates=json.dumps([]),
                    discovery_confidence="0.00",
                    review_flag="true",
                    review_reason=";".join(warnings),
                    evidence_notes="No website provided or invalid website field",
                    last_verified_at=last_verified_at,
                )
            ],
            [],
        )

    session = requests.Session()
    limiter = RateLimiter(crawl_cfg.rate_limit_s)
    robots, robots_status, robots_note = fetch_robots_rules(session, website_root, timeout_s=crawl_cfg.timeout_s)

    discovered: Dict[str, Dict[str, Any]] = {}
    crawl_errors: List[Dict[str, Any]] = []
    linkedin_company = ""
    linkedin_profiles: List[str] = []

    def add_url(
        url: str,
        method: str,
        http_status: str,
        crawl_allowed: str,
        title_hint: str,
        snippet_hint: str,
        discovery_confidence: float,
        evidence_note: str,
    ) -> None:
        cu = canonicalize_url(url)
        if not cu:
            return
        pr = urlparse(cu)
        if not pr.netloc or not same_root_domain(root_domain, pr.netloc):
            return
        page_type = classify_page_type(cu, title_hint, snippet_hint)
        priority = score_page_priority(page_type, subtier)

        likely_person = page_type in {"bio", "provider_profile"}
        likely_dir = page_type in {"provider_directory"}
        likely_contact = page_type in {"contact"}
        likely_program = page_type in {"program_page", "payer_program", "integrations", "partnership"}
        likely_leadership = page_type in {"leadership"}

        existing = discovered.get(cu)
        if existing:
            # keep best (highest confidence / priority)
            if discovery_confidence > float(existing.get("discovery_confidence") or 0):
                existing["discovery_method"] = method
                existing["discovery_confidence"] = f"{discovery_confidence:.2f}"
            # merge evidence notes
            existing["evidence_notes"] = _merge_notes(str(existing.get("evidence_notes") or ""), evidence_note)
            return

        discovered[cu] = _row(
            account_id=account_id,
            org_name=org_name,
            website_root=website_root,
            discovered_url=cu,
            page_type=page_type,
            page_priority=str(priority),
            discovery_method=method,
            source_domain=pr.netloc.lower(),
            http_status=http_status,
            crawl_allowed=crawl_allowed,
            title_hint=title_hint,
            snippet_hint=snippet_hint,
            likely_person_page=as_bool_str(likely_person),
            likely_directory_page=as_bool_str(likely_dir),
            likely_contact_page=as_bool_str(likely_contact),
            likely_program_page=as_bool_str(likely_program),
            likely_leadership_page=as_bool_str(likely_leadership),
            linkedin_company_url="",
            linkedin_profile_url_candidates=json.dumps([]),
            discovery_confidence=f"{discovery_confidence:.2f}",
            review_flag="false",
            review_reason="",
            evidence_notes=evidence_note,
            last_verified_at=last_verified_at,
        )

    # Seed with website root
    add_url(
        website_root,
        "website_input",
        http_status=str(robots_status or ""),
        crawl_allowed=as_bool_str(True),
        title_hint="",
        snippet_hint="",
        discovery_confidence=0.50,
        evidence_note="Using website input root domain",
    )

    # Common path probes (only if robots allows)
    for path in SEED_PATHS:
        if not is_crawl_allowed(robots, path):
            continue
        probe_url = canonicalize_url(urljoin(website_root.rstrip("/") + "/", path.lstrip("/")))
        resp, err = request_with_retry(session, probe_url, retry_count=crawl_cfg.retry_count, limiter=limiter, timeout_s=crawl_cfg.timeout_s)
        if err:
            crawl_errors.append(
                {
                    "account_id": account_id,
                    "org_name": org_name,
                    "url": probe_url,
                    "error": err,
                    "method": "common_path_probe",
                    "at": utc_now_iso(),
                }
            )
            continue
        if not resp:
            continue
        status = int(resp.status_code)
        if status in {200, 301, 302}:
            final_url = canonicalize_url(str(resp.url))
            title = title_from_html(resp.text)
            snippet = snippet_from_html(resp.text)
            add_url(
                final_url,
                "common_path_probe",
                str(status),
                as_bool_str(True),
                title,
                snippet,
                0.75,
                f"Probed common path {path}",
            )
            c, ps = extract_linkedin_links(resp.text, final_url)
            if c and not linkedin_company:
                linkedin_company = c
            for purl in ps:
                if purl not in linkedin_profiles:
                    linkedin_profiles.append(purl)

    # Sitemaps from robots/common paths
    sitemap_urls = discover_sitemaps(robots, website_root)
    for sm in sitemap_urls[:5]:  # cap sitemap checks
        pr = urlparse(sm)
        if not same_root_domain(root_domain, pr.netloc):
            continue
        if not is_crawl_allowed(robots, pr.path or "/"):
            continue
        resp, err = request_with_retry(session, sm, retry_count=crawl_cfg.retry_count, limiter=limiter, timeout_s=crawl_cfg.timeout_s)
        if err or not resp:
            continue
        if int(resp.status_code) >= 400:
            continue
        # parse XML lightly by regex (avoid heavy deps beyond lxml in bs4 parser)
        xml = resp.text or ""
        # Extract loc tags (first N)
        locs = re.findall(r"<loc>(.*?)</loc>", xml, flags=re.IGNORECASE)
        for loc in locs[:200]:
            cu = canonicalize_url(loc.strip())
            if not cu:
                continue
            p = urlparse(cu)
            if not same_root_domain(root_domain, p.netloc):
                continue
            if not looks_high_value_path(p.path):
                continue
            add_url(
                cu,
                "sitemap_xml",
                str(resp.status_code),
                as_bool_str(is_crawl_allowed(robots, p.path)),
                "",
                "",
                0.65,
                "Discovered via sitemap loc",
            )

    # Shallow crawl: expand from top pages
    # Build a queue of candidates by priority
    candidates = sorted(
        discovered.values(),
        key=lambda r: (int(r.get("page_priority") or 5), -(float(r.get("discovery_confidence") or 0.0))),
    )
    queue: List[Tuple[str, int]] = []
    visited: Set[str] = set()
    for r in candidates:
        u = str(r.get("discovered_url") or "")
        if u:
            queue.append((u, 0))

    pages_fetched = 0
    while queue and pages_fetched < crawl_cfg.max_pages_per_domain:
        url, depth = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        pr = urlparse(url)
        if not is_crawl_allowed(robots, pr.path or "/"):
            continue
        if depth > crawl_cfg.max_depth:
            continue
        resp, err = request_with_retry(session, url, retry_count=crawl_cfg.retry_count, limiter=limiter, timeout_s=crawl_cfg.timeout_s)
        pages_fetched += 1
        if err or not resp:
            if err:
                crawl_errors.append(
                    {"account_id": account_id, "org_name": org_name, "url": url, "error": err, "method": "internal_link", "at": utc_now_iso()}
                )
            continue
        if int(resp.status_code) >= 400:
            continue
        final_url = canonicalize_url(str(resp.url))
        title = title_from_html(resp.text)
        snippet = snippet_from_html(resp.text)
        add_url(
            final_url,
            "internal_link",
            str(resp.status_code),
            as_bool_str(True),
            title,
            snippet,
            0.70,
            f"Fetched and extracted internal links at depth {depth}",
        )

        c, ps = extract_linkedin_links(resp.text, final_url)
        if c and not linkedin_company:
            linkedin_company = c
        for purl in ps:
            if purl not in linkedin_profiles:
                linkedin_profiles.append(purl)

        if depth < crawl_cfg.max_depth:
            links = extract_internal_links(resp.text, final_url, root_domain)
            # prioritize likely high-value paths
            links_sorted = sorted(links, key=lambda u2: (not looks_high_value_path(urlparse(u2).path), len(urlparse(u2).path)))
            for ln in links_sorted[:25]:
                if ln not in visited:
                    queue.append((ln, depth + 1))

    # Finalize rows: add linkedin fields, review flags if no high value found
    rows = list(discovered.values())
    # Rank per account: priority then confidence then URL length
    rows.sort(key=lambda r: (int(r.get("page_priority") or 5), -(float(r.get("discovery_confidence") or 0.0)), len(str(r.get("discovered_url") or ""))))

    found_top = any(int(r.get("page_priority") or 5) <= 2 for r in rows if r.get("discovered_url"))
    robots_blocked_any = any(not is_crawl_allowed(robots, urlparse(r.get("discovered_url") or "").path or "/") for r in rows if r.get("discovered_url"))

    for r in rows:
        r["linkedin_company_url"] = linkedin_company
        r["linkedin_profile_url_candidates"] = json.dumps(linkedin_profiles[:20])

        review = False
        reasons: List[str] = []
        if not website:
            review = True
            reasons.append("website_missing")
        if robots_note:
            reasons.append(robots_note)
        if robots_blocked_any:
            reasons.append("robots_blocks_some_paths")
        if not found_top:
            review = True
            reasons.append("no_high_value_pages_found")
        if linkedin_company and not LINKEDIN_COMPANY_RE.match(linkedin_company):
            review = True
            reasons.append("linkedin_company_url_malformed")
        if any(not LINKEDIN_PROFILE_RE.match(p) for p in linkedin_profiles):
            review = True
            reasons.append("linkedin_profile_url_candidate_malformed")

        r["review_flag"] = as_bool_str(review)
        r["review_reason"] = ";".join([x for x in reasons if x])

        # Evidence notes: concise
        if found_top:
            r["evidence_notes"] = _merge_notes(str(r.get("evidence_notes") or ""), "Found at least one high-value page (priority<=2)")
        else:
            r["evidence_notes"] = _merge_notes(str(r.get("evidence_notes") or ""), "Only generic/low-value pages discovered")
        if evidence_urls:
            r["evidence_notes"] = _merge_notes(str(r.get("evidence_notes") or ""), "Seed evidence_urls present (not directly followed)")

    return rows, crawl_errors


def _merge_notes(a: str, b: str) -> str:
    a = (a or "").strip()
    b = (b or "").strip()
    if not a:
        return b
    if not b:
        return a
    if b in a:
        return a
    return a + " | " + b


def _row(**kwargs: Any) -> Dict[str, Any]:
    out = {c: "" for c in OUTPUT_COLUMNS}
    for k, v in kwargs.items():
        if k in out:
            out[k] = v
    # enforce stringy fields
    for k in out:
        if out[k] is None:
            out[k] = ""
        if not isinstance(out[k], str):
            out[k] = str(out[k])
    return out


def as_bool_str(value: bool) -> str:
    return "true" if value else "false"


# ---------------------------
# IO pipeline
# ---------------------------
def read_classified(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def write_csv(path: Path, df: pd.DataFrame) -> None:
    for c in OUTPUT_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    df[OUTPUT_COLUMNS].to_csv(path, index=False)


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Discover high-value public pages for classified accounts.")
    p.add_argument("--base-dir", default=".", help="Base directory containing output/ (and optional input/).")
    p.add_argument("--states", default="GA,NC", help="Comma-separated states (default GA,NC).")
    p.add_argument("--rate-limit", type=float, default=0.50, help="Min seconds between requests per domain.")
    p.add_argument("--retries", type=int, default=2, help="Retry count per request.")
    p.add_argument("--timeout", type=int, default=15, help="Request timeout seconds.")
    p.add_argument("--max-pages", type=int, default=30, help="Max pages to fetch per domain.")
    p.add_argument("--max-depth", type=int, default=2, help="Max crawl depth from seed pages.")
    p.add_argument("--log-level", default="INFO", help="Logging level.")
    p.add_argument(
        "--output-subdir",
        default="",
        help="Write under output/<subdir>/ (e.g. pilot). Default: pilot/ when any --pilot-* flag is set.",
    )
    p.add_argument("--pilot-subtier", default="", help="Only process accounts with this subtier_primary (e.g. 1A).")
    p.add_argument("--pilot-max-accounts", type=int, default=0, help="Max accounts per state after filters (0 = no limit).")
    p.add_argument("--pilot-require-website", action="store_true", help="Require non-empty website on classified row.")
    p.add_argument(
        "--pilot-min-classification-confidence",
        type=float,
        default=0.0,
        help="Minimum classification_confidence (0 = no floor).",
    )
    args = p.parse_args(argv)

    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s - %(message)s")

    base_dir = Path(args.base_dir).expanduser().resolve()
    pilot_subtier = str(args.pilot_subtier or "").strip() or None
    pilot_max = int(args.pilot_max_accounts or 0)
    pilot_max_arg = pilot_max if pilot_max > 0 else None
    subdir = default_output_subdir_if_pilot(
        str(args.output_subdir or ""),
        pilot_subtier=pilot_subtier,
        pilot_max_accounts=pilot_max_arg,
        pilot_require_website=bool(args.pilot_require_website),
        pilot_min_classification_confidence=float(args.pilot_min_classification_confidence or 0),
    )
    out_dir = resolve_output_dir(base_dir, subdir)
    use_pilot = pilot_mode_active(
        pilot_subtier=pilot_subtier,
        pilot_max_accounts=pilot_max_arg,
        pilot_require_website=bool(args.pilot_require_website),
        pilot_min_classification_confidence=float(args.pilot_min_classification_confidence or 0),
    )

    crawl_cfg = CrawlConfig(
        rate_limit_s=float(args.rate_limit),
        retry_count=int(args.retries),
        timeout_s=int(args.timeout),
        max_pages_per_domain=int(args.max_pages),
        max_depth=int(args.max_depth),
    )

    states = [s.strip().upper() for s in str(args.states).split(",") if s.strip()]

    all_rows: List[Dict[str, Any]] = []
    review_rows: List[Dict[str, Any]] = []
    crawl_errors: List[Dict[str, Any]] = []

    for st in states:
        if use_pilot:
            df = read_full_classified_for_state(base_dir, st)
            if df.empty:
                LOGGER.warning("Missing full classified file for %s under output/ (skipping)", st)
                continue
            df = filter_classified_pilot(
                df,
                subtier=pilot_subtier,
                max_accounts=pilot_max_arg,
                require_website=bool(args.pilot_require_website),
                min_classification_confidence=float(args.pilot_min_classification_confidence or 0),
            )
            if df.empty:
                LOGGER.warning("Pilot filter yielded no accounts for %s (skipping)", st)
                continue
            # Persist slice so 04/05/06 use the same cohort
            df.to_csv(out_dir / f"accounts_classified_{st}.csv", index=False)
            LOGGER.info("Pilot slice for %s: %s accounts → %s", st, len(df), out_dir / f"accounts_classified_{st}.csv")
        else:
            in_path = out_dir / f"accounts_classified_{st}.csv"
            if not in_path.exists():
                LOGGER.warning("Missing classified file for %s: %s (skipping)", st, in_path)
                continue
            df = read_classified(in_path)
        LOGGER.info("Discovering public pages for %s (%s accounts)", st, len(df))
        rows_for_state: List[Dict[str, Any]] = []
        for acct in df.to_dict(orient="records"):
            discovered, errs = discover_for_account(acct, crawl_cfg)
            rows_for_state.extend(discovered)
            crawl_errors.extend(errs)

        st_df = pd.DataFrame(rows_for_state)
        if not st_df.empty:
            st_df["page_priority"] = st_df["page_priority"].astype(str)
        write_csv(out_dir / f"public_pages_{st}.csv", st_df)
        all_rows.extend(rows_for_state)

    all_df = pd.DataFrame(all_rows)
    write_csv(out_dir / "public_pages_all.csv", all_df)

    if not all_df.empty:
        rev_df = all_df[all_df["review_flag"].astype(str).str.lower() == "true"].copy()
    else:
        rev_df = pd.DataFrame(columns=OUTPUT_COLUMNS)
    write_csv(out_dir / "public_pages_review_queue.csv", rev_df)

    err_df = pd.DataFrame(crawl_errors)
    (out_dir / "crawl_errors.csv").write_text(err_df.to_csv(index=False) if not err_df.empty else "account_id,org_name,url,error,method,at\n", encoding="utf-8")

    LOGGER.info("Done. URLs=%s Reviews=%s Errors=%s", len(all_df), len(rev_df), len(err_df))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

