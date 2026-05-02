"""Persona-tagging rules for the Wave 1 LinkedIn pipeline.

Single source of truth for: "given a person's title (and optionally their
company name), which of the 5 buying-committee personas do they belong to,
and how confident are we?" Output is injected into the Parallel.ai task
prompt so every extraction applies the same rules.

The 5 personas (see knowledge_base/business/BUYING_COMMITTEE_DYNAMICS.md):
- operational_owner       — feels the workflow pain daily
- clinical_champion       — needs clinical credibility for the story
- economic_buyer          — owns the budget; CFO/COO/SVP/President
- tech_gatekeeper         — informatics/IT; gates EHR integration
- bh_quality_influencer   — behavioral health / quality lead; demo-stage validator

Strategy: HYBRID
- `tag_persona_keyword()` handles the obvious 70-80% deterministically.
- For rows where keyword returns `unknown` or `low` confidence, the
  Parallel.ai task uses PERSONA_DEFINITIONS as system context to make a
  judgment call.

ORDERING NOTE: more specific titles must be checked before broader ones.
"Behavioral Health Medical Director" must hit the BH-clinical branch before
"Medical Director" (broader) catches it. "CMIO" must hit the tech_gatekeeper
branch before "Chief Medical" catches it for clinical_champion.

Imported by: scripts/parallel_persona_extractor.py
"""

from __future__ import annotations

import re
from typing import Literal, Optional, TypedDict

Persona = Literal[
    "operational_owner",
    "clinical_champion",
    "economic_buyer",
    "tech_gatekeeper",
    "bh_quality_influencer",
    "unknown",
]


class PersonaTag(TypedDict):
    persona: Persona
    confidence: Literal["high", "medium", "low"]
    rationale: str


# ---------------------------------------------------------------------------
# Disqualifiers — not buying-committee (HR, sales, admin, outside universe)
# ---------------------------------------------------------------------------
# Run before persona keyword chains. Whole-word tokens use boundaries.

_DISQUALIFIER_PHRASES: tuple[str, ...] = (
    "chief human resource",
    "human resources officer",
    "talent acquisition",
    "recruiter",
    "vp human resources",
    "head of people",
    "people officer",
    "chief of staff",
    "executive assistant",
    "software engineer",
    "data architect",
    "financial professional",
    # Sales / biz-dev (non-buyer); avoid bare "sales" (false positives)
    " of sales",
    "sales and",
    "sales &",
    "sales director",
    "account executive",
    "business development manager",
)

_DISQUALIFIER_TOKENS: tuple[str, ...] = (
    "chro",
    "sdr",
    "bdr",
)

# Company signals that contradict subtier 1A (mid-market provider group).
_NOT_1A_COMPANY_SUBSTRINGS: tuple[str, ...] = (
    " hospital",
    "health system",
    "medical center",
    "hca healthcare",
    " ascension",
    "commonspirit",
    "adventhealth",
    "atrium health",
    "wellstar",
    "northside",
    "wake med",
    "wakemed",
    "metrohealth",
    "memorialcare",
    "integris",
    "aetna",
    "humana",
    "cigna",
    "anthem",
    "unitedhealth",
    "cvs health",
    "centene",
    "molina",
    "bcbs",
    "blue cross",
    "wellcare",
    "navina",
    "privia",
    "aledade",
    "iqvia",
    "oak street health",
    "one medical",
    "navvis",
    "allina",
    "memorial care",
    "ng insights",
)


def disqualify_reason(title: str) -> Optional[str]:
    """If title clearly excludes buying-committee, return the matched signal."""
    t = (title or "").lower().strip()
    if not t:
        return None
    for phrase in _DISQUALIFIER_PHRASES:
        if phrase in t:
            return phrase
    for tok in _DISQUALIFIER_TOKENS:
        if re.search(r"\b" + re.escape(tok) + r"\b", t):
            return tok
    return None


def is_disqualified(title: str) -> bool:
    """True if the title should never be tagged as a buying-committee persona."""
    return disqualify_reason(title) is not None


def _matches_nonvice_president_economic_buyer(title_lower: str) -> bool:
    """True for President / Group President roles, excluding Vice President."""
    if "vice president" in title_lower:
        return False
    return bool(re.search(r"\bpresident\b", title_lower))


# ---------------------------------------------------------------------------
# Keyword rules — deterministic fast path
# ---------------------------------------------------------------------------
# Order is precedence: more specific before more general.

_TECH_GATEKEEPER_HARD = (
    "cmio",
    "chief medical information",
    "clinical informatics",
    "vp informatics",
    "director of informatics",
    "vp health it",
    "health it director",
    "director of clinical analytics",
    "director of data science",
    "vp data & analytics",
    "vp interoperability",
    "interoperability lead",
    "ehr administrator",
    "director of clinical systems",
    "chief technology officer",
    "cto",
    "vp engineering",
    "vp it",
    "cio",
)

