"""
Chat Management System with SQLite Database
Handles chat sessions, messages, and persistence across server restarts.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import uuid


class ChatDatabase:
    """Manages chat sessions and messages in SQLite database."""
    
    def __init__(self, db_path: str = "data/chat_history.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Chat sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                message_count INTEGER DEFAULT 0
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_user 
            ON chat_sessions(user_id, is_active)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_message_session 
            ON messages(session_id, created_at)
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, user_id: str, title: str = "New Chat") -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_sessions (session_id, user_id, title)
            VALUES (?, ?, ?)
        """, (session_id, user_id, title))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all chat sessions for a user."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute("""
                SELECT * FROM chat_sessions 
                WHERE user_id = ? AND is_active = 1
                ORDER BY updated_at DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT * FROM chat_sessions 
                WHERE user_id = ?
                ORDER BY updated_at DESC
            """, (user_id,))
        
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return sessions
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM chat_sessions WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_session_title(self, session_id: str, title: str):
        """Update session title."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE chat_sessions 
            SET title = ?, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (title, session_id))
        
        conn.commit()
        conn.close()
    
    def delete_session(self, session_id: str):
        """Soft delete a session (mark as inactive)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE chat_sessions 
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (session_id,))
        
        conn.commit()
        conn.close()
    
    def permanent_delete_session(self, session_id: str):
        """Permanently delete a session and all its messages."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete messages first (foreign key constraint)
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        
        # Delete session
        cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
        
        conn.commit()
        conn.close()
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a message to a session."""
        message_id = str(uuid.uuid4())
        metadata_json = json.dumps(metadata) if metadata else None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (message_id, session_id, role, content, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (message_id, session_id, role, content, metadata_json))
        
        # Update session
        cursor.execute("""
            UPDATE chat_sessions 
            SET updated_at = CURRENT_TIMESTAMP,
                message_count = message_count + 1
            WHERE session_id = ?
        """, (session_id,))
        
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM messages 
            WHERE session_id = ?
            ORDER BY created_at ASC
        """, (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            msg = dict(row)
            if msg['metadata']:
                msg['metadata'] = json.loads(msg['metadata'])
            messages.append(msg)
        
        conn.close()
        
        return messages
    
    def clear_session_messages(self, session_id: str):
        """Clear all messages from a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        
        cursor.execute("""
            UPDATE chat_sessions 
            SET message_count = 0, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (session_id,))
        
        conn.commit()
        conn.close()
    
    def get_session_count(self, user_id: str) -> int:
        """Get total number of active sessions for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM chat_sessions 
            WHERE user_id = ? AND is_active = 1
        """, (user_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def search_sessions(self, user_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search sessions by title or message content."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT cs.* 
            FROM chat_sessions cs
            LEFT JOIN messages m ON cs.session_id = m.session_id
            WHERE cs.user_id = ? 
            AND cs.is_active = 1
            AND (cs.title LIKE ? OR m.content LIKE ?)
            ORDER BY cs.updated_at DESC
        """, (user_id, f"%{search_term}%", f"%{search_term}%"))
        
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return sessions
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total sessions
        cursor.execute("""
            SELECT COUNT(*) FROM chat_sessions 
            WHERE user_id = ? AND is_active = 1
        """, (user_id,))
        total_sessions = cursor.fetchone()[0]
        
        # Total messages
        cursor.execute("""
            SELECT COUNT(*) FROM messages m
            JOIN chat_sessions cs ON m.session_id = cs.session_id
            WHERE cs.user_id = ? AND cs.is_active = 1
        """, (user_id,))
        total_messages = cursor.fetchone()[0]
        
        # Most recent session
        cursor.execute("""
            SELECT updated_at FROM chat_sessions 
            WHERE user_id = ? AND is_active = 1
            ORDER BY updated_at DESC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        last_activity = row[0] if row else None
        
        conn.close()
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "last_activity": last_activity
        }
