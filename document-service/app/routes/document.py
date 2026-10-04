import os
import shutil

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.models.document import Document
from app.models.document_chunk import DocumentChunk

from app.schemas.document import DocumentResponse

from app.security.dependencies import get_current_user

from app.extractors.text_extractor import extract_text
from app.processors.chunker import split_text


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


UPLOAD_DIR = "uploads"


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get the logged-in user's ID from the JWT
    user_id = int(current_user["sub"])

    # Create uploads folder if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Create the file path
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text from the uploaded document
    extracted_text = extract_text(file_path)

    # Split extracted text into smaller chunks
    chunks = split_text(extracted_text)

    # Create the document record
    document = Document(
        user_id=user_id,
        filename=file.filename,
        file_path=file_path,
        extracted_text=extracted_text
    )

    db.add(document)

    # Get the generated document ID before creating chunks
    db.flush()

    # Create a database record for every chunk
    for index, chunk in enumerate(chunks):

        document_chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk
        )

        db.add(document_chunk)

    # Save document and chunks
    db.commit()

    # Refresh document from database
    db.refresh(document)

    return document


@router.get("/", response_model=list[DocumentResponse])
def get_my_documents(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    documents = (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.id.desc())
        .all()
    )

    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(current_user["sub"])

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Delete the physical file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete the document record
    db.delete(document)

    db.commit()

    return {
        "message": "Document deleted successfully"
    }