_BH_QUALITY_HARD = (
    "director of behavioral health",
    "vp behavioral health",
    "behavioral health director",
    "bh program director",
    "behavioral health program director",
    "director of bh integration",
    "director of behavioral health integration",
    "behavioral health quality",
    "director of quality measurement",
    "director of hedis",
    "stars program director",
    "vp stars performance",
    "director of quality improvement",
    "quality performance director",
    "director of clinical quality programs",
    "director of bh quality",
)

_CLINICAL_CHAMPION_HARD = (
    "chief medical officer",
    "cmo",
    "vp medical affairs",
    "vp clinical affairs",
    "vp medical operations",
    "vp clinical operations",
    "behavioral health medical director",
    "chief behavioral health officer",
    "population health medical director",
    "medical director population health",
    "medical director value-based care",
    "medical director value based care",
    "medical director quality",
    "medical director primary care",
    "primary care medical executive",
    "associate cmo",
    "chief clinical officer",
    "physician executive",
    "supervising physician",
    "lead physician",
    "chief of medicine",
)

# Economic Buyer — no bare "president" (matches inside "Vice President").
_ECONOMIC_BUYER_HARD = (
    "chief financial officer",
    "cfo",
    "chief executive officer",
    "ceo",
    "chief operating officer",
    "coo",
    "vp finance",
    "vp revenue",
    "chief revenue officer",
    "vp revenue cycle",
    "chief strategy officer",
    "svp health plan operations",
    "svp enterprise operations",
    "svp clinical affairs",
    "svp operations",
    "svp business development",
    "svp strategy",
    "managing director",
    "managing partner",
    "executive director",
    "general manager",
)

_OPERATIONAL_OWNER_HARD = (
    "vp population health",
    "director of population health",
    "vp care transformation",
    "director of care transformation",
    "director of care management",
    "director of care navigation",
    "director of care coordination",
    "director of clinical programs",
    "director of value-based programs",
    "director of value based programs",
    "director of risk adjustment",
    "vp care delivery",
    "vp clinical operations",
    "vp ambulatory operations",
    "vp ambulatory",
    "vp primary care service line",
    "director of ambulatory operations",
    "director of ambulatory strategy",
    "vp operations",
    "director of operations",
    "director of network performance",
    "director of value-based operations",
    "risk operations leader",
    "director of patient engagement",
    "practice administrator",
    "practice manager",
    "office manager",
    "director of practice operations",
    "operations manager",
    "clinic administrator",
    "ehr administrator",
    "it manager",
    "it director",
)


def _has_any(haystack: str, needles: tuple[str, ...]) -> Optional[str]:
    """Return the first needle found in haystack as a whole word, else None."""
    for n in needles:
        pattern = r"\b" + re.escape(n) + r"\b"
        if re.search(pattern, haystack):
            return n
    return None


def parse_subtier_code(raw: str) -> str:
    """Normalize Parallel/LLM subtier strings to 1A … 3C or unknown."""
    if not raw or not str(raw).strip():
        return "unknown"
    s = str(raw).strip()
    if s.lower() == "unknown":
        return "unknown"
    m = re.search(r"\b([123])\s*([AaBbCc])\b", s)
    if m:
        return f"{m.group(1)}{m.group(2).upper()}"
    compact = re.sub(r"\s+", "", s)
    m2 = re.match(r"^([123])([abcABC])", compact)
    if m2:
        return f"{m2.group(1)}{m2.group(2).upper()}"
    return "unknown"


def company_signals_not_1a(company: str) -> bool:
    """True if employer name strongly suggests NOT mid-market provider group 1A."""
    c = (company or "").lower().strip()
    if not c:
        return False
    return any(hint in c for hint in _NOT_1A_COMPANY_SUBSTRINGS)


def refine_subtier_1a(subtier_guess: str, company: str) -> tuple[str, str]:
    """Return (subtier_code, subtier_confidence) with 1A demotion when company mismatches.

    When LLM returns 1A but the company is a health system, payer, or vendor,
    demote to unknown + low confidence for Wave 1A HeyReach gating.
    """
    code = parse_subtier_code(subtier_guess)
    c = (company or "").strip()

    if code == "1A":
        if company_signals_not_1a(c):
            return "unknown", "low"
        if not c:
            return "1A", "medium"
        return "1A", "high"

    if code == "unknown":
        return "unknown", "low"

    return code, "high" if code != "unknown" else "low"


