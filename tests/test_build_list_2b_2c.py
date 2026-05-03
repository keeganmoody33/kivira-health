"""Tests for scripts/build_list_2b_2c.py — MSSP persona pivot for 2B/2C."""

from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_SPEC = importlib.util.spec_from_file_location(
    "build_list_2b_2c",
    REPO_ROOT / "scripts" / "build_list_2b_2c.py",
)
_mod = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_mod)


def _mssp_row(
    aco_id: str,
    aco_name: str,
    par_lbn: str = "Some Practice LLC",
    service_area: str = "TX",
    medical_director: str = "",
    compliance_contact: str = "",
    exec_name: str = "",
) -> dict[str, str]:
    return {
        "ACO_ID": aco_id,
        "Par_LBN": par_lbn,
        "ACO_Name": aco_name,
        "ACO_Service_Area": service_area,
        "ACO_Exec_Name": exec_name,
        "ACO_Medical_Director_Name": medical_director,
        "ACO_Compliance_Contact_Name": compliance_contact,
    }


class TestPersonaPivot2B(unittest.TestCase):
    """2B = clinical champion via ACO_Medical_Director_Name."""

    def test_extracts_medical_director(self) -> None:
        rows = [
            _mssp_row("A001", "Acme ACO LLC", medical_director="Dr. Jane Lee, MD"),
        ]
        out = _mod.parse_mssp_for_persona(rows, "2B")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["Organization Name"], "Acme ACO LLC")
        self.assertEqual(out[0]["Contact Name"], "Dr. Jane Lee, MD")
        self.assertIn("subtier=2B", out[0]["Internal Notes"])
        self.assertEqual(out[0]["Priority Personas"], "clinical_champion")
        self.assertIn("Medical Director", out[0]["Contact Title"])

    def test_skips_aco_with_no_medical_director(self) -> None:
        rows = [
            _mssp_row("A001", "ACO With Director", medical_director="Dr. A"),
            _mssp_row("A002", "ACO Without Director", medical_director=""),
        ]
        out = _mod.parse_mssp_for_persona(rows, "2B")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["Organization Name"], "ACO With Director")

    def test_dedupes_at_aco_id(self) -> None:
        # Same ACO appears N times (once per Par_LBN). Should emit ONCE for 2B.
        rows = [
            _mssp_row("A001", "Acme ACO", par_lbn=f"Practice {i}", medical_director="Dr. Jane")
            for i in range(5)
        ]
        out = _mod.parse_mssp_for_persona(rows, "2B")
        self.assertEqual(len(out), 1)


class TestPersonaPivot2C(unittest.TestCase):
    """2C = economic buyer / contract via ACO_Compliance_Contact_Name."""

    def test_extracts_compliance_contact(self) -> None:
        rows = [
            _mssp_row("A001", "Beta ACO LLC", compliance_contact="Sam Compliance"),
        ]
        out = _mod.parse_mssp_for_persona(rows, "2C")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["Contact Name"], "Sam Compliance")
        self.assertEqual(out[0]["Priority Personas"], "economic_buyer")
        self.assertIn("subtier=2C", out[0]["Internal Notes"])
        self.assertIn("Compliance", out[0]["Contact Title"])

    def test_2b_and_2c_are_independent_pivots(self) -> None:
        rows = [
            _mssp_row(
                "A001",
                "Hybrid ACO",
                medical_director="Dr. Clinical",
                compliance_contact="Mr. Compliance",
            ),
        ]
        out_2b = _mod.parse_mssp_for_persona(rows, "2B")
        out_2c = _mod.parse_mssp_for_persona(rows, "2C")
        self.assertEqual(len(out_2b), 1)
        self.assertEqual(len(out_2c), 1)
        self.assertEqual(out_2b[0]["Contact Name"], "Dr. Clinical")
        self.assertEqual(out_2c[0]["Contact Name"], "Mr. Compliance")
        # Source IDs must differ so dedup downstream works correctly.
        self.assertNotEqual(out_2b[0]["Source ID"], out_2c[0]["Source ID"])


class TestStateNormalization(unittest.TestCase):
    def test_takes_first_state_from_comma_list(self) -> None:
        rows = [
            _mssp_row("A001", "Multi-State ACO", service_area="TX, NM, OK", medical_director="Dr. X"),
        ]
        out = _mod.parse_mssp_for_persona(rows, "2B")
        self.assertEqual(out[0]["State Code"], "TX")

    def test_uppercases_state(self) -> None:
        rows = [
            _mssp_row("A001", "Some ACO", service_area="ca", medical_director="Dr. X"),
        ]
        out = _mod.parse_mssp_for_persona(rows, "2B")
        self.assertEqual(out[0]["State Code"], "CA")


class TestUnknownSubtierRejected(unittest.TestCase):
    def test_raises_on_unknown_subtier(self) -> None:
        with self.assertRaises(ValueError):
            _mod.parse_mssp_for_persona([], "9Z")


class TestMainIntegration(unittest.TestCase):
    def test_main_writes_both_outputs(self) -> None:
        rows = [
            _mssp_row(
                "A001",
                "ACO One",
                medical_director="Dr. Med One",
                compliance_contact="Mr. Comp One",
            ),
            _mssp_row(
                "A002",
                "ACO Two",
                medical_director="Dr. Med Two",
                # No compliance contact — should appear in 2B but not 2C.
                compliance_contact="",
            ),
        ]
        with tempfile.TemporaryDirectory() as td:
            in_path = Path(td) / "mssp.csv"
            out_2b = Path(td) / "out_2b.csv"
            out_2c = Path(td) / "out_2c.csv"
            with in_path.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=sorted(rows[0].keys()))
                w.writeheader()
                for r in rows:
                    w.writerow(r)

            rc = _mod.main([
                "--mssp-csv",
                str(in_path),
                "--out-2b",
                str(out_2b),
                "--out-2c",
                str(out_2c),
            ])
            self.assertEqual(rc, 0)

            with out_2b.open() as f:
                rows_2b = list(csv.DictReader(f))
            with out_2c.open() as f:
                rows_2c = list(csv.DictReader(f))
            self.assertEqual(len(rows_2b), 2)
            self.assertEqual(len(rows_2c), 1)
            self.assertEqual(rows_2c[0]["Organization Name"], "ACO One")


if __name__ == "__main__":
    unittest.main()
