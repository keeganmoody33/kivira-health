from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tam_builder.adapters import SyntheticPublicSignalAdapter
from tam_builder.briefing import generate_briefs
from tam_builder.estimation import estimate_accounts
from tam_builder.io_utils import load_json, read_csv
from tam_builder.normalize import normalize_accounts
from tam_builder.personas import route_persona_row
from tam_builder.tiering import tier_account_row


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "fixtures"
SCRIPT_PATH = REPO_ROOT / "scripts" / "kivira_tam_builder.py"


class TestNormalization(unittest.TestCase):
    def test_normalize_fixture_accounts(self) -> None:
        raw_rows = read_csv(FIXTURES_DIR / "raw_accounts.csv")
        normalized_rows, errors, column_map = normalize_accounts(raw_rows)

        self.assertFalse(errors)
        self.assertEqual(4, len(normalized_rows))
        self.assertEqual("Organization Name", column_map["org_name"])
        self.assertEqual("State Code", column_map["state"])

        aco_row = next(row for row in normalized_rows if row["org_name"] == "North Star ACO")
        self.assertEqual("aco_parent", aco_row["org_type"])
        self.assertEqual("NC", aco_row["state"])
        self.assertEqual("north-star-aco-nc", aco_row["normalized_org_key"])

    def test_invalid_rows_surface_validation_errors(self) -> None:
        raw_rows = read_csv(FIXTURES_DIR / "invalid_accounts.csv")
        normalized_rows, errors, _ = normalize_accounts(raw_rows)

        self.assertEqual([], normalized_rows)
        self.assertGreaterEqual(len(errors), 4)
        fields = {error["field"] for error in errors}
        self.assertIn("org_name", fields)
        self.assertIn("state", fields)
        self.assertIn("org_type", fields)
        self.assertIn("max_candidates", fields)


