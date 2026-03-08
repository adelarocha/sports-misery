"""
Sports Misery Calculator - Scoring Engine v3
============================================
Atomic unit: season misery score (signed float).
Total = sum of all season scores across fan lifetime.
Positive = misery. Negative = joy.

Key principles:
- Championships are strong joy (-200), compounding if titles come within 15 years
- Playoff appearances are joy (negative). Deeper = more joy.
- Finals losses start as joy (first time = great season) and flip to misery on repeat.
  Recency matters: losses closer together compound harder.
- Missed playoffs: misery scaled by how bad the team was (4 bands).
- Drought multiplier: tiered across 4 buckets, hard ceiling to prevent stacking.
- Post-championship joy offset lingers for 3 years after a title.
- Heartbreak registry: hardcoded legendary collapses add flat point bonuses.
"""

import math
from typing import Optional


# ---------------------------------------------------------------------------
# Base outcome scores
# ---------------------------------------------------------------------------
# exit: 0=missed playoffs, 1=R1, 2=R2, 3=Conf Finals, 4=Finals loss, 5=Champion

def base_playoff_joy(exit_round: int) -> float:
    """
    Playoff appearances are joy (negative). Finals losses handled separately.
    Championship joy is also handled separately (compounding).
    This covers: R1, R2, Conf Finals only.
    """
    if exit_round == 3:   return -20.0   # Conference finals
    elif exit_round == 2: return -12.0   # Round 2
    elif exit_round == 1: return -5.0    # Round 1
    return 0.0


def missed_playoff_misery(win_pct: float) -> float:
    """
    Missed playoffs: misery scaled by how bad the team was.
    Four bands.
    """
    if win_pct >= 0.556:   return 15.0   # Competitive miss (e.g. 9-8 NFL, 48-win NBA)
    elif win_pct >= 0.444: return 30.0   # Mediocre
    elif win_pct >= 0.333: return 46.0   # Bad
    else:                  return 60.0   # Historically terrible


# ---------------------------------------------------------------------------
# Championship joy — compounding
# ---------------------------------------------------------------------------
def championship_joy(champ_index: int) -> float:
    """
    Joy score for the Nth championship in a dynasty (within 15-year window).
    champ_index: 0 = first title, 1 = second title in window, etc.
    Compounds: -200, -260, -330, -415...  (~30% per additional title)
    """
    return -200.0 * (1.30 ** champ_index)


def get_dynasty_index(year: int, prior_champs_in_window: list) -> int:
    """
    How many prior championships has this fan seen within the last 15 years?
    That determines the compounding multiplier for this title.
    """
    window = [c for c in prior_champs_in_window if year - c <= 15]
    return len(window)


# ---------------------------------------------------------------------------
# Finals loss scoring — recency-weighted compounding
# ---------------------------------------------------------------------------
def finals_loss_score(
    year: int,
    prior_finals_losses: list,   # years of prior Finals losses (in fan memory, no title since)
    prior_champs: list,          # years of prior championships in fan memory
) -> float:
    """
    Finals appearances that end in a loss.

    First Finals loss in fan memory (or after a championship): joy (-30).
    Subsequent losses without a title in between flip positive and compound.
    Recency factor: a loss 2 years ago hurts more than one 20 years ago.

    Returns a signed score: negative = joy, positive = misery.
    """
    # Count prior Finals losses since the last championship
    last_champ = max(prior_champs) if prior_champs else None
    if last_champ:
        losses_since_title = [y for y in prior_finals_losses if y > last_champ]
    else:
        losses_since_title = list(prior_finals_losses)

    n = len(losses_since_title)  # number of prior losses without a title

    if n == 0:
        # First Finals loss — still a great season
        return -30.0

    # Subsequent losses flip positive. Base misery by loss number:
    # 2nd loss: +10, 3rd: +40, 4th: +75, 5th+: +100
    base_misery = {1: 10.0, 2: 40.0, 3: 75.0}.get(n, 100.0)

    # Recency factor: weight each prior loss by how recent it was.
    # A loss 1 year ago = full weight (1.0). A loss 15+ years ago = low weight (0.2).
    # Average recency weight across all prior losses.
    recency_weights = []
    for loss_year in losses_since_title:
        gap = year - loss_year
        weight = max(0.2, 1.0 - (gap - 1) * 0.055)  # decays from 1.0 to 0.2 over ~15 years
        recency_weights.append(weight)

    avg_recency = sum(recency_weights) / len(recency_weights)

    # Recency amplifies misery: 1.0x at average recency, up to 1.5x for all recent losses
    recency_multiplier = 0.75 + (avg_recency * 0.75)   # range: 0.90 to 1.50

    return round(base_misery * recency_multiplier, 1)


