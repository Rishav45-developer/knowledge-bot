
import logging
import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.document import (
    DocumentResponse,
    DocumentSearchRequest,
)
from app.security.dependencies import get_current_user
from app.vectorstore.chroma import (
    search_chunks,
    delete_document_chunks,
)
from app.worker.producer import publish_document_job


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

UPLOAD_DIR = "/app/uploads"


# --------------------------------------------------
# Upload document and queue processing
# --------------------------------------------------

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required",
        )

    original_filename = os.path.basename(file.filename)
    stored_filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    document = None

    try:
        # 1. Save the uploaded file.
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Save document metadata in PostgreSQL.
        document = Document(
            user_id=user_id,
            filename=original_filename,
            file_path=file_path,
            extracted_text=None,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # 3. Queue asynchronous processing.
        try:
            publish_document_job(document.id)

        except Exception as error:
            db.delete(document)
            db.commit()

            if os.path.exists(file_path):
                os.remove(file_path)

            raise HTTPException(
                status_code=503,
                detail=(
                    "Could not queue document processing. "
                    "Please try again."
                ),
            ) from error

        return {
            "message": "Document uploaded and processing job queued",
            "document_id": document.id,
            "filename": document.filename,
            "processing_status": "queued",
        }

    except HTTPException:
        raise

    except Exception as error:
        db.rollback()

        if os.path.exists(file_path):
            os.remove(file_path)

        logger.exception(
            "Document upload failed for user_id=%s",
            user_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Document upload failed.",
        ) from error

    finally:
        file.file.close()


# --------------------------------------------------
# Get my documents
# --------------------------------------------------

@router.get("/", response_model=list[DocumentResponse])
def get_my_documents(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])

    return (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.id.desc())
        .all()
    )


# --------------------------------------------------
# Semantic document search
# --------------------------------------------------

@router.post("/search")
def search_documents(
    search_data: DocumentSearchRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])
    query = search_data.query.strip()
    n_results = search_data.n_results
    document_id = search_data.document_id

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    # If a document was selected, make sure it belongs to this user.
    if document_id is not None:
        owned_document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == user_id,
            )
            .first()
        )

        if owned_document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found.",
            )

    logger.info(
        "Document search started: user_id=%s, document_id=%s, "
        "query=%r, n_results=%s",
        user_id,
        document_id,
        query,
        n_results,
    )

    try:
        results = search_chunks(
            query=query,
            user_id=user_id,
            n_results=n_results,
            document_id=document_id,
        )

        logger.info(
            "Document search succeeded: user_id=%s, result_count=%s",
            user_id,
            len(results.get("ids", [[]])[0]),
        )

        return results

    except Exception as error:
        logger.exception(
            "Document search failed: user_id=%s, query=%r",
            user_id,
            query,
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Document search is temporarily unavailable. "
                "Please try again."
            ),
        ) from error

# --------------------------------------------------
# Get single document
# --------------------------------------------------

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document


# --------------------------------------------------
# Delete document
# --------------------------------------------------

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = int(current_user["sub"])

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    file_path = document.file_path

    try:
        # 1. Delete vectors belonging to this document.
        delete_document_chunks(
            document_id=document.id,
            user_id=user_id,
        )

        # 2. Delete PostgreSQL chunk records.
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).delete(synchronize_session=False)

        # 3. Delete the document record.
        db.delete(document)
        db.commit()

        # 4. Remove the uploaded file after the commit.
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "message": "Document deleted successfully"
        }

    except Exception as error:
        db.rollback()

        logger.exception(
            "Document deletion failed: document_id=%s, user_id=%s",
            document_id,
            user_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Document deletion failed.",
        ) from error
