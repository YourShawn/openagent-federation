from pydantic import BaseModel


class RegisterReq(BaseModel):
    nickname: str | None = None
    operator: str | None = None
    primary_topic: str | None = None


class AddFriendReq(BaseModel):
    my_agent_id: str
    friend_agent_id: str


class JoinTopicReq(BaseModel):
    agent_id: str
    topic_id: str | None = None
    invite_token: str | None = None
