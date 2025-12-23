"""
Database storage layer for DevLog sessions.
Handles all SQLite operations and queries.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class Storage:
    """Manages persistent storage of work sessions using SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize storage with database path.
        
        Args:
            db_path: Path to SQLite database file. Defaults to ~/.devlog/devlog.db
        """
        if db_path is None:
            home = Path.home()
            devlog_dir = home / ".devlog"
            devlog_dir.mkdir(exist_ok=True)
            db_path = str(devlog_dir / "devlog.db")
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration INTEGER,
                    notes TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_start_time 
                ON sessions(start_time)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tags_session_id 
                ON tags(session_id)
            """)
            
            conn.commit()
    
    def create_session(self, description: str, tags: List[str]) -> int:
        """
        Create a new work session.
        
        Args:
            description: Description of the work being done
            tags: List of tags to categorize the session
            
        Returns:
            The ID of the created session
        """
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (description, start_time, created_at)
                VALUES (?, ?, ?)
            """, (description, now, now))
            
            session_id = cursor.lastrowid
            
            for tag in tags:
                cursor.execute("""
                    INSERT INTO tags (session_id, tag)
                    VALUES (?, ?)
                """, (session_id, tag.lower().strip()))
            
            conn.commit()
            return session_id
    
    def end_session(self, session_id: int, notes: Optional[str] = None) -> bool:
        """
        End a work session and calculate duration.
        
        Args:
            session_id: ID of the session to end
            notes: Optional notes to add to the session
            
        Returns:
            True if session was ended, False if not found
        """
        now = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT start_time FROM sessions WHERE id = ?
            """, (session_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            start_time = datetime.fromisoformat(result[0])
            duration = int((now - start_time).total_seconds() / 60)  # minutes
            
            cursor.execute("""
                UPDATE sessions 
                SET end_time = ?, duration = ?, notes = ?
                WHERE id = ?
            """, (now.isoformat(), duration, notes, session_id))
            
            conn.commit()
            return True
    
    def get_active_session(self) -> Optional[Dict]:
        """
        Get the currently active session (no end_time).
        
        Returns:
            Session dict or None if no active session
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT s.*, GROUP_CONCAT(t.tag) as tags
                FROM sessions s
                LEFT JOIN tags t ON s.id = t.session_id
                WHERE s.end_time IS NULL
                GROUP BY s.id
                ORDER BY s.start_time DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_sessions(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tag: Optional[str] = None,
        search_term: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query sessions with various filters.
        
        Args:
            start_date: Filter sessions after this date
            end_date: Filter sessions before this date
            tag: Filter by specific tag
            search_term: Search in description and notes
            limit: Maximum number of results
            
        Returns:
            List of session dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT s.*, GROUP_CONCAT(t.tag) as tags
                FROM sessions s
                LEFT JOIN tags t ON s.id = t.session_id
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND s.start_time >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND s.start_time <= ?"
                params.append(end_date.isoformat())
            
            if tag:
                query += " AND s.id IN (SELECT session_id FROM tags WHERE tag = ?)"
                params.append(tag.lower().strip())
            
            if search_term:
                query += " AND (s.description LIKE ? OR s.notes LIKE ?)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern])
            
            query += " GROUP BY s.id ORDER BY s.start_time DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_tag_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Tuple[str, int, int]]:
        """
        Get time spent per tag.
        
        Args:
            start_date: Filter sessions after this date
            end_date: Filter sessions before this date
            
        Returns:
            List of (tag, session_count, total_minutes) tuples
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT t.tag, COUNT(DISTINCT s.id) as session_count, 
                       COALESCE(SUM(s.duration), 0) as total_minutes
                FROM tags t
                JOIN sessions s ON t.session_id = s.id
                WHERE s.duration IS NOT NULL
            """
            params = []
            
            if start_date:
                query += " AND s.start_time >= ?"
                params.append(start_date.isoformat())
            
            if end_date:
                query += " AND s.start_time <= ?"
                params.append(end_date.isoformat())
            
            query += " GROUP BY t.tag ORDER BY total_minutes DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def delete_session(self, session_id: int) -> bool:
        """
        Delete a session by ID.
        
        Args:
            session_id: ID of session to delete
            
        Returns:
            True if deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0
