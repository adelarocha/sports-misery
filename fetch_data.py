#!/usr/bin/env python3
"""
Sports Misery Calculator — Live Data Fetcher
=============================================
Run this on your Mac to pull real season-by-season records from free public APIs.
Overwrites data/nfl.json, data/nba.json, data/mlb.json, data/nhl.json.

Usage:
    python3 fetch_data.py             # fetch all leagues
    python3 fetch_data.py --league nfl
    python3 fetch_data.py --league mlb --since 2020   # only update recent seasons

APIs used (all free, no key required):
    MLB  — statsapi.mlb.com  (official)
    NHL  — api-web.nhle.com  (official)
    NBA  — stats.nba.com     (official, needs browser headers)
    NFL  — site.api.espn.com (ESPN undocumented, stable)
"""

import json
import time
import argparse
import urllib.request
import urllib.error
import ssl
from pathlib import Path
from datetime import datetime

# macOS ships Python without system SSL certs; use unverified context for public sports APIs
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

CURRENT_YEAR = datetime.now().year
RATE_LIMIT_DELAY = 0.4   # seconds between requests

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def fetch_json(url, headers=None, retries=3, delay=1.0, timeout=15):
    """Fetch JSON from a URL with retry logic. Uses direct connection, no proxy."""
    hdrs = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if headers:
        hdrs.update(headers)

    req = urllib.request.Request(url, headers=hdrs)

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print(f"    HTTP {e.code} for {url[:80]}...")
            if e.code == 429:
                wait = delay * (2 ** attempt)
                print(f"    Rate limited — waiting {wait:.0f}s")
                time.sleep(wait)
            elif attempt == retries - 1:
                raise
            else:
                time.sleep(delay)
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"    Error ({e}) — retrying...")
            time.sleep(delay)

    return None


def save_league(league_id, data):
    path = DATA_DIR / f"{league_id.lower()}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved {path}")


def load_existing(league_id):
    path = DATA_DIR / f"{league_id.lower()}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


# Exit round values (consistent across all leagues):
# 0 = missed playoffs
# 1 = Round 1 (wild card / first round)
# 2 = Round 2 (divisional / second round)
# 3 = Conference Finals / semifinal
# 4 = Finals loss (runner-up)
# 5 = Champion


# ---------------------------------------------------------------------------
# MLB — statsapi.mlb.com
# ---------------------------------------------------------------------------

MLB_TEAMS = {
    # team_id: (our_code, name, city, founded)
    133: ("OAK", "Oakland Athletics",         "Oakland",      1901),
    134: ("PIT", "Pittsburgh Pirates",         "Pittsburgh",   1882),
    135: ("SD",  "San Diego Padres",           "San Diego",    1969),
    136: ("SEA", "Seattle Mariners",           "Seattle",      1977),
    137: ("SF",  "San Francisco Giants",       "San Francisco",1883),
    138: ("STL", "St. Louis Cardinals",        "St. Louis",    1882),
    139: ("TB",  "Tampa Bay Rays",             "Tampa Bay",    1998),
    140: ("TEX", "Texas Rangers",              "Arlington",    1961),
    141: ("TOR", "Toronto Blue Jays",          "Toronto",      1977),
    142: ("MIN", "Minnesota Twins",            "Minneapolis",  1901),
    143: ("PHI", "Philadelphia Phillies",      "Philadelphia", 1883),
    144: ("ATL", "Atlanta Braves",             "Atlanta",      1876),
    145: ("CWS", "Chicago White Sox",          "Chicago",      1900),
    146: ("MIA", "Miami Marlins",              "Miami",        1993),
    147: ("NYY", "New York Yankees",           "New York",     1903),
    158: ("MIL", "Milwaukee Brewers",          "Milwaukee",    1969),
    108: ("LAA", "Los Angeles Angels",         "Anaheim",      1961),
    109: ("ARI", "Arizona Diamondbacks",       "Phoenix",      1998),
    110: ("BAL", "Baltimore Orioles",          "Baltimore",    1901),
    111: ("BOS", "Boston Red Sox",             "Boston",       1901),
    112: ("CHC", "Chicago Cubs",               "Chicago",      1876),
    113: ("CIN", "Cincinnati Reds",            "Cincinnati",   1882),
    114: ("CLE", "Cleveland Guardians",        "Cleveland",    1901),
    115: ("COL", "Colorado Rockies",           "Denver",       1993),
    116: ("DET", "Detroit Tigers",             "Detroit",      1901),
    117: ("HOU", "Houston Astros",             "Houston",      1962),
    118: ("KC",  "Kansas City Royals",         "Kansas City",  1969),
    119: ("LAD", "Los Angeles Dodgers",        "Los Angeles",  1883),
    120: ("WAS", "Washington Nationals",       "Washington",   2005),
    121: ("NYM", "New York Mets",              "New York",     1962),
}

# MLB playoff round codes from the API -> our exit value
MLB_ROUND_MAP = {
    "F":  5,   # World Series win (champion)
    "LCS": 4,  # Lost LCS (Conference Finals)
    "DS":  2,  # Lost Division Series
    "WC":  1,  # Wild card loss
}

# Accurate championship and finals loss data (World Series)
MLB_CHAMPIONSHIPS = {
    "OAK": [1972, 1973, 1974, 1989],
    "PIT": [1960, 1971, 1979],
    "SD":  [],
    "SEA": [],
    "SF":  [1954, 2010, 2012, 2014],
    "STL": [1926, 1931, 1934, 1942, 1944, 1946, 1964, 1967, 1982, 2006, 2011],
    "TB":  [],
    "TEX": [],
    "TOR": [1992, 1993],
    "MIN": [1924, 1987, 1991],
    "PHI": [1929, 1930, 1980, 2008],
    "ATL": [1914, 1957, 1995],
    "CWS": [1906, 1917, 2005],
    "MIA": [1997, 2003],
    "NYY": [1923,1927,1928,1932,1936,1937,1938,1939,1941,1943,1947,1949,1950,1951,1952,1953,1956,1958,1961,1962,1977,1978,1996,1998,1999,2000,2009],
    "MIL": [],
    "LAA": [2002],
    "ARI": [2001],
    "BAL": [1966, 1970, 1983],
    "BOS": [1903,1912,1915,1916,1918,2004,2007,2013,2018],
    "CHC": [1907, 1908, 2016],
    "CIN": [1919, 1940, 1975, 1976, 1990],
    "CLE": [1920, 1948],
    "COL": [],
    "DET": [1935, 1945, 1968, 1984],
    "HOU": [2017, 2022],
    "KC":  [1985, 2015],
    "LAD": [1955,1959,1963,1965,1981,1988,2020],
    "WAS": [1924, 2019],
    "NYM": [1969, 1986],
}

