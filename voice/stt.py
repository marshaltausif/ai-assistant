import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import os

model = whisper.load_model("base")


def listen_and_transcribe(duration=6):
    fs = 16000
    print("🎙️ Listening... Speak now")

    recording = sd.rec(
        int(duration * fs),
        samplerate=fs,
        channels=1,
        dtype="int16"
    )
    sd.wait()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav.write(f.name, fs, recording)
        path = f.name

    try:
        result = model.transcribe(path)
        text = result["text"].strip()
    finally:
        os.remove(path)

    print(f"🗣️ You said: {text}")
    return text
