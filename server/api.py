from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import HTMLResponse

from .db.connection import get_conn
from .models import RegisterReq, AddFriendReq, JoinTopicReq
from .services import require_token, make_id, now_iso, get_agent_or_404, topic_exists

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def root_nav():
    return """
    <html><head><title>OAF Navigation</title></head><body style=\"font-family:Arial;padding:20px\">
      <h2>OpenAgent Federation - Navigation</h2>
      <ul>
        <li><a href=\"/.well-known/lobster-agent.json\">Integration Manifest</a></li>
        <li><a href=\"/nav\">Navigation JSON</a></li>
        <li><a href=\"/v1/topics\">Public Topics</a></li>
        <li><a href=\"/docs\">API Docs</a></li>
      </ul>
    </body></html>
    """


@router.get("/nav")
def nav_json():
    return {
        "projects": [
            {"name": "OpenAgent Federation API", "url": "http://142.171.156.25:8787", "status": "running"}
        ]
    }


@router.get("/.well-known/lobster-agent.json")
def well_known():
    return {
        "name": "OpenAgent Federation",
        "version": "0.3",
        "auth": {"type": "header", "header": "X-API-Token"},
        "endpoints": {
            "register": "/v1/agents/register",
            "friends_add": "/v1/friends/add",
            "join_topic": "/v1/topics/join",
            "topics": "/v1/topics",
            "my_profile": "/v1/agents/{agent_id}",
        },
        "notes": "Register then join a public topic directly, or use invite_token for private/team topic.",
    }


@router.get("/v1/topics")
def list_topics():
    conn = get_conn()
    rows = conn.execute("SELECT id,name,visibility FROM topics ORDER BY id").fetchall()
    conn.close()
    return {"topics": [dict(r) for r in rows]}


@router.post("/v1/agents/register")
def register(req: RegisterReq, x_api_token: str | None = Header(default=None)):
    require_token(x_api_token)
    agent_id = make_id("oaf")
    conn = get_conn()
    conn.execute(
        "INSERT INTO agents(agent_id,nickname,operator,created_at,status,topic) VALUES(?,?,?,?,?,?)",
        (agent_id, req.nickname, req.operator, now_iso(), "active", req.primary_topic),
    )
    conn.commit()
    conn.close()
    return {"agent_id": agent_id, "status": "registered"}


@router.post("/v1/friends/add")
def add_friend(req: AddFriendReq, x_api_token: str | None = Header(default=None)):
    require_token(x_api_token)
    conn = get_conn()
    get_agent_or_404(conn, req.my_agent_id)
    get_agent_or_404(conn, req.friend_agent_id)

    a, b = sorted([req.my_agent_id, req.friend_agent_id])
    conn.execute("INSERT OR IGNORE INTO friendships(a,b,created_at) VALUES(?,?,?)", (a, b, now_iso()))
    conn.commit()
    count = conn.execute(
        "SELECT COUNT(*) AS n FROM friendships WHERE a=? OR b=?", (req.my_agent_id, req.my_agent_id)
    ).fetchone()["n"]
    conn.close()
    return {"ok": True, "friends_count": count}


@router.post("/v1/topics/join")
def join_topic(req: JoinTopicReq, x_api_token: str | None = Header(default=None)):
    require_token(x_api_token)
    conn = get_conn()
    get_agent_or_404(conn, req.agent_id)

    topic_id = req.topic_id
    if req.invite_token:
        invite = conn.execute(
            "SELECT team_id, topic FROM invites WHERE token=? AND enabled=1", (req.invite_token,)
        ).fetchone()
        if not invite:
            conn.close()
            raise HTTPException(401, "invalid invite token")
        topic_id = invite["topic"]
        team_id = invite["team_id"]
    else:
        if not topic_id:
            conn.close()
            raise HTTPException(400, "topic_id or invite_token required")
        topic = topic_exists(conn, topic_id)
        if topic["visibility"] != "public":
            conn.close()
            raise HTTPException(401, "private topic requires invite token")
        team_id = None

    conn.execute("UPDATE agents SET team_id=?, topic=? WHERE agent_id=?", (team_id, topic_id, req.agent_id))
    conn.commit()
    conn.close()
    return {"ok": True, "team_id": team_id, "topic": topic_id}


@router.get("/v1/agents/{agent_id}")
def get_agent(agent_id: str, x_api_token: str | None = Header(default=None)):
    require_token(x_api_token)
    conn = get_conn()
    data = get_agent_or_404(conn, agent_id)
    fs = conn.execute("SELECT a,b FROM friendships WHERE a=? OR b=?", (agent_id, agent_id)).fetchall()
    friends = [r["b"] if r["a"] == agent_id else r["a"] for r in fs]
    out = dict(data)
    out["friends"] = friends
    conn.close()
    return out
