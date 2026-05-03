"""Tests for scripts/build_list_1a.py — taxonomy filter + NPPES org-size proxy."""

from __future__ import annotations

import csv
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_SPEC = importlib.util.spec_from_file_location(
    "build_list_1a",
    REPO_ROOT / "scripts" / "build_list_1a.py",
)
_mod = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_mod)


# Real NPPES taxonomy codes used in production data.
FAMILY_MED = "207Q00000X"
INTERNAL_MED = "207R00000X"
ADULT_MED = "207QA0505X"
NP_PRIMARY = "363L00000X"
GENERAL_PRACTICE = "208D00000X"
PEDIATRICS = "208000000X"
CARDIOLOGY = "207RC0000X"  # NOT primary care — should be filtered out


class TestTaxonomyFilter(unittest.TestCase):
    """The PCP-broad set: FM, IM, Adult Med, NP-Primary-Care, GP, Peds."""

    def test_all_six_codes_present(self) -> None:
        expected = {
            "207Q00000X",  # Family Medicine
            "207R00000X",  # Internal Medicine
            "207QA0505X",  # Adult Medicine
            "363L00000X",  # NP, Primary Care
            "208D00000X",  # General Practice
            "208000000X",  # Pediatrics
        }
        self.assertEqual(_mod.PRIMARY_CARE_TAXONOMY_CODES, expected)

    def test_does_not_include_specialty_codes(self) -> None:
        self.assertNotIn(CARDIOLOGY, _mod.PRIMARY_CARE_TAXONOMY_CODES)
        self.assertNotIn("207RG0100X", _mod.PRIMARY_CARE_TAXONOMY_CODES)  # Geriatric IM
        self.assertNotIn("207XS0114X", _mod.PRIMARY_CARE_TAXONOMY_CODES)  # Sports Med


def _make_row(
    npi: str,
    org_name: str,
    state: str = "TX",
    entity_type: str = "2",
    taxonomy: str = FAMILY_MED,
    ao_last: str = "Smith",
    ao_first: str = "Jane",
) -> dict[str, str]:
    """Build a minimal NPPES Type-2 row dict with the columns aggregate_orgs uses."""
    return {
        "NPI": npi,
        "Entity Type Code": entity_type,
        "Provider Organization Name (Legal Business Name)": org_name,
        "Provider Business Practice Location Address State Name": state,
        "Healthcare Provider Taxonomy Code_1": taxonomy,
        "Authorized Official Last Name": ao_last,
        "Authorized Official First Name": ao_first,
    }


