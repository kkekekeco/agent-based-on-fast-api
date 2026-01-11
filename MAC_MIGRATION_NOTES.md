# Mac Migration Notes - Windows to Mac Development Setup

## What We Did on Windows

### 1. Monorepo Structure Created
- **Merged `doc-retrival` into `fastapi` repository** as a subdirectory
- All code is now in one repository: `agent-based-on-fast-api`
- Repository URL: `https://github.com/kkekekeco/agent-based-on-fast-api.git`

### 2. Code Changes
- Updated all path references from `../202601-doc-retrival` to `doc-retrival/`
- Updated `main.py` to load index from `doc-retrival/my_notes.index`
- Updated `.gitignore` to ignore index files in `doc-retrival/` subdirectory
- Updated README files to reflect monorepo structure

### 3. Cleanup
- Removed standalone `202601-doc-retrival` folder (no longer needed)
- All code is now in `202601-fastapi/` directory

## Important Notes for Mac Development

### ⚠️ Critical: Environment Setup
1. **`.env` file is NOT synced** (in `.gitignore`)
   - You need to create `.env` file on Mac with your `AI_BUILDER_TOKEN`
   - Copy from `.env.example` if exists, or create new one

2. **Index files are NOT synced** (in `.gitignore`)
   - `doc-retrival/*.index` and `doc-retrival/*_metadata.json` are ignored
   - You'll need to rebuild the index on Mac with your notes

### 📝 Mac Has More Notes
Since Mac has more notes, you'll need to:
1. Add your Mac notes to `doc-retrival/docs/` folder
2. Rebuild the index using `doc-retrival/refresh_index.sh`
3. The index will be created at `doc-retrival/my_notes.index`

## Mac Setup Instructions

### Step 1: Clone Repository
```bash
git clone https://github.com/kkekekeco/agent-based-on-fast-api.git
cd agent-based-on-fast-api
```

### Step 2: Environment Configuration
```bash
# Create .env file
cp .env.example .env  # If .env.example exists
# OR create manually:
# echo "AI_BUILDER_TOKEN=your-token-here" > .env

# Edit .env and add your AI_BUILDER_TOKEN
nano .env  # or use your preferred editor
```

### Step 3: Install Dependencies
```bash
# Install FastAPI dependencies
pip install -r requirements.txt

# Install doc-retrival dependencies
pip install -r doc-retrival/requirements_faiss.txt
```

### Step 4: Add Your Mac Notes
```bash
# Copy your Mac notes to the docs folder
# Example:
cp -r ~/path/to/your/notes/* doc-retrival/docs/

# Or manually add files to doc-retrival/docs/
```

### Step 5: Build Index
```bash
cd doc-retrival
./refresh_index.sh
cd ..
```

### Step 6: Verify Index Created
```bash
# Check if index files exist
ls -lh doc-retrival/*.index
ls -lh doc-retrival/*_metadata.json
```

### Step 7: Run FastAPI
```bash
# From project root
fastapi dev main.py
```

## Development Workflow on Mac

### Daily Workflow
```bash
# 1. Pull latest changes (if working on multiple machines)
git pull origin main

# 2. Make your changes...

# 3. When updating notes, rebuild index
cd doc-retrival
./refresh_index.sh
cd ..

# 4. Test locally
fastapi dev main.py

# 5. Commit and push
git add .
git commit -m "Your changes description"
git push origin main
```

### Updating Notes and Index
```bash
# Add new markdown files to doc-retrival/docs/
# Then rebuild index:
cd doc-retrival
./refresh_index.sh
cd ..

# Or manually:
python doc-retrival/indexer.py --dir doc-retrival/docs --output doc-retrival/my_notes.index

# After rebuilding, reload index in FastAPI (if server is running):
# Call POST /admin/reload-index endpoint
# OR restart the FastAPI server
```

## File Structure on Mac

```
agent-based-on-fast-api/
├── main.py                    # FastAPI application
├── requirements.txt           # FastAPI dependencies
├── .env                       # Environment variables (NOT synced, create on Mac)
├── doc-retrival/              # Document indexing system
│   ├── indexer.py
│   ├── refresh_index.sh      # Mac/Linux script
│   ├── requirements_faiss.txt
│   ├── docs/                 # Your notes go here (NOT synced)
│   │   └── *.md              # Your markdown notes
│   ├── my_notes.index        # Generated index (NOT synced)
│   └── my_notes_metadata.json # Generated metadata (NOT synced)
└── static/                    # Frontend files
```

## What's NOT Synced (Git Ignored)

These files are intentionally NOT synced because they contain:
- **Personal/sensitive data**: `.env` (API keys)
- **Personal notes**: `doc-retrival/docs/*.md` (your personal markdown files)
- **Generated indexes**: `doc-retrival/*.index` and `*_metadata.json` (large binary files)

You need to:
1. Create `.env` on Mac with your API token
2. Add your Mac notes to `doc-retrival/docs/`
3. Rebuild index on Mac

## Troubleshooting

### Index Not Found Error
If you see "Notes index not available" warning:
```bash
# Make sure index exists
ls doc-retrival/my_notes.index

# If not, rebuild it
cd doc-retrival
./refresh_index.sh
cd ..
```

### Path Issues
All paths are relative to the project root. The FastAPI app expects:
- Index at: `doc-retrival/my_notes.index`
- Metadata at: `doc-retrival/my_notes_metadata.json`

### API Token Issues
Make sure `.env` file exists and contains:
```
AI_BUILDER_TOKEN=your-actual-token-here
```

## Next Steps

1. ✅ Clone repository on Mac
2. ✅ Set up `.env` file
3. ✅ Install dependencies
4. ✅ Add your Mac notes to `doc-retrival/docs/`
5. ✅ Build index
6. ✅ Start developing!

## Questions?

- Check `README.md` for general project info
- Check `doc-retrival/README.md` for indexer details
- All code is in the repository, ready to use!
