import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lead_capture_worker as w


class TestLeadCaptureWorkerUpgrades(unittest.TestCase):
    def test_cowen_math_and_system_count_consistency(self):
        calc = w.calculate_5_systems("Cowen Airo Celestin Vega", "07/07/2017")
        self.assertEqual(calc["dob"], "2017-07-07")
        self.assertEqual(calc["top_3_overlap_numbers"], "7, 9, 6")
        self.assertEqual(calc["life_path"], "15/6")
        # 99 reduces to 18/9 instead of 99/9
        self.assertEqual(calc["expression"], "18/9")
        # Clean middle-dot Vedic formatting without double closing parens ))
        self.assertEqual(calc["vedic_moolank"], "7 · Ketu (South Node)")
        self.assertNotIn("))", calc["vedic_moolank"])

        anchors = {a["number"]: a for a in calc["anchors"]}
        # Anchor #7: 4x across 4 systems
        self.assertEqual(anchors[7]["count"], 4)
        self.assertEqual(len(anchors[7]["systems"]), 4)
        # Anchor #9: 3x across 3 systems (Pythagorean, Chaldean, Vedic)
        self.assertEqual(anchors[9]["count"], 3)
        self.assertEqual(anchors[9]["systems"], ["Pythagorean", "Chaldean", "Vedic"])
        # Anchor #6: 2x across 2 systems (Pythagorean, Vedic)
        self.assertEqual(anchors[6]["count"], 2)
        self.assertEqual(anchors[6]["systems"], ["Pythagorean", "Vedic"])

    def test_adam_founder_math_preserved(self):
        calc = w.calculate_5_systems("Adam Vega", "1978-08-19")
        self.assertEqual(calc["top_3_overlap_numbers"], "7, 8, 4")
        for a in calc["anchors"]:
            self.assertLessEqual(len(a["systems"]), a["count"])

    def test_cross_browser_teaser_deep_link(self):
        url = w.build_teaser_deep_link("Cowen Airo Celestin Vega", "2017-07-07", "getshoes7@gmail.com")
        self.assertEqual(
            url,
            "https://blueprint.megavegaventures.com/?view=teaser&name=Cowen+Airo+Celestin+Vega&dob=2017-07-07&email=getshoes7%40gmail.com",
        )

    def test_email_1_conversion_elements(self):
        self.assertEqual(w.SENDER_DISPLAY, "Sacred Number Blueprint <adamvega@megavegaventures.com>")
        calc = w.calculate_5_systems("Cowen Airo Celestin Vega", "2017-07-07")
        lead = {
            "name": "Cowen Airo Celestin Vega",
            "dob": "2017-07-07",
            "email": "getshoes7@gmail.com",
            "calc": calc,
        }
        subj, plain, html_body = w.build_luxury_followup_email(lead)
        self.assertIn("Master Overlap #7 (The Mystic Strategist)", subj)
        self.assertIn("SINGLE-SYSTEM FRICTION ALERT", html_body)
        self.assertIn("🔒 Locked in Full 20-Page Dossier", html_body)
        self.assertIn("WHAT’S INSIDE YOUR 20-PAGE SOVEREIGN DOSSIER", html_body)
        self.assertIn("UNLOCK MY FULL 20-PAGE SOVEREIGN DOSSIER ($37)", html_body)
        self.assertIn(
            "https://blueprint.megavegaventures.com/?view=teaser&name=Cowen+Airo+Celestin+Vega&dob=2017-07-07&email=getshoes7%40gmail.com",
            html_body,
        )
        self.assertIn("3× across 3 systems: Pythagorean, Chaldean, Vedic", html_body)
        self.assertIn("2× across 2 systems: Pythagorean, Vedic", html_body)

    def test_email_2_and_email_3_sequence_builders(self):
        calc = w.calculate_5_systems("Cowen Airo Celestin Vega", "2017-07-07")
        lead = {
            "name": "Cowen Airo Celestin Vega",
            "dob": "2017-07-07",
            "email": "getshoes7@gmail.com",
            "calc": calc,
        }
        s2, _, h2 = w.build_followup_email_2_loshu(lead)
        self.assertEqual(s2, "✦ Cowen, the missing numbers in your Chinese Lo Shu Grid...")
        self.assertIn("Anchor #9 · The Sage-Warrior", h2)

        s3, _, h3 = w.build_followup_email_3_cycles(lead)
        self.assertEqual(s3, "⏳ Cowen, your current 52-Day Rosicrucian Cycle is active")
        self.assertIn("ROSICRUCIAN 52-DAY BIORHYTHM ALERT", h3)

    def test_partner_dob_personalization_in_email_1(self):
        calc = w.calculate_5_systems("Sarah Jenkins", "1990-07-16")
        lead = {
            "name": "Sarah Jenkins",
            "dob": "1990-07-16",
            "email": "sarah.real.test@gmail.com",
            "partner_dob": "1988-10-26",
            "calc": calc,
        }
        subj, plain, html_body = w.build_luxury_followup_email(lead)
        self.assertIn("PARTNER / CRUSH COMPATIBILITY SNAPSHOT", html_body)
        self.assertIn("1988-10-26", html_body)
        self.assertIn("8 · Shani (Saturn)", html_body)
        self.assertIn("PARTNER / CRUSH COMPATIBILITY SNAPSHOT", plain)

    def test_viral_outlier_finder_sqlite_and_scripts(self):
        import sqlite3
        import viral_outlier_finder as vof

        self.assertTrue(os.path.exists(vof.DB_PATH))
        conn = sqlite3.connect(vof.DB_PATH)
        cur = conn.cursor()
        acc_count = cur.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        post_count = cur.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        outlier_count = cur.execute("SELECT COUNT(*) FROM posts WHERE outlier_ratio >= 3.0").fetchone()[0]
        conn.close()
        self.assertGreaterEqual(acc_count, 6)
        self.assertGreaterEqual(post_count, 20)
        self.assertGreaterEqual(outlier_count, 10)
        for sc in vof.READY_SCRIPT_CONCEPTS:
            fk = vof.flesch_kincaid_grade(f"{sc['hook_line']} {sc['but_therefore_twist']} {sc['cta_line']}")
            self.assertLessEqual(fk, 5.5)

    def test_demo_preview_and_love_mini_tier_support(self):
        calc = w.calculate_5_systems("Chloe", "1998-07-16")
        lead = {
            "name": "Chloe",
            "dob": "1998-07-16",
            "email": "chloe.real@gmail.com",
            "partner_dob": "1996-04-13",
            "calc": calc,
        }
        subj, plain, html_body = w.build_luxury_followup_email(lead)
        self.assertIn("$17 Partner Synastry", html_body)
        self.assertIn("$17 PARTNER SYNASTRY MINI-READ", plain)


if __name__ == "__main__":
    unittest.main()
