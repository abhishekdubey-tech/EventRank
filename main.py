"""
main.py - Command-Line Interface and Demonstration for EventRank.
"""

from datetime import date
from ranking import load_events, rank_events


def print_divider(char="=", length=80):
    print(char * length)


def display_results(results, title):
    print_divider()
    print(f" {title.upper()} (Found: {len(results)})")
    print_divider()

    if not results:
        print("  [i] No hackathons matched your constraints. Try broadening your criteria.")
        print_divider()
        return

    for idx, item in enumerate(results, start=1):
        print(f"\n#{idx} [{item['id']}] {item['title']}")
        print(f"    Domain: {item['domain']} | Level: {item['skill_level']} | Mode: {item['mode']} ({item['location']})")
        print(f"    Fee: ₹{item['fee']} | Deadline: {item['registration_deadline']}")
        print(f"    Raw Rating: {item['average_rating']}★ ({item['review_count']} reviews) -> Adjusted Trust Rating: {item['adjusted_rating']}★")
        print(f"    -> FINAL SCORE: {item['final_score']} / 100.00")
        
        bd = item["score_breakdown"]
        print("    Component Breakdown:")
        print(f"       * Bayesian Rating Score (35%):  {bd['rating_score']}/100")
        print(f"       * Preference Match (25%):       {bd['preference_score']}/100")
        print(f"       * Learning Score (25%):         {bd['learning_score']}/100")
        print(f"       * Review Confidence (10%):      {bd['review_confidence']}/100")
        print(f"       * Affordability Score (5%):     {bd['affordability_score']}/100")
        
        print("    Why Recommended:")
        for reason in item["reasons"]:
            print(f"       - {reason}")
    print("\n" + "=" * 80)


def main():
    csv_file = "events.csv"
    print(f"\n[+] Loading hackathon dataset from '{csv_file}'...")
    
    try:
        events = load_events(csv_file)
        print(f"[+] Loaded {len(events)} events successfully.")
    except Exception as exc:
        print(f"[!] Failed to load events: {exc}")
        return

    # Fixed demo reference date so demo output remains deterministic across all future runs
    demo_today = date(2026, 10, 1)

    # --------------------------------------------------------------------------
    # Scenario 1: Realistic Student Search
    # --------------------------------------------------------------------------
    student_preferences = {
        "domain": "AI/ML",
        "skill_level": "Beginner",
        "mode": "Online",
        "max_budget": 500,
        "team_size": 2,
    }

    print("\n[+] SCENARIO 1: College Student Preferences:")
    for k, v in student_preferences.items():
        print(f"    - {k}: {v}")

    ranked_recommendations = rank_events(events, student_preferences, reference_date=demo_today)
    top_5 = ranked_recommendations[:5]
    display_results(top_5, "Top Recommendations for Scenario 1")

    # --------------------------------------------------------------------------
    # Scenario 2: Overly Restrictive Constraints (Testing Empty State Handling)
    # --------------------------------------------------------------------------
    impossible_preferences = {
        "domain": "Cybersecurity",
        "skill_level": "Advanced",
        "mode": "Offline",
        "location": "Jaipur",  # No events in Jaipur
        "max_budget": 0,
        "team_size": 8,         # Exceeds max team size
    }

    print("\n[+] SCENARIO 2: Overly Restrictive / Non-matching Preferences:")
    for k, v in impossible_preferences.items():
        print(f"    - {k}: {v}")

    empty_recommendations = rank_events(events, impossible_preferences, reference_date=demo_today)
    display_results(empty_recommendations, "Scenario 2 (Empty Results Test)")


if __name__ == "__main__":
    main()