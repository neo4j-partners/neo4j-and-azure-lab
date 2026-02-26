"""Configuration, Azure authentication, and Neo4j connection management."""

from __future__ import annotations

import sys
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from azure.identity import AzureCliCredential, DefaultAzureCredential
from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from pydantic import Field, SecretStr, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolved once at import time -- stable regardless of cwd.
_PKG_DIR = Path(__file__).resolve().parent
_ENV_FILE = _PKG_DIR.parent / ".env"

load_dotenv(_ENV_FILE)


class Neo4jConfig(BaseSettings):
    """Neo4j connection settings loaded from .env."""

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    uri: str = Field(validation_alias="NEO4J_URI")
    username: str = Field(validation_alias="NEO4J_USERNAME")
    password: SecretStr = Field(validation_alias="NEO4J_PASSWORD")

    @model_validator(mode="after")
    def _check_uri_scheme(self) -> Neo4jConfig:
        valid = ("neo4j://", "neo4j+s://", "neo4j+ssc://",
                 "bolt://", "bolt+s://", "bolt+ssc://")
        if not self.uri.startswith(valid):
            raise ValueError(
                f"NEO4J_URI must start with a valid scheme "
                f"(neo4j+s://, bolt+s://, etc.), got: {self.uri}"
            )
        return self


class AgentConfig(BaseSettings):
    """Azure AI Foundry configuration loaded from .env."""

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    project_endpoint: str = Field(validation_alias="AZURE_AI_PROJECT_ENDPOINT")
    model_name: str = Field(
        default="gpt-4o",
        validation_alias="AZURE_AI_MODEL_NAME",
    )
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


# ---------------------------------------------------------------------------
# Azure authentication
# ---------------------------------------------------------------------------


def get_azure_token() -> str:
    """Get Azure token for cognitive services.

    Tries AzureCliCredential first (for Dev Containers after ``az login``),
    then falls back to DefaultAzureCredential for other environments.
    """
    scope = "https://cognitiveservices.azure.com/.default"

    try:
        credential = AzureCliCredential()
        return credential.get_token(scope).token
    except Exception:
        pass

    try:
        credential = DefaultAzureCredential()
        return credential.get_token(scope).token
    except Exception as e:
        raise RuntimeError(
            "Azure authentication failed. Please run:\n"
            "  az login --use-device-code\n"
            f"Original error: {e}"
        ) from e


def get_llm():
    """Get LLM using Azure AI Foundry's OpenAI-compatible endpoint."""
    from neo4j_graphrag.llm import OpenAILLM

    config = AgentConfig()
    token = get_azure_token()

    return OpenAILLM(
        model_name=config.model_name,
        base_url=config.inference_endpoint,
        api_key=token,
    )


def get_embedder():
    """Get embedder using Azure AI Foundry's OpenAI-compatible endpoint."""
    from neo4j_graphrag.embeddings import OpenAIEmbeddings

    config = AgentConfig()
    token = get_azure_token()

    return OpenAIEmbeddings(
        model=config.embedding_name,
        base_url=config.inference_endpoint,
        api_key=token,
    )


# ---------------------------------------------------------------------------
# Neo4j connection
# ---------------------------------------------------------------------------


@contextmanager
def connect() -> Generator[Driver, None, None]:
    """Create a Neo4j driver, verify connectivity, and close on exit."""
    config = Neo4jConfig()
    driver = GraphDatabase.driver(
        config.uri,
        auth=(config.username, config.password.get_secret_value()),
    )
    try:
        driver.verify_connectivity()
    except (ServiceUnavailable, OSError) as exc:
        driver.close()
        print(f"[FAIL] Cannot connect to {config.uri}")
        print(f"       {exc}")
        print("\nCheck that the Neo4j instance is running and reachable.")
        sys.exit(1)
    try:
        print(f"[OK] Connected to {config.uri}\n")
        yield driver
    finally:
        driver.close()