MLB_FINALS_LOSSES = {
    "OAK": [1988, 1990],
    "PIT": [1903, 1925, 1927],
    "SD":  [1984, 1998],
    "SEA": [],
    "SF":  [1962, 1989, 2002],
    "STL": [1928, 1930, 1943, 1968, 1985, 1987, 2004],
    "TB":  [2008, 2020],
    "TEX": [2010, 2011, 2023],
    "TOR": [],
    "MIN": [1965],
    "PHI": [1915, 1950, 1983, 1993],
    "ATL": [1958, 1991, 1992, 1996, 1999],
    "CWS": [1919, 1959],
    "MIA": [],
    "NYY": [1921,1922,1926,1942,1955,1957,1960,1963,1964,1976,1981,2001,2003],
    "MIL": [1982],
    "LAA": [],
    "ARI": [],
    "BAL": [1969, 1971, 1979],
    "BOS": [1946, 1967, 1975, 1986],
    "CHC": [1906, 1910, 1918, 1929, 1932, 1935, 1938, 1945],
    "CIN": [1939, 1961, 1970, 1972],
    "CLE": [1954, 1995, 1997, 2016],
    "COL": [2007],
    "DET": [1907, 1908, 1909, 1934, 1940],
    "HOU": [2005, 2019, 2021],
    "KC":  [1980],
    "LAD": [1916,1920,1941,1947,1949,1952,1953,1956,1966,1974,1977,1978],
    "WAS": [1925, 1933],
    "NYM": [1973, 2000, 2015],
}


def fetch_mlb(since_year=1969):
    print("\n=== MLB ===")
    existing = load_existing("mlb")
    teams_out = {}

    # Build base team entries
    for mlb_id, (code, name, city, founded) in MLB_TEAMS.items():
        teams_out[code] = {
            "id": code, "name": name, "city": city,
            "founded": founded, "league": "MLB",
            "championships": MLB_CHAMPIONSHIPS.get(code, []),
            "finals_losses": MLB_FINALS_LOSSES.get(code, []),
            "seasons": {},
        }
        # Carry over existing seasons older than since_year
        if existing and code in existing.get("teams", {}):
            for yr, s in existing["teams"][code]["seasons"].items():
                if int(yr) < since_year:
                    teams_out[code]["seasons"][yr] = s

    # Pull season records from the API year by year
    end_year = CURRENT_YEAR - 1  # last completed season

    for season in range(since_year, end_year + 1):
        print(f"  MLB {season}...", end=" ", flush=True)
        url = f"https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season={season}&standingsTypes=regularSeason"
        try:
            data = fetch_json(url)
            time.sleep(RATE_LIMIT_DELAY)
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        # Parse standings
        season_records = {}  # code -> {w, l, g}
        for record in data.get("records", []):
            for tr in record.get("teamRecords", []):
                mlb_id = tr["team"]["id"]
                if mlb_id not in MLB_TEAMS:
                    continue
                code = MLB_TEAMS[mlb_id][0]
                w = tr.get("wins", 0)
                l = tr.get("losses", 0)
                season_records[code] = {"w": w, "l": l, "g": w + l}

        # Get playoff results for this season
        playoff_exits = fetch_mlb_playoffs(season)
        time.sleep(RATE_LIMIT_DELAY)

        for code, rec in season_records.items():
            champs = teams_out[code]["championships"]
            finals_l = teams_out[code]["finals_losses"]

            if season in champs:
                exit_round = 5
                playoffs = True
            elif season in finals_l:
                exit_round = 4
                playoffs = True
            elif code in playoff_exits:
                exit_round = playoff_exits[code]
                playoffs = True
            else:
                exit_round = 0
                playoffs = False

            teams_out[code]["seasons"][str(season)] = {
                "w": rec["w"], "l": rec["l"], "t": 0,
                "g": rec["g"], "playoffs": playoffs, "exit": exit_round,
            }

        print(f"OK ({len(season_records)} teams)")

    save_league("mlb", {"league": "MLB", "teams": teams_out})


def fetch_mlb_playoffs(season):
    """Returns dict of team_code -> exit_round for teams that made the playoffs."""
    exits = {}
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&season={season}&gameType=P&hydrate=team"
    try:
        data = fetch_json(url)
    except Exception:
        return exits

    # Find the highest round each team reached
    # Series types: WC=Wild Card, DS=Division Series, LCS=League Championship, WS=World Series
    round_value = {"WC": 1, "DS": 2, "LCS": 3, "WS": 4}
    team_max_round = {}

    for date_entry in data.get("dates", []):
        for game in date_entry.get("games", []):
            series_desc = game.get("seriesDescription", "")
            game_type   = game.get("gameType", "")
            if game_type not in ("W", "D", "L", "S"):
                continue  # not a playoff game type

            # Map game type to round
            if game_type == "W": rval = 1
            elif game_type == "D": rval = 2
            elif game_type == "L": rval = 3
            elif game_type == "S": rval = 4
            else: continue

            for side in ("home", "away"):
                team_id = game.get("teams", {}).get(side, {}).get("team", {}).get("id")
                if team_id and team_id in MLB_TEAMS:
                    code = MLB_TEAMS[team_id][0]
                    team_max_round[code] = max(team_max_round.get(code, 0), rval)

    # Convert max round reached to exit round
    # If a team reached round R and didn't win the WS, they lost at round R
    for code, max_r in team_max_round.items():
        exits[code] = max_r  # exit = the round they reached (they lost there)

    return exits


