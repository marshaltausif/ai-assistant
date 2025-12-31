import asyncio
import edge_tts
import tempfile
import os
import playsound

VOICE = "en-US-AriaNeural"

async def _speak_async(text: str):
    if not text:
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        temp_path = f.name

    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(temp_path)

    playsound.playsound(temp_path)
    os.remove(temp_path)


def speak(text: str):
    asyncio.run(_speak_async(text))
