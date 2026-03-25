from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOSTNAME: str
    DB_PASSWORD: str
    DB_PORT: str
    DB_NAME: str
    DB_USERNAME:str
    SECRET_KEY: str
    ALGO: str
    ACCESS_EXPIRED: int
    APP_VERSION: str
    DEBUG_MODE: bool = False

    class Config:
        env_file = ".env"

settings = Settings()