from fastapi import FastAPI, Depends

from app.database.connection import Base, engine
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.routes.document import router as document_router   
from app.security.dependencies import get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Microservices - Document Service",
    version="1.0.0"

)

app.include_router(document_router)

@app.get("/")
def root():
    return {
        "message": "Document Service is running"
    }


@app.get("/documents/test")
def test_auth(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "JWT authentication working",
        "user_id": current_user.get("sub"),
        "email": current_user.get("email"),
        "role": current_user.get("role")
    }