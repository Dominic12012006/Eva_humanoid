import threading
import io
import json
import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import chromadb
from . import models, schemas
from .database import engine, SessionLocal
from dotenv import load_dotenv
import os
from elevenlabs.client import ElevenLabs
import io
load_dotenv()

elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

def audio_to_text1(audio_path):
    try:
        with open(audio_path, "rb") as f:
            transcription = elevenlabs.speech_to_text.convert(
                file=f,
                model_id="scribe_v1",
                tag_audio_events=False,
                diarize=False
            )
        return transcription.text
    except Exception as e:
        print("Error transcribing audio:", e)
        return None


def audio_to_text(audio_data):
    try:
        # Convert recorded audio to BytesIO
        audio_file = io.BytesIO(audio_data.get_wav_data())

        # Call ElevenLabs speech-to-text
        transcription = elevenlabs.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",      # ElevenLabs transcription model
            tag_audio_events=False,    # optional: True if you want events
            # language_code="eng",
            diarize=False              # optional: True if multiple speakers
        )

        return transcription.text
    except Exception as e:
        print("Error transcribing audio:", e)
        return None

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
'''
def background_listener():
    global current_transcript, wake_detected
    print("🎧 Wake listener active.")
    while True:
        try:
            audio_stream = start_listening()  # listen continuously
            if audio_stream:
                text = audio_to_text(audio_stream).lower()
                if text:
                    with transcript_lock:
                        current_transcript = text
                    print(f"🗣️ Heard: {text}")

                    # detect wake word
                    if "eva" in text:
                        wake_detected = True
                        print("👂 Wake word detected: EVA")
        except Exception as e:
            print(f"🎙️ Listener error: {e}")
'''
@app.on_event("startup")
def start_voice_assistant():
    listener_thread = threading.Thread(target=start_listening, daemon=True)
    listener_thread.start()

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

@app.get("/wake_status")
def get_wake_status():
    global wake_detected
    status = wake_detected
    if wake_detected:
        wake_detected = False  # reset after frontend sees it
    return {"wake": status}

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
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    audio_bytes = await file.read()
    audio_stream = io.BytesIO(audio_bytes)
    text = audio_to_text(audio_stream)

    class TempPrompt:
        def __init__(self, answer):
            self.answer = answer

    answer = questions(TempPrompt(text))
    db_response = models.Response(
        type="audio",
        data=answer,
        map_data=None,
        llm_name="eva",
        confidence=18,
        timestamp=datetime.utcnow(),
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return {"text": text, "data": db_response.data}
