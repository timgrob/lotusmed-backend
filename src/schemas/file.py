from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    filename: str
    size: int
