from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):    
    SECRET_KEY: str 
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_PORT: str
    DB_HOST: str
    ANTHROPIC_API_KEY: str



    # Pydantic read automatically the .env file
    model_config = SettingsConfigDict(env_file=".env")

# Create an unique instance (Singleton)
settings = Settings()