from pathlib import Path

import pytest

import src.prompts
from src.prompts import DocumentType, load_prompt, save_prompt


@pytest.fixture
def prompts_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(src.prompts, "PROMPTS_DIR", tmp_path)
    return tmp_path


def test_save_prompt_writes_canonical_file(prompts_dir: Path):
    target = save_prompt(DocumentType.MEDICAL_TRANSLATION, "# Guide")

    assert target == prompts_dir / "medical_translation.md"
    assert target.read_text(encoding="utf-8") == "# Guide"


def test_save_prompt_overwrites_existing(prompts_dir: Path):
    save_prompt(DocumentType.MEDICAL_INFOGRAPHIC, "first")
    target = save_prompt(DocumentType.MEDICAL_INFOGRAPHIC, "second")

    assert target.read_text(encoding="utf-8") == "second"


def test_saved_prompt_is_loadable_and_refreshes_cache(prompts_dir: Path):
    doc_type = DocumentType.MEDICAL_TRANSLATION
    save_prompt(doc_type, "  original  ")
    assert load_prompt(doc_type.filename) == "original"

    # A new upload must invalidate the cache so the latest content is served.
    save_prompt(doc_type, "  updated  ")
    assert load_prompt(doc_type.filename) == "updated"