# ---------------------------------------------------------------------------
# Post-championship joy offset
# ---------------------------------------------------------------------------
def championship_joy_offset(years_since_last_champ: int) -> float:
    """
    Additive reduction for the seasons immediately after a championship.
    Captures 'house money' feeling. Applied before drought multiplier.
    """
    if years_since_last_champ == 1:   return -25.0
    elif years_since_last_champ == 2: return -12.0
    elif years_since_last_champ == 3: return -6.0
    else:                             return 0.0


# ---------------------------------------------------------------------------
# Drought multiplier — 4 tiered buckets
# ---------------------------------------------------------------------------
def drought_multiplier(
    consec_losing: int,
    consec_no_playoffs: int,
    consec_no_playoff_win: int,
    consec_no_championship: int,
) -> float:
    """
    Tiered drought multiplier applied only to positive (misery) scores.
    Each bucket adds a small increment on top of the prior one.
    Hard ceiling of 2.0x to prevent aggressive stacking.

    Bucket 1: consecutive losing seasons (below .500) — contributes most
    Bucket 2: consecutive playoff misses — adds on top
    Bucket 3: consecutive seasons without a playoff win/series win — smaller add
    Bucket 4: consecutive seasons without a championship — smallest marginal add
    """

    # Bucket 1: losing seasons streak
    if consec_losing <= 0:
        b1 = 0.0
    elif consec_losing <= 3:
        b1 = consec_losing * 0.04          # up to +0.12
    elif consec_losing <= 8:
        b1 = 0.12 + (consec_losing - 3) * 0.03  # up to +0.27
    else:
        b1 = 0.27 + (consec_losing - 8) * 0.01  # tapers, max ~+0.35

    # Bucket 2: consecutive playoff misses (adds on top, smaller)
    if consec_no_playoffs <= 2:
        b2 = 0.0
    elif consec_no_playoffs <= 6:
        b2 = (consec_no_playoffs - 2) * 0.03   # up to +0.12
    elif consec_no_playoffs <= 12:
        b2 = 0.12 + (consec_no_playoffs - 6) * 0.02  # up to +0.24
    else:
        b2 = 0.24 + (consec_no_playoffs - 12) * 0.005  # tapers

    # Bucket 3: no playoff win/series win (even smaller add)
    if consec_no_playoff_win <= 3:
        b3 = 0.0
    elif consec_no_playoff_win <= 10:
        b3 = (consec_no_playoff_win - 3) * 0.015  # up to +0.105
    else:
        b3 = 0.105 + (consec_no_playoff_win - 10) * 0.005  # tapers

    # Bucket 4: no championship (smallest marginal add)
    if consec_no_championship <= 10:
        b4 = 0.0
    elif consec_no_championship <= 25:
        b4 = (consec_no_championship - 10) * 0.008  # up to +0.12
    else:
        b4 = 0.12 + (consec_no_championship - 25) * 0.002  # tapers

    combined = 1.0 + b1 + b2 + b3 + b4
    return min(2.0, combined)   # hard ceiling


