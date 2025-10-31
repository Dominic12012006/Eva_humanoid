import threading
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import json
import logging
from pydantic import BaseModel
from .app import chromadb
from . import models, schemas
from .database import engine, SessionLocal

from .app import rag_query, call_llm_norm, llm_classify

from ...open import start_listening, global_state, state_lock 
class MicStatus(BaseModel):
    mic_status: str
    last_prompt: str | None
    last_response: str | None


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
    """Wrapper to run the blocking start_listening in a separate thread."""
    try:

        start_listening()
    except Exception as e:
        print(f"🎙️ Voice Listener Thread died with an error: {e}")

@app.on_event("startup")
def start_voice_assistant():
    """Called once when the application starts up."""

    listener_thread = threading.Thread(target=run_listener_in_background, daemon=True)
    listener_thread.start()
    print("🎙️ Voice Listener Thread started successfully in the background.")



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



def questions(user_input):
    clean_prompt=user_input.answer
    print(f"Text Input Prompt: {clean_prompt}")
    classify = llm_classify(clean_prompt).lower()
    combined_prompt = f"\nUser: {clean_prompt}\nAssistant:"

    if "yes" in classify:
        res = rag_query(combined_prompt)
    else:
        res = call_llm_norm(combined_prompt)
    return res


@app.post("/recieve_response")
def send_response(response: schemas.Questionresponse, db: Session = Depends(get_db)):
    """Receives explicit text input from the UI and saves the LLM response."""
    answer=questions(response)
    map_data1=None

    db_response = models.Response(
            type='text',
            data=answer,
            map_data=map_data1,
            llm_name='eva',
            confidence=18,
            timestamp=datetime.utcnow(),
        )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return {"data":db_response.data,
            "map_data":db_response.map_data
    }



@app.get("/get_all_responses", response_model=list[schemas.ResponseOut])
def get_all_responses(limit: int = 100, db: Session = Depends(get_db)):
    responses = (
        db.query(models.Response)
        .order_by(models.Response.id.desc())
        .limit(limit)
        .all()
    )
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

