import os
import chromadb
from huggingface_hub import InferenceClient
import time
import os
from dotenv import load_dotenv

load_dotenv()
# -----------------------------
# 0. API setup
# -----------------------------
# Hugging Face API (for embeddings only)
  # replace with your HF token
hf_client = InferenceClient(os.getenv('hf_token'))
HF_EMBED_MODEL = "BAAI/bge-large-en-v1.5"

# OpenRouter API (for conversation)
OPENROUTER_KEY = ""  # replace with your OpenRouter key
or_client = InferenceClient(os.getenv('open_router_key'))
OR_MODEL = "openai/gpt-oss-20b"


# -----------------------------
# 1. Load persistent ChromaDB collection
# -----------------------------
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="pdf_collection")

# -----------------------------
# 2. Retrieve relevant chunks for a query
# -----------------------------
def retrieve_context(query, top_k=5):
    """
    Embed the query using HF, then retrieve top_k relevant chunks from ChromaDB.
    """
    # Generate embedding via HF
    query_embedding = hf_client.feature_extraction(query, model=HF_EMBED_MODEL)

    # Retrieve from Chroma
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    
    # Combine retrieved chunks into context
    context = "\n\n".join(results["documents"][0])
    return context

# -----------------------------
# 3. Generate answer using OpenRouter LLM
# -----------------------------
def generate_answer(question, context):
    """
    Feed the question and retrieved context to OpenRouter LLM to get an answer.
    """
    prompt = f"""
You are a helpful assistant. Use the following context to answer the question.
Context:
{context}

Question: {question}
Answer:"""

    response = hf_client.text_generation(
        model=OR_MODEL,
        prompt=prompt,
        max_new_tokens=500,
        temperature=0.3
    )
    
    # HF/OpenRouter API returns a list of dicts
    return response[0]['generated_text']

# -----------------------------
# 4. Chat loop
# -----------------------------
if __name__ == "__main__":
    print("Type 'exit' or 'quit' to stop.\n")
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            break

        # Retrieve relevant context from ChromaDB
        context = retrieve_context(query)

        # Generate answer using OpenRouter LLM
        answer = generate_answer(query, context)
        print("\nAI:", answer)
