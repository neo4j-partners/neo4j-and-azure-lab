"""
Embeddings and Vector Search

This solution demonstrates embedding generation and vector similarity
search using Neo4j and Microsoft Foundry.

Run with: uv run python main.py solutions 2
"""

import asyncio

from neo4j_graphrag.indexes import create_vector_index
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import (
    FixedSizeSplitter,
)

from config import get_neo4j_driver, get_embedder

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
INDEX_NAME = "chunkEmbeddings"


def clear_graph(driver) -> int:
    """Remove all Document and Chunk nodes."""
    with driver.session() as session:
        result = session.run("""
            MATCH (n) WHERE n:Document OR n:Chunk
            DETACH DELETE n
            RETURN count(n) as deleted
        """)
        return result.single()["deleted"]


async def split_text(text: str, chunk_size: int = 400, overlap: int = 50):
    """Split text using FixedSizeSplitter."""
    splitter = FixedSizeSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return await splitter.run(text=text)


def generate_embeddings(embedder, chunks) -> list[dict]:
    """Generate embeddings for each chunk."""
    chunk_data = []
    for i, chunk in enumerate(chunks.chunks):
        embedding = embedder.embed_query(chunk.text)
        chunk_data.append({
            "text": chunk.text,
            "index": i,
            "embedding": embedding
        })
    return chunk_data


def store_chunks_with_embeddings(driver, doc_path: str, chunk_data: list[dict]) -> None:
    """Store Document and Chunk nodes with embeddings."""
    with driver.session() as session:
        # Create Document
        session.run("CREATE (d:Document {path: $path})", path=doc_path)

        # Create Chunks with embeddings
        for chunk in chunk_data:
            session.run("""
                MATCH (d:Document {path: $path})
                CREATE (c:Chunk {
                    text: $text,
                    index: $index,
                    embedding: $embedding
                })
                CREATE (c)-[:FROM_DOCUMENT]->(d)
            """, path=doc_path, text=chunk["text"],
                index=chunk["index"], embedding=chunk["embedding"])

        # Create NEXT_CHUNK relationships
        session.run("""
            MATCH (d:Document {path: $path})<-[:FROM_DOCUMENT]-(c:Chunk)
            WITH c ORDER BY c.index
            WITH collect(c) as chunks
            UNWIND range(0, size(chunks)-2) as i
            WITH chunks[i] as c1, chunks[i+1] as c2
            CREATE (c1)-[:NEXT_CHUNK]->(c2)
        """, path=doc_path)


def create_index(driver) -> None:
    """Create vector index for similarity search."""
    # Drop existing index
    try:
        with driver.session() as session:
            session.run(f"DROP INDEX {INDEX_NAME} IF EXISTS")
    except Exception:
        pass

    # Create new index
    create_vector_index(
        driver=driver,
        name=INDEX_NAME,
        label="Chunk",
        embedding_property="embedding",
        dimensions=1536,
        similarity_fn="cosine"
    )


def vector_search(driver, embedder, query: str, top_k: int = 3) -> list:
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


def demo_search(driver, embedder) -> None:
    """Demo vector similarity search."""
    queries = [
        "What products does Apple make?",
        "Tell me about iPhone and Mac computers",
        "What services does the company offer?",
        "When does the fiscal year end?"
    ]

    for query in queries:
        print(f"\nQuery: \"{query}\"")
        print("-" * 50)
        results = vector_search(driver, embedder, query, top_k=1)
        if results:
            record = results[0]
            print(f"Best match (score: {record['score']:.4f}):")
            print(f"  {record['text']}")


async def main():
    """Run embeddings demo."""
    with get_neo4j_driver() as driver:
        driver.verify_connectivity()
        print("Connected to Neo4j successfully!")

        # Clear existing data
        deleted = clear_graph(driver)
        print(f"Deleted {deleted} existing nodes")

        # Split text
        print("\nSplitting text...")
        chunks = await split_text(SAMPLE_TEXT)
        print(f"Split into {len(chunks.chunks)} chunks")

        # Generate embeddings
        print("\nGenerating embeddings...")
        embedder = get_embedder()
        chunk_data = generate_embeddings(embedder, chunks)
        print(f"Generated embeddings for {len(chunk_data)} chunks")
        print(f"Embedding dimensions: {len(chunk_data[0]['embedding'])}")

        # Store in Neo4j
        print("\nStoring in Neo4j...")
        store_chunks_with_embeddings(driver, DOCUMENT_PATH, chunk_data)
        print("Stored Document and Chunk nodes with embeddings")

        # Create index
        print("\nCreating vector index...")
        create_index(driver)
        print(f"Created vector index: {INDEX_NAME}")

        # Demo search
        print("\n=== Vector Search Demo ===")
        demo_search(driver, embedder)

    print("\n\nConnection closed.")


if __name__ == "__main__":
    asyncio.run(main())
