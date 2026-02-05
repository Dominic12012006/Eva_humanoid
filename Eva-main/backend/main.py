'''for kiosk mode
chromium-browser \
  --kiosk \
  --no-sandbox \
  --disable-gpu \
  --disable-software-rasterizer \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-restore-session-state \
  --incognito \
  http://localhost:3000

'''
import threading
import io
import json
import logging
from . import token2
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile,Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from . import state
import chromadb
from . import models, schemas
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from .database import engine, SessionLocal
from .background import callback
from .app import rag_query,call_llm_norm,llm_classify,checklang,getimage
from .voice import audio_to_text,audio_to_text_button
import speech_recognition as sr
import time
from .tts import speak
from .ttsmurf import play_streaming_audio
from dotenv import load_dotenv
import re
from elevenlabs.client import ElevenLabs
import os
from .battery import voltage_return
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
logger = logging.getLogger("uvicorn.error")
image=False
#The language global variable
language_gobal=''
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
micAllowed=False
current_transcript = ""
wake_detected = False
transcript_lock = threading.Lock()
load_dotenv()

elevenlabs = ElevenLabs(
    api_key="sk_e5ae4363b36e0fb9509a934a6393487b7ad7b564dea2608b",
)
#USE FUZZY LOGIC
#SET TIME LIMIT ONCE WAKE WORD IS SAID INSTEAD OF REPEATING KEYWORD
#CHANGE WAKE WORD
# @app.post('/show_questions')
# def show_questions(db:Session=Depends(),):

    
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
mic_index = 25
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
                global image
                if "yes" in classify:
                    print(f"\nRAG USER: {clean_prompt}")
                    res = rag_query(combined_prompt)
                    
                    image=True
                else:
                    print(f"\nNORM USER: {clean_prompt}")
                    res = call_llm_norm(combined_prompt)
                    image=False
                ######print res
                # Add assistant response to history
                add_to_history("assistant", res)
                # res_sum=summarize(res)
                #dddd chatbot output
                print(f"\nAssistant: {res}\n")
                ######speaking animation
                # speak(res)#####
                play_streaming_audio(res)
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

stop_listening = None
listener_thread = None
listening_active = False


def callback_landing(recognizer, audio):
    global wake_detected, stop_listening, listening_active

    data = audio.get_wav_data()
    if len(data) < 100:
        print("Warning: captured audio seems too short.")
        return

    try:
        prompt = audio_to_text(audio, 'eng')

        if 'eva' in prompt.lower():
            wake_detected = True
            print("Wake word detected!")

            if stop_listening:
                print("Stopping background listener...")
                stop_listening(wait_for_stop=False)
                stop_listening = None

            # 🔹 Stop the while-loop in start_listening_landing()
            listening_active = False
            print("done")

    except Exception as e:
        print("Error in callback:", e)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def start_listening_landing():
    global stop_listening, listening_active
    import speech_recognition as sr

    r = sr.Recognizer()
    source = sr.Microphone()

    print("Adjusting for ambient noise...")
    with source as s:
        r.adjust_for_ambient_noise(s, duration=1)
        print("\nSay 'eva' followed by your prompt.\n")

    listening_active = True
    stop_listening = r.listen_in_background(source, callback_landing)

    try:
        while listening_active:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping ASR (keyboard)...")
    finally:
        if stop_listening:
            stop_listening(wait_for_stop=False)
            stop_listening = None
        listening_active = False


# @app.get("/start-listening")
def start_voice_assistant():
    global listener_thread, wake_detected
    if listener_thread and listener_thread.is_alive():
        return {"status": "already_running"}

    wake_detected = False
    listener_thread = threading.Thread(target=start_listening_landing, daemon=True)
    listener_thread.start()

    return {"status": "started"}
start_voice_assistant()

@app.get("/")
def on_startup():
    global wake_detected
    wake_detected=False
    print("sdfsdv")
    start_voice_assistant()
# @app.post('/dashboard_listening')
# async def dashboard_listening(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     lang: str = Form(...)
# ):
#     audio_bytes = await file.read()

#     if lang.lower() == 'english':
#         code = 'eng'
#     elif lang.lower() == 'hindi':
#         code = 'hin'
#     elif lang.lower() == 'tamil':
#         code = 'tam'
#     else:
#         code = 'eng'

