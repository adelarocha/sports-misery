#!/usr/bin/env python3
"""
Recomputes actual scores for all seed personas using live data files,
then rewrites SEED_ENTRIES in seed_db.py with correct values.

Usage:
    python3 generate_seeds.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scoring import calculate_team_misery, calculate_overall_misery

DATA_DIR = Path(__file__).parent / "data"

# Load all four league data files
def load_leagues():
    leagues = {}
    for lg in ("nfl", "nba", "mlb", "nhl"):
        path = DATA_DIR / f"{lg}.json"
        if not path.exists():
            print(f"ERROR: {path} not found. Run fetch_data.py first.")
            sys.exit(1)
        with open(path) as f:
            data = json.load(f)
        for code, team in data["teams"].items():
            key = f"{lg.upper()}:{code}"
            leagues[key] = team
    return leagues

# Persona definitions: (display_name, team_keys, fan_start)
PERSONAS = [
    ("MinnesotaMisery",     ["NFL:MIN","NBA:MIN","MLB:MIN","NHL:MIN"],          1990),
    ("NYAllDayFan",         ["NFL:NYJ","MLB:NYM","NBA:NYK"],                    1990),
    ("DCAllTeamsFan",       ["NFL:WAS","MLB:WAS","NBA:WAS","NHL:WSH"],          1990),
    ("ClevelandFaithful",   ["NFL:CLE","MLB:CLE","NBA:CLE"],                    1990),
    ("PhillyPhanatic",      ["NFL:PHI","MLB:PHI","NBA:PHI","NHL:PHI"],          1990),
    ("ArizonaSunburn",      ["NFL:ARI","NBA:PHX","MLB:ARI"],                    1995),
    ("TorontoTears",        ["NHL:TOR","NBA:TOR","MLB:TOR"],                    1990),
    ("CarolinaAllIn",       ["NFL:CAR","NBA:CHA","NHL:CAR"],                    1995),
    ("BuffaloOrDie",        ["NFL:BUF","NHL:BUF"],                              1990),
    ("AtlantaUnited",       ["NFL:ATL","MLB:ATL","NBA:ATL"],                    1995),
    ("OaklandGrief",        ["NFL:LV","MLB:OAK"],                               1990),
    ("MilwaukeeFaithful",   ["MLB:MIL","NBA:MIL"],                              1990),
    ("TampaBayAllIn",       ["NFL:TB","MLB:TB","NHL:TBL","NBA:ORL"],            1995),
    ("CincinnatiBengalsFan",["NFL:CIN","MLB:CIN"],                              1990),
    ("PhoenixSunsFan",      ["NBA:PHX","NFL:ARI"],                              1993),
    ("DetroitSuffers",      ["NFL:DET","MLB:DET","NBA:DET","NHL:DET"],          1990),
    ("DallasDreamer",       ["NFL:DAL","NBA:DAL","MLB:TEX","NHL:DAL"],          1995),
    ("MontrealHabsFan",     ["NHL:MTL","NBA:TOR"],                              1990),
    ("TennesseeTime",       ["NFL:TEN","NBA:MEM"],                              1999),
    ("WisconsinCheese",     ["NFL:GB","NBA:MIL","MLB:MIL"],                     1990),
    ("SacramentoKingsFan",  ["NBA:SAC"],                                        1993),
    ("BrownsBacker",        ["NFL:CLE"],                                        1990),
    ("DenverBroncoFan",     ["NFL:DEN","NBA:DEN","NHL:COL","MLB:COL"],          1990),
    ("JetsNation",          ["NFL:NYJ"],                                        1985),
    ("ChiSoxFan",           ["MLB:CWS","NFL:CHI","NBA:CHI"],                    1995),
    ("CubsFan4Life",        ["MLB:CHC"],                                        1980),
    ("OrlandoMagicFan",     ["NBA:ORL"],                                        1993),
    ("SaintsFan",           ["NFL:NO","NBA:NOP"],                               1995),
    ("KnicksTape",          ["NBA:NYK"],                                        1994),
    ("RaiderNation",        ["NFL:LV"],                                         1990),
    ("BaltimoreRavenous",   ["NFL:BAL","MLB:BAL","NHL:WSH"],                    1996),
    ("PortlandRipCity",     ["NBA:POR"],                                        1990),
    ("MiamiMelancholy",     ["NFL:MIA","NBA:MIA","MLB:MIA","NHL:FLA"],          1995),
    ("MemphisGrizzFan",     ["NBA:MEM"],                                        2001),
    ("JacksonvilleJag",     ["NFL:JAX"],                                        1995),
    ("ColoradoChaos",       ["NFL:DEN","MLB:COL","NBA:DEN","NHL:COL"],          1995),
    ("IndianaFan",          ["NFL:IND","NBA:IND"],                              1995),
    ("HoustonAllIn",        ["NFL:HOU","MLB:HOU","NBA:HOU"],                    1993),
    ("SeattleStill",        ["NFL:SEA","MLB:SEA"],                              1995),
    ("SFGiantsFan",         ["MLB:SF","NFL:SF","NBA:GSW","NHL:SJS"],            1990),
    ("VegasGoldenFan",      ["NHL:VGK","NFL:LV"],                               2017),
    ("PittsburghSteel",     ["NFL:PIT","MLB:PIT","NHL:PIT"],                    1990),
    ("OklahomaThunder",     ["NBA:OKC","NFL:KC"],                               2008),
    ("ChicagoBullsLegacy",  ["NBA:CHI","MLB:CHC","NFL:CHI","NHL:CHI"],          1990),
    ("KCChiefsFan",         ["NFL:KC","MLB:KC"],                                2012),
    ("SanAntonioSpursFan",  ["NBA:SAS"],                                        1993),
    ("BayAreaAllIn",        ["NBA:GSW","MLB:SF","NFL:SF"],                      2010),
    ("NewEnglandLifer",     ["NFL:NE","MLB:BOS","NBA:BOS","NHL:BOS"],           1990),
    ("BostonDynasty",       ["NFL:NE","MLB:BOS","NBA:BOS","NHL:BOS"],           2000),
    ("LakersForLife",       ["NBA:LAL"],                                        1980),
]


def compute_score(leagues, team_keys, fan_start):
    results = []
    for key in team_keys:
        if key not in leagues:
            print(f"  WARNING: {key} not found in data — skipping")
            continue
        r = calculate_team_misery(leagues[key], fan_start)
        if "error" not in r:
            results.append(r)
    if not results:
        return 0
    overall = calculate_overall_misery(results)
    return int(round(overall["total_score"]))


def main():
    print("Loading league data...")
    leagues = load_leagues()
    print(f"Loaded {len(leagues)} teams across all leagues.\n")

    computed = []
    for name, team_keys, fan_start in PERSONAS:
        score = compute_score(leagues, team_keys, fan_start)
        computed.append((name, score, team_keys, fan_start))
        print(f"  {name:30s}  score={score:>7}")

    # Sort by score descending (most miserable first)
    computed.sort(key=lambda x: x[1], reverse=True)

    print("\n\nGenerating updated SEED_ENTRIES...\n")

    # Build the new seed_db.py content
    lines = []
    lines.append('"""')
    lines.append('Seed data for the Sports Misery leaderboard.')
    lines.append('50 pre-populated fan personas representing real city fanbases.')
    lines.append('Scores are actual outputs from the scoring model — run generate_seeds.py to refresh.')
    lines.append('"""')
    lines.append('')
    lines.append('# Each entry: display_name, score, teams (list of "LEAGUE:TEAMID"), fan_start')
    lines.append('SEED_ENTRIES = [')

    tiers = [
        (computed[0][1],  "── Peak misery ────────────────────────────────────────────────────────"),
        (computed[10][1], "── Heavy misery ───────────────────────────────────────────────────────"),
        (computed[20][1], "── Mid-tier ───────────────────────────────────────────────────────────"),
        (computed[30][1], "── Lower misery ───────────────────────────────────────────────────────"),
        (computed[40][1], "── Lucky / winners ────────────────────────────────────────────────────"),
    ]
    tier_indices = [0, 10, 20, 30, 40]

    for i, (name, score, team_keys, fan_start) in enumerate(computed):
        if i in tier_indices:
            j = tier_indices.index(i)
            lines.append(f"    # {tiers[j][1]}")
        teams_str = json.dumps(team_keys)
        lines.append(f'    {{"display_name": "{name}", "score": {score:>6}, "teams": {teams_str}, "fan_start": {fan_start}}},')

    lines.append(']')
    lines.append('')
    lines.append('')
    lines.append('if __name__ == "__main__":')
    lines.append('    """Standalone: seed the DB directly."""')
    lines.append('    import os')
    lines.append('    if not os.environ.get("DATABASE_URL"):')
    lines.append('        print("ERROR: DATABASE_URL not set.")')
    lines.append('        raise SystemExit(1)')
    lines.append('    import db')
    lines.append('    db.init_db()')
    lines.append('    db.add_unique_email_constraint()')
    lines.append('    if db.has_seeded():')
    lines.append('        print("Already seeded. Skipping.")')
    lines.append('        raise SystemExit(0)')
    lines.append('    db.seed_leaderboard(SEED_ENTRIES)')
    lines.append('    print(f"Seeded {len(SEED_ENTRIES)} entries.")')

    out_path = Path(__file__).parent / "seed_db.py"
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nWrote {len(computed)} entries to {out_path}")
    print(f"\nScore range: {computed[0][0]} = {computed[0][1]}  ...  {computed[-1][0]} = {computed[-1][1]}")


if __name__ == "__main__":
    main()
