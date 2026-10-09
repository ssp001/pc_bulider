from pydantic_settings import SettingsConfigDict, BaseSettings


class __CoreSettings(BaseSettings):
    MODEL_NAME: str
    GROQ_API_KEY: str
    LANGSMITH_TRACING: str
    LANGSMITH_ENDPOINT: str
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str
    TRAVILY_API: str
    model_config = SettingsConfigDict(
        env_file=".env"
    )
