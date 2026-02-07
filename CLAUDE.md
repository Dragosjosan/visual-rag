# Visual RAG — Visual Retrieval-Augmented Generation with ColPali + Milvus

## Project Structure

```
src/
  app.py                # FastAPI application setup (lifespan, CORS, router)
  api/v1/               # API endpoints (ingest, search, generate, documents)
  core/                  # Config (Pydantic Settings), model loader (singleton)
  models/                # Pydantic request/response models
  services/              # All business logic (embedding, ingestion, milvus, search, generation, pdf)
  utils/                 # Shared helpers (image utils, document utils)
tests/                   # Mirrors src/ structure (api/, services/, utils/)
backlog/                 # Task management (Backlog.md format)
data/                    # PDF documents, generated images, temp files
```

## General Code Standards

- No docstrings, no comments (unless logic is non-obvious)
- Small, focused functions — break large functions into smaller ones
- No business logic in routers — use services and utils
- Use error handling in all generated code
- Use `assert` in tests, never just print/log

## Python Style

### Package Manager
- Use `uv` for everything: running scripts, tests, adding dependencies
- `uv add <library>` to install — never edit pyproject.toml manually
- `uv run pytest` to run tests

### Type Hints
- Use type hints everywhere
- Modern syntax: `str | None`, `list[str]`, `dict[str, Any]` — never `Optional`, `List`, `Dict`

### Logging
- Use `loguru` for logging — never `print()`

### Linting & Formatting
- Line length: 120 chars (enforced by ruff)
- Target: Python 3.11
- Ruff rules: E, F, I, B, UP (errors, pyflakes, isort, bugbear, pyupgrade)
- Run: `make lint` and `make format`

## FastAPI Architecture

- **Routers** (`api/v1/`): Thin HTTP layer only — validate input, call service, return response
- **Services** (`services/`): All business logic lives here
- **Models** (`models/`): Pydantic models for all request/response data
- **Utils** (`utils/`): Shared helpers

### Pydantic
- All API data flows must use Pydantic models — no raw dicts for structured data
- Use Pydantic v2 patterns (`model_validator`, `field_validator`)
- Validate at API boundaries

### Error Handling
- Raise `HTTPException` with appropriate status codes (400, 404, 500)
- Use `loguru` for error logging
- Implement rollback on multi-step operations (e.g., ingestion failure)

## AI/ML Guardrails

- **Never modify model parameters** (temperature, batch size, embedding dimensions) without asking the user first
- **Never change the ColQwen2 model name or configuration** without asking
- **Never modify VLM prompts or Ollama settings** without asking
- Follow the singleton pattern for model loading (`ColQwen2ModelLoader`)

## Testing

- Framework: `pytest` with `pytest-asyncio` (async mode: auto)
- Markers: `@pytest.mark.unit` (mocked) and `@pytest.mark.integration` (real API calls)
- Test structure mirrors `src/` — place tests in matching `tests/` subdirectory
- Run all: `uv run pytest`
- Run unit only: `uv run pytest -m unit`
- Run integration only: `uv run pytest -m integration`

## Environment Variables

See `.env.example` for full list. Key variables:

| Variable | Purpose | Default |
|---|---|---|
| `MILVUS_HOST` / `MILVUS_PORT` | Milvus connection | `localhost:19530` |
| `MILVUS_COLLECTION_NAME` | Vector collection name | `visual_rag_patches` |
| `COLQWEN2_MODEL_NAME` | Embedding model | `vidore/colqwen2-v0.1` |
| `COLQWEN2_DEVICE` | Compute device | `cuda` / `mps` / `cpu` |
| `OLLAMA_BASE_URL` | VLM endpoint | `http://localhost:11434` |
| `VLM_MODEL_NAME` | Generation model | `llama2` |

## Git & Workflow

- **Do not commit** — the user handles commits manually
- **Do not push** — the user handles pushes manually
- When you find bugs, tech debt, or improvements while working, suggest creating a backlog task but don't create it without asking first

## Tasks & Backlog

- Always ask the user before creating a new task
- Tasks go in `backlog/tasks/` using Backlog.md format

## Running the Project

- See `Makefile` for all available commands (`make help`)