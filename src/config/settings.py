from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    OPA_URL: str
    REDIS_HOST: str
    REDIS_PORT: int
    SYSTEM_PROMPT: str
    GEMINI_API_KEY: str
    model_config = SettingsConfigDict(env_file='.env')
settings = Settings()