# ---------------------------------------------------------------------------
# NHL — api-web.nhle.com
# ---------------------------------------------------------------------------

NHL_TEAMS = {
    "ANA": ("ANA", "Anaheim Ducks",           "Anaheim",       1993),
    "BOS": ("BOS", "Boston Bruins",           "Boston",        1924),
    "BUF": ("BUF", "Buffalo Sabres",          "Buffalo",       1970),
    "CGY": ("CGY", "Calgary Flames",          "Calgary",       1972),
    "CAR": ("CAR", "Carolina Hurricanes",     "Raleigh",       1972),
    "CHI": ("CHI", "Chicago Blackhawks",      "Chicago",       1926),
    "COL": ("COL", "Colorado Avalanche",      "Denver",        1972),
    "CBJ": ("CBJ", "Columbus Blue Jackets",   "Columbus",      2000),
    "DAL": ("DAL", "Dallas Stars",            "Dallas",        1967),
    "DET": ("DET", "Detroit Red Wings",       "Detroit",       1926),
    "EDM": ("EDM", "Edmonton Oilers",         "Edmonton",      1979),
    "FLA": ("FLA", "Florida Panthers",        "Sunrise",       1993),
    "LAK": ("LAK", "Los Angeles Kings",       "Los Angeles",   1967),
    "MIN": ("MIN", "Minnesota Wild",          "Minneapolis",   2000),
    "MTL": ("MTL", "Montreal Canadiens",      "Montreal",      1909),
    "NSH": ("NSH", "Nashville Predators",     "Nashville",     1998),
    "NJD": ("NJD", "New Jersey Devils",       "Newark",        1974),
    "NYI": ("NYI", "New York Islanders",      "Elmont",        1972),
    "NYR": ("NYR", "New York Rangers",        "New York",      1926),
    "OTT": ("OTT", "Ottawa Senators",         "Ottawa",        1992),
    "PHI": ("PHI", "Philadelphia Flyers",     "Philadelphia",  1967),
    "PIT": ("PIT", "Pittsburgh Penguins",     "Pittsburgh",    1967),
    "STL": ("STL", "St. Louis Blues",         "St. Louis",     1967),
    "SJS": ("SJS", "San Jose Sharks",         "San Jose",      1991),
    "SEA": ("SEA", "Seattle Kraken",          "Seattle",       2021),
    "TBL": ("TBL", "Tampa Bay Lightning",     "Tampa",         1992),
    "TOR": ("TOR", "Toronto Maple Leafs",     "Toronto",       1917),
    "UTA": ("UTA", "Utah Hockey Club",        "Salt Lake City",2024),
    "VAN": ("VAN", "Vancouver Canucks",       "Vancouver",     1970),
    "VGK": ("VGK", "Vegas Golden Knights",    "Las Vegas",     2017),
    "WSH": ("WSH", "Washington Capitals",     "Washington",    1974),
    "WPG": ("WPG", "Winnipeg Jets",           "Winnipeg",      1999),
}

NHL_CHAMPIONSHIPS = {
    "ANA": [2007],
    "BOS": [1929,1939,1941,1970,1972,2011],
    "BUF": [],
    "CGY": [1989],
    "CAR": [2006],
    "CHI": [1934,1938,1961,2010,2013,2015],
    "COL": [1996,2001,2022],
    "CBJ": [],
    "DAL": [1999],
    "DET": [1936,1937,1943,1950,1952,1954,1955,1997,1998,2002,2008],
    "EDM": [1984,1985,1987,1988,1990],
    "FLA": [2024],
    "LAK": [2012,2014],
    "MIN": [],
    "MTL": [1916,1924,1930,1931,1944,1946,1953,1956,1957,1958,1959,1960,1965,1966,1968,1969,1971,1973,1976,1977,1978,1979,1986,1993],
    "NSH": [],
    "NJD": [1995,2000,2003],
    "NYI": [1980,1981,1982,1983],
    "NYR": [1928,1933,1940,1994],
    "OTT": [],
    "PHI": [1974,1975],
    "PIT": [1991,1992,2009,2016,2017],
    "STL": [2019],
    "SJS": [],
    "SEA": [],
    "TBL": [2004,2020,2021],
    "TOR": [1918,1922,1932,1942,1945,1947,1948,1949,1951,1962,1963,1964,1967],
    "UTA": [],
    "VAN": [],
    "VGK": [2023],
    "WSH": [2018],
    "WPG": [],
}

NHL_FINALS_LOSSES = {
    "ANA": [2003],
    "BOS": [1930,1943,1946,1953,1957,1958,1974,1977,1978,1988,1990,2013],
    "BUF": [1975,1999],
    "CGY": [1986,2004],
    "CAR": [2002,2009,2019],
    "CHI": [1931,1944,1971,1973,1992],
    "COL": [2001],  # already a champ, but 1994 loss as Nordiques not tracked
    "CBJ": [],
    "DAL": [2000],
    "DET": [1934,1942,1945,1948,1956,1961,1963,1964,1966,1995,2009],
    "EDM": [1983,2006],
    "FLA": [1996,2023],
    "LAK": [1993],
    "MIN": [],
    "MTL": [1947,1952,1954,1955,1967,1989],
    "NSH": [2017],
    "NJD": [2001],
    "NYI": [1975],
    "NYR": [1950,1972,1979,1992],
    "OTT": [1927],
    "PHI": [1976,1980,1985,1987,1997],
    "PIT": [1990,1993,2008],
    "STL": [1968,1969,1970],
    "SJS": [2016],
    "SEA": [],
    "TBL": [2015],
    "TOR": [],
    "UTA": [],
    "VAN": [1982,1994,2011],
    "VGK": [2018],
    "WSH": [1998],
    "WPG": [],
}


