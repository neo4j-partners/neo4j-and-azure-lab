"""
Entity Extraction Basics

This solution demonstrates entity extraction using SimpleKGPipeline
to build a knowledge graph from text.

Run with: uv run python main.py solutions 3
"""

import asyncio

from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline

from config import get_neo4j_driver, get_llm, get_embedder

# Sample text representing SEC 10-K filing content
SAMPLE_TEXT = """
Apple Inc. ("Apple" or the "Company") designs, manufactures and markets smartphones,
personal computers, tablets, wearables and accessories, and sells a variety of related
services. The Company's fiscal year is the 52- or 53-week period that ends on the last
Saturday of September.

Products

iPhone is the Company's line of smartphones based on its iOS operating system. The iPhone
product line includes iPhone 14 Pro, iPhone 14, iPhone 13 and iPhone SE. Mac is the Company's
line of personal computers based on its macOS operating system. iPad is the Company's line
of multi-purpose tablets based on its iPadOS operating system.

Services

Advertising includes third-party licensing arrangements and the Company's own advertising
platforms. AppleCare offers a portfolio of fee-based service and support products. Cloud
Services store and keep customers' content up-to-date across all devices. Digital Content
operates various platforms for discovering, purchasing, streaming and downloading digital
content and apps. Payment Services include Apple Card and Apple Pay.
""".strip()

# Schema definition
ENTITY_TYPES = [
    {"label": "Company", "description": "A company or organization"},
    {"label": "Product", "description": "A product offered by a company"},
    {"label": "Service", "description": "A service offered by a company"},
]

RELATIONSHIP_TYPES = [
    {"label": "OFFERS_PRODUCT", "description": "Company offers a product"},
    {"label": "OFFERS_SERVICE", "description": "Company offers a service"},
]

PATTERNS = [
    ("Company", "OFFERS_PRODUCT", "Product"),
    ("Company", "OFFERS_SERVICE", "Service"),
]


def clear_graph(driver) -> int:
    """Remove all nodes from previous runs."""
    with driver.session() as session:
        result = session.run("""
            MATCH (n)
            DETACH DELETE n
            RETURN count(n) as deleted
        """)
        return result.single()["deleted"]


def show_entities(driver) -> None:
    """Display extracted entities by type."""
    with driver.session() as session:
        # Get entity counts - using modern label expressions and explicit grouping
        result = session.run("""
            MATCH (n:Company|Product|Service)
            WITH labels(n)[0] as label
            RETURN label, count(*) as count
            ORDER BY count DESC
        """)
        print("\n=== Entity Counts ===")
        for record in result:
            print(f"  {record['label']}: {record['count']}")

        # List entities by type - with null filtering on sorted property
        for label in ["Company", "Product", "Service"]:
            result = session.run(f"""
                MATCH (n:{label})
                WHERE n.name IS NOT NULL
                RETURN n.name as name
                ORDER BY n.name
                LIMIT 10
            """)
            names = [record["name"] for record in result]
            if names:
                print(f"\n=== {label} Entities ===")
                for name in names:
                    print(f"  - {name}")


def show_relationships(driver) -> None:
    """Display extracted relationships."""
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Company)-[r]->(target)
            WHERE type(r) IN ['OFFERS_PRODUCT', 'OFFERS_SERVICE']
            RETURN c.name as company, type(r) as relationship,
                   labels(target)[0] as target_type, target.name as target_name
            ORDER BY c.name, type(r)
            LIMIT 20
        """)

        print("\n=== Extracted Relationships ===")
        for record in result:
            print(f"  ({record['company']}) -[{record['relationship']}]-> "
                  f"({record['target_type']}: {record['target_name']})")


def show_graph_summary(driver) -> None:
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
        print("\n=== Node Counts ===")
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


def find_chunks_for_entity(driver, entity_name: str) -> None:
    """Find chunks that mention a specific entity."""
    with driver.session() as session:
        # Entities point TO chunks via FROM_CHUNK (matches notebook pattern)
        result = session.run("""
            MATCH (e)-[:FROM_CHUNK]->(c:Chunk)
            WHERE e.name CONTAINS $name
            RETURN e.name as entity, labels(e)[0] as type, c.text as chunk_text
            LIMIT 5
        """, name=entity_name)

        records = list(result)
        if records:
            print(f"\nChunks mentioning '{entity_name}':")
            for record in records:
                print(f"  Entity: {record['entity']} ({record['type']})")
                print(f"  Chunk: {record['chunk_text']}")
        else:
            print(f"\nNo chunks found mentioning '{entity_name}'")


async def main():
    """Run entity extraction demo."""
    with get_neo4j_driver() as driver:
        driver.verify_connectivity()
        print("Connected to Neo4j successfully!")

        # Clear all existing data (SimpleKGPipeline creates everything fresh)
        deleted = clear_graph(driver)
        print(f"Deleted {deleted} nodes")

        # Initialize LLM and embedder
        print("\nInitializing LLM and embedder...")
        llm = get_llm()
        embedder = get_embedder()
        print(f"LLM: {llm.model_name}")
        print(f"Embedder: {embedder.model}")

        # Create pipeline
        print("\nCreating SimpleKGPipeline...")
        pipeline = SimpleKGPipeline(
            llm=llm,
            driver=driver,
            embedder=embedder,
            schema={
                "node_types": ENTITY_TYPES,
                "relationship_types": RELATIONSHIP_TYPES,
                "patterns": PATTERNS,
            },
            from_pdf=False,
            on_error="IGNORE",
        )
        print("Pipeline created successfully!")

        # Run extraction
        print("\nRunning entity extraction...")
        print("(This may take 30-60 seconds)")
        result = await pipeline.run_async(text=SAMPLE_TEXT)
        print("Entity extraction complete!")

        # Show results
        show_entities(driver)
        show_relationships(driver)
        show_graph_summary(driver)

        # Demo finding chunks for entities
        print("\n=== Find Chunks for Entities ===")
        find_chunks_for_entity(driver, "iPhone")
        find_chunks_for_entity(driver, "Apple")

    print("\n\nConnection closed.")


if __name__ == "__main__":
    asyncio.run(main())
