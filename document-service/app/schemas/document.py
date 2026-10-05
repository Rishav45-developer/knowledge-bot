from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_path: str
    extracted_text: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentSearchRequest(BaseModel):
    query: str
    n_results: int = 5