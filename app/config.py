from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "Python App"
    app_url: str = "http://localhost:8000"
    secret_key: str = "dev-secret-key-change-in-production-must-be-32-chars"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./data.db"

    # Auth - Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # Storage
    storage_path: str = "./uploads"

    # Logging
    log_level: str = "INFO"


settings = Settings()
