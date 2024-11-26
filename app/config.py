from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str = "recycling_app"
    DB_PASSWORD: str = "password123"
    DB_HOST: str = "localhost"
    DB_PORT: str = "1521"
    DB_SERVICE: str = "XE"
    
    class Config:
        env_file = ".env"

settings = Settings() 