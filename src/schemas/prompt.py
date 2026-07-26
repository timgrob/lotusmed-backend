from pydantic import BaseModel

from src.prompts import DocumentType


class PromptUploadResponse(BaseModel):
    document_type: DocumentType
    size: int
