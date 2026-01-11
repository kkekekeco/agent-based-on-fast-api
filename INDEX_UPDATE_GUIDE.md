# Index Update Guide

## Current Behavior

**索引不会自动更新**。当前的实现是：

1. **启动时加载**：索引在 FastAPI 应用启动时加载一次（`@app.on_event("startup")`）
2. **查询时使用**：`query_my_notes` 工具只是查询已加载的索引，不会重新构建
3. **静态索引**：索引在内存中保持静态，直到手动重新加载或应用重启

## Workflow for Updating Knowledge Base

### Option 1: Quick Refresh (Recommended)

使用自动化脚本一键更新：

**Windows:**
```powershell
cd 202601-doc-retrival
.\refresh_index.ps1
```

**Mac/Linux:**
```bash
cd 202601-doc-retrival
chmod +x refresh_index.sh  # First time only
./refresh_index.sh
```

这个脚本会：
1. 重新构建索引（扫描所有 .md 文件）
2. 自动调用 FastAPI 的 `/admin/reload-index` 端点重新加载索引
3. **无需重启服务器**

### Option 2: Manual Steps

1. **添加新的 Markdown 文件**到 `202601-doc-retrival/docs/` 文件夹
2. **重新构建索引**（Windows/Mac/Linux 相同）：
   ```bash
   cd 202601-doc-retrival
   python indexer.py --dir docs --output my_notes.index
   ```
3. **重新加载索引**（二选一）：
   - **方法 A**: 调用 API 端点（无需重启）
     - **Windows:**
       ```powershell
       Invoke-RestMethod -Uri "http://127.0.0.1:8000/admin/reload-index" -Method Post
       ```
     - **Mac/Linux:**
       ```bash
       curl -X POST http://127.0.0.1:8000/admin/reload-index
       ```
   - **方法 B**: 重启 FastAPI 应用

### Option 3: API Endpoint

直接调用重新加载端点（如果索引文件已更新）：

**Windows:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/admin/reload-index" -Method Post
```

**Mac/Linux:**
```bash
curl -X POST http://127.0.0.1:8000/admin/reload-index
```

## Why Not Auto-Update on Every Query?

**性能原因：**
- 构建索引需要：
  - 读取所有文件
  - 分块文档
  - 调用嵌入 API（文件多时可能很慢）
  - 构建 FAISS 索引
- 这会让每次查询变得非常慢（几秒到几分钟）
- 索引构建是昂贵的操作，所以我们构建一次然后重复使用

## Best Practices

1. **批量更新**：添加多个文件，然后一次性重建索引
2. **定期更新**：定期重建索引（例如每天）
3. **使用重新加载端点**：快速更新而无需完全重启服务器
4. **使用自动化脚本**：`refresh_index.ps1` 简化整个过程

## Summary

**回答你的问题：**

- ❌ **不会**：每次在 agent web 里问问题时，索引**不会**自动刷新
- ✅ **需要**：你需要：
  1. 添加新的 .md 文件到 `docs` 文件夹
  2. 运行 `python indexer.py` 重新构建索引
  3. 调用 `/admin/reload-index` 端点（或重启服务器）重新加载索引

**推荐流程：**

**Windows:**
```powershell
# 1. 添加文件到 docs 文件夹
# 2. 运行一键刷新脚本
cd 202601-doc-retrival
.\refresh_index.ps1
# 完成！索引已更新，无需重启服务器
```

**Mac/Linux:**
```bash
# 1. 添加文件到 docs 文件夹
# 2. 运行一键刷新脚本
cd 202601-doc-retrival
./refresh_index.sh
# 完成！索引已更新，无需重启服务器
```
