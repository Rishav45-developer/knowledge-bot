
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.database.connection import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    filename = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    extracted_text = Column(
        Text,
        nullable=True
    )

    processing_status = Column(
        String(20),
        nullable=False,
        default="queued",
        server_default="queued"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
