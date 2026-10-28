from typing import Literal

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    title: str | None = None


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str | None
    created_at: object

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str
    mode: Literal["normal", "document"] = "normal"
    document_id: int | None = None


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: object

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse