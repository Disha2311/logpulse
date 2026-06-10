from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # SMTP Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "test@gmail.com"
    SMTP_PASSWORD: str = "testpassword"

    # Alerts configuration
    DEFAULT_ALERT_COOLDOWN_MINUTES: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
