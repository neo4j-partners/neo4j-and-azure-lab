"""
Shared configuration and utilities for workshop solutions.

This module provides common functionality for Neo4j connections,
Microsoft Foundry integration, and configuration management.
"""

from contextlib import contextmanager
from pathlib import Path

from azure.identity import AzureCliCredential, DefaultAzureCredential
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.llm import OpenAILLM
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env from financial_data_load directory
_root_env = Path(__file__).parent.parent / ".env"
load_dotenv(_root_env)


class Neo4jConfig(BaseSettings):
    """Neo4j configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    uri: str = Field(validation_alias="NEO4J_URI")
    username: str = Field(validation_alias="NEO4J_USERNAME")
    password: str = Field(validation_alias="NEO4J_PASSWORD")


class AgentConfig(BaseSettings):
    """Agent configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    project_endpoint: str = Field(validation_alias="AZURE_AI_PROJECT_ENDPOINT")
    model_name: str = Field(default="gpt-5.2", validation_alias="AZURE_AI_MODEL_NAME")
    embedding_name: str = Field(
        default="text-embedding-ada-002",
        validation_alias="AZURE_AI_EMBEDDING_NAME",
    )

    @computed_field
    @property
    def inference_endpoint(self) -> str:
        """Get the model inference endpoint from project endpoint."""
        if "/api/projects/" in self.project_endpoint:
            base = self.project_endpoint.split("/api/projects/")[0]
            return f"{base}/models"
        return self.project_endpoint


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

    If authentication fails, provides a helpful error message.
    """
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
    """
    Get embedder using Microsoft Foundry's OpenAI-compatible endpoint.

    Uses Azure CLI credentials to authenticate with the inference endpoint.
    """
    config = get_agent_config()
    token = _get_azure_token()

    return OpenAIEmbeddings(
        model=config.embedding_name,
        base_url=config.inference_endpoint,
        api_key=token,
    )


def get_llm() -> OpenAILLM:
    """
    Get LLM using Microsoft Foundry's OpenAI-compatible endpoint.

    Uses Azure CLI credentials to authenticate with the inference endpoint.
    """
    config = get_agent_config()
    token = _get_azure_token()

    return OpenAILLM(
        model_name=config.model_name,
        base_url=config.inference_endpoint,
        api_key=token,
    )
