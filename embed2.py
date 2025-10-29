import os
import pdfplumber
import numpy as np
import faiss
import pickle
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# -----------------------------
# Config
# -----------------------------
pdf_path = "hand-book-2024-25.pdf"
faiss_index_path = "pdf_index.faiss"
chunks_path = "all_chunks.pkl"
batch_size = 8
model_name = "nvidia/NV-Embed-v2"

# -----------------------------
# 1. Load SentenceTransformer model
# -----------------------------
model = SentenceTransformer(model_name, device="cuda", trust_remote_code=True)

# -----------------------------
# 2. Check for existing FAISS index
# -----------------------------
if os.path.exists(faiss_index_path) and os.path.exists(chunks_path):
    print("Loading existing FAISS index and chunks...")
    index = faiss.read_index(faiss_index_path)
    with open(chunks_path, "rb") as f:
        all_chunks = pickle.load(f)
    print(f"Loaded FAISS index with {index.ntotal} vectors and {len(all_chunks)} chunks.")
else:
    # -----------------------------
    # 3. Extract text from PDF
    # -----------------------------
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
    print(f"Extracted {len(pages_text)} pages")

    # -----------------------------
    # 4. Chunk text
    # -----------------------------
    def chunk_text(text, max_words=200):
        words = text.split()
        chunks = []
        for i in range(0, len(words), max_words):
            chunk = " ".join(words[i:i+max_words])
            chunks.append(chunk)
        return chunks

    all_chunks = []
    for page_text in pages_text:
        all_chunks.extend(chunk_text(page_text))
    print(f"Total chunks: {len(all_chunks)}")

    # -----------------------------
    # 5. Embed text chunks
    # -----------------------------
    all_embeddings = []

    for i in tqdm(range(0, len(all_chunks), batch_size), desc="Embedding chunks"):
        batch_chunks = all_chunks[i:i+batch_size]
        batch_emb = model.encode(batch_chunks, convert_to_numpy=True, show_progress_bar=False)
        all_embeddings.append(batch_emb)

    all_embeddings = np.vstack(all_embeddings)
    print("All embeddings shape:", all_embeddings.shape)

    # -----------------------------
    # 6. Create FAISS index
    # -----------------------------
    dim = all_embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity (inner product)
    index.add(all_embeddings)
    print(f"FAISS index contains {index.ntotal} vectors")

    # -----------------------------
    # 7. Save FAISS index + chunks
    # -----------------------------
    faiss.write_index(index, faiss_index_path)
    with open(chunks_path, "wb") as f:
        pickle.dump(all_chunks, f)
    print("Saved FAISS index and chunks mapping.")

# -----------------------------
# 8. Querying
# -----------------------------
def search_query(query, k=5):
    query_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_emb)
    D, I = index.search(query_emb, k)
    print("Top-k indices:", I)
    print("Distances:", D)
    for idx in I[0]:
        print(all_chunks[idx])


# Example query
search_query("srm chancellor", k=5)
