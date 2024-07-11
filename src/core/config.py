import os
from functools import lru_cache

from pydantic import AnyUrl, BaseSettings, validator


class Settings(BaseSettings):
    APP_NAME: str = "ai-service"
    APP_ENV: str = "local"
    APP_URL: str
    RELEASE_STRING: str = os.getenv("RELEASE_STRING", "dev")

    API_PREFIX: str = "/ai-service"
    API_V1_PREFIX: str = "/v1"

    # Log and Debug
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

    # Redis
    REDIS_URL: AnyUrl = None
    REDIS_CACHE_DB: int = 0

    # Datbase - PostrgreSQL
    DB_HOST: str = "postgresql"
    DB_USER: str = None
    DB_PASSWORD: str = None
    DB_PORT: int = 5432
    DB_DATABASE: str = "zingtree"
    DB_DIALECT: str = "postgresql+psycopg2"
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True

    # Datbase - MySQL
    MYSQL_DB_HOST: str = "db"
    MYSQL_DB_USER: str = None
    MYSQL_DB_PASSWORD: str = None
    MYSQL_DB_PORT: str = 3306
    MYSQL_DB_DATABASE: str = "zingtree"
    MYSQL_DB_DIALECT: str = "mysql+pymysql"
    MYSQL_DB_POOL_RECYCLE: int = 3600
    MYSQL_DB_POOL_PRE_PING: bool = True

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"
    KAFKA_EMBED_JOB_STATUS_TOPIC: str = "embed-job-status-local"
    KAFKA_EMBED_JOBS_TOPIC: str = "embed-jobs-local"
    KAFKA_GROUP_ID: str = "random-id-123"

    # AWS
    AWS_ACCESS_KEY_ID: str = None
    AWS_SECRET_ACCESS_KEY: str = None
    AWS_DEFAULT_REGION: str = "us-east-1"
    AWS_LOCALSTACK_URL: str = "http://local-aws:4566"

    # Assets
    ASSETS_S3_BUCKET: str
    ASSETS_CACHE_TTL: int = 60 * 5  # 5 minutes

    # Authoring
    AUTHORING_PROMPTS_TEMPLATES_FILE: str = "prompt_templates.json"

    # Open AI
    OPENAI_ORG_ID: str = None
    OPENAI_API_KEY: str = None

    # Slack
    SLACK_CHANNEL_ID: str = None
    SLACK_TOKEN: str = None

    # Embeddings
    # Typical values are 768, 1024, 2048, 4096
    # For Amazon Titan Embeddings, the value should be 1536
    EMBEDDINGS_DIMENSIONS: int = 4096

    # The values could be "bedrock_embedder",
    # "cohere_embedder" or "huggingface_embedder"
    EMBEDDINGS_ENDPOINT_TYPE: str = "huggingface_embedder"
    EMBEDDINGS_ENDPOINT_NAME: str = "amazon.titan-e1t-medium"

    # Summarizer
    # The values could be "bedrock_summarizer", "cohere_summarizer"
    # or "huggingface_summarizer"
    SUMMARIZER_ENDPOINT_TYPE: str = "huggingface_summarizer"

    SUMMARIZER_ENDPOINT_NAME: str = "amazon.titan-tg1-large"
    SUMMARIZER_PROMPT_TYPE: str = "short"
    SUMMARIZER_CONFIG_FILE: str = "summarizer_config.json"

    # Semantic Search Snippet Length
    SEMANTIC_SEARCH_CHUNK_LENGTH: int = 1000

    # Semantic Search Chunking Method
    # The values could be "characters" or "sentences"
    SEMANTIC_SEARCH_CHUNKING_METHOD: str = "sentences"

    # The values could be "none", "prefix" or "suffix"
    SEMANTIC_SEARCH_CONCAT: str = "none"

    # The values could be  "True" or "False"
    SEMANTIC_SEARCH_QUERY_EXPANSION: bool = False

    # Value between 0 and 1
    SEMANTIC_SEARCH_THRESHOLD: float = 0.70

    # svc URLs
    SERVICE_TO_SERVICE_KEY: str = "just-some-key"
    CONNECTORS_SVC_URL: str = "http://connectors-svc"
    CONFIG_SVC_URL: str = "http://config-svc"
    LIME_URL: str = "http://lime"

    # Transformation Config
    SILVER_TO_GOLD_ENABLE: bool = True

    @validator("*", pre=True)
    def clean_input(cls, value: object) -> any:
        return value.strip("\"'") if isinstance(value, str) else value

    @validator("SEMANTIC_SEARCH_THRESHOLD")
    def validate_semantic_search_threshold(cls, value):
        if not isinstance(value, float):
            raise ValueError("Treshold must be a float")
        if value < 0 or value > 1:
            raise ValueError("Treshold must be between 0 and 1")
        return value

    class Config:
        env_file = (
            ".env"
            if os.getenv("APP_ENV", "local") != "testing"
            else ".env.testing"
        )


@lru_cache()
def get_settings():
    return Settings()