class TestPipeline(unittest.TestCase):
    def setUp(self) -> None:
        raw_rows = read_csv(FIXTURES_DIR / "raw_accounts.csv")
        normalized_rows, errors, _ = normalize_accounts(raw_rows)
        self.assertFalse(errors)
        self.normalized_rows = normalized_rows

    def test_estimation_tiering_and_routing_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            estimates = estimate_accounts(
                self.normalized_rows,
                adapter=SyntheticPublicSignalAdapter(),
                artifact_dir=Path(tmpdir) / "artifacts",
                include_low_confidence=True,
            )

        by_org = {row["org_name"]: row for row in estimates}
        self.assertEqual("A", by_org["North Star ACO"]["confidence_grade"])
        self.assertEqual("B", by_org["Sunrise Medical Group"]["confidence_grade"])
        self.assertEqual("C", by_org["Riverbend Independent Primary Care"]["confidence_grade"])
        self.assertEqual("D", by_org["Oak Lane Family Practice"]["confidence_grade"])

        self.assertAlmostEqual(78280.0, by_org["North Star ACO"]["base_gap"])
        self.assertAlmostEqual(31576.0, by_org["Sunrise Medical Group"]["base_gap"])
        self.assertAlmostEqual(10300.0, by_org["Riverbend Independent Primary Care"]["base_gap"])
        self.assertAlmostEqual(0.0, by_org["Oak Lane Family Practice"]["base_gap"])

        tiered = {row["org_name"]: tier_account_row(row) for row in estimates}
        self.assertEqual("Tier 1", tiered["North Star ACO"]["tier"])
        self.assertEqual("Tier 2", tiered["Sunrise Medical Group"]["tier"])
        self.assertEqual("Tier 3", tiered["Riverbend Independent Primary Care"]["tier"])
        self.assertEqual("Tier 4", tiered["Oak Lane Family Practice"]["tier"])

        routed = {row["org_name"]: route_persona_row(row) for row in tiered.values()}
        self.assertEqual("pop_health|cfo|bh_ops", routed["North Star ACO"]["persona_sequence"])
        self.assertEqual("medical_director|cfo|cmio", routed["Sunrise Medical Group"]["persona_sequence"])
        self.assertEqual("medical_director|cfo|pcp", routed["Riverbend Independent Primary Care"]["persona_sequence"])
        self.assertEqual("pcp|cfo", routed["Oak Lane Family Practice"]["persona_sequence"])

    def test_contract_artifacts_and_guardrails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir) / "artifacts"
            estimates = estimate_accounts(
                self.normalized_rows,
                adapter=SyntheticPublicSignalAdapter(),
                artifact_dir=artifact_dir,
                include_low_confidence=True,
            )
            tiered = [tier_account_row(row) for row in estimates]
            routed = [route_persona_row(row) for row in tiered]
            briefs = generate_briefs(routed)

            for slug in (
                "north-star-aco",
                "sunrise-medical-group",
                "riverbend-independent-primary-care",
                "oak-lane-family-practice",
            ):
                summary_json = artifact_dir / f"{slug}_estimate.json"
                summary_csv = artifact_dir / f"{slug}_estimate.csv"
                provider_debug_csv = artifact_dir / f"{slug}_provider_debug.csv"
                self.assertTrue(summary_json.exists())
                self.assertTrue(summary_csv.exists())
                self.assertTrue(provider_debug_csv.exists())

            north_star_json = load_json(artifact_dir / "north-star-aco_estimate.json")
            self.assertIn("observed_metrics", north_star_json)
            self.assertIn("modeled_opportunity", north_star_json)
            self.assertIn("persona_messages", north_star_json)
            self.assertEqual("A", north_star_json["confidence_grade"])

            provider_rows = read_csv(artifact_dir / "north-star-aco_provider_debug.csv")
            self.assertEqual(18, len(provider_rows))
            self.assertEqual(
                [
                    "org_name",
                    "state",
                    "city",
                    "provider_npi",
                    "provider_name",
                    "match_confidence",
                    "affiliation_score",
                    "match_reason",
                    "observed_g0444_benes",
                    "observed_96127_benes",
                    "observed_cocm_benes",
                    "observed_cocm_services",
                    "observed_cocm_revenue",
                ],
                list(provider_rows[0].keys()),
            )

            c_and_d_briefs = [brief for brief in briefs if brief["confidence_grade"] in {"C", "D"}]
            self.assertTrue(c_and_d_briefs)
            for brief in c_and_d_briefs:
                self.assertNotRegex(brief["outbound_message"], r"\$")
                self.assertNotRegex(brief["outbound_message"], r"\d")

            for brief in briefs:
                lowered = brief["outbound_message"].lower()
                self.assertNotIn("autonomous diagnosis", lowered)
                self.assertNotIn("replace clinical judgment", lowered)
                self.assertNotIn("diagnose patients automatically", lowered)

            cmio_brief = next(brief for brief in briefs if brief["persona"] == "cmio")
            self.assertIn("CDS-aligned", cmio_brief["value_prop_angle"])


class TestCliSmoke(unittest.TestCase):
    def test_cli_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            normalized_path = tmpdir_path / "normalized.csv"
            estimates_path = tmpdir_path / "estimates.csv"
            tiered_path = tmpdir_path / "tiered.csv"
            routed_path = tmpdir_path / "routed.csv"
            briefs_path = tmpdir_path / "briefs.csv"
            artifact_dir = tmpdir_path / "artifacts"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "normalize-accounts",
                    "--input",
                    str(FIXTURES_DIR / "raw_accounts.csv"),
                    "--output",
                    str(normalized_path),
                ],
                cwd=REPO_ROOT,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "estimate-cocm",
                    "--input",
                    str(normalized_path),
                    "--output",
                    str(estimates_path),
                    "--artifact-dir",
                    str(artifact_dir),
                    "--adapter",
                    "synthetic",
                    "--include-low-confidence",
                ],
                cwd=REPO_ROOT,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "tier-accounts",
                    "--input",
                    str(estimates_path),
                    "--output",
                    str(tiered_path),
                ],
                cwd=REPO_ROOT,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "route-personas",
                    "--input",
                    str(tiered_path),
                    "--output",
                    str(routed_path),
                ],
                cwd=REPO_ROOT,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "generate-briefs",
                    "--input",
                    str(routed_path),
                    "--output",
                    str(briefs_path),
                ],
                cwd=REPO_ROOT,
                check=True,
            )

            normalized_rows = read_csv(normalized_path)
            estimate_rows = read_csv(estimates_path)
            brief_rows = read_csv(briefs_path)
            self.assertEqual(4, len(normalized_rows))
            self.assertEqual(4, len(estimate_rows))
            self.assertGreater(len(brief_rows), 4)


if __name__ == "__main__":
    unittest.main()
