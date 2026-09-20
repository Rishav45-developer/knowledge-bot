from pydantic import BaseModel

class ConversationCreate(BaseModel):
    title: str | None = None

class ConversationResponse(BaseModel):
    id:int
    user_id:int
    title: str | None
    created_at: object

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: object

    class Config:
        from_sttributes = True


class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse

            
            