#     text = audio_to_text_button(audio_bytes, code)
#     if not text or text.strip() == "":
#         return {"status": "false"}

#     wake_words = ["eva", "hey eva", "hello eva"]
#     status = extract_prompt(text, wake_words)

#     if status is not None:
#         return {"text": text, "status": "true"}
#     else:
#         return {"status": "false"}
@app.on_event("startup")
def start_ros():
    ros_thread = threading.Thread(target=ros_spin, daemon=True)
    ros_thread.start()
    logger.info("ROS battery node started")

@app.get("/status")
def get_status():    
    global wake_detected
    wake_detected
    return {
        "listening": listener_thread.is_alive() if listener_thread else False,
        "wake_detected": wake_detected
    }

@app.post('/talking')
async def eva_talking(file: UploadFile = File(...), db: Session = Depends(get_db),lang:str=Form(...)):
    audio_bytes = await file.read()
    # audio_stream = io.BytesIO(audio_bytes)
    global language_gobal
    language_gobal=lang.lower()
    if lang.lower()=='english':
        code='eng'
    elif lang.lower()=='hindi':
        code='hin'
    elif lang.lower()=='tamil':
        code='tam'
    else:
        code='eng'
    print(code)
    text = audio_to_text_button(audio_bytes,code)
    print(text)
    answer = questions(text)
    
    if image:
        imgurl=getimage(text)
        db_image=models.Images(image=imgurl)
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
    else:
        imgurl=None
    print(imgurl)
    # speak(answer)
    play_streaming_audio(answer)
    global micAllowed
    micAllowed=True
    return {"text": text, "data":answer, "image":imgurl,'micStatus':micAllowed}

def questions(user_input,language):
    clean_prompt = user_input
    classify = llm_classify(clean_prompt).lower()
    combined_prompt = f"\nUser: {clean_prompt} Do not acknowledge but generate response in {language} language\nAssistant:"
    global image
    print(combined_prompt)

    print(language_gobal)
    if "yes" in classify:
        image=True
        return rag_query(combined_prompt)
    else:
        image=False
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
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
@app.post('/admin')
def admin_thing(creds:schemas.Admin,db:Session=Depends(get_db)):
    hashedPassowrds=""
    hashedPassowrds=pwd_context.hash(creds.password)
    db_add=models.User(
        email=creds.email,
        password=hashedPassowrds
    )
    db.add(db_add)
    db.commit()
    db.refresh(db_add)
    access_token=token2.create_access_token(
        data={'sub':db_add.email}
    )
    return{"email":creds.email,"passowrd":creds.password,"access token":access_token}

@app.post('/authenticate')
def authentication(creds:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user_logins=db.query(models.User).filter(models.User.email==creds.username).first()
    if not user_logins:
        raise HTTPException(status_code=404,detail="Email is wrong ")
    if not pwd_context.verify(creds.password,user_logins.password):
        raise HTTPException(status_code=404,detail="Password entered is wrong")
    access_token=token2.create_access_token(data={'sub':creds.username})
    return{'access_token':access_token,'token_type':'bearer'}

@app.post("/recieve_response")
def send_response(response: schemas.Questionresponse, db: Session = Depends(get_db)):
    q=response.answer
    a = questions(response.answer,response.lang)
    if image:
        imgurl=getimage(response.answer)
        db_image=models.Images(image=imgurl)
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
    else:
        imgurl=None
        # db_image=models.Images(image=imgurl)
        # db.add(db_image)
        # db.commit()
        # db.refresh(db_image)
    db_question=models.Question(question=q)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    global language_gobal
    language_gobal=response.lang
    with open(r"/home/eva/Desktop/dominic/Eva-main/backend/language.txt", "w") as f:
        f.write(language_gobal)

    state.language=response.lang
    print(language_gobal)
    db_answer=models.Answer(answer=a)
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    print(a,imgurl)
    db_response = models.Response(
        type="text",
        data=a,
        map_data=imgurl,
        llm_name="eva",
        confidence=18,
        timestamp=datetime.utcnow(),
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    # speak(answer)
    play_streaming_audio(a)
    return {"data": db_response.data,"image":db_response.map_data}

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db),lang:str=Form(...)):
    audio_bytes = await file.read()
    global micAllowed
    # if not micAllowed:
    # audio_stream = io.BytesIO(audio_bytes)
    
    # print(language_gobal)
    if lang.lower()=='english':
        state.language='eng'
        code='eng'
    elif lang.lower()=='hindi':
        state.language='hin'
        code='hin'
    elif lang.lower()=='tamil':
        state.language='tam'
        code='tam'
    else:
        state.language='eng'
        code='eng'
    global language_gobal
    language_gobal=code
    with open(r"/home/eva/Desktop/dominic/Eva-main/backend/language.txt", "w") as f:
        f.write(language_gobal)
    print(language_gobal)
    text = audio_to_text_button(audio_bytes,code)
    new_quesion_audio=models.Question(question=text)
    db.add(new_quesion_audio)
    db.commit()
    db.refresh(new_quesion_audio)

    print(text)

    answers = questions(text,lang)
    new_answer_audio=models.Answer(answer=answers)
    db.add(new_answer_audio)
    db.commit()
    db.refresh(new_answer_audio)
    if image:
        imgurl=getimage(text)
        db_image=models.Images(image=imgurl)
        db.add(db_image)
        db.commit()
        db.refresh(db_image) 
    else:
        imgurl=None
        # db_image=models.Images(image=imgurl)
        # db.add(db_image)
        # db.commit()
        # db.refresh(db_image)
    print(imgurl)
    # speak(answer)
    play_streaming_audio(answers)
    return {"text": text, "data":answers, "image":imgurl}


