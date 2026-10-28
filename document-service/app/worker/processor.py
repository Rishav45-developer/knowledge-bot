
import logging

from app.database.connection import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.extractors.text_extractor import extract_text
from app.processors.chunker import split_text
from app.vectorstore.chroma import store_chunk, delete_document_chunks


logger = logging.getLogger(__name__)


def process_document(document_id: int) -> None:
    """Extract, split, and index one uploaded document."""
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document is None:
            raise ValueError(f"Document {document_id} not found")

        document.processing_status = "processing"
        db.commit()

        try:
            extracted_text = extract_text(document.file_path)

            if not extracted_text or not extracted_text.strip():
                raise ValueError(
                    "No text could be extracted from the document"
                )

            chunks = split_text(extracted_text)

            if not chunks:
                raise ValueError(
                    "Document processing produced no text chunks"
                )

            # Remove existing vectors and chunks before reprocessing.
            delete_document_chunks(
                document.id,
                document.user_id,
            )

            db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document.id
            ).delete(synchronize_session=False)

            document.extracted_text = extracted_text

            for index, chunk in enumerate(chunks):
                db.add(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=index,
                        content=chunk,
                    )
                )

                store_chunk(
                    chunk_id=f"{document.id}-{index}",
                    content=chunk,
                    document_id=document.id,
                    chunk_index=index,
                    user_id=document.user_id,
                    filename=document.filename,
                )

            document.processing_status = "completed"
            db.commit()

            logger.info(
                "Document %s processed successfully",
                document_id,
            )

        except Exception:
            db.rollback()

            # Record the failure without hiding the original exception.
            try:
                failed_document = (
                    db.query(Document)
                    .filter(Document.id == document_id)
                    .first()
                )

                if failed_document is not None:
                    failed_document.processing_status = "failed"
                    db.commit()

            except Exception:
                db.rollback()
                logger.exception(
                    "Could not update failure status for document %s",
                    document_id,
                )

            # Notify the RabbitMQ consumer so it can handle the failure.
            raise

    finally:
        db.close()
