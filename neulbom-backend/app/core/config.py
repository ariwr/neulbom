from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    UPSTAGE_API_KEY: Optional[str] = None
    
    # LLM Provider Selection
    DEFAULT_LLM_PROVIDER: str = "upstage"  # "gemini" or "upstage"
    
    # LLM API URLs
    UPSTAGE_API_URL: str = "https://api.upstage.ai/v1/chat/completions"
    UPSTAGE_EMBEDDING_API_URL: str = "https://api.upstage.ai/v1/embeddings"
    
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite:///./neulbom.db"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]
    
    # RAG Settings
    VECTOR_DB_PATH: str = "./data/vector_db"
    EMBEDDING_PROVIDER: str = "upstage"  # "upstage" or "gemini"
    EMBEDDING_MODEL: str = "solar-embedding-1-large-passage"  # Upstage 문서 임베딩 모델
    EMBEDDING_QUERY_MODEL: str = "solar-embedding-1-large-query"  # Upstage 쿼리 임베딩 모델
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"  # Gemini 임베딩 모델 (gemini-embedding-001)
    EMBEDDING_DIMENSION: int = 4096  # Upstage: 4096, Gemini: 768 (실제 모델에 따라 변경)
    
    # Crisis Detection
    CRISIS_HOTLINE: str = "129"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # .env 파일에 OpenAI 모델명이 남아있을 경우 강제로 수정
        if "text-embedding" in self.EMBEDDING_MODEL:
            self.EMBEDDING_MODEL = "solar-embedding-1-large-passage"
            self.EMBEDDING_DIMENSION = 4096
        
        if "text-embedding" in self.EMBEDDING_QUERY_MODEL:
            self.EMBEDDING_QUERY_MODEL = "solar-embedding-1-large-query"


settings = Settings()