def tag_persona_keyword(title: str, company: Optional[str] = None) -> PersonaTag:
    """Deterministic keyword classifier. First match wins."""
    t = (title or "").lower().strip()
    if not t:
        return {
            "persona": "unknown",
            "confidence": "low",
            "rationale": "empty title",
        }

    dq = disqualify_reason(t)
    if dq:
        return {
            "persona": "unknown",
            "confidence": "high",
            "rationale": f"disqualified: {dq!r}",
        }

    hit = _has_any(t, _TECH_GATEKEEPER_HARD)
    if hit:
        return {
            "persona": "tech_gatekeeper",
            "confidence": "high",
            "rationale": f"keyword: {hit!r}",
        }

    hit = _has_any(t, _BH_QUALITY_HARD)
    if hit:
        return {
            "persona": "bh_quality_influencer",
            "confidence": "high",
            "rationale": f"keyword: {hit!r}",
        }

    hit = _has_any(t, _CLINICAL_CHAMPION_HARD)
    if hit:
        return {
            "persona": "clinical_champion",
            "confidence": "high",
            "rationale": f"keyword: {hit!r}",
        }

    hit = _has_any(t, _ECONOMIC_BUYER_HARD)
    if not hit and _matches_nonvice_president_economic_buyer(t):
        hit = "president"

    if hit:
        return {
            "persona": "economic_buyer",
            "confidence": "high",
            "rationale": f"keyword: {hit!r}",
        }

    hit = _has_any(t, _OPERATIONAL_OWNER_HARD)
    if hit:
        return {
            "persona": "operational_owner",
            "confidence": "high",
            "rationale": f"keyword: {hit!r}",
        }

    return {
        "persona": "unknown",
        "confidence": "low",
        "rationale": "no keyword match — fall back to LLM",
    }


# ---------------------------------------------------------------------------
# Persona definitions — used by Parallel.ai LLM fallback
# ---------------------------------------------------------------------------

PERSONA_DEFINITIONS: dict[Persona, str] = {
    "operational_owner": (
        "Owns clinic / care-management / population-health operations. Feels "
        "BH workload pain daily. Examples: Director of Care Management, "
        "Population Health Director, Practice Administrator, VP Care "
        "Transformation. Tag here if the role is operational-focused at a "
        "provider org and not clearly executive finance, IT, or BH-specific."
    ),
    "clinical_champion": (
        "Physician executive whose endorsement carries clinical credibility. "
        "Examples: CMO, VP Medical Affairs, Medical Director (population "
        "health, value-based care, or primary care). Tag here when the title "
        "indicates a physician leadership role focused on clinical strategy."
    ),
    "economic_buyer": (
        "Owns the budget and signs the contract. Examples: CFO, COO, VP "
        "Finance, Chief Strategy Officer, SVP Operations, President, "
        "Managing Director, Executive Director. Not first to reach cold; "
        "tag for sequencing-after-warm."
    ),
    "tech_gatekeeper": (
        "Gates EHR integration, security review, interoperability. Examples: "
        "CMIO, CIO, VP Clinical Informatics, Director of Health IT, Director "
        "of Clinical Analytics, VP Data & Analytics. Tag for any "
        "informatics/IT/analytics title at a healthcare org."
    ),
    "bh_quality_influencer": (
        "Leads behavioral health programs OR quality measurement (HEDIS, "
        "Stars, risk adjustment). Examples: Director of Behavioral Health, "
        "BH Program Director, Director of HEDIS, Stars Program Director, "
        "Director of Quality Measurement. Highest self-selected pain "
        "alignment for Kivira's wedge."
    ),
    "unknown": (
        "Title does not clearly fit any of the five personas above. Common "
        "case: recruiters, students, vendor sales reps, non-clinical admin "
        "staff. Tag this when the title is genuinely outside the buying "
        "committee."
    ),
}


# ---------------------------------------------------------------------------
# Strategy switch
# ---------------------------------------------------------------------------

TAGGING_STRATEGY: Literal["keyword", "llm", "hybrid"] = "hybrid"


def tag_persona(title: str, company: Optional[str] = None) -> PersonaTag:
    """Public entry point. Routes to the chosen strategy.

    High confidence covers both (a) a matched persona and (b) a disqualified
    title — do not send disqualified rows to the LLM in hybrid mode.
    """
    if TAGGING_STRATEGY == "keyword":
        return tag_persona_keyword(title, company)
    if TAGGING_STRATEGY == "llm":
        return {
            "persona": "unknown",
            "confidence": "low",
            "rationale": "llm-managed — see Parallel.ai task",
        }
    kw = tag_persona_keyword(title, company)
    if kw["confidence"] == "high":
        return kw
    return {
        "persona": "unknown",
        "confidence": "low",
        "rationale": "keyword miss — defer to LLM in Parallel.ai task",
    }


# ---------------------------------------------------------------------------
# Self-test (run as a module)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    examples = [
        ("Chief Medical Officer", "Wellstar"),
        ("Director of Behavioral Health", "Atrium Health"),
        ("CMIO", "Northside Hospital"),
        ("VP Population Health", "Aledade"),
        ("Practice Administrator", "ABC Family Medicine"),
        ("Behavioral Health Medical Director", "FQHC of Atlanta"),
        ("CFO", "Privia Health"),
        ("Director of Care Management", "Oak Street Health"),
        ("Senior Software Engineer", "Epic"),
        ("Director of HEDIS", "BCBS Georgia"),
        ("Vice President (VP) of Value-Based Care", "Navina"),
        ("President, Medicare Advantage", "Humana"),
        ("Senior Vice President and Chief Human Resource Officer", "HCA"),
    ]
    for title, company in examples:
        tag = tag_persona(title, company)
        print(f"  {title:<48} → {tag['persona']:<24} [{tag['confidence']}]  {tag['rationale']}")
