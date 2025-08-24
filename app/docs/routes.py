from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Document

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request, email: str = None, db: Session = Depends(get_db)):
    """
    Render home page showing all documents for the logged-in user.
    email: email of the logged-in user (can be replaced with session/JWT later)
    """
    if not email:
        return {"error": "Email required to view documents"}

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"error": "User not found"}

    documents = db.query(Document).filter(Document.user_id == user.user_id).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "email": email,
            "documents": documents,
            "title": f"{email}'s Documents"
        }
    )
