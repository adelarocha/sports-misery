# Sports Misery Index

A personalized sports suffering calculator for fans of NFL, NBA, MLB, and NHL teams.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate team data (one-time setup)
cd sports-misery
python generate_data.py

# 3. Start the server
uvicorn main:app --reload --port 8000

# 4. Open your browser
open http://localhost:8000
```

## How It Works

Enter your earliest sports memory year and select up to one team per league.
The app calculates a personalized Misery Index (0–100) across five dimensions:

| Dimension | Weight | What it measures |
|---|---|---|
| Championship Drought | 30% | Years since your team won a title (log scale) |
| Win-Loss Futility | 25% | How often your team loses vs. league average |
| Playoff Miss Rate | 20% | How frequently they miss the postseason |
| Playoff Exit Pain | 15% | How deep they go when they do make it |
| Heartbreak Factor | 10% | Curated iconic collapses and near-misses |

All dimensions apply **recency weighting** — recent seasons hurt more.

## Scores

| Score | Label |
|---|---|
| 85–100 | Legendary Suffering |
| 70–84 | Chronic Heartbreak |
| 55–69 | Perpetual Disappointment |
| 40–54 | Occasional Sadness |
| 25–39 | Pretty Lucky, Actually |
| 0–24 | Insufferable Winner |

## API

```
GET  /api/teams               # All teams by league
GET  /api/teams/{league}      # Teams for one league
POST /api/calculate           # Calculate misery index
GET  /api/team/{league}/{id}  # Single team profile
```

## Data

Historical season data is approximated from known performance eras and accurate
championship records. To refresh with real Sports-Reference data, see
`scripts/fetch_real_data.py` (run separately, requires internet access).

## Project Structure

```
sports-misery/
├── main.py          FastAPI backend + static file serving
├── scoring.py       Five-dimension misery scoring engine
├── generate_data.py Data generation from team era definitions
├── data/            Generated JSON files (auto-created)
├── static/
│   ├── index.html   Single-page frontend
│   └── app.js       Frontend JavaScript
└── requirements.txt
```
