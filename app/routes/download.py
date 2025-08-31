from fastapi import HTTPException
from fastapi.responses import FileResponse

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import os
from app.database import get_db
from app.models import User, Document

router = APIRouter()

@router.get("/download/{doc_id}")
def download_file(doc_id: int, db: Session = Depends(get_db)):
    # Find document

    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Build file path (where we saved uploads earlier)
    user = db.query(User).filter(User.user_id == doc.user_id).first()
    user_folder = os.path.join("data/uploads", user.email)
    file_path = os.path.join(user_folder, f"{doc.doc_id}_{doc.doc_name}")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(
        path=file_path,
        filename=doc.doc_name,
        media_type="application/octet-stream"
    )
