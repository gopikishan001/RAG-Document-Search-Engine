from fastapi import FastAPI
from app.routes import upload, search

app = FastAPI(title="RAG Document Search Engine")

# Include Routers
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
# app.include_router(search.router, prefix="/search", tags=["Search"])

# Root route
@app.get("/")
def root():
    return {"message": "Welcome to the RAG Document Search Engine!"}
