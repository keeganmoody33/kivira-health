"""Persona routing for the CoCM wedge."""

from __future__ import annotations

import json

from tam_builder.constants import DEFAULT_PERSONA_SEQUENCE, PERSONA_TITLE_MAP
from tam_builder.io_utils import dump_pipe_list, parse_pipe_list


def route_persona_row(row: dict[str, object]) -> dict[str, object]:
    org_type = str(row.get("org_type", ""))
    account_priorities = parse_pipe_list(str(row.get("priority_personas", "")))
    default_sequence = list(DEFAULT_PERSONA_SEQUENCE.get(org_type, ()))
    ordered = merge_persona_priorities(account_priorities, default_sequence)
    route = dict(row)
    route["primary_persona"] = ordered[0] if ordered else ""
    route["persona_sequence"] = dump_pipe_list(ordered)
    route["title_variants"] = json.dumps(
        {persona: list(PERSONA_TITLE_MAP[persona]) for persona in ordered},
        sort_keys=True,
    )
    route["route_rationale"] = route_rationale(org_type)
    return route


def merge_persona_priorities(
    preferred: list[str],
    default_sequence: list[str],
) -> list[str]:
    ordered: list[str] = []
    for persona in preferred + default_sequence:
        if persona and persona not in ordered:
            ordered.append(persona)
    return ordered


def route_rationale(org_type: str) -> str:
    if org_type == "solo_practice":
        return "Lead with the clinician-owner workflow story; finance only if the account engages on economics."
    if org_type == "independent_group":
        return "Clinical leadership is the wedge; admin and operational titles support qualification."
    if org_type == "health_system_medical_group":
        return "Start with the clinical operator, then finance, then informatics for implementation readiness."
    if org_type == "aco_parent":
        return "Population health leadership owns the problem first; finance and BH ops support scale and integration."
    return "Use org-type buyer mapping to validate the right champion order."
