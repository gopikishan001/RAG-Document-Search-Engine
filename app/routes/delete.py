from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.models import User, Document

import os
import faiss
import pickle
from app.services.embedding import get_embeddings, get_single_embedding, EMBEDDING_DIM


router = APIRouter()

@router.delete("/delete/{doc_id}")
def delete_file(doc_id: int, db: Session = Depends(get_db)):

    # 1. Find document in SQL
    doc = db.query(Document).filter(Document.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    user = db.query(User).filter(User.user_id == doc.user_id).first()
    user_email = user.email

    try :
        db.delete(doc)
        db.commit()
    except Exception as e:
        print(f"SQL entry delete error: {e}")

    # # 2. Delete from vector DB
    user_folder = os.path.join("data/vectordb", user_email)  
    index_file = os.path.join(user_folder, "vectordb.index")
    chunks_file = os.path.join(user_folder, "chunks.pkl")


    if os.path.exists(index_file) and os.path.exists(chunks_file):
        # Load existing index + chunks
        with open(chunks_file, "rb") as f:
            all_chunks = pickle.load(f)

        if doc_id in all_chunks:
            del all_chunks[doc_id]  # remove the chunks for this doc

            # Rebuild FAISS index from remaining chunks
            flat_chunks = []
            for chunks in all_chunks.values():
                flat_chunks.extend(chunks)

            if flat_chunks:
                embeddings = get_embeddings(flat_chunks)
                index = faiss.IndexFlatL2(EMBEDDING_DIM)
                index.add(embeddings)
                faiss.write_index(index, index_file)
            else:
                # No chunks left, delete index file
                os.remove(index_file)

            # Save updated chunks
            with open(chunks_file, "wb") as f:
                pickle.dump(all_chunks, f)


    # 3. Delete local file
    user_folder = os.path.join("data/uploads", user_email)
    file_path = os.path.join(user_folder, f"{doc.doc_id}_{doc.doc_name}")
    if os.path.exists(file_path):
        os.remove(file_path)


    # 6. Redirect to home page
    return RedirectResponse(url="/home", status_code=303)
