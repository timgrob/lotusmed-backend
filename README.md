# LotusMed Backend

A `Python` backend applicatoin build with `FastAPI` backend for LotusMed: rewrites medical documents (doctor's letters, diagnostic reports) into patient-friendly language and generates medical infographic images.

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Pytest
- Uvicorn
- Ruff
- uv

## Project Structure

```text
app/
├── api/
├── core/
├── db/
├── models/
├── schemas/
├── services/
├── repositories/
├── utils/
└── main.py
```

### Repository layout

| Directory | Contents |
|---|---|
| `api/` | contains HTTP routes and endpoints. |
| `core/` | contains configuration, logging, and security utilities. |
| `db/` | contains database connection, session and base setup. |
| `models/` | contains SQLAlchemy database tables. |
| `schemas/` | contains Pydantic request and response models. |
| `services/` | contains business logic. |
| `repositories/` | contains database access logic. |
| `utils` | generic helper functions. |

## Local Setup

### 1. Clone repository
```bash
git clone <repository-url>
cd <repository url>
```

### 2. Install uv
If `uv` is not installed yet:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On macOS with Homebrew:
```bash
brew install uv
```

### 3. Create and sync environment
```bash
uv sync
```
This creates a virtual environment and installs the dependencies from pyproject.toml and uv.lock.

### 4. Create environment file
```bash
cp .env.example .env
```
Update the values in .env as needed.

### 5. Run database migrations
```bash
uv run alembic upgrade head
```

### 6. Start the development server
```bash
uv run uvicorn src.main:app --reload
```
The API should now be available at: http://localhost:8000.
The interactive API documentation: http://localhost:8000.
Alternative API documentation: http://localhost:8000/redoc

## Common commands

Run the application:
```bash
uv run uvicorn src.main:app --reload
```

Run tests:
```bash
uv run pytest
```

Run linting:
```bash
uv run ruff check .
```

Format code:
```bash
uv run ruff format .
```

Create a new migration:
```bash
uv run alembic revision --autogenerate -m "describe migration"
```

Apply migrations:
```bash
uv run alembic upgrade head
```

Rollback one migration:
```bash
uv run alembic downgrade -1
```

Add a dependency:
```bash
uv add <package-name>
```

Add a development dependency:
```bash
uv add --dev <package-name>
```

Remove a dependency:
```bash
uv remove <package-name>
``` 

Update dependencies:
```bash
uv sync --upgrade
``` 
