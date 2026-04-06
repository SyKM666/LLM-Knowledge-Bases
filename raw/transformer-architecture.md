# Transformer Architecture

The Transformer is a deep learning model architecture introduced in the paper "Attention Is All You Need" (Vaswani et al., 2017). It relies entirely on self-attention mechanisms, dispensing with recurrence and convolutions.

## Key Components

### Self-Attention
The core mechanism computes attention weights between all pairs of positions in a sequence. Given queries Q, keys K, and values V:

Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V

### Multi-Head Attention
Instead of performing a single attention function, the model projects Q, K, V into h different subspaces and computes attention in parallel, then concatenates and projects the results.

### Position-wise Feed-Forward Networks
Each layer contains a fully connected feed-forward network applied to each position separately:
FFN(x) = max(0, xW1 + b1)W2 + b2

### Positional Encoding
Since the model contains no recurrence, positional encodings are added to input embeddings to inject sequence order information. The original paper uses sinusoidal functions.

## Architecture Overview
- Encoder: 6 identical layers, each with multi-head self-attention + FFN
- Decoder: 6 identical layers, with masked self-attention + encoder-decoder attention + FFN
- Both use residual connections and layer normalization

## Impact
The Transformer has become the foundation for virtually all modern NLP models (BERT, GPT, T5, etc.) and is increasingly used in vision (ViT), audio, and multimodal tasks.
