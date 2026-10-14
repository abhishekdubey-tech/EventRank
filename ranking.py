"""
ranking.py - Core Backend Business Logic for EventRank.
Supports Hackathons, Internships, Competitions, and Webinars/Seminars.
"""

from __future__ import annotations

import csv
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

# ==============================================================================
# WEIGHT CONFIGURATION (Transparent Heuristic Model - Sums to 1.00)
# ==============================================================================
WEIGHT_ADJUSTED_RATING: float = 0.35      # Quality (Bayesian trust rating)
WEIGHT_PREFERENCE_MATCH: float = 0.25     # User alignment (domain & skill)
WEIGHT_LEARNING_VALUE: float = 0.25       # Pedagogical / career value
WEIGHT_REVIEW_CONFIDENCE: float = 0.10    # Confidence based on volume
WEIGHT_AFFORDABILITY: float = 0.05        # Budget friendliness

DEFAULT_GLOBAL_AVERAGE_RATING: float = 3.5
DEFAULT_MINIMUM_REVIEWS: float = 5.0

REQUIRED_CSV_COLUMNS: Tuple[str, ...] = (
    "id",
    "title",
    "opportunity_type",
    "domain",
    "skill_level",
    "mode",
    "location",
    "fee",
    "team_min",
    "team_max",
    "registration_deadline",
    "average_rating",
    "review_count",
    "learning_score",
)

VALID_MODES: Tuple[str, ...] = ("Online", "Offline")
VALID_SKILL_LEVELS: Tuple[str, ...] = ("Beginner", "Intermediate", "Advanced")


def load_events(csv_path: str) -> List[Dict[str, Any]]:
    """Load and validate opportunities from a CSV file."""
    events: List[Dict[str, Any]] = []

    with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"CSV file '{csv_path}' is empty or contains no valid header.")

        cleaned_headers = [col.strip() for col in reader.fieldnames if col]
        missing_cols = [col for col in REQUIRED_CSV_COLUMNS if col not in cleaned_headers]
        if missing_cols:
            raise ValueError(
                f"CSV schema mismatch. Missing required columns: {', '.join(missing_cols)}"
            )

        for line_num, raw_row in enumerate(reader, start=2):
            row = {
                k.strip(): (v.strip() if v is not None else "")
                for k, v in raw_row.items()
                if k is not None
            }

            for col in REQUIRED_CSV_COLUMNS:
                if col not in row or row[col] == "":
                    raise ValueError(
                        f"Line {line_num}: Missing required field '{col}' for ID '{row.get('id', 'UNKNOWN')}'."
                    )

            event_id = row["id"]
            title = row["title"]
            opportunity_type = row["opportunity_type"]
            domain = row["domain"]
            skill_level = row["skill_level"]
            mode = row["mode"]
            location = row["location"]

            if mode not in VALID_MODES:
                raise ValueError(f"Line {line_num} (ID: {event_id}): Invalid mode '{mode}'.")

            if skill_level not in VALID_SKILL_LEVELS:
                raise ValueError(f"Line {line_num} (ID: {event_id}): Invalid skill_level '{skill_level}'.")

            try:
                fee = float(row["fee"])
                if fee < 0:
                    raise ValueError("Fee cannot be negative.")
            except ValueError as err:
                raise ValueError(f"Line {line_num} (ID: {event_id}): Invalid fee. {err}") from err

            try:
                team_min = int(row["team_min"])
                team_max = int(row["team_max"])
                if team_min <= 0 or team_max < team_min:
                    raise ValueError(f"Invalid team size range [{team_min}, {team_max}].")
            except ValueError as err:
                raise ValueError(f"Line {line_num} (ID: {event_id}): Invalid team bounds. {err}") from err

            try:
                reg_deadline = datetime.strptime(row["registration_deadline"], "%Y-%m-%d").date()
            except ValueError as err:
                raise ValueError(f"Line {line_num} (ID: {event_id}): Invalid date format.") from err

            try:
                avg_rating = float(row["average_rating"])
                if not (1.0 <= avg_rating <= 5.0):
                    raise ValueError("Rating out of bounds.")
            except ValueError as err:
                raise ValueError(f"Line {line_num} (ID: {event_id}): Invalid average_rating. {err}") from err

            try:
                review_count = int(row["review_count"])
                if review_count < 0:
                    raise ValueError("Review count negative.")
            except ValueError as err:
                raise ValueError(f"Line {line_num} (ID: {event_id}): Invalid review_count. {err}") from err

            try:
                learning_score = float(row["learning_score"])
                if not (0.0 <= learning_score <= 100.0):
                    raise ValueError("Learning score out of range.")
            except ValueError as err:
                raise ValueError(f"Line {line_num} (ID: {event_id}): Invalid learning_score. {err}") from err

            events.append({
                "id": event_id,
                "title": title,
                "opportunity_type": opportunity_type,
                "domain": domain,
                "skill_level": skill_level,
                "mode": mode,
                "location": location,
                "fee": fee,
                "team_min": team_min,
                "team_max": team_max,
                "registration_deadline": reg_deadline,
                "average_rating": avg_rating,
                "review_count": review_count,
                "learning_score": learning_score,
            })

    return events


