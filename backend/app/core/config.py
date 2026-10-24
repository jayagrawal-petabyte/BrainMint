from typing import List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEV_SECRET = "dev-only-insecure-secret-change-me"


class Settings(BaseSettings):
    PROJECT_NAME: str = "BrainMint Software Website"
    API_V1_STR: str = "/api/v1"
    SITE_URL: str = "https://brainmint.com"
    ENVIRONMENT: str = "development"  # development | staging | production
    LOG_LEVEL: str = "INFO"

    # ---- Database (Supabase pooler URL in staging/production) ----
    DATABASE_URL: str = "sqlite:///./test.db"

    # ---- Auth ----
    SECRET_KEY: str = _DEV_SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ---- CORS (comma separated list of frontend origins) ----
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # ---- Email ----
    EMAIL_ENABLED: bool = True
    EMAIL_PROVIDER: str = "smtp"  # smtp | sendgrid | mailgun
    EMAIL_FROM: str = "BrainMint Software <hello@brainmint.com>"
    EMAIL_TEAM_TO: str = ""  # inbox that receives enquiries

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True

    SENDGRID_API_KEY: str = ""
    MAILGUN_API_KEY: str = ""
    MAILGUN_DOMAIN: str = ""

    # Names read by app/services/email_service.py. They default to the fields
    # above, so one set of env vars is enough.
    SMTP_USER: str = ""
    EMAILS_FROM_EMAIL: str = ""
    EMAILS_TO_EMAIL: str = ""

    # ---- CAPTCHA ----
    CAPTCHA_ENABLED: bool = True
    CAPTCHA_PROVIDER: str = "hcaptcha"  # hcaptcha | recaptcha
    CAPTCHA_SECRET_KEY: str = ""
    RECAPTCHA_MIN_SCORE: float = 0.5

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="allow")

    @field_validator("DATABASE_URL")
    @classmethod
    def _normalise_db_url(cls, v: str) -> str:
        # Some providers hand out postgres:// which SQLAlchemy 2 rejects.
        # Pin the psycopg2 driver explicitly: SQLAlchemy 2.1+ otherwise defaults to psycopg v3.
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    
    @model_validator(mode="after")
    def _fill_aliases_and_check(self) -> "Settings":
        self.SMTP_USER = self.SMTP_USER or self.SMTP_USERNAME
        self.EMAILS_FROM_EMAIL = self.EMAILS_FROM_EMAIL or self.EMAIL_FROM
        self.EMAILS_TO_EMAIL = self.EMAILS_TO_EMAIL or self.EMAIL_TEAM_TO
        if self.is_deployed and self.SECRET_KEY == _DEV_SECRET:
            raise ValueError("SECRET_KEY must be set to a strong random value in staging/production")
        return self

    @property
    def is_deployed(self) -> bool:
        return self.ENVIRONMENT.lower() in {"staging", "production"}

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()