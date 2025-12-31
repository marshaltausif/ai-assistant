# voice/tts.py
import asyncio
import edge_tts
import tempfile
import os
import playsound

VOICE = "en-US-AriaNeural"  # or "en-US-GuyNeural", "en-IN-PrabhatNeural"

async def synthesize_speech(text: str, voice: str = VOICE) -> str:
    """Convert text to speech and save as temp file"""
    if not text.strip():
        return None
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        temp_path = f.name
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(temp_path)
        return temp_path
    except Exception as e:
        print(f"TTS Error: {e}")
        os.unlink(temp_path)
        return None

def speak(text: str, voice: str = VOICE):
    """Synchronous wrapper for TTS"""
    if not text.strip():
        return
    
    try:
        # Run async function in sync context
        temp_file = asyncio.run(synthesize_speech(text, voice))
        
        if temp_file and os.path.exists(temp_file):
            playsound.playsound(temp_file)
            os.unlink(temp_file)  # Clean up
            
    except Exception as e:
        print(f"Speech Error: {e}")
        # Fallback to pyttsx3 if edge_tts fails
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except:
            print("All TTS methods failed")

# Alternative async version
async def speak_async(text: str, voice: str = VOICE):
    """Async version for use in async contexts"""
    if not text.strip():
        return
    
    temp_file = await synthesize_speech(text, voice)
    if temp_file and os.path.exists(temp_file):
        playsound.playsound(temp_file)
        os.unlink(temp_file)