import threading
import io
import json
import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .app import chromadb, rag_query, call_llm_norm, llm_classify
from . import models, schemas
from .database import engine, SessionLocal
from ...open import start_listening,audio_to_text
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

def run_listener_in_background():
    try:
        start_listening()
    except Exception as e:
        print(f"🎙️ Voice Listener Thread died with an error: {e}")

@app.on_event("startup")
def start_voice_assistant():
    listener_thread = threading.Thread(target=run_listener_in_background, daemon=True)
    listener_thread.start()
    print("🎙️ Voice Listener Thread started successfully.")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def questions(user_input):
    clean_prompt = user_input.answer
    print(f"🧠 Text Input Prompt: {clean_prompt}")
    classify = llm_classify(clean_prompt).lower()
    combined_prompt = f"\nUser: {clean_prompt}\nAssistant:"
    if "yes" in classify:
        res = rag_query(combined_prompt)
    else:
        res = call_llm_norm(combined_prompt)
    return res
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

    print(" Converting audio to text...")
    text = audio_to_text(audio_stream) 
    print(f"🗣️ Transcribed Text: {text}")

    class TempPrompt:
        def __init__(self, answer): self.answer = answer

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
