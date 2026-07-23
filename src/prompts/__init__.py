from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent

MAX_PROMPT_FILE_BYTES = 1_000_000


class DocumentType(StrEnum):
    MEDICAL_TRANSLATION = "medical_translation"
    MEDICAL_INFOGRAPHIC = "medical_infographic"

    @property
    def filename(self) -> str:
        return f"{self.value}.md"


@lru_cache
def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8").strip()


def save_prompt(document_type: DocumentType, content: str) -> Path:
    """Write uploaded content to the canonical prompt file for a document type.

    Overwrites any existing prompt for the type and invalidates the read cache
    so the latest upload is served on the next ``load_prompt`` call.

    Args:
        document_type: The prompt slot to write.
        content: UTF-8 text to store.

    Returns:
        The path the prompt was written to.
    """
    target = PROMPTS_DIR / document_type.filename
    target.write_text(content, encoding="utf-8")
    load_prompt.cache_clear()
    return target
