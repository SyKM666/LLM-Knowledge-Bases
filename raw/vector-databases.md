# Vector Databases

Vector databases are specialized database systems designed to store, index, and query high-dimensional vector embeddings efficiently.

## Why Vector Databases?

Traditional databases use exact match or keyword-based search. With the rise of embedding models (e.g., sentence-transformers, OpenAI embeddings), data is increasingly represented as dense vectors. Vector databases enable similarity search over these embeddings.

## Key Operations
- **Insert**: Store vectors with associated metadata
- **Search**: Find the nearest neighbors to a query vector (approximate nearest neighbor / ANN)
- **Filter**: Combine vector similarity with metadata filtering

## Popular Solutions
- **Pinecone**: Fully managed, cloud-native
- **Weaviate**: Open-source, supports hybrid search
- **Milvus**: Open-source, highly scalable
- **Chroma**: Lightweight, developer-friendly
- **FAISS**: Library (not a database) by Meta for efficient similarity search
- **pgvector**: PostgreSQL extension for vector operations

## ANN Algorithms
- HNSW (Hierarchical Navigable Small World): Graph-based, high recall
- IVF (Inverted File Index): Partition-based, good for large datasets
- PQ (Product Quantization): Compression technique for memory efficiency

## Use Cases
- Semantic search
- RAG (Retrieval-Augmented Generation) — the retrieval backend
- Recommendation systems
- Image/audio similarity search
- Anomaly detection

## Considerations
- Dimensionality affects performance (typical: 384-1536 dimensions)
- Index build time vs. query latency tradeoffs
- Consistency models vary (eventual vs. strong)
- Cost scales with vector count and dimensionality
