"""Normalization and validation for account CSV inputs."""

from __future__ import annotations

import json
import re
from pathlib import Path

from tam_builder.constants import (
    COLUMN_ALIASES,
    DEFAULT_PERSONA_SEQUENCE,
    ERROR_FIELDS,
    NORMALIZED_ACCOUNT_FIELDS,
    ORG_TYPES,
    PERSONAS,
)
from tam_builder.io_utils import dump_pipe_list, parse_pipe_list, slugify

TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"0", "false", "no", "n", ""}
IDENTITY_QUALITIES = {"weak", "moderate", "strong"}


def normalize_accounts(
    rows: list[dict[str, str]],
    mapping_file: str | None = None,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, str]]:
    explicit_map = load_column_map(mapping_file) if mapping_file else {}
    column_map = infer_column_map(rows[0].keys() if rows else [], explicit_map)
    normalized_rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    for row_number, row in enumerate(rows, start=2):
        normalized_row, row_errors = normalize_account_row(row, row_number, column_map)
        if row_errors:
            errors.extend(row_errors)
            continue
        normalized_rows.append(normalized_row)
    return normalized_rows, errors, column_map


def infer_column_map(headers: list[str] | object, explicit_map: dict[str, str]) -> dict[str, str]:
    normalized_headers = {simplify(header): header for header in headers}
    mapping: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        if canonical in explicit_map:
            mapping[canonical] = explicit_map[canonical]
            continue
        for alias in aliases:
            match = normalized_headers.get(simplify(alias))
            if match:
                mapping[canonical] = match
                break
    return mapping


def load_column_map(path: str) -> dict[str, str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Mapping file must contain a JSON object.")
    return {str(key): str(value) for key, value in payload.items()}


def normalize_account_row(
    row: dict[str, str],
    row_number: int,
    column_map: dict[str, str],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    errors: list[dict[str, object]] = []

    def raw(field: str) -> str:
        column = column_map.get(field)
        if not column:
            return ""
        return str(row.get(column, "")).strip()

    org_name = raw("org_name")
    state = raw("state").upper()
    city = raw("city")
    org_type = normalize_org_type(raw("org_type"))
    max_candidates = parse_int(raw("max_candidates"), default=0)
    priority_personas = normalize_personas(raw("priority_personas"))
    if not priority_personas and org_type in DEFAULT_PERSONA_SEQUENCE:
        priority_personas = list(DEFAULT_PERSONA_SEQUENCE[org_type])

    if not org_name:
        errors.append(error(row_number, "org_name", org_name, "Missing organization name."))
    if len(state) != 2:
        errors.append(error(row_number, "state", state, "State must be a two-letter code."))
    if org_type not in ORG_TYPES:
        errors.append(
            error(
                row_number,
                "org_type",
                org_type,
                f"Org type must be one of: {', '.join(ORG_TYPES)}.",
            )
        )
    if max_candidates <= 0:
        errors.append(error(row_number, "max_candidates", max_candidates, "Max candidates must be a positive integer."))

    identified_contact = parse_bool(raw("identified_contact"), default=None)
    contact_name = raw("contact_name")
    contact_title = raw("contact_title")
    contact_email = raw("contact_email")
    if identified_contact is None:
        identified_contact = bool(contact_name or contact_title or contact_email)
    if contact_email and "@" not in contact_email:
        errors.append(error(row_number, "contact_email", contact_email, "Contact email must contain @ when supplied."))

    identity_quality = raw("identity_match_quality").lower() or "weak"
    if identity_quality not in IDENTITY_QUALITIES:
        errors.append(
            error(
                row_number,
                "identity_match_quality",
                identity_quality,
                "Identity quality must be weak, moderate, or strong.",
            )
        )

    blended_penalty = parse_bool(raw("experimental_blended_denominator"), default=False)
    if blended_penalty is None:
        errors.append(
            error(
                row_number,
                "experimental_blended_denominator",
                raw("experimental_blended_denominator"),
                "Experimental blended denominator must be a boolean-like value.",
            )
        )
        blended_penalty = False

    if errors:
        return {}, errors

    normalized = {
        "org_name": org_name,
        "state": state,
        "city": city,
        "org_type": org_type,
        "priority_personas": dump_pipe_list(priority_personas),
        "max_candidates": max_candidates,
        "notes": raw("notes"),
        "source_system": raw("source_system") or "manual_csv",
        "source_record_id": raw("source_record_id"),
        "normalized_org_key": slugify(f"{org_name}-{state}"),
        "parent_org_name": raw("parent_org_name"),
        "system_affiliation": raw("system_affiliation"),
        "vbc_track": raw("vbc_track"),
        "ehr": raw("ehr"),
        "payer_mix": raw("payer_mix"),
        "ambient_ai": raw("ambient_ai"),
        "bh_readiness": raw("bh_readiness"),
        "procurement_type": raw("procurement_type"),
        "active_competitor": raw("active_competitor"),
        "decision_maker_count": parse_int(raw("decision_maker_count"), default=0),
        "identified_contact": bool(identified_contact),
        "contact_name": contact_name,
        "contact_title": contact_title,
        "contact_email": contact_email,
        "high_confidence_clinicians": parse_int(raw("high_confidence_clinicians"), default=0),
        "medium_confidence_clinicians": parse_int(raw("medium_confidence_clinicians"), default=0),
        "low_confidence_clinicians": parse_int(raw("low_confidence_clinicians"), default=0),
        "observed_g0444_benes": parse_int(raw("observed_g0444_benes"), default=0),
        "observed_96127_benes": parse_int(raw("observed_96127_benes"), default=0),
        "observed_cocm_benes": parse_int(raw("observed_cocm_benes"), default=0),
        "observed_cocm_services": parse_int(raw("observed_cocm_services"), default=0),
        "observed_cocm_revenue": parse_float(raw("observed_cocm_revenue"), default=0.0),
        "identity_match_quality": identity_quality,
        "experimental_blended_denominator": bool(blended_penalty),
    }
    return ordered_row(normalized, NORMALIZED_ACCOUNT_FIELDS), []


def normalize_org_type(value: str) -> str:
    collapsed = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return collapsed


def normalize_personas(value: str) -> list[str]:
    personas = []
    for persona in parse_pipe_list(value):
        normalized = re.sub(r"[^a-z0-9]+", "_", persona.lower()).strip("_")
        if normalized in PERSONAS and normalized not in personas:
            personas.append(normalized)
    return personas


def parse_int(value: object, default: int = 0) -> int:
    text = str(value).strip()
    if not text:
        return default
    try:
        return int(float(text))
    except ValueError:
        return default


def parse_float(value: object, default: float = 0.0) -> float:
    text = str(value).strip().replace("$", "").replace(",", "")
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def parse_bool(value: object, default: bool | None = False) -> bool | None:
    text = str(value).strip().lower()
    if text in TRUE_VALUES:
        return True
    if text in FALSE_VALUES:
        return False
    return default


def simplify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def ordered_row(row: dict[str, object], field_order: list[str]) -> dict[str, object]:
    ordered = {field: row.get(field, "") for field in field_order}
    for key, value in row.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def error(row_number: int, field: str, value: object, message: str) -> dict[str, object]:
    return {
        "row_number": row_number,
        "field": field,
        "value": value,
        "message": message,
    }


__all__ = [
    "ERROR_FIELDS",
    "NORMALIZED_ACCOUNT_FIELDS",
    "normalize_accounts",
]
