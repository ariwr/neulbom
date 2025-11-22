from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    UPSTAGE_API_KEY: Optional[str] = None
    
    # LLM Provider Selection
    DEFAULT_LLM_PROVIDER: str = "gemini"  # "gemini" or "upstage"
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite:///./neulbom.db"
    
    # RAG Settings
    VECTOR_DB_PATH: str = "./data/vector_db"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Crisis Detection
    CRISIS_HOTLINE: str = "129"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

