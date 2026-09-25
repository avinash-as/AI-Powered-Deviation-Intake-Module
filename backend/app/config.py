from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Deviation Intake API"
    database_url: str = "postgresql+psycopg2://deviation:deviation@localhost:5432/deviations"
    # sqlite fallback for quick local run without postgres:
    # set DATABASE_URL=sqlite:///./deviations.db
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    # Second assignment-approved model, tried automatically if the primary is retired/rate-limited.
    groq_fallback_model: str = "gemma2-9b-it"
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_prefix = ""
        extra = "ignore"


settings = Settings()