class TestAggregateOrgsFromNPPES(unittest.TestCase):
    """Pass-1 aggregation: groups by (org_name_upper, state), counts NPIs, applies taxonomy."""

    def test_groups_same_org_across_npis(self) -> None:
        rows = [
            _make_row("1000000001", "ABC Family Medicine LLC", state="TX"),
            _make_row("1000000002", "ABC Family Medicine LLC", state="TX"),
            _make_row("1000000003", "ABC Family Medicine LLC", state="TX"),
        ]
        org_data, stats = _mod.aggregate_orgs_from_nppes(iter(rows))
        self.assertEqual(len(org_data), 1)
        key = ("ABC FAMILY MEDICINE LLC", "TX")
        self.assertEqual(org_data[key]["count"], 3)
        self.assertEqual(org_data[key]["original_name"], "ABC Family Medicine LLC")

    def test_separates_orgs_by_state(self) -> None:
        rows = [
            _make_row("1000000001", "Acme Medical Group", state="TX"),
            _make_row("1000000002", "Acme Medical Group", state="CA"),
        ]
        org_data, _ = _mod.aggregate_orgs_from_nppes(iter(rows))
        self.assertEqual(len(org_data), 2)
        self.assertIn(("ACME MEDICAL GROUP", "TX"), org_data)
        self.assertIn(("ACME MEDICAL GROUP", "CA"), org_data)

    def test_filters_non_primary_care_taxonomy(self) -> None:
        rows = [
            _make_row("1000000001", "Cardio Specialty Group", taxonomy=CARDIOLOGY),
            _make_row("1000000002", "Family Med Group", taxonomy=FAMILY_MED),
        ]
        org_data, stats = _mod.aggregate_orgs_from_nppes(iter(rows))
        self.assertEqual(len(org_data), 1)
        self.assertEqual(stats["skipped_no_primary_care"], 1)
        self.assertIn(("FAMILY MED GROUP", "TX"), org_data)

    def test_keeps_all_six_taxonomy_codes(self) -> None:
        rows = [
            _make_row("1", "FM Group", taxonomy=FAMILY_MED),
            _make_row("2", "IM Group", taxonomy=INTERNAL_MED),
            _make_row("3", "Adult Group", taxonomy=ADULT_MED),
            _make_row("4", "NP Group", taxonomy=NP_PRIMARY),
            _make_row("5", "GP Group", taxonomy=GENERAL_PRACTICE),
            _make_row("6", "Peds Group", taxonomy=PEDIATRICS),
        ]
        org_data, _ = _mod.aggregate_orgs_from_nppes(iter(rows))
        self.assertEqual(len(org_data), 6)

    def test_filters_non_type2_entities(self) -> None:
        rows = [
            _make_row("1000000001", "Type-1 Provider", entity_type="1"),
            _make_row("1000000002", "Type-2 Org", entity_type="2"),
        ]
        org_data, stats = _mod.aggregate_orgs_from_nppes(iter(rows))
        self.assertEqual(len(org_data), 1)
        self.assertEqual(stats["skipped_not_type2"], 1)

    def test_state_filter_applies(self) -> None:
        rows = [
            _make_row("1", "TX Group", state="TX"),
            _make_row("2", "CA Group", state="CA"),
            _make_row("3", "NY Group", state="NY"),
        ]
        org_data, stats = _mod.aggregate_orgs_from_nppes(iter(rows), state_filter={"TX", "CA"})
        self.assertEqual(len(org_data), 2)
        self.assertEqual(stats["skipped_state"], 1)

    def test_taxonomy_match_in_any_slot(self) -> None:
        # Real NPPES has taxonomy codes 1-15. We should find matches anywhere.
        row = _make_row("1", "Multi-Tax Group", taxonomy=CARDIOLOGY)
        row["Healthcare Provider Taxonomy Code_3"] = FAMILY_MED  # FM in slot 3
        org_data, _ = _mod.aggregate_orgs_from_nppes(iter([row]))
        self.assertEqual(len(org_data), 1)


class TestNoiseFilter(unittest.TestCase):
    """Hospital/IDN/academic/govt noise patterns are dropped by default."""

    def test_drops_hospital(self) -> None:
        self.assertTrue(_mod.is_org_noise("MERCY HOSPITAL OF DENVER"))
        self.assertTrue(_mod.is_org_noise("CHILDREN'S HOSPITAL OF PHILADELPHIA"))
        self.assertTrue(_mod.is_org_noise("DEACONESS HOSPITAL, INC"))

    def test_drops_medical_center(self) -> None:
        self.assertTrue(_mod.is_org_noise("SPARTANBURG MEDICAL CENTER"))
        self.assertTrue(_mod.is_org_noise("RUSH UNIVERSITY MEDICAL CENTER"))

    def test_drops_health_system(self) -> None:
        self.assertTrue(_mod.is_org_noise("GENESIS HEALTH SYSTEM"))
        self.assertTrue(_mod.is_org_noise("PROVIDENCE HEALTH & SERVICES - OREGON"))
        self.assertTrue(_mod.is_org_noise("UNIVERSITY HEALTH SYSTEM, INC"))

    def test_drops_university_and_govt(self) -> None:
        self.assertTrue(_mod.is_org_noise("BOARD OF REGENTS OF THE UNIVERSITY OF OKLAHOMA"))
        self.assertTrue(_mod.is_org_noise("UNIVERSITY OF MIAMI"))
        self.assertTrue(_mod.is_org_noise("HEALTH AND HUMAN SERVICES COMMISSION"))
        self.assertTrue(_mod.is_org_noise("DEPARTMENT OF VETERANS AFFAIRS"))

    def test_keeps_real_pcp_groups(self) -> None:
        self.assertFalse(_mod.is_org_noise("HATTIESBURG CLINIC PA"))
        self.assertFalse(_mod.is_org_noise("ABC FAMILY MEDICINE LLC"))
        self.assertFalse(_mod.is_org_noise("MEDICAL ASSOCIATES OF THE LEHIGH VALLEY PC"))
        self.assertFalse(_mod.is_org_noise("HEALTHPOINT MEDICAL GROUP INC"))
        self.assertFalse(_mod.is_org_noise("LOWCOUNTRY MEDICAL ASSOCIATES"))

    def test_noise_filter_runs_in_main(self) -> None:
        rows = [_make_row(str(i), "Mercy Hospital", state="TX") for i in range(3)]
        rows += [_make_row(str(100 + i), "FM Group LLC", state="TX") for i in range(3)]

        with tempfile.TemporaryDirectory() as td:
            in_path = Path(td) / "fake.csv"
            out_path = Path(td) / "out.csv"
            # write fake nppes
            header_set: set[str] = set()
            for r in rows:
                header_set.update(r.keys())
            with in_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=sorted(header_set))
                writer.writeheader()
                for r in rows:
                    writer.writerow(r)
            rc = _mod.main(["--nppes-csv", str(in_path), "--out", str(out_path)])
            self.assertEqual(rc, 0)
            with out_path.open() as f:
                out_rows = list(csv.DictReader(f))
            # Hospital dropped; FM Group kept.
            self.assertEqual(len(out_rows), 1)
            self.assertEqual(out_rows[0]["Organization Name"], "FM Group LLC")

    def test_include_noise_disables_filter(self) -> None:
        rows = [_make_row(str(i), "Mercy Hospital", state="TX") for i in range(3)]

        with tempfile.TemporaryDirectory() as td:
            in_path = Path(td) / "fake.csv"
            out_path = Path(td) / "out.csv"
            header_set: set[str] = set()
            for r in rows:
                header_set.update(r.keys())
            with in_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=sorted(header_set))
                writer.writeheader()
                for r in rows:
                    writer.writerow(r)
            rc = _mod.main(
                ["--nppes-csv", str(in_path), "--out", str(out_path), "--include-noise"]
            )
            self.assertEqual(rc, 0)
            with out_path.open() as f:
                out_rows = list(csv.DictReader(f))
            self.assertEqual(len(out_rows), 1)
            self.assertEqual(out_rows[0]["Organization Name"], "Mercy Hospital")


class TestSizeGateIntegration(unittest.TestCase):
    """End-to-end main() — size gate filters single-site orgs and mega-chains."""

    def _write_fake_nppes(self, path: Path, rows: list[dict[str, str]]) -> None:
        # Use the union of keys as headers — DictWriter requires a fixed list.
        header_set: set[str] = set()
        for r in rows:
            header_set.update(r.keys())
        headers = sorted(header_set)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

    def test_size_gate_drops_single_npi_orgs(self) -> None:
        # 1 row for "Solo Practice" (count=1, dropped at min=2)
        # 3 rows for "Multi-Site Group" (count=3, kept)
        # 50 rows for "Mega Chain" (count=50, dropped at max=30)
        rows = [_make_row("1", "Solo Practice", state="TX")]
        rows += [_make_row(str(2 + i), "Multi-Site Group", state="TX") for i in range(3)]
        rows += [_make_row(str(100 + i), "Mega Chain", state="TX") for i in range(50)]

        with tempfile.TemporaryDirectory() as td:
            in_path = Path(td) / "fake_nppes.csv"
            out_path = Path(td) / "out.csv"
            self._write_fake_nppes(in_path, rows)
            rc = _mod.main([
                "--nppes-csv",
                str(in_path),
                "--out",
                str(out_path),
                "--min-org-npis",
                "2",
                "--max-org-npis",
                "30",
            ])
            self.assertEqual(rc, 0)
            with out_path.open() as f:
                out_rows = list(csv.DictReader(f))
            self.assertEqual(len(out_rows), 1)
            self.assertEqual(out_rows[0]["Organization Name"], "Multi-Site Group")
            self.assertEqual(out_rows[0]["State Code"], "TX")
            self.assertIn("npi_count=3", out_rows[0]["Internal Notes"])

    def test_drops_specialty_taxonomy_at_aggregation(self) -> None:
        rows = [_make_row(str(i), "Cardio Group", taxonomy=CARDIOLOGY) for i in range(5)]
        rows += [_make_row(str(100 + i), "FM Group", taxonomy=FAMILY_MED) for i in range(3)]

        with tempfile.TemporaryDirectory() as td:
            in_path = Path(td) / "fake_nppes.csv"
            out_path = Path(td) / "out.csv"
            self._write_fake_nppes(in_path, rows)
            rc = _mod.main([
                "--nppes-csv",
                str(in_path),
                "--out",
                str(out_path),
            ])
            self.assertEqual(rc, 0)
            with out_path.open() as f:
                out_rows = list(csv.DictReader(f))
            self.assertEqual(len(out_rows), 1)
            self.assertEqual(out_rows[0]["Organization Name"], "FM Group")


if __name__ == "__main__":
    unittest.main()
