# EventRank: Discover What's Worth Attending (Backend MVP)

An explainable, heuristic-based hackathon recommendation engine built for college students.

---

## 1. Dataset Status
> **Notice:** The dataset in `events.csv` is **completely synthetic and fictional**, created exclusively for testing and demonstrating recommendation algorithms. Event titles, ratings, and locations do not reflect real hackathons or real participant reviews.

---

## 2. Project Architecture & Components

The engine is contained in `ranking.py` and structured as pure, stateless functions:

1. **`load_events(csv_path)`**
   - Validates column schema and handles UTF-8 BOM encoding.
   - Converts strings to `float`, `int`, and `datetime.date`.
   - Rejects corrupted or missing values with descriptive errors.

2. **`filter_events(events, preferences, reference_date=None)`**
   - Applies hard constraints (Domain, Skill Level, Mode, Budget, Location, Team Size, and Registration Deadline).
   - Online events are accessible regardless of location filter.
   - Any unspecified filter is treated as neutral (no events excluded).

3. **`calculate_adjusted_rating(event, global_average=3.5, minimum_reviews=5)`**
   - Implements Bayesian smoothing:  
     $$\text{Adjusted Rating} = \frac{v \cdot R + m \cdot C}{v + m}$$
   - Prevents unproven hackathons with 1 review of 5.0★ from outranking proven events with dozens of 4.7★ reviews.

4. **`calculate_event_score(event, preferences)`**
   - Computes transparent composite scores (0–100):
     - **Bayesian Rating (35%)**: Scaled linearly from 1.0–5.0 to 0–100.
     - **Preference Match (25%)**: 50 pts domain match + 50 pts skill match.
     - **Learning Score (25%)**: Practical learning & career value score.
     - **Review Confidence (10%)**: Asymptotic heuristic reaching 100% confidence at 30 reviews.
     - **Affordability (5%)**: Ratio of entry fee against user's maximum budget.

5. **`explain_recommendation(event, preferences, score_details)`**
   - Generates truthful, data-backed reasons explaining why an event was recommended without claiming reviews are "verified" or "guaranteed".

6. **`rank_events(events, preferences, reference_date=None)`**
   - Orchestrates filtering, scoring, and explaining.
   - Applies deterministic tie-breaking: `(-final_score, -adjusted_rating, -review_count, id)`.

---

## 3. Assumptions and Limitations
- **Heuristic Ranking**: This is a transparent weighted scoring system, **not** an AI/ML model trained on historical attendance data.
- **In-Memory Operation**: The backend operates on Python dictionaries loaded in memory, suitable for hackathon MVP workloads (< 50,000 records).
- **Stateless**: Functions maintain no mutable global state, ensuring thread safety and easy web framework integration.