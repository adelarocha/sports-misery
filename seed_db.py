"""
Seed data for the Sports Misery leaderboard.
50 pre-populated fan personas representing real city fanbases.
Scores are pre-calculated approximations based on the scoring model.

This file is imported by main.py on first startup.
It can also be run standalone: python seed_db.py
"""

# Each entry: display_name, score, teams (list of team IDs), fan_start
SEED_ENTRIES = [
    # ── Highest misery ─────────────────────────────────────────────────────
    {
        "display_name": "NYAllDayFan",
        "score": 5600,
        "teams": ["NFL:NYJ", "MLB:NYM", "NBA:NYK"],
        "fan_start": 1990,
    },
    {
        "display_name": "MinnesotaMisery",
        "score": 5250,
        "teams": ["NFL:MIN", "NBA:MIN", "MLB:MIN", "NHL:MIN"],
        "fan_start": 1990,
    },
    {
        "display_name": "DCAllTeamsFan",
        "score": 4839,
        "teams": ["NFL:WAS", "MLB:WSH", "NBA:WAS", "NHL:WSH"],
        "fan_start": 1990,
    },
    {
        "display_name": "DetroitSuffers",
        "score": 4720,
        "teams": ["NFL:DET", "MLB:DET", "NBA:DET", "NHL:DET"],
        "fan_start": 1990,
    },
    {
        "display_name": "ClevelandFaithful",
        "score": 4650,
        "teams": ["NFL:CLE", "MLB:CLE", "NBA:CLE"],
        "fan_start": 1990,
    },
    {
        "display_name": "BuffaloOrDie",
        "score": 4510,
        "teams": ["NFL:BUF", "MLB:BUF", "NHL:BUF"],
        "fan_start": 1990,
    },
    {
        "display_name": "JetsNation",
        "score": 4480,
        "teams": ["NFL:NYJ"],
        "fan_start": 1985,
    },
    {
        "display_name": "CubsFan4Life",
        "score": 4200,
        "teams": ["MLB:CHC"],
        "fan_start": 1980,
    },
    {
        "display_name": "TampaBayAllIn",
        "score": 4100,
        "teams": ["NFL:TB", "MLB:TB", "NHL:TB", "NBA:ORL"],
        "fan_start": 1995,
    },
    {
        "display_name": "PhillyPhanatic",
        "score": 4050,
        "teams": ["NFL:PHI", "MLB:PHI", "NBA:PHI", "NHL:PHI"],
        "fan_start": 1990,
    },
    # ── Heavy misery ───────────────────────────────────────────────────────
    {
        "display_name": "BrownsBacker",
        "score": 3980,
        "teams": ["NFL:CLE"],
        "fan_start": 1990,
    },
    {
        "display_name": "KnicksTape",
        "score": 3870,
        "teams": ["NBA:NYK"],
        "fan_start": 1994,
    },
    {
        "display_name": "TorontoTears",
        "score": 3810,
        "teams": ["NHL:TOR", "NBA:TOR", "MLB:TOR"],
        "fan_start": 1990,
    },
    {
        "display_name": "ArizonaSunburn",
        "score": 3750,
        "teams": ["NFL:ARI", "NBA:PHX", "MLB:ARI"],
        "fan_start": 1995,
    },
    {
        "display_name": "SacramentoKingsFan",
        "score": 3680,
        "teams": ["NBA:SAC"],
        "fan_start": 1993,
    },
    {
        "display_name": "OaklandGrief",
        "score": 3600,
        "teams": ["NFL:LV", "MLB:OAK"],
        "fan_start": 1990,
    },
    {
        "display_name": "ChiSoxFan",
        "score": 3550,
        "teams": ["MLB:CWS", "NFL:CHI", "NBA:CHI"],
        "fan_start": 1995,
    },
    {
        "display_name": "HoustonAllIn",
        "score": 3490,
        "teams": ["NFL:HOU", "MLB:HOU", "NBA:HOU"],
        "fan_start": 1993,
    },
    {
        "display_name": "SeattleStill",
        "score": 3420,
        "teams": ["NFL:SEA", "MLB:SEA"],
        "fan_start": 1995,
    },
    {
        "display_name": "MiamiMelancholy",
        "score": 3380,
        "teams": ["NFL:MIA", "NBA:MIA", "MLB:MIA", "NHL:FLA"],
        "fan_start": 1995,
    },
    # ── Mid-tier misery ────────────────────────────────────────────────────
    {
        "display_name": "DallasDreamer",
        "score": 3200,
        "teams": ["NFL:DAL", "NBA:DAL", "MLB:TEX", "NHL:DAL"],
        "fan_start": 1995,
    },
    {
        "display_name": "CincinnatiBengalsFan",
        "score": 3150,
        "teams": ["NFL:CIN", "MLB:CIN"],
        "fan_start": 1990,
    },
    {
        "display_name": "TennesseeTime",
        "score": 3080,
        "teams": ["NFL:TEN", "NBA:MEM"],
        "fan_start": 1999,
    },
    {
        "display_name": "JacksonvilleJag",
        "score": 2990,
        "teams": ["NFL:JAX"],
        "fan_start": 1995,
    },
    {
        "display_name": "CarloinaAllIn",
        "score": 2930,
        "teams": ["NFL:CAR", "NBA:CHA", "NHL:CAR"],
        "fan_start": 1995,
    },
    {
        "display_name": "AtlantaUnited",
        "score": 2880,
        "teams": ["NFL:ATL", "MLB:ATL", "NBA:ATL", "NHL:ATL"],
        "fan_start": 1995,
    },
    {
        "display_name": "ColoradoChaos",
        "score": 2810,
        "teams": ["NFL:DEN", "MLB:COL", "NBA:DEN", "NHL:COL"],
        "fan_start": 1995,
    },
    {
        "display_name": "MilwaukeeFaithful",
        "score": 2760,
        "teams": ["MLB:MIL", "NBA:MIL"],
        "fan_start": 1990,
    },
    {
        "display_name": "SaintsFan",
        "score": 2700,
        "teams": ["NFL:NO", "NBA:NOP"],
        "fan_start": 1995,
    },
    {
        "display_name": "OrlandoMagicFan",
        "score": 2640,
        "teams": ["NBA:ORL"],
        "fan_start": 1993,
    },
    # ── Average ────────────────────────────────────────────────────────────
    {
        "display_name": "RaiderNation",
        "score": 2580,
        "teams": ["NFL:LV"],
        "fan_start": 1990,
    },
    {
        "display_name": "PortlandRipCity",
        "score": 2510,
        "teams": ["NBA:POR"],
        "fan_start": 1990,
    },
    {
        "display_name": "IndianapaFan",
        "score": 2460,
        "teams": ["NFL:IND", "NBA:IND", "MLB:IND"],
        "fan_start": 1995,
    },
    {
        "display_name": "OklahomaThunder",
        "score": 2390,
        "teams": ["NBA:OKC", "NFL:KC"],
        "fan_start": 2008,
    },
    {
        "display_name": "MontréalHabsFan",
        "score": 2320,
        "teams": ["NHL:MTL", "NBA:TOR"],
        "fan_start": 1990,
    },
    {
        "display_name": "PhoenixSunsFan",
        "score": 2280,
        "teams": ["NBA:PHX", "NFL:ARI"],
        "fan_start": 1993,
    },
    {
        "display_name": "NewEnglandLifer",
        "score": 2100,
        "teams": ["NFL:NE", "MLB:BOS", "NBA:BOS", "NHL:BOS"],
        "fan_start": 1990,
    },
    {
        "display_name": "WisconsinCheese",
        "score": 2050,
        "teams": ["NFL:GB", "NBA:MIL", "MLB:MIL"],
        "fan_start": 1990,
    },
    {
        "display_name": "BaltimoreRavenous",
        "score": 1960,
        "teams": ["NFL:BAL", "MLB:BAL", "NHL:WSH"],
        "fan_start": 1996,
    },
    {
        "display_name": "MemphisGrizzFan",
        "score": 1890,
        "teams": ["NBA:MEM"],
        "fan_start": 2001,
    },
    {
        "display_name": "VegasGoldenFan",
        "score": 1820,
        "teams": ["NHL:VGK", "NFL:LV", "NBA:UTA"],
        "fan_start": 2017,
    },
    # ── Lower misery / winners ─────────────────────────────────────────────
    {
        "display_name": "DenverBroncoFan",
        "score": 1650,
        "teams": ["NFL:DEN", "NBA:DEN", "NHL:COL", "MLB:COL"],
        "fan_start": 1990,
    },
    {
        "display_name": "PittsburghSteel",
        "score": 1540,
        "teams": ["NFL:PIT", "MLB:PIT", "NHL:PIT"],
        "fan_start": 1990,
    },
    {
        "display_name": "SanAntonioSpursFan",
        "score": 1200,
        "teams": ["NBA:SAS"],
        "fan_start": 1993,
    },
    {
        "display_name": "ChicagoBullsLegacy",
        "score": 980,
        "teams": ["NBA:CHI", "MLB:CHC", "NFL:CHI", "NHL:CHI"],
        "fan_start": 1990,
    },
    {
        "display_name": "SFGiantsFan",
        "score": 820,
        "teams": ["MLB:SF", "NFL:SF", "NBA:GSW", "NHL:SJS"],
        "fan_start": 1990,
    },
    {
        "display_name": "KCChiefsFan",
        "score": -471,
        "teams": ["NFL:KC", "MLB:KC"],
        "fan_start": 2012,
    },
    {
        "display_name": "BayAreaAllIn",
        "score": -650,
        "teams": ["NBA:GSW", "MLB:SF", "NFL:SF"],
        "fan_start": 2010,
    },
    {
        "display_name": "BostonDynasty",
        "score": -822,
        "teams": ["NFL:NE", "MLB:BOS", "NBA:BOS", "NHL:BOS"],
        "fan_start": 2000,
    },
    {
        "display_name": "LakersForLife",
        "score": -1409,
        "teams": ["NBA:LAL"],
        "fan_start": 1980,
    },
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
