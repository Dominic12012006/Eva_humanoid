import threading
import io
import json
import logging
import time
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import chromadb
from . import models, schemas
from .database import engine, SessionLocal

from .app import rag_query, call_llm_norm, llm_classify

# from ...open import start_listening, global_state, state_lock 
class MicStatus(BaseModel):
    mic_status: str
    last_prompt: str | None
    last_response: str | None


models.Base.metadata.create_all(bind=engine)
app = FastAPI()
logger = logging.getLogger("uvicorn.error")

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Globals ----
current_transcript = ""
transcript_lock = threading.Lock()
recognizer = sr.Recognizer()
mic_index = 25  # adjust for your Jetson mic index
source = sr.Microphone(device_index=mic_index)


# 🎧 Background listener thread
def background_listener():
    global current_transcript
    print("🎤 Starting continuous microphone listener...")

    with source as s:
        recognizer.adjust_for_ambient_noise(s, duration=1)
        print("✅ Mic ready. Listening in background...")

    while True:
        try:
            with source as s:
                # Capture short 3–5 sec clips continuously
                audio = recognizer.listen(s, phrase_time_limit=4)
                text = audio_to_text(audio)
                if text:
                    with transcript_lock:
                        current_transcript = text
                    print(f"🗣️ Heard: {text}")
        except Exception as e:
            print(f"🎙️ Listener error: {e}")
        time.sleep(0.3)


@app.on_event("startup")
def start_background_listener():
    listener_thread = threading.Thread(target=background_listener, daemon=True)
    listener_thread.start()
    print("🎧 Background listener started successfully.")


# ---- DB Dependency ----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''
@app.get("/get_mic_status", response_model=MicStatus)
def get_mic_status():
    """Frontend polls this endpoint to check the listener's current state."""
    with state_lock:
        current_state = global_state.copy()
        
    return MicStatus(
        mic_status=current_state.get("mic_status", "sleeping"),
        last_prompt=current_state.get("last_prompt"),
        last_response=current_state.get("last_response")
    )
'''

# @app.post()
# def listen():
#     input=
    

# ---- Question/Response Flow ----
def questions(user_input):
    clean_prompt = user_input.answer
    print(f"Text Input Prompt: {clean_prompt}")
    classify = llm_classify(clean_prompt).lower()
    combined_prompt = f"\nUser: {clean_prompt}\nAssistant:"
    if "yes" in classify:
        res = rag_query(combined_prompt)
    else:
        res = call_llm_norm(combined_prompt)
    return res


# ---- Endpoints ----
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
    return {"data": db_response.data, "map_data": db_response.map_data}


@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    audio_bytes = await file.read()
    audio_stream = io.BytesIO(audio_bytes)

    print("🎧 Converting uploaded audio to text...")
    text = audio_to_text(audio_stream)
    print(f"🗣️ Transcribed Text: {text}")

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


# 🆕 Live Transcript (for frontend polling)
@app.get("/get_live_text")
def get_live_text():
    with transcript_lock:
        text_copy = current_transcript
    return {"text": text_copy}


# ---- Utility Endpoints ----
@app.get("/get_all_responses", response_model=list[schemas.ResponseOut])
def get_all_responses(limit: int = 100, db: Session = Depends(get_db)):
    responses = db.query(models.Response).order_by(models.Response.id.desc()).limit(limit).all()
    for r in responses:
        try:
            r.data = json.loads(r.data)
        except (TypeError, json.JSONDecodeError):
            pass
    return responses


@app.get("/get_response/{response_id}", response_model=schemas.ResponseOut)
def get_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(models.Response).filter(models.Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    try:
        response.data = json.loads(response.data)
    except (TypeError, json.JSONDecodeError):
        pass
    return response


@app.delete("/clear_responses")
def clear_responses(db: Session = Depends(get_db)):
    db.query(models.Response).delete()
    db.commit()
    return {"status": "cleared"}