def filter_events(
    events: List[Dict[str, Any]],
    preferences: Dict[str, Any],
    reference_date: Optional[date] = None,
) -> List[Dict[str, Any]]:
    """Filter opportunities by applying hard constraints."""
    if reference_date is None:
        pref_date = preferences.get("current_date")
        if isinstance(pref_date, date):
            reference_date = pref_date
        elif isinstance(pref_date, str):
            reference_date = datetime.strptime(pref_date, "%Y-%m-%d").date()
        else:
            reference_date = date.today()

    filtered: List[Dict[str, Any]] = []

    pref_type = preferences.get("opportunity_type")
    pref_domain = preferences.get("domain")
    pref_skill = preferences.get("skill_level")
    pref_mode = preferences.get("mode")
    pref_budget = preferences.get("max_budget")
    pref_location = preferences.get("location")
    pref_team_size = preferences.get("team_size")

    for event in events:
        # 1. Deadline filter
        if event["registration_deadline"] < reference_date:
            continue

        # 2. Opportunity Type filter (Hackathon, Internship, Competition, Webinar)
        if pref_type and event["opportunity_type"].strip().lower() != pref_type.strip().lower():
            continue

        # 3. Domain filter
        if pref_domain and event["domain"].strip().lower() != pref_domain.strip().lower():
            continue

        # 4. Skill level filter
        if pref_skill and event["skill_level"].strip().lower() != pref_skill.strip().lower():
            continue

        # 5. Mode filter
        if pref_mode and event["mode"].strip().lower() != pref_mode.strip().lower():
            continue

        # 6. Budget filter
        if pref_budget is not None and float(pref_budget) >= 0:
            if event["fee"] > float(pref_budget):
                continue

        # 7. Team Size filter
        if pref_team_size is not None:
            ts = int(pref_team_size)
            if not (event["team_min"] <= ts <= event["team_max"]):
                continue

        # 8. Location filter (Offline only)
        if pref_location and event["mode"].lower() == "offline":
            if event["location"].strip().lower() != pref_location.strip().lower():
                continue

        filtered.append(event)

    return filtered


def calculate_adjusted_rating(
    event: Dict[str, Any],
    global_average: float = DEFAULT_GLOBAL_AVERAGE_RATING,
    minimum_reviews: float = DEFAULT_MINIMUM_REVIEWS,
) -> float:
    """Calculate Bayesian adjusted rating."""
    v = float(event.get("review_count", 0))
    r = float(event.get("average_rating", global_average))
    m = float(minimum_reviews)
    c = float(global_average)

    if (v + m) == 0:
        return c

    return round((v * r + m * c) / (v + m), 4)


