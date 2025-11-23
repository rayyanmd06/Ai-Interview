import os
import base64
from io import BytesIO
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
AudioSegment.converter = r"G:\ffmpeg\bin\ffmpeg.exe"   
AudioSegment.ffprobe   = r"G:\ffmpeg\bin\ffprobe.exe"

TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

def text_to_speech(text: str) -> str:
    if not text:
        return None
    try:
        tts = gTTS(text=text, lang="en")
        buf = BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        audio_b64 = base64.b64encode(buf.read()).decode("utf-8")
        return audio_b64
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def convert_webm_to_wav(webm_path: str) -> str:
    """Convert WebM recording from browser to WAV for SpeechRecognition."""
    wav_path = webm_path.replace(".webm", ".wav")
    try:
        audio = AudioSegment.from_file(webm_path, format="webm")
        audio.export(wav_path, format="wav")
        return wav_path
    except Exception as e:
        print(f"Conversion error: {e}")
        return None

def speech_to_text_from_wav(wav_path: str) -> str:
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand the audio."
    except sr.RequestError:
        return "Speech recognition API unavailable."
    except Exception as e:
        print(f"STT Error: {e}")
        return f"Error processing audio: {e}"
