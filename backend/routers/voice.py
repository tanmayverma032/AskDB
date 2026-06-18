from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from fastapi.responses import StreamingResponse
import io

from backend.services.voice import voice_service

router = APIRouter(prefix="/api/voice", tags=["voice"])

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe uploaded audio file to text.
    """
    try:
        # Read file contents
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file")
            
        text = await voice_service.transcribe(audio_bytes)
        return {"text": text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/synthesize")
async def synthesize_speech(payload: dict = Body(...)):
    """
    Synthesize text to speech and return audio stream.
    Expects {"text": "Hello world"} in body.
    """
    try:
        text = payload.get("text")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required for synthesis")
            
        audio_bytes = await voice_service.synthesize(text)
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")
