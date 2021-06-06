from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    DEBUG: bool = False
    SERVER_HOST: str = 'http://localhost:8000'
    PROJECT_NAME: str = 'CrossBase'
    SECRET_KEY: str
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DATABASE: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get('POSTGRES_PORT'),
            path=f"/{values.get('POSTGRES_DATABASE') or ''}",
        )

    EMAIL_TEMPLATES_DIR: str = 'email-templates/build'
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 5
    EMAILS_ENABLED: bool = True
    EMAILS_FROM_NAME = 'CrossBase'
    EMAILS_FROM_EMAIL = 'noreply@crossbase.io'

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_TLS: bool
    SMTP_USER: str
    SMTP_PASSWORD: str

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
