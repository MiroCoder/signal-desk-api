from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_password: str
    jwt_secret: str
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SIGNALDESK_")

settings = Settings()