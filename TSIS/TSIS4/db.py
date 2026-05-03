import psycopg2
import config

_DB_AVAILABLE = True

def _connect():
    global _DB_AVAILABLE
    if not _DB_AVAILABLE:
        raise RuntimeError("Database marked unavailable for this session.")
    try:
        return psycopg2.connect(**config.DB_CONFIG)
    except psycopg2.OperationalError as exc:
        _DB_AVAILABLE = False
        raise RuntimeError(f"PostgreSQL connection failed: {exc}") from exc


def init_db() -> bool:
    
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        id       SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS game_sessions (
                        id            SERIAL  PRIMARY KEY,
                        player_id     INTEGER REFERENCES players(id),
                        score         INTEGER   NOT NULL,
                        level_reached INTEGER   NOT NULL,
                        played_at     TIMESTAMP DEFAULT NOW()
                    );
                """)
        return True
    except (RuntimeError, psycopg2.Error):
        return False


def get_or_create_player(username: str):
    """
    Look up a player by username, inserting a new row if not found.
    Returns the integer player_id, or None if the DB is unreachable.
    """
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                # check for existing player
                cur.execute(
                    "SELECT id FROM players WHERE username = %s",
                    (username,)
                )
                row = cur.fetchone()
                if row:
                    return row[0]

                # insert new player and return generated id
                cur.execute(
                    "INSERT INTO players (username) VALUES (%s) RETURNING id",
                    (username,)
                )
                return cur.fetchone()[0]
    except (RuntimeError, psycopg2.Error):
        return None


def save_session(player_id, score: int, level: int) -> bool:
    """
    Insert a game_sessions row for the finished run.
    Returns True on success, False if player_id is None or DB unavailable.
    """
    if player_id is None:
        return False
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO game_sessions "
                    "(player_id, score, level_reached) VALUES (%s, %s, %s)",
                    (player_id, score, level)
                )
        return True
    except (RuntimeError, psycopg2.Error):
        return False


def get_leaderboard() -> list:
    """
    Fetch the top-10 all-time scores from the database.
    Returns a list of (username, score, level_reached, date) tuples,
    or an empty list if the DB is unreachable.
    """
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT  p.username,
                            gs.score,
                            gs.level_reached,
                            gs.played_at::date
                    FROM    game_sessions gs
                    JOIN    players p ON gs.player_id = p.id
                    ORDER BY gs.score DESC
                    LIMIT   10
                """)
                return cur.fetchall()
    except (RuntimeError, psycopg2.Error):
        return []


def get_personal_best(username: str) -> int:
    """
    Return the player's all-time highest score, or 0 if none / DB unavailable.
    """
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT  MAX(gs.score)
                    FROM    game_sessions gs
                    JOIN    players p ON gs.player_id = p.id
                    WHERE   p.username = %s
                """, (username,))
                row = cur.fetchone()
                return int(row[0]) if row and row[0] is not None else 0
    except (RuntimeError, psycopg2.Error):
        return 0
