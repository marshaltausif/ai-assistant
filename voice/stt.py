# voice/stt.py
import whisper
import sounddevice as sd
import numpy as np
import tempfile
import wave
import os

class SpeechToText:
    def __init__(self, model_size="base"):
        """Initialize Whisper model"""
        self.model = whisper.load_model(model_size)
        self.sample_rate = 16000
        self.channels = 1
    
    def record_audio(self, duration=5):
        """Record audio for specified duration"""
        print(f"🎤 Recording for {duration} seconds...")
        
        # Record audio
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.float32
        )
        sd.wait()  # Wait for recording to complete
        
        return audio.flatten()
    
    def save_temp_wav(self, audio_data):
        """Save audio data to temporary WAV file"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            filename = f.name
        
        # Save as WAV
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            
            # Convert float32 to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())
        
        return filename
    
    def transcribe(self, audio_file):
        """Transcribe audio file to text"""
        try:
            result = self.model.transcribe(audio_file, fp16=False)
            return result["text"].strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def listen(self, duration=5):
        """Complete listen and transcribe process"""
        try:
            # Record audio
            audio_data = self.record_audio(duration)
            
            # Save to temp file
            temp_file = self.save_temp_wav(audio_data)
            
            # Transcribe
            text = self.transcribe(temp_file)
            
            # Cleanup
            os.unlink(temp_file)
            
            return text
            
        except Exception as e:
            print(f"Listening error: {e}")
            return ""

# Quick function for backward compatibility
def listen_and_transcribe(duration=5):
    """Quick function for simple use"""
    stt = SpeechToText()
    return stt.listen(duration)