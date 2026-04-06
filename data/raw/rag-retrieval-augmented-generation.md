# Retrieval-Augmented Generation (RAG)

RAG is a technique that combines information retrieval with text generation. Instead of relying solely on a language model's parametric knowledge, RAG retrieves relevant documents from an external knowledge base and conditions the generation on them.

## How RAG Works

1. **Query Encoding**: The user's question is encoded into a dense vector representation.
2. **Retrieval**: The query vector is used to search a document index (e.g., FAISS, Elasticsearch) for the top-k most relevant passages.
3. **Augmented Generation**: The retrieved passages are concatenated with the original query and fed to a language model, which generates the final answer.

## Advantages
- Reduces hallucination by grounding responses in actual documents
- Knowledge can be updated by updating the document index, without retraining the model
- More transparent — sources can be cited

## Challenges
- Retrieval quality is a bottleneck; poor retrieval leads to poor generation
- Latency increases due to the retrieval step
- Chunk size and overlap strategies significantly affect performance
- The context window limits how many documents can be included

## Variations
- **Naive RAG**: Simple retrieve-then-generate pipeline
- **Advanced RAG**: Includes query rewriting, re-ranking, and iterative retrieval
- **Modular RAG**: Decomposable components that can be mixed and matched

## Relation to Fine-tuning
RAG and fine-tuning are complementary. Fine-tuning bakes knowledge into model weights; RAG provides dynamic, up-to-date context. Many production systems use both.
