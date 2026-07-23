from pathlib import Path

import pytest

import src.prompts
from src.core.exceptions import AlreadyExistsError, InvalidFileError
from src.prompts import load_prompt, save_prompt


@pytest.fixture
def prompts_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(src.prompts, "PROMPTS_DIR", tmp_path)
    return tmp_path


def test_save_prompt_writes_file(prompts_dir: Path):
    target = save_prompt("guide.md", "# Guide")

    assert target == prompts_dir / "guide.md"
    assert target.read_text(encoding="utf-8") == "# Guide"


def test_save_prompt_strips_directory_components(prompts_dir: Path):
    target = save_prompt("../../escape.md", "payload")

    assert target == prompts_dir / "escape.md"


def test_save_prompt_rejects_bad_extension(prompts_dir: Path):
    with pytest.raises(InvalidFileError):
        save_prompt("script.py", "print('x')")


def test_save_prompt_rejects_missing_name(prompts_dir: Path):
    with pytest.raises(InvalidFileError):
        save_prompt(".md", "no stem")


def test_save_prompt_rejects_duplicate(prompts_dir: Path):
    save_prompt("dup.md", "first")

    with pytest.raises(AlreadyExistsError):
        save_prompt("dup.md", "second")


def test_saved_prompt_is_loadable(prompts_dir: Path):
    save_prompt("fresh.md", "  fresh body  ")

    # load_prompt strips surrounding whitespace and reads the just-written file.
    assert load_prompt("fresh.md") == "fresh body"
