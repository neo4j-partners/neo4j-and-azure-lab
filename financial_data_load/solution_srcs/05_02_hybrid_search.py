"""
Hybrid Search with Neo4j GraphRAG

Demonstrates Neo4j's official hybrid search using the HybridRetriever and
HybridCypherRetriever classes from the neo4j-graphrag package.

How Hybrid Search Works:
1. Query executes against both vector and fulltext indexes simultaneously
2. Each index returns results with relevance scores
3. Scores are normalized for comparability
4. Results are merged and deduplicated
5. Combined scores are ranked using the alpha parameter
6. Top-k results are returned

Alpha Parameter:
- alpha=1.0: Pure vector (semantic) search
- alpha=0.5: Equal weight to both
- alpha=0.0: Pure fulltext (keyword) search

References:
- https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_rag.html
- https://neo4j.com/blog/developer/hybrid-retrieval-graphrag-python-package/

Usage:
    uv run python solutions/05_02_hybrid_search.py
"""

import neo4j
from neo4j_graphrag.retrievers import HybridRetriever, HybridCypherRetriever
from neo4j_graphrag.types import RetrieverResultItem

from config import get_neo4j_driver, get_embedder

# Index names
# HybridRetriever requires both indexes to be on the SAME node type
# - Vector index: on Chunk.embedding (semantic similarity)
# - Fulltext index: on Chunk.text (keyword matching)
VECTOR_INDEX = "chunkEmbeddings"
FULLTEXT_INDEX = "chunkText"

# Retrieval query for HybridCypherRetriever
# This runs AFTER hybrid search finds matching Chunk nodes
# 'node' = matched Chunk, 'score' = combined hybrid score
RETRIEVAL_QUERY = """
// Get document from chunk
MATCH (node)-[:FROM_DOCUMENT]->(doc:Document)

// Find companies mentioned in this chunk
OPTIONAL MATCH (company:Company)-[:FROM_CHUNK]->(node)

// Get risk factors for context (if company found)
OPTIONAL MATCH (company)-[:FACES_RISK]->(risk:RiskFactor)

// Get products mentioned in same chunk
OPTIONAL MATCH (product:Product)-[:FROM_CHUNK]->(node)

// Explicit grouping before aggregations for modern Cypher compliance
WITH node.text AS text,
     score,
     company.name AS company,
     doc.path AS document,
     collect(DISTINCT risk.name)[0..3] AS risks,
     collect(DISTINCT product.name)[0..3] AS products

// Return enriched results
RETURN text,
       score,
       company,
       document,
       risks,
       products
"""


def format_hybrid_cypher_result(record: neo4j.Record) -> RetrieverResultItem:
    """
    Format HybridCypherRetriever results for easy access.

    This is the recommended pattern from Neo4j for customizing retriever output.
    The function receives a neo4j.Record with keys matching the RETURN clause
    of the retrieval query.

    Reference: neo4j-graphrag-python/examples/customize/retrievers/result_formatter_vector_cypher_retriever.py
    """
    return RetrieverResultItem(
        content={
            "text": record.get("text", ""),
            "company": record.get("company", "N/A"),
            "document": record.get("document", ""),
            "risks": record.get("risks", []),
            "products": record.get("products", []),
        },
        metadata={"score": record.get("score", 0.0)},
    )


def basic_hybrid_search(retriever: HybridRetriever, query: str) -> None:
    """
    Pattern 1: Basic hybrid search using HybridRetriever.

    The HybridRetriever automatically:
    - Searches both vector and fulltext indexes
    - Normalizes scores for fair comparison
    - Merges and deduplicates results
    - Ranks by combined score
    """
    print(f"\n=== Basic Hybrid Search ===")
    print(f"Query: '{query}'")

    results = retriever.search(query_text=query, top_k=5)

    print(f"Found {len(results.items)} results\n")
    for i, item in enumerate(results.items, 1):
        score = item.metadata.get("score", "N/A")
        text = item.content[:150] if isinstance(item.content, str) else str(item.content)[:150]
        print(f"{i}. Score: {score}")
        print(f"   {text}...\n")


def alpha_comparison(retriever: HybridRetriever, query: str) -> None:
    """
    Pattern 2: Compare different alpha values.

    Alpha controls the balance between vector and fulltext:
    combined_score = alpha * vector_score + (1 - alpha) * fulltext_score
    """
    print(f"\n=== Alpha Comparison ===")
    print(f"Query: '{query}'")

    for alpha in [1.0, 0.5, 0.0]:
        label = {1.0: "Pure Vector", 0.5: "Balanced", 0.0: "Pure Fulltext"}[alpha]

        results = retriever.search(query_text=query, top_k=3, alpha=alpha)

        print(f"\n--- Alpha={alpha} ({label}) ---")
        for i, item in enumerate(results.items, 1):
            text = item.content[:100] if isinstance(item.content, str) else str(item.content)[:100]
            print(f"{i}. {text}...")


def graph_enhanced_search(retriever: HybridCypherRetriever, query: str) -> None:
    """
    Pattern 3: Hybrid search with graph traversal using HybridCypherRetriever.

    Extends hybrid search by:
    1. First finding relevant nodes via hybrid search
    2. Then traversing the graph to gather related context
    3. Returning enriched results with company, risks, products

    The result_formatter converts neo4j.Record to RetrieverResultItem with:
    - content: dict with text, company, risks, products
    - metadata: dict with score
    """
    print(f"\n=== Graph-Enhanced Hybrid Search ===")
    print(f"Query: '{query}'")

    results = retriever.search(query_text=query, top_k=5)

    print(f"\nFound {len(results.items)} results\n")
    for i, item in enumerate(results.items, 1):
        # content is a dict from our result_formatter
        content = item.content if isinstance(item.content, dict) else {}
        # score is in metadata from our result_formatter
        score = item.metadata.get("score", "N/A") if item.metadata else "N/A"

        print(f"{i}. Company: {content.get('company', 'N/A')}")
        print(f"   Score: {score}")

        text = content.get("text", "")
        print(f"   Text: {text[:120]}...")

        risks = content.get("risks", [])
        if risks:
            print(f"   Risks: {', '.join(risks)}")

        products = content.get("products", [])
        if products:
            print(f"   Products: {', '.join(products)}")
        print()


def search_method_comparison(retriever: HybridRetriever, query: str) -> None:
    """
    Pattern 4: Compare vector-only, fulltext-only, and hybrid search.

    Demonstrates when hybrid outperforms single methods:
    - Queries with specific names/terms benefit from fulltext
    - Queries with semantic concepts benefit from vector
    - Hybrid combines both advantages
    """
    print(f"\n=== Search Method Comparison ===")
    print(f"Query: '{query}'")
    print("=" * 60)

    # Pure Vector
    print("\n[VECTOR ONLY - alpha=1.0]")
    print("Finds semantically similar content, may miss exact terms\n")
    results = retriever.search(query_text=query, top_k=2, alpha=1.0)
    for item in results.items:
        text = item.content[:100] if isinstance(item.content, str) else str(item.content)[:100]
        print(f"  - {text}...")

    # Pure Fulltext
    print("\n[FULLTEXT ONLY - alpha=0.0]")
    print("Matches keywords exactly, may miss semantic meaning\n")
    results = retriever.search(query_text=query, top_k=2, alpha=0.0)
    for item in results.items:
        text = item.content[:100] if isinstance(item.content, str) else str(item.content)[:100]
        print(f"  - {text}...")

    # Hybrid
    print("\n[HYBRID - alpha=0.5]")
    print("Combines both: exact matches + semantic relevance\n")
    results = retriever.search(query_text=query, top_k=2, alpha=0.5)
    for item in results.items:
        text = item.content[:100] if isinstance(item.content, str) else str(item.content)[:100]
        print(f"  - {text}...")


def main() -> None:
    """Run all hybrid search examples."""
    with get_neo4j_driver() as driver:
        driver.verify_connectivity()
        print("Connected to Neo4j")

        # Initialize embedder
        embedder = get_embedder()
        print(f"Embedder: {embedder.model}")

        # Check indexes exist
        with driver.session() as session:
            # Check fulltext index on Chunk.text (required for hybrid search)
            result = session.run(
                "SHOW FULLTEXT INDEXES YIELD name WHERE name = $name RETURN name",
                name=FULLTEXT_INDEX,
            )
            if not result.single():
                print(f"\nError: Fulltext index '{FULLTEXT_INDEX}' not found.")
                print("Run: uv run python full_data_load.py to create indexes.")
                return

            # Check vector index
            result = session.run(
                "SHOW VECTOR INDEXES YIELD name WHERE name = $name RETURN name",
                name=VECTOR_INDEX,
            )
            if not result.single():
                print(f"\nError: Vector index '{VECTOR_INDEX}' not found.")
                print("Run: uv run python full_data_load.py to create indexes.")
                return

        # Create HybridRetriever
        # This is the basic hybrid retriever that combines vector + fulltext search
        hybrid_retriever = HybridRetriever(
            driver=driver,
            vector_index_name=VECTOR_INDEX,
            fulltext_index_name=FULLTEXT_INDEX,
            embedder=embedder,
            return_properties=["text"],
        )

        # Create HybridCypherRetriever
        # This extends hybrid search with graph traversal
        # Uses result_formatter to convert neo4j.Record to structured dict
        hybrid_cypher_retriever = HybridCypherRetriever(
            driver=driver,
            vector_index_name=VECTOR_INDEX,
            fulltext_index_name=FULLTEXT_INDEX,
            retrieval_query=RETRIEVAL_QUERY,
            embedder=embedder,
            result_formatter=format_hybrid_cypher_result,
        )

        # Run examples
        basic_hybrid_search(hybrid_retriever, "supply chain risks and disruptions")
        alpha_comparison(hybrid_retriever, "Apple financial risks")
        graph_enhanced_search(hybrid_cypher_retriever, "artificial intelligence")
        search_method_comparison(hybrid_retriever, "Microsoft cloud computing strategy")

    print("\nConnection closed")


if __name__ == "__main__":
    main()
