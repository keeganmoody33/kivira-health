"""Discovery-safe outbound brief generation."""

from __future__ import annotations

import json

from tam_builder.constants import BANNED_LANGUAGE, CAVEATS, PERSONA_TITLE_MAP
from tam_builder.io_utils import parse_pipe_list
from tam_builder.personas import route_persona_row
from tam_builder.tiering import tier_account_row


def generate_briefs(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    briefs: list[dict[str, object]] = []
    for row in rows:
        enriched = ensure_brief_context(row)
        personas = parse_pipe_list(str(enriched.get("persona_sequence", "")))
        if not personas:
            personas = parse_pipe_list(str(enriched.get("priority_personas", "")))
        for persona in personas:
            briefs.append(build_brief_row(enriched, persona))
    return briefs


def ensure_brief_context(row: dict[str, object]) -> dict[str, object]:
    enriched = dict(row)
    if "tier" not in enriched or not enriched.get("tier"):
        enriched = tier_account_row(enriched)
    if "persona_sequence" not in enriched or not enriched.get("persona_sequence"):
        enriched = route_persona_row(enriched)
    return enriched


def build_brief_row(row: dict[str, object], persona: str) -> dict[str, object]:
    grade = str(row.get("confidence_grade", "D"))
    org_name = str(row.get("org_name", ""))
    base_gap = float(row.get("base_gap", 0) or 0)
    conservative_gap = float(row.get("conservative_gap", 0) or 0)
    aggressive_gap = float(row.get("aggressive_gap", 0) or 0)
    screening_proxy = int(float(row.get("screening_proxy_benes", 0) or 0))

    why_now = build_why_now(persona, row, screening_proxy)
    value_prop_angle = build_value_prop_angle(persona, row)
    likely_objections = build_likely_objections(persona, row)
    discovery_questions = build_discovery_questions(persona, row)
    outbound_message = build_outbound_message(
        org_name,
        persona,
        grade,
        screening_proxy,
        conservative_gap,
        base_gap,
        aggressive_gap,
    )
    caveats = json.dumps(list(CAVEATS), sort_keys=True)
    validate_message(outbound_message)

    return {
        "org_name": row.get("org_name", ""),
        "state": row.get("state", ""),
        "city": row.get("city", ""),
        "org_type": row.get("org_type", ""),
        "tier": row.get("tier", ""),
        "confidence_grade": grade,
        "numeric_claims_allowed": row.get("numeric_claims_allowed", False),
        "outbound_eligibility_status": row.get("outbound_eligibility_status", ""),
        "persona": persona,
        "title_candidates": "|".join(PERSONA_TITLE_MAP.get(persona, ())),
        "why_now": why_now,
        "value_prop_angle": value_prop_angle,
        "likely_objections": likely_objections,
        "discovery_questions": discovery_questions,
        "outbound_message": outbound_message,
        "caveats": caveats,
    }


def build_why_now(persona: str, row: dict[str, object], screening_proxy: int) -> str:
    org_name = str(row.get("org_name", "this account"))
    if persona == "cfo":
        return f"{org_name} shows public screening activity, which suggests there may be unmanaged reimbursement leakage worth validating."
    if persona == "cmio":
        return f"{org_name} appears to have enough primary care screening volume to make workflow integration and EHR fit materially important."
    if persona == "pop_health":
        return f"{org_name} appears to sit in a population-health context where screening activity can translate into care-management workflow pressure."
    if persona == "bh_ops":
        return f"{org_name} looks like a setting where BH integration capacity and referral handoffs may be under strain."
    if persona == "pcp":
        return f"{org_name} is a primary-care workflow environment where screening burden can overwhelm a small clinical team."
    return f"{org_name} shows roughly {screening_proxy} public screening beneficiaries, which makes a workflow-first CoCM conversation timely."


def build_value_prop_angle(persona: str, row: dict[str, object]) -> str:
    if persona == "cfo":
        return "Frame this as workflow-supported reimbursement capture with directional public-data caveats, not as a guaranteed revenue claim."
    if persona == "cmio":
        return "Emphasize CDS-aligned workflow integration and implementation discipline rather than standalone intelligence."
    if persona == "pop_health":
        return "Connect screening volume to care management follow-through, attribution quality, and behavioral-health pathway consistency."
    if persona == "bh_ops":
        return "Focus on closing the gap between screening activity and BH follow-up capacity without implying autonomous diagnosis."
    if persona == "pcp":
        return "Lead with front-line workflow relief and follow-up consistency, not finance."
    return "Lead with clinical workflow and only use modeled economics as support when the grade allows it."


def build_likely_objections(persona: str, row: dict[str, object]) -> str:
    grade = str(row.get("confidence_grade", "D"))
    if persona == "cfo":
        return "We already have a workflow, these public numbers may be off, and reimbursement may not justify change."
    if persona == "cmio":
        return "We do not need another tool, integration effort is limited, and governance will question CDS claims."
    if grade in {"C", "D"}:
        return "Attribution may be too noisy, the timing may be premature, and the account may prefer proof before discussion."
    return "This may not reflect our true patient mix, screening does not equal CoCM readiness, and we need to validate workflow ownership."


def build_discovery_questions(persona: str, row: dict[str, object]) -> str:
    org_name = str(row.get("org_name", "the account"))
    if persona == "cfo":
        return f"What portion of {org_name}'s primary care screening volume already converts into billable CoCM workflows, and where is leakage today?"
    if persona == "cmio":
        return f"How does {org_name} currently move a positive screen from the EHR into follow-up work queues and human review?"
    if persona == "pop_health":
        return f"Where does {org_name} see the biggest drop-off between screening, outreach, and sustained behavioral-health follow-through?"
    if persona == "bh_ops":
        return f"What is {org_name}'s current handoff process from PCP screening into BH follow-up, and where does it break down?"
    if persona == "pcp":
        return f"When a PCP at {org_name} sees a positive screen, what parts of triage and follow-up still fall back on manual workflow?"
    return f"How does {org_name} currently handle positive screening follow-up, billing readiness, and care-team coordination?"


def build_outbound_message(
    org_name: str,
    persona: str,
    grade: str,
    screening_proxy: int,
    conservative_gap: float,
    base_gap: float,
    aggressive_gap: float,
) -> str:
    persona_open = {
        "pcp": "workflow strain around mental-health follow-up",
        "medical_director": "primary-care screening follow-through",
        "cfo": "directional CoCM reimbursement leakage",
        "cmio": "EHR-native follow-up workflow design",
        "pop_health": "population-health follow-up consistency",
        "bh_ops": "behavioral-health integration throughput",
    }.get(persona, "primary-care behavioral-health workflow")

    if grade in {"A", "B"}:
        range_text = f"${conservative_gap:,.0f}-${aggressive_gap:,.0f}"
        return (
            f"We noticed public primary-care screening activity that may point to {persona_open} at {org_name}. "
            f"Our directional public-data model suggests a possible CoCM opportunity range around {range_text}, "
            f"with a base case near ${base_gap:,.0f}. If useful, we can compare that against your actual workflow and billing reality."
        )
    if grade == "C":
        return (
            f"We noticed public screening activity that suggests {org_name} may be dealing with {persona_open}. "
            f"We would approach this as a discovery conversation about workflow, follow-up, and care-team coordination rather than as a hard numeric claim."
        )
    return (
        f"Public data alone is too thin to make a reliable account-specific estimate for {org_name}. "
        f"Any follow-up should focus on qualification through workflow context, not modeled economics."
    )


def validate_message(message: str) -> None:
    lowered = message.lower()
    for banned in BANNED_LANGUAGE:
        if banned in lowered:
            raise ValueError(f"Outbound message contains banned language: {banned}")
