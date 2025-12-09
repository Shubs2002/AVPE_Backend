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

    # ☁️ Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    # 🔐 JWT Authentication
    JWT_SECRET_KEY: str | None = None
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 🔒 Character Encryption
    CHARACTER_ENCRYPTION_KEY: str | None = None

    # 📧 Email Configuration (for OTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None
    SMTP_FROM_NAME: str = "AVPE"

    # 🔢 OTP Configuration
    OTP_EXPIRE_MINUTES: int = 10
    OTP_LENGTH: int = 6
    CHARACTER_ENCRYPTION_KEY: str | None = None

    # Define CORS origins for different environments
    DEV_ORIGINS: ClassVar[list[str]] = ["*"]
    PROD_ORIGINS: ClassVar[list[str]] = ["*"]

    @property
    def cors_origins(self):
        return self.DEV_ORIGINS if self.ENV == "dev" else self.PROD_ORIGINS


# Initialize settings AFTER envs are loaded
_env = load_envs()
settings = Settings(ENV=_env)
