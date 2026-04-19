from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./notif.db"
    rate_limit_per_minute: int = 30

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
