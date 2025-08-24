import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database filename
DB_FILENAME = "app.db"
DATABASE_URL = f"sqlite:///{DB_FILENAME}"

# SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """FastAPI dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize DB tables if DB file does not exist"""
    if not os.path.exists(DB_FILENAME):
        from app.models import User, Document  # import models
        Base.metadata.create_all(bind=engine)
        print(f"Database created: {DB_FILENAME}")
    else:
        print(f"Database already exists: {DB_FILENAME}")


def delete_db():
    """Delete the database file"""
    if os.path.exists(DB_FILENAME):
        os.remove(DB_FILENAME)
        print(f"Database deleted: {DB_FILENAME}")
    else:
        print("No database file found to delete")
