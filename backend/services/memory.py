import time
from typing import List, Dict, Any
from backend.config import settings

class ConversationMemory:
    def __init__(self, max_history: int = settings.MAX_CHAT_HISTORY):
        self.max_history = max_history
        # Structure: { session_id: { "messages": [...], "last_accessed": timestamp } }
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def add_message(self, session_id: str, role: str, content: str):
        """Adds a message to the session history, trimming to max_history."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "last_accessed": time.time()
            }
            
        session = self.sessions[session_id]
        session["last_accessed"] = time.time()
        
        session["messages"].append({"role": role, "content": content})
        
        # Trim history if it exceeds max_history
        # Keep only the last `max_history` messages
        if len(session["messages"]) > self.max_history:
            # Try to keep pairs (user + assistant) intact
            session["messages"] = session["messages"][-self.max_history:]

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Returns the message history for a session."""
        if session_id in self.sessions:
            self.sessions[session_id]["last_accessed"] = time.time()
            return self.sessions[session_id]["messages"]
        return []

    def get_context_for_prompt(self, session_id: str) -> str:
        """Formats the history as a string suitable for a prompt context."""
        history = self.get_history(session_id)
        if not history:
            return ""
            
        context_parts = ["Previous Conversation:"]
        for msg in history:
            role_name = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role_name}: {msg['content']}")
            
        return "\n".join(context_parts) + "\n\n"

    def clear_session(self, session_id: str):
        """Removes a session from memory."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def cleanup_stale(self, max_age_hours: int = 24):
        """Removes sessions older than max_age_hours."""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        stale_sessions = [
            sid for sid, data in self.sessions.items()
            if (current_time - data["last_accessed"]) > max_age_seconds
        ]
        
        for sid in stale_sessions:
            del self.sessions[sid]

# Singleton instance
memory = ConversationMemory()
