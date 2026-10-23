import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lead_capture_worker import extract_utm_from_payload, format_attribution_source
from seed_first_comments import TARGET_FIRST_COMMENTS, is_automod_safe_first_comment


def test_target_first_comments_are_automod_safe():
    assert len(TARGET_FIRST_COMMENTS) >= 4
    for item in TARGET_FIRST_COMMENTS:
        assert is_automod_safe_first_comment(item["comment"]), f"Failed automod check: {item['comment']}"


def test_automod_validator_blocks_spam_triggers():
    unsafe_samples = [
        "Tap @sacrednumberblueprint above to see your chart",
        "Check the link in our bio right now",
        "Visit our profile for a free reading",
        "Click our page to test your numbers",
    ]
    for s in unsafe_samples:
        assert not is_automod_safe_first_comment(s)


def test_tiktok_scripts_first_comments_are_automod_safe():
    scripts_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tiktok_scripts.json")
    with open(scripts_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    found_fc = 0
    cohort_c_ids = set()
    for s in data.get("scripts", []):
        fc = s.get("first_comment")
        if fc:
            found_fc += 1
            assert is_automod_safe_first_comment(fc), f"Script {s['id']} first_comment failed: {fc}"
        if s.get("cohort") == "Cohort C":
            cohort_c_ids.add(s["id"])
    assert found_fc >= 5
    assert {"short_01", "short_02", "short_03"}.issubset(cohort_c_ids)


def test_utm_and_cohort_attribution():
    # Default organic bio
    assert format_attribution_source({}) == "Organic Bio"
    assert format_attribution_source({"utm_source": "tiktok", "utm_medium": "bio"}) == "Organic Bio"

    # Cohort B organic
    assert format_attribution_source({"utm_source": "tiktok", "utm_medium": "bio", "cohort": "B"}) == "Organic Bio · Cohort B"
    assert format_attribution_source({"cohort": "broll_01"}) == "Cohort B"

    # TikTok Promote
    assert format_attribution_source({"utm_source": "tiktok", "utm_medium": "promote"}) == "TikTok Promote"
    assert format_attribution_source({"utm_source": "tiktok", "utm_medium": "promote", "cohort": "B"}) == "TikTok Promote (Cohort B)"
    assert format_attribution_source({"ttclid": "E.C.P.12345", "cohort": "broll_01"}) == "TikTok Promote (Cohort B)"


def test_extract_utm_from_payload():
    payload = {
        "event": "lead_capture",
        "utm_source": "tiktok",
        "cohort": "B",
        "profile": {
            "fullName": "Test User",
            "utm": {"utm_medium": "promote", "utm_campaign": "broll_01"},
        },
    }
    u = extract_utm_from_payload(payload)
    assert u["utm_source"] == "tiktok"
    assert u["utm_medium"] == "promote"
    assert u["utm_campaign"] == "broll_01"
    assert u["cohort"] == "B"
    assert format_attribution_source(u) == "TikTok Promote (Cohort B)"


if __name__ == "__main__":
    test_target_first_comments_are_automod_safe()
    test_automod_validator_blocks_spam_triggers()
    test_tiktok_scripts_first_comments_are_automod_safe()
    test_utm_and_cohort_attribution()
    test_extract_utm_from_payload()
    print("ALL 5 TEST SUITES PASSED!")