def fetch_nhl(since_year=1970):
    print("\n=== NHL ===")
    existing = load_existing("nhl")
    teams_out = {}

    for code, (_, name, city, founded) in NHL_TEAMS.items():
        teams_out[code] = {
            "id": code, "name": name, "city": city,
            "founded": founded, "league": "NHL",
            "championships": NHL_CHAMPIONSHIPS.get(code, []),
            "finals_losses": NHL_FINALS_LOSSES.get(code, []),
            "seasons": {},
        }
        if existing and code in existing.get("teams", {}):
            for yr, s in existing["teams"][code]["seasons"].items():
                if int(yr) < since_year:
                    teams_out[code]["seasons"][yr] = s

    end_year = CURRENT_YEAR - 1

    for season in range(since_year, end_year + 1):
        # NHL season ID format: 20232024 for the 2023-24 season
        season_id = f"{season}{season+1}"
        print(f"  NHL {season}-{season+1}...", end=" ", flush=True)

        # Lockout seasons with no games
        if season == 2004:  # 2004-05 lockout
            print("LOCKOUT — skip")
            for code in teams_out:
                teams_out[code]["seasons"][str(season)] = None
            continue

        url = f"https://api-web.nhle.com/v1/standings/{season+1}-02-01"
        try:
            data = fetch_json(url)
            time.sleep(RATE_LIMIT_DELAY)
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        standings = data.get("standings", [])
        season_records = {}

        for entry in standings:
            abbrev = entry.get("teamAbbrev", {})
            if isinstance(abbrev, dict):
                abbrev = abbrev.get("default", "")
            # Normalize abbreviations
            abbrev = normalize_nhl_abbrev(abbrev, season)
            if abbrev not in NHL_TEAMS:
                continue
            w  = entry.get("wins", 0)
            l  = entry.get("losses", 0)
            ot = entry.get("otLosses", 0)
            gp = entry.get("gamesPlayed", w + l + ot)
            season_records[abbrev] = {"w": w, "l": l + ot, "t": 0, "g": gp}

        # Get playoff results
        playoff_exits = fetch_nhl_playoffs(season)
        time.sleep(RATE_LIMIT_DELAY)

        for code, rec in season_records.items():
            champs   = teams_out[code]["championships"]
            finals_l = teams_out[code]["finals_losses"]

            if season in champs:
                exit_round, playoffs = 5, True
            elif season in finals_l:
                exit_round, playoffs = 4, True
            elif code in playoff_exits:
                exit_round, playoffs = playoff_exits[code], True
            else:
                exit_round, playoffs = 0, False

            teams_out[code]["seasons"][str(season)] = {
                "w": rec["w"], "l": rec["l"], "t": rec["t"],
                "g": rec["g"], "playoffs": playoffs, "exit": exit_round,
            }

        print(f"OK ({len(season_records)} teams)")

    save_league("nhl", {"league": "NHL", "teams": teams_out})


def normalize_nhl_abbrev(abbrev, season):
    """Handle franchise relocations and name changes."""
    remap = {
        "PHX": "ARI",  # Phoenix -> Arizona
        "ATL": "WPG",  # Atlanta Thrashers -> Winnipeg Jets (2011)
        "HFD": "CAR",  # Hartford Whalers -> Carolina
        "QUE": "COL",  # Quebec Nordiques -> Colorado
        "MNS": "DAL",  # Minnesota North Stars -> Dallas
        "WST": "WSH",
        "S.J": "SJS",
        "N.J": "NJD",
        "T.B": "TBL",
        "L.A": "LAK",
    }
    return remap.get(abbrev, abbrev)


def fetch_nhl_playoffs(season):
    """Get playoff exit rounds from the NHL API bracket."""
    exits = {}
    url = f"https://api-web.nhle.com/v1/playoff-bracket/{season+1}"
    try:
        data = fetch_json(url)
    except Exception:
        return exits

    # Parse rounds — track highest round each team reached and whether they won
    rounds = data.get("rounds", [])
    for rnd in rounds:
        rnd_num = rnd.get("roundNumber", 0)
        for series in rnd.get("series", []):
            top = series.get("topSeedTeam", {})
            bot = series.get("bottomSeedTeam", {})

            top_code = normalize_nhl_abbrev(top.get("abbrev", ""), season)
            bot_code = normalize_nhl_abbrev(bot.get("abbrev", ""), season)
            top_wins = top.get("wins", 0)
            bot_wins = bot.get("wins", 0)

            for code, wins, opp_wins in [(top_code, top_wins, bot_wins), (bot_code, bot_wins, top_wins)]:
                if code not in NHL_TEAMS:
                    continue
                # They reached this round — mark exit if they lost
                if opp_wins > wins:
                    exits[code] = rnd_num

    return exits


# ---------------------------------------------------------------------------
# NBA — stats.nba.com
# ---------------------------------------------------------------------------

NBA_TEAMS = {
    1610612737: ("ATL", "Atlanta Hawks",           "Atlanta",       1946),
    1610612738: ("BOS", "Boston Celtics",          "Boston",        1946),
    1610612751: ("BKN", "Brooklyn Nets",           "Brooklyn",      1976),
    1610612766: ("CHA", "Charlotte Hornets",       "Charlotte",     1988),
    1610612741: ("CHI", "Chicago Bulls",           "Chicago",       1966),
    1610612739: ("CLE", "Cleveland Cavaliers",     "Cleveland",     1970),
    1610612742: ("DAL", "Dallas Mavericks",        "Dallas",        1980),
    1610612743: ("DEN", "Denver Nuggets",          "Denver",        1976),
    1610612765: ("DET", "Detroit Pistons",         "Detroit",       1941),
    1610612744: ("GSW", "Golden State Warriors",   "San Francisco", 1946),
    1610612745: ("HOU", "Houston Rockets",         "Houston",       1967),
    1610612754: ("IND", "Indiana Pacers",          "Indianapolis",  1967),
    1610612746: ("LAC", "Los Angeles Clippers",    "Los Angeles",   1970),
    1610612747: ("LAL", "Los Angeles Lakers",      "Los Angeles",   1947),
    1610612763: ("MEM", "Memphis Grizzlies",       "Memphis",       1995),
    1610612748: ("MIA", "Miami Heat",              "Miami",         1988),
    1610612749: ("MIL", "Milwaukee Bucks",         "Milwaukee",     1968),
    1610612750: ("MIN", "Minnesota Timberwolves",  "Minneapolis",   1989),
    1610612740: ("NOP", "New Orleans Pelicans",    "New Orleans",   2002),
    1610612752: ("NYK", "New York Knicks",         "New York",      1946),
    1610612760: ("OKC", "Oklahoma City Thunder",   "Oklahoma City", 1967),
    1610612753: ("ORL", "Orlando Magic",           "Orlando",       1989),
    1610612755: ("PHI", "Philadelphia 76ers",      "Philadelphia",  1946),
    1610612756: ("PHX", "Phoenix Suns",            "Phoenix",       1968),
    1610612757: ("POR", "Portland Trail Blazers",  "Portland",      1970),
    1610612758: ("SAC", "Sacramento Kings",        "Sacramento",    1945),
    1610612759: ("SAS", "San Antonio Spurs",       "San Antonio",   1967),
    1610612761: ("TOR", "Toronto Raptors",         "Toronto",       1995),
    1610612762: ("UTA", "Utah Jazz",               "Salt Lake City",1974),
    1610612764: ("WAS", "Washington Wizards",      "Washington",    1961),
}

NBA_CHAMPIONSHIPS = {
    "ATL": [1958],
    "BOS": [1957,1959,1960,1961,1962,1963,1964,1965,1966,1968,1969,1974,1976,1981,1984,1986,2008,2024],
    "BKN": [],
    "CHA": [],
    "CHI": [1991,1992,1993,1996,1997,1998],
    "CLE": [2016],
    "DAL": [2011],
    "DEN": [2023],
    "DET": [1989,1990,2004],
    "GSW": [1947,1956,1975,2015,2017,2018,2022],
    "HOU": [1994,1995],
    "IND": [],
    "LAC": [],
    "LAL": [1949,1950,1952,1953,1954,1972,1980,1982,1985,1987,1988,2000,2001,2002,2009,2010,2020],
    "MEM": [],
    "MIA": [2006,2012,2013],
    "MIL": [1971,2021],
    "MIN": [],
    "NOP": [],
    "NYK": [1970,1973],
    "OKC": [],
    "ORL": [],
    "PHI": [1955,1967,1983],
    "PHX": [],
    "POR": [1977],
    "SAC": [1951],
    "SAS": [1999,2003,2005,2007,2014],
    "TOR": [2019],
    "UTA": [],
    "WAS": [1978],
}

NBA_FINALS_LOSSES = {
    "ATL": [1957,1960,1961],
    "BOS": [1958,1985,1987,2010],
    "BKN": [],
    "CHA": [],
    "CHI": [],
    "CLE": [2007,2015,2017,2018],
    "DAL": [2006],
    "DEN": [],
    "DET": [1988,2005],
    "GSW": [1964,2016,2019],
    "HOU": [1981,1986,1994],
    "IND": [2000],
    "LAC": [],
    "LAL": [1959,1962,1963,1965,1966,1968,1969,1970,1973,1983,1984,1989,2004,2008],
    "MEM": [],
    "MIA": [1997,2011,2014,2020],
    "MIL": [1974],
    "MIN": [],
    "NOP": [],
    "NYK": [1951,1952,1953,1972,1994,1999],
    "OKC": [2012],
    "ORL": [1995],
    "PHI": [1948,1950,1977,1980,1982,2001],
    "PHX": [1976,1993,2021],
    "POR": [1990,1992],
    "SAC": [],
    "SAS": [1994],
    "TOR": [],
    "UTA": [1997,1998],
    "WAS": [1979],
}


def fetch_nba(since_year=1970):
    print("\n=== NBA ===")
    existing = load_existing("nba")
    teams_out = {}

    for nba_id, (code, name, city, founded) in NBA_TEAMS.items():
        teams_out[code] = {
            "id": code, "name": name, "city": city,
            "founded": founded, "league": "NBA",
            "championships": NBA_CHAMPIONSHIPS.get(code, []),
            "finals_losses": NBA_FINALS_LOSSES.get(code, []),
            "seasons": {},
        }
        if existing and code in existing.get("teams", {}):
            for yr, s in existing["teams"][code]["seasons"].items():
                if int(yr) < since_year:
                    teams_out[code]["seasons"][yr] = s

    end_year = CURRENT_YEAR - 1
    nba_headers = {
        "Referer": "https://www.nba.com/",
        "Origin":  "https://www.nba.com",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
    }

    for season in range(since_year, end_year + 1):
        # NBA season ID: "2023-24" for the 2023-24 season
        season_str = f"{season}-{str(season+1)[-2:]}"
        print(f"  NBA {season_str}...", end=" ", flush=True)

        # Shortened seasons
        gp_expected = 82
        if season == 2011: gp_expected = 66
        if season == 2019: gp_expected = 72  # COVID shortened
        if season == 2020: gp_expected = 72

        url = (f"https://stats.nba.com/stats/leaguestandings?"
               f"LeagueID=00&Season={season_str}&SeasonType=Regular+Season")
        try:
            data = fetch_json(url, headers=nba_headers, timeout=5, retries=1)
            time.sleep(RATE_LIMIT_DELAY)
        except Exception as e:
            print(f"ESPN fallback", end=" ", flush=True)
            try:
                espn_records = fetch_nba_espn_season(season)
            except Exception:
                espn_records = {}
            if espn_records:
                _apply_nba_season(teams_out, espn_records, {}, season)
                print(f"OK via ESPN ({len(espn_records)} teams)")
            else:
                print(f"SKIP (no data)")
            continue

        # Parse NBA stats API response
        result_sets = data.get("resultSets", [])
        if not result_sets:
            print("No data")
            continue

        headers_row = result_sets[0].get("headers", [])
        rows        = result_sets[0].get("rowSet", [])

        # Find column indices
        def col(name):
            try: return headers_row.index(name)
            except ValueError: return None

        team_col = col("TeamID")
        w_col    = col("WINS")
        l_col    = col("LOSSES")

        season_records = {}
        for row in rows:
            nba_id = row[team_col] if team_col is not None else None
            if nba_id not in NBA_TEAMS:
                continue
            code = NBA_TEAMS[nba_id][0]
            w = row[w_col] if w_col is not None else 0
            l = row[l_col] if l_col is not None else 0
            season_records[code] = {"w": w, "l": l, "g": w + l}

        # Get playoff exits
        playoff_exits = fetch_nba_playoffs(season)
        time.sleep(RATE_LIMIT_DELAY)

        _apply_nba_season(teams_out, season_records, playoff_exits, season)
        print(f"OK ({len(season_records)} teams)")

    save_league("nba", {"league": "NBA", "teams": teams_out})


