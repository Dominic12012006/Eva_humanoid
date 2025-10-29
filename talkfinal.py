import re
import time
import io
import speech_recognition as sr
from groq import Groq
import sounddevice
from llm3 import rag_query, call_llm_norm, llm_classify,summarize
from tts import speak

# ---------------- Groq API Setup ----------------
from dotenv import load_dotenv
load_dotenv()
import os
# ---------------- Groq API Setup ----------------
groq_client = Groq(api_key=os.getenv('groq_api'))
# ---------------- Conversation History ----------------
conversation_history = []  # list of dicts like [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]

def add_to_history(role, content):
    """Add a new message to conversation history."""
    conversation_history.append({"role": role, "content": content})
    # Limit history length to prevent context overload
    if len(conversation_history) > 10:
        conversation_history.pop(0)

def get_context_text():
    """Convert history to a text-based context for passing into LLM."""
    context = ""
    for msg in conversation_history:
        prefix = "User:" if msg["role"] == "user" else "Assistant:"
        context += f"{prefix} {msg['content']}\n"
    return context.strip()

# ---------------- Audio Processing ----------------
def audio_to_text(audio_data):
    """Convert recorded audio to text using Groq's Whisper model."""
    try:
        audio_file = io.BytesIO(audio_data.get_wav_data())
        translation = groq_client.audio.translations.create(
            file=("audio.wav", audio_file.getvalue()),
            model="whisper-large-v3",
        )
        return translation.text
    except Exception as e:
        print("Error transcribing audio:", e)
        return None

def extract_prompt(transcribed_text, wake_word):
    """Extracts the prompt after the wake word (e.g., 'hello, tell me a joke')."""
    pattern = rf'\b{re.escape(wake_word)}[\s,.?!]*(.*)'
    match = re.search(pattern, transcribed_text, re.IGNORECASE)
    return match.group(1).strip() if match else None

# ---------------- ASR Setup ----------------
r = sr.Recognizer()
wake_word = "hello"
mic_index = 24
source = sr.Microphone(device_index=mic_index)

# ---------------- Callback ----------------
def callback(recognizer, audio):
    data = audio.get_wav_data()
    if len(data) < 1000:
        print("Warning: captured audio seems too short.")
        return

    try:
        prompt_text = audio_to_text(audio)
        if prompt_text:
            clean_prompt = extract_prompt(prompt_text, wake_word)
            if clean_prompt:
                classify = llm_classify(clean_prompt).lower()
                print(f"Classification: {classify}")

                # Add user message to history
                add_to_history("user", clean_prompt)

                context = get_context_text()
                combined_prompt = f"{context}\nUser: {clean_prompt}\nAssistant:"

                if "yes" in classify:
                    print(f"\nRAG USER: {clean_prompt}")
                    res = rag_query(combined_prompt)
                else:
                    print(f"\nNORM USER: {clean_prompt}")
                    res = call_llm_norm(combined_prompt)

                # Add assistant response to history
                add_to_history("assistant", res)
                res_sum=summarize(res)
                print(f"\nAssistant: {res_sum}\n")
                speak(res)

    except Exception as e:
        print("Error in callback:", e)

# ---------------- Main Loop ----------------
def start_listening():
    print("Adjusting for ambient noise, please wait...")
    with source as s:
        r.adjust_for_ambient_noise(s, duration=1)
        print(f"\nSay '{wake_word}' followed by your prompt.\n")

        # Test mic once
        print("Testing mic with one recording...")
        audio = r.listen(s, timeout=5, phrase_time_limit=5)
        print(f"Captured {len(audio.get_wav_data())} bytes of audio!")

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

# ---------------- Run ----------------
if __name__ == "__main__":
    start_listening()
