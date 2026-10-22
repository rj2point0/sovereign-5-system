"""
=============================================================================
UNIT TESTS FOR TIKTOK COMMENT AUTO-RESPONDER
tests/test_comment_responder.py
Verifies:
1. Birthday parsing across diverse formats
2. Accurate Pythagorean Life Path & Vedic Moolank calculation
3. Life Path & Master Number detection
4. Intent classification across Buckets A, B, C, D, E
5. Mention of @sacrednumberblueprint and bio link in all replies
6. Deduplication store behavior
=============================================================================
"""

import os
import sys
import tempfile
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from comment_reply_engine import (
    CommentReplyEngine,
    parse_birthday_from_text,
    parse_number_from_text,
    calculate_life_path,
    calculate_vedic_moolank,
    NUMBER_ARCHETYPES,
    VEDIC_RULERS,
)
from tiktok_comment_responder import DeduplicationStore, TikTokCommentResponder


class TestBirthdayParsing(unittest.TestCase):
    def test_standard_and_informal_dates(self):
        cases = [
            ("08/19/1978", (1978, 8, 19)),
            ("March 14 1995", (1995, 3, 14)),
            ("11-22-1988", (1988, 11, 22)),
            ("July 4th 2000", (2000, 7, 4)),
            ("19th of August 1978", (1978, 8, 19)),
            ("1992-10-25", (1992, 10, 25)),
            ("25/12/1985", (1985, 12, 25)),
            ("8/19/78", (1978, 8, 19)),
            ("I was born on Oct 31, 1999!!", (1999, 10, 31)),
            ("born 03/15/1990 here", (1990, 3, 15)),
        ]
        for text, expected in cases:
            res = parse_birthday_from_text(text)
            self.assertIsNotNone(res, f"Failed to parse date from: {text}")
            y, mo, d, _ = res
            self.assertEqual((y, mo, d), expected, f"Parsed date mismatch for: {text}")

    def test_invalid_dates(self):
        invalid = [
            "Just a normal comment",
            "I love number 7",
            "192/400/9999",
            "May 99 2020",
        ]
        for text in invalid:
            res = parse_birthday_from_text(text)
            self.assertIsNone(res, f"Expected None for invalid text: {text}")


class TestNumerologyMath(unittest.TestCase):
    def test_adam_vega_sample(self):
        # 1978-08-19:
        # Year: 1+9+7+8 = 25 -> 7
        # Month: 8 -> 8
        # Day: 1+9 = 10 -> 1
        # Total: 7 + 8 + 1 = 16 -> 7
        lp_root, lp_disp = calculate_life_path(1978, 8, 19)
        self.assertEqual(lp_root, 7)
        self.assertEqual(lp_disp, "16/7")

        # Vedic Moolank: Day 19 -> 1+9 = 10 -> 1 (Surya / Sun)
        moolank, ruler = calculate_vedic_moolank(19)
        self.assertEqual(moolank, 1)
        self.assertIn("Surya", ruler["planet"])

    def test_sample_march_14_1995(self):
        # 1995-03-14:
        # Year: 1+9+9+5 = 24 -> 6
        # Month: 3
        # Day: 1+4 = 5
        # Total: 6 + 3 + 5 = 14 -> 5
        lp_root, lp_disp = calculate_life_path(1995, 3, 14)
        self.assertEqual(lp_root, 5)
        self.assertEqual(lp_disp, "14/5")

        # Vedic Moolank: Day 14 -> 1+4 = 5 (Budha / Mercury)
        moolank, ruler = calculate_vedic_moolank(14)
        self.assertEqual(moolank, 5)
        self.assertIn("Budha", ruler["planet"])

    def test_master_number_retention(self):
        # Test date that yields sum 11:
        # e.g. Year reduced 4, Month 3, Day 4 -> 4+3+4 = 11
        # 2002-03-04: 2002 -> 4; 03 -> 3; 04 -> 4 => total = 11
        lp_val, lp_disp = calculate_life_path(2002, 3, 4)
        self.assertEqual(lp_val, 11)
        self.assertEqual(lp_disp, "Master 11")


class TestNumberDetection(unittest.TestCase):
    def test_life_path_and_standalone_numbers(self):
        cases = [
            ("Life path 7", 7),
            ("I'm an 8", 8),
            ("I am a 4", 4),
            ("Master number 11", 11),
            ("33", 33),
            ("my number is 5", 5),
            ("mine is 6", 6),
            ("1", 1),
            ("22", 22),
            ("lp 9 here", 9),
            ("7!!", 7),
        ]
        for text, expected in cases:
            num = parse_number_from_text(text)
            self.assertEqual(num, expected, f"Failed to match number from: {text}")


