from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_path: str
    extracted_text: str
    created_at: datetime

    class Config:
        from_attributes = True
