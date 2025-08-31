from fastapi import FastAPI, Request, Cookie, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from app.database import get_db, init_db
from app.models import User, Document

# Services
from app.services.vectorstore import get_faiss_results
from app.services.llm import generate_answer

# Routers
from app.routes import upload, download, delete
from app.auth import routes as auth_routes
from app.docs import routes as docs_routes

init_db()

app = FastAPI(title="RAG Document Search Engine", version="0.1.0")

# Static & templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def root(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/home")
def home(request: Request, user_id: str = Cookie(None), db: Session = Depends(get_db)):
    """User dashboard showing uploaded docs + search bar"""
    if not user_id:
        return RedirectResponse(url="/")

    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/")

    documents = db.query(Document).filter(Document.user_id == user.user_id).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "email": user.email,
            "documents": documents,
            "query": "",
            "faiss_results": [],
            "llm_answer": "",
            "top_k": 3,
            "temperature": 0.2,
            "max_tokens" : 30,
        }
    )


@app.post("/search")
def perform_search(
    request: Request,
    user_id: str = Cookie(None),
    query: str = Form(...),
    top_k: int = Form(5),
    temperature: float = Form(0.7),
    max_tokens: int = Form(5),
    db: Session = Depends(get_db),
):
    """Perform RAG search across all docs for this user"""
    if not user_id:
        return RedirectResponse(url="/")

    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if not user:
        return RedirectResponse(url="/")

    documents = db.query(Document).filter(Document.user_id == user.user_id).all()

    # 1. FAISS retrieval (search across user's vector DB)
    faiss_results = get_faiss_results(user.email, query, top_k)

    # 2. LLM answer
    llm_answer = generate_answer(faiss_results, query, temperature, max_tokens)

    search = {
        "query": query,
        "results": [
            {"doc_id": r["doc_id"], "doc_name": f"Doc {r['doc_id']}", "text": r["chunk"]}
            for r in faiss_results
        ],
        "answer": llm_answer
    }

    # Only render results snippet
    return templates.TemplateResponse(
        "search_results.html",
        {
            "request": request,
            "search": search
        }
    )

    # return templates.TemplateResponse(
    #     "index.html",
    #     {
    #         "request": request,
    #         "email": user.email,
    #         "documents": documents,
    #         "search": {
    #             "query": query,
    #             "results": [
    #                 {"doc_id": r["doc_id"], "text": r["chunk"], "doc_name": "Document"}  # add doc_name if you have
    #                 for r in faiss_results
    #             ],
    #             "answer": llm_answer
    #         },
    #         "top_k": top_k,
    #         "temperature": temperature,
    #     }
    # )

@app.get("/health")
def health():
    return {"status": "ok"}


# Routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(docs_routes.router, prefix="/docs", tags=["Docs"])
app.include_router(download.router, prefix="/docs", tags=["Download"])
app.include_router(delete.router, prefix="/docs", tags=["Delete"])