class TestCommentClassification(unittest.TestCase):
    def setUp(self):
        self.engine = CommentReplyEngine(use_llm=False)

    def test_bucket_a_birthday(self):
        res = self.engine.generate_reply("I was born on 08/19/1978!", author="@user1")
        self.assertEqual(res["bucket"], "A_BIRTHDAY")
        self.assertIn("16/7", res["reply"])
        self.assertIn("@sacrednumberblueprint", res["reply"])
        for forbidden in ("click", "link", "bio", "free"):
            self.assertNotIn(forbidden, res["reply"].lower())

    def test_bucket_b_number(self):
        res = self.engine.generate_reply("I'm a Life Path 8", author="@user2")
        self.assertEqual(res["bucket"], "B_NUMBER")
        self.assertIn("8", res["reply"])
        self.assertIn("@sacrednumberblueprint", res["reply"])

    def test_bucket_c_link_request(self):
        for q in ["Where is the link?", "How do I calculate mine?", "Is it free or does it cost money?"]:
            res = self.engine.generate_reply(q, author="@user3")
            self.assertEqual(res["bucket"], "C_LINK_HOW")
            self.assertIn("@sacrednumberblueprint", res["reply"])

    def test_bucket_d_burnout_timing(self):
        for q in [
            "I have been working 80 hours a week and feel so burned out and exhausted",
            "Why do I feel so stuck and hitting a wall?",
            "My relationship timing feels like constant friction"
        ]:
            res = self.engine.generate_reply(q, author="@user4")
            self.assertEqual(res["bucket"], "D_BURNOUT_TIMING")
            self.assertIn("@sacrednumberblueprint", res["reply"])
            self.assertTrue("cycle" in res["reply"].lower() or "timing" in res["reply"].lower() or "window" in res["reply"].lower())

    def test_bucket_e_affirmation(self):
        for q in ["Claiming this energy ✨🙏", "So accurate!!", "Amen", "Wow following"]:
            res = self.engine.generate_reply(q, author="@user5")
            self.assertEqual(res["bucket"], "E_AFFIRMATION")
            self.assertIn("@sacrednumberblueprint", res["reply"])

    def test_variation_rotation(self):
        # Two identical comments with different seeds should yield different variations
        r1 = self.engine.get_deterministic_reply("E_AFFIRMATION", {}, seed=0)
        r2 = self.engine.get_deterministic_reply("E_AFFIRMATION", {}, seed=1)
        self.assertNotEqual(r1, r2, "Rotation failed: identical replies returned for different seeds")

    def test_spam_filter_safe_all_buckets_and_variations(self):
        """Ensure NO reply variation across all 5 buckets ever contains 'click', 'link', 'bio', or 'free'."""
        forbidden = ("click", "link", "bio", "free")
        sample_comments = [
            "08/19/1978",
            "March 14 1995",
            "Life path 5",
            "I'm an 8",
            "Master number 11",
            "Where is the link?",
            "I feel so burned out and exhausted",
            "Claiming this energy ✨",
        ]
        for comment in sample_comments:
            for seed in range(10):
                res = self.engine.generate_reply(comment, author=f"@u_{seed}", seed=seed)
                reply_lower = res["reply"].lower()
                self.assertIn("@sacrednumberblueprint", res["reply"])
                for word in forbidden:
                    self.assertNotIn(
                        word,
                        reply_lower,
                        f"Forbidden word '{word}' found in {res['bucket']} seed {seed}: {res['reply']}"
                    )


class TestDeduplicationStore(unittest.TestCase):
    def test_dedup_persistence_and_skip(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            store = DeduplicationStore(filepath=temp_path, sync_gdrive=False)
            self.assertFalse(store.has("test_comment_101"))

            store.record("test_comment_101", "@test_user", "March 14 1995", "A_BIRTHDAY", "Test reply")
            self.assertTrue(store.has("test_comment_101"))

            # Reload from disk into a fresh instance
            store2 = DeduplicationStore(filepath=temp_path, sync_gdrive=False)
            self.assertTrue(store2.has("test_comment_101"))
            self.assertEqual(store2.data["test_comment_101"]["author"], "@test_user")
            self.assertEqual(store2.data["test_comment_101"]["bucket"], "A_BIRTHDAY")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
