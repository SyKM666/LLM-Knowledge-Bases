# Vector Databases

Vector databases are specialized database systems designed to store, index, and query high-dimensional vector embeddings efficiently. They enable similarity search over dense vector representations produced by modern embedding models, making them a critical component in semantic search, recommendation systems, and retrieval-augmented generation pipelines.

## Why Vector Databases?

Traditional databases rely on exact match or keyword-based search. With the rise of embedding models (e.g., sentence-transformers, OpenAI embeddings), data is increasingly represented as dense vectors. Vector databases are purpose-built to perform similarity search over these embeddings, bridging the gap between raw data and meaningful, context-aware retrieval.

## Key Operations

- **Insert** — Store vectors with associated metadata.
- **Search** — Find the nearest neighbors to a query vector using approximate nearest neighbor (ANN) techniques.
- **Filter** — Combine vector similarity with metadata filtering for more targeted results.

## Popular Solutions

| Solution | Type | Notes |
|---|---|---|
| **Pinecone** | Fully managed | Cloud-native, minimal operational overhead |
| **Weaviate** | Open-source | Supports hybrid search (vector + keyword) |
| **Milvus** | Open-source | Highly scalable for large datasets |
| **Chroma** | Open-source | Lightweight and developer-friendly |
| **FAISS** | Library (not a database) | Built by Meta for efficient similarity search |
| **pgvector** | PostgreSQL extension | Adds vector operations to an existing RDBMS |

## ANN Algorithms

- **HNSW (Hierarchical Navigable Small World)** — Graph-based approach offering high recall.
- **IVF (Inverted File Index)** — Partition-based method well-suited for large datasets.
- **PQ (Product Quantization)** — Compression technique that improves memory efficiency.

## Use Cases

- **Semantic search** — Finding results by meaning rather than exact keywords.
- **RAG (Retrieval-Augmented Generation)** — Serving as the retrieval backend that grounds language model responses in real data.
- **Recommendation systems** — Surfacing similar items based on learned representations.
- **Image/audio similarity search** — Matching across non-text modalities.
- **Anomaly detection** — Identifying outliers in high-dimensional space.

## Design Considerations

- **Dimensionality** affects both performance and storage; typical embeddings range from 384 to 1536 dimensions.
- **Index build time vs. query latency** — Faster indexing may come at the cost of slower or less accurate queries, and vice versa.
- **Consistency models** vary across solutions, from eventual consistency to strong consistency.
- **Cost** scales with vector count and dimensionality, making capacity planning important for production workloads.

## Categories

Databases, Machine Learning Infrastructure, Information Retrieval, Embeddings, Semantic Search, AI Tooling

## See Also

- [[rag-retrieval-augmented-generation]]
- [[transformer-architecture]]