class WelcomeRequest(BaseModel):
    text: str

@app.post('/welcome_text')
def welcome(req: WelcomeRequest):
    # speak(req.text)
    play_streaming_audio(req.text)
    return {"message": f"Received text: {req.text}"}

@app.delete('/delete_questions')
def del_questions(db:Session=Depends(get_db)):
    db.query(models.Question).delete()
    db.commit()
    return{"message":"All questions deleted"}

@app.delete('/delete_answers')
def del_answers(db:Session=Depends(get_db)):
    db.query(models.Answer).delete()
    db.commit()
    return{"message":"All answers deleted"}
from typing import List
@app.get('/show_questions', response_model=List[schemas.Show_questions])
def show_questions(sb: Session = Depends(get_db)):
    return sb.query(models.Question).order_by(models.Question.id.desc()).all()

@app.get('/show_answer', response_model=List[schemas.Show_answer])
def show_answer(sb: Session = Depends(get_db)):
    return sb.query(models.Answer).order_by(models.Answer.id.desc()).all()

@app.delete('/delete_images')
def del_answers(db:Session=Depends(get_db)):
    db.query(models.Images).delete()
    db.commit()
    return{"message":"All images deleted"}

@app.get('/show_images', response_model=List[schemas.Show_image])
def show_answer(sb: Session = Depends(get_db)):
    return sb.query(models.Images).order_by(models.Images.id.desc()).all()
import threading
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState




battery_voltage = None


class BatteryNode(Node):
    def __init__(self):
        super().__init__('battery_node')

        self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            10
        )

    def battery_callback(self, msg: BatteryState):
        global battery_voltage
        battery_voltage = msg.voltage
        self.get_logger().info(f"Battery voltage: {battery_voltage:.2f} V")


def ros_spin():
    rclpy.init()
    node = BatteryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()





@app.get("/battery")
def get_battery():
    max_battery_voltage=27.17
    min_battery_voltage=23.17
    range=max_battery_voltage-min_battery_voltage
    pos=battery_voltage-min_battery_voltage
    battery_percentage=(pos/range)*100
    if battery_percentage <30:
        return {"status": "low", "percentage":battery_percentage}
    return {
        "status": "ok",
        "percentage":battery_percentage
    }

# if __name__ == "__main__":
#     ros_thread = threading.Thread(target=ros_spin, daemon=True)
#     ros_thread.start()

# @app.post('/battery_level')
# def battery_level():
#     battery=voltage_return()
#     battery_max=27.17
#     battery_percentage=(battery/battery_max)*100
#     if battery_percentage<30.0:
#         return {
#             'battery':battery_percentage,
#             'status':'low'
#         }
#     else :
#         return {
#             'battery':battery_percentage,
#             'status':'okay'
#         }
    

