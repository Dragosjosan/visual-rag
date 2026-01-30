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
- Use types when generating code. Use the modern way of writing `<type> | None` instead of `Optional` and `list`, `tuple`, etc.
- Use error handling when generating code.
- Use small functions for logic. Break big functions into smaller functions, to improve readability.
- Use services and utils for all routers. No business logic in the router.

## Purpose
- Use ColPali to create visual embeddings
- Use Milvus to store the embeddings
- Create a retrieval engine to retrieve the best matching chunks
- Create FastAPI backend
