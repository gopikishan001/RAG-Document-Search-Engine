# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)  # store hashed passwords
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="owner")


class Document(Base):
    __tablename__ = "doc_data"

    doc_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    doc_uploaded_date = Column(DateTime, default=datetime.utcnow)
    doc_name = Column(String, nullable=False)
    size = Column(Integer)
    total_words = Column(Integer)
    total_sentences = Column(Integer)

    owner = relationship("User", back_populates="documents")
