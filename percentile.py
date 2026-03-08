"""
Sports Misery Calculator - Percentile Rankings
Pre-computes reference scores for all teams across common fan start years.
Places users in the distribution: "more miserable than X% of fans."

v1: Pre-computed reference population (all teams, 5 start-year cohorts).
Future: Replace with actual user submission data as responses accumulate.
"""

import json
import os
from pathlib import Path
from scoring import calculate_team_misery

DATA_DIR = Path(__file__).parent / "data"
CACHE_FILE = Path(__file__).parent / "data" / "percentile_cache.json"

# Fan start cohorts used for reference population
REFERENCE_START_YEARS = [1970, 1980, 1990, 2000, 2010]

_cache = None


def build_reference_population(league_data: dict) -> list:
    """
    Compute single-team misery scores for every team x every start year.
    Returns a flat list of scores used as the reference distribution.
    """
    scores = []
    for league_key, data in league_data.items():
        for team_id, team_data in data["teams"].items():
            for start_year in REFERENCE_START_YEARS:
                result = calculate_team_misery(team_data, start_year)
                if "error" not in result and result["seasons_watched"] >= 5:
                    scores.append({
                        "team_id": team_id,
                        "league": league_key,
                        "fan_start": start_year,
                        "total_score": result["total_score"],
                        "seasons_watched": result["seasons_watched"],
                    })
    return sorted(scores, key=lambda x: x["total_score"])


def load_or_build_cache(league_data: dict) -> list:
    """Load pre-computed reference population from cache, or build it."""
    global _cache
    if _cache is not None:
        return _cache

    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            _cache = json.load(f)
        return _cache

    print("Building percentile reference population...")
    _cache = build_reference_population(league_data)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(_cache, f)
    print(f"  {len(_cache)} reference data points computed.")

    return _cache


def get_percentile(user_score: float, league_data: dict,
                   fan_start: int, num_teams: int) -> dict:
    """
    Return what percentile the user's score falls in.
    Compares against single-team reference fans from a similar start-year cohort.

    Returns:
        percentile: 0-100 (100 = most miserable)
        comparison_text: human-readable string
        cohort_size: how many reference fans were compared
        cohort_median: median score in the cohort
    """
    reference = load_or_build_cache(league_data)

    # Find the closest reference start year
    closest_start = min(REFERENCE_START_YEARS, key=lambda y: abs(y - fan_start))

    # Filter to comparable cohort (same start year ±5 years, single-team scores)
    cohort = [
        r["total_score"] for r in reference
        if abs(r["fan_start"] - closest_start) <= 5
    ]

    if not cohort:
        return {"percentile": 50, "comparison_text": "Not enough data", "cohort_size": 0}

    # Scale user score by number of teams (reference is single-team)
    # Compare per-team average to keep it apples-to-apples
    comparable_score = user_score / max(num_teams, 1)

    cohort_sorted = sorted(cohort)
    n = len(cohort_sorted)

    # Count how many reference fans score BELOW the user (i.e. less miserable)
    below = sum(1 for s in cohort_sorted if s < comparable_score)
    percentile = round((below / n) * 100)

    # Median of cohort
    median = cohort_sorted[n // 2]

    # Build comparison text
    if percentile >= 95:
        comparison = f"more miserable than {percentile}% of fans — truly elite suffering"
    elif percentile >= 75:
        comparison = f"more miserable than {percentile}% of fans"
    elif percentile >= 50:
        comparison = f"more miserable than {percentile}% of fans"
    elif percentile >= 25:
        comparison = f"less miserable than {100 - percentile}% of fans — you've had it pretty good"
    else:
        comparison = f"less miserable than {100 - percentile}% of fans — genuinely lucky"

    return {
        "percentile": percentile,
        "comparison_text": comparison,
        "cohort_size": n,
        "cohort_median_score": round(median, 1),
        "note": "v1: based on pre-computed reference population. Will update with real user data.",
    }


def invalidate_cache():
    """Force rebuild of reference population on next call."""
    global _cache
    _cache = None
    if CACHE_FILE.exists():
        os.remove(CACHE_FILE)
