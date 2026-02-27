"""
Data Loading Fundamentals

This solution demonstrates basic data loading into Neo4j,
creating Document and Chunk nodes with relationships.

Run with: uv run python main.py solutions 1
"""

from config import get_neo4j_driver

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

DOCUMENT_PATH = "form10k-sample/apple-2023-10k.pdf"
DOCUMENT_PAGE = 1


def clear_graph(driver) -> int:
    """Remove all Document and Chunk nodes."""
    with driver.session() as session:
        result = session.run("""
            MATCH (n) WHERE n:Document OR n:Chunk
            DETACH DELETE n
            RETURN count(n) as deleted
        """)
        return result.single()["deleted"]


def split_into_chunks(text: str) -> list[str]:
    """Split text into chunks by double newlines (paragraphs)."""
    return [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]


def create_document(driver, path: str, page: int) -> str:
    """Create a Document node and return its element ID."""
    with driver.session() as session:
        result = session.run("""
            CREATE (d:Document {path: $path, page: $page})
            RETURN elementId(d) as doc_id
        """, path=path, page=page)
        return result.single()["doc_id"]


def create_chunks(driver, doc_id: str, chunks: list[str]) -> list[str]:
    """Create Chunk nodes linked to a Document. Returns chunk element IDs."""
    chunk_ids = []
    with driver.session() as session:
        for index, text in enumerate(chunks):
            result = session.run("""
                MATCH (d:Document) WHERE elementId(d) = $doc_id
                CREATE (c:Chunk {text: $text, index: $index})
                CREATE (c)-[:FROM_DOCUMENT]->(d)
                RETURN elementId(c) as chunk_id
            """, doc_id=doc_id, text=text, index=index)
            chunk_ids.append(result.single()["chunk_id"])
    return chunk_ids


def link_chunks(driver, chunk_ids: list[str]) -> int:
    """Create NEXT_CHUNK relationships between sequential chunks."""
    with driver.session() as session:
        for i in range(len(chunk_ids) - 1):
            session.run("""
                MATCH (c1:Chunk) WHERE elementId(c1) = $id1
                MATCH (c2:Chunk) WHERE elementId(c2) = $id2
                CREATE (c1)-[:NEXT_CHUNK]->(c2)
            """, id1=chunk_ids[i], id2=chunk_ids[i + 1])
    return len(chunk_ids) - 1


def show_graph_structure(driver) -> None:
    """Display the Document-Chunk graph structure."""
    with driver.session() as session:
        result = session.run("""
            MATCH (d:Document)
            OPTIONAL MATCH (d)<-[:FROM_DOCUMENT]-(c:Chunk)
            RETURN d.path as document, d.page as page, count(c) as chunks
        """)
        print("\n=== Graph Structure ===")
        for record in result:
            print(f"Document: {record['document']} (page {record['page']})")
            print(f"  Chunks: {record['chunks']}")

        result = session.run("""
            MATCH (c:Chunk)
            OPTIONAL MATCH (c)-[:NEXT_CHUNK]->(next:Chunk)
            RETURN c.index as idx,
                   c.text as text,
                   next.index as next_idx
            ORDER BY c.index
        """)
        print("\n=== Chunk Chain ===")
        for record in result:
            next_str = f" -> Chunk {record['next_idx']}" if record['next_idx'] is not None else " (end)"
            print(f"Chunk {record['idx']}: \"{record['text']}\"{next_str}")


def main():
    """Run data loading demo."""
    with get_neo4j_driver() as driver:
        driver.verify_connectivity()
        print("Connected to Neo4j successfully!")

        # Clear existing data
        deleted = clear_graph(driver)
        print(f"Deleted {deleted} existing nodes")

        # Split text into chunks
        chunks = split_into_chunks(SAMPLE_TEXT)
        print(f"\nSplit text into {len(chunks)} chunks")

        # Create document
        doc_id = create_document(driver, DOCUMENT_PATH, DOCUMENT_PAGE)
        print(f"Created Document node")

        # Create chunks
        chunk_ids = create_chunks(driver, doc_id, chunks)
        print(f"Created {len(chunk_ids)} Chunk nodes")

        # Link chunks
        links = link_chunks(driver, chunk_ids)
        print(f"Created {links} NEXT_CHUNK relationships")

        # Show structure
        show_graph_structure(driver)

    print("\nConnection closed.")


if __name__ == "__main__":
    main()
