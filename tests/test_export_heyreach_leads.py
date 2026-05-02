"""Tests for scripts/export_heyreach_leads.py."""

from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_SPEC = importlib.util.spec_from_file_location(
    "export_heyreach_leads",
    REPO_ROOT / "scripts" / "export_heyreach_leads.py",
)
_mod = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_mod)


class TestSplitFullName(unittest.TestCase):
    def test_splits_simple(self) -> None:
        self.assertEqual(_mod.split_full_name("Jane Doe"), ("Jane", "Doe"))

    def test_strips_comma_suffix(self) -> None:
        self.assertEqual(
            _mod.split_full_name('"Dana McCalley, MBA"'),
            ("Dana", "McCalley"),
        )


class TestExportIntegration(unittest.TestCase):
    def test_export_filters_and_writes(self) -> None:
        master_headers = [
            "linkedin_profile_url",
            "full_name",
            "current_title",
            "current_company",
            "persona",
            "persona_confidence",
            "persona_rationale",
            "subtier_guess",
            "subtier_confidence",
            "signal_score",
            "location",
            "source_query",
            "date_captured",
            "heyreach_campaign",
            "notes",
        ]
        rows = [
            {
                "linkedin_profile_url": "https://www.linkedin.com/in/a/",
                "full_name": "Alex Ops",
                "current_title": "VP Operations",
                "current_company": "Sunrise Medical Group",
                "persona": "operational_owner",
                "persona_confidence": "high",
                "persona_rationale": "keyword: 'vp operations'",
                "subtier_guess": "1A",
                "subtier_confidence": "high",
                "signal_score": "40",
                "location": "",
                "source_query": "Q1",
                "date_captured": "2026-05-02",
                "heyreach_campaign": "",
                "notes": "",
            },
            {
                "linkedin_profile_url": "https://www.linkedin.com/in/b/",
                "full_name": "Sam Seller",
                "current_title": "VP Sales",
                "current_company": "VendorCo",
                "persona": "unknown",
                "persona_confidence": "high",
                "persona_rationale": "disqualified",
                "subtier_guess": "unknown",
                "subtier_confidence": "low",
                "signal_score": "0",
                "location": "",
                "source_query": "Q1",
                "date_captured": "2026-05-02",
                "heyreach_campaign": "",
                "notes": "",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "master.csv"
            out = Path(tmp) / "ready.csv"
            with src.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=master_headers)
                w.writeheader()
                w.writerows(rows)

            total, kept = _mod.export_rows(src, out, 25, False, None)
            self.assertEqual(total, 2)
            self.assertEqual(kept, 1)
            with out.open("r", encoding="utf-8", newline="") as f:
                r = list(csv.DictReader(f))
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0]["profileUrl"], "https://www.linkedin.com/in/a/")
            self.assertEqual(r[0]["firstName"], "Alex")
            self.assertEqual(r[0]["persona"], "operational_owner")

            _, kept_t12 = _mod.export_rows(src, out, 25, True, None)
            self.assertEqual(kept_t12, 1)

    def test_per_subtier_cap(self) -> None:
        master_headers = [
            "linkedin_profile_url",
            "full_name",
            "current_title",
            "current_company",
            "persona",
            "persona_confidence",
            "persona_rationale",
            "subtier_guess",
            "subtier_confidence",
            "signal_score",
            "location",
            "source_query",
            "date_captured",
            "heyreach_campaign",
            "notes",
        ]
        rows = []
        for i in range(5):
            rows.append(
                {
                    "linkedin_profile_url": f"https://www.linkedin.com/in/u{i}/",
                    "full_name": f"User {i}",
                    "current_title": "Director",
                    "current_company": "Co",
                    "persona": "operational_owner",
                    "persona_confidence": "high",
                    "persona_rationale": "keyword: x",
                    "subtier_guess": "1A",
                    "subtier_confidence": "high",
                    "signal_score": str(40 - i),
                    "location": "",
                    "source_query": "Q",
                    "date_captured": "",
                    "heyreach_campaign": "",
                    "notes": "",
                }
            )
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "master.csv"
            out = Path(tmp) / "ready.csv"
            with src.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=master_headers)
                w.writeheader()
                w.writerows(rows)

            _, kept = _mod.export_rows(src, out, 25, False, 2)
            self.assertEqual(kept, 2)


if __name__ == "__main__":
    unittest.main()
