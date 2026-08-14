import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-only-change-me-not-for-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "sqlite+aiosqlite:///./docflow.db"

    FUW_PORTAL_URL: str = "https://ug.fuwportal.edu.ng/index.php"

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    STORAGE_DIR: str = "./storage/pdfs"

    # Comma-separated browser origins. Empty + DEBUG allows localhost defaults.
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    ADMIN_EMAIL: str = ""
    ADMIN_FULL_NAME: str = "DocFlow Administrator"
    ADMIN_PASSWORD: str = ""

    ALLOW_PUBLIC_REGISTER: bool = True
    AUTO_GENERATE_RATE_LIMIT: int = 8
    AUTO_GENERATE_RATE_WINDOW_SECONDS: int = 600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("STORAGE_DIR")
    @classmethod
    def ensure_storage(cls, value: str) -> str:
        os.makedirs(value, exist_ok=True)
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [item.strip() for item in self.CORS_ORIGINS.split(",") if item.strip()]
        if self.DEBUG and not origins:
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
        return origins or ["http://localhost:3000"]

    @property
    def is_insecure_default_secret(self) -> bool:
        return self.SECRET_KEY in {
            "dev-only-change-me-not-for-production",
            "docflow_super_secret_key_change_in_production_2026_a8f9d3b",
            "docflow_production_secure_secret_key_2026",
        }


settings = Settings()
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
