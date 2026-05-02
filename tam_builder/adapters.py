"""Public-signal adapters for synthetic-first estimation."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from tam_builder.constants import DEFAULT_SYNTHETIC_SIGNALS


@dataclass
class AdapterResult:
    account_updates: dict[str, object]
    provider_debug_rows: list[dict[str, object]]


class PublicSignalAdapter:
    name = "base"

    def collect(self, account: dict[str, object], include_low_confidence: bool = False) -> AdapterResult:
        raise NotImplementedError


class SyntheticPublicSignalAdapter(PublicSignalAdapter):
    name = "synthetic"

    def collect(self, account: dict[str, object], include_low_confidence: bool = False) -> AdapterResult:
        org_type = str(account.get("org_type", ""))
        defaults = DEFAULT_SYNTHETIC_SIGNALS.get(org_type, {})
        updates = {
            key: account.get(key) if account.get(key) not in ("", None) else value
            for key, value in defaults.items()
        }
        for field in defaults:
            if field not in updates:
                updates[field] = defaults[field]
        high = int(float(updates.get("high_confidence_clinicians", 0) or 0))
        medium = int(float(updates.get("medium_confidence_clinicians", 0) or 0))
        low = int(float(updates.get("low_confidence_clinicians", 0) or 0))
        provider_rows = build_provider_debug_rows(
            account,
            high,
            medium,
            low if include_low_confidence else 0,
            updates,
        )
        return AdapterResult(account_updates=updates, provider_debug_rows=provider_rows)


class LivePublicSignalAdapter(PublicSignalAdapter):
    name = "live-public"

    def collect(self, account: dict[str, object], include_low_confidence: bool = False) -> AdapterResult:
        """Collect public signals from local CMS Part B extracts.

        This adapter is intentionally file-backed (not API-backed) so it can be used in offline,
        deterministic list-building runs.

        Required input signals (local files under --signal-dir):

        1) provider_signals.csv
           Columns:
           - provider_npi
           - observed_g0444_benes
           - observed_96127_benes
           - observed_cocm_benes
           - observed_cocm_services
           - observed_cocm_revenue

        2) org_provider_map.csv
           Columns:
           - org_name
           - state
           - provider_npi
           - match_confidence (high|medium|low)
           - affiliation_score (0-1, optional)
           - match_reason (optional)

        If an account row includes `provider_npis` (pipe-delimited list), the adapter will use that
        directly and skip org_provider_map lookup.
        """

        signal_dir = Path(str(account.get("public_signal_dir") or account.get("signal_dir") or "data/public_signals"))
        provider_signals_path = signal_dir / "provider_signals.csv"
        org_map_path = signal_dir / "org_provider_map.csv"

        provider_signals = _load_provider_signals(provider_signals_path)

        provider_npis = _parse_pipe_list(str(account.get("provider_npis", "")))
        if provider_npis:
            providers = _providers_from_npis(provider_npis, provider_signals)
        else:
            providers = _providers_for_org(account, org_map_path, provider_signals)

        if not providers:
            # Fall back to synthetic defaults rather than failing the whole run.
            synthetic = SyntheticPublicSignalAdapter()
            return synthetic.collect(account, include_low_confidence=include_low_confidence)

        # Aggregate observed signals.
        agg = {
            "high_confidence_clinicians": 0,
            "medium_confidence_clinicians": 0,
            "low_confidence_clinicians": 0,
            "observed_g0444_benes": 0,
            "observed_96127_benes": 0,
            "observed_cocm_benes": 0,
            "observed_cocm_services": 0,
            "observed_cocm_revenue": 0.0,
            "identity_match_quality": "moderate",
        }

        for p in providers:
            conf = p.get("match_confidence", "medium")
            if conf == "high":
                agg["high_confidence_clinicians"] += 1
            elif conf == "low":
                agg["low_confidence_clinicians"] += 1
            else:
                agg["medium_confidence_clinicians"] += 1

            agg["observed_g0444_benes"] += int(float(p.get("observed_g0444_benes", 0) or 0))
            agg["observed_96127_benes"] += int(float(p.get("observed_96127_benes", 0) or 0))
            agg["observed_cocm_benes"] += int(float(p.get("observed_cocm_benes", 0) or 0))
            agg["observed_cocm_services"] += int(float(p.get("observed_cocm_services", 0) or 0))
            agg["observed_cocm_revenue"] += float(p.get("observed_cocm_revenue", 0.0) or 0.0)

        total = agg["high_confidence_clinicians"] + agg["medium_confidence_clinicians"] + agg["low_confidence_clinicians"]
        if total >= 10 and agg["high_confidence_clinicians"] >= 5:
            agg["identity_match_quality"] = "strong"
        elif agg["high_confidence_clinicians"] >= 2:
            agg["identity_match_quality"] = "moderate"
        else:
            agg["identity_match_quality"] = "weak"

        if not include_low_confidence:
            # Drop low-confidence clinicians from debug rows and counts.
            providers = [p for p in providers if p.get("match_confidence") != "low"]
            agg["low_confidence_clinicians"] = 0

        agg["observed_cocm_revenue"] = round(float(agg["observed_cocm_revenue"]), 2)
        return AdapterResult(account_updates=agg, provider_debug_rows=providers)


def get_adapter(name: str) -> PublicSignalAdapter:
    if name == "synthetic":
        return SyntheticPublicSignalAdapter()
    if name == "live-public":
        return LivePublicSignalAdapter()
    raise ValueError(f"Unsupported adapter: {name}")


def build_provider_debug_rows(
    account: dict[str, object],
    high: int,
    medium: int,
    low: int,
    updates: dict[str, object],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    total = high + medium + low
    g0444 = int(float(updates.get("observed_g0444_benes", 0) or 0))
    code_96127 = int(float(updates.get("observed_96127_benes", 0) or 0))
    cocm_benes = int(float(updates.get("observed_cocm_benes", 0) or 0))
    cocm_services = int(float(updates.get("observed_cocm_services", 0) or 0))
    cocm_revenue = float(updates.get("observed_cocm_revenue", 0.0) or 0.0)

    if total == 0:
        return rows

    for index in range(total):
        confidence = "high" if index < high else "medium" if index < high + medium else "low"
        slice_size = total or 1
        rows.append(
            {
                "org_name": account.get("org_name", ""),
                "state": account.get("state", ""),
                "city": account.get("city", ""),
                "provider_npi": f"9900{index + 1:06d}",
                "provider_name": f"Synthetic Clinician {index + 1}",
                "match_confidence": confidence,
                "affiliation_score": 0.92 if confidence == "high" else 0.74 if confidence == "medium" else 0.48,
                "match_reason": f"Synthetic {confidence}-confidence PCP match",
                "observed_g0444_benes": int(round(g0444 / slice_size)),
                "observed_96127_benes": int(round(code_96127 / slice_size)),
                "observed_cocm_benes": int(round(cocm_benes / slice_size)),
                "observed_cocm_services": int(round(cocm_services / slice_size)),
                "observed_cocm_revenue": round(cocm_revenue / slice_size, 2),
            }
        )
    return rows


def _parse_pipe_list(value: str) -> list[str]:
    parts = [p.strip() for p in (value or "").split("|")]
    return [p for p in parts if p]


def _load_provider_signals(path: Path) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        by_npi: dict[str, dict[str, object]] = {}
        for row in reader:
            npi = (row.get("provider_npi") or "").strip()
            if not npi:
                continue
            by_npi[npi] = {k: (v or "").strip() for k, v in row.items()}
        return by_npi


def _providers_from_npis(npis: list[str], signals: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for npi in npis:
        sig = signals.get(npi, {})
        out.append(
            {
                "org_name": "",
                "state": "",
                "city": "",
                "provider_npi": npi,
                "provider_name": "",
                "match_confidence": "high",
                "affiliation_score": 0.9,
                "match_reason": "Provided provider_npis list",
                "observed_g0444_benes": sig.get("observed_g0444_benes", 0),
                "observed_96127_benes": sig.get("observed_96127_benes", 0),
                "observed_cocm_benes": sig.get("observed_cocm_benes", 0),
                "observed_cocm_services": sig.get("observed_cocm_services", 0),
                "observed_cocm_revenue": sig.get("observed_cocm_revenue", 0.0),
            }
        )
    return out


def _providers_for_org(
    account: dict[str, object],
    org_map_path: Path,
    signals: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    if not org_map_path.exists():
        return []
    org_name = str(account.get("org_name", "")).strip().lower()
    state = str(account.get("state", "")).strip().upper()
    city = str(account.get("city", "")).strip()

    providers: list[dict[str, object]] = []
    with org_map_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_org = (row.get("org_name") or "").strip().lower()
            row_state = (row.get("state") or "").strip().upper()
            if row_org != org_name or (state and row_state and row_state != state):
                continue
            npi = (row.get("provider_npi") or "").strip()
            if not npi:
                continue
            sig = signals.get(npi, {})
            providers.append(
                {
                    "org_name": account.get("org_name", ""),
                    "state": account.get("state", ""),
                    "city": city,
                    "provider_npi": npi,
                    "provider_name": row.get("provider_name", "") or "",
                    "match_confidence": (row.get("match_confidence") or "medium").strip().lower(),
                    "affiliation_score": float(row.get("affiliation_score") or 0.0),
                    "match_reason": row.get("match_reason") or "org_provider_map match",
                    "observed_g0444_benes": sig.get("observed_g0444_benes", 0),
                    "observed_96127_benes": sig.get("observed_96127_benes", 0),
                    "observed_cocm_benes": sig.get("observed_cocm_benes", 0),
                    "observed_cocm_services": sig.get("observed_cocm_services", 0),
                    "observed_cocm_revenue": sig.get("observed_cocm_revenue", 0.0),
                }
            )
    return providers
