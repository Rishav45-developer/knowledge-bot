from fastapi import FastAPI

from app.database.connection import Base, engine
from app.models.conversation import Conversation
from app.models.message import Message
from app.routes.chat import router as chat_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Microservices - Chat Service",
    version="1.0.0"
)


app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "Chat Service is running"
    }