def _apply_nba_season(teams_out, season_records, playoff_exits, season):
    for code, rec in season_records.items():
        if code not in teams_out:
            continue
        champs   = teams_out[code]["championships"]
        finals_l = teams_out[code]["finals_losses"]

        if season in champs:
            exit_round, playoffs = 5, True
        elif season in finals_l:
            exit_round, playoffs = 4, True
        elif code in playoff_exits:
            exit_round, playoffs = playoff_exits[code], True
        else:
            exit_round, playoffs = 0, False

        teams_out[code]["seasons"][str(season)] = {
            "w": rec["w"], "l": rec["l"], "t": 0,
            "g": rec.get("g", rec["w"] + rec["l"]),
            "playoffs": playoffs, "exit": exit_round,
        }


def fetch_nba_espn_season(season):
    """Fallback: ESPN standings for NBA season."""
    url = f"https://site.api.espn.com/apis/v2/sports/basketball/nba/standings?season={season+1}"
    try:
        data = fetch_json(url)
    except Exception:
        return {}

    records = {}
    for group in data.get("children", []):
        for entry in group.get("standings", {}).get("entries", []):
            team_abbrev = entry.get("team", {}).get("abbreviation", "")
            code = normalize_nba_abbrev(team_abbrev)
            stats = {s["name"]: s.get("value", s.get("displayValue", 0)) for s in entry.get("stats", [])}
            w = int(stats.get("wins", 0))
            l = int(stats.get("losses", 0))
            if code:
                records[code] = {"w": w, "l": l, "g": w + l}
    return records


def fetch_nba_playoffs(season):
    """Get playoff exit rounds via ESPN bracket."""
    exits = {}
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?seasontype=3&season={season+1}"
    try:
        data = fetch_json(url)
    except Exception:
        return exits

    # Parse playoff series results
    team_max_round = {}
    for event in data.get("events", []):
        round_num = event.get("season", {}).get("slug", "")
        # Approximate round from event name
        name = event.get("name", "").lower()
        if "first round" in name or "wild card" in name:
            rval = 1
        elif "second round" in name or "conference semifinal" in name:
            rval = 2
        elif "conference final" in name:
            rval = 3
        elif "final" in name:
            rval = 4
        else:
            continue

        for comp in event.get("competitions", [{}]):
            for competitor in comp.get("competitors", []):
                abbrev = competitor.get("team", {}).get("abbreviation", "")
                code   = normalize_nba_abbrev(abbrev)
                winner = competitor.get("winner", False)
                if code:
                    team_max_round[code] = max(team_max_round.get(code, 0), rval)

    for code, max_r in team_max_round.items():
        exits[code] = max_r

    return exits


def normalize_nba_abbrev(abbrev):
    """Map ESPN abbreviations to our codes."""
    remap = {
        "GS":  "GSW",
        "SA":  "SAS",
        "NO":  "NOP",
        "NY":  "NYK",
        "NJ":  "BKN",
        "NJN": "BKN",
        "WSH": "WAS",
        "SEA": "OKC",
        "VAN": "MEM",
        "NOH": "NOP",
        "NOK": "NOP",
        "CHA": "CHA",
        "CHH": "CHA",
        "UTH": "UTA",
    }
    return remap.get(abbrev, abbrev)


# ---------------------------------------------------------------------------
# NFL — site.api.espn.com
# ---------------------------------------------------------------------------

NFL_TEAMS = {
    "ARI": ("ARI", "Arizona Cardinals",      "Glendale",      1920),
    "ATL": ("ATL", "Atlanta Falcons",        "Atlanta",       1966),
    "BAL": ("BAL", "Baltimore Ravens",       "Baltimore",     1996),
    "BUF": ("BUF", "Buffalo Bills",          "Buffalo",       1960),
    "CAR": ("CAR", "Carolina Panthers",      "Charlotte",     1995),
    "CHI": ("CHI", "Chicago Bears",          "Chicago",       1920),
    "CIN": ("CIN", "Cincinnati Bengals",     "Cincinnati",    1968),
    "CLE": ("CLE", "Cleveland Browns",       "Cleveland",     1950),
    "DAL": ("DAL", "Dallas Cowboys",         "Arlington",     1960),
    "DEN": ("DEN", "Denver Broncos",         "Denver",        1960),
    "DET": ("DET", "Detroit Lions",          "Detroit",       1930),
    "GB":  ("GB",  "Green Bay Packers",      "Green Bay",     1919),
    "HOU": ("HOU", "Houston Texans",         "Houston",       2002),
    "IND": ("IND", "Indianapolis Colts",     "Indianapolis",  1953),
    "JAX": ("JAX", "Jacksonville Jaguars",   "Jacksonville",  1995),
    "KC":  ("KC",  "Kansas City Chiefs",     "Kansas City",   1960),
    "LAC": ("LAC", "Los Angeles Chargers",   "Los Angeles",   1960),
    "LAR": ("LAR", "Los Angeles Rams",       "Los Angeles",   1936),
    "LV":  ("LV",  "Las Vegas Raiders",      "Las Vegas",     1960),
    "MIA": ("MIA", "Miami Dolphins",         "Miami Gardens", 1966),
    "MIN": ("MIN", "Minnesota Vikings",      "Minneapolis",   1961),
    "NE":  ("NE",  "New England Patriots",   "Foxborough",    1960),
    "NO":  ("NO",  "New Orleans Saints",     "New Orleans",   1967),
    "NYG": ("NYG", "New York Giants",        "East Rutherford",1925),
    "NYJ": ("NYJ", "New York Jets",          "East Rutherford",1960),
    "PHI": ("PHI", "Philadelphia Eagles",    "Philadelphia",  1933),
    "PIT": ("PIT", "Pittsburgh Steelers",    "Pittsburgh",    1933),
    "SEA": ("SEA", "Seattle Seahawks",       "Seattle",       1976),
    "SF":  ("SF",  "San Francisco 49ers",    "Santa Clara",   1946),
    "TB":  ("TB",  "Tampa Bay Buccaneers",   "Tampa",         1976),
    "TEN": ("TEN", "Tennessee Titans",       "Nashville",     1960),
    "WAS": ("WAS", "Washington Commanders",  "Landover",      1932),
}

