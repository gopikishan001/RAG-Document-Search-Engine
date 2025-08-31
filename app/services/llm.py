import os

# ========= CONFIG =========
MODE = "offline"       # "online" or "offline"
LIBRARY = "huggingface"   # "openai" or "huggingface"
# ==========================


# --- Base function (default stub) ---
def generate_answer(faiss_results, query, temperature=0.2, max_tokens=50):
    return f"LLM call function not implemented for this MODE - LIBRARY :: {MODE} - {LIBRARY}"


# === OPENAI (online only) ===
if LIBRARY == "openai" and MODE == "online":
    from openai import OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY must be set in environment")

    client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_answer(faiss_results, query, temperature=0.2, max_tokens=50):
        context = "\n".join([res["chunk"] for res in faiss_results])
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # you can change to "gpt-4o"
            messages=[
                {"role": "system", "content": "You are a helpful assistant who answers strictly based on context."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message["content"]


# === HUGGING FACE (online API) ===
elif LIBRARY == "huggingface" and MODE == "online":
    import requests
    HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN must be set in environment for Hugging Face API")

    API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

    def generate_answer(faiss_results, query, temperature=0.2, max_tokens=50):
        context = "\n".join([res["chunk"] for res in faiss_results])
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"

        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "do_sample": True
            }
        }

        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()
        return result[0]["generated_text"][len(prompt):].strip()


# === HUGGING FACE (offline/local) ===
elif LIBRARY == "huggingface" and MODE == "offline":
    from transformers import pipeline

    # NOTE: only small models will work with 4GB RAM
    HF_MODEL = "distilgpt2"
    generator = pipeline("text-generation", model=HF_MODEL)

    def generate_answer(faiss_results, query, temperature=0.2, max_tokens=50):
        context = "\n".join([res["chunk"] for res in faiss_results])
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"

        outputs = generator(
            prompt,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True
        )

        return outputs[0]["generated_text"][len(prompt):].strip()
