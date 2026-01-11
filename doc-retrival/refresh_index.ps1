# PowerShell script to refresh the index and reload it in FastAPI

Write-Host "Refreshing notes index..." -ForegroundColor Cyan

# Step 1: Rebuild the index
Write-Host "`n[1/2] Rebuilding index..." -ForegroundColor Yellow
python indexer.py --dir docs --output my_notes.index

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nError: Failed to rebuild index!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[2/2] Reloading index in FastAPI..." -ForegroundColor Yellow

# Step 2: Reload index in FastAPI (if server is running)
$reloadUrl = "http://127.0.0.1:8000/admin/reload-index"
try {
    $response = Invoke-RestMethod -Uri $reloadUrl -Method Post -ErrorAction Stop
    Write-Host "`n[SUCCESS] Index reloaded in FastAPI!" -ForegroundColor Green
    Write-Host "  Vectors: $($response.vectors)" -ForegroundColor Gray
    Write-Host "  Chunks: $($response.chunks)" -ForegroundColor Gray
} catch {
    Write-Host "`n[WARNING] Could not reload index in FastAPI (server may not be running)" -ForegroundColor Yellow
    Write-Host "  You may need to restart the FastAPI server manually" -ForegroundColor Gray
}

Write-Host "`nIndex refresh complete!" -ForegroundColor Green
