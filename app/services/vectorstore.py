import os
import faiss
import pickle
import numpy as np
from app.services.embedding import get_embeddings, get_single_embedding, EMBEDDING_DIM

DATA_DIR = "data/vectordb"


def split_text(text: str, chunk_size: int = 30, overlap: int = 5) -> list[str]:
    """
    Split text into smaller chunks with optional overlap.
    """
        
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def update_vectorstore(email: str, doc_id: int, text_content):
    """
    Split document into chunks and add to user's FAISS index.
    """

    text_chunks = split_text(text_content)

    embeddings = get_embeddings(text_chunks)

    # User folder
    user_folder = os.path.join(DATA_DIR, email)
    os.makedirs(user_folder, exist_ok=True)

    index_file = os.path.join(user_folder, "vectordb.index")
    chunks_file = os.path.join(user_folder, "chunks.pkl")

    if os.path.exists(index_file) and os.path.exists(chunks_file):
        # Load existing index + chunks
        index = faiss.read_index(index_file)
        with open(chunks_file, "rb") as f:
            all_chunks = pickle.load(f)
    else:
        # Create new index + chunks
        index = faiss.IndexFlatL2(EMBEDDING_DIM)
        all_chunks = {}

    # Add new embeddings to index
    index.add(embeddings)

    # Store chunks by doc_id
    all_chunks[doc_id] = text_chunks

    # Save back
    faiss.write_index(index, index_file)
    with open(chunks_file, "wb") as f:
        pickle.dump(all_chunks, f)


def get_faiss_results(email: str, query: str, top_k: int = 5):
    """
    Retrieve top-k chunks from the user's FAISS index for a query
    """
    user_folder = os.path.join(DATA_DIR, email)
    index_file = os.path.join(user_folder, "vectordb.index")
    chunks_file = os.path.join(user_folder, "chunks.pkl")

    if not os.path.exists(index_file) or not os.path.exists(chunks_file):
        return []

    # Load index + chunks
    index = faiss.read_index(index_file)
    with open(chunks_file, "rb") as f:
        all_chunks = pickle.load(f)

    # Flatten chunks (doc_id → chunks)
    flat_chunks = []
    chunk_map = []  # maps index position → (doc_id, chunk_idx)
    for doc_id, chunks in all_chunks.items():
        for i, ch in enumerate(chunks):
            flat_chunks.append(ch)
            chunk_map.append((doc_id, i))

    # Encode query
    query_vec = get_single_embedding(query)

    # Search
    distances, indices = index.search(query_vec, top_k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx < len(flat_chunks):
            doc_id, chunk_idx = chunk_map[idx]
            results.append({
                "doc_id": doc_id,
                "chunk": flat_chunks[idx],
                "distance": float(dist)
            })

    return results
