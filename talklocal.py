import re
import time
import io
import speech_recognition as sr
from faster_whisper import WhisperModel
from groq import Groq
import sounddevice
from llm3 import rag_query,call_llm_norm,llm_classify
from tts import speak
# ---------------- Groq API Setup ----------------
from dotenv import load_dotenv
load_dotenv()
import os
# ---------------- Groq API Setup ----------------
groq_client = Groq(api_key=os.getenv('groq_api'))
whisper_model = WhisperModel("small", device="cuda", compute_type="float16")

def audio_to_text(audio_data):
    """Convert recorded audio to text using Faster-Whisper (local)."""
    try:
        audio_bytes = io.BytesIO(audio_data.get_wav_data())
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_bytes.getvalue())
        segments, info = whisper_model.transcribe("temp_audio.wav", task="transcribe")
        text = " ".join([seg.text.strip() for seg in segments])
        print(f"[Whisper] Detected language: {info.language}")
        print(f"[Whisper] Transcribed text: {text}")

        return text,info.language

    except Exception as e:
        print("Error transcribing audio:", e)
        return None,None



def extract_prompt(transcribed_text, wake_word):
    """Extracts the prompt after the wake word (e.g., 'hello, tell me a joke')."""
    pattern = rf'\b{re.escape(wake_word)}[\s,.?!]*(.*)'
    match = re.search(pattern, transcribed_text, re.IGNORECASE)
    return match.group(1).strip() if match else None

# ---------------- ASR Setup ----------------
r = sr.Recognizer()
wake_word = "hello"

# Replace with your mic index (or leave empty for default)
mic_index = 24
source = sr.Microphone()#device_index=mic_index)

# ---------------- Callback for background listening ----------------
def callback(recognizer, audio):
    data = audio.get_wav_data()
    if len(data) < 1000:
        print("Warning: captured audio seems too short.")
        return

    try:
        prompt_text,lang = audio_to_text(audio)
        if prompt_text:
            clean_prompt = extract_prompt(prompt_text, wake_word)
            if clean_prompt:
                classify=llm_classify(clean_prompt).lower()
                print(classify)
                if "yes" in classify:
                    print()
                    print(f'ragUSER: {clean_prompt}')
                    res=rag_query(clean_prompt)
                else:
                    print(f'normUSER: {clean_prompt}')
                    res=call_llm_norm(clean_prompt)
                print(res)
                speak(res,lang)

    except Exception as e:
        print("Error in callback:", e)

# ---------------- Main listening loop ----------------
def start_listening():
    print("Adjusting for ambient noise, please wait...")
    with source as s:
        r.adjust_for_ambient_noise(s, duration=1)
        print(f"\nSay '{wake_word}' followed by your prompt.\n")

        # Test blocking listen first
        print("Testing mic with one recording...")
        audio = r.listen(s, timeout=5, phrase_time_limit=5)
        print(f"Captured {len(audio.get_wav_data())} bytes of audio!")

    # Start background listening
    stop_listening = r.listen_in_background(source, callback)

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping ASR...")
        stop_listening(wait_for_stop=False)

# ---------------- Run ----------------
if __name__ == "__main__":
    start_listening()
