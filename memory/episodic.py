"""
Episodic Memory Module
Manages memory of specific past interactions and episodes.
"""

import logging
import sqlite3
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EpisodicMemory:
    """Manages episodic memory of past interactions and conversations."""
    
    def __init__(self, db_path: str = "data/memory/episodic_memory.db"):
        """Initialize episodic memory with SQLite database."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.info(f"Episodic memory initialized at {db_path}")
    
    def _init_database(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS episodes (
                    episode_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    session_id TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    summary TEXT,
                    metadata TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    episode_id TEXT,
                    user_id TEXT,
                    query TEXT,
                    response TEXT,
                    agents_used TEXT,
                    image_path TEXT,
                    retrieved_images TEXT,
                    confidence_score REAL,
                    timestamp TEXT,
                    FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_episodes 
                ON episodes(user_id, start_time DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_interactions 
                ON interactions(user_id, timestamp DESC)
            """)
            
            conn.commit()
    
    def create_episode(self, episode_id: str, user_id: str, session_id: str, 
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new episode."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO episodes (episode_id, user_id, session_id, start_time, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (episode_id, user_id, session_id, now, json.dumps(metadata or {})))
            conn.commit()
        
        logger.info(f"Created episode {episode_id} for user {user_id}")
        return episode_id
    
    def record_interaction(self, episode_id: str, user_id: str, query: str, 
                          response: str, agents_used: List[str], 
                          image_path: str = "", retrieved_images: Optional[List[Dict]] = None,
                          confidence_score: Optional[float] = None) -> int:
        """Record a single interaction within an episode."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO interactions 
                (episode_id, user_id, query, response, agents_used, image_path, 
                 retrieved_images, confidence_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                episode_id, user_id, query, response, 
                json.dumps(agents_used), image_path,
                json.dumps(retrieved_images or []),
                confidence_score,
                datetime.now().isoformat()
            ))
            
            interaction_id = cursor.lastrowid
            conn.commit()
        
        logger.debug(f"Recorded interaction {interaction_id} in episode {episode_id}")
        return interaction_id
    
    def end_episode(self, episode_id: str, summary: str = "") -> None:
        """Mark an episode as ended."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE episodes 
                SET end_time = ?, summary = ?
                WHERE episode_id = ?
            """, (datetime.now().isoformat(), summary, episode_id))
            conn.commit()
        
        logger.info(f"Ended episode {episode_id}")
    
    def get_episode(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """Get episode details with all interactions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT episode_id, user_id, session_id, start_time, end_time, summary, metadata
                FROM episodes WHERE episode_id = ?
            """, (episode_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            episode = {
                "episode_id": row[0],
                "user_id": row[1],
                "session_id": row[2],
                "start_time": row[3],
                "end_time": row[4],
                "summary": row[5],
                "metadata": json.loads(row[6]) if row[6] else {}
            }
            
            cursor.execute("""
                SELECT query, response, agents_used, image_path, retrieved_images, 
                       confidence_score, timestamp
                FROM interactions 
                WHERE episode_id = ?
                ORDER BY timestamp ASC
            """, (episode_id,))
            
            interactions = []
            for irow in cursor.fetchall():
                interactions.append({
                    "query": irow[0],
                    "response": irow[1],
                    "agents_used": json.loads(irow[2]) if irow[2] else [],
                    "image_path": irow[3],
                    "retrieved_images": json.loads(irow[4]) if irow[4] else [],
                    "confidence_score": irow[5],
                    "timestamp": irow[6]
                })
            
            episode["interactions"] = interactions
            return episode
    
    def get_user_episodes(self, user_id: str, limit: int = 10, 
                         days_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent episodes for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT e.episode_id, e.session_id, e.start_time, e.end_time, e.summary,
                       COUNT(i.id) as interaction_count
                FROM episodes e
                LEFT JOIN interactions i ON e.episode_id = i.episode_id
                WHERE e.user_id = ?
            """
            params = [user_id]
            
            if days_back:
                cutoff = (datetime.now() - timedelta(days=days_back)).isoformat()
                query += " AND e.start_time >= ?"
                params.append(cutoff)
            
            query += " GROUP BY e.episode_id ORDER BY e.start_time DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            episodes = []
            for row in cursor.fetchall():
                episodes.append({
                    "episode_id": row[0],
                    "session_id": row[1],
                    "start_time": row[2],
                    "end_time": row[3],
                    "summary": row[4],
                    "interaction_count": row[5]
                })
            
            return episodes
    
    def search_interactions(self, user_id: str, search_term: str, 
                          limit: int = 20) -> List[Dict[str, Any]]:
        """Search past interactions by query or response content."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            cursor.execute("""
                SELECT i.episode_id, i.query, i.response, i.agents_used, 
                       i.confidence_score, i.timestamp, e.session_id
                FROM interactions i
                JOIN episodes e ON i.episode_id = e.episode_id
                WHERE i.user_id = ? AND (i.query LIKE ? OR i.response LIKE ?)
                ORDER BY i.timestamp DESC
                LIMIT ?
            """, (user_id, search_pattern, search_pattern, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "episode_id": row[0],
                    "query": row[1],
                    "response": row[2],
                    "agents_used": json.loads(row[3]) if row[3] else [],
                    "confidence_score": row[4],
                    "timestamp": row[5],
                    "session_id": row[6]
                })
            
            return results
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get episodic memory statistics for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Statistics dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM episodes WHERE user_id = ?", (user_id,))
            total_episodes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM interactions WHERE user_id = ?", (user_id,))
            total_interactions = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT AVG(confidence_score) 
                FROM interactions 
                WHERE user_id = ? AND confidence_score IS NOT NULL
            """, (user_id,))
            avg_confidence = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT MIN(start_time), MAX(start_time) 
                FROM episodes 
                WHERE user_id = ?
            """, (user_id,))
            date_range = cursor.fetchone()
            
            return {
                "total_episodes": total_episodes,
                "total_interactions": total_interactions,
                "average_confidence": round(avg_confidence, 3),
                "first_episode": date_range[0],
                "last_episode": date_range[1]
            }
