"""
Full Dataset Exploration Queries

This script demonstrates various queries to explore the full Neo4j knowledge graph
containing SEC 10-K filings from multiple companies with extracted entities and relationships.

Prerequisites:
- Full dataset must be loaded (use full_data_load.py script)
- Neo4j connection configured in config.py
"""

from config import get_neo4j_driver, get_embedder


INDEX_NAME = "chunkEmbeddings"


def show_graph_summary(driver):
    """Show a summary of the complete graph."""
    with driver.session() as session:
        # Count all node types - with explicit grouping
        result = session.run("""
            MATCH (n)
            UNWIND labels(n) as label
            WITH label
            RETURN label, count(*) as count
            ORDER BY count DESC
        """)
        print("=== Node Counts ===")
        for record in result:
            print(f"  {record['label']}: {record['count']}")

        # Count relationship types - with explicit grouping
        result = session.run("""
            MATCH ()-[r]->()
            WITH type(r) as type
            RETURN type, count(*) as count
            ORDER BY count DESC
        """)
        print("\n=== Relationship Counts ===")
        for record in result:
            print(f"  {record['type']}: {record['count']}")


def vector_search(driver, embedder, query: str, top_k: int = 3):
    """Search for chunks similar to the query."""
    query_embedding = embedder.embed_query(query)

    with driver.session() as session:
        result = session.run("""
            CALL db.index.vector.queryNodes($index_name, $top_k, $embedding)
            YIELD node, score
            RETURN node.text as text, node.index as idx, score
            ORDER BY score DESC
        """, index_name=INDEX_NAME, top_k=top_k, embedding=query_embedding)

        return list(result)


def show_entities(driver):
    """Display extracted entities by type."""
    with driver.session() as session:
        # Get entity counts by label (excluding internal labels)
        result = session.run("""
            MATCH (n)
            WHERE NOT n:Chunk AND NOT n:Document AND NOT n:__KGBuilder__
            WITH labels(n) as lbls
            UNWIND lbls as label
            WITH label
            WHERE NOT label STARTS WITH '__'
            RETURN label, count(*) as count
            ORDER BY count DESC
            LIMIT 10
        """)
        print("=== Entity Counts (Top 10) ===")
        for record in result:
            print(f"  {record['label']}: {record['count']}")


def list_companies(driver):
    """List all Company entities."""
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Company)
            WHERE c.name IS NOT NULL
            RETURN c.name as name
            ORDER BY c.name
            LIMIT 20
        """)
        print("=== Companies ===")
        for record in result:
            print(f"  - {record['name']}")


def find_chunks_for_entity(driver, entity_name: str, limit: int = 5):
    """Find chunks that mention a specific entity."""
    with driver.session() as session:
        result = session.run("""
            MATCH (e)-[:FROM_CHUNK]->(c:Chunk)
            WHERE toUpper(e.name) CONTAINS toUpper($name)
            RETURN e.name as entity, labels(e)[0] as type, c.text as chunk_text
            LIMIT $limit
        """, name=entity_name, limit=limit)

        records = list(result)
        if records:
            print(f"=== Chunks mentioning '{entity_name}' ===")
            for i, record in enumerate(records):
                print(f"\n[{i+1}] Entity: {record['entity']} ({record['type']})")
                print(f"    Chunk: {record['chunk_text'][:200]}...")
        else:
            print(f"No chunks found mentioning '{entity_name}'")


def show_company_products(driver, company_name: str):
    """Show products related to a company via shared chunks."""
    with driver.session() as session:
        # Companies and Products are connected through shared chunks
        # (Company)-[:FROM_CHUNK]->(Chunk)<-[:FROM_CHUNK]-(Product)
        result = session.run("""
            MATCH (c:Company)-[:FROM_CHUNK]->(chunk:Chunk)<-[:FROM_CHUNK]-(p:Product)
            WHERE toUpper(c.name) CONTAINS toUpper($name)
              AND p.name IS NOT NULL
            WITH c.name AS company, p.name AS product
            RETURN DISTINCT company, product
            ORDER BY product
            LIMIT 20
        """, name=company_name)

        records = list(result)
        if records:
            print(f"=== Products from '{company_name}' ===")
            for record in records:
                print(f"  {record['company']} -> {record['product']}")
        else:
            print(f"No products found for '{company_name}'")


def main():
    # Setup connection
    print("Connecting to Neo4j...")
    with get_neo4j_driver() as driver:
        driver.verify_connectivity()
        print("Connected to Neo4j successfully!\n")

        # Initialize embedder
        embedder = get_embedder()
        print(f"Embedder initialized: {embedder.model}\n")

        # Show graph summary
        print("\n" + "="*60)
        print("GRAPH SUMMARY")
        print("="*60)
        show_graph_summary(driver)

        # Show entities
        print("\n" + "="*60)
        print("ENTITY EXPLORATION")
        print("="*60)
        show_entities(driver)
        print()
        list_companies(driver)

        # Vector search examples
        print("\n" + "="*60)
        print("VECTOR SEARCH EXAMPLES")
        print("="*60)
        queries = [
            "What products does Apple make?",
            "Tell me about iPhone and Mac computers",
            "What services does the company offer?",
            "When does the fiscal year end?"
        ]

        for query in queries:
            print(f"\nQuery: \"{query}\"")
            print("-" * 50)
            results = vector_search(driver, embedder, query, top_k=3)
            for i, record in enumerate(results):
                print(f"\n[{i+1}] Score: {record['score']:.4f}")
                print(f"    {record['text'][:200]}...")

        # Find chunks for entities
        print("\n" + "="*60)
        print("ENTITY-CHUNK RELATIONSHIPS")
        print("="*60)
        print()
        find_chunks_for_entity(driver, "iPhone", limit=3)
        print()
        find_chunks_for_entity(driver, "Microsoft", limit=3)
        print()
        find_chunks_for_entity(driver, "GPU", limit=3)

        # Show company products
        print("\n" + "="*60)
        print("COMPANY-PRODUCT RELATIONSHIPS")
        print("="*60)
        print()
        show_company_products(driver, "Apple")
        print()
        show_company_products(driver, "Microsoft")

    print("\n" + "="*60)
    print("Connection closed.")


if __name__ == "__main__":
    main()
