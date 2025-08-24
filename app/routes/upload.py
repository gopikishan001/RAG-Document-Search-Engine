from fastapi import APIRouter, UploadFile, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from datetime import datetime
from app.database import get_db
from app.models import User, Document
from app.services.vectorstore import update_vectorstore


router = APIRouter()

UPLOAD_DIR = "data/uploads"


@router.post("/")
async def upload_file(
    file: UploadFile,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    # Find user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"error": "User not found"}

    # Create user folder if not exists
    user_folder = os.path.join(UPLOAD_DIR, email)
    os.makedirs(user_folder, exist_ok=True)

    # Save file temporarily
    file_path = os.path.join(user_folder, file.filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Calculate metadata
    size_kb = len(content) // 1024
    text_content = content.decode("utf-8", errors="ignore")
    total_words = len(text_content.split())
    total_sentences = text_content.count(".")

    # Add document entry to DB
    new_doc = Document(
        user_id=user.user_id,
        doc_uploaded_date=datetime.now(),
        doc_name=file.filename,
        size=size_kb,
        total_words=total_words,
        total_sentences=total_sentences
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Rename file with doc_id
    new_file_path = os.path.join(user_folder, f"{new_doc.doc_id}_{file.filename}")
    os.rename(file_path, new_file_path)

    # --- FAISS indexing ---
    update_vectorstore(email, new_doc.doc_id, text_content)

    return RedirectResponse(url="/home", status_code=302)

