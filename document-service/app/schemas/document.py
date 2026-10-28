from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_path: str
    extracted_text: str | None
    processing_status: str
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentSearchRequest(BaseModel):
    query: str
    n_results: int = 5
    document_id: int | None = None