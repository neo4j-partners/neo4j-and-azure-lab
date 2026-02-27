"""
Shared configuration and utilities for workshop solutions.

This module provides common functionality for Neo4j connections,
LLM/embedder initialization, and configuration management.
Supports both direct OpenAI and Azure AI Foundry.
"""

from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.llm import OpenAILLM
from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env from repository root
_root_env = Path(__file__).parent.parent / ".env"
load_dotenv(_root_env)


class Neo4jConfig(BaseSettings):
    """Neo4j configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    uri: str = Field(validation_alias="NEO4J_URI")
    username: str = Field(validation_alias="NEO4J_USERNAME")
    password: str = Field(validation_alias="NEO4J_PASSWORD")


class AgentConfig(BaseSettings):
    """LLM configuration loaded from environment variables.

    Supports two providers (auto-detected from environment):
    - OpenAI directly: set OPENAI_API_KEY
    - Azure AI Foundry: set AZURE_AI_PROJECT_ENDPOINT (uses az login)
    """

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    openai_api_key: str | None = Field(
        default=None, validation_alias="OPENAI_API_KEY"
    )
    project_endpoint: str | None = Field(
        default=None, validation_alias="AZURE_AI_PROJECT_ENDPOINT"
    )
    model_name: str = Field(default="gpt-4o", validation_alias="AZURE_AI_MODEL_NAME")
    embedding_name: str = Field(
        default="text-embedding-ada-002",
        validation_alias="AZURE_AI_EMBEDDING_NAME",
    )

    @model_validator(mode="after")
    def _check_provider(self) -> AgentConfig:
        if not self.openai_api_key and not self.project_endpoint:
            raise ValueError(
                "No LLM provider configured. Set one of:\n"
                "  - OPENAI_API_KEY (for OpenAI directly)\n"
                "  - AZURE_AI_PROJECT_ENDPOINT (for Azure AI Foundry)"
            )
        return self

    @computed_field
    @property
    def inference_endpoint(self) -> str | None:
        """Get the model inference endpoint from project endpoint."""
        if not self.project_endpoint:
            return None
        if "/api/projects/" in self.project_endpoint:
            base = self.project_endpoint.split("/api/projects/")[0]
            return f"{base}/models"
        return self.project_endpoint

    @property
    def use_openai(self) -> bool:
        """True when using OpenAI directly instead of Azure."""
        return self.openai_api_key is not None


@contextmanager
def get_neo4j_driver():
    """Context manager for Neo4j driver connection."""
    config = Neo4jConfig()
    driver = GraphDatabase.driver(
        config.uri,
        auth=(config.username, config.password),
    )
    try:
        yield driver
    finally:
        driver.close()


def get_agent_config() -> AgentConfig:
    """Get agent configuration from environment."""
    return AgentConfig()


def _get_azure_token() -> str:
    """
    Get Azure token for cognitive services.

    Tries AzureCliCredential first (for Dev Containers after 'az login'),
    then falls back to DefaultAzureCredential for other environments.
    """
    from azure.identity import AzureCliCredential, DefaultAzureCredential

    scope = "https://cognitiveservices.azure.com/.default"

    # Try Azure CLI first (most common in Dev Containers)
    try:
        credential = AzureCliCredential()
        token = credential.get_token(scope)
        return token.token
    except Exception:
        pass

    # Fall back to DefaultAzureCredential
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token(scope)
        return token.token
    except Exception as e:
        raise RuntimeError(
            "Azure authentication failed. Please run:\n"
            "  1. az login --use-device-code\n"
            "  2. Restart your Jupyter kernel (Kernel → Restart)\n\n"
            f"Original error: {e}"
        ) from e


def get_embedder() -> OpenAIEmbeddings:
    """Get embedder configured from environment (OpenAI or Azure AI Foundry)."""
    config = get_agent_config()

    if config.use_openai:
        return OpenAIEmbeddings(
            model=config.embedding_name,
            api_key=config.openai_api_key,
        )

    token = _get_azure_token()
    return OpenAIEmbeddings(
        model=config.embedding_name,
        base_url=config.inference_endpoint,
        api_key=token,
    )


def get_llm() -> OpenAILLM:
    """Get LLM configured from environment (OpenAI or Azure AI Foundry)."""
    config = get_agent_config()

    if config.use_openai:
        return OpenAILLM(
            model_name=config.model_name,
            api_key=config.openai_api_key,
        )

    token = _get_azure_token()
    return OpenAILLM(
        model_name=config.model_name,
        base_url=config.inference_endpoint,
        api_key=token,
    )
