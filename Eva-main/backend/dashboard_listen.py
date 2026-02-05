from dotenv import load_dotenv
import re
from elevenlabs.client import ElevenLabs
import io
from . import state
import speech_recognition as sr
from .voice import audio_to_text,audio_to_text_button
from .app import rag_query,call_llm_norm,llm_classify,checklang,getimage
from . import models
from .database import engine
from .database import SessionLocal
# from tts import speak
from .ttsmurf import play_streaming_audio
import time
import sounddevice
import os
load_dotenv()
models.Base.metadata.create_all(bind=engine)
elevenlabs = ElevenLabs(
    api_key=os.getenv("elevenapi"),
)
# ques='Hello whats the hellu'
# ans='Hello the name is eva'
question=''
answer=' '
conversation_history = []  
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

db=SessionLocal()
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
wake_words = ["assistant"]#["eva","इवा","ईवा","ഇവ","இவா"]
mic_index = 25
source = sr.Microphone()#device_index=mic_index)

def callback(recognizer, audio):
    global current_transcript, wake_detected
    data = audio.get_wav_data()
    if len(data) < 1000:
        print("Warning: captured audio seems too short.")
        return

    try:
        prompt=audio_to_text(audio,'eng')

        if prompt:
            clean_prompt=extract_prompt(prompt,wake_words)
            if clean_prompt:
                global question
                print('bc')
                question=clean_prompt
                # with transcript_lock:
                #         current_transcript = clean_prompt
                wake_detected = True
                classify = llm_classify(clean_prompt).lower()
                print(f"Classification: {classify}")

                # Add user message to history
                add_to_history("user", clean_prompt)

                context = get_context_text()
                with open(r"/home/eva/Desktop/dominic/Eva-main/backend/language.txt", "r") as f:
                    language = f.read()
                
                combined_prompt = f"{context}\nUser: {clean_prompt} [Do not acknowledge but generate response in {language} language]\nAssistant:"
                ####print clean_promnpt
                print(combined_prompt)
                ######stop animation
                if "yes" in classify:
                    print(f"\nRAG USER: {clean_prompt}")
                    res = rag_query(combined_prompt)
                    global answer
                    answer=res
                    image=True
                else:
                    print(f"\nNORM USER: {clean_prompt}")
                    res = call_llm_norm(combined_prompt)
                    answer=res
                    image=False
                ######print res
                # Add assistant response to history
                add_to_history("assistant", res)
                # res_sum=summarize(res)
                #dddd chatbot output
                print(f"\nAssistant: {res}\n")
                ######speaking animation
                # speak(res)#####global question
                play_streaming_audio(res)
                #####stop speak ani
                print("done")
                record_question(question)
                record_answer(answer)

    except Exception as e:
        print("Error in callback:", e)
def record_question(a):
    new_question=models.Question(question=a)
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    print("Question has been stored in the database")
def record_answer(c):
    new_answer=models.Answer(answer=c)
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)
    print('Answer has been stored in the database')
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

# record_question(ques)
# record_answer(ans)
start_listening()

print(question)
print(answer)
          