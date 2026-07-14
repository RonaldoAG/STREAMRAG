from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
