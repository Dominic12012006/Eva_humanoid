import os
import re
import time
import queue
import threading
from google.cloud import texttospeech_v1beta1 as texttospeech
from google.api_core.client_options import ClientOptions
from playsound import playsound

# ---- CONFIG ----
PROJECT_ID = "quiet-spirit-469107-t6"
TTS_LOCATION = "global"   # or use regional endpoint if needed
MODEL = "gemini-2.5-flash-tts"  # or gemini-2.5-pro-tts
VOICE = "Aoede"
LANGUAGE_CODE = "en-US"

# ---- INITIALIZE CLIENT ----
API_ENDPOINT = (
    f"{TTS_LOCATION}-texttospeech.googleapis.com"
    if TTS_LOCATION != "global"
    else "texttospeech.googleapis.com"
)

client = texttospeech.TextToSpeechClient(
    client_options=ClientOptions(api_endpoint=API_ENDPOINT)
)

# ---- DEFINE INPUT TEXT AND PROMPT ----
PROMPT = "You are a guide to SRM University. Talk in calm and measured tones with a fast pace"

# ---- DEFINE VOICE SELECTION ----
voice = texttospeech.VoiceSelectionParams(
    name=VOICE,
    language_code=LANGUAGE_CODE,
    model_name=MODEL
)

# ---- SYNTHESIZE SPEECH ----
def synthesize(TEXT,index):
    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=TEXT, prompt=PROMPT),
        voice=voice,
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
    )

    # ---- SAVE OUTPUT AUDIO ----
    output_file = f"gemini_output{index}.mp3"
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f"✅ Audio content written to {output_file}")

    # ---- PLAY SOUND (optional) ----
    return output_file

def split(text):
    sentences=re.split(r'(?<=[.!?])+',text.strip())
    return [s for s in sentences if s]

audio_queue=queue.Queue()
def playback():
    while True:
        filename=audio_queue.get()
        if filename is None:
            break
        print(f"playing {filename}")
        playsound(filename)
        audio_queue.task_done()

def tts_worker(sentences):
    for i,sentence in enumerate(sentences):
        print(f"generating sentences{i+1}/{len(sentences)}...")
        filename=synthesize(sentence,i)
        audio_queue.put(filename)
        time.sleep(0.3)
    audio_queue.put(None)
def speak(text):
    sentences=split(text)
    play_thread=threading.Thread(target=playback,daemon=True)
    play_thread.start()
    tts_worker(sentences)
    audio_queue.join()
    print("all played")
    