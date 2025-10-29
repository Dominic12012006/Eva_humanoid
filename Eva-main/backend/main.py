from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import json
import logging
from . import models, schemas
from .database import engine, SessionLocal
from .app import rag_query, call_llm_norm, llm_classify


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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def questions(user_input):
    clean_prompt=user_input.answer
    print(clean_prompt)
    classify = llm_classify(clean_prompt).lower()
    combined_prompt = f"\nUser: {clean_prompt}\nAssistant:"

    if "yes" in classify:
        res = rag_query(combined_prompt)
    else:
        res = call_llm_norm(combined_prompt)
    return res

# app.get('/show_response')
# def response():
#     return{
#         'response':res
#     }
@app.post('/send_question')
def send_question(response:schemas.Questionresponse):
    return questions(response)
@app.post("/recieve_response")
def send_response(response: schemas.Questionresponse, db: Session = Depends(get_db)):
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
        r.data = json.loads(r.data)
    return responses


@app.get("/get_response/{response_id}", response_model=schemas.ResponseOut)
def get_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(models.Response).filter(models.Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    response.data = json.loads(response.data)
    return response


@app.delete("/clear_responses")
def clear_responses(db: Session = Depends(get_db)):
    db.query(models.Response).delete()
    db.commit()
    return {"status": "cleared"}

