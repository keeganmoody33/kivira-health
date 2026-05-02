from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd

from tam_builder.pilot_filters import filter_classified_pilot, resolve_output_dir

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script_module(name: str, rel_path: str):
    path = REPO_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestPilotFilters(unittest.TestCase):
    def test_filter_subtier_and_max(self) -> None:
        df = pd.DataFrame(
            [
                {"account_id": "2", "subtier_primary": "1A", "classification_status": "classified", "classification_confidence": "0.9"},
                {"account_id": "1", "subtier_primary": "1B", "classification_status": "classified", "classification_confidence": "0.9"},
                {"account_id": "3", "subtier_primary": "1A", "classification_status": "classified", "classification_confidence": "0.9"},
            ]
        )
        out = filter_classified_pilot(df, subtier="1A", max_accounts=1, require_website=False, min_classification_confidence=0.0)
        self.assertEqual(len(out), 1)
        self.assertEqual(out.iloc[0]["account_id"], "2")  # 1A rows sorted by account_id: 2 before 3

    def test_exclude_classification_excluded(self) -> None:
        df = pd.DataFrame(
            [
                {"account_id": "x", "subtier_primary": "1A", "classification_status": "excluded"},
                {"account_id": "y", "subtier_primary": "1A", "classification_status": "classified"},
            ]
        )
        out = filter_classified_pilot(df, subtier="1A")
        self.assertEqual(len(out), 1)
        self.assertEqual(out.iloc[0]["account_id"], "y")

    def test_require_website(self) -> None:
        df = pd.DataFrame(
            [
                {"account_id": "a", "subtier_primary": "1A", "classification_status": "classified", "website": ""},
                {"account_id": "b", "subtier_primary": "1A", "classification_status": "classified", "website": "https://x.org"},
            ]
        )
        out = filter_classified_pilot(df, subtier="1A", require_website=True)
        self.assertEqual(len(out), 1)
        self.assertEqual(out.iloc[0]["account_id"], "b")


class Test04DedupeContacts(unittest.TestCase):
    def test_dedupe_sets_duplicate_flag(self) -> None:
        ext = _load_script_module("kivira_extract_contacts", "04_extract_contacts.py")
        rows = [
            {
                "account_id": "a1",
                "person_name": "Jane Doe",
                "title_normalized": "Director",
                "job_title": "Director",
                "source_domain": "clinic.org",
            },
            {
                "account_id": "a1",
                "person_name": "Jane Doe",
                "title_normalized": "Director",
                "job_title": "Director",
                "source_domain": "clinic.org",
            },
        ]
        out = ext.dedupe_contacts(rows)
        self.assertEqual(len(out), 2)
        flags = [r.get("duplicate_person_flag") for r in out]
        self.assertIn("false", flags)
        self.assertIn("true", flags)


class Test07EmptyReviewDataframeColumns(unittest.TestCase):
    def test_empty_accounts_reviewed_has_qa_status(self) -> None:
        # Mirrors 07 post-loop column materialization (empty Wave 1 → no KeyError on qa_status).
        REVIEW_ACCOUNT_COLUMNS = [
            "account_id",
            "org_name",
            "parent_org_id",
            "primary_state",
            "subtier_primary",
            "primary_contact_id",
            "backup_contact_id",
            "economic_buyer_id",
            "committee_coverage_score",
            "account_readiness_score",
            "qa_status",
            "qa_reason",
            "dedupe_group_id",
            "dedupe_decision",
            "launch_blocker_flag",
            "evidence_notes",
            "last_verified_at",
        ]
        accounts_reviewed_df = pd.DataFrame([])
        for c in REVIEW_ACCOUNT_COLUMNS:
            if c not in accounts_reviewed_df.columns:
                accounts_reviewed_df[c] = ""
        self.assertIn("qa_status", accounts_reviewed_df.columns)
        pass_accounts = accounts_reviewed_df[accounts_reviewed_df["qa_status"] == "pass"].copy()
        self.assertEqual(len(pass_accounts), 0)


class TestResolveOutputDir(unittest.TestCase):
    def test_nested_pilot(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "repo"
            base.mkdir()
            out = resolve_output_dir(base, "pilot")
            self.assertEqual(out.name, "pilot")
            self.assertEqual(out.parent.name, "output")
            self.assertTrue(out.is_dir())


if __name__ == "__main__":
    unittest.main()
