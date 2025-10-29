# import chromadb

# # -----------------------------
# # 1. Connect to persistent ChromaDB
# # -----------------------------
# chroma_client = chromadb.PersistentClient(path="./chroma_db")

# # Get the same collection used before
# collection = chroma_client.get_collection(name="pdf_collection")

# # -----------------------------
# # 2. View first 5 chunks
# # -----------------------------
# count = collection.count()
# print(f"Total records in collection: {count}")

# results = collection.get(include=["documents"])

# print("\n--- First 5 Chunks ---")
# for i, (doc_id, doc_text) in enumerate(zip(results["ids"], results["documents"])):
#     if i >= 5:
#         break
#     print(f"\n=== Chunk {i} | ID: {doc_id} ===")
#     print(doc_text[:500] + ("..." if len(doc_text) > 500 else ""))

import chromadb
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
load_dotenv()
# -----------------------------
# Hugging Face setup for your query embedding
# -----------------------------

MODEL_NAME = "BAAI/bge-large-en-v1.5"
client = InferenceClient(os.getenv('hf_token'))

def get_embedding(text):
    """Return vector embedding using Hugging Face model."""
    return client.feature_extraction(text, model=MODEL_NAME)

# -----------------------------
# Connect to persistent ChromaDB
# -----------------------------
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="pdf_collection")
print("Loaded collection from disk.")

# -----------------------------
# Compute embedding for test query
# -----------------------------
test_query = "What is the vision of SRM Institute of Science and Technology?"
query_emb = get_embedding(test_query)  # returns a vector

# -----------------------------
# Query using embedding directly
# -----------------------------
results = collection.query(
    query_embeddings=[query_emb],  # pass embedding instead of query_texts
    n_results=3,
    include=["documents", "distances"]  # IDs can be in metadatas if you stored them
)

# -----------------------------
# Print top results
# -----------------------------
print(f"\n🔎 Test Query: {test_query}")
print("\n--- Top Retrieved Chunks ---")
for i, (doc, dist) in enumerate(zip(results["documents"][0], results["distances"][0])):
    similarity = 1 - dist
    print(f"\n=== Match {i+1} | similarity={similarity:.4f} ===")
    print(doc[:500] + ("..." if len(doc) > 500 else ""))
