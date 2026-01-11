# RAG Pipeline for Local Markdown Files

A RAG (Retrieval-Augmented Generation) pipeline for indexing and searching local Markdown documents using FAISS and AI Builder Space API.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements_faiss.txt

# 2. Set API key
# Windows (PowerShell):
$env:AI_BUILDER_TOKEN="your-token-here"
# Mac/Linux:
export AI_BUILDER_TOKEN="your-token-here"

# 3. Prepare documents
mkdir docs
# Add your .md files to the docs folder

# 4. Build index
python indexer.py --dir docs --output my_notes.index
```

## Project Structure

```
doc-retrival/
├── README.md              # This file
├── indexer.py             # Main indexer script
├── requirements_faiss.txt # Dependencies
├── refresh_index.ps1      # Windows refresh script
├── refresh_index.sh       # Mac/Linux refresh script
└── docs/                  # Your Markdown files go here
```

## Features

- ✅ **High performance** - Optimized vector search with FAISS
- ✅ **Full control** - Customize chunking and indexing
- ✅ **Lightweight** - Minimal dependencies
- ✅ **Scalable** - Handles large document collections
- ✅ **Uses AI Builder Space API** - For embeddings and LLM

## Usage

### Build Index

```bash
# Basic usage (searches 'docs' folder, saves to 'my_notes.index')
python indexer.py

# Custom directory and output
python indexer.py --dir "path/to/notes" --output "custom.index"

# Customize chunking
python indexer.py --chunk-size 1024 --overlap 100
```

### Update Index

When you add new files, rebuild the index:

**Windows:**
```powershell
.\refresh_index.ps1
```

**Mac/Linux:**
```bash
./refresh_index.sh
```

## Integration with FastAPI

This indexer is part of the FastAPI monorepo. The FastAPI app will automatically load `my_notes.index` from this directory and use it for the `query_my_notes` tool.

## Platform Support

The code is **fully cross-platform**. Works on Windows, Mac, and Linux. Only command syntax differs (PowerShell vs bash).
