"""Tests for Tier 2A ACO attack list logic."""

from tam_builder.aco_attack import (
    classify_fit_tier,
    exclusion_reason,
    parse_mssp_org_rows,
)
from tam_builder.aco_persona_rules import (
    classify_persona,
    is_anti_persona,
    is_cms_placeholder_contact,
)


def test_classify_fit_tier_high():
    assert classify_fit_tier(enhanced=True, period=3) == "HIGH"
    assert classify_fit_tier(enhanced=False, period=3, reach=True) == "HIGH"


def test_exclusion_hospital_only():
    assert exclusion_reason("Springfield Regional Hospital") == "hospital_only"
    assert exclusion_reason("Springfield Physician ACO") == ""


def test_parse_mssp_org_rows_minimal():
    csv_text = (
        "aco_id,aco_name,aco_service_area,agreement_period_num,enhanced_track,"
        "basic_track,basic_track_level,aco_exec_name,aco_exec_email,aco_exec_phone,"
        "aco_medical_director_name,pc_flex_agreement_status\n"
        "1,Test Physician ACO LLC,GA,3,1,0,,Jane Doe,jane@test.org,555,"
        "Dr Smith,0\n"
        "2,Shell Management LLC,TX,1,0,0,,,,,,0\n"
    )
    rows = parse_mssp_org_rows(csv_text)
    by_name = {r.aco_name: r for r in rows}
    assert by_name["Test Physician ACO LLC"].fit_tier == "HIGH"
    assert by_name["Test Physician ACO LLC"].exclude_reason == ""
    assert by_name["Shell Management LLC"].exclude_reason == "admin_shell"


def test_persona_classify_pop_health():
    bucket, conf = classify_persona("VP Population Health at Example ACO")
    assert bucket == "op_owner"
    assert conf == "H"


def test_anti_persona_recruiter():
    assert is_anti_persona("Technical Recruiter", "Some Health System")


def test_cms_placeholder_exec():
    assert is_cms_placeholder_contact("ACO Executive (per CMS public filing)")
