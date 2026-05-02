#!/usr/bin/env python3
"""
04_extract_contacts.py

Extract contact candidates from ranked public pages discovered in 03_discover_public_pages.py.

Inputs (defaults under ./output/):
- output/public_pages_GA.csv
- output/public_pages_NC.csv
- output/accounts_classified_GA.csv
- output/accounts_classified_NC.csv

Outputs (under output_dir/output/):
- contacts_raw_GA.csv
- contacts_raw_NC.csv
- contacts_raw_all.csv
- contact_evidence.csv
- contact_review_queue.csv
- contact_extraction_errors.csv

Constraints:
- Public web evidence only. No logins/forms/gated flows.
- Do not scrape LinkedIn; only store LinkedIn URLs explicitly present on source pages.
- Do not guess emails/phones/LinkedIn.

Dependencies: requests, pandas, beautifulsoup4, lxml, extruct, w3lib, python-dateutil, rapidfuzz, stdlib
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import random
import re
import time
from pathlib import Path
from dataclasses import dataclass

from tam_builder.pilot_filters import resolve_output_dir
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from dateutil.parser import isoparse

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception as e:  # noqa: BLE001
    raise RuntimeError("beautifulsoup4 is required for 04_extract_contacts.py") from e

try:
    import extruct  # type: ignore
except Exception:  # noqa: BLE001
    extruct = None

try:
    from w3lib.html import get_base_url  # type: ignore
except Exception:  # noqa: BLE001
    get_base_url = None

try:
    from rapidfuzz import fuzz as _rapidfuzz_fuzz  # type: ignore
except Exception:  # noqa: BLE001
    _rapidfuzz_fuzz = None


LOGGER = logging.getLogger("kivira.contacts")


CONTACTS_COLUMNS: List[str] = [
    "contact_id",
    "account_id",
    "org_name",
    "parent_org_id",
    "primary_state",
    "subtier_primary",
    "subtier_secondary_tags",
    "person_name",
    "first_name",
    "last_name",
    "middle_name",
    "suffix",
    "credentials",
    "job_title",
    "title_normalized",
    "department",
    "seniority_guess",
    "email",
    "email_domain",
    "phone_direct",
    "phone_main",
    "extension",
    "linkedin_profile_url",
    "linkedin_company_url",
    "source_url",
    "source_domain",
    "source_page_type",
    "source_page_priority",
    "source_snippet",
    "extraction_method",
    "extraction_confidence",
    "person_confidence",
    "title_confidence",
    "contact_confidence",
    "exact_name_match_flag",
    "duplicate_person_flag",
    "review_flag",
    "review_reason",
    "last_verified_at",
]


EVIDENCE_COLUMNS: List[str] = [
    "contact_id",
    "evidence_type",
    "evidence_value",
    "evidence_source_url",
    "evidence_snippet",
    "evidence_position",
    "evidence_confidence",
    "last_verified_at",
]


EMAIL_RE = re.compile(r"(?i)\b([a-z0-9._%+\-]+)@([a-z0-9.\-]+\.[a-z]{2,})\b")
OBFUSCATED_EMAIL_RE = re.compile(r"(?i)\b([a-z0-9._%+\-]+)\s*(?:\\[at\\]|\(at\)| at )\s*([a-z0-9.\-]+\.[a-z]{2,})\b")
PHONE_RE = re.compile(r"(?x)(\+?1[\s\-\.])?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}(\s*(?:x|ext\.?|extension)\s*\d{1,6})?")

LINKEDIN_PROFILE_RE = re.compile(r"^https?://([a-z]+\.)?linkedin\.com/in/[^/?#]+/?", re.IGNORECASE)
LINKEDIN_COMPANY_RE = re.compile(r"^https?://([a-z]+\.)?linkedin\.com/company/[^/?#]+/?", re.IGNORECASE)


COMMON_CREDENTIALS = {"MD", "DO", "NP", "FNP", "FNP-C", "PA", "RN", "LCSW", "LMFT", "PHD", "MBA", "MPH", "MSN", "DNP", "PsyD"}
COMMON_SUFFIXES = {"JR", "SR", "II", "III", "IV"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso_or_now(value: str | None) -> str:
    if not value:
        return utc_now_iso()
    try:
        dt = isoparse(str(value))
        return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()
    except Exception:
        return utc_now_iso()


def token_sort_ratio(a: str, b: str) -> int:
    a = (a or "").strip()
    b = (b or "").strip()
    if not a and not b:
        return 100
    if _rapidfuzz_fuzz is not None:
        return int(_rapidfuzz_fuzz.token_sort_ratio(a, b))
    import difflib

    def norm_tokens(s: str) -> str:
        toks = [t for t in re.split(r"\s+", s.upper()) if t]
        toks.sort()
        return " ".join(toks)

    return int(round(difflib.SequenceMatcher(a=norm_tokens(a), b=norm_tokens(b)).ratio() * 100))


def canonicalize_url(url: str) -> str:
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
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return f"{scheme}://{netloc}{path}"


def extract_emails(text: str) -> Tuple[List[str], bool]:
    """
    Returns (emails, obfuscated_found)
    """
    found: List[str] = []
    for m in EMAIL_RE.finditer(text or ""):
        email = f"{m.group(1)}@{m.group(2)}".lower()
        if email not in found:
            found.append(email)
    obf = False
    if not found:
        for m in OBFUSCATED_EMAIL_RE.finditer(text or ""):
            obf = True
            email = f"{m.group(1)}@{m.group(2)}".lower()
            if email not in found:
                found.append(email)
    return found, obf


def extract_phones(text: str) -> List[Tuple[str, str]]:
    """
    Returns list of (phone, extension) where extension may be ''.
    """
    out: List[Tuple[str, str]] = []
    for m in PHONE_RE.finditer(text or ""):
        raw = m.group(0).strip()
        ext = ""
        ext_match = re.search(r"(?i)(?:x|ext\.?|extension)\s*(\d{1,6})", raw)
        if ext_match:
            ext = ext_match.group(1)
        # normalize phone digits
        digits = re.sub(r"\D", "", raw)
        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]
        if len(digits) != 10:
            continue
        phone = f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
        tup = (phone, ext)
        if tup not in out:
            out.append(tup)
    return out


def split_name(name: str) -> Tuple[str, str, str, str, str, str]:
    """
    Returns:
    person_name, first, last, middle, suffix, credentials
    """
    raw = " ".join((name or "").replace(",", " ").split())
    if not raw:
        return "", "", "", "", "", ""

    parts = raw.split()
    creds: List[str] = []
    suf = ""

    # Pull trailing credentials/suffixes (e.g., "John Doe, MD")
    while parts:
        token = parts[-1].strip(".").upper()
        if token in COMMON_SUFFIXES and not suf:
            suf = token
            parts = parts[:-1]
            continue
        if token in COMMON_CREDENTIALS:
            creds.insert(0, parts[-1].strip(","))
            parts = parts[:-1]
            continue
        break

    if len(parts) == 1:
        return raw, parts[0], "", "", suf, " ".join(creds)

    first = parts[0]
    last = parts[-1]
    middle = " ".join(parts[1:-1]) if len(parts) > 2 else ""
    return raw, first, last, middle, suf, " ".join(creds)


def normalize_contact_dedupe_field(value: str) -> str:
    """Lowercase + collapse whitespace for stable dedupe keys."""
    return " ".join((value or "").lower().split())


def normalize_title(title: str) -> str:
    t = " ".join((title or "").split())
    if not t:
        return ""
    # common normalizations
    repl = {
        "CMO": "Chief Medical Officer",
        "CIO": "Chief Information Officer",
        "COO": "Chief Operating Officer",
        "CEO": "Chief Executive Officer",
        "VP Pop Health": "VP Population Health",
        "Pop Health": "Population Health",
        "Care Mgmt": "Care Management",
        "Dir.": "Director",
        "Mgr.": "Manager",
    }
    # token-level replace (conservative)
    for k, v in repl.items():
        if t.strip().upper() == k.upper():
            return v
    # phrase replacements
    t2 = t
    t2 = re.sub(r"(?i)\bVP\s+Pop\s+Health\b", "VP Population Health", t2)
    t2 = re.sub(r"(?i)\bDirector,\s*Care\s+Mgmt\b", "Director of Care Management", t2)
    return t2


def guess_seniority(title: str, credentials: str) -> str:
    t = (title or "").lower()
    c = (credentials or "").upper()
    if any(x in t for x in ["chief ", " cmo", " ceo", " coo", " cfo", "president"]):
        return "executive"
    if "vp" in t or "vice president" in t:
        return "vp"
    if "director" in t or "head of" in t:
        return "director"
    if "manager" in t:
        return "manager"
    if "cmio" in t or "informatics" in t or "it" in t or "security" in t:
        return "technical"
    if c in {"MD", "DO"} or any(x in c for x in ["MD", "DO", "NP", "PA"]):
        return "physician_leader"
    if "administrator" in t or "practice" in t or "operations" in t:
        return "admin"
    return "unknown"


def score_contact_candidate(
    *,
    has_full_name: bool,
    has_title: bool,
    has_email: bool,
    has_phone: bool,
    has_linkedin: bool,
    page_type: str,
    page_priority: int,
) -> Tuple[float, float, float, float]:
    """
    Returns (extraction_confidence, person_confidence, title_confidence, contact_confidence).
    """
    base = 0.30
    if page_type in {"provider_profile", "bio"}:
        base += 0.20
    if page_type in {"leadership", "provider_directory"}:
        base += 0.10
    if page_priority == 1:
        base += 0.10
    if page_priority == 2:
        base += 0.05

    person = base + (0.25 if has_full_name else 0.0)
    title = base + (0.25 if has_title else 0.0)
    contact = base + (0.20 if has_email else 0.0) + (0.15 if has_phone else 0.0) + (0.10 if has_linkedin else 0.0)

    extraction = min(1.0, (person + title + contact) / 3.0)
    return min(1.0, extraction), min(1.0, person), min(1.0, title), min(1.0, contact)


def stable_contact_id(account_id: str, person_name: str, title_norm: str, source_domain: str) -> str:
    raw = f"{account_id}||{person_name}||{title_norm}||{source_domain}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]


def extract_jsonld_people(html: str, page_url: str) -> List[Dict[str, Any]]:
    """
    Returns list of dicts with keys: name, job_title, email, phone, linkedin_profile_url, snippet
    """
    if not html or extruct is None:
        return []
    base_url = page_url
    if get_base_url is not None:
        try:
            base_url = get_base_url(html, page_url)
        except Exception:
            base_url = page_url
    try:
        data = extruct.extract(html, base_url=base_url, syntaxes=["json-ld"], uniform=True)  # type: ignore
    except Exception:
        return []
    out: List[Dict[str, Any]] = []
    for obj in data.get("json-ld", []) if isinstance(data, dict) else []:
        if not isinstance(obj, dict):
            continue
        typ = obj.get("@type") or obj.get("type")
        if isinstance(typ, list):
            typ = ",".join(str(x) for x in typ)
        typ_s = str(typ or "").lower()
        if "person" not in typ_s:
            continue
        name = str(obj.get("name") or "").strip()
        job = str(obj.get("jobTitle") or obj.get("job_title") or "").strip()
        email = str(obj.get("email") or "").strip()
        phone = str(obj.get("telephone") or "").strip()
        same_as = obj.get("sameAs") or obj.get("same_as") or []
        linkedin = ""
        if isinstance(same_as, str):
            same_as = [same_as]
        if isinstance(same_as, list):
            for u in same_as:
                cu = canonicalize_url(str(u))
                if LINKEDIN_PROFILE_RE.match(cu):
                    linkedin = cu
                    break
        if name:
            out.append(
                {
                    "name": name,
                    "job_title": job,
                    "email": email,
                    "phone": phone,
                    "linkedin_profile_url": linkedin,
                    "snippet": f"JSON-LD Person: {name}" + (f" — {job}" if job else ""),
                    "method": "jsonld",
                }
            )
    return out


def extract_microformat_people(html: str, page_url: str) -> List[Dict[str, Any]]:
    """
    Best-effort microformats/vcard extraction via extruct when available.
    """
    if not html or extruct is None:
        return []
    base_url = page_url
    if get_base_url is not None:
        try:
            base_url = get_base_url(html, page_url)
        except Exception:
            base_url = page_url
    try:
        data = extruct.extract(html, base_url=base_url, syntaxes=["microformat", "rdfa"], uniform=True)  # type: ignore
    except Exception:
        return []
    out: List[Dict[str, Any]] = []
    # Uniform microformat output varies; keep conservative.
    for item in data.get("microformat", []) if isinstance(data, dict) else []:
        if not isinstance(item, dict):
            continue
        props = item.get("properties") or {}
        name = ""
        if isinstance(props.get("name"), list) and props.get("name"):
            name = str(props["name"][0]).strip()
        job = ""
        if isinstance(props.get("job-title"), list) and props.get("job-title"):
            job = str(props["job-title"][0]).strip()
        email = ""
        if isinstance(props.get("email"), list) and props.get("email"):
            email = str(props["email"][0]).strip()
        tel = ""
        if isinstance(props.get("tel"), list) and props.get("tel"):
            tel = str(props["tel"][0]).strip()
        if name:
            out.append(
                {
                    "name": name,
                    "job_title": job,
                    "email": email,
                    "phone": tel,
                    "linkedin_profile_url": "",
                    "snippet": f"Microformat: {name}" + (f" — {job}" if job else ""),
                    "method": "microformat",
                }
            )
    return out


def extract_visible_people(html: str, page_url: str, page_type: str) -> List[Dict[str, Any]]:
    """
    Heuristic visible HTML extraction for staff/provider cards.
    """
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    out: List[Dict[str, Any]] = []

    # Candidate containers: cards or list items with staff/provider hints.
    containers = soup.select(
        ".team, .staff, .provider, .providers, .leadership, .bio, .card, .profile, .directory, .physician, .doctor"
    )
    # If none, fall back to sections.
    if not containers:
        containers = soup.find_all(["article", "section", "li", "div"], limit=250)

    for el in containers[:250]:
        text = " ".join(el.get_text(" ").split())
        if len(text) < 20:
            continue
        # Find a likely name: look for strong tags or headings inside.
        name = ""
        for tag in el.find_all(["h1", "h2", "h3", "strong"], limit=3):
            cand = " ".join(tag.get_text(" ").split())
            if 2 <= len(cand.split()) <= 5 and any(ch.isalpha() for ch in cand):
                name = cand
                break
        if not name:
            continue

        # Title: next span/p or class hint
        job = ""
        for tag in el.find_all(["p", "span", "div"], limit=6):
            cand = " ".join(tag.get_text(" ").split())
            if not cand:
                continue
            if cand == name:
                continue
            # Filter out long paragraphs
            if 2 <= len(cand.split()) <= 12 and any(k in cand.lower() for k in ["chief", "director", "vp", "manager", "officer", "md", "do", "nurse", "administrator"]):
                job = cand
                break

        # Emails / phones from element scope
        emails, _ = extract_emails(text)
        phones = extract_phones(text)

        # LinkedIn link if present
        linkedin = ""
        for a in el.find_all("a", href=True, limit=10):
            href = canonicalize_url(urljoin(page_url, str(a.get("href") or "")))
            if LINKEDIN_PROFILE_RE.match(href):
                linkedin = href
                break

        out.append(
            {
                "name": name,
                "job_title": job,
                "email": emails[0] if emails else "",
                "phone": phones[0][0] if phones else "",
                "extension": phones[0][1] if phones else "",
                "linkedin_profile_url": linkedin,
                "snippet": (text[:240] + ("…" if len(text) > 240 else "")),
                "method": "visible_html",
            }
        )

    return out


def extract_linkedin_company_from_page(html: str, page_url: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    for a in soup.find_all("a", href=True):
        href = canonicalize_url(urljoin(page_url, str(a.get("href") or "")))
        if LINKEDIN_COMPANY_RE.match(href):
            return href
    return ""


def dedupe_contacts(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Dedupe within account on normalized full name + normalized title + source_domain.
    Keep multiple source URLs but mark duplicate_person_flag.
    """
    seen: Dict[Tuple[str, str, str, str], int] = {}
    out: List[Dict[str, Any]] = []
    for r in rows:
        acct = str(r.get("account_id") or "")
        name = normalize_contact_dedupe_field(str(r.get("person_name") or ""))
        title = normalize_contact_dedupe_field(
            normalize_title(str(r.get("title_normalized") or r.get("job_title") or ""))
        )
        dom = str(r.get("source_domain") or "")
        key = (acct, name, title, dom)
        if key in seen:
            r["duplicate_person_flag"] = "true"
        else:
            seen[key] = 1
            r["duplicate_person_flag"] = "false"
        out.append(r)
    return out


