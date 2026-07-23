from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from src.core.exceptions import AlreadyExistsError, InvalidFileError

PROMPTS_DIR = Path(__file__).parent

ALLOWED_PROMPT_SUFFIXES = {".md", ".txt"}
MAX_PROMPT_FILE_BYTES = 1_000_000


@lru_cache
def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8").strip()


def save_prompt(filename: str, content: str) -> Path:
    """Save uploaded text content as a prompt file in the prompts directory.

    Args:
        filename: Client-supplied filename; only its basename is used.
        content: UTF-8 text to write.

    Returns:
        The path the prompt was written to.

    Raises:
        InvalidFileError: If the filename is missing/malformed or has a
            disallowed extension.
        AlreadyExistsError: If a prompt with the same name already exists.
    """
    name = Path(filename).name  # strip any directory components (traversal guard)
    if not name or not Path(name).stem:
        raise InvalidFileError("A valid filename is required")
    if Path(name).suffix.lower() not in ALLOWED_PROMPT_SUFFIXES:
        raise InvalidFileError("Only .md and .txt files are allowed")

    target = (PROMPTS_DIR / name).resolve()
    if target.parent != PROMPTS_DIR.resolve():  # defense-in-depth traversal guard
        raise InvalidFileError("Invalid filename")
    if target.exists():
        raise AlreadyExistsError(f"Prompt already exists: {name}")

    target.write_text(content, encoding="utf-8")
    load_prompt.cache_clear()  # keep the read cache consistent
    return target
