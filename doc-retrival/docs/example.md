# Example Document

This is a sample Markdown document to demonstrate the RAG pipeline.

## Introduction

RAG (Retrieval-Augmented Generation) is a technique that combines information retrieval with language generation. It allows AI systems to answer questions based on specific documents rather than just their training data.

## Key Concepts

### Vector Embeddings

Documents are converted into vector embeddings, which are numerical representations that capture semantic meaning. Similar documents have similar vectors.

### Semantic Search

When you ask a question, the system:
1. Converts your question into a vector
2. Searches for similar document chunks
3. Uses those chunks as context for the LLM
4. Generates an answer based on the retrieved context

## Benefits

- **Accuracy**: Answers are grounded in your documents
- **Up-to-date**: Can use recent documents not in training data
- **Transparency**: Can show source documents
- **Privacy**: Can run completely locally

## Use Cases

- Document Q&A
- Knowledge base search
- Code documentation search
- Research paper analysis
