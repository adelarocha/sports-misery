"""
Database module for Sports Misery Calculator leaderboard.
Uses PostgreSQL via psycopg2. Connection string read from DATABASE_URL env var.
"""
import os
import json
import psycopg2
import psycopg2.extras
from contextlib import contextmanager

DATABASE_URL = os.environ.get("DATABASE_URL", "")


def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return psycopg2.connect(DATABASE_URL, sslmode="require")


@contextmanager
def cursor():
    conn = get_conn()
    try:
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                yield cur
    finally:
        conn.close()


def init_db():
    """Create the leaderboard table if it doesn't exist."""
    with cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                id          SERIAL PRIMARY KEY,
                display_name TEXT NOT NULL,
                email       TEXT,
                score       INTEGER NOT NULL,
                teams       TEXT NOT NULL,
                fan_start   INTEGER NOT NULL,
                is_seed     BOOLEAN NOT NULL DEFAULT FALSE,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        # Index for fast rank queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS leaderboard_score_idx ON leaderboard(score DESC);
        """)
    print("DB: leaderboard table ready.")


def submit_entry(display_name: str, email: str, score: int,
                 teams: list, fan_start: int, is_seed: bool = False) -> dict:
    """
    Insert a new leaderboard entry.
    If email already exists (and is not seed), update their entry.
    Returns the row dict.
    """
    teams_str = json.dumps(teams)
    with cursor() as cur:
        if email and not is_seed:
            # Check if email already exists
            cur.execute("SELECT id FROM leaderboard WHERE email = %s LIMIT 1;", (email,))
            existing = cur.fetchone()
            if existing:
                cur.execute("""
                    UPDATE leaderboard
                    SET display_name = %s, score = %s, teams = %s,
                        fan_start = %s, created_at = NOW()
                    WHERE email = %s
                    RETURNING *;
                """, (display_name, score, teams_str, fan_start, email))
            else:
                cur.execute("""
                    INSERT INTO leaderboard (display_name, email, score, teams, fan_start, is_seed)
                    VALUES (%s, %s, %s, %s, %s, FALSE)
                    RETURNING *;
                """, (display_name, email, score, teams_str, fan_start))
        else:
            cur.execute("""
                INSERT INTO leaderboard (display_name, email, score, teams, fan_start, is_seed)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *;
            """, (display_name, email or None, score, teams_str, fan_start, is_seed))
        return dict(cur.fetchone())


def get_leaderboard(limit: int = 100) -> list:
    """Return top entries sorted by score DESC."""
    with cursor() as cur:
        cur.execute("""
            SELECT id, display_name, score, teams, fan_start, is_seed, created_at
            FROM leaderboard
            ORDER BY score DESC
            LIMIT %s;
        """, (limit,))
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def get_rank(score: int) -> dict:
    """
    Return rank (1-based, higher score = higher rank) and total count.
    """
    with cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM leaderboard;")
        total = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(*) AS above FROM leaderboard WHERE score > %s;", (score,))
        above = cur.fetchone()["above"]
    rank = above + 1  # 1-indexed; ties go to earlier entry
    return {"rank": rank, "total": total}


def has_seeded() -> bool:
    """Return True if seed entries are already in the DB."""
    with cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM leaderboard WHERE is_seed = TRUE;")
        return cur.fetchone()["n"] > 0


def clear_seed_entries() -> int:
    """Delete all seed entries. Returns number of rows deleted."""
    with cursor() as cur:
        cur.execute("DELETE FROM leaderboard WHERE is_seed = TRUE;")
        return cur.rowcount


def add_unique_email_constraint():
    """Attempt to add unique constraint on email for non-null values. Safe to call multiple times."""
    with cursor() as cur:
        try:
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS leaderboard_email_unique
                ON leaderboard (email)
                WHERE email IS NOT NULL;
            """)
        except Exception:
            pass  # already exists
