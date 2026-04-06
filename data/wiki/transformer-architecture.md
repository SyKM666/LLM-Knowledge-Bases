# Transformer Architecture

The Transformer is a deep learning model architecture introduced in the landmark paper "Attention Is All You Need" (Vaswani et al., 2017). It relies entirely on self-attention mechanisms, dispensing with recurrence and convolutions, and has become the foundation for virtually all modern large language models and beyond.

## Key Components

### Self-Attention

The core mechanism computes attention weights between all pairs of positions in a sequence. Given queries Q, keys K, and values V:

**Attention(Q, K, V) = softmax(QK^T / √d_k) V**

The scaling factor √d_k prevents dot products from growing too large, which would push the softmax into regions with extremely small gradients.

### Multi-Head Attention

Instead of performing a single attention function, the model projects Q, K, and V into *h* different subspaces and computes attention in parallel. The results are then concatenated and projected. This allows the model to jointly attend to information from different representation subspaces at different positions.

### Position-wise Feed-Forward Networks

Each layer contains a fully connected feed-forward network applied to each position separately and identically:

**FFN(x) = max(0, xW₁ + b₁)W₂ + b₂**

### Positional Encoding

Since the model contains no recurrence or convolution, positional encodings are added to input embeddings to inject sequence order information. The original paper uses sinusoidal functions of varying frequencies.

## Architecture Overview

The Transformer follows an encoder-decoder structure:

- **Encoder**: 6 identical layers, each consisting of multi-head self-attention followed by a position-wise feed-forward network.
- **Decoder**: 6 identical layers, each consisting of masked self-attention, encoder-decoder attention, and a position-wise feed-forward network.
- Both the encoder and decoder use **residual connections** and **layer normalization** around each sub-layer.

## Impact

The Transformer has become the foundation for virtually all modern NLP models, including BERT, GPT, and T5. Its influence has expanded well beyond natural language processing into computer vision (Vision Transformer / ViT), audio processing, and multimodal tasks.

## Categories

Deep Learning, Model Architecture, Attention Mechanisms, Natural Language Processing, Neural Networks

## See Also

- [[rag-retrieval-augmented-generation]]
- [[vector-databases]]