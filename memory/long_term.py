"""
Long-Term Memory Module
Manages persistent user preferences and learned patterns.
"""

import logging
import json
import sqlite3
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class LongTermMemory:
    """Manages long-term persistent memory across sessions."""
    
    def __init__(self, db_path: str = "data/memory/long_term_memory.db"):
        """Initialize long-term memory with SQLite database."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info(f"Long-term memory initialized at {db_path}")
    
    def _init_database(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    preferences TEXT,
                    created_at TEXT,
                    last_active TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    query_type TEXT,
                    query_text TEXT,
                    frequency INTEGER DEFAULT 1,
                    last_used TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    query TEXT,
                    response TEXT,
                    rating INTEGER,
                    feedback_text TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
                )
            """)
            
            conn.commit()
    
    def get_or_create_user(self, user_id: str) -> Dict[str, Any]:
        """Get user profile or create if doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT preferences, created_at, last_active FROM user_profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                cursor.execute("UPDATE user_profiles SET last_active = ? WHERE user_id = ?", 
                             (datetime.now().isoformat(), user_id))
                conn.commit()
                
                return {
                    "user_id": user_id,
                    "preferences": json.loads(row[0]) if row[0] else {},
                    "created_at": row[1],
                    "last_active": datetime.now().isoformat()
                }
            else:
                now = datetime.now().isoformat()
                default_prefs = {
                    "preferred_image_types": [],
                    "favorite_topics": [],
                    "language": "en",
                    "detail_level": "normal"
                }
                
                cursor.execute("""
                    INSERT INTO user_profiles (user_id, preferences, created_at, last_active)
                    VALUES (?, ?, ?, ?)
                """, (user_id, json.dumps(default_prefs), now, now))
                conn.commit()
                
                return {
                    "user_id": user_id,
                    "preferences": default_prefs,
                    "created_at": now,
                    "last_active": now
                }
    
    def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """Update user preferences."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_profiles 
                SET preferences = ?, last_active = ?
                WHERE user_id = ?
            """, (json.dumps(preferences), datetime.now().isoformat(), user_id))
            conn.commit()
        
        logger.info(f"Updated preferences for user {user_id}")
    
    def record_query_pattern(self, user_id: str, query_type: str, query_text: str) -> None:
        """Record a query pattern for learning user behavior."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, frequency FROM query_patterns 
                WHERE user_id = ? AND query_type = ? AND query_text = ?
            """, (user_id, query_type, query_text))
            
            row = cursor.fetchone()
            
            if row:
                cursor.execute("""
                    UPDATE query_patterns 
                    SET frequency = frequency + 1, last_used = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), row[0]))
            else:
                cursor.execute("""
                    INSERT INTO query_patterns (user_id, query_type, query_text, last_used)
                    VALUES (?, ?, ?, ?)
                """, (user_id, query_type, query_text, datetime.now().isoformat()))
            
            conn.commit()
    
    def get_query_patterns(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequent query patterns for user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT query_type, query_text, frequency, last_used
                FROM query_patterns
                WHERE user_id = ?
                ORDER BY frequency DESC, last_used DESC
                LIMIT ?
            """, (user_id, limit))
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    "query_type": row[0],
                    "query_text": row[1],
                    "frequency": row[2],
                    "last_used": row[3]
                })
            
            return patterns
    
    def record_feedback(self, user_id: str, query: str, response: str, 
                       rating: int, feedback_text: str = "") -> None:
        """Record user feedback for improving responses."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback_history (user_id, query, response, rating, feedback_text, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, query, response, rating, feedback_text, datetime.now().isoformat()))
            conn.commit()
        
        logger.info(f"Recorded feedback for user {user_id}: rating={rating}")
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM query_patterns WHERE user_id = ?", (user_id,))
            total_queries = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*), AVG(rating) FROM feedback_history WHERE user_id = ?", (user_id,))
            feedback_row = cursor.fetchone()
            total_feedback = feedback_row[0]
            avg_rating = feedback_row[1] or 0
            
            cursor.execute("""
                SELECT query_type, COUNT(*) as count 
                FROM query_patterns 
                WHERE user_id = ? 
                GROUP BY query_type 
                ORDER BY count DESC 
                LIMIT 5
            """, (user_id,))
            top_query_types = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            return {
                "total_queries": total_queries,
                "total_feedback": total_feedback,
                "average_rating": round(avg_rating, 2),
                "top_query_types": top_query_types
            }
