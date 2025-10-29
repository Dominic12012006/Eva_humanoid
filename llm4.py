import os
import chromadb
from huggingface_hub import InferenceClient
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
# -----------------------------
# 1. Setup Hugging Face for embeddings
# -----------------------------
HF_TOKEN = os.getenv('hf_token')  # better to export it in your environment
MODEL_NAME = "BAAI/bge-large-en-v1.5"
hf_client = InferenceClient(api_key=HF_TOKEN)

def get_embedding(text: str):
    """Return embedding vector for a given text using HF model."""
    return hf_client.feature_extraction(text, model=MODEL_NAME)

# -----------------------------
# 2. Setup OpenAI client (for reasoning + chat)
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------
# 3. Connect to ChromaDB collection
# -----------------------------
chroma_client = chromadb.PersistentClient(path="./chroma_db")

try:
    collection = chroma_client.get_collection(name="pdf_collection")
    print("✅ Loaded existing collection from disk.")
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
# 5. LLM Functions
# -----------------------------

def call_llm_rag(prompt: str):
    """Call GPT with context-based RAG reasoning."""
    sys_msg = "You are a guide to the people in SRM University. You will receive relevant context from RAG about the university per query."

    response = client.responses.create(
        model="gpt-5",
        reasoning={"effort": "medium"},
        input=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt}
        ]
    )

    return response.output_text


def call_llm_norm(prompt: str):
    """Normal (non-RAG) GPT query."""
    sys_msg = "You are a helpful guide to the people in SRM University."

    response = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt}
        ]
    )

    return response.output_text


def llm_classify(prompt: str):
    """Check if RAG context is required."""
    sys_msg = (
        "You are a RAG support classifier. "
        "If the user query requires additional SRM University context, respond only with 'YES'. "
        "If not, respond only with 'NO'."
    )

    response = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt}
        ]
    )

    return response.output_text.strip().upper()


def summarize(prompt: str):
    """Summarize chatbot output for TTS (short voice-friendly form)."""
    sys_msg = (
        "You will be given chatbot output. Summarize it so it’s suitable for short voice output (2-3 lines), "
        "unless the user explicitly asked for a long explanation."
    )

    response = client.responses.create(
        model="gpt-5",
        input=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt}
        ]
    )

    return response.output_text

# -----------------------------
# 6. RAG query function
# -----------------------------
def rag_query(query: str):
    """Perform RAG + GPT reasoning."""
    # Step 1: Classification
    classification = llm_classify(query)
    if classification == "YES":
        context_docs = retrieve_documents(query)
        prompt = f"{query}\n\nContext:\n" + "\n".join(context_docs)
        answer = call_llm_rag(prompt)
    else:
        answer = call_llm_norm(query)
    return answer

