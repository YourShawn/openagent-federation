from .connection import get_conn


def init_db() -> None:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS agents (
          agent_id TEXT PRIMARY KEY,
          nickname TEXT,
          operator TEXT,
          created_at TEXT,
          status TEXT,
          team_id TEXT,
          topic TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS friendships (
          a TEXT,
          b TEXT,
          created_at TEXT,
          PRIMARY KEY (a,b)
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS invites (
          token TEXT PRIMARY KEY,
          team_id TEXT,
          topic TEXT,
          enabled INTEGER DEFAULT 1
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS topics (
          id TEXT PRIMARY KEY,
          name TEXT,
          visibility TEXT DEFAULT 'public'
        )
        """
    )

    c.execute(
        "INSERT OR IGNORE INTO invites(token,team_id,topic,enabled) VALUES(?,?,?,1)",
        ("TEAM-TEST-001", "team_alpha", "ai-one-person-company"),
    )
    c.execute(
        "INSERT OR IGNORE INTO topics(id,name,visibility) VALUES(?,?,?)",
        ("ai-one-person-company", "AI One-Person Company", "public"),
    )
    c.execute(
        "INSERT OR IGNORE INTO topics(id,name,visibility) VALUES(?,?,?)",
        ("federated-research-network", "Federated Research Network", "public"),
    )

    conn.commit()
    conn.close()
