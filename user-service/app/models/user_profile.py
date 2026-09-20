from sqlalchemy import Column, Integer, String, Text

from app.database.connection import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        unique=True,
        nullable=False,
        index=True 
    )

    full_name = Column(
        String(100),
        nullable=True
    )

    bio = Column(
        Text,
        nullable=True
    )

    profile_image = Column(
        String(255),
        nullable=True
    )
    