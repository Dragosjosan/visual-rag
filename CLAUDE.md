#

# Visual RAG with Azure AI Search

## Code best practices
- Do not use docstrings and comments

## Python tools
- Use `uv` as a package manager and to run python scripts, tests, tools, etc.
- Use `loguru` instead of prints
- Use `pytest` for writing tests
- Use `assert` in your tests, do NOT just print/log results
- Use `uv add <library>` instead of editing the pyproject toml, to install it directly.
- Use types when generating code
- Use error handling when generating code.
- Use small functions for logic. Break big functions into smaller functions, to improve readability.
- Do NOT write business logic in the FastAPI router. Use services, and the services use utils.

## Purpose
- Use ColPali to create visual embeddings
- Use Milvus to store the embeddings
- Create a retrieval engine to retrieve the best matching chunks
- Create FastAPI backend
