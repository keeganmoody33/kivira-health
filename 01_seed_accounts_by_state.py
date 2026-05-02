#!/usr/bin/env python3
"""
01_seed_accounts_by_state.py

Georgia-first healthcare account seed table from public sources only.

This script is intentionally conservative:
- Primary source is a locally-downloaded NPPES "NPI Full Replacement Monthly" CSV (public).
- Optional secondary evidence sources (e.g., CMS ACO REACH participants) can be added via config.
- The CMS NPI Registry API connector exists but is limited (broad state-only queries are rejected).

Outputs (under output_dir/output/):
- accounts_seed_GA.csv
- accounts_seed_NC.csv
- accounts_seed_all.csv
- dedup_review.csv
- source_errors.csv

Dependencies: requests, pandas, rapidfuzz, python-dateutil (plus stdlib)
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd
import requests
from dateutil.parser import isoparse

try:
    # Preferred (fast, better matching). Required by spec, but optional at runtime.
    from rapidfuzz import fuzz as _rapidfuzz_fuzz  # type: ignore
except Exception:  # noqa: BLE001
    _rapidfuzz_fuzz = None


LOGGER = logging.getLogger("kivira.seed")

# Required: GA, NC first; rest as placeholders for easy extension.
STATE_PRIORITY_ORDER: List[str] = [
    "GA",
    "NC",
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
]


SCHEMA_COLUMNS: List[str] = [
    "account_id",
    "source_system",
    "source_record_id",
    "org_name",
    "org_name_raw",
    "entity_type",
    "parent_org_name",
    "parent_org_id",
    "subtier_primary",
    "subtier_secondary_tags",
    "practice_address_1",
    "practice_city",
    "practice_state",
    "practice_postal_code",
    "mailing_address_1",
    "mailing_city",
    "mailing_state",
    "mailing_postal_code",
    "primary_state",
    "all_states_seen",
    "multi_state_flag",
    "source_state_basis",
    "state_confidence",
    "website",
    "phone_main",
    "npi_count_est",
    "pcp_count_est",
    "vbc_signal",
    "bh_signal",
    "exclusion_status",
    "exclusion_reason",
    "evidence_urls",
    "last_verified_at",
]


@dataclass(frozen=True)
class Config:
    target_states: List[str]
    output_dir: str
    rate_limit_per_source: float
    retry_count: int

    # Source toggles / endpoints.
    npi_registry_base_url: str = "https://npiregistry.cms.hhs.gov/api/"
    npi_registry_version: str = "2.1"
    npi_registry_limit: int = 200
    npi_registry_max_records_per_state: Optional[int] = None
    use_npi_registry_api: bool = False

    # Preferred seed input: downloaded NPPES "NPI Full Replacement Monthly" CSV.
    # This script does not auto-download the full NPPES file (it's very large); point to a local file.
    nppes_full_csv_path: Optional[str] = None
    nppes_chunksize: int = 200_000

    # Optional (not required): if provided, will attempt to fetch and add evidence tags.
    cms_aco_reach_participants_csv_url: Optional[str] = None
    cms_aco_reach_cache_path: Optional[str] = None


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
# Pure functions (unit-testable)
# ---------------------------
def normalize_org_name(name: str) -> str:
    """
    Normalize organization name for matching/deduping.
    Conservative: remove punctuation, collapse whitespace, uppercase.
    """
    if not name:
        return ""
    cleaned = []
    for ch in name.strip():
        if ch.isalnum() or ch.isspace():
            cleaned.append(ch.upper())
        else:
            cleaned.append(" ")
    out = " ".join("".join(cleaned).split())
    # Common suffix cleanup without being overly aggressive.
    for suffix in [" LLC", " PLLC", " INC", " INCORPORATED", " PC", " PA", " LLP", " LP", " LTD", " CO", " CORP", " CORPORATION"]:
        if out.endswith(suffix):
            out = out[: -len(suffix)].rstrip()
    return out


def assign_primary_state(
    practice_state: str | None,
    mailing_state: str | None,
    inferred_state: str | None = None,
    parent_hq_state: str | None = None,
) -> Tuple[str | None, str, float]:
    """
    Prefer practice_state, then mailing_state, then inferred_state, then parent_hq_state.

    Returns (primary_state, source_state_basis, state_confidence).
    """
    ps = (practice_state or "").strip().upper()
    ms = (mailing_state or "").strip().upper()
    ins = (inferred_state or "").strip().upper()
    phs = (parent_hq_state or "").strip().upper()

    if ps:
        return ps, "practice_address", 0.95
    if ms:
        return ms, "mailing_address", 0.85
    if ins:
        return ins, "inferred_from_evidence", 0.60
    if phs:
        return phs, "parent_hq_fallback", 0.35
    return None, "unknown", 0.0


def build_all_states_seen(practice_state: str | None, mailing_state: str | None, primary_state: str | None) -> str:
    states = []
    for s in [practice_state, mailing_state, primary_state]:
        s2 = (s or "").strip().upper()
        if s2 and s2 not in states:
            states.append(s2)
    return "|".join(states)


def _address_key(address_1: str | None, city: str | None, state: str | None, postal: str | None) -> str:
    parts = [
        (address_1 or "").strip().upper(),
        (city or "").strip().upper(),
        (state or "").strip().upper(),
        (postal or "").strip().upper()[:5],
    ]
    return "|".join([p for p in parts if p])


def _stable_account_id(norm_name: str, address_key: str, primary_state: str | None) -> str:
    raw = f"{norm_name}||{address_key}||{(primary_state or '').upper()}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


def dedupe_accounts(
    rows: List[Dict[str, Any]],
    *,
    name_threshold: int = 92,
    address_threshold: int = 88,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Deduplicate account candidates into a single row per account.

    Strategy:
    - Group by normalized name (exact) first for speed.
    - Within groups, merge rows with sufficiently similar address keys.
    - Produce a review queue for ambiguous near-matches.
    """
    if not rows:
        return [], []

    # Prepare
    prepared: List[Dict[str, Any]] = []
    for r in rows:
        org_raw = (r.get("org_name_raw") or r.get("org_name") or "").strip()
        org_norm = normalize_org_name(org_raw)
        practice_key = _address_key(
            r.get("practice_address_1"),
            r.get("practice_city"),
            r.get("practice_state"),
            r.get("practice_postal_code"),
        )
        mailing_key = _address_key(
            r.get("mailing_address_1"),
            r.get("mailing_city"),
            r.get("mailing_state"),
            r.get("mailing_postal_code"),
        )
        r2 = dict(r)
        r2["_org_norm"] = org_norm
        r2["_practice_key"] = practice_key
        r2["_mailing_key"] = mailing_key
        prepared.append(r2)

    # Bucket by exact normalized name (fast path).
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for r in prepared:
        buckets.setdefault(r["_org_norm"], []).append(r)

    deduped: List[Dict[str, Any]] = []
    review: List[Dict[str, Any]] = []

    for org_norm, bucket in buckets.items():
        if not org_norm:
            # Keep empties separate; cannot reliably dedupe.
            for r in bucket:
                review.append(
                    {
                        "reason": "missing_org_name",
                        "source_system": r.get("source_system"),
                        "source_record_id": r.get("source_record_id"),
                        "org_name_raw": r.get("org_name_raw"),
                        "practice_address_1": r.get("practice_address_1"),
                        "practice_city": r.get("practice_city"),
                        "practice_state": r.get("practice_state"),
                        "practice_postal_code": r.get("practice_postal_code"),
                        "mailing_address_1": r.get("mailing_address_1"),
                        "mailing_city": r.get("mailing_city"),
                        "mailing_state": r.get("mailing_state"),
                        "mailing_postal_code": r.get("mailing_postal_code"),
                    }
                )
            continue

        merged: List[Dict[str, Any]] = []
        for r in bucket:
            placed = False
            for m in merged:
                # Address similarity: compare practice first; fallback to mailing.
                a1 = r["_practice_key"] or r["_mailing_key"]
                a2 = m["_practice_key"] or m["_mailing_key"]
                if not a1 or not a2:
                    continue
                if token_sort_ratio(a1, a2) >= address_threshold:
                    # Merge into m.
                    m["_sources"].append((r.get("source_system"), r.get("source_record_id")))
                    m["_npis"].append(r.get("source_record_id"))
                    m["evidence_urls"] = _merge_pipe_delimited(m.get("evidence_urls"), r.get("evidence_urls"))
                    m["all_states_seen"] = _merge_pipe_delimited(m.get("all_states_seen"), r.get("all_states_seen"))
                    m["multi_state_flag"] = "true" if "|" in (m.get("all_states_seen") or "") else "false"
                    placed = True
                    break
            if not placed:
                r["_sources"] = [(r.get("source_system"), r.get("source_record_id"))]
                r["_npis"] = [r.get("source_record_id")]
                merged.append(r)

        # After merging exact-norm buckets, add a review entry for near name collisions across different norms.
        # (We handle cross-norm review later in a second pass.)
        for m in merged:
            # Ensure npi_count_est
            npis = [n for n in m.get("_npis", []) if n]
            m["npi_count_est"] = str(len(set(npis))) if npis else (m.get("npi_count_est") or "")
            deduped.append(m)

    # Cross-bucket near-name review: detect highly similar names in same state.
    # This does not merge; it only flags for manual review.
    # Keep complexity bounded by only comparing within same primary_state.
    by_state: Dict[str, List[Dict[str, Any]]] = {}
    for r in deduped:
        st = (r.get("primary_state") or "").strip().upper() or "UNKNOWN"
        by_state.setdefault(st, []).append(r)

    for st, state_rows in by_state.items():
        if len(state_rows) < 2:
            continue
        # Randomly sample pairs if extremely large to keep runtime reasonable.
        max_pairs = 3000
        pairs_checked = 0
        for i in range(len(state_rows)):
            for j in range(i + 1, len(state_rows)):
                pairs_checked += 1
                if pairs_checked > max_pairs:
                    break
                a = state_rows[i]
                b = state_rows[j]
                score = token_sort_ratio(a.get("_org_norm", ""), b.get("_org_norm", ""))
                if score >= name_threshold and a.get("account_id") != b.get("account_id"):
                    review.append(
                        {
                            "reason": "near_name_match_same_state",
                            "state": st,
                            "name_similarity": score,
                            "account_id_a": a.get("account_id"),
                            "org_name_a": a.get("org_name"),
                            "practice_key_a": a.get("_practice_key") or a.get("_mailing_key"),
                            "account_id_b": b.get("account_id"),
                            "org_name_b": b.get("org_name"),
                            "practice_key_b": b.get("_practice_key") or b.get("_mailing_key"),
                        }
                    )
            if pairs_checked > max_pairs:
                break

    # Strip internal keys.
    cleaned_deduped = []
    for r in deduped:
        r2 = {k: v for k, v in r.items() if not k.startswith("_")}
        cleaned_deduped.append(r2)
    return cleaned_deduped, review


