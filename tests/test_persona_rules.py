"""Regression tests for tam_builder.persona_rules (Wave 1 LinkedIn tagging)."""

from __future__ import annotations

import unittest

from tam_builder.persona_rules import (
    company_signals_not_1a,
    refine_subtier_1a,
    tag_persona_keyword,
)


class TestPresidentAndDisqualifiers(unittest.TestCase):
    def test_vp_value_based_care_not_economic_buyer_via_president(self) -> None:
        """Bare 'president' must not match inside 'Vice President'."""
        tag = tag_persona_keyword(
            "Vice President (VP) of Value-Based Care", "Navina"
        )
        self.assertNotEqual(tag["persona"], "economic_buyer")

    def test_president_medicare_advantage_is_economic_buyer(self) -> None:
        tag = tag_persona_keyword("President, Medicare Advantage", "Humana")
        self.assertEqual(tag["persona"], "economic_buyer")
        self.assertEqual(tag["confidence"], "high")
        self.assertIn("president", tag["rationale"])

    def test_chro_disqualified(self) -> None:
        tag = tag_persona_keyword(
            "Senior Vice President and Chief Human Resource Officer",
            "HCA Healthcare",
        )
        self.assertEqual(tag["persona"], "unknown")
        self.assertEqual(tag["confidence"], "high")
        self.assertIn("disqualified", tag["rationale"])

    def test_chief_of_staff_disqualified(self) -> None:
        tag = tag_persona_keyword(
            "Vice President, Sr. Strategic Advisor & Chief of Staff to the Group President",
            "CVS Health",
        )
        self.assertEqual(tag["persona"], "unknown")
        self.assertIn("chief of staff", tag["rationale"])

    def test_svp_sales_disqualified(self) -> None:
        tag = tag_persona_keyword(
            "Senior Vice President of Sales and CX (HDMS)",
            "Aetna",
        )
        self.assertEqual(tag["persona"], "unknown")
        self.assertIn("disqualified", tag["rationale"])

    def test_cmio_tech_gatekeeper(self) -> None:
        tag = tag_persona_keyword("CMIO", "Northside Hospital")
        self.assertEqual(tag["persona"], "tech_gatekeeper")

    def test_cfo_economic_buyer(self) -> None:
        tag = tag_persona_keyword("CFO", "Privia Health")
        self.assertEqual(tag["persona"], "economic_buyer")

    def test_software_engineer_disqualified(self) -> None:
        tag = tag_persona_keyword("Senior Software Engineer", "Epic")
        self.assertEqual(tag["persona"], "unknown")
        self.assertIn("disqualified", tag["rationale"])

    def test_data_architect_disqualified(self) -> None:
        tag = tag_persona_keyword(
            "Data Architect | Technology Consultant", "IQVIA"
        )
        self.assertEqual(tag["persona"], "unknown")

    def test_financial_professional_disqualified(self) -> None:
        tag = tag_persona_keyword("Financial Professional", "American Shared Hospital Services")
        self.assertEqual(tag["persona"], "unknown")

    def test_chief_strategy_officer_economic_buyer(self) -> None:
        tag = tag_persona_keyword("Chief Strategy Officer", "MemorialCare")
        self.assertEqual(tag["persona"], "economic_buyer")


class TestRefineSubtier1A(unittest.TestCase):
    def test_navina_demotes_1a(self) -> None:
        st, conf = refine_subtier_1a("1A", "Navina")
        self.assertEqual(st, "unknown")
        self.assertEqual(conf, "low")

    def test_clean_medical_group_keeps_1a(self) -> None:
        st, conf = refine_subtier_1a("1A", "Sunrise Medical Group")
        self.assertEqual(st, "1A")
        self.assertEqual(conf, "high")

    def test_hospital_system_demotes(self) -> None:
        self.assertTrue(company_signals_not_1a("MetroHealth System"))

    def test_non_1a_code_passes_through(self) -> None:
        st, conf = refine_subtier_1a("3A (health system)", "Wellstar")
        self.assertEqual(st, "3A")
        self.assertEqual(conf, "high")


if __name__ == "__main__":
    unittest.main()
