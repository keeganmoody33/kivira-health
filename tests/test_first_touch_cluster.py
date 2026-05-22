from tam_builder.josh_pilot.first_touch_cluster import (
    classify_first_touch_cluster,
    format_address,
    is_physician_title,
)


def test_dr_address():
    assert format_address("Jeremy", "Wigginton", "MD", "CMO") == "Dr. Wigginton"
    assert format_address("Chris", "Oltmans", "Chief Population Health Officer", "") == "Chris"


def test_cluster_provider():
    c, _ = classify_first_touch_cluster(
        "Medical Director",
        persona="clinical_champion",
        subtier="1A",
    )
    assert c == "A"


def test_cluster_vbc_subtier():
    c, _ = classify_first_touch_cluster(
        "Sr Dir Quality & Risk Adjustment",
        persona="economic_buyer",
        subtier="2A",
    )
    assert c == "B"


def test_cluster_partnership():
    c, _ = classify_first_touch_cluster(
        "Director of Growth",
        persona="unknown",
        subtier="2B",
    )
    assert c == "D"


def test_cluster_care_mgmt():
    c, _ = classify_first_touch_cluster(
        "VP Care Management",
        persona="operational_owner",
        subtier="2C",
    )
    assert c == "C"
