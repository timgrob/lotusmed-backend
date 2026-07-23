from fastapi import APIRouter, UploadFile, status

from src.core.exceptions import InvalidFileError
from src.prompts import MAX_PROMPT_FILE_BYTES, save_prompt
from src.schemas.file import FileUploadResponse

router = APIRouter(prefix="/file", tags=["file"])


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(file: UploadFile) -> FileUploadResponse:
    """Upload a Markdown or text file and save it to the prompts directory."""
    if file.size is not None and file.size > MAX_PROMPT_FILE_BYTES:
        raise InvalidFileError("File exceeds the maximum allowed size")

    raw = await file.read()
    if len(raw) > MAX_PROMPT_FILE_BYTES:
        raise InvalidFileError("File exceeds the maximum allowed size")
    if not raw:
        raise InvalidFileError("File is empty")

    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidFileError("File must be valid UTF-8 text") from exc

    saved = save_prompt(file.filename or "", content)
    return FileUploadResponse(filename=saved.name, size=len(raw))
