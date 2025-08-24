# app/services/embedding.py
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # force CPU

from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Always load on CPU
_embedder = SentenceTransformer(MODEL_NAME, device="cpu")


def get_embeddings(texts: list) -> np.ndarray:
    """
    Get embeddings for a list of texts.
    Returns numpy float32 of shape (len(texts), EMBEDDING_DIM).
    """
    if isinstance(texts, str):
        texts = [texts]
    if len(texts) == 0:
        return np.zeros((0, EMBEDDING_DIM), dtype="float32")

    emb = _embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return np.asarray(emb, dtype="float32")


def get_single_embedding(text: str) -> np.ndarray:
    """
    Get embedding for a single text (query).
    Returns numpy float32 of shape (1, EMBEDDING_DIM).
    """
    emb = _embedder.encode([text], convert_to_numpy=True, show_progress_bar=False)
    return np.asarray(emb, dtype="float32").reshape(1, -1)
