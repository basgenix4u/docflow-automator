import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "docflow_super_secret_key_change_in_production_2026_a8f9d3b"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database: Neon PostgreSQL or local SQLite
    DATABASE_URL: str = "sqlite+aiosqlite:////home/user/docflow-automator/backend/docflow.db"

    FUW_PORTAL_URL: str = "https://ug.fuwportal.edu.ng/index.php"

    # Free Cloud Storage (Cloudinary)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    STORAGE_DIR: str = "/home/user/docflow-automator/storage/pdfs"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

os.makedirs(settings.STORAGE_DIR, exist_ok=True)
