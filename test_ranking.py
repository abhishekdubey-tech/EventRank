"""
test_ranking.py - Comprehensive Unit Tests for EventRank Backend.
"""

from datetime import date
import os
import tempfile
import unittest

from ranking import (
    calculate_adjusted_rating,
    calculate_event_score,
    explain_recommendation,
    filter_events,
    load_events,
    rank_events,
)


class TestEventRankBackend(unittest.TestCase):
    def setUp(self):
        """Prepare sample events and a fixed reference date."""
        self.ref_date = date(2026, 10, 1)
        self.sample_events = [
            {
                "id": "EV001",
                "title": "AI Buildathon",
                "opportunity_type": "Hackathon",
                "domain": "AI/ML",
                "skill_level": "Beginner",
                "mode": "Online",
                "location": "Anywhere",
                "fee": 0.0,
                "team_min": 1,
                "team_max": 4,
                "registration_deadline": date(2027, 4, 15),
                "average_rating": 4.6,
                "review_count": 24,
                "learning_score": 90.0,
            },
            {
                "id": "EV002",
                "title": "CyberShield CTF",
                "opportunity_type": "Competition",
                "domain": "Cybersecurity",
                "skill_level": "Intermediate",
                "mode": "Offline",
                "location": "Bengaluru",
                "fee": 500.0,
                "team_min": 2,
                "team_max": 4,
                "registration_deadline": date(2027, 3, 20),
                "average_rating": 4.8,
                "review_count": 42,
                "learning_score": 95.0,
            },
            {
                "id": "EV_EXPIRED",
                "title": "Old Hack",
                "opportunity_type": "Hackathon",
                "domain": "AI/ML",
                "skill_level": "Beginner",
                "mode": "Online",
                "location": "Anywhere",
                "fee": 0.0,
                "team_min": 1,
                "team_max": 4,
                "registration_deadline": date(2025, 1, 1),
                "average_rating": 4.9,
                "review_count": 100,
                "learning_score": 99.0,
            },
        ]

    # --------------------------------------------------------------------------
    # CSV Loader & Validation Tests
    # --------------------------------------------------------------------------
    def test_load_events_valid_csv(self):
        csv_data = (
            "\ufeffid,title,opportunity_type,domain,skill_level,mode,location,fee,team_min,team_max,registration_deadline,average_rating,review_count,learning_score\n"
            "EV100,Test Hackathon,Hackathon,Python,Beginner,Online,Anywhere,0,1,3,2027-01-01,4.5,10,85\n"
        )
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
            tf.write(csv_data)
            tf_path = tf.name

        try:
            loaded = load_events(tf_path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["id"], "EV100")
            self.assertEqual(loaded[0]["opportunity_type"], "Hackathon")
            self.assertEqual(loaded[0]["registration_deadline"], date(2027, 1, 1))
            self.assertIsInstance(loaded[0]["fee"], float)
            self.assertIsInstance(loaded[0]["team_min"], int)
        finally:
            os.remove(tf_path)

    def test_load_events_missing_columns(self):
        csv_data = "id,title,domain\nEV100,Test,Python\n"
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
            tf.write(csv_data)
            tf_path = tf.name

        try:
            with self.assertRaises(ValueError) as ctx:
                load_events(tf_path)
            self.assertIn("Missing required columns", str(ctx.exception))
        finally:
            os.remove(tf_path)

    def test_load_events_invalid_numeric_values(self):
        csv_data = (
            "id,title,opportunity_type,domain,skill_level,mode,location,fee,team_min,team_max,registration_deadline,average_rating,review_count,learning_score\n"
            "EV100,Test,Hackathon,Python,Beginner,Online,Anywhere,INVALID_FEE,1,3,2027-01-01,4.5,10,85\n"
        )
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
            tf.write(csv_data)
            tf_path = tf.name

        try:
            with self.assertRaises(ValueError):
                load_events(tf_path)
        finally:
            os.remove(tf_path)

    def test_load_events_invalid_date(self):
        csv_data = (
            "id,title,opportunity_type,domain,skill_level,mode,location,fee,team_min,team_max,registration_deadline,average_rating,review_count,learning_score\n"
            "EV100,Test,Hackathon,Python,Beginner,Online,Anywhere,0,1,3,01-01-2027,4.5,10,85\n"
        )
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
            tf.write(csv_data)
            tf_path = tf.name

        try:
            with self.assertRaises(ValueError):
                load_events(tf_path)
        finally:
            os.remove(tf_path)

    # --------------------------------------------------------------------------
    # Hard Filter Tests
    # --------------------------------------------------------------------------
    def test_expired_deadline_filtered_out(self):
        filtered = filter_events(self.sample_events, {}, reference_date=self.ref_date)
        ids = [e["id"] for e in filtered]
        self.assertNotIn("EV_EXPIRED", ids)
        self.assertIn("EV001", ids)

    def test_opportunity_type_filter(self):
        prefs = {"opportunity_type": "Competition"}
        filtered = filter_events(self.sample_events, prefs, reference_date=self.ref_date)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], "EV002")

    def test_domain_and_skill_filter(self):
        prefs = {"domain": "AI/ML", "skill_level": "Beginner"}
        filtered = filter_events(self.sample_events, prefs, reference_date=self.ref_date)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], "EV001")

    def test_online_mode_and_anywhere_location(self):
        prefs = {"mode": "Online", "location": "Bengaluru"}
        filtered = filter_events(self.sample_events, prefs, reference_date=self.ref_date)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], "EV001")

    def test_offline_location_matching(self):
        prefs = {"mode": "Offline", "location": "Bengaluru"}
        filtered = filter_events(self.sample_events, prefs, reference_date=self.ref_date)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], "EV002")

        prefs_unmatched = {"mode": "Offline", "location": "Chennai"}
        self.assertEqual(len(filter_events(self.sample_events, prefs_unmatched, reference_date=self.ref_date)), 0)

    def test_budget_filter(self):
        prefs = {"max_budget": 100}
        filtered = filter_events(self.sample_events, prefs, reference_date=self.ref_date)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], "EV001")

    def test_team_size_filter(self):
        prefs_solo = {"team_size": 1}
        filtered = filter_events(self.sample_events, prefs_solo, reference_date=self.ref_date)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], "EV001")

        prefs_large = {"team_size": 5}
        self.assertEqual(len(filter_events(self.sample_events, prefs_large, reference_date=self.ref_date)), 0)

    # --------------------------------------------------------------------------
    # Adjusted Rating Tests
    # --------------------------------------------------------------------------
    def test_calculate_adjusted_rating_zero_reviews(self):
        dummy = {"average_rating": 5.0, "review_count": 0}
        adj = calculate_adjusted_rating(dummy, global_average=3.5, minimum_reviews=5)
        self.assertAlmostEqual(adj, 3.5, places=2)

    def test_calculate_adjusted_rating_high_reviews(self):
        dummy = {"average_rating": 4.8, "review_count": 100}
        adj = calculate_adjusted_rating(dummy, global_average=3.5, minimum_reviews=5)
        self.assertGreater(adj, 4.7)

    # --------------------------------------------------------------------------
    # Scoring Algorithm & Edge Cases
    # --------------------------------------------------------------------------
    def test_calculate_event_score_bounds_and_weights(self):
        score, breakdown = calculate_event_score(self.sample_events[0], {"domain": "AI/ML", "skill_level": "Beginner"})
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
        for val in breakdown.values():
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 100.0)

    def test_zero_budget_handling(self):
        score, breakdown = calculate_event_score(self.sample_events[0], {"max_budget": 0})
        self.assertEqual(breakdown["affordability_score"], 100.0)

    # --------------------------------------------------------------------------
    # Ranking & Explainability Tests
    # --------------------------------------------------------------------------
    def test_ranking_descending_order(self):
        results = rank_events(self.sample_events, {}, reference_date=self.ref_date)
        self.assertTrue(len(results) >= 2)
        self.assertGreaterEqual(results[0]["final_score"], results[1]["final_score"])

    def test_deterministic_tie_breaking(self):
        tied_events = [
            {
                "id": "EV_B",
                "title": "Hackathon B",
                "opportunity_type": "Hackathon",
                "domain": "AI/ML",
                "skill_level": "Beginner",
                "mode": "Online",
                "location": "Anywhere",
                "fee": 0,
                "team_min": 1,
                "team_max": 4,
                "registration_deadline": date(2027, 1, 1),
                "average_rating": 4.5,
                "review_count": 20,
                "learning_score": 80.0,
            },
            {
                "id": "EV_A",
                "title": "Hackathon A",
                "opportunity_type": "Hackathon",
                "domain": "AI/ML",
                "skill_level": "Beginner",
                "mode": "Online",
                "location": "Anywhere",
                "fee": 0,
                "team_min": 1,
                "team_max": 4,
                "registration_deadline": date(2027, 1, 1),
                "average_rating": 4.5,
                "review_count": 20,
                "learning_score": 80.0,
            },
        ]
        results = rank_events(tied_events, {}, reference_date=self.ref_date)
        self.assertEqual(results[0]["id"], "EV_A")
        self.assertEqual(results[1]["id"], "EV_B")

    def test_recommendation_reasons(self):
        ev = self.sample_events[0]
        prefs = {"domain": "AI/ML", "skill_level": "Beginner", "max_budget": 100}
        score, breakdown = calculate_event_score(ev, prefs)
        reasons = explain_recommendation(ev, prefs, breakdown)
        self.assertIsInstance(reasons, list)
        self.assertGreater(len(reasons), 0)
        self.assertTrue(any("AI/ML" in r for r in reasons))

    def test_empty_results(self):
        prefs = {"domain": "NonExistentDomain"}
        results = rank_events(self.sample_events, prefs, reference_date=self.ref_date)
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()