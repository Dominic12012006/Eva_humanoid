from faster_whisper import WhisperModel

# ---------------- Config ----------------
# Use 'small' for quick CPU/GPU testing
model_name = "small"  
device = "cpu"  # or "cuda" if GPU is ready
compute_type = "int8"  # smaller footprint on CPU

# ---------------- Initialize model ----------------
whisper_model = WhisperModel(model_name, device=device, compute_type=compute_type)

# ---------------- Test transcription ----------------
audio_path = "output.wav"  # Replace with your WAV file

segments, info = whisper_model.transcribe(audio_path, task="transcribe")

print(f"Detected language: {info.language}")
print("Transcription:")
for segment in segments:
    print(segment.text.strip())
