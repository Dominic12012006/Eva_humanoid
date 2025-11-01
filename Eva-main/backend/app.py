import os
import chromadb
from huggingface_hub import InferenceClient
from groq import Groq
from fastapi import FastAPI

# app=FastAPI()
# @app.get('/question')
# def get_question():
#     print("a")
import os
from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("hf_token")  # set this in your environment
MODEL_NAME = "BAAI/bge-large-en-v1.5"
hf_client = InferenceClient(api_key=HF_TOKEN)

def get_embedding(text: str):
    """Return embedding vector for a given text using HF model."""
    return hf_client.feature_extraction(text, model=MODEL_NAME)
groq_client = Groq(api_key=os.getenv("groq_api"))

def call_llm_rag(prompt: str):
    sys_msg = (
        "You are a guide to the people in SRM University named 'Eva', u will get relevent context through RAG about the university per query.. Be professional, curt and crisp in your responses. Also always respond in the same language as the language user gives."       
    )

    function_convo = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": prompt}
    ]

    chat_completion = groq_client.chat.completions.create(
        messages=function_convo,
        model="llama-3.3-70b-versatile"
    )

    response = chat_completion.choices[0].message
    return response.content

def call_llm_norm(prompt: str):
    sys_msg = (
        "You are a guide to the people in SRM University named 'Eva'. Be professional, curt and crisp in your responses. Also always respond in the same language as the language user gives."       
    )

    function_convo = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": prompt}
    ]

    chat_completion = groq_client.chat.completions.create(
        messages=function_convo,
        model="llama-3.3-70b-versatile"
    )

    response = chat_completion.choices[0].message
    return response.content

def llm_classify(prompt: str):
    sys_msg = (
        "You are to act as a support to a RAG system, to decide if the user query required additional context related to srm university or not. If context is required, respond with only 'YES', if context is not required answer with only 'NO'. Answer only in 1 word either yes or no."       
    )

    function_convo = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": prompt}
    ]

    chat_completion = groq_client.chat.completions.create(
        messages=function_convo,
        model="llama-3.3-70b-versatile"
    )

    response = chat_completion.choices[0].message
    return response.content


chroma_client = chromadb.PersistentClient(path=r"/home/eva/Desktop/dominic/chroma_db")

try:
    collection = chroma_client.get_collection(name="pdf_collection")
    print("Loaded existing collection from disk.")
except Exception as e:
    print("Failed to load collection:", e)
    exit(1)

def retrieve_documents(query: str, top_k: int = 3):
    """Compute embedding and query ChromaDB to get top_k docs."""
    query_emb = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=["documents", "distances"]
    )
    return results["documents"][0]


def rag_query(query: str):
    context_docs = retrieve_documents(query)
    # Combine query with retrieved documents
    prompt = query + "\n\nContext:\n" + "\n".join(context_docs)
    # Call Groq LLM (chat)
    answer = call_llm_rag(prompt)
    return answer


def summarize(prompt: str):
    sys_msg = (
        "You will be given the output of a chatbot. You need to summarize it such the the output you give , after a tts model, can then be used for voice output by the chatbot. It should be max 2-3 lines after summarisation, UNLESS the user specifies he wants a long explanantion."       
    )

    function_convo = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": prompt}
    ]

    chat_completion = groq_client.chat.completions.create(
        messages=function_convo,
        model="llama-3.3-70b-versatile"
    )

    response = chat_completion.choices[0].message
    return response.content

def checklang(prompt: str):
    sys_msg = (
        "You will be given the output of a chatbot. You need to return 'YES' if the input phonetically makes an English sentence. else return 'NO' "       
    )

    function_convo = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": prompt}
    ]

    chat_completion = groq_client.chat.completions.create(
        messages=function_convo,
        model="llama-3.3-70b-versatile"
    )
    response = chat_completion.choices[0].message
    print(response)

    return response.content


# if __name__ == "__main__":
#     print("Chat with your RAG AI (type 'exit' to quit)\n")
#     while True:
#         query = input("You: ").strip()
#         if query.lower()=="exit":
#             print("Exiting chat. Goodbye!")
#             break
        
#         answer = rag_query(query)
#         print(f"Eva: {answer}\n")
