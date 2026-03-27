"""
Seed data for the Sports Misery leaderboard.
50 pre-populated fan personas representing real city fanbases.
Scores are actual outputs from the scoring model — run generate_seeds.py to refresh.

This file is imported by main.py on first startup.
It can also be run standalone: python seed_db.py
"""

# Each entry: display_name, score, teams (list of "LEAGUE:TEAMID"), fan_start
SEED_ENTRIES = [
    # ── Peak misery ────────────────────────────────────────────────────────
    {"display_name": "MinnesotaMisery",     "score":  5068, "teams": ["NFL:MIN","NBA:MIN","MLB:MIN","NHL:MIN"],          "fan_start": 1990},
    {"display_name": "NYAllDayFan",         "score":  4468, "teams": ["NFL:NYJ","MLB:NYM","NBA:NYK"],                    "fan_start": 1990},
    {"display_name": "DCAllTeamsFan",       "score":  4291, "teams": ["NFL:WAS","MLB:WAS","NBA:WAS","NHL:WSH"],          "fan_start": 1990},
    {"display_name": "ClevelandFaithful",   "score":  3824, "teams": ["NFL:CLE","MLB:CLE","NBA:CLE"],                    "fan_start": 1990},
    {"display_name": "PhillyPhanatic",      "score":  3311, "teams": ["NFL:PHI","MLB:PHI","NBA:PHI","NHL:PHI"],          "fan_start": 1990},
    {"display_name": "ArizonaSunburn",      "score":  3177, "teams": ["NFL:ARI","NBA:PHX","MLB:ARI"],                    "fan_start": 1995},
    {"display_name": "TorontoTears",        "score":  3083, "teams": ["NHL:TOR","NBA:TOR","MLB:TOR"],                    "fan_start": 1990},
    {"display_name": "CarolinaAllIn",       "score":  3079, "teams": ["NFL:CAR","NBA:CHA","NHL:CAR"],                    "fan_start": 1995},
    {"display_name": "BuffaloOrDie",        "score":  3052, "teams": ["NFL:BUF","NHL:BUF"],                              "fan_start": 1990},
    {"display_name": "AtlantaUnited",       "score":  2940, "teams": ["NFL:ATL","MLB:ATL","NBA:ATL"],                    "fan_start": 1995},
    # ── Heavy misery ───────────────────────────────────────────────────────
    {"display_name": "OaklandGrief",        "score":  2867, "teams": ["NFL:LV","MLB:OAK"],                               "fan_start": 1990},
    {"display_name": "MilwaukeeFaithful",   "score":  2849, "teams": ["MLB:MIL","NBA:MIL"],                              "fan_start": 1990},
    {"display_name": "TampaBayAllIn",       "score":  2579, "teams": ["NFL:TB","MLB:TB","NHL:TBL","NBA:ORL"],            "fan_start": 1995},
    {"display_name": "CincinnatiBengalsFan","score":  2532, "teams": ["NFL:CIN","MLB:CIN"],                              "fan_start": 1990},
    {"display_name": "PhoenixSunsFan",      "score":  2504, "teams": ["NBA:PHX","NFL:ARI"],                              "fan_start": 1993},
    {"display_name": "DetroitSuffers",      "score":  2424, "teams": ["NFL:DET","MLB:DET","NBA:DET","NHL:DET"],          "fan_start": 1990},
    {"display_name": "DallasDreamer",       "score":  2199, "teams": ["NFL:DAL","NBA:DAL","MLB:TEX","NHL:DAL"],          "fan_start": 1995},
    {"display_name": "MontrealHabsFan",     "score":  2012, "teams": ["NHL:MTL","NBA:TOR"],                              "fan_start": 1990},
    {"display_name": "TennesseeTime",       "score":  2005, "teams": ["NFL:TEN","NBA:MEM"],                              "fan_start": 1999},
    {"display_name": "WisconsinCheese",     "score":  1989, "teams": ["NFL:GB","NBA:MIL","MLB:MIL"],                     "fan_start": 1990},
    # ── Mid-tier ───────────────────────────────────────────────────────────
    {"display_name": "SacramentoKingsFan",  "score":  1973, "teams": ["NBA:SAC"],                                        "fan_start": 1993},
    {"display_name": "BrownsBacker",        "score":  1828, "teams": ["NFL:CLE"],                                        "fan_start": 1990},
    {"display_name": "DenverBroncoFan",     "score":  1763, "teams": ["NFL:DEN","NBA:DEN","NHL:COL","MLB:COL"],          "fan_start": 1990},
    {"display_name": "JetsNation",          "score":  1757, "teams": ["NFL:NYJ"],                                        "fan_start": 1985},
    {"display_name": "ChiSoxFan",           "score":  1731, "teams": ["MLB:CWS","NFL:CHI","NBA:CHI"],                    "fan_start": 1995},
    {"display_name": "CubsFan4Life",        "score":  1672, "teams": ["MLB:CHC"],                                        "fan_start": 1980},
    {"display_name": "OrlandoMagicFan",     "score":  1592, "teams": ["NBA:ORL"],                                        "fan_start": 1993},
    {"display_name": "SaintsFan",           "score":  1469, "teams": ["NFL:NO","NBA:NOP"],                               "fan_start": 1995},
    {"display_name": "KnicksTape",          "score":  1468, "teams": ["NBA:NYK"],                                        "fan_start": 1994},
    {"display_name": "RaiderNation",        "score":  1424, "teams": ["NFL:LV"],                                         "fan_start": 1990},
    # ── Lower misery ───────────────────────────────────────────────────────
    {"display_name": "BaltimoreRavenous",   "score":  1419, "teams": ["NFL:BAL","MLB:BAL","NHL:WSH"],                    "fan_start": 1996},
    {"display_name": "PortlandRipCity",     "score":  1411, "teams": ["NBA:POR"],                                        "fan_start": 1990},
    {"display_name": "MiamiMelancholy",     "score":  1343, "teams": ["NFL:MIA","NBA:MIA","MLB:MIA","NHL:FLA"],          "fan_start": 1995},
    {"display_name": "MemphisGrizzFan",     "score":  1102, "teams": ["NBA:MEM"],                                        "fan_start": 2001},
    {"display_name": "JacksonvilleJag",     "score":  1070, "teams": ["NFL:JAX"],                                        "fan_start": 1995},
    {"display_name": "ColoradoChaos",       "score":   940, "teams": ["NFL:DEN","MLB:COL","NBA:DEN","NHL:COL"],          "fan_start": 1995},
    {"display_name": "IndianaFan",          "score":   898, "teams": ["NFL:IND","NBA:IND"],                              "fan_start": 1995},
    {"display_name": "HoustonAllIn",        "score":   842, "teams": ["NFL:HOU","MLB:HOU","NBA:HOU"],                    "fan_start": 1993},
    {"display_name": "SeattleStill",        "score":   814, "teams": ["NFL:SEA","MLB:SEA"],                              "fan_start": 1995},
    {"display_name": "SFGiantsFan",         "score":   370, "teams": ["MLB:SF","NFL:SF","NBA:GSW","NHL:SJS"],            "fan_start": 1990},
    # ── Lucky / winners ────────────────────────────────────────────────────
    {"display_name": "VegasGoldenFan",      "score":    89, "teams": ["NHL:VGK","NFL:LV"],                               "fan_start": 2017},
    {"display_name": "PittsburghSteel",     "score":  -246, "teams": ["NFL:PIT","MLB:PIT","NHL:PIT"],                    "fan_start": 1990},
    {"display_name": "OklahomaThunder",     "score": -1019, "teams": ["NBA:OKC","NFL:KC"],                               "fan_start": 2008},
    {"display_name": "ChicagoBullsLegacy",  "score": -1128, "teams": ["NBA:CHI","MLB:CHC","NFL:CHI","NHL:CHI"],          "fan_start": 1990},
    {"display_name": "KCChiefsFan",         "score": -1468, "teams": ["NFL:KC","MLB:KC"],                                "fan_start": 2012},
    {"display_name": "SanAntonioSpursFan",  "score": -2770, "teams": ["NBA:SAS"],                                        "fan_start": 1993},
    {"display_name": "BayAreaAllIn",        "score": -3058, "teams": ["NBA:GSW","MLB:SF","NFL:SF"],                      "fan_start": 2010},
    {"display_name": "NewEnglandLifer",     "score": -4670, "teams": ["NFL:NE","MLB:BOS","NBA:BOS","NHL:BOS"],           "fan_start": 1990},
    {"display_name": "BostonDynasty",       "score": -6255, "teams": ["NFL:NE","MLB:BOS","NBA:BOS","NHL:BOS"],           "fan_start": 2000},
    {"display_name": "LakersForLife",       "score": -7659, "teams": ["NBA:LAL"],                                        "fan_start": 1980},
]


if __name__ == "__main__":
    """Standalone: seed the DB directly."""
    import os
    if not os.environ.get("DATABASE_URL"):
        print("ERROR: DATABASE_URL not set.")
        raise SystemExit(1)
    import db
    db.init_db()
    db.add_unique_email_constraint()
    if db.has_seeded():
        print("Already seeded. Skipping.")
    else:
        for e in SEED_ENTRIES:
            db.submit_entry(
                display_name=e["display_name"],
                email=None,
                score=e["score"],
                teams=e["teams"],
                fan_start=e["fan_start"],
                is_seed=True,
            )
        print(f"Seeded {len(SEED_ENTRIES)} entries successfully.")
