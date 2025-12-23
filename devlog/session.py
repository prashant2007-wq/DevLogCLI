"""
Business logic for managing work sessions.
Coordinates between CLI and storage layer.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from devlog.storage import Storage


class SessionManager:
    """Handles session lifecycle and business rules."""
    
    def __init__(self, storage: Optional[Storage] = None):
        """
        Initialize session manager.
        
        Args:
            storage: Storage instance. Creates default if not provided.
        """
        self.storage = storage or Storage()
    
    def start_session(self, description: str, tags: List[str]) -> Dict:
        """
        Start a new work session.
        
        Args:
            description: What you're working on
            tags: Categories/labels for this session
            
        Returns:
            Dictionary with session details
            
        Raises:
            ValueError: If there's already an active session
        """
        active = self.storage.get_active_session()
        if active:
            raise ValueError(
                f"Session already in progress: {active['description']}. "
                "Stop it first with 'devlog stop'"
            )
        
        if not description.strip():
            raise ValueError("Description cannot be empty")
        
        cleaned_tags = [t.strip() for t in tags if t.strip()]
        
        session_id = self.storage.create_session(description, cleaned_tags)
        
        return {
            'id': session_id,
            'description': description,
            'tags': cleaned_tags,
            'start_time': datetime.now()
        }
    
    def stop_session(self, notes: Optional[str] = None) -> Dict:
        """
        Stop the currently active session.
        
        Args:
            notes: Optional notes about what was accomplished
            
        Returns:
            Dictionary with completed session details
            
        Raises:
            ValueError: If no active session exists
        """
        active = self.storage.get_active_session()
        if not active:
            raise ValueError("No active session to stop")
        
        success = self.storage.end_session(active['id'], notes)
        if not success:
            raise ValueError("Failed to stop session")
        
        start_time = datetime.fromisoformat(active['start_time'])
        duration = datetime.now() - start_time
        
        return {
            'id': active['id'],
            'description': active['description'],
            'duration': duration,
            'notes': notes
        }
    
    def get_current_session(self) -> Optional[Dict]:
        """
        Get the currently active session if one exists.
        
        Returns:
            Active session dict or None
        """
        session = self.storage.get_active_session()
        if session and session['tags']:
            session['tags'] = session['tags'].split(',')
        return session
    
    def list_sessions(
        self,
        days: Optional[int] = None,
        today: bool = False,
        tag: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        List past sessions with filters.
        
        Args:
            days: Show sessions from last N days
            today: Show only today's sessions
            tag: Filter by specific tag
            limit: Maximum sessions to return
            
        Returns:
            List of session dictionaries
        """
        start_date = None
        end_date = None
        
        if today:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = datetime.now()
        elif days:
            start_date = datetime.now() - timedelta(days=days)
            end_date = datetime.now()
        
        sessions = self.storage.get_sessions(
            start_date=start_date,
            end_date=end_date,
            tag=tag,
            limit=limit
        )
        
        for session in sessions:
            if session['tags']:
                session['tags'] = session['tags'].split(',')
            else:
                session['tags'] = []
        
        return sessions
    
    def search_sessions(self, search_term: str, limit: int = 50) -> List[Dict]:
        """
        Search sessions by description or notes.
        
        Args:
            search_term: Text to search for
            limit: Maximum results
            
        Returns:
            List of matching session dictionaries
        """
        sessions = self.storage.get_sessions(
            search_term=search_term,
            limit=limit
        )
        
        for session in sessions:
            if session['tags']:
                session['tags'] = session['tags'].split(',')
            else:
                session['tags'] = []
        
        return sessions
    
    def delete_session(self, session_id: int) -> bool:
        """
        Delete a session by ID.
        
        Args:
            session_id: ID of session to delete
            
        Returns:
            True if deleted successfully
        """
        return self.storage.delete_session(session_id)
    
    def get_session_stats(
        self,
        days: Optional[int] = None,
        today: bool = False
    ) -> Dict:
        """
        Calculate statistics for sessions.
        
        Args:
            days: Calculate stats for last N days
            today: Calculate stats for today only
            
        Returns:
            Dictionary with total_time, session_count, avg_session_time
        """
        sessions = self.list_sessions(days=days, today=today, limit=1000)
        
        completed_sessions = [s for s in sessions if s.get('duration')]
        total_minutes = sum(s['duration'] for s in completed_sessions)
        session_count = len(completed_sessions)
        avg_minutes = total_minutes / session_count if session_count > 0 else 0
        
        return {
            'total_minutes': total_minutes,
            'session_count': session_count,
            'avg_minutes': avg_minutes,
            'total_sessions_including_active': len(sessions)
        }
