"""
Sports Misery Calculator - Tornado Web Server
Run: python main.py [--port 8000]
"""

import json
import os
import argparse
from pathlib import Path

import tornado.ioloop
import tornado.web

from scoring import calculate_team_misery, calculate_overall_misery, misery_label
from percentile import get_percentile, load_or_build_cache

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"
LEAGUE_DATA = {}


def load_data():
    for league in ["nfl", "nba", "mlb", "nhl"]:
        fpath = DATA_DIR / f"{league}.json"
        if fpath.exists():
            with open(fpath) as f:
                LEAGUE_DATA[league.upper()] = json.load(f)
            print(f"  Loaded {league.upper()}: {len(LEAGUE_DATA[league.upper()]['teams'])} teams")
        else:
            print(f"  WARNING: {fpath} not found. Run: python generate_data.py")


# ---------------------------------------------------------------------------
# Base handler
# ---------------------------------------------------------------------------
class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")

    def options(self, *args):
        self.set_status(204)
        self.finish()

    def write_json(self, obj, status=200):
        self.set_status(status)
        self.write(json.dumps(obj))

    def write_error_json(self, status, detail):
        self.set_status(status)
        self.write(json.dumps({"error": detail}))

    def get_team(self, league, team_id):
        league_key = league.upper()
        if league_key not in LEAGUE_DATA:
            return None, f"League {league} not found"
        teams = LEAGUE_DATA[league_key].get("teams", {})
        if team_id not in teams:
            return None, f"Team {team_id} not found in {league}"
        return teams[team_id], None


# ---------------------------------------------------------------------------
# API handlers
# ---------------------------------------------------------------------------
class TeamsAllHandler(BaseHandler):
    def get(self):
        result = {}
        for league_key, data in LEAGUE_DATA.items():
            result[league_key] = sorted(
                [{"id": t["id"], "name": t["name"], "city": t["city"]}
                 for t in data["teams"].values()],
                key=lambda x: x["name"]
            )
        self.write_json(result)


class TeamsLeagueHandler(BaseHandler):
    def get(self, league):
        league_key = league.upper()
        if league_key not in LEAGUE_DATA:
            return self.write_error_json(404, f"League {league} not available")
        teams = LEAGUE_DATA[league_key]["teams"]
        self.write_json({
            "league": league_key,
            "teams": sorted(
                [{"id": t["id"], "name": t["name"], "city": t["city"]}
                 for t in teams.values()],
                key=lambda x: x["name"]
            )
        })


class CalculateHandler(BaseHandler):
    def post(self):
        try:
            body = json.loads(self.request.body)
        except Exception:
            return self.write_error_json(400, "Invalid JSON body")

        fan_start = body.get("fan_start_year")
        if not isinstance(fan_start, int) or fan_start < 1950 or fan_start > 2024:
            return self.write_error_json(400, "fan_start_year must be between 1950 and 2024")

        # Per-league start years — fall back to global fan_start if not provided
        league_starts = {
            "NFL": body.get("nfl_start_year") or fan_start,
            "NBA": body.get("nba_start_year") or fan_start,
            "MLB": body.get("mlb_start_year") or fan_start,
            "NHL": body.get("nhl_start_year") or fan_start,
        }

        selections = {
            "NFL": body.get("nfl_team"),
            "NBA": body.get("nba_team"),
            "MLB": body.get("mlb_team"),
            "NHL": body.get("nhl_team"),
        }

        team_results = []
        errors = []

        for league, team_id in selections.items():
            if not team_id:
                continue
            team_data, err = self.get_team(league, team_id)
            if err:
                errors.append({"league": league, "team": team_id, "error": err})
                continue
            result = calculate_team_misery(team_data, league_starts[league])
            if "error" not in result:
                # Strip verbose season_scores from response to keep payload small
                result_slim = {k: v for k, v in result.items() if k != "season_scores"}
                # Keep season scores for timeline but summarize
                result_slim["season_timeline"] = {
                    yr: {"score": s["total"], "base": s["base"],
                         "heartbreak_desc": s.get("heartbreak_desc")}
                    for yr, s in result["season_scores"].items()
                }
                # Compute regular season and postseason records from raw data
                effective_start = result["fan_start"]
                reg_w = reg_l = reg_t = 0
                post_w = post_l = 0
                for yr_str, s in team_data["seasons"].items():
                    if s is None or int(yr_str) < effective_start:
                        continue
                    reg_w += s.get("w", 0)
                    reg_l += s.get("l", 0)
                    reg_t += s.get("t", 0)
                result_slim["reg_record"] = {"w": reg_w, "l": reg_l, "t": reg_t}
                team_results.append(result_slim)
            else:
                errors.append({"league": league, "team": team_id, "error": result["error"]})

        if not team_results:
            return self.write_error_json(400, "No valid teams found. Select at least one team.")

        overall = calculate_overall_misery(team_results)
        total_score = overall["total_score"]
        num_teams = len(team_results)

        # Misery label
        total_seasons = sum(t.get("seasons_watched", 1) for t in team_results)
        label_data = misery_label(total_score, num_teams, total_seasons)

        # Percentile
        percentile_data = get_percentile(total_score, LEAGUE_DATA, fan_start, num_teams)

        self.write_json({
            "total_score": total_score,
            "label": label_data["label"],
            "emoji": label_data["emoji"],
            "percentile": percentile_data,
            "fan_start_year": fan_start,
            "team_results": overall["team_results"],
            "errors": errors,
        })


class TeamProfileHandler(BaseHandler):
    def get(self, league, team_id):
        fan_start = int(self.get_argument("fan_start", "1990"))
        team_data, err = self.get_team(league, team_id)
        if err:
            return self.write_error_json(404, err)
        result = calculate_team_misery(team_data, fan_start)
        self.write_json(result)


class HealthHandler(BaseHandler):
    def get(self):
        self.write_json({"status": "ok", "leagues_loaded": list(LEAGUE_DATA.keys())})


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------
STATIC_DIR = Path(__file__).parent / "static"


class FrontendHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/html")
        with open(STATIC_DIR / "index.html", "rb") as f:
            self.write(f.read())


def make_app():
    return tornado.web.Application([
        (r"/",                                      FrontendHandler),
        (r"/api/teams",                             TeamsAllHandler),
        (r"/api/teams/([a-zA-Z]+)",                 TeamsLeagueHandler),
        (r"/api/calculate",                         CalculateHandler),
        (r"/api/team/([a-zA-Z]+)/([A-Z0-9]+)",     TeamProfileHandler),
        (r"/api/health",                            HealthHandler),
        (r"/static/(.*)",                           tornado.web.StaticFileHandler,
         {"path": str(STATIC_DIR)}),
    ], debug=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    # Railway (and most PaaS) inject PORT as an env variable
    port = args.port or int(os.environ.get("PORT", 8000))

    print("Sports Misery Calculator")
    print("========================")
    print("Loading team data...")
    load_data()

    print("Building percentile reference population (first run may take ~10s)...")
    load_or_build_cache(LEAGUE_DATA)

    app = make_app()
    app.listen(port, address="0.0.0.0")
    print(f"\nServer running at http://0.0.0.0:{port}")
    print("Press Ctrl+C to stop.\n")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
