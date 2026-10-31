from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/employee_review"
    test_database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/employee_review_test"
    cors_origins: str = "http://localhost:5173"


settings = Settings()
