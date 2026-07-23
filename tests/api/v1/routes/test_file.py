from pathlib import Path

import pytest
from fastapi import status
from httpx2 import AsyncClient

import src.prompts

pytestmark = pytest.mark.anyio

UPLOAD_URL = "/api/v1/file/upload"


@pytest.fixture
def prompts_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(src.prompts, "PROMPTS_DIR", tmp_path)
    return tmp_path


async def test_upload_markdown_succeeds(client: AsyncClient, prompts_dir: Path):
    content = b"# Title\n\nSome prompt body."

    response = await client.post(
        UPLOAD_URL, files={"file": ("new_prompt.md", content, "text/markdown")}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"filename": "new_prompt.md", "size": len(content)}
    assert (prompts_dir / "new_prompt.md").read_bytes() == content


async def test_upload_txt_succeeds(client: AsyncClient, prompts_dir: Path):
    response = await client.post(
        UPLOAD_URL, files={"file": ("notes.txt", b"plain text", "text/plain")}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert (prompts_dir / "notes.txt").exists()


async def test_upload_disallowed_extension_returns_400(
    client: AsyncClient, prompts_dir: Path
):
    response = await client.post(
        UPLOAD_URL, files={"file": ("evil.pdf", b"%PDF-1.4", "application/pdf")}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not any(prompts_dir.iterdir())


async def test_upload_non_utf8_returns_400(client: AsyncClient, prompts_dir: Path):
    response = await client.post(
        UPLOAD_URL,
        files={"file": ("bad.md", b"\xff\xfe\x00binary", "text/markdown")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not any(prompts_dir.iterdir())


async def test_upload_empty_returns_400(client: AsyncClient, prompts_dir: Path):
    response = await client.post(
        UPLOAD_URL, files={"file": ("empty.md", b"", "text/markdown")}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_upload_duplicate_returns_409(client: AsyncClient, prompts_dir: Path):
    (prompts_dir / "dup.md").write_text("existing", encoding="utf-8")

    response = await client.post(
        UPLOAD_URL, files={"file": ("dup.md", b"new content", "text/markdown")}
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    # The existing file is untouched.
    assert (prompts_dir / "dup.md").read_text(encoding="utf-8") == "existing"


async def test_upload_path_traversal_is_contained(
    client: AsyncClient, prompts_dir: Path
):
    response = await client.post(
        UPLOAD_URL,
        files={"file": ("../../evil.md", b"payload", "text/markdown")},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["filename"] == "evil.md"
    assert (prompts_dir / "evil.md").exists()
    # Nothing escaped the prompts directory.
    assert not (prompts_dir.parent.parent / "evil.md").exists()
