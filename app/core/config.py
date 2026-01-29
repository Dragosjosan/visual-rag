from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    milvus_host: str = Field(default="localhost")
    milvus_port: int = Field(default=19530)
    milvus_collection_name: str = Field(default="visual_rag_patches")

    colqwen2_model_name: str = Field(default="vidore/colqwen2-v1.0-hf")
    colqwen2_device: str = Field(default="mps")
    colqwen2_batch_size: int = Field(default=4)

    ollama_base_url: str = Field(default="http://localhost:11434")
    vlm_model_name: str = Field(default="llama2")

    pdf_dpi: int = Field(default=150)
    pdf_max_pages: int = Field(default=100)
    documents_dir: str = Field(default="data")

    top_k: int = Field(default=5)
    similarity_threshold: float = Field(default=0.7)


settings = Settings()
