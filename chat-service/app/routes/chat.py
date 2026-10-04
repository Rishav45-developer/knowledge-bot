from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.conversation import Conversation
from app.models.message import Message

from app.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ChatResponse
)

from app.security.dependencies import get_current_user

from app.ai.graph import build_chat_graph


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# Build LangGraph once when the service starts
chat_graph = build_chat_graph()


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
# 3. SEND MESSAGE + GET AI RESPONSE
# =========================================================

@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ChatResponse
)
def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    # -----------------------------------------------------
    # Step 1: Check conversation ownership
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Step 2: Load previous messages from PostgreSQL
    # -----------------------------------------------------

    previous_messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.id.asc())
        .all()
    )

    # -----------------------------------------------------
    # Step 3: Convert database messages into history
    # -----------------------------------------------------

    history = []

    for message in previous_messages:
        history.append({
            "role": message.role,
            "content": message.content
        })

    # -----------------------------------------------------
    # Step 4: Save current user's message
    # -----------------------------------------------------

    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=message_data.content
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # -----------------------------------------------------
    # Step 5: Send history + current message to LangGraph
    # -----------------------------------------------------

    result = chat_graph.invoke({
        "message": message_data.content,
        "history": history,
        "response": ""
    })

    ai_response = result["response"]

    # -----------------------------------------------------
    # Step 6: Save AI response
    # -----------------------------------------------------

    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response
    )

    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    # -----------------------------------------------------
    # Step 7: Return both messages
    # -----------------------------------------------------

    return {
        "user_message": user_message,
        "assistant_message": assistant_message
    }


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

    # -----------------------------------------------------
    # Step 1: Check conversation ownership
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Step 2: Get all messages
    # -----------------------------------------------------

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.id.asc())
        .all()
    )

    return messages




