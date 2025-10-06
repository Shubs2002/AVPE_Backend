import os
from typing import ClassVar
from dotenv import load_dotenv
from pydantic_settings import BaseSettings   # ✅ correct import

def load_envs():
    """Load base + environment-specific .env files."""
    # Always load base .env
    load_dotenv(".env")

    # Pick env from system OR fallback to dev
    env = os.getenv("ENV", "dev")

    # Load correct .env file depending on ENV (override base)
    if env == "prod":
        load_dotenv(".env.prod", override=True)
    else:
        load_dotenv(".env.dev", override=True)

    return env


class Settings(BaseSettings):
    ENV: str

    # Existing
    SCOPES: str | None = None
    REDIRECT_URI: str | None = None

    # 🔑 New → OpenAI / OpenRouter
    OPENAI_API_KEY: str | None = None
    OPENROUTER_BASE_URL: str | None = None
    SCRIPT_MODEL: str | None = None

    # ⚙️ New → Google Cloud Platform
    GCP_SERVICE_ACC_AVPE_FILE_NAME: str | None = None
    GOOGLE_STUDIO_API_KEY: str | None = None
    VIDEO_GENERATION_MODEL: str | None = None

    # 🗄️ MongoDB Configuration
    MONGODB_URI: str | None = None
    MONGODB_DATABASE: str | None = None

    # Define CORS origins for different environments
    DEV_ORIGINS: ClassVar[list[str]] = ["*"]
    PROD_ORIGINS: ClassVar[list[str]] = ["*"]

    @property
    def cors_origins(self):
        return self.DEV_ORIGINS if self.ENV == "dev" else self.PROD_ORIGINS


# Initialize settings AFTER envs are loaded
_env = load_envs()
settings = Settings(ENV=_env)
