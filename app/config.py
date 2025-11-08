from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    model_config = {"protected_namespaces": ()}
    """Application settings loaded from environment variables"""
    
    # Mistral AI Configuration
    mistral_api_key: str
    model_name: str = "mistral-small-latest"
    embedding_model: str = "mistral-embed"
    
    # Application Configuration
    app_name: str = "Mistral Document RAG API"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Cache settings to avoid repeated file reads"""
    return Settings()
