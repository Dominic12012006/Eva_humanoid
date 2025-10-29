import os
import chromadb
from chromadb.utils import embedding_functions
import ollama

# -----------------------------
# 1. Setup Ollama Embedding (mxbai-embed-large)
# -----------------------------
ollama_ef = embedding_functions.OllamaEmbeddingFunction(model_name="mxbai-embed-large")

def get_embedding(text: str):
    """Return embedding vector for a given text using Ollama embedding model."""
    result = ollama_ef([text])
    return result[0]

# -----------------------------
# 2. Setup Ollama Chat (llama2:7b-chat)
# -----------------------------
def call_llm_rag(prompt: str):
    sys_msg = (
        "You are a helpful guide for students and visitors of SRM University. "
        "Use the provided context about SRM to answer questions accurately."
    )

    full_prompt = f"{sys_msg}\n\n{prompt}"

    response = ollama.chat(
        model="llama2:7b-chat",
        messages=[{"role": "user", "content": full_prompt}]
    )

    return response["message"]["content"]

def call_llm_norm(prompt: str):
    sys_msg = "You are a friendly guide for SRM University visitors."
    full_prompt = f"{sys_msg}\n\n{prompt}"

    response = ollama.chat(
        model="llama2:7b-chat",
        messages=[{"role": "user", "content": full_prompt}]
    )

    return response["message"]["content"]

def llm_classify(prompt: str):
    sys_msg = (
        "You are part of a RAG system. Decide if the user query requires "
        "context about SRM University. Reply with only 'YES' or 'NO'."
        "if its a question referencing a college, even if not srm specifically, return 'YES'."
        "If its a question you lack knowledge on, even if not mentioning a college, return 'YES'"

    )

    full_prompt = f"{sys_msg}\n\n{prompt}"

    response = ollama.chat(
        model="llama2:7b-chat",
        messages=[{"role": "user", "content": full_prompt}]
    )

    return response["message"]["content"].strip().upper()

# -----------------------------
# 3. Connect to ChromaDB collection
# -----------------------------
chroma_client = chromadb.PersistentClient(path="./chroma_db")

try:
    collection = chroma_client.get_collection(name="pdf_collection")
    print("✅ Loaded existing ChromaDB collection from disk.")
except Exception as e:
    print("❌ Failed to load collection:", e)
    exit(1)

# -----------------------------
# 4. Retrieve top documents using query embedding
# -----------------------------
def retrieve_documents(query: str, top_k: int = 3):
    """Compute embedding and query ChromaDB to get top_k docs."""
    query_emb = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=["documents", "distances"]
    )
    return results["documents"][0]

# -----------------------------
# 5. RAG query function
# -----------------------------
def rag_query(query: str):
    context_docs = retrieve_documents(query)
    prompt = f"User query: {query}\n\nContext:\n" + "\n".join(context_docs)
    answer = call_llm_rag(prompt)
    return answer

# -----------------------------
# 6. Main chat loop
# -----------------------------
if __name__ == "__main__":
    print("💬 Chat with your Local RAG AI (type 'exit' to quit)\n")
    while True:
        query = input("You: ").strip()
        if query.lower() == "exit":
            print("👋 Exiting chat. Goodbye!")
            break

        # Optional: classify if RAG needed
        needs_rag = llm_classify(query)
        if needs_rag == "YES":
            answer = rag_query(query)
        else:
            answer = call_llm_norm(query)

        print(f"Eva: {answer}\n")