def _merge_pipe_delimited(a: Any, b: Any) -> str:
    """
    Merge pipe-delimited strings (or lists) into a canonical pipe-delimited string with stable ordering.
    """
    def to_items(x: Any) -> List[str]:
        if x is None:
            return []
        if isinstance(x, list):
            return [str(i).strip() for i in x if str(i).strip()]
        s = str(x).strip()
        if not s:
            return []
        return [p.strip() for p in s.split("|") if p.strip()]

    items = []
    for it in to_items(a) + to_items(b):
        if it not in items:
            items.append(it)
    return "|".join(items)


def token_sort_ratio(a: str, b: str) -> int:
    """
    Approximate rapidfuzz.fuzz.token_sort_ratio.

    - Uses rapidfuzz when installed.
    - Falls back to difflib-based similarity (slower, lower quality) to keep script runnable.
    """
    a = (a or "").strip()
    b = (b or "").strip()
    if not a and not b:
        return 100
    if _rapidfuzz_fuzz is not None:
        return int(_rapidfuzz_fuzz.token_sort_ratio(a, b))

    # Fallback: sort tokens and compute SequenceMatcher ratio
    import difflib

    def norm_tokens(s: str) -> str:
        toks = [t for t in s.upper().split() if t]
        toks.sort()
        return " ".join(toks)

    aa = norm_tokens(a)
    bb = norm_tokens(b)
    return int(round(difflib.SequenceMatcher(a=aa, b=bb).ratio() * 100))


