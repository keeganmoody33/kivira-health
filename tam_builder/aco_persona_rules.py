"""Tier 2A ACO persona classification and anti-persona filters.

Canonical patterns align with [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] Tier 2A.
Used by scripts/build_aco_persona_heyreach.py and HeyReach list QA.
"""

from __future__ import annotations

import re
from typing import Iterable

# Ordered: most specific first. (pattern, bucket, confidence)
PERSONA_RULES: list[tuple[str, str, str]] = [
    (r"chief behavioral health officer|behavioral health medical director", "clin_champ", "H"),
    (r"director of behavioral health|director of bh|vp behavioral health|"
     r"behavioral health director|director, behavioral health", "bh_quality", "H"),
    (r"(?:director|administrator|administrative director|regional director|"
     r"clinical director|program director).*\bbehavioral\b", "bh_quality", "M"),
    (r"\bbh integration\b|bh program", "bh_quality", "M"),
    (r"\bcmo\b|chief medical officer|chief clinical officer", "clin_champ", "H"),
    (r"medical director.*population health|population health.*medical director", "clin_champ", "H"),
    (r"medical director.*(?:quality|value[ -]based|aco)", "clin_champ", "H"),
    (r"physician executive|vp medical|vp clinical|chief physician", "clin_champ", "M"),
    (r"director.*clinical (?:initiatives|programs|integration|operations|quality)", "clin_champ", "M"),
    (r"medical director", "clin_champ", "M"),
    (r"vp population health|vice president[, ]+population health|"
     r"svp population health", "op_owner", "H"),
    (r"(?:executive |senior |regional |sr\.? )?director[, ]+population health|"
     r"director of population health|director.*\bpopulation health\b", "op_owner", "H"),
    (r"director of care coordination|director of value[ -]based|"
     r"vp value[ -]based|vp care management", "op_owner", "H"),
    (r"director of network performance|risk operations leader|"
     r"director of aco|aco.*operations", "op_owner", "M"),
    (r"director,? care management|director of programs|"
     r"director of operations", "op_owner", "M"),
    (r"vp quality|director of quality (?:improvement|measurement|programs|operations)|"
     r"quality performance director|stars program director|"
     r"director,? hedis|hedis director", "bh_quality", "M"),
    (r"chief executive officer|\bceo\b|^president\b|\bpresident\b at |"
     r"\bsvp\b.*(?:clinical|medical)", "econ_buyer", "H"),
    (r"chief financial officer|\bcfo\b", "econ_buyer", "H"),
    (r"chief operating officer|\bcoo\b", "econ_buyer", "M"),
    (r"executive director", "econ_buyer", "M"),
    (r"president\b", "econ_buyer", "M"),
    (r"chief medical information officer|\bcmio\b", "tech_gate", "H"),
    (r"\bcio\b|chief information officer|chief technology officer|\bcto\b", "tech_gate", "H"),
    (r"director of analytics|vp data|interoperability|"
     r"director.*analytics", "tech_gate", "M"),
    (r"health it director|director of clinical analytics", "tech_gate", "M"),
    (r"chief population health officer", "econ_buyer", "H"),
    (r"physician.*(?:population health|value[ -]based|aco|quality)", "clin_champ", "M"),
    (r"population health (?:manager|specialist|coordinator|analyst|"
     r"administrator|consultant|lead)", "op_owner", "M"),
    (r"(?:value[ -]based|vbc).*(?:director|manager|leader|lead|administrator)", "op_owner", "M"),
    (r"aco (?:practice engagement|engagement|operations|administrator|"
     r"administration|manager|coordinator|specialist|analyst|lead)", "op_owner", "M"),
    (r"care management.*(?:director|manager|administrator)|"
     r"director.*care management", "op_owner", "M"),
    (r"quality (?:improvement|measurement|management|analyst|specialist).*"
     r"(?:lead|coordinator|manager|administrator)", "bh_quality", "M"),
    (r"\bvp\b|vice president", "op_owner", "L"),
    (r"\bdirector\b", "op_owner", "L"),
    (r"\bmanager\b.*(?:health|care|quality|operations|practice)|"
     r"(?:health|care|quality|operations|practice).*\bmanager\b", "op_owner", "L"),
    (r"\badministrator\b.*(?:health|care|quality|operations|practice|aco)|"
     r"(?:health|care|quality|operations|practice|aco).*\badministrator\b", "op_owner", "L"),
]