def make_contact_rows_for_page(
    page_row: Dict[str, Any],
    account_row: Dict[str, Any],
    html: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Returns (contacts, evidence_rows, error_rows)
    """
    contacts: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    account_id = str(account_row.get("account_id") or "").strip()
    org_name = str(account_row.get("org_name") or "").strip()
    parent_org_id = str(account_row.get("parent_org_id") or "").strip()
    primary_state = str(account_row.get("primary_state") or "").strip().upper()
    subtier_primary = str(account_row.get("subtier_primary") or "").strip().upper()
    subtier_secondary_tags = str(account_row.get("subtier_secondary_tags") or "").strip()

    source_url = str(page_row.get("discovered_url") or "").strip()
    source_domain = urlparse(source_url).netloc.lower()
    source_page_type = str(page_row.get("page_type") or "").strip()
    source_page_priority = str(page_row.get("page_priority") or "").strip()
    linkedin_company_url = str(page_row.get("linkedin_company_url") or "").strip()
    last_verified_at = parse_iso_or_now(str(page_row.get("last_verified_at") or account_row.get("last_verified_at") or ""))

    # Page-scope links (company linkedin as fallback)
    page_linkedin_company = extract_linkedin_company_from_page(html, source_url)
    if page_linkedin_company and not linkedin_company_url:
        linkedin_company_url = page_linkedin_company

    # Extract candidates from multiple methods
    candidates: List[Dict[str, Any]] = []
    candidates.extend(extract_jsonld_people(html, source_url))
    candidates.extend(extract_microformat_people(html, source_url))
    candidates.extend(extract_visible_people(html, source_url, source_page_type))

    # If we found no candidates but page has mailto/tel, we still produce a review stub
    page_text = " ".join(BeautifulSoup(html or "", "lxml").get_text(" ").split())
    page_emails, obf = extract_emails(page_text)
    page_phones = extract_phones(page_text)

    if not candidates and (page_emails or page_phones):
        candidates.append(
            {
                "name": "",
                "job_title": "",
                "email": page_emails[0] if page_emails else "",
                "phone": page_phones[0][0] if page_phones else "",
                "extension": page_phones[0][1] if page_phones else "",
                "linkedin_profile_url": "",
                "snippet": (page_text[:240] + ("…" if len(page_text) > 240 else "")),
                "method": "page_level_contact",
            }
        )

    for cand in candidates[:200]:
        name_raw = str(cand.get("name") or "").strip()
        job_title = str(cand.get("job_title") or "").strip()
        email = str(cand.get("email") or "").strip().lower()
        phone = str(cand.get("phone") or "").strip()
        extension = str(cand.get("extension") or "").strip()
        linkedin_profile_url = canonicalize_url(str(cand.get("linkedin_profile_url") or "").strip())
        snippet = str(cand.get("snippet") or "").strip()
        method = str(cand.get("method") or "unknown").strip()

        person_name, first, last, middle, suffix, credentials = split_name(name_raw)
        title_norm = normalize_title(job_title)
        seniority = guess_seniority(title_norm or job_title, credentials)

        has_full_name = bool(first and last)
        has_title = bool(job_title)
        has_email = bool(email and EMAIL_RE.search(email))
        has_phone = bool(phone)
        has_linkedin = bool(linkedin_profile_url and LINKEDIN_PROFILE_RE.match(linkedin_profile_url))
        page_pri = int(source_page_priority) if source_page_priority.isdigit() else 5

        extraction_conf, person_conf, title_conf, contact_conf = score_contact_candidate(
            has_full_name=has_full_name,
            has_title=has_title,
            has_email=has_email,
            has_phone=has_phone,
            has_linkedin=has_linkedin,
            page_type=source_page_type,
            page_priority=page_pri,
        )

        review_flag = False
        review_reasons: List[str] = []
        if not has_full_name and name_raw:
            review_flag = True
            review_reasons.append("partial_name")
        if name_raw and not has_title and source_page_type in {"leadership", "bio", "provider_profile"}:
            review_flag = True
            review_reasons.append("missing_title")
        if obf:
            review_flag = True
            review_reasons.append("email_obfuscated")
        if linkedin_profile_url and not LINKEDIN_PROFILE_RE.match(linkedin_profile_url):
            review_flag = True
            review_reasons.append("linkedin_profile_malformed")
        if not name_raw and (email or phone):
            review_flag = True
            review_reasons.append("contact_without_name")

        # Map phones: if leadership/provider profile, treat as direct; if contact page, treat as main
        phone_direct = ""
        phone_main = ""
        if phone:
            if source_page_type in {"provider_profile", "bio"}:
                phone_direct = phone
            elif source_page_type in {"contact"} and not has_full_name:
                phone_main = phone
            else:
                # ambiguous: store as phone_main unless we have a named person
                phone_direct = phone if has_full_name else ""
                phone_main = phone if not has_full_name else ""

        email_domain = ""
        if email and "@" in email:
            email_domain = email.split("@", 1)[1].lower()

        contact_id = stable_contact_id(account_id, person_name or email or phone or source_url, title_norm or job_title, source_domain)

        evidence_note = ""
        if name_raw and job_title:
            evidence_note = f"{source_page_type} page lists {name_raw} as {job_title}"
        elif name_raw:
            evidence_note = f"{source_page_type} page lists {name_raw}"
        elif email or phone:
            evidence_note = f"{source_page_type} page shows contact info without named person"
        else:
            evidence_note = f"{source_page_type} page parsed with weak signals"

        row: Dict[str, Any] = {
            "contact_id": contact_id,
            "account_id": account_id,
            "org_name": org_name,
            "parent_org_id": parent_org_id,
            "primary_state": primary_state,
            "subtier_primary": subtier_primary,
            "subtier_secondary_tags": subtier_secondary_tags or json.dumps([]),
            "person_name": person_name,
            "first_name": first,
            "last_name": last,
            "middle_name": middle,
            "suffix": suffix,
            "credentials": credentials,
            "job_title": job_title,
            "title_normalized": title_norm,
            "department": "",
            "seniority_guess": seniority,
            "email": email,
            "email_domain": email_domain,
            "phone_direct": phone_direct,
            "phone_main": phone_main,
            "extension": extension,
            "linkedin_profile_url": linkedin_profile_url if LINKEDIN_PROFILE_RE.match(linkedin_profile_url or "") else "",
            "linkedin_company_url": linkedin_company_url if LINKEDIN_COMPANY_RE.match(linkedin_company_url or "") else "",
            "source_url": source_url,
            "source_domain": source_domain,
            "source_page_type": source_page_type,
            "source_page_priority": source_page_priority,
            "source_snippet": snippet[:500],
            "extraction_method": method,
            "extraction_confidence": f"{extraction_conf:.2f}",
            "person_confidence": f"{person_conf:.2f}",
            "title_confidence": f"{title_conf:.2f}",
            "contact_confidence": f"{contact_conf:.2f}",
            "exact_name_match_flag": "false",
            "duplicate_person_flag": "false",
            "review_flag": "true" if review_flag else "false",
            "review_reason": ";".join(review_reasons),
            "last_verified_at": last_verified_at,
        }

        # Ensure exact columns exist
        for c in CONTACTS_COLUMNS:
            if c not in row:
                row[c] = ""
            if row[c] is None:
                row[c] = ""
            if not isinstance(row[c], str):
                row[c] = str(row[c])

        contacts.append({c: row.get(c, "") for c in CONTACTS_COLUMNS})

        # Evidence rows per extracted field
        pos = "page"
        if person_name:
            evidence.append(_e(contact_id, "name", person_name, source_url, snippet, pos, person_conf, last_verified_at))
        if job_title:
            evidence.append(_e(contact_id, "title", job_title, source_url, snippet, pos, title_conf, last_verified_at))
        if title_norm and title_norm != job_title:
            evidence.append(_e(contact_id, "title_normalized", title_norm, source_url, snippet, pos, title_conf, last_verified_at))
        if email:
            evidence.append(_e(contact_id, "email", email, source_url, snippet, pos, contact_conf, last_verified_at))
        if phone:
            evidence.append(_e(contact_id, "phone", phone, source_url, snippet, pos, contact_conf, last_verified_at))
        if linkedin_profile_url:
            evidence.append(_e(contact_id, "linkedin_profile_url", linkedin_profile_url, source_url, snippet, pos, contact_conf, last_verified_at))
        if linkedin_company_url:
            evidence.append(_e(contact_id, "linkedin_company_url", linkedin_company_url, source_url, snippet, pos, 0.60, last_verified_at))

        # Evidence note
        evidence.append(_e(contact_id, "evidence_note", evidence_note, source_url, snippet, pos, extraction_conf, last_verified_at))

    return contacts, evidence, errors


def _e(
    contact_id: str,
    evidence_type: str,
    evidence_value: str,
    url: str,
    snippet: str,
    position: str,
    confidence: float,
    last_verified_at: str,
) -> Dict[str, Any]:
    row = {
        "contact_id": contact_id,
        "evidence_type": evidence_type,
        "evidence_value": str(evidence_value or "").strip(),
        "evidence_source_url": url,
        "evidence_snippet": (snippet or "")[:500],
        "evidence_position": position,
        "evidence_confidence": f"{float(confidence):.2f}",
        "last_verified_at": last_verified_at,
    }
    return {c: row.get(c, "") for c in EVIDENCE_COLUMNS}


@dataclass(frozen=True)
class CrawlConfig:
    rate_limit_s: float = 0.50
    retry_count: int = 2
    timeout_s: int = 20
    max_pages_per_account: int = 8
    max_total_pages: int = 2000
    max_page_priority: int = 2  # only crawl top priorities by default


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


def fetch_html(
    session: requests.Session,
    limiter: RateLimiter,
    url: str,
    *,
    retry_count: int,
    timeout_s: int,
) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    last_err: Optional[str] = None
    for attempt in range(retry_count + 1):
        limiter.wait()
        try:
            resp = session.get(url, timeout=timeout_s, headers={"User-Agent": "kivira-contact-extractor/1.0"})
            status = int(resp.status_code)
            if status >= 400:
                return None, status, f"http_{status}"
            ctype = str(resp.headers.get("content-type") or "").lower()
            if "text/html" not in ctype and "application/xhtml" not in ctype and "xml" not in ctype:
                # skip non-html
                return None, status, f"unsupported_content_type:{ctype}"
            return resp.text, status, None
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
            backoff = (2**attempt) + random.random()
            time.sleep(backoff)
    return None, None, last_err


def read_csv_safe(path: pd.io.common.FilePath) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def build_account_index(classified_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    idx: Dict[str, Dict[str, Any]] = {}
    for r in classified_df.to_dict(orient="records"):
        aid = str(r.get("account_id") or "").strip()
        if aid:
            idx[aid] = r
    return idx


def pick_pages_for_account(public_pages_df: pd.DataFrame, account_id: str, cfg: CrawlConfig) -> pd.DataFrame:
    df = public_pages_df[public_pages_df["account_id"].astype(str) == str(account_id)].copy()
    if df.empty:
        return df
    # Only crawl allowed
    df["crawl_allowed"] = df["crawl_allowed"].astype(str).str.lower()
    df = df[df["crawl_allowed"].isin(["true", "1", "yes", ""])].copy()
    # rank by priority then confidence
    def pri(x: str) -> int:
        try:
            return int(str(x))
        except Exception:
            return 5

    def conf(x: str) -> float:
        try:
            return float(str(x))
        except Exception:
            return 0.0

    df = df.sort_values(
        by=["page_priority", "discovery_confidence"],
        ascending=[True, False],
        key=lambda s: s.map(pri) if s.name == "page_priority" else s.map(conf),
    )
    # cap by priority threshold and per-account count
    df = df[df["page_priority"].map(pri) <= cfg.max_page_priority].head(cfg.max_pages_per_account)
    return df


def write_contacts_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    df = pd.DataFrame(rows)
    for c in CONTACTS_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    df[CONTACTS_COLUMNS].to_csv(path, index=False)


def write_evidence_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    df = pd.DataFrame(rows)
    for c in EVIDENCE_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    df[EVIDENCE_COLUMNS].to_csv(path, index=False)


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Extract contact candidates from discovered public pages.")
    p.add_argument("--base-dir", default=".", help="Base directory containing output/ and optional input/.")
    p.add_argument("--states", default="GA,NC", help="Comma-separated states to process.")
    p.add_argument("--rate-limit", type=float, default=0.50, help="Min seconds between requests.")
    p.add_argument("--retries", type=int, default=2, help="Retry count per request.")
    p.add_argument("--timeout", type=int, default=20, help="Request timeout seconds.")
    p.add_argument("--max-pages-per-account", type=int, default=8, help="Max pages fetched per account.")
    p.add_argument("--max-total-pages", type=int, default=2000, help="Safety cap on total pages fetched.")
    p.add_argument("--max-page-priority", type=int, default=2, help="Only crawl pages with priority <= this.")
    p.add_argument("--log-level", default="INFO", help="Logging level.")
    p.add_argument(
        "--output-subdir",
        default="",
        help="Read/write under output/<subdir>/ (match 03 pilot run, e.g. pilot).",
    )
    p.add_argument(
        "--pilot-scale-page-cap",
        action="store_true",
        help="Raise page limit to max(--max-total-pages, 8 * accounts in slice), capped at 50000.",
    )
    args = p.parse_args(argv)

    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s - %(message)s")

    base_dir = Path(args.base_dir).expanduser().resolve()
    out_dir = resolve_output_dir(base_dir, str(args.output_subdir or ""))

    cfg = CrawlConfig(
        rate_limit_s=float(args.rate_limit),
        retry_count=int(args.retries),
        timeout_s=int(args.timeout),
        max_pages_per_account=int(args.max_pages_per_account),
        max_total_pages=int(args.max_total_pages),
        max_page_priority=int(args.max_page_priority),
    )

    states = [s.strip().upper() for s in str(args.states).split(",") if s.strip()]

    all_contacts: List[Dict[str, Any]] = []
    all_evidence: List[Dict[str, Any]] = []
    all_errors: List[Dict[str, Any]] = []

    session = requests.Session()
    limiter = RateLimiter(cfg.rate_limit_s)

    for st in states:
        public_pages_path = out_dir / f"public_pages_{st}.csv"
        classified_path = out_dir / f"accounts_classified_{st}.csv"
        if not public_pages_path.exists() or not classified_path.exists():
            LOGGER.warning("Missing inputs for %s (skipping): %s %s", st, public_pages_path, classified_path)
            continue

        LOGGER.info("Extracting contacts for %s", st)
        pages_df = read_csv_safe(public_pages_path)
        classified_df = read_csv_safe(classified_path)
        acct_idx = build_account_index(classified_df)

        page_cap = int(cfg.max_total_pages)
        if bool(args.pilot_scale_page_cap) and acct_idx:
            page_cap = max(page_cap, min(50000, len(acct_idx) * 8))
            LOGGER.info("Pilot-scaled page cap for %s: %s (accounts=%s)", st, page_cap, len(acct_idx))

        contacts_state: List[Dict[str, Any]] = []

        fetched_pages = 0
        for account_id, acct in acct_idx.items():
            if fetched_pages >= page_cap:
                break
            page_subset = pick_pages_for_account(pages_df, account_id, cfg)
            if page_subset.empty:
                # Review stub if no pages
                contacts_state.append(
                    {c: "" for c in CONTACTS_COLUMNS}
                    | {
                        "contact_id": stable_contact_id(account_id, "NO_PAGES", "", ""),
                        "account_id": account_id,
                        "org_name": str(acct.get("org_name") or ""),
                        "parent_org_id": str(acct.get("parent_org_id") or ""),
                        "primary_state": str(acct.get("primary_state") or "").upper(),
                        "subtier_primary": str(acct.get("subtier_primary") or "").upper(),
                        "subtier_secondary_tags": str(acct.get("subtier_secondary_tags") or json.dumps([])),
                        "review_flag": "true",
                        "review_reason": "no_discovered_pages",
                        "last_verified_at": parse_iso_or_now(str(acct.get("last_verified_at") or "")),
                    }
                )
                continue

            for pr in page_subset.to_dict(orient="records"):
                url = canonicalize_url(str(pr.get("discovered_url") or ""))
                if not url:
                    continue
                fetched_pages += 1
                if fetched_pages > page_cap:
                    break

                html, status, err = fetch_html(
                    session,
                    limiter,
                    url,
                    retry_count=cfg.retry_count,
                    timeout_s=cfg.timeout_s,
                )
                if err or not html:
                    all_errors.append(
                        {
                            "account_id": account_id,
                            "org_name": str(acct.get("org_name") or ""),
                            "source_url": url,
                            "error": err or "",
                            "http_status": str(status or ""),
                            "at": utc_now_iso(),
                        }
                    )
                    continue

                page_contacts, page_evidence, _ = make_contact_rows_for_page(pr, acct, html)
                contacts_state.extend(page_contacts)
                all_evidence.extend(page_evidence)

        # Dedupe + mark duplicates
        contacts_state = dedupe_contacts(contacts_state)

        # Write per-state outputs
        write_contacts_csv(out_dir / f"contacts_raw_{st}.csv", contacts_state)
        all_contacts.extend(contacts_state)

    # Write all outputs
    all_contacts = dedupe_contacts(all_contacts)
    write_contacts_csv(out_dir / "contacts_raw_all.csv", all_contacts)
    write_evidence_csv(out_dir / "contact_evidence.csv", all_evidence)

    # Review queue: review_flag true
    df_all = pd.DataFrame(all_contacts)
    if not df_all.empty:
        review_df = df_all[df_all["review_flag"].astype(str).str.lower() == "true"].copy()
        write_contacts_csv(out_dir / "contact_review_queue.csv", review_df.to_dict(orient="records"))
    else:
        write_contacts_csv(out_dir / "contact_review_queue.csv", [])

    err_df = pd.DataFrame(all_errors)
    (out_dir / "contact_extraction_errors.csv").write_text(
        err_df.to_csv(index=False) if not err_df.empty else "account_id,org_name,source_url,error,http_status,at\n",
        encoding="utf-8",
    )

    LOGGER.info("Done. Contacts=%s Evidence=%s Errors=%s", len(all_contacts), len(all_evidence), len(all_errors))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

