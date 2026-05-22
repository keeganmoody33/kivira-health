from tam_builder.josh_pilot.message_lane import classify_message_lane


def test_revenue_title_roi():
    lane, _ = classify_message_lane("Director of Revenue Cycle")
    assert lane == "roi"


def test_bh_clinical():
    lane, _ = classify_message_lane("Clinical Director of Behavioral Health")
    assert lane == "clinical"


def test_ops_practice_manager():
    lane, _ = classify_message_lane("Practice Manager")
    assert lane == "ops"


def test_bh_overrides_economic_persona():
    lane, _ = classify_message_lane(
        "CFO",
        persona="economic_buyer",
        about="leading collaborative care and BHI integration",
    )
    assert lane == "clinical"
