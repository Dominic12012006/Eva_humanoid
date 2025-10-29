import os
import time
import PyPDF2
import chromadb
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
load_dotenv()

MODEL_NAME = "BAAI/bge-large-en-v1.5"
client = InferenceClient(os.getenv('hf_token'))

def load_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            else:
                print(f"Skipping empty page {i}")
    return text

pdf_path = "hand-book-2024-25.pdf"
pdf_text = load_pdf(pdf_path)

# -----------------------------
# 2. Chunk the text
# -----------------------------
def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

chunks = chunk_text(pdf_text)
print(f"Total chunks: {len(chunks)}")

# -----------------------------
# 3. Setup Persistent ChromaDB
# -----------------------------
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Try to get existing collection, otherwise create new
try:
    collection = chroma_client.get_collection(name="pdf_collection")
    print("Loaded existing collection from disk.")
except:
    collection = chroma_client.create_collection(name="pdf_collection")
    print("Created new collection.")

# -----------------------------
# 4. Function to get embedding
# -----------------------------
def get_embedding(text):
    result = client.feature_extraction(text, model=MODEL_NAME)
    return result

# -----------------------------
# 5. Add chunks to Chroma in batches
# -----------------------------
# -----------------------------
# 5. Add chunks to Chroma in batches
# -----------------------------
batch_size = 20
for i in range(0, len(chunks), batch_size):
    batch_chunks = chunks[i:i+batch_size]
    batch_ids = [f"doc_{j}" for j in range(i, i+len(batch_chunks))]

    # Generate embeddings
    batch_embeddings = [get_embedding(c) for c in batch_chunks]

    # Add to collection
    collection.add(
        documents=batch_chunks,
        embeddings=batch_embeddings,
        ids=batch_ids
    )

    print(f"Inserted batch {i} to {i+len(batch_chunks)-1}")
    time.sleep(0.5)


print("All chunks successfully embedded and stored in persistent ChromaDB!")
