"""Static configuration for the Kivira TAM builder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioAssumption:
    activation_rate: float
    monthly_payment: float
    treatment_months: float


ORG_TYPES = (
    "solo_practice",
    "independent_group",
    "health_system_medical_group",
    "aco_parent",
)

PERSONAS = (
    "pcp",
    "medical_director",
    "cfo",
    "cmio",
    "pop_health",
    "bh_ops",
)

DEFAULT_PERSONA_SEQUENCE = {
    "solo_practice": ("pcp", "cfo"),
    "independent_group": ("medical_director", "cfo", "pcp"),
    "health_system_medical_group": ("medical_director", "cfo", "cmio"),
    "aco_parent": ("pop_health", "cfo", "bh_ops"),
}

PERSONA_TITLE_MAP = {
    "pcp": (
        "PCP owner",
        "physician owner",
        "founding clinician",
        "lead physician",
        "managing partner",
        "practice owner",
        "NP/PA owner",
    ),
    "medical_director": (
        "medical director",
        "CMO",
        "chief medical officer",
        "VP primary care",
        "primary care medical director",
        "VP medical affairs",
        "service line leader",
        "clinical director",
    ),
    "cfo": (
        "CFO",
        "COO",
        "CEO",
        "president",
        "VP revenue cycle",
        "practice administrator",
        "VP finance",
        "managing director",
    ),
    "cmio": (
        "CMIO",
        "VP clinical informatics",
        "CIO",
        "director of clinical informatics",
        "digital health director",
        "director of health IT",
        "director of EHR applications",
    ),
    "pop_health": (
        "VP population health",
        "director of population health",
        "VP quality",
        "director of quality",
        "director of care management",
        "director of risk adjustment",
        "VP clinical transformation",
        "care transformation lead",
    ),
    "bh_ops": (
        "BH integration director",
        "director of behavioral health",
        "VP behavioral health",
        "behavioral health program director",
        "BH program director",
        "director of quality improvement",
        "director of clinical supervision",
        "BH quality director",
    ),
}

SCENARIO_ASSUMPTIONS = {
    "solo_practice": {
        "conservative": ScenarioAssumption(0.06, 110.0, 3.0),
        "base": ScenarioAssumption(0.10, 120.0, 5.0),
        "aggressive": ScenarioAssumption(0.15, 135.0, 7.0),
    },
    "independent_group": {
        "conservative": ScenarioAssumption(0.06, 110.0, 3.0),
        "base": ScenarioAssumption(0.10, 120.0, 5.0),
        "aggressive": ScenarioAssumption(0.15, 135.0, 7.0),
    },
    "health_system_medical_group": {
        "conservative": ScenarioAssumption(0.08, 115.0, 4.0),
        "base": ScenarioAssumption(0.12, 127.0, 6.0),
        "aggressive": ScenarioAssumption(0.18, 140.0, 8.0),
    },
    "aco_parent": {
        "conservative": ScenarioAssumption(0.08, 115.0, 4.0),
        "base": ScenarioAssumption(0.14, 130.0, 6.0),
        "aggressive": ScenarioAssumption(0.20, 145.0, 8.0),
    },
}

DEFAULT_SYNTHETIC_SIGNALS = {
    "solo_practice": {
        "high_confidence_clinicians": 1,
        "medium_confidence_clinicians": 1,
        "low_confidence_clinicians": 0,
        "observed_g0444_benes": 12,
        "observed_96127_benes": 6,
        "observed_cocm_benes": 0,
        "observed_cocm_services": 0,
        "observed_cocm_revenue": 0.0,
        "identity_match_quality": "moderate",
    },
    "independent_group": {
        "high_confidence_clinicians": 4,
        "medium_confidence_clinicians": 2,
        "low_confidence_clinicians": 1,
        "observed_g0444_benes": 90,
        "observed_96127_benes": 60,
        "observed_cocm_benes": 8,
        "observed_cocm_services": 40,
        "observed_cocm_revenue": 2500.0,
        "identity_match_quality": "moderate",
    },
    "health_system_medical_group": {
        "high_confidence_clinicians": 8,
        "medium_confidence_clinicians": 4,
        "low_confidence_clinicians": 2,
        "observed_g0444_benes": 250,
        "observed_96127_benes": 180,
        "observed_cocm_benes": 20,
        "observed_cocm_services": 120,
        "observed_cocm_revenue": 5000.0,
        "identity_match_quality": "strong",
    },
    "aco_parent": {
        "high_confidence_clinicians": 10,
        "medium_confidence_clinicians": 5,
        "low_confidence_clinicians": 3,
        "observed_g0444_benes": 500,
        "observed_96127_benes": 320,
        "observed_cocm_benes": 40,
        "observed_cocm_services": 200,
        "observed_cocm_revenue": 10000.0,
        "identity_match_quality": "strong",
    },
}

CAVEATS = (
    "Modeled from public Medicare fee-for-service and NPPES-style signals only.",
    "Excludes MA, commercial, Medicaid, and uninsured populations.",
    "Provider-to-organization affiliation is inferred from public data and may be imperfect.",
    "CMS public files can suppress small beneficiary counts.",
    "Opportunity values are directional workflow estimates, not audited financial statements.",
)

BANNED_LANGUAGE = (
    "autonomous diagnosis",
    "replace clinical judgment",
    "replaces clinical judgment",
    "diagnose patients automatically",
    "diagnosis without clinician review",
)

NORMALIZED_ACCOUNT_FIELDS = [
    "org_name",
    "state",
    "city",
    "org_type",
    "priority_personas",
    "max_candidates",
    "notes",
    "source_system",
    "source_record_id",
    "normalized_org_key",
    "parent_org_name",
    "system_affiliation",
    "vbc_track",
    "ehr",
    "payer_mix",
    "ambient_ai",
    "bh_readiness",
    "procurement_type",
    "active_competitor",
    "decision_maker_count",
    "identified_contact",
    "contact_name",
    "contact_title",
    "contact_email",
    "high_confidence_clinicians",
    "medium_confidence_clinicians",
    "low_confidence_clinicians",
    "observed_g0444_benes",
    "observed_96127_benes",
    "observed_cocm_benes",
    "observed_cocm_services",
    "observed_cocm_revenue",
    "identity_match_quality",
    "experimental_blended_denominator",
]

ESTIMATE_FIELDS = NORMALIZED_ACCOUNT_FIELDS + [
    "matched_clinicians",
    "cocm_visibility",
    "screening_proxy_benes",
    "conservative_gap",
    "base_gap",
    "aggressive_gap",
    "confidence_score",
    "confidence_grade",
    "caveats",
    "persona_messages",
]

TIER_FIELDS = ESTIMATE_FIELDS + [
    "tier",
    "tier_score",
    "outbound_eligibility_status",
    "outbound_recommendation",
    "numeric_claims_allowed",
]

ROUTED_FIELDS = TIER_FIELDS + [
    "primary_persona",
    "persona_sequence",
    "title_variants",
    "route_rationale",
]

BRIEF_FIELDS = [
    "org_name",
    "state",
    "city",
    "org_type",
    "tier",
    "confidence_grade",
    "numeric_claims_allowed",
    "outbound_eligibility_status",
    "persona",
    "title_candidates",
    "why_now",
    "value_prop_angle",
    "likely_objections",
    "discovery_questions",
    "outbound_message",
    "caveats",
]

ERROR_FIELDS = ["row_number", "field", "value", "message"]

COLUMN_ALIASES = {
    "org_name": (
        "org_name",
        "organization name",
        "organization",
        "account name",
        "account",
    ),
    "state": ("state", "state code", "st"),
    "city": ("city", "metro", "market", "hq city"),
    "org_type": ("org_type", "organization type", "account type", "type"),
    "priority_personas": ("priority_personas", "priority personas", "personas"),
    "max_candidates": ("max_candidates", "candidate ceiling", "max candidates"),
    "notes": ("notes", "internal notes", "note"),
    "source_system": ("source_system", "source system", "crm system"),
    "source_record_id": ("source_record_id", "source id", "record id"),
    "parent_org_name": ("parent_org_name", "parent org", "parent organization"),
    "system_affiliation": ("system_affiliation", "system affiliation"),
    "vbc_track": ("vbc_track", "value-based track", "vbc"),
    "ehr": ("ehr", "primary ehr", "emr"),
    "payer_mix": ("payer_mix", "payer mix"),
    "ambient_ai": ("ambient_ai", "ambient ai", "ambient ai vendor"),
    "bh_readiness": ("bh_readiness", "bh readiness", "behavioral health readiness"),
    "procurement_type": ("procurement_type", "procurement type"),
    "active_competitor": ("active_competitor", "active competitor"),
    "decision_maker_count": ("decision_maker_count", "decision makers", "decision maker count"),
    "identified_contact": ("identified_contact", "has named contact", "identified contact"),
    "contact_name": ("contact_name", "contact name"),
    "contact_title": ("contact_title", "contact title"),
    "contact_email": ("contact_email", "contact email"),
    "high_confidence_clinicians": (
        "high_confidence_clinicians",
        "high confidence clinicians",
        "hi conf clinicians",
    ),
    "medium_confidence_clinicians": (
        "medium_confidence_clinicians",
        "medium confidence clinicians",
        "med conf clinicians",
    ),
    "low_confidence_clinicians": (
        "low_confidence_clinicians",
        "low confidence clinicians",
    ),
    "observed_g0444_benes": ("observed_g0444_benes", "g0444 benes"),
    "observed_96127_benes": ("observed_96127_benes", "96127 benes"),
    "observed_cocm_benes": ("observed_cocm_benes", "cocm benes"),
    "observed_cocm_services": ("observed_cocm_services", "cocm services"),
    "observed_cocm_revenue": ("observed_cocm_revenue", "cocm revenue"),
    "identity_match_quality": ("identity_match_quality", "identity quality"),
    "experimental_blended_denominator": (
        "experimental_blended_denominator",
        "experimental blended denominator",
    ),
}
