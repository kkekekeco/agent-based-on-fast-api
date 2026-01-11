#!/bin/bash
# Bash script to refresh the index and reload it in FastAPI (Mac/Linux)

echo "Refreshing notes index..."

# Step 1: Rebuild the index
echo ""
echo "[1/2] Rebuilding index..."
python indexer.py --dir docs --output my_notes.index

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to rebuild index!"
    exit 1
fi

echo ""
echo "[2/2] Reloading index in FastAPI..."

# Step 2: Reload index in FastAPI (if server is running)
RELOAD_URL="http://127.0.0.1:8000/admin/reload-index"
if curl -s -X POST "$RELOAD_URL" > /dev/null 2>&1; then
    RESPONSE=$(curl -s -X POST "$RELOAD_URL")
    echo ""
    echo "[SUCCESS] Index reloaded in FastAPI!"
    echo "$RESPONSE" | grep -o '"vectors":[0-9]*' | sed 's/"vectors"://' | xargs -I {} echo "  Vectors: {}"
    echo "$RESPONSE" | grep -o '"chunks":[0-9]*' | sed 's/"chunks"://' | xargs -I {} echo "  Chunks: {}"
else
    echo ""
    echo "[WARNING] Could not reload index in FastAPI (server may not be running)"
    echo "  You may need to restart the FastAPI server manually"
fi

echo ""
echo "Index refresh complete!"
