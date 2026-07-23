from pydantic import BaseModel

from src.prompts import DocumentType


class FileUploadResponse(BaseModel):
    document_type: DocumentType
    size: int
