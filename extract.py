import chromadb
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
load_dotenv()
# -----------------------------
# Setup
# -----------------------------
 # replace with your HF token
HF_EMBED_MODEL = "BAAI/bge-large-en-v1.5"
hf_client = InferenceClient(os.getenv('hf_token'))

# Load ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="pdf_collection")

# -----------------------------
# Retrieve relevant embeddings for a query
# -----------------------------
def retrieve_relevant_embeddings(query, top_k=5):
    """
    Embed the query using Hugging Face, then retrieve top_k relevant embeddings from ChromaDB.
    Returns the embeddings, documents, metadata, and IDs.
    """
    # 1. Generate embedding for the query
    query_embedding = hf_client.feature_extraction(query, model=HF_EMBED_MODEL)

    # Flatten if returned as nested list
    if isinstance(query_embedding[0], list):
        query_embedding = query_embedding[0]

    # Wrap in a list for Chroma query
    query_embedding = [query_embedding]

    # 2. Query ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    # 3. Handle no results
    if not results['embeddings'] or results['embeddings'][0] is None:
        print("No relevant embeddings found for this query.")
        return [], [], [], []

    # 4. Extract relevant info
    relevant_embeddings = results["embeddings"][0]
    relevant_documents = results["documents"][0]
    relevant_metadatas = results["metadatas"][0]
    relevant_ids = results["ids"][0]

    return relevant_ids, relevant_embeddings, relevant_documents, relevant_metadatas

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    user_query = "srm"
    ids, embeddings, docs, metadatas = retrieve_relevant_embeddings(user_query, top_k=3)

    print("IDs:", ids)
    print("Embeddings:", embeddings)
    print("Documents:", docs)
    print("Metadatas:", metadatas)
