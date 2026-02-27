"""
Fulltext Search Examples

Demonstrates Neo4j fulltext search capabilities for keyword-based
entity search across Company, Product, and RiskFactor names.

Usage:
    uv run python main.py solutions 12
"""

from neo4j import Driver

from config import get_neo4j_driver


def basic_search(driver: Driver, term: str) -> None:
    """Basic keyword search."""
    print(f"\n=== Basic Search: '{term}' ===")
    with driver.session() as session:
        result = session.run(
            """
            CALL db.index.fulltext.queryNodes('search_entities', $term)
            YIELD node, score
            RETURN labels(node) AS labels, node.name AS name, score
            LIMIT 10
            """,
            term=term,
        )
        for record in result:
            print(f"  [{record['labels'][0]}] {record['name']} (score: {record['score']:.4f})")


def fuzzy_search(driver: Driver, term: str) -> None:
    """Fuzzy search with typo tolerance."""
    print(f"\n=== Fuzzy Search: '{term}' ===")
    with driver.session() as session:
        result = session.run(
            """
            CALL db.index.fulltext.queryNodes('search_entities', $term)
            YIELD node, score
            RETURN labels(node) AS labels, node.name AS name, score
            LIMIT 5
            """,
            term=term,
        )
        for record in result:
            print(f"  [{record['labels'][0]}] {record['name']} (score: {record['score']:.4f})")


def wildcard_search(driver: Driver, term: str) -> None:
    """Wildcard prefix search."""
    print(f"\n=== Wildcard Search: '{term}' ===")
    with driver.session() as session:
        result = session.run(
            """
            CALL db.index.fulltext.queryNodes('search_entities', $term)
            YIELD node, score
            RETURN labels(node) AS labels, node.name AS name, score
            LIMIT 10
            """,
            term=term,
        )
        for record in result:
            print(f"  [{record['labels'][0]}] {record['name']} (score: {record['score']:.4f})")


def boolean_search(driver: Driver, term: str) -> None:
    """Boolean operator search."""
    print(f"\n=== Boolean Search: '{term}' ===")
    with driver.session() as session:
        result = session.run(
            """
            CALL db.index.fulltext.queryNodes('search_entities', $term)
            YIELD node, score
            RETURN labels(node) AS labels, node.name AS name, score
            LIMIT 10
            """,
            term=term,
        )
        for record in result:
            print(f"  [{record['labels'][0]}] {record['name']} (score: {record['score']:.4f})")


def search_with_graph_traversal(driver: Driver, company_name: str) -> None:
    """Search company and traverse to related entities."""
    print(f"\n=== Graph Traversal: '{company_name}' ===")
    with driver.session() as session:
        # Traverse from Company to Documents via chunks
        # Path: (Company)-[:FROM_CHUNK]->(Chunk)-[:FROM_DOCUMENT]->(Document)
        result = session.run(
            """
            CALL db.index.fulltext.queryNodes('search_entities', $term)
            YIELD node, score
            WHERE 'Company' IN labels(node)
            WITH node AS company, score
            LIMIT 1

            OPTIONAL MATCH (company)-[:FROM_CHUNK]->(chunk:Chunk)-[:FROM_DOCUMENT]->(doc:Document)
            WITH company, score, collect(DISTINCT doc.path)[0..10] AS documents

            OPTIONAL MATCH (company)-[:FACES_RISK]->(risk:RiskFactor)
            WITH company, score, documents, collect(DISTINCT risk.name)[0..5] AS risks

            RETURN company.name AS company, score, documents, risks
            """,
            term=company_name,
        )

        record = result.single()
        if record:
            print(f"Company: {record['company']} (score: {record['score']:.4f})")
            print("Related Documents:")
            for doc in record["documents"]:
                print(f"  - {doc}")
            print("Risk Factors:")
            for risk in record["risks"]:
                print(f"  - {risk}")
        else:
            print(f"No company found for '{company_name}'")


def hybrid_search(driver: Driver, keyword: str) -> None:
    """Hybrid search combining fulltext with graph patterns."""
    print(f"\n=== Hybrid Search: '{keyword}' ===")
    with driver.session() as session:
        # Find company by keyword, then get chunks where it was mentioned
        # Path: (Company)-[:FROM_CHUNK]->(Chunk)
        result = session.run(
            """
            CALL db.index.fulltext.queryNodes('search_entities', $keyword)
            YIELD node AS entity, score AS keyword_score
            WHERE 'Company' IN labels(entity)
            WITH entity, keyword_score
            LIMIT 1

            MATCH (entity)-[:FROM_CHUNK]->(chunk:Chunk)
            WHERE chunk.text IS NOT NULL

            RETURN entity.name AS company,
                   keyword_score,
                   chunk.text AS text
            LIMIT 5
            """,
            keyword=keyword,
        )

        for record in result:
            print(f"\n[{record['company']}] (score: {record['keyword_score']:.4f})")
            print(f"  {record['text'][:200]}...")


def main() -> None:
    """Run all fulltext search examples."""
    with get_neo4j_driver() as driver:
        driver.verify_connectivity()
        print("Connected to Neo4j")

        # Check if fulltext index exists
        with driver.session() as session:
            result = session.run(
                "SHOW FULLTEXT INDEXES YIELD name WHERE name = 'search_entities' RETURN name"
            )
            if not result.single():
                print("\nError: Fulltext index 'search_entities' not found.")
                print("Run: uv run python main.py load --clear")
                return

        # Run examples
        basic_search(driver, "Apple")
        fuzzy_search(driver, "Aplle~")
        wildcard_search(driver, "Micro*")
        boolean_search(driver, "supply NOT chain")
        search_with_graph_traversal(driver, "Nvidia")
        hybrid_search(driver, "Amazon")


if __name__ == "__main__":
    main()
