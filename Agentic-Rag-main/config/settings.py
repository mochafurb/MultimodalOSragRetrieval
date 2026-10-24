from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = "mock-key"
    openai_api_base: str | None = None
    openai_embedding_model: str = "text-embedding-3-large"
    openai_chat_model: str = "gpt-4o-mini"
    openai_vision_model: str = "gpt-4o-mini"

    pinecone_api_key: str = "mock-key"
    pinecone_environment: str = "us-east-1-aws"
    pinecone_index_name: str = "dbms-rag-openai"
    pinecone_namespace_text: str = "text-chunks"
    pinecone_namespace_image: str = "image-chunks"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dbms_rag"

    max_retrieval_k: int = 20
    rerank_top_n: int = 8
    chunk_size: int = 800
    chunk_overlap: int = 150
    max_reflection_loops: int = 2
    colpali_enabled: bool = True
    app_env: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