NFL_CHAMPIONSHIPS = {
    "ARI": [1925, 1947],
    "ATL": [],
    "BAL": [2000, 2012],
    "BUF": [],
    "CAR": [],
    "CHI": [1921,1932,1933,1940,1941,1943,1946,1963],
    "CIN": [],
    "CLE": [1950,1954,1955,1964],
    "DAL": [1971,1977,1992,1993,1995],
    "DEN": [1997,1998,2015],
    "DET": [1935,1952,1953,1957],
    "GB":  [1929,1930,1931,1936,1939,1944,1961,1962,1965,1966,1967,1996,2010],
    "HOU": [],
    "IND": [1958,1959,1968,2006],
    "JAX": [],
    "KC":  [1969,2019,2022,2023],
    "LAC": [],
    "LAR": [1945,1951,1999,2021],
    "LV":  [1976,1980,1983],
    "MIA": [1972,1973],
    "MIN": [],
    "NE":  [2001,2003,2004,2014,2016,2018],
    "NO":  [2009],
    "NYG": [1927,1934,1938,1944,1956,1986,1990,2007,2011],
    "NYJ": [1968],
    "PHI": [1948,1949,1960,2017,2024],
    "PIT": [1974,1975,1978,1979,2005,2008],
    "SEA": [2013, 2025],
    "SF":  [1981,1984,1988,1989,1994],
    "TB":  [2002,2020],
    "TEN": [],
    "WAS": [1937,1942,1982,1987,1991],
}

NFL_FINALS_LOSSES = {
    "ARI": [2008, 2023],
    "ATL": [1998, 2016],
    "BAL": [1968, 1969],
    "BUF": [1990, 1991, 1992, 1993],
    "CAR": [2003, 2015],
    "CHI": [1934, 1937, 1942, 1956, 1985],
    "CIN": [1981, 1988, 2021],
    "CLE": [],
    "DAL": [1970, 1975, 1978],
    "DEN": [1977, 1986, 1987, 1989, 2013],
    "DET": [1954],
    "GB":  [1960, 1997, 2010],
    "HOU": [],
    "IND": [1964, 1995, 2009],
    "JAX": [],
    "KC":  [1966, 2020, 2024],
    "LAC": [1994],
    "LAR": [1979, 2001, 2018],
    "LV":  [2002],
    "MIA": [1971, 1982, 1984],
    "MIN": [1969, 1973, 1974, 1976],
    "NE":  [1985, 1996, 2011, 2017, 2025],
    "NO":  [],
    "NYG": [1933, 1935, 1939, 1941, 1944, 1958, 1959, 1961, 1962, 1963],
    "NYJ": [],
    "PHI": [1947, 2004, 2022],
    "PIT": [1994, 1995],
    "SEA": [2005, 2014],
    "SF":  [2012, 2019, 2023],
    "TB":  [1979],
    "TEN": [1999],
    "WAS": [1936, 1945],
}


def fetch_nfl(since_year=1970):
    print("\n=== NFL ===")
    existing = load_existing("nfl")
    teams_out = {}

    for code, (_, name, city, founded) in NFL_TEAMS.items():
        teams_out[code] = {
            "id": code, "name": name, "city": city,
            "founded": founded, "league": "NFL",
            "championships": NFL_CHAMPIONSHIPS.get(code, []),
            "finals_losses": NFL_FINALS_LOSSES.get(code, []),
            "seasons": {},
        }
        if existing and code in existing.get("teams", {}):
            for yr, s in existing["teams"][code]["seasons"].items():
                if int(yr) < since_year:
                    teams_out[code]["seasons"][yr] = s

    end_year = CURRENT_YEAR - 1

    for season in range(since_year, end_year + 1):
        print(f"  NFL {season}...", end=" ", flush=True)
        url = f"https://site.api.espn.com/apis/v2/sports/football/nfl/standings?season={season}"
        try:
            data = fetch_json(url)
            time.sleep(RATE_LIMIT_DELAY)
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        season_records = {}
        for group in data.get("children", []):
            for entry in group.get("standings", {}).get("entries", []):
                abbrev = entry.get("team", {}).get("abbreviation", "")
                code   = normalize_nfl_abbrev(abbrev, season)
                stats  = {s["name"]: s.get("value", 0) for s in entry.get("stats", [])}
                w = int(stats.get("wins", 0))
                l = int(stats.get("losses", 0))
                t = int(stats.get("ties", 0))
                # Games played
                g = 16
                if season >= 2021: g = 17
                elif season < 1978: g = 14
                if code:
                    season_records[code] = {"w": w, "l": l, "t": t, "g": g}

        # Playoff exits
        playoff_exits = fetch_nfl_playoffs(season, teams_out)
        time.sleep(RATE_LIMIT_DELAY)

        for code, rec in season_records.items():
            if code not in teams_out:
                continue
            champs   = teams_out[code]["championships"]
            finals_l = teams_out[code]["finals_losses"]

            if season in champs:
                exit_round, playoffs = 5, True
            elif season in finals_l:
                exit_round, playoffs = 4, True
            elif code in playoff_exits:
                exit_round, playoffs = playoff_exits[code], True
            else:
                exit_round, playoffs = 0, False

            teams_out[code]["seasons"][str(season)] = {
                "w": rec["w"], "l": rec["l"], "t": rec["t"],
                "g": rec["g"], "playoffs": playoffs, "exit": exit_round,
            }

        print(f"OK ({len(season_records)} teams)")

    save_league("nfl", {"league": "NFL", "teams": teams_out})


