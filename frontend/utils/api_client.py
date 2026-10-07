import os
import httpx
from typing import Dict, Any, List, Optional

class AskDBClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or os.getenv("API_URL", "http://localhost:8000")).rstrip("/")
        self.client = httpx.Client(timeout=30.0)
        
    def _handle_error(self, e: Exception) -> Dict[str, Any]:
        return {"error": str(e), "success": False}
        
    def connect_database(self, db_type, host, port, user, password, database) -> Dict[str, Any]:
        try:
            response = self.client.post(
                f"{self.base_url}/api/database/connect",
                json={
                    "db_type": db_type,
                    "host": host,
                    "port": port,
                    "user": user,
                    "password": password,
                    "database": database
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_error(e)

    def disconnect_database(self) -> Dict[str, Any]:
        try:
            response = self.client.post(f"{self.base_url}/api/database/disconnect")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_error(e)

    def get_status(self) -> Dict[str, Any]:
        try:
            response = self.client.get(f"{self.base_url}/api/database/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_error(e)

    def get_schema(self) -> Dict[str, Any]:
        try:
            response = self.client.get(f"{self.base_url}/api/database/schema")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_error(e)

    def get_tables(self) -> List[str]:
        try:
            response = self.client.get(f"{self.base_url}/api/database/tables")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return []

    def chat(self, question: str, session_id: str) -> Dict[str, Any]:
        try:
            response = self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "question": question,
                    "session_id": session_id
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_error(e)

    def explain_query(self, sql: str) -> Dict[str, Any]:
        try:
            response = self.client.post(
                f"{self.base_url}/api/query/explain",
                json={"sql": sql}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_error(e)

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        try:
            files = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
            response = self.client.post(
                f"{self.base_url}/api/voice/transcribe",
                files=files
            )
            response.raise_for_status()
            return response.json().get("text", "")
        except Exception as e:
            return f"Error transcribing audio: {str(e)}"

    def synthesize_speech(self, text: str) -> bytes:
        try:
            response = self.client.post(
                f"{self.base_url}/api/voice/synthesize",
                json={"text": text}
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            return b""

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        try:
            response = self.client.get(f"{self.base_url}/api/query/history/{session_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return []

api_client = AskDBClient()
