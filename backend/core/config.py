from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    model_config = {"env_file": ".env"}

    allowed_origins: List[str] = ["http://localhost:3000"]
    max_file_size_mb: int = 20
    supabase_url: str = ""
    supabase_service_role_key: str = ""


settings = Settings()
