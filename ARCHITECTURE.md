# Architecture

A `Python` backend application built with `FastAPI` and managed with `uv`.

This project is structured to keep API routes thin, business logic isolated, database access explicit, and configuration centralized. 
It is designed to be understandable for both human developers and coding agents.

For coding conventions, setup, and commands, see [AGENTS.md](AGENTS.md).
For the file-by-file layout, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md).

## Request Flow (current)

```text
Client
  ↓
FastAPI app (src/main.py) — mounts routers under /api/v1
  ↓
Route handler (src/api/v1/routes/)
  ↓  Depends(get_agent)                    ↓
OpenAI client (src/agents/openai_agent.py) │ in-memory USERS_DB dict (users.py)
  ↓                                        │
OpenAI API (Responses API / Images API)
```

Route handlers currently contain the business logic directly (prompt assembly,
OpenAI calls, error mapping). There is no service or repository layer yet —
see "Target architecture" below before adding one.

## Components

| Component | File | Responsibility |
|---|---|---|
| App entrypoint | `src/main.py` | Creates `FastAPI` app, registers routers, root health route `GET /` |
| Paraphrase routes | `src/api/v1/routes/paraphrase.py` | `POST /api/v1/paraphrase/generate-text` (medical text → layman's terms), `POST /api/v1/paraphrase/generate-image` (text → base64 PNG infographic) |
| User routes | `src/api/v1/routes/users.py` | Placeholder CRUD backed by an in-memory dict (`USERS_DB`); data is lost on restart |
| OpenAI client | `src/agents/openai_agent.py` | Module-level `OpenAI` client; injected into routes via `Depends(get_agent)` |
| Settings | `src/core/config.py` | Single `pydantic-settings` `Settings` class, loaded from `.env`, cached with `@lru_cache` via `get_settings()` |
| Prompts | `src/prompts/` | Markdown prompt templates, loaded and cached by `load_prompt(name)` in `src/prompts/__init__.py` |
| Schemas | `src/models/` | Pydantic request/response models (note: Pydantic, not SQLAlchemy, despite the directory name) |

## Target architecture (not yet implemented)

The intended end state adds persistence and a layered design:

```text
Client → FastAPI Router → Service Layer → Repository Layer → PostgreSQL
```

Planned but **not present in the code yet**: `services/`, `repositories/`,
`db/` (SQLAlchemy engine/session), `schemas/` (separate from `models/`),
Alembic migrations, and a `tests/` suite. When implementing any of these,
follow the conventions in AGENTS.md (async SQLAlchemy 2.0, thin routes,
business logic in services).
