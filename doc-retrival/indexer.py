"""
Standalone Indexer Script
Recursively indexes all .md files in a folder, creates embeddings, and builds a FAISS index.
"""

import os
import json
from pathlib import Path
from typing import List, Dict
import faiss
import numpy as np
from openai import OpenAI
import re


class MarkdownIndexer:
    """Indexer for Markdown files using FAISS and AI Builder Space API."""
    
    def __init__(self, api_key: str, base_url: str = "https://space.ai-builders.com/backend/v1"):
        """
        Initialize the indexer.
        
        Args:
            api_key: AI Builder Space API key
            base_url: Base URL for the API
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.base_url = base_url
        self.chunks = []  # Store document chunks with metadata
        self.embeddings = None
        self.index = None
        self.dimension = None
        
    def find_markdown_files(self, root_dir: str) -> List[Path]:
        """
        Recursively find all .md files in the specified directory.
        
        Args:
            root_dir: Root directory to search
            
        Returns:
            List of Path objects for all .md files found
        """
        root_path = Path(root_dir)
        if not root_path.exists():
            raise ValueError(f"Directory {root_dir} does not exist")
        
        md_files = list(root_path.rglob("*.md"))
        print(f"Found {len(md_files)} Markdown files in {root_dir}")
        return md_files
    
    def load_and_split_file(self, file_path: Path, chunk_size: int = 512, overlap: int = 50) -> List[Dict]:
        """
        Load a Markdown file and split it into chunks.
        
        Args:
            file_path: Path to the Markdown file
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of chunk dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        # Remove markdown formatting for cleaner text
        # Remove code blocks
        content = re.sub(r'```[\s\S]*?```', '', content)
        # Remove inline code
        content = re.sub(r'`[^`]+`', '', content)
        # Remove markdown headers
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
        # Remove markdown links [text](url)
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        # Remove markdown images
        content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', content)
        # Remove markdown bold/italic
        content = re.sub(r'\*\*([^\*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^\*]+)\*', r'\1', content)
        # Clean up whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Split into chunks
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk_text = content[start:end]
            
            if chunk_text.strip():  # Only add non-empty chunks
                try:
                    rel_file = str(file_path.relative_to(Path.cwd()))
                except ValueError:
                    rel_file = str(file_path)
                chunks.append({
                    'text': chunk_text,
                    'file': rel_file,
                    'file_path': str(file_path),
                    'start': start,
                    'end': end
                })
            
            start = end - overlap  # Overlap for context
        
        return chunks
    
    def get_embeddings(self, texts: List[str], batch_size: int = 10) -> np.ndarray:
        """
        Get embeddings from the API.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process per API call
            
        Returns:
            Numpy array of embeddings
        """
        embeddings = []
        
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            print(f"  Getting embeddings for batch {batch_num}/{total_batches} ({len(batch)} texts)...")
            
            try:
                response = self.client.embeddings.create(
                    model="text-embedding-ada-002",  # Default model, adjust if needed
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                # Set dimension on first batch
                if self.dimension is None and batch_embeddings:
                    self.dimension = len(batch_embeddings[0])
                    
            except Exception as e:
                print(f"  Error getting embeddings for batch {batch_num}: {e}")
                raise
        
        return np.array(embeddings, dtype='float32')
    
    def build_index(self, root_dir: str, chunk_size: int = 512, overlap: int = 50):
        """
        Build FAISS index from all Markdown files in the directory.
        
        Args:
            root_dir: Root directory to search for .md files
            chunk_size: Chunk size for text splitting
            overlap: Overlap between chunks
        """
        print(f"\n{'='*60}")
        print(f"Building index from: {root_dir}")
        print(f"{'='*60}\n")
        
        # Step 1: Find all Markdown files
        md_files = self.find_markdown_files(root_dir)
        
        if not md_files:
            print("No Markdown files found!")
            return
        
        # Step 2: Load and split files
        print(f"\nLoading and splitting {len(md_files)} files...")
        all_chunks = []
        
        for md_file in md_files:
            try:
                rel_path = md_file.relative_to(Path.cwd())
            except ValueError:
                rel_path = md_file
            print(f"  Processing: {rel_path}")
            chunks = self.load_and_split_file(md_file, chunk_size, overlap)
            all_chunks.extend(chunks)
        
        self.chunks = all_chunks
        print(f"\nCreated {len(self.chunks)} chunks from {len(md_files)} files")
        
        if not self.chunks:
            print("No chunks created!")
            return
        
        # Step 3: Get embeddings
        print(f"\nGetting embeddings for {len(self.chunks)} chunks...")
        texts = [chunk['text'] for chunk in self.chunks]
        self.embeddings = self.get_embeddings(texts)
        
        if self.dimension is None:
            raise ValueError("Could not determine embedding dimension")
        
        # Step 4: Build FAISS index
        print(f"\nBuilding FAISS index (dimension: {self.dimension})...")
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)
        
        # Use Inner Product index for normalized vectors (cosine similarity)
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Add embeddings to index
        self.index.add(self.embeddings)
        
        print(f"Index built successfully with {self.index.ntotal} vectors")
    
    def save_index(self, index_path: str = "my_notes.index"):
        """
        Save FAISS index and metadata to disk.
        
        Args:
            index_path: Path to save the index file
        """
        if self.index is None:
            raise ValueError("No index to save. Call build_index() first.")
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        print(f"Saved FAISS index to {index_path}")
        
        # Save metadata (chunks information)
        metadata_path = index_path.replace('.index', '_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'chunks': self.chunks,
                'dimension': self.dimension,
                'total_vectors': self.index.ntotal
            }, f, ensure_ascii=False, indent=2)
        print(f"Saved metadata to {metadata_path}")
        
        print(f"\n{'='*60}")
        print("Indexing complete!")
        print(f"  Index file: {index_path}")
        print(f"  Metadata file: {metadata_path}")
        print(f"  Total vectors: {self.index.ntotal}")
        print(f"{'='*60}\n")


def main():
    """Main function to run the indexer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Index Markdown files using FAISS and AI Builder Space API')
    parser.add_argument(
        '--dir',
        type=str,
        default='docs',
        help='Directory to search for Markdown files (default: docs)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='my_notes.index',
        help='Output index file name (default: my_notes.index)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=512,
        help='Chunk size in characters (default: 512)'
    )
    parser.add_argument(
        '--overlap',
        type=int,
        default=50,
        help='Overlap between chunks in characters (default: 50)'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        help='AI Builder Space API key (or set AI_BUILDER_TOKEN env var)'
    )
    parser.add_argument(
        '--base-url',
        type=str,
        default='https://space.ai-builders.com/backend/v1',
        help='Base URL for the API (default: https://space.ai-builders.com/backend/v1)'
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv("AI_BUILDER_TOKEN")
    if not api_key:
        raise ValueError(
            "API key not provided. Use --api-key argument or set AI_BUILDER_TOKEN environment variable."
        )
    
    # Initialize indexer
    indexer = MarkdownIndexer(api_key=api_key, base_url=args.base_url)
    
    # Build index
    indexer.build_index(
        root_dir=args.dir,
        chunk_size=args.chunk_size,
        overlap=args.overlap
    )
    
    # Save index
    indexer.save_index(index_path=args.output)


if __name__ == "__main__":
    main()
