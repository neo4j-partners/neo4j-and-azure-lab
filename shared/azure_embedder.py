"""
Custom Azure AI Foundry embedder for neo4j-agent-memory.

The neo4j-agent-memory package defaults to OpenAI's embedding API, requiring
OPENAI_API_KEY. This module provides an embedder that uses the Azure AI Foundry
inference endpoint (OpenAI-compatible) with Azure CLI authentication.
"""

from __future__ import annotations

from openai import AsyncOpenAI

from neo4j_agent_memory.core.exceptions import EmbeddingError
from neo4j_agent_memory.embeddings.base import BaseEmbedder

from config import _get_azure_token, get_agent_config


class AzureFoundryEmbedder(BaseEmbedder):
    """Embedder using Azure AI Foundry's OpenAI-compatible inference endpoint."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        dimensions: int = 1536,
        batch_size: int = 100,
    ):
        self._base_url = base_url
        self._api_key = api_key
        self._model = model
        self._dimensions = dimensions
        self._batch_size = batch_size
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def embed(self, text: str) -> list[float]:
        try:
            response = await self._client.embeddings.create(
                input=text,
                model=self._model,
            )
            return response.data[0].embedding
        except Exception as e:
            raise EmbeddingError(f"Azure embedding failed: {e}") from e

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            all_embeddings: list[list[float]] = []
            for i in range(0, len(texts), self._batch_size):
                batch = texts[i : i + self._batch_size]
                response = await self._client.embeddings.create(
                    input=batch,
                    model=self._model,
                )
                all_embeddings.extend([item.embedding for item in response.data])
            return all_embeddings
        except Exception as e:
            raise EmbeddingError(f"Azure batch embedding failed: {e}") from e


def get_memory_embedder() -> AzureFoundryEmbedder | None:
    """Factory that returns a configured AzureFoundryEmbedder, or None for OpenAI.

    When None is returned, MemoryClient will use its default OpenAI embedder.
    """
    config = get_agent_config()
    if config.use_openai:
        return None
    token = _get_azure_token()
    return AzureFoundryEmbedder(
        base_url=config.inference_endpoint,
        api_key=token,
        model=config.embedding_name,
    )
