from pathlib import Path

import pytest
from fastapi import status
from httpx2 import AsyncClient

import src.prompts

pytestmark = pytest.mark.anyio


@pytest.fixture
def prompts_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(src.prompts, "PROMPTS_DIR", tmp_path)
    return tmp_path


async def test_upload_translation_succeeds(client: AsyncClient, prompts_dir: Path):
    content = b"# Translation prompt"

    response = await client.post(
        "/api/v1/file/upload/medical_translation",
        files={"file": ("anything.md", content, "text/markdown")},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "document_type": "medical_translation",
        "size": len(content),
    }
    assert (prompts_dir / "medical_translation.md").read_bytes() == content


async def test_upload_infographic_succeeds(client: AsyncClient, prompts_dir: Path):
    response = await client.post(
        "/api/v1/file/upload/medical_infographic",
        files={"file": ("x.md", b"# Infographic", "text/markdown")},
    )

    assert response.status_code == status.HTTP_200_OK
    assert (prompts_dir / "medical_infographic.md").exists()


async def test_upload_unknown_type_returns_422(client: AsyncClient, prompts_dir: Path):
    response = await client.post(
        "/api/v1/file/upload/medical_haiku",
        files={"file": ("x.md", b"content", "text/markdown")},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert not any(prompts_dir.iterdir())


async def test_upload_non_utf8_returns_400(client: AsyncClient, prompts_dir: Path):
    response = await client.post(
        "/api/v1/file/upload/medical_translation",
        files={"file": ("x.md", b"\xff\xfe\x00binary", "text/markdown")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not any(prompts_dir.iterdir())


async def test_upload_empty_returns_400(client: AsyncClient, prompts_dir: Path):
    response = await client.post(
        "/api/v1/file/upload/medical_translation",
        files={"file": ("x.md", b"", "text/markdown")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_upload_overwrites_existing(client: AsyncClient, prompts_dir: Path):
    (prompts_dir / "medical_translation.md").write_text("old", encoding="utf-8")

    response = await client.post(
        "/api/v1/file/upload/medical_translation",
        files={"file": ("x.md", b"new content", "text/markdown")},
    )

    assert response.status_code == status.HTTP_200_OK
    assert (prompts_dir / "medical_translation.md").read_text(
        encoding="utf-8"
    ) == "new content"
