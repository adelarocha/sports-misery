#!/usr/bin/env python3
"""
Quick audit: checks playoff counts for known teams against expected ground truth.
Run AFTER regenerating data with fetch_data.py.

Usage:
    python3 audit_playoffs.py
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# Known ground-truth checks: (league, team_code, since_year, expected_min_playoffs)
# These are conservative lower bounds — the real numbers should be >= these.
CHECKS = [
    # NBA
    ("NBA", "LAL", 1990, 20),   # Lakers: near-perennial playoff team
    ("NBA", "CHI", 1990, 10),   # Bulls: Jordan 6 titles + 2 more appearances after
    ("NBA", "BOS", 1990, 14),   # Celtics: strong era
    ("NBA", "SAS", 1990, 20),   # Spurs: elite consistency
    ("NBA", "NYK", 1990, 12),   # Knicks: at least a dozen in 35 years
    ("NBA", "MIA", 1990, 12),   # Heat: LeBron era + Alonzo etc.
    # MLB
    ("MLB", "NYY", 1990, 20),   # Yankees: regular playoff contender
    ("MLB", "BOS", 1990, 10),   # Red Sox: multiple WS wins
    ("MLB", "ATL", 1990, 15),   # Braves: dynasty in the 90s
    ("MLB", "LAD", 1990, 12),   # Dodgers: consistent contender
    # NHL
    ("NHL", "BOS", 1990, 20),   # Bruins: perennial playoff team
    ("NHL", "DET", 1990, 20),   # Red Wings: 25 consecutive playoff years 1991-2016
    ("NHL", "TOR", 1990, 12),   # Maple Leafs: despite drought, still made playoffs often
    ("NHL", "PIT", 1990, 18),   # Penguins: elite era
    ("NHL", "PHI", 1990, 18),   # Flyers: consistent
]

def main():
    print("=== Playoff Audit ===\n")
    all_pass = True

    for league, team, since, min_expected in CHECKS:
        fpath = DATA_DIR / f"{league.lower()}.json"
        if not fpath.exists():
            print(f"  MISSING: {league}.json — run fetch_data.py first")
            all_pass = False
            continue

        with open(fpath) as f:
            data = json.load(f)

        team_data = data.get("teams", {}).get(team)
        if not team_data:
            print(f"  MISSING TEAM: {league}:{team}")
            all_pass = False
            continue

        playoff_years = [
            int(yr) for yr, s in team_data["seasons"].items()
            if s and s.get("playoffs") and int(yr) >= since
        ]
        playoff_years.sort()
        count = len(playoff_years)
        status = "✓ PASS" if count >= min_expected else "✗ FAIL"
        if count < min_expected:
            all_pass = False

        print(f"  {status}  {league} {team} since {since}: {count} playoff seasons (expected >={min_expected})")
        if count < min_expected:
            print(f"         Years found: {playoff_years}")

    print()
    if all_pass:
        print("All checks passed! Data looks good.")
    else:
        print("Some checks FAILED — playoff data still incomplete. Check fetch_data.py output for errors.")

if __name__ == "__main__":
    main()