# ---------------------------
# HTTP utilities
# ---------------------------
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


def request_json_with_retry(
    session: requests.Session,
    url: str,
    params: Dict[str, Any],
    *,
    retry_count: int,
    rate_limiter: RateLimiter,
    timeout_s: int = 30,
) -> Dict[str, Any]:
    last_err: Optional[Exception] = None
    for attempt in range(retry_count + 1):
        rate_limiter.wait()
        try:
            resp = session.get(url, params=params, timeout=timeout_s, headers={"User-Agent": "kivira-public-data-pipeline/1.0"})
            if resp.status_code >= 500:
                raise RuntimeError(f"server_error status={resp.status_code}")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:  # noqa: BLE001
            last_err = e
            backoff = (2**attempt) + random.random()
            LOGGER.warning("Request failed (attempt %s/%s): %s; backing off %.2fs", attempt + 1, retry_count + 1, e, backoff)
            time.sleep(backoff)
    raise RuntimeError(f"Failed after retries: {last_err}")


# ---------------------------
# Source connectors
# ---------------------------
def fetch_npi_registry_orgs_for_state(config: Config, state: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Fetch NPI-2 organization records for a given state from the NPI Registry API,
    and convert into account candidate rows.

    Returns (rows, errors).
    """
    state = state.strip().upper()
    session = requests.Session()
    limiter = RateLimiter(config.rate_limit_per_source)

    rows: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    skip = 0
    limit = int(config.npi_registry_limit)
    fetched = 0

    # NOTE: The public NPI Registry API does not allow broad queries like {state=GA, enumeration_type=NPI-2}
    # without additional criteria. This connector is therefore optional and off by default.
    while True:
        if config.npi_registry_max_records_per_state is not None and fetched >= config.npi_registry_max_records_per_state:
            break

        params = {
            "version": config.npi_registry_version,
            "enumeration_type": "NPI-2",
            "state": state,
            "limit": limit,
            "skip": skip,
        }

        try:
            payload = request_json_with_retry(
                session,
                config.npi_registry_base_url,
                params,
                retry_count=config.retry_count,
                rate_limiter=limiter,
            )
        except Exception as e:  # noqa: BLE001
            errors.append(
                {
                    "source_system": "npi_registry",
                    "source_record_id": f"state={state}&skip={skip}",
                    "error": str(e),
                    "at": utc_now_iso(),
                }
            )
            break

        # If API rejects the query, it returns an "Errors" array.
        if payload.get("Errors"):
            errors.append(
                {
                    "source_system": "npi_registry",
                    "source_record_id": f"state={state}&skip={skip}",
                    "error": f"api_rejected_query: {payload.get('Errors')}",
                    "at": utc_now_iso(),
                }
            )
            break

        results = payload.get("results") or []
        if not results:
            break

        for item in results:
            try:
                npi = str(item.get("number") or "").strip()
                basic = item.get("basic") or {}
                org_name_raw = str(basic.get("organization_name") or "").strip()
                org_name = normalize_org_name(org_name_raw) or org_name_raw

                addresses = item.get("addresses") or []
                practice = _pick_address(addresses, "LOCATION")
                mailing = _pick_address(addresses, "MAILING")

                practice_state = (practice.get("state") or "").strip().upper() or None
                mailing_state = (mailing.get("state") or "").strip().upper() or None

                primary_state, basis, confidence = assign_primary_state(practice_state, mailing_state)
                all_states_seen = build_all_states_seen(practice_state, mailing_state, primary_state)

                evidence_urls = [f"https://npiregistry.cms.hhs.gov/provider-view/{npi}"] if npi else []

                row: Dict[str, Any] = {
                    "account_id": "",  # filled post-dedupe
                    "source_system": "npi_registry",
                    "source_record_id": npi,
                    "org_name": org_name_raw or org_name,
                    "org_name_raw": org_name_raw,
                    "entity_type": "provider_org",
                    "parent_org_name": "",
                    "parent_org_id": "",
                    "subtier_primary": "",
                    "subtier_secondary_tags": json.dumps([]),
                    "practice_address_1": practice.get("address_1") or "",
                    "practice_city": practice.get("city") or "",
                    "practice_state": practice.get("state") or "",
                    "practice_postal_code": practice.get("postal_code") or "",
                    "mailing_address_1": mailing.get("address_1") or "",
                    "mailing_city": mailing.get("city") or "",
                    "mailing_state": mailing.get("state") or "",
                    "mailing_postal_code": mailing.get("postal_code") or "",
                    "primary_state": primary_state or "",
                    "all_states_seen": all_states_seen,
                    "multi_state_flag": "true" if "|" in all_states_seen else "false",
                    "source_state_basis": basis,
                    "state_confidence": f"{confidence:.2f}",
                    "website": "",
                    "phone_main": "",
                    "npi_count_est": "1" if npi else "",
                    "pcp_count_est": "",
                    "vbc_signal": "",
                    "bh_signal": "",
                    "exclusion_status": "",
                    "exclusion_reason": "",
                    "evidence_urls": "|".join(evidence_urls),
                    "last_verified_at": utc_now_iso(),
                }

                # NPI Registry fields (website/phone vary); keep conservative.
                row["website"] = str(basic.get("website") or "").strip()
                row["phone_main"] = str(basic.get("authorized_official_telephone_number") or "").strip()
                if not row["phone_main"]:
                    row["phone_main"] = str(basic.get("telephone_number") or "").strip()

                rows.append(row)
                fetched += 1
                if config.npi_registry_max_records_per_state is not None and fetched >= config.npi_registry_max_records_per_state:
                    break
            except Exception as e:  # noqa: BLE001
                errors.append(
                    {
                        "source_system": "npi_registry",
                        "source_record_id": str(item.get("number") or ""),
                        "error": str(e),
                        "at": utc_now_iso(),
                    }
                )

        skip += limit

    return rows, errors


def fetch_nppes_orgs_for_states(config: Config, states: Sequence[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Preferred seeding method: read the downloaded NPPES full replacement monthly CSV locally,
    filter to Entity Type Code == 2 (organizations), and build account-level candidates.

    The NPPES file is large; we stream it in chunks.
    """
    nppes_path = Path(config.nppes_full_csv_path or "").expanduser()
    if not nppes_path.exists():
        return [], [
            {
                "source_system": "nppes_full_csv",
                "source_record_id": str(nppes_path),
                "error": "nppes_full_csv_path_missing_or_not_found",
                "at": utc_now_iso(),
            }
        ]

    states_set = {s.strip().upper() for s in states if s.strip()}
    rows: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    # Column names in NPPES are stable but long; use exact strings.
    # See NPPES documentation for the "NPI Full Replacement Monthly" file layout.
    COL = {
        "npi": "NPI",
        "entity_type": "Entity Type Code",
        "org_legal": "Provider Organization Name (Legal Business Name)",
        "org_dba": "Provider Organization Name (Other Organization Name)",
        "practice_addr1": "Provider First Line Business Practice Location Address",
        "practice_city": "Provider Business Practice Location Address City Name",
        "practice_state": "Provider Business Practice Location Address State Name",
        "practice_zip": "Provider Business Practice Location Address Postal Code",
        "mail_addr1": "Provider First Line Business Mailing Address",
        "mail_city": "Provider Business Mailing Address City Name",
        "mail_state": "Provider Business Mailing Address State Name",
        "mail_zip": "Provider Business Mailing Address Postal Code",
        "phone": "Provider Business Practice Location Address Telephone Number",
        "other_phone": "Provider Business Mailing Address Telephone Number",
        "enumeration_date": "Provider Enumeration Date",
        "last_update": "Last Update Date",
    }

    usecols = [c for c in COL.values()]
    chunksize = int(config.nppes_chunksize)

    LOGGER.info("Reading NPPES CSV in chunks (chunksize=%s): %s", chunksize, nppes_path)
    try:
        it = pd.read_csv(
            nppes_path,
            dtype=str,
            usecols=lambda c: c in set(usecols),
            chunksize=chunksize,
            low_memory=False,
        )
    except Exception as e:  # noqa: BLE001
        return [], [{"source_system": "nppes_full_csv", "source_record_id": str(nppes_path), "error": str(e), "at": utc_now_iso()}]

    for idx, chunk in enumerate(it):
        try:
            chunk = chunk.fillna("")
            # Entity Type Code == 2 (organization)
            chunk = chunk[chunk[COL["entity_type"]].astype(str).str.strip() == "2"]
            if chunk.empty:
                continue

            # Filter to in-scope states if present in either practice or mailing.
            ps = chunk[COL["practice_state"]].astype(str).str.upper().str.strip()
            ms = chunk[COL["mail_state"]].astype(str).str.upper().str.strip()
            mask = ps.isin(states_set) | ms.isin(states_set)
            chunk = chunk[mask]
            if chunk.empty:
                continue

            for _, r in chunk.iterrows():
                npi = str(r.get(COL["npi"], "")).strip()
                org_legal = str(r.get(COL["org_legal"], "")).strip()
                org_dba = str(r.get(COL["org_dba"], "")).strip()
                org_name_raw = org_legal or org_dba
                if not org_name_raw:
                    continue

                practice_state = str(r.get(COL["practice_state"], "")).strip().upper() or None
                mailing_state = str(r.get(COL["mail_state"], "")).strip().upper() or None
                primary_state, basis, confidence = assign_primary_state(practice_state, mailing_state)
                all_states_seen = build_all_states_seen(practice_state, mailing_state, primary_state)

                # Evidence url per NPI; at account-level we keep a pipe-delimited set post-dedupe.
                evidence_url = f"https://npiregistry.cms.hhs.gov/provider-view/{npi}" if npi else ""

                last_verified_at = str(r.get(COL["last_update"], "")).strip() or str(r.get(COL["enumeration_date"], "")).strip()
                dt = parse_iso_or_none(last_verified_at)
                last_verified_at_iso = (dt.astimezone(timezone.utc).replace(microsecond=0).isoformat() if dt else utc_now_iso())

                row: Dict[str, Any] = {
                    "account_id": "",
                    "source_system": "nppes_full_csv",
                    "source_record_id": npi,
                    "org_name": org_name_raw,
                    "org_name_raw": org_name_raw,
                    "entity_type": "provider_org",
                    "parent_org_name": "",
                    "parent_org_id": "",
                    "subtier_primary": "",
                    "subtier_secondary_tags": json.dumps([]),
                    "practice_address_1": str(r.get(COL["practice_addr1"], "")).strip(),
                    "practice_city": str(r.get(COL["practice_city"], "")).strip(),
                    "practice_state": str(r.get(COL["practice_state"], "")).strip().upper(),
                    "practice_postal_code": str(r.get(COL["practice_zip"], "")).strip(),
                    "mailing_address_1": str(r.get(COL["mail_addr1"], "")).strip(),
                    "mailing_city": str(r.get(COL["mail_city"], "")).strip(),
                    "mailing_state": str(r.get(COL["mail_state"], "")).strip().upper(),
                    "mailing_postal_code": str(r.get(COL["mail_zip"], "")).strip(),
                    "primary_state": primary_state or "",
                    "all_states_seen": all_states_seen,
                    "multi_state_flag": "true" if "|" in all_states_seen else "false",
                    "source_state_basis": basis,
                    "state_confidence": f"{confidence:.2f}",
                    "website": "",
                    "phone_main": str(r.get(COL["phone"], "")).strip() or str(r.get(COL["other_phone"], "")).strip(),
                    "npi_count_est": "1" if npi else "",
                    "pcp_count_est": "",
                    "vbc_signal": "",
                    "bh_signal": "",
                    "exclusion_status": "",
                    "exclusion_reason": "",
                    "evidence_urls": evidence_url,
                    "last_verified_at": last_verified_at_iso,
                }
                rows.append(row)
        except Exception as e:  # noqa: BLE001
            errors.append({"source_system": "nppes_full_csv", "source_record_id": f"chunk={idx}", "error": str(e), "at": utc_now_iso()})

    return rows, errors


def _pick_address(addresses: List[Dict[str, Any]], purpose: str) -> Dict[str, str]:
    purpose = purpose.strip().upper()
    for addr in addresses:
        if str(addr.get("address_purpose") or "").strip().upper() == purpose:
            return {
                "address_1": str(addr.get("address_1") or "").strip(),
                "city": str(addr.get("city") or "").strip(),
                "state": str(addr.get("state") or "").strip(),
                "postal_code": str(addr.get("postal_code") or "").strip(),
            }
    return {"address_1": "", "city": "", "state": "", "postal_code": ""}


def maybe_fetch_cms_aco_reach_participants(config: Config) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Optional: download a CMS ACO REACH participant list CSV (if configured) for evidence-only.

    The format of public REACH participant files changes over time; this function is designed to be
    resilient and non-blocking. It returns a DataFrame with best-effort columns:
    - org_name_raw, practice_state, evidence_url
    """
    if not config.cms_aco_reach_participants_csv_url:
        return pd.DataFrame(), []

    cache_path = Path(config.cms_aco_reach_cache_path or "").expanduser() if config.cms_aco_reach_cache_path else None
    errors: List[Dict[str, Any]] = []
    url = config.cms_aco_reach_participants_csv_url

    try:
        if cache_path and cache_path.exists():
            df = pd.read_csv(cache_path)
        else:
            resp = requests.get(url, timeout=60, headers={"User-Agent": "kivira-public-data-pipeline/1.0"})
            resp.raise_for_status()
            content = resp.content
            if cache_path:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_bytes(content)
            df = pd.read_csv(pd.io.common.BytesIO(content))
    except Exception as e:  # noqa: BLE001
        errors.append({"source_system": "cms_aco_reach", "source_record_id": url, "error": str(e), "at": utc_now_iso()})
        return pd.DataFrame(), errors

    # Try to infer likely name/state columns.
    cols = {c.lower().strip(): c for c in df.columns}
    name_col = None
    for key in ["organization name", "legal business name", "participant", "entity name", "aco participant name", "practice name", "provider name"]:
        if key in cols:
            name_col = cols[key]
            break
    if not name_col:
        # Pick the first column that looks like a name.
        for c in df.columns:
            if "name" in c.lower():
                name_col = c
                break

    state_col = None
    for key in ["state", "practice state", "mailing state", "hq state"]:
        if key in cols:
            state_col = cols[key]
            break

    if not name_col:
        errors.append({"source_system": "cms_aco_reach", "source_record_id": url, "error": "could_not_infer_name_column", "at": utc_now_iso()})
        return pd.DataFrame(), errors

    out = pd.DataFrame(
        {
            "org_name_raw": df[name_col].astype(str).fillna(""),
            "practice_state": df[state_col].astype(str).fillna("").str.upper() if state_col else "",
            "evidence_url": url,
        }
    )
    return out, errors


# ---------------------------
# Main pipeline
# ---------------------------
def ensure_output_dirs(output_dir: str) -> Path:
    base = Path(output_dir).expanduser().resolve()
    out = base / "output"
    out.mkdir(parents=True, exist_ok=True)
    return out


def make_seed_table(config: Config) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Produce a seed table (accounts) and a source_errors table.
    """
    all_rows: List[Dict[str, Any]] = []
    all_errors: List[Dict[str, Any]] = []

    # Optional evidence source
    reach_df, reach_errors = maybe_fetch_cms_aco_reach_participants(config)
    all_errors.extend(reach_errors)
    reach_names_by_state: Dict[str, set[str]] = {}
    if not reach_df.empty:
        for _, r in reach_df.iterrows():
            st = str(r.get("practice_state") or "").strip().upper()
            nm = normalize_org_name(str(r.get("org_name_raw") or ""))
            if st and nm:
                reach_names_by_state.setdefault(st, set()).add(nm)

    if config.nppes_full_csv_path:
        nppes_rows, nppes_errors = fetch_nppes_orgs_for_states(config, config.target_states)
        all_rows.extend(nppes_rows)
        all_errors.extend(nppes_errors)
    elif config.use_npi_registry_api:
        for st in config.target_states:
            rows, errors = fetch_npi_registry_orgs_for_state(config, st)
            all_rows.extend(rows)
            all_errors.extend(errors)
    else:
        all_errors.append(
            {
                "source_system": "seed",
                "source_record_id": "",
                "error": "no_seed_source_configured: set --nppes-path (preferred) or --use-npi-api (limited)",
                "at": utc_now_iso(),
            }
        )

    # Best-effort: tag VBC signal if organization name appears in REACH participants for that state.
    for r in all_rows:
        st = (r.get("primary_state") or "").strip().upper()
        nm = normalize_org_name(str(r.get("org_name_raw") or ""))
        if st and nm and nm in reach_names_by_state.get(st, set()):
            r["vbc_signal"] = "ACO_REACH_PARTICIPANT_NAME_MATCH"
            r["evidence_urls"] = _merge_pipe_delimited(r.get("evidence_urls"), config.cms_aco_reach_participants_csv_url or "")

    # Dedupe and generate account_id.
    deduped_rows, dedup_review = dedupe_accounts(all_rows)
    for r in deduped_rows:
        norm = normalize_org_name(str(r.get("org_name_raw") or r.get("org_name") or ""))
        address_key = _address_key(
            r.get("practice_address_1"),
            r.get("practice_city"),
            r.get("practice_state"),
            r.get("practice_postal_code"),
        ) or _address_key(
            r.get("mailing_address_1"),
            r.get("mailing_city"),
            r.get("mailing_state"),
            r.get("mailing_postal_code"),
        )
        primary_state = (r.get("primary_state") or "").strip().upper() or None
        r["account_id"] = _stable_account_id(norm, address_key, primary_state)

        # Ensure schema compliance types.
        if not r.get("subtier_primary"):
            r["subtier_primary"] = ""
        if not r.get("subtier_secondary_tags"):
            r["subtier_secondary_tags"] = json.dumps([])
        if r.get("last_verified_at"):
            # Normalize timestamp format if possible.
            dt = parse_iso_or_none(str(r["last_verified_at"]))
            r["last_verified_at"] = (dt.astimezone(timezone.utc).replace(microsecond=0).isoformat() if dt else utc_now_iso())
        else:
            r["last_verified_at"] = utc_now_iso()

    seed_df = pd.DataFrame(deduped_rows)
    # Force exact schema columns (fill missing).
    for col in SCHEMA_COLUMNS:
        if col not in seed_df.columns:
            seed_df[col] = ""
    seed_df = seed_df[SCHEMA_COLUMNS].fillna("")

    # Review + errors tables
    review_df = pd.DataFrame(dedup_review)
    errors_df = pd.DataFrame(all_errors)

    return seed_df, pd.concat([review_df, errors_df], ignore_index=True)


def write_outputs(config: Config, seed_df: pd.DataFrame, review_and_errors: pd.DataFrame) -> None:
    out_dir = ensure_output_dirs(config.output_dir)

    # Per-state and all
    seed_df = seed_df.copy()
    seed_df["primary_state"] = seed_df["primary_state"].astype(str).str.upper()

    all_path = out_dir / "accounts_seed_all.csv"
    seed_df.to_csv(all_path, index=False)

    for st in config.target_states:
        st = st.strip().upper()
        st_path = out_dir / f"accounts_seed_{st}.csv"
        seed_df[seed_df["primary_state"] == st].to_csv(st_path, index=False)

    # Split review/errors outputs to required file names
    dedup_review_path = out_dir / "dedup_review.csv"
    source_errors_path = out_dir / "source_errors.csv"

    if not review_and_errors.empty:
        # Heuristic: rows with 'reason' are review; rows with 'error' are errors.
        review_cols = [c for c in review_and_errors.columns if c]
        review_df = review_and_errors[review_and_errors.get("reason").notna()] if "reason" in review_and_errors.columns else pd.DataFrame()
        err_df = review_and_errors[review_and_errors.get("error").notna()] if "error" in review_and_errors.columns else pd.DataFrame()

        if not review_df.empty:
            review_df.to_csv(dedup_review_path, index=False, columns=[c for c in review_cols if c in review_df.columns])
        else:
            pd.DataFrame().to_csv(dedup_review_path, index=False)

        if not err_df.empty:
            err_df.to_csv(source_errors_path, index=False, columns=[c for c in review_cols if c in err_df.columns])
        else:
            pd.DataFrame().to_csv(source_errors_path, index=False)
    else:
        pd.DataFrame().to_csv(dedup_review_path, index=False)
        pd.DataFrame().to_csv(source_errors_path, index=False)


def build_default_config(output_dir: str) -> Config:
    return Config(
        target_states=["GA", "NC"],
        output_dir=output_dir,
        rate_limit_per_source=0.35,
        retry_count=3,
    )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Seed GA-first account table from public sources (NPI Registry API).")
    p.add_argument("--output-dir", default=".", help="Base directory containing output/ folder.")
    p.add_argument("--states", default="GA,NC", help="Comma-separated state abbreviations (default GA,NC).")
    p.add_argument("--rate-limit", type=float, default=0.35, help="Min seconds between requests per source.")
    p.add_argument("--retries", type=int, default=3, help="Retry count per request.")
    p.add_argument("--npi-limit", type=int, default=200, help="NPI Registry limit per request (default 200).")
    p.add_argument("--npi-max-per-state", type=int, default=0, help="If >0, cap total NPI results per state.")
    p.add_argument("--use-npi-api", action="store_true", help="Use NPI Registry API (limited; often requires extra criteria).")
    p.add_argument("--nppes-path", default="", help="Path to downloaded NPPES full replacement monthly CSV (preferred).")
    p.add_argument("--nppes-chunksize", type=int, default=200000, help="Chunk size for NPPES CSV streaming.")
    p.add_argument("--cms-reach-csv-url", default="", help="Optional CMS ACO REACH participants CSV URL.")
    p.add_argument("--cms-reach-cache", default="", help="Optional local cache path for REACH CSV.")
    p.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR).")
    return p.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s - %(message)s")

    states = [s.strip().upper() for s in str(args.states).split(",") if s.strip()]
    # Stabilize order: priority order first, then rest.
    states_sorted = [s for s in STATE_PRIORITY_ORDER if s in states] + [s for s in states if s not in STATE_PRIORITY_ORDER]

    config = Config(
        target_states=states_sorted or ["GA", "NC"],
        output_dir=str(args.output_dir),
        rate_limit_per_source=float(args.rate_limit),
        retry_count=int(args.retries),
        npi_registry_limit=int(args.npi_limit),
        npi_registry_max_records_per_state=(int(args.npi_max_per_state) if int(args.npi_max_per_state) > 0 else None),
        use_npi_registry_api=bool(args.use_npi_api),
        nppes_full_csv_path=(str(args.nppes_path).strip() or None),
        nppes_chunksize=int(args.nppes_chunksize),
        cms_aco_reach_participants_csv_url=(str(args.cms_reach_csv_url).strip() or None),
        cms_aco_reach_cache_path=(str(args.cms_reach_cache).strip() or None),
    )

    LOGGER.info("Seeding accounts for states=%s output_dir=%s", config.target_states, config.output_dir)
    seed_df, review_and_errors = make_seed_table(config)
    write_outputs(config, seed_df, review_and_errors)
    LOGGER.info("Done. Seed rows=%s", len(seed_df))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

