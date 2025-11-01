import threading
import io
import json
import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile,Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import chromadb
from . import models, schemas
from .database import engine, SessionLocal
from .background import callback
from .app import rag_query,call_llm_norm,llm_classify,checklang
from .voice import audio_to_text
import speech_recognition as sr
import time
from .tts import speak
from dotenv import load_dotenv
import re
from elevenlabs.client import ElevenLabs
import os
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
logger = logging.getLogger("uvicorn.error")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_transcript = ""
wake_detected = False
transcript_lock = threading.Lock()
load_dotenv()

elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)
#USE FUZZY LOGIC
#SET TIME LIMIT ONCE WAKE WORD IS SAID INSTEAD OF REPEATING KEYWORD
#CHANGE WAKE WORD


conversation_history = []  # list of dicts like [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]

def add_to_history(role, content):
    """Add a new message to conversation history."""
    conversation_history.append({"role": role, "content": content})
    # Limit history length to prevent context overload
    if len(conversation_history) > 5:
        conversation_history.pop(0)

def get_context_text():
    """Convert history to a text-based context for passing into LLM."""
    context = ""
    for msg in conversation_history:
        prefix = "User:" if msg["role"] == "user" else "Assistant:"
        context += f"{prefix} {msg['content']}\n"
    return context.strip()
def checkwake(audio_data):
    try:
        # Convert recorded audio to BytesIO
        audio_file = io.BytesIO(audio_data.get_wav_data())

        # Call ElevenLabs speech-to-text
        transcription = elevenlabs.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",      # ElevenLabs transcription model
            tag_audio_events=False,    # optional: True if you want events
            language_code="eng",
            diarize=False              # optional: True if multiple speakers
        )

        return transcription.text
    except Exception as e:
        print("Error transcribing audio:", e)
        return None


def extract_prompt_word(transcribed_text, wake_word):
    """Extracts the prompt after the wake word (e.g., 'hello, tell me a joke')."""
    pattern = rf'\b{re.escape(wake_word)}[\s,.?!]*(.*)'
    match = re.search(pattern, transcribed_text, re.IGNORECASE)
    return match.group(1).strip() if match else None
def extract_prompt(transcribed_text, wake_words):
    for wake_word in wake_words:
        text=extract_prompt_word(transcribed_text, wake_word)
        if text:
            return text
    return None
r = sr.Recognizer()
r.pause_threshold=1.2
wake_words = ["eva","इवा","ईवा","ഇവ","இவா"]
mic_index = 24
source = sr.Microphone(device_index=mic_index)

def callback(recognizer, audio):
    global current_transcript, wake_detected
    data = audio.get_wav_data()
    if len(data) < 1000:
        print("Warning: captured audio seems too short.")
        return

    try:
        prompt=audio_to_text(audio,'hin')

        if prompt:
            clean_prompt=extract_prompt(prompt,wake_words)
            if clean_prompt:
                with transcript_lock:
                        current_transcript = clean_prompt
                wake_detected = True
                classify = llm_classify(clean_prompt).lower()
                print(f"Classification: {classify}")

                # Add user message to history
                add_to_history("user", clean_prompt)

                context = get_context_text()
                combined_prompt = f"{context}\nUser: {clean_prompt}\nAssistant:"
                #####print clean_promnpt
                ######stop animation
                if "yes" in classify:
                    print(f"\nRAG USER: {clean_prompt}")
                    res = rag_query(combined_prompt)
                else:
                    print(f"\nNORM USER: {clean_prompt}")
                    res = call_llm_norm(combined_prompt)
                ######print res
                # Add assistant response to history
                add_to_history("assistant", res)
                # res_sum=summarize(res)
                #dddd chatbot output
                print(f"\nAssistant: {res}\n")
                ######speaking animation
                speak(res)
                #####stop speak ani
                print("done")

    except Exception as e:
        print("Error in callback:", e)

def start_listening():
    print("Adjusting for ambient noise, please wait...")
    with source as s:
        r.adjust_for_ambient_noise(s, duration=1)
        print(f"\nSay eva followed by your prompt.\n")

        # Test mic once
        # print("Testing mic with one recording...")
        # audio = r.listen(s, timeout=10, phrase_time_limit=15)
        # print(f"Captured {len(audio.get_wav_data())} bytes of audio!")

    stop_listening = r.listen_in_background(source, callback)

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping ASR...")
        stop_listening(wait_for_stop=False)
        print("\nConversation History:")
        for i, msg in enumerate(conversation_history):
            print(f"{i+1}. {msg['role'].capitalize()}: {msg['content']}")

stop_listening = None  # Declare globally so callback can access it

def callback_landing(recognizer, audio):
    global current_transcript, wake_detected, stop_listening

    data = audio.get_wav_data()
    if len(data) < 1000:
        print("Warning: captured audio seems too short.")
        return

    try:
        prompt = audio_to_text(audio, 'hin')

        if prompt:
            clean_prompt = extract_prompt(prompt, wake_words)
            if clean_prompt:
                # 🔹 Stop listening immediately
                if stop_listening:
                    print("Stopping background listener...")
                    stop_listening(wait_for_stop=False)
                    stop_listening = None
                    

                
                print("done")

    except Exception as e:
        print("Error in callback:", e)


def start_listening_landing():
    global stop_listening
    print("Adjusting for ambient noise, please wait...")
    with source as s:
        r.adjust_for_ambient_noise(s, duration=1)
        print(f"\nSay eva followed by your prompt.\n")

    # 🔹 Assign the background listener handle
    stop_listening = r.listen_in_background(source, callback_landing)

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping ASR...")
        if stop_listening:
            stop_listening(wait_for_stop=False)
            return True

        


import threading


listener_thread = None

@app.post("/start-listening")
def start_voice_assistant():
    global listener_thread
    if listener_thread and listener_thread.is_alive():
        return {"status": "already running"}

    listener_thread = threading.Thread(target=start_listening_landing, daemon=True)
    listener_thread.start()
    return {"status": "listening started"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def questions(user_input):
    clean_prompt = user_input.answer
    classify = llm_classify(clean_prompt).lower()
    combined_prompt = f"\nUser: {clean_prompt}\nAssistant:"
    if "yes" in classify:
        return rag_query(combined_prompt)
    else:
        return call_llm_norm(combined_prompt)

# @app.get("/wake_status")
# def get_wake_status():
#     global wake_detected
#     status = wake_detected
#     print(status)
#     if wake_detected:
#         wake_detected = False  # reset after frontend sees it
#     return {"wake": status}

@app.get("/get_live_text")
def get_live_text():
    with transcript_lock:
        text_copy = current_transcript
    return {"text": text_copy}

@app.post("/recieve_response")
def send_response(response: schemas.Questionresponse, db: Session = Depends(get_db)):
    answer = questions(response)
    db_response = models.Response(
        type="text",
        data=answer,
        map_data=None,
        llm_name="eva",
        confidence=18,
        timestamp=datetime.utcnow(),
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return {"data": db_response.data}

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db),lang:str=Form(...)):
    audio_bytes = await file.read()
    # audio_stream = io.BytesIO(audio_bytes)
    if lang.lower()=='english':
        code='eng'
    elif lang.lower()=='hindi':
        code='hin'
    elif lang.lower()=='tamil':
        code='tam'
    else:
        code='eng'
    print(code)
    text = audio_to_text(audio_bytes,code)

    print(text)
    class TempPrompt:
        def __init__(self, answer):
            self.answer = answer

    answer = questions(TempPrompt(text))
    speak(answer)
    return {"text": text, "data":answer}
