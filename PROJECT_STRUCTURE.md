# Project Structure

All application code lives in `src/`. The app is run as a module rooted at the
repo top level (`uv run uvicorn src.main:app`), so imports are absolute:
`from src.core.config import get_settings`.

This tree lists what **actually exists**. also see [ARCHITECTURE.md](ARCHITECTURE.md).

```text
.
├── src/
│   ├── main.py                      # FastAPI app; registers routers under /api/v1
│   ├── api/
│   │   └── v1/
│   │       └── routes/
│   │           ├── paraphrase.py    # POST /paraphrase/generate-text, /paraphrase/generate-image
│   │           └── users.py         # Placeholder user CRUD (in-memory dict, not persisted)
│   ├── agents/
│   │   └── openai_agent.py          # Shared OpenAI client + get_agent() dependency
│   ├── core/
│   │   └── config.py                # Settings (pydantic-settings, reads .env); get_settings()
│   ├── models/
│   │   ├── paraphrase.py            # Pydantic request/response models for paraphrase routes
│   │   └── user.py                  # Pydantic user models (User, UserCreate, UserUpdate, enums)
│   └── prompts/
│       ├── __init__.py              # load_prompt(name) — reads and caches a prompt file
│       ├── medical_translation.md   # System prompt: rewrite medical text in layman's terms
│       ├── medical_depiction.md     # Prompt rules for medical image generation
│       └── medical_infographic.md   # Prompt rules for infographic generation
├── AGENTS.md                        # Conventions, setup, commands — read this before coding
├── ARCHITECTURE.md                  # Request flow, components, current vs. target design
├── Dockerfile
├── .env.example                     # Required env vars (copy to .env)
├── pyproject.toml                   # Dependencies and tool config (managed with uv)
└── uv.lock
```

## Where to put new code

| You are adding… | Put it in… |
|---|---|
| A new endpoint | New file in `src/api/v1/routes/`, then register its router in `src/main.py` |
| Request/response models | `src/models/<domain>.py` (Pydantic) |
| An LLM prompt or prompt change | `src/prompts/*.md` — routes load them via `load_prompt("<file>.md")` |
| A new external client (LLM, API) | `src/agents/`, exposed as a `Depends` provider like `get_agent()` |
| A new config value | `Settings` in `src/core/config.py`, plus `.env.example` |
| Business logic beyond a trivial route | Create `src/services/` (per the target architecture in ARCHITECTURE.md) |