# ---------------------------------------------------------------------------
# Heartbreak events registry
# ---------------------------------------------------------------------------
HEARTBREAK_EVENTS = {
    "ATL": [
        (2016, 25, "28-3: Largest Super Bowl lead ever blown"),
        (1998, 10, "Lost NFC Championship after 14-2 season"),
    ],
    "BUF": [
        (1990, 20, "Wide Right — Scott Norwood's missed FG"),
        (1991, 18, "Thurman Thomas lost helmet, never recovered"),
        (1992, 16, "Third consecutive Super Bowl loss"),
        (1993, 16, "Fourth consecutive Super Bowl loss — unprecedented"),
        (2022, 15, "Damar Hamlin cardiac arrest derailed season"),
    ],
    "MIN": [
        (1998, 22, "Gary Anderson missed FG, then lost NFC Championship"),
        (2009, 18, "Brett Favre INT in OT ends NFC title run"),
        (1969, 15, "Lost Super Bowl IV despite being heavy favorites"),
        (2000, 12, "NFC title game blown on final drive"),
        (2017, 12, "Minneapolis Miracle... then blown out in NFC title"),
    ],
    "CLE": [
        (1986, 22, "The Drive — Elway 98 yards in Cleveland"),
        (1987, 20, "The Fumble — Earnest Byner"),
        (1995, 18, "Art Modell moves franchise to Baltimore"),
    ],
    "CHC": [
        (2003, 22, "Bartman Game — 5 outs away from World Series"),
        (1984, 15, "Leon Durham error in NLCS"),
        (1969, 12, "Collapsed from 9.5 games up in August"),
    ],
    "BOS_MLB": [
        (1986, 25, "Buckner Error — one strike away from WS title"),
        (1978, 18, "Bucky Dent HR, collapsed late-season lead"),
        (2003, 15, "Aaron Boone walk-off HR, Grady Little leaves Pedro in"),
    ],
    "NYM": [
        (2007, 20, "Collapsed from 7-game lead with 17 games left"),
        (2008, 15, "Collapsed from division lead again, final year at Shea"),
        (1988, 12, "Lost NLCS to Dodgers as heavy favorites"),
    ],
    "SEA_NFL": [
        (2014, 25, "Goal-line interception on 2nd and 1, Super Bowl XLIX"),
    ],
    "DEN": [
        (1986, 15, "Lost Super Bowl 39-20 to Giants after The Drive"),
        (1987, 14, "Lost Super Bowl 42-10 to Redskins"),
        (1989, 14, "Lost Super Bowl 55-10 to 49ers"),
        (2013, 18, "Lost Super Bowl 43-8 to Seahawks as historically great offense"),
    ],
    "SFG": [
        (2002, 22, "Rally Monkey — up 3-2 with 8th inning lead in Game 6"),
        (2016, 12, "Lost NLDS as defending champions"),
    ],
    "PHI_MLB": [
        (1964, 18, "Phillies Phold — collapsed from 6.5 games up with 12 to play"),
        (1977, 10, "Lost NLCS to Dodgers as favorites"),
        (1978, 10, "Lost NLCS to Dodgers again"),
    ],
    "TOR_NHL": [
        (2013, 15, "Blew 4-1 lead in Game 7, third period vs Boston"),
        (2019, 12, "Lost Game 7 first round to Boston again"),
        (2020, 12, "Lost Game 7 first round to Columbus"),
        (2023, 12, "Lost first round again — 7th straight first-round exit or miss"),
    ],
    "VAN": [
        (1994, 18, "Game 7 Cup Final loss to Rangers — city riots"),
        (2011, 18, "Game 7 Cup Final loss to Bruins — city riots again"),
    ],
    "WAS_NFL": [
        (2012, 15, "RG3 injured in wild card game, team never recovered"),
    ],
    "HOU_MLB": [
        (2017, 10, "Sign-stealing scandal taints championship"),
        (2019, 10, "Sign-stealing scandal revealed — Astros 2.0"),
    ],
}


def get_heartbreak_bonus(team_id: str, league: str, year: int) -> float:
    keys_to_try = [f"{team_id}_{league}", team_id]
    for key in keys_to_try:
        for (event_year, severity, _) in HEARTBREAK_EVENTS.get(key, []):
            if event_year == year:
                return float(severity)
    return 0.0


def get_heartbreak_description(team_id: str, league: str, year: int) -> Optional[str]:
    keys_to_try = [f"{team_id}_{league}", team_id]
    for key in keys_to_try:
        for (event_year, _, desc) in HEARTBREAK_EVENTS.get(key, []):
            if event_year == year:
                return desc
    return None


# ---------------------------------------------------------------------------
# Full team calculation
# ---------------------------------------------------------------------------
def calculate_team_misery(team_data: dict, fan_start: int) -> dict:
    league        = team_data["league"]
    seasons       = team_data["seasons"]
    championships = team_data.get("championships", [])
    finals_losses = team_data.get("finals_losses", [])
    team_start    = team_data["founded"]
    team_id       = team_data["id"]

    effective_start = max(fan_start, team_start)

    fan_seasons_sorted = sorted(
        [(int(k), v) for k, v in seasons.items()
         if int(k) >= effective_start and v is not None],
        key=lambda x: x[0]
    )

    if not fan_seasons_sorted:
        return {"error": "No seasons found for the given start year.", "total_score": 0}

    # Championships and finals losses visible to this fan
    fan_champs       = [c for c in championships if c >= effective_start]
    fan_finals_losses_all = [y for y in finals_losses if y >= effective_start]

    total_score   = 0.0
    season_scores = {}
    worst_season_year  = None
    worst_season_score = float("-inf")
    best_season_year   = None
    best_season_score  = float("inf")

    # Drought trackers (reset on events)
    consec_losing         = 0
    consec_no_playoffs    = 0
    consec_no_playoff_win = 0
    consec_no_championship = 0

    for year, s in fan_seasons_sorted:
        g = s.get("g", 0)
        if g == 0:
            continue

        exit_round = s.get("exit", 0)
        win_pct    = s["w"] / g

        # --- Championships seen so far (before this year) ---
        prior_champs = [c for c in fan_champs if c < year]

        # --- Finals losses in fan memory without a title in between ---
        last_champ = max(prior_champs) if prior_champs else None
        if last_champ:
            prior_finals_losses_since_title = [y2 for y2 in fan_finals_losses_all
                                               if last_champ < y2 < year]
        else:
            prior_finals_losses_since_title = [y2 for y2 in fan_finals_losses_all if y2 < year]

        # --- Years since last championship (for joy offset) ---
        if prior_champs:
            years_since_last_champ = year - max(prior_champs)
        else:
            years_since_last_champ = 999

        # ---- Score this season ----

        if exit_round == 5:
            # Championship — compounding joy
            dynasty_idx = get_dynasty_index(year, prior_champs)
            base = championship_joy(dynasty_idx)
            joy_offset = 0.0
            d_mult = 1.0
            heartbreak = 0.0

        elif exit_round == 4:
            # Finals loss — recency-weighted, flips on repeat
            base = finals_loss_score(year, prior_finals_losses_since_title, prior_champs)
            joy_offset = championship_joy_offset(years_since_last_champ) if base < 0 else 0.0
            d_mult = drought_multiplier(
                consec_losing, consec_no_playoffs,
                consec_no_playoff_win, consec_no_championship
            ) if base > 0 else 1.0
            heartbreak = get_heartbreak_bonus(team_id, league, year)

        elif exit_round in (1, 2, 3):
            # Playoff appearance — joy
            base = base_playoff_joy(exit_round)
            joy_offset = championship_joy_offset(years_since_last_champ)
            d_mult = 1.0
            heartbreak = get_heartbreak_bonus(team_id, league, year)

        else:
            # Missed playoffs — misery
            base = missed_playoff_misery(win_pct)
            joy_offset = championship_joy_offset(years_since_last_champ)
            adjusted_before_drought = base + joy_offset
            d_mult = drought_multiplier(
                consec_losing, consec_no_playoffs,
                consec_no_playoff_win, consec_no_championship
            ) if adjusted_before_drought > 0 else 1.0
            heartbreak = get_heartbreak_bonus(team_id, league, year)

        # Assemble score
        adjusted = base + joy_offset
        if adjusted > 0:
            adjusted *= d_mult
        adjusted += heartbreak

        total = round(adjusted, 1)
        heartbreak_desc = get_heartbreak_description(team_id, league, year)

        season_scores[str(year)] = {
            "total": total,
            "base": round(base, 1),
            "components": {
                "base_outcome": round(base, 1),
                "joy_offset": round(joy_offset, 1),
                "drought_multiplier": round(d_mult, 3),
                "heartbreak": round(heartbreak, 1),
            },
            "heartbreak_desc": heartbreak_desc,
        }

        total_score += total

        # Track extremes
        if total > worst_season_score:
            worst_season_score = total
            worst_season_year  = year
        if total < best_season_score:
            best_season_score = total
            best_season_year  = year

        # ---- Update drought trackers ----
        if exit_round == 5:
            # Championship resets everything
            consec_losing          = 0
            consec_no_playoffs     = 0
            consec_no_playoff_win  = 0
            consec_no_championship = 0
        else:
            consec_no_championship += 1

            if exit_round == 0:
                consec_no_playoffs += 1
                consec_no_playoff_win += 1
            else:
                consec_no_playoffs = 0
                # Playoff win = advanced past R1; R1 exit = no playoff win
                if exit_round >= 2:
                    consec_no_playoff_win = 0
                else:
                    consec_no_playoff_win += 1

            if win_pct < 0.500:
                consec_losing += 1
            else:
                consec_losing = 0

    total_seasons  = len(fan_seasons_sorted)
    playoff_seasons = sum(1 for _, s in fan_seasons_sorted if s and s.get("exit", 0) > 0)

    return {
        "team_id": team_id,
        "team_name": team_data["name"],
        "league": league,
        "fan_start": effective_start,
        "seasons_watched": total_seasons,
        "championships": fan_champs,
        "finals_losses": [y for y in fan_finals_losses_all],
        "playoff_appearances": playoff_seasons,
        "total_score": round(total_score, 1),
        "avg_score_per_season": round(total_score / total_seasons, 1) if total_seasons else 0,
        "worst_season": {"year": worst_season_year, "score": round(worst_season_score, 1)},
        "best_season":  {"year": best_season_year,  "score": round(best_season_score, 1)},
        "season_scores": season_scores,
    }


