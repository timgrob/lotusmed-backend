from fastapi import APIRouter, UploadFile, status

from src.core.exceptions import InvalidFileError
from src.prompts import MAX_PROMPT_FILE_BYTES, DocumentType, save_prompt
from src.schemas.prompt import PromptUploadResponse

router = APIRouter(prefix="/prompt", tags=["prompt"])


@router.post(
    "/upload/{document_type}",
    response_model=PromptUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_file(
    document_type: DocumentType, file: UploadFile
) -> PromptUploadResponse:
    """Upload a prompt file and set it as the given document type's prompt."""
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

    save_prompt(document_type, content)
    return PromptUploadResponse(document_type=document_type, size=len(raw))
