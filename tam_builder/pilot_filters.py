"""
Pilot / Tier-1A slice helpers for GTM pipeline scripts (03–06).

Keeps filtering logic in one place so discovery → extraction → personas → wave
use the same account cohort.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import pandas as pd


def resolve_output_dir(base_dir: Path, output_subdir: str) -> Path:
    out = base_dir / "output"
    sub = (output_subdir or "").strip().strip("/")
    if sub:
        out = out / sub
    out.mkdir(parents=True, exist_ok=True)
    return out


def classified_source_path(base_dir: Path, state: str) -> Path:
    """Full classified file (always under output/, not pilot subdir)."""
    return base_dir / "output" / f"accounts_classified_{state.strip().upper()}.csv"


def pilot_mode_active(
    *,
    pilot_subtier: Optional[str],
    pilot_max_accounts: Optional[int],
    pilot_require_website: bool,
    pilot_min_classification_confidence: float,
) -> bool:
    if pilot_subtier and str(pilot_subtier).strip():
        return True
    if pilot_max_accounts is not None and int(pilot_max_accounts) > 0:
        return True
    if pilot_require_website:
        return True
    if float(pilot_min_classification_confidence or 0) > 0:
        return True
    return False


def default_output_subdir_if_pilot(
    output_subdir: str,
    *,
    pilot_subtier: Optional[str],
    pilot_max_accounts: Optional[int],
    pilot_require_website: bool,
    pilot_min_classification_confidence: float,
) -> str:
    """Avoid overwriting full output/ when pilot filters are used."""
    if (output_subdir or "").strip():
        return output_subdir.strip().strip("/")
    if pilot_mode_active(
        pilot_subtier=pilot_subtier,
        pilot_max_accounts=pilot_max_accounts,
        pilot_require_website=pilot_require_website,
        pilot_min_classification_confidence=pilot_min_classification_confidence,
    ):
        return "pilot"
    return ""


def filter_classified_pilot(
    df: pd.DataFrame,
    *,
    subtier: Optional[str] = None,
    max_accounts: Optional[int] = None,
    require_website: bool = False,
    min_classification_confidence: float = 0.0,
) -> pd.DataFrame:
    out = df.copy()
    if subtier and str(subtier).strip():
        st = str(subtier).strip().upper()
        if "subtier_primary" not in out.columns:
            return out.iloc[0:0]
        out = out[out["subtier_primary"].astype(str).str.upper().str.strip() == st]
    if "classification_status" in out.columns:
        out = out[out["classification_status"].astype(str).str.lower().str.strip() != "excluded"]
    if require_website:
        if "website" not in out.columns:
            return out.iloc[0:0]
        out = out[out["website"].astype(str).str.strip() != ""]
    if min_classification_confidence and min_classification_confidence > 0:
        if "classification_confidence" not in out.columns:
            return out.iloc[0:0]

        def _conf(x: Any) -> float:
            try:
                return float(str(x or "0").strip())
            except ValueError:
                return 0.0

        out = out[out["classification_confidence"].map(_conf) >= float(min_classification_confidence)]
    if "account_id" in out.columns:
        out = out.sort_values(by=["account_id"], key=lambda s: s.astype(str))
    if max_accounts is not None and int(max_accounts) > 0:
        out = out.head(int(max_accounts))
    return out


def read_full_classified_for_state(base_dir: Path, state: str) -> pd.DataFrame:
    path = classified_source_path(base_dir, state)
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str).fillna("")