# ---------------------------------------------------------------------------
# Multi-team aggregation
# ---------------------------------------------------------------------------
def calculate_overall_misery(team_results: list) -> dict:
    if not team_results:
        return {"total_score": 0, "team_results": []}

    total = sum(t["total_score"] for t in team_results)
    sorted_results = sorted(team_results, key=lambda x: x["total_score"], reverse=True)

    return {
        "total_score": round(total, 1),
        "team_results": sorted_results,
    }


# ---------------------------------------------------------------------------
# Misery label
# ---------------------------------------------------------------------------
def misery_label(score: float, num_teams: int, total_seasons: int) -> dict:
    """
    Human-readable label based on score per team.
    Normalizes for number of teams followed (a 4-team fan shouldn't get
    4x the label just for following more teams), but NOT for years watched
    (a 40-year fan has genuinely suffered more than a 20-year fan).
    """
    teams      = max(num_teams, 1)
    per_season = score / teams

    if per_season >= 45:
        label, emoji = "Legendary Suffering",                    "💀"
    elif per_season >= 30:
        label, emoji = "Chronic Heartbreak",                     "😭"
    elif per_season >= 15:
        label, emoji = "Perpetual Disappointment",               "😤"
    elif per_season >= 5:
        label, emoji = "Occasional Sadness",                     "😔"
    elif per_season >= -10:
        label, emoji = "Pretty Lucky, Actually",                 "🙂"
    elif per_season >= -30:
        label, emoji = "Insufferable Winner",                    "🏆"
    else:
        label, emoji = "Dynasty Fan. We Don't Want to Hear It.", "👑"

    return {"label": label, "emoji": emoji, "per_season_avg": round(per_season, 1)}