# Seasons where ESPN data is wrong — these completely replace the API response.
# Champion and SB loser are handled via championships/finals_losses lists (exit 5/4).
# Format: { season_year: { team_code: exit_round } }
NFL_PLAYOFF_FULL_REPLACE = {
    # Super Bowl LIX: PHI beat KC. ESPN returns wrong bracket for this season.
    2024: {
        "PHI": 4, "KC":  4,           # SB teams (5/4 overridden by champ/finals lists)
        "BUF": 3, "WAS": 3,           # Conference final losers
        "BAL": 2, "HOU": 2, "DET": 2, "LAR": 2,  # Divisional losers
        "LAC": 1, "DEN": 1, "PIT": 1, "MIN": 1, "TB": 1, "GB": 1,  # Wild card losers
    },
}

# Teams ESPN's postseason standings silently omit — merged on top of API results.
# Format: { season_year: { team_code: exit_round } }
NFL_PLAYOFF_OVERRIDES = {
    # Browns beat PIT in WC, lost to KC in Divisional
    2020: {"CLE": 2},
}

def fetch_nfl_playoffs(season, teams_out):
    """
    Get NFL playoff exit rounds via ESPN postseason standings.
    The standings endpoint returns every playoff team with their playoff W-L.
    Playoff wins map to exit round:
      0 wins = Wild Card loss  -> exit 1
      1 win  = Divisional loss -> exit 2
      2 wins = Conf Final loss -> exit 3
      3 wins = Super Bowl loss -> exit 4  (champion overridden by championships list -> 5)
      4 wins = Champion        -> exit 5  (handled via championships list)
    """
    exits = {}

    # Use hardcoded data if ESPN's response is known to be wrong for this season
    if season in NFL_PLAYOFF_FULL_REPLACE:
        exits = {k: v for k, v in NFL_PLAYOFF_FULL_REPLACE[season].items() if k in teams_out}
        for code, exit_round in NFL_PLAYOFF_OVERRIDES.get(season, {}).items():
            if code in teams_out:
                exits[code] = exit_round
        if exits:
            print(f"      playoff teams (hardcoded): {sorted(exits.keys())}")
        return exits

    url = (
        f"https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
        f"?season={season+1}&seasontype=3"
    )
    try:
        data = fetch_json(url)
    except Exception as e:
        print(f"      playoff standings err: {e}")
        return exits

    for conf in data.get("children", []):
        for entry in conf.get("standings", {}).get("entries", []):
            abbrev = entry.get("team", {}).get("abbreviation", "")
            code   = normalize_nfl_abbrev(abbrev, season)
            if not code or code not in teams_out:
                continue
            stats  = entry.get("stats", [])
            wins   = next((int(s["value"]) for s in stats if s["name"] == "wins"),        None)
            losses = next((int(s["value"]) for s in stats if s["name"] == "losses"),      None)
            seed   = next((s["value"]      for s in stats if s["name"] == "playoffSeed"), None)

            if wins is None or losses is None:
                continue
            # ESPN includes all teams in older postseason standings with 0-0 records.
            # A real playoff team must have played at least one game (wins+losses >= 1)
            # and have a playoff seed.
            if (wins + losses) < 1 or seed is None:
                continue

            if wins == 0:
                exit_round = 1
            elif wins == 1:
                exit_round = 2
            elif wins == 2:
                exit_round = 3
            else:
                exit_round = 4  # SB loser; champion overridden by championships list
            exits[code] = exit_round

    # Apply manual overrides for teams ESPN omits
    for code, exit_round in NFL_PLAYOFF_OVERRIDES.get(season, {}).items():
        if code in teams_out:
            exits[code] = exit_round

    if exits:
        print(f"      playoff teams: {sorted(exits.keys())}")
    return exits


def normalize_nfl_abbrev(abbrev, season):
    """Handle team relocations and rebrands."""
    remap = {
        "OAK": "LV",   # Oakland Raiders -> Las Vegas
        "SD":  "LAC",  # San Diego -> LA Chargers
        "STL": "LAR",  # St. Louis -> LA Rams
        "HST": "HOU",
        "JAC": "JAX",
        "WSH": "WAS",
        "SL":  "LAR",
    }
    return remap.get(abbrev, abbrev)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Fetch live sports data")
    parser.add_argument("--league", choices=["mlb","nhl","nba","nfl","all"], default="all")
    parser.add_argument("--since",  type=int, default=None,
                        help="Only fetch seasons from this year onward (default: full history)")
    args = parser.parse_args()

    print(f"Sports Misery Data Fetcher")
    print(f"Saving to: {DATA_DIR.resolve()}")
    print(f"Current year: {CURRENT_YEAR}")

    leagues = [args.league] if args.league != "all" else ["mlb", "nhl", "nba", "nfl"]

    for league in leagues:
        since = args.since
        if league == "mlb":
            fetch_mlb(since_year=since or 1969)
        elif league == "nhl":
            fetch_nhl(since_year=since or 1970)
        elif league == "nba":
            fetch_nba(since_year=since or 1970)
        elif league == "nfl":
            fetch_nfl(since_year=since or 1970)

    print("\nDone. Restart main.py to load the updated data.")


if __name__ == "__main__":
    main()
