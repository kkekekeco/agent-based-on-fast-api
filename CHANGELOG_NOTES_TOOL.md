# Changelog: Added query_my_notes Tool

## Summary

Added a new tool `query_my_notes` to the FastAPI agentic chat application that enables the agent to search through the user's personal knowledge base (indexed Markdown notes).

## Changes Made

### 1. Dependencies (`requirements.txt`)
- Added `faiss-cpu>=1.7.4` for vector search
- Added `numpy>=1.24.0` for array operations

### 2. New Imports (`main.py`)
- `faiss` - FAISS library for vector similarity search
- `numpy as np` - NumPy for array operations
- `Path` from `pathlib` - For path handling

### 3. New Functions

#### `load_notes_index(index_path)`
- Loads the FAISS index and metadata at application startup
- Called automatically via `@app.on_event("startup")`
- Uses global variables `_notes_index`, `_notes_metadata`, `_notes_dimension`

#### `query_my_notes(query, top_k=5)`
- Searches the personal knowledge base using vector similarity
- Takes a query string and returns top-k most relevant note chunks
- Returns JSON string with results including:
  - Text content
  - Source file
  - Similarity score
  - Metadata (start/end positions)

### 4. Tool Definition

Added `query_my_notes` to the `tools` array with:
- **Name**: `query_my_notes`
- **Description**: Research assistant tool for personal knowledge base
- **Parameters**:
  - `query` (required): Search query string
  - `top_k` (optional, default: 5): Number of results to return

### 5. Updated System Prompt

Enhanced the agent's system prompt to:
- Treat `query_my_notes` as a research assistant for personal knowledge base
- **Autonomously** use the tool when questions might be answered by personal notes
- **Formulate targeted queries** that match the user's question
- **Call multiple times** with different queries to explore different aspects
- **Refine queries** based on previous results if needed
- **Combine information** from multiple searches

### 6. Tool Call Handling

Added handling for `query_my_notes` in the agent chat endpoint:
- Extracts `query` and `top_k` parameters
- Calls `query_my_notes()` function
- Adds tool output to message history
- Logs tool usage for debugging

### 7. Configuration

- **Index Path**: `../202601-doc-retrival/my_notes.index` (relative to FastAPI app)
- **Max Turns**: Increased from 3 to 5 to allow for iterative note searches
- **Version**: Updated to 4.0.0

## Usage

The agent will now automatically:
1. Detect when a question might be answered by personal notes
2. Formulate search queries
3. Call `query_my_notes` one or more times
4. Refine queries based on results if needed
5. Synthesize answers from note search results

## Example

**User**: "What did I write about RAG pipelines?"

**Agent Behavior**:
1. Recognizes this is about personal notes
2. Calls `query_my_notes("RAG pipelines")`
3. If results are insufficient, might call `query_my_notes("retrieval augmented generation")`
4. Combines results and provides answer with source citations

## Notes

- The index is loaded once at startup for performance
- If the index file is not found, the tool will return an error message
- The tool uses the same embedding model (`text-embedding-ada-002`) as the indexer
- Results are returned as JSON for the agent to parse and use
