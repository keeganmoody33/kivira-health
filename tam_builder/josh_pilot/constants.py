from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURE_DIR = REPO_ROOT / "fixtures" / "josh_drs_group_2026"
ENV_FILE = REPO_ROOT / ".env.local"

EXEC_CSV = REPO_ROOT / "Drs Group US_Kivira Project 2026 - Physician_Group_Nationwide_Execs_.csv"
PCP_CSV = REPO_ROOT / "Drs Group US_Kivira Project 2026 - Kivira Target PCP List_ April 2026.csv"
READ_CSV = REPO_ROOT / "Drs Group US_Kivira Project 2026 - READ.csv"

WAVE1_RUNS_DIR = REPO_ROOT / "fixtures" / "wave1_runs"
ACO_WAVE2_CSV = REPO_ROOT / "fixtures" / "aco_attack" / "wave2_linkedin_2a.csv"

# Headerless Josh export column order
JOSH_ROW_FIELDS = (
    "contact_name",
    "title_raw",
    "title_bucket",
    "email",
    "col4_misc",
    "phone",
    "org_name",
    "org_type",
    "address",
    "city",
    "state",
    "size_metric",
)

NORMALIZED_EXTRA = ("col4_kind", "email_missing", "source")

PERSONA_PRIORITY = (
    "bh_quality_influencer",
    "clinical_champion",
    "operational_owner",
    "economic_buyer",
    "tech_gatekeeper",
)

SUBTIER_ORDER = ("1A", "1B", "1C", "2A", "2B", "2C", "3A", "3B", "3C", "UNK")

MASTER_FIELDS = (
    "contact_id",
    "contact_name",
    "title_raw",
    "title_bucket",
    "org_name",
    "org_type",
    "city",
    "state",
    "size_metric",
    "source",
    "subtier_code",
    "persona",
    "persona_confidence",
    "persona_rationale",
    "message_lane",
    "lane_rationale",
    "read_bucket",
    "pilot_score",
    "pilot_score_breakdown",
    "confidence_grade",
    "linkedin_profile_url",
    "linkedin_headline",
    "linkedin_position",
    "linkedin_about",
    "has_profile_photo",
    "profile_photo_url",
    "enrichment_source",
    "enrichment_confidence",
    "snippet_or_quote",
    "validation_flags",
    "notes",
)

HEYREACH_FIELDS = (
    "profileUrl",
    "firstName",
    "lastName",
    "companyName",
    "position",
    "persona",
    "subtier",
    "subtier_confidence",
    "signal",
    "source_query",
    "notes",
    "subtier_code",
    "message_lane",
)
