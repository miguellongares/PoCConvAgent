from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_base_url: str
    llm_model: str
    llm_api_key: str = "none"
    padi_base_url: str = "https://public-health.padi-web.cirad.fr/api/v1"
    padi_token: str = ""
    stac_base_url: str = "https://stac.mood-platform.eu"
    qdrant_url: str = "http://localhost:6333"


settings = Settings()
