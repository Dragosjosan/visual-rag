#

# Visual RAG with Azure AI Search

## Code best practices
- Do not use docstrings and comments

## Python tools
- Use `uv` as a package manager and to run python scripts, tests, tools, etc.
- Use `loguru` instead of prints
- Use `pytest` for writing tests
- Use `assert` in your tests, do NOT just print/log results

## Purpose
- Use ColPali to create visual embeddings
- Use Milvus to store the embeddings
- Create a retrieval engine to retrieve the best matching chunks
- Create FastAPI backend
