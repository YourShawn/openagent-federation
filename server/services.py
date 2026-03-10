from datetime import datetime, timezone
import secrets
from fastapi import HTTPException

from .core.config import settings
from .db.connection import get_conn


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_id(prefix: str, nbytes: int = 8) -> str:
    return f"{prefix}_{secrets.token_hex(nbytes)}"


def require_token(x_api_token: str | None) -> None:
    if x_api_token != settings.api_token:
        raise HTTPException(401, "invalid token")


def get_agent_or_404(conn, agent_id: str):
    row = conn.execute("SELECT * FROM agents WHERE agent_id=?", (agent_id,)).fetchone()
    if not row:
        raise HTTPException(404, "agent not found")
    return row


def topic_exists(conn, topic_id: str):
    row = conn.execute("SELECT id, visibility FROM topics WHERE id=?", (topic_id,)).fetchone()
    if not row:
        raise HTTPException(404, "topic not found")
    return row
