from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

JWT_ALGORITHM = "HS256"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    project_name: str = Field("Users", alias="PROJECT_NAME")
    postgres_user: str = Field("app", alias="POSTGRES_USER")
    postgres_db: str = Field("database", alias="POSTGRES_DB")
    postgres_password: str = Field("postgres", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field("postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_url: str = Field(
        "postgresql+asyncpg://postgres:postgres@db:5432/foo", alias="POSTGRES_URL"
    )
    redis_host: str = Field("127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")

    jwt_secret_key: str = Field("my_secret_key", alias="JWT_SECRET_KEY")
    access_token_exp_hours: int = Field(1, alias="ACCESS_TOKEN_EXP_HOURS")
    refresh_token_exp_days: int = Field(10, alias="REFRESH_TOKEN_EXP_DAYS")
    engine_echo: bool = Field(False, alias="ENGINE_ECHO")


settings = Settings()
