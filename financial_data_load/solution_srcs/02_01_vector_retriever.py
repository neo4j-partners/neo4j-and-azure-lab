"""
Vector Retriever Demo

This workshop demonstrates basic semantic search using VectorRetriever
and GraphRAG from neo4j-graphrag-python.

Run with: uv run python solutions/02_01_vector_retriever.py
"""

from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.retrievers import VectorRetriever

from config import get_embedder, get_neo4j_driver, get_llm


def create_vector_retriever(driver, embedder) -> VectorRetriever:
    """Create a VectorRetriever for semantic search."""
    return VectorRetriever(
        driver=driver,
        index_name="chunkEmbeddings",
        embedder=embedder,
        return_properties=["text"],
    )


def demo_vector_search(retriever: VectorRetriever, query: str) -> None:
    """Demo direct vector search without LLM."""
    print(f"\n--- Direct Vector Search ---")
    print(f"Query: {query}\n")

    results = retriever.search(query_text=query, top_k=5)
    print(f"Number of results returned: {len(results.items)}\n")
    for item in results.items:
        score = item.metadata.get("score", 0)
        content = item.content[:200] + "..." if item.content and len(item.content) > 200 else (item.content or "")
        print(f"Score: {score:.4f}, Content: {content}")


def demo_rag_search(llm, retriever: VectorRetriever, query: str) -> None:
    """Demo GraphRAG search with LLM answer generation."""
    print(f"\n--- GraphRAG Search ---")
    print(f"Query: {query}\n")

    rag = GraphRAG(llm=llm, retriever=retriever)
    response = rag.search(query, retriever_config={"top_k": 5}, return_context=True)
    print(f"Number of results returned: {len(response.retriever_result.items)}\n")
    print(f"Answer: {response.answer}")


def main():
    """Run vector retriever demos."""
    with get_neo4j_driver() as driver:
        embedder = get_embedder()
        llm = get_llm()
        retriever = create_vector_retriever(driver, embedder)

        # Demo 1: GraphRAG search with LLM
        demo_rag_search(llm, retriever, "What companies mention AI in their filings?")

        # Demo 2: Another GraphRAG example
        demo_rag_search(llm, retriever, "What products does Microsoft reference?")


if __name__ == "__main__":
    main()


# Example queries to try:
# - What are the risks that Apple faces?
# - What products does Microsoft reference?
# - What warnings have Nvidia given?
# - What companies mention AI in their filings?
