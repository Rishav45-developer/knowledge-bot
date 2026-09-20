from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse
)
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# =========================================================
# 1. GET MY CONVERSATIONS
# =========================================================

@router.get(
    "/conversations",
    response_model=list[ConversationResponse]
)
def get_my_conversations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.id.desc())
        .all()
    )

    return conversations


# =========================================================
# 2. CREATE A CONVERSATION
# =========================================================

@router.post(
    "/conversations",
    response_model=ConversationResponse
)
def create_conversation(
    conversation_data: ConversationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    new_conversation = Conversation(
        user_id=user_id,
        title=conversation_data.title
    )

    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)

    return new_conversation


# =========================================================
# 3. ADD MESSAGE TO A CONVERSATION
# =========================================================

@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse
)
def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    # Check that the conversation belongs to the logged-in user
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    new_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=message_data.content
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message


# =========================================================
# 4. GET MESSAGES OF A CONVERSATION
# =========================================================

@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse]
)
def get_conversation_messages(
    conversation_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    # First check ownership of the conversation
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Get all messages belonging to this conversation
    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.id.asc())
        .all()
    )

    return messages