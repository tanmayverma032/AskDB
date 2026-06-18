import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe(self, audio_bytes: bytes, format: str = "wav") -> str:
        """
        Transcribes audio bytes to text using speech_recognition.
        """
        try:
            # Convert bytes to AudioData
            # speech_recognition's AudioFile requires a file-like object
            audio_file = BytesIO(audio_bytes)
            
            with sr.AudioFile(audio_file) as source:
                # Listen to the audio data
                audio_data = self.recognizer.record(source)
                
                # Recognize speech using Google Web Speech API
                # In a production environment, you might want to use a paid API like Google Cloud Speech-to-Text
                text = self.recognizer.recognize_google(audio_data)
                return text
                
        except sr.UnknownValueError:
            logger.warning("Speech Recognition could not understand the audio")
            raise ValueError("Could not understand the audio. Please try speaking clearly.")
        except sr.RequestError as e:
            logger.error(f"Could not request results from Speech Recognition service; {e}")
            raise RuntimeError(f"Speech recognition service error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in audio transcription: {str(e)}")
            raise RuntimeError(f"Error processing audio: {str(e)}")

    def synthesize(self, text: str) -> bytes:
        """
        Synthesizes text to speech (MP3) using gTTS.
        """
        try:
            if not text:
                raise ValueError("Text to synthesize cannot be empty.")
                
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to BytesIO
            fp = BytesIO()
            tts.write_to_fp(fp)
            
            # Reset pointer to start of stream
            fp.seek(0)
            
            return fp.read()
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            raise RuntimeError(f"Error generating voice audio: {str(e)}")

# Singleton
voice_service = VoiceService()
