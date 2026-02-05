import os
import threading
import queue
import pyaudio
from murf import Murf, MurfRegion

# ---------------- CONFIG ---------------- #

SAMPLE_RATE = 24000
CHANNELS = 1
FORMAT = pyaudio.paInt16
BYTES_PER_SAMPLE = 2

FRAME_SIZE = 3840  # 80 ms stable Murf frame
QUEUE_MAX = 32     # jitter buffer depth

# ---------------- MURF CLIENT ---------------- #

client = Murf(
    api_key=os.getenv("MURF_API_KEY"),
    region=MurfRegion.IN   # use closest region
)

# ---------------- AUDIO PLAYER THREAD ---------------- #

def _audio_player(audio_q: queue.Queue):
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        output=True,
        frames_per_buffer=FRAME_SIZE
    )

    while True:
        frame = audio_q.get()
        if frame is None:
            break
        stream.write(frame)

    # Clean shutdown
    stream.stop_stream()
    stream.close()
    pa.terminate()

# ---------------- PUBLIC NON-BLOCKING FUNCTION ---------------- #

def play_streaming_audio(text: str):
    """
    Non-blocking streaming TTS playback.
    Safe to call from other code.
    """

    audio_q = queue.Queue(maxsize=QUEUE_MAX)
    pcm_buffer = bytearray()

    # Start playback thread
    player_thread = threading.Thread(
        target=_audio_player,
        args=(audio_q,),
        daemon=True
    )
    player_thread.start()

    def producer():
        audio_stream = client.text_to_speech.stream(
            text=text,
            voice_id="Anisha",
            model="FALCON",
            sample_rate=SAMPLE_RATE,
            format="PCM"
        )

        for chunk in audio_stream:
            if not chunk or len(chunk)!=3840:
                continue

            # Accumulate PCM
            pcm_buffer.extend(chunk)

            # Ensure int16 alignment
            remainder = len(pcm_buffer) % BYTES_PER_SAMPLE
            if remainder:
                del pcm_buffer[-remainder:]

            # Emit fixed-size frames
            while len(pcm_buffer) >= FRAME_SIZE:
                frame = bytes(pcm_buffer[:FRAME_SIZE])
                del pcm_buffer[:FRAME_SIZE]
                audio_q.put(frame)

        # Flush remainder with silence padding
        if pcm_buffer:
            pad = FRAME_SIZE - len(pcm_buffer)
            pcm_buffer.extend(b"\x00" * pad)
            audio_q.put(bytes(pcm_buffer))

        # Signal playback end
        audio_q.put(None)

    # Run producer in background
    threading.Thread(target=producer, daemon=True).start()

# ---------------- EXAMPLE USAGE ---------------- #

if __name__ == "__main__":
    play_streaming_audio(
        "A link to the audio file will be returned in the response. "
        "You can use this link to download the audio file and use it wherever you need it. "
        "The audio file will be available for download for 72 hours after generation."
    )

    print("TTS started — main thread continues running.")
