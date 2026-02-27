"""Utilities for data loading, Neo4j operations, and AI services."""

import asyncio
from pathlib import Path

from azure.identity import AzureCliCredential, DefaultAzureCredential
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter
from neo4j_graphrag.llm import OpenAILLM
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load configuration from project root .env
_config_file = Path(__file__).parent.parent / ".env"
load_dotenv(_config_file)


# =============================================================================
# Configuration Classes
# =============================================================================

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
    model_name: str = Field(default="gpt-4o", validation_alias="AZURE_AI_MODEL_NAME")
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


# =============================================================================
# Azure Authentication
# =============================================================================

def _get_azure_token() -> str:
    """Get Azure token for cognitive services.

    Tries AzureCliCredential first (for Dev Containers after 'az login'),
    then falls back to DefaultAzureCredential for other environments.
    """
    scope = "https://cognitiveservices.azure.com/.default"

    try:
        credential = AzureCliCredential()
        token = credential.get_token(scope)
        return token.token
    except Exception:
        pass

    try:
        credential = DefaultAzureCredential()
        token = credential.get_token(scope)
        return token.token
    except Exception as e:
        raise RuntimeError(
            "Azure authentication failed. Please run:\n"
            "  1. az login --use-device-code\n"
            "  2. Restart your Jupyter kernel\n\n"
            f"Original error: {e}"
        ) from e


# =============================================================================
# AI Services
# =============================================================================

def get_embedder() -> OpenAIEmbeddings:
    """Get embedder using Azure AI's OpenAI-compatible endpoint."""
    config = AgentConfig()
    token = _get_azure_token()

    return OpenAIEmbeddings(
        model=config.embedding_name,
        base_url=config.inference_endpoint,
        api_key=token,
    )


def get_llm() -> OpenAILLM:
    """Get LLM using Azure AI's OpenAI-compatible endpoint."""
    config = AgentConfig()
    token = _get_azure_token()

    return OpenAILLM(
        model_name=config.model_name,
        base_url=config.inference_endpoint,
        api_key=token,
    )


# =============================================================================
# Neo4j Connection
# =============================================================================

class Neo4jConnection:
    """Manages Neo4j database connection."""

    def __init__(self):
        """Initialize and connect to Neo4j using environment configuration."""
        self.config = Neo4jConfig()
        self.driver = GraphDatabase.driver(
            self.config.uri,
            auth=(self.config.username, self.config.password)
        )

    def verify(self):
        """Verify the connection is working."""
        self.driver.verify_connectivity()
        print("Connected to Neo4j successfully!")
        return self

    def clear_graph(self):
        """Remove all Document and Chunk nodes."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n) WHERE n:Document OR n:Chunk
                DETACH DELETE n
                RETURN count(n) as deleted
            """)
            count = result.single()["deleted"]
            print(f"Deleted {count} nodes")
        return self

    def close(self):
        """Close the database connection."""
        self.driver.close()
        print("Connection closed.")


# =============================================================================
# Data Loading
# =============================================================================

class DataLoader:
    """Handles loading text data from files."""

    def __init__(self, file_path: str):
        """Initialize with path to data file."""
        self.file_path = Path(file_path)
        self._text = None

    @property
    def text(self) -> str:
        """Load and return the text content from the file."""
        if self._text is None:
            self._text = self.file_path.read_text().strip()
        return self._text

    def get_metadata(self) -> dict:
        """Return metadata about the loaded file."""
        return {
            "path": str(self.file_path),
            "name": self.file_path.name,
            "size": len(self.text)
        }


# =============================================================================
# Text Splitting
# =============================================================================

def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    """Split text into chunks using FixedSizeSplitter.

    Args:
        text: Text to split
        chunk_size: Maximum characters per chunk
        chunk_overlap: Characters to overlap between chunks

    Returns:
        List of chunk text strings
    """
    splitter = FixedSizeSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        approximate=True
    )
    # Use nest_asyncio or get_event_loop to handle Jupyter's running event loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Inside Jupyter or another async context — use nest_asyncio
        import nest_asyncio
        nest_asyncio.apply()
        result = asyncio.run(splitter.run(text))
    else:
        result = asyncio.run(splitter.run(text))
    return [chunk.text for chunk in result.chunks]
