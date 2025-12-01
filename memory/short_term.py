"""
Short-Term Memory Module
Manages conversation context within a single session.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """Manages short-term conversational memory for the current session."""
    
    def __init__(self, max_turns: int = 10):
        """
        Initialize short-term memory.
        
        Args:
            max_turns: Maximum number of conversation turns to retain
        """
        self.max_turns = max_turns
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_start = datetime.now()
        logger.info(f"Short-term memory initialized with max_turns={max_turns}")
    
    def add_turn(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a conversation turn to short-term memory.
        
        Args:
            role: Speaker role (user/assistant)
            content: Message content
            metadata: Optional metadata (agent used, confidence, etc.)
        """
        turn = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversation_history.append(turn)
        
        if len(self.conversation_history) > self.max_turns * 2:
            self.conversation_history = self.conversation_history[-(self.max_turns * 2):]
        
        logger.debug(f"Added {role} turn to STM. Total turns: {len(self.conversation_history)}")
    
    def get_context(self, num_turns: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve recent conversation context.
        
        Args:
            num_turns: Number of recent turns to retrieve (None = all)
            
        Returns:
            List of conversation turns
        """
        if num_turns is None:
            return self.conversation_history.copy()
        return self.conversation_history[-num_turns:] if self.conversation_history else []
    
    def format_for_llm(self, num_turns: Optional[int] = None) -> str:
        """
        Format conversation history for LLM context.
        
        Args:
            num_turns: Number of recent turns to include
            
        Returns:
            Formatted conversation string
        """
        turns = self.get_context(num_turns)
        if not turns:
            return "No conversation history."
        
        formatted = []
        for turn in turns:
            role = turn["role"].capitalize()
            content = turn["content"][:200]
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)
    
    def get_last_query(self) -> Optional[str]:
        """Get the last user query."""
        for turn in reversed(self.conversation_history):
            if turn["role"] == "user":
                return turn["content"]
        return None
    
    def get_last_response(self) -> Optional[str]:
        """Get the last assistant response."""
        for turn in reversed(self.conversation_history):
            if turn["role"] == "assistant":
                return turn["content"]
        return None
    
    def clear(self) -> None:
        """Clear all conversation history."""
        self.conversation_history.clear()
        self.session_start = datetime.now()
        logger.info("Short-term memory cleared")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the current session."""
        user_turns = sum(1 for t in self.conversation_history if t["role"] == "user")
        assistant_turns = sum(1 for t in self.conversation_history if t["role"] == "assistant")
        
        return {
            "total_turns": len(self.conversation_history),
            "user_turns": user_turns,
            "assistant_turns": assistant_turns,
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "session_start": self.session_start.isoformat()
        }
