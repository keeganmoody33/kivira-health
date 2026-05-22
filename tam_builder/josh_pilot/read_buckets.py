from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

# READ.csv bucket keywords (title playbook)
INTEGRATED_CARE_KEYWORDS = (
    "integrated care",
    "integrated health",
    "behavioral health integration",
    "bhi",
    "collaborative care",
    "cocm",
    "population health",
    "behavioral health",
    "mental health",
)

ROI_KEYWORDS = (
    "value based",
    "value-based",
    "vbc",
    "risk adjustment",
    "revenue cycle",
    "rcm",
    "hedis",
    "stars",
    "risk performance",
    "cfo",
    "chief financial",
    "revenue",
    "reimbursement",
    "billing",
)

OPS_KEYWORDS = (
    "practice manager",
    "practice administrator",
    "office manager",
    "director of operations",
    "vp operations",
    "care management",
    "care coordination",
    "operations supervisor",
    "enrollment",
)

NON_PCP_ORG_BLOCKLIST = (
    "physical therapy",
    "chiropractic",
    "optometry",
    "eyecare",
    "eye care",
    "dental",
    "orthopedic",
    "rehab",
    "marriage",
    "blind",
    "vision",
)


def parse_read_csv(path: Path) -> dict[str, Any]:
    """Parse READ.csv into structured buckets + boolean strings."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [ln.strip().strip('"') for ln in text.splitlines() if ln.strip()]

    buckets: dict[str, list[str]] = {
        "integrated_care": [],
        "regulatory_revenue": [],
        "service_line": [],
        "boolean_strings": [],
    }
    current: str | None = None

    for line in lines:
        low = line.lower()
        if "integrated care" in low and "power titles" in low:
            current = "integrated_care"
            continue
        if "regulatory" in low and "revenue" in low:
            current = "regulatory_revenue"
            continue
        if "service line" in low:
            current = "service_line"
            continue
        if "boolean strings" in low or "sales navigator" in low:
            current = "boolean_strings"
            continue
        if current == "boolean_strings":
            if line.startswith("The ") and ":" in line:
                buckets["boolean_strings"].append(line)
            continue
        if current and current != "boolean_strings":
            if len(line) > 3 and not line.startswith("These "):
                buckets[current].append(line)

    return buckets


def write_read_yaml(path: Path, buckets: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(buckets, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def match_read_bucket(title: str) -> str:
    """Return integrated_care | regulatory_revenue | service_line | none."""
    t = (title or "").lower()
    if any(k in t for k in INTEGRATED_CARE_KEYWORDS):
        return "integrated_care"
    if any(k in t for k in ROI_KEYWORDS):
        return "regulatory_revenue"
    if any(k in t for k in OPS_KEYWORDS):
        return "service_line"
    return "none"


def is_non_pcp_org(org_name: str, title: str) -> bool:
    blob = f"{org_name} {title}".lower()
    return any(b in blob for b in NON_PCP_ORG_BLOCKLIST)
