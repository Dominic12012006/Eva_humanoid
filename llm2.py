import chromadb
from huggingface_hub import InferenceClient
from llama_index import ServiceContext, VectorStoreIndex, load_index_from_storage, StorageContext
from llama_index.llms.groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

hf_client = InferenceClient(os.getenv('hf_token'))
# Initialize Groq client
groq_llm = Groq(model="llama3-70b-8192", api_key=os.getenv('groq_api'))

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="pdf_collection")

def get_embedding(text: str):
    """Generate embedding for the given text using Hugging Face model."""
    return hf_client.feature_extraction(text, model="BAAI/bge-large-en-v1.5")

def retrieve_documents(query_emb: list, top_k: int = 3):
    """Retrieve top_k documents from ChromaDB based on the query embedding."""
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=["documents"]
    )
    return results["documents"][0]

def generate_response(query: str, context: list):
    """Generate a response using Groq's LLM."""
    # Combine query with context
    combined_input = query + "\n\n" + "\n".join(context)
    # Send to Groq API for inference
    response = groq_llm.complete(combined_input)
    return response

def rag_query(query: str):
    """Perform RAG by retrieving relevant documents and generating a response."""
    # Step 1: Compute query embedding
    query_emb = get_embedding(query)
    # Step 2: Retrieve relevant documents
    context = retrieve_documents(query_emb)
    # Step 3: Generate response using LLM via Groq
    response = generate_response(query, context)
    return response

if __name__ == "__main__":
    query = "What is the vision of SRM Institute of Science and Technology?"
    answer = rag_query(query)
    print("Answer:", answer)
