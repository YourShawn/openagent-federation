from pydantic import BaseModel
import os


class Settings(BaseModel):
    api_token: str = os.getenv("OAF_API_TOKEN", "OAF-TEST-TOKEN-001")
    db_path: str = os.getenv("OAF_DB_PATH", "./data/oaf.db")


settings = Settings()