# Wave 1 anti-persona patterns (list-build time). See PERSONA_TITLE_DICTIONARY §Anti-Persona.
ANTI_PERSONA_TITLE_RE = re.compile(
    r"(?:\bgtm engineer\b|\brecruiter\b|\boutside sales\b|\bvirtual assistant\b|"
    r"\bwealth advisor\b|\bfinancial advisor\b|\bsales development\b|"
    r"\blead generation\b|\bventure scout\b|\bpharmacy operations\b|\bpublisher\b|"
    r"\baccount executive\b|\bbusiness development representative\b|\bsdr\b|\bbdr\b)",
    re.IGNORECASE,
)

ANTI_PERSONA_COMPANY_RE = re.compile(
    r"(?:salesforge|heyreach|premium inboxes|warmleads|leadsfriday|hotglue|"
    r"quiklynx|airops|teleport|unstructured|cardone ventures|peopleperhour|upwork|"
    r"hcltech|edward jones)",
    re.IGNORECASE,
)

# CMS placeholder exec title — not an operating pop-health buyer for LinkedIn persona load.
CMS_PLACEHOLDER_EXEC_RE = re.compile(
    r"aco executive \(per cms public filing\)|aco public contact \(per cms public filing\)",
    re.IGNORECASE,
)

US_STATE_TOKENS = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "florida", "georgia", "hawaii", "idaho",
    "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana",
    "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada", "hampshire",
    "jersey", "mexico", "york", "carolina", "dakota", "ohio", "oklahoma",
    "oregon", "pennsylvania", "rhode", "tennessee", "texas", "utah",
    "vermont", "virginia", "washington", "wisconsin", "wyoming",
}

GENERIC_ORG_TOKENS = {
    "health", "healthcare", "care", "medical", "medicine", "clinical",
    "services", "service", "partners", "partner", "network", "networks",
    "associates", "association", "physicians", "physician", "hospital",
    "hospitals", "clinic", "clinics", "consultation", "management",
    "solutions", "coalition", "accountable", "organization", "professional",
    "group", "alliance", "system", "systems", "wellness", "primary",
    "community", "regional", "national", "integrated", "advanced",
    "premier", "select", "performance", "aco", "llc", "inc", "the",
    "and", "of", "co", "corp", "corporation", "company", "or", "ltd",
    "pa", "pc", "llp", "mssp", "for",
}


def classify_persona(title: str, snippet: str = "") -> tuple[str, str]:
    blob = f"{title} {snippet}".lower()
    for pattern, bucket, conf in PERSONA_RULES:
        if re.search(pattern, blob):
            return bucket, conf
    return "unknown", "L"


def is_anti_persona(title: str, company: str = "", snippet: str = "") -> bool:
    blob = f"{title} {company} {snippet}"
    if ANTI_PERSONA_TITLE_RE.search(blob):
        return True
    if ANTI_PERSONA_COMPANY_RE.search(company):
        return True
    return False


def is_cms_placeholder_contact(title: str) -> bool:
    return bool(CMS_PLACEHOLDER_EXEC_RE.search(title or ""))


def tokenize_org(name: str) -> list[str]:
    raw = re.findall(r"[a-z]+", (name or "").lower())
    return [t for t in raw if len(t) >= 3 and t not in GENERIC_ORG_TOKENS]


def brand_token(org_name: str) -> str | None:
    toks = sorted(tokenize_org(org_name), key=len, reverse=True)
    return toks[0] if toks else None


def brand_is_state_only(org_name: str) -> bool:
    tok = brand_token(org_name)
    return bool(tok and tok in US_STATE_TOKENS)


def filter_persona_rows(
    rows: Iterable[dict],
    *,
    title_key: str = "position",
    company_key: str = "companyName",
    snippet_key: str = "_snippet",
) -> tuple[list[dict], list[dict]]:
    """Return (kept, excluded) after anti-persona + unknown-low-confidence drop."""
    kept: list[dict] = []
    excluded: list[dict] = []
    for row in rows:
        title = str(row.get(title_key) or row.get("_title") or "")
        company = str(row.get(company_key) or "")
        snippet = str(row.get(snippet_key) or "")
        if is_anti_persona(title, company, snippet):
            excluded.append({**row, "_exclude_reason": "anti_persona"})
            continue
        bucket, conf = classify_persona(title, snippet)
        if bucket == "unknown" and conf == "L":
            excluded.append({**row, "_exclude_reason": "unknown_persona"})
            continue
        kept.append(row)
    return kept, excluded