def calculate_event_score(
    event: Dict[str, Any],
    preferences: Dict[str, Any],
) -> Tuple[float, Dict[str, float]]:
    """Compute score from 0 to 100 with component breakdown."""
    adj_rating = calculate_adjusted_rating(event)
    q_score = max(0.0, min(100.0, ((adj_rating - 1.0) / 4.0) * 100.0))

    domain_pref = preferences.get("domain")
    skill_pref = preferences.get("skill_level")

    domain_score = 50.0
    if domain_pref:
        domain_score = 50.0 if event["domain"].strip().lower() == domain_pref.strip().lower() else 0.0

    skill_score = 50.0
    if skill_pref:
        skill_score = 50.0 if event["skill_level"].strip().lower() == skill_pref.strip().lower() else 0.0

    p_score = domain_score + skill_score
    l_score = max(0.0, min(100.0, float(event.get("learning_score", 0.0))))

    rev_count = max(0, int(event.get("review_count", 0)))
    c_score = min(100.0, (rev_count / 30.0) * 100.0)

    fee = float(event.get("fee", 0.0))
    pref_budget = preferences.get("max_budget")

    if fee == 0.0:
        a_score = 100.0
    elif pref_budget is not None and float(pref_budget) > 0:
        ratio = min(1.0, fee / float(pref_budget))
        a_score = max(0.0, 100.0 - (ratio * 50.0))
    elif pref_budget is not None and float(pref_budget) == 0.0:
        a_score = 100.0 if fee == 0.0 else 0.0
    else:
        a_score = max(0.0, 100.0 - (fee / 20.0))

    final_score = (
        (WEIGHT_ADJUSTED_RATING * q_score)
        + (WEIGHT_PREFERENCE_MATCH * p_score)
        + (WEIGHT_LEARNING_VALUE * l_score)
        + (WEIGHT_REVIEW_CONFIDENCE * c_score)
        + (WEIGHT_AFFORDABILITY * a_score)
    )

    breakdown = {
        "rating_score": round(q_score, 2),
        "preference_score": round(p_score, 2),
        "learning_score": round(l_score, 2),
        "review_confidence": round(c_score, 2),
        "affordability_score": round(a_score, 2),
    }

    return round(final_score, 2), breakdown


def explain_recommendation(
    event: Dict[str, Any],
    preferences: Dict[str, Any],
    score_details: Dict[str, float],
) -> List[str]:
    """Generate human-readable reasons for recommendation."""
    reasons: List[str] = []

    # Opportunity category
    reasons.append(f"Format: {event['opportunity_type']}")

    if preferences.get("domain") and event["domain"].strip().lower() == preferences["domain"].strip().lower():
        reasons.append(f"Matches domain: {event['domain']}")

    if preferences.get("skill_level") and event["skill_level"].strip().lower() == preferences["skill_level"].strip().lower():
        reasons.append(f"Targets your level: {event['skill_level']}")

    if event["learning_score"] >= 85.0:
        reasons.append(f"High career/practical value rating ({int(event['learning_score'])}/100)")

    adj_rating = calculate_adjusted_rating(event)
    if adj_rating >= 4.2:
        reasons.append(f"High participant feedback (Bayesian: {adj_rating:.2f}/5.0)")

    if event["review_count"] >= 25:
        reasons.append(f"Reliable review sample ({event['review_count']} reviews)")

    if event["fee"] == 0:
        reasons.append("Zero entry / registration fee")
    elif preferences.get("max_budget") is not None and event["fee"] <= preferences["max_budget"]:
        reasons.append(f"Fee (₹{int(event['fee'])}) fits within your budget")

    if event["mode"].lower() == "online":
        reasons.append("Online format accessible anywhere")
    elif preferences.get("location") and event["location"].strip().lower() == preferences["location"].strip().lower():
        reasons.append(f"Hosted in {event['location']}")

    return reasons


def rank_events(
    events: List[Dict[str, Any]],
    preferences: Dict[str, Any],
    reference_date: Optional[date] = None,
) -> List[Dict[str, Any]]:
    """Filters, scores, and deterministically ranks opportunities."""
    eligible = filter_events(events, preferences, reference_date=reference_date)
    if not eligible:
        return []

    ranked: List[Dict[str, Any]] = []

    for event in eligible:
        final_score, breakdown = calculate_event_score(event, preferences)
        adj_rating = calculate_adjusted_rating(event)
        reasons = explain_recommendation(event, preferences, breakdown)

        ranked.append({
            "id": event["id"],
            "title": event["title"],
            "opportunity_type": event["opportunity_type"],
            "domain": event["domain"],
            "skill_level": event["skill_level"],
            "mode": event["mode"],
            "location": event["location"],
            "fee": float(event["fee"]),
            "registration_deadline": event["registration_deadline"].strftime("%Y-%m-%d"),
            "average_rating": float(event["average_rating"]),
            "review_count": int(event["review_count"]),
            "adjusted_rating": round(adj_rating, 2),
            "final_score": final_score,
            "score_breakdown": breakdown,
            "reasons": reasons,
        })

    ranked.sort(
        key=lambda x: (
            -x["final_score"],
            -x["adjusted_rating"],
            -x["review_count"],
            x["id"],
        )
    )

    return ranked