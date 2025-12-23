"""
Tests for session management business logic.
"""

import pytest
import tempfile
import os
from datetime import datetime
from devlog.session import SessionManager
from devlog.storage import Storage


@pytest.fixture
def session_manager():
    """Create a session manager with temporary storage."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    storage = Storage(db_path)
    manager = SessionManager(storage)
    
    yield manager
    
    os.unlink(db_path)


def test_start_session(session_manager):
    """Test starting a new session."""
    result = session_manager.start_session(
        "Working on feature X",
        ["backend", "api"]
    )
    
    assert result['description'] == "Working on feature X"
    assert result['tags'] == ["backend", "api"]
    assert isinstance(result['start_time'], datetime)


def test_start_session_with_active_session(session_manager):
    """Test that starting a session when one is active raises error."""
    session_manager.start_session("First session", ["test"])
    
    with pytest.raises(ValueError, match="already in progress"):
        session_manager.start_session("Second session", ["test"])


def test_start_session_empty_description(session_manager):
    """Test that empty description raises error."""
    with pytest.raises(ValueError, match="cannot be empty"):
        session_manager.start_session("", ["test"])


def test_stop_session(session_manager):
    """Test stopping a session."""
    session_manager.start_session("Test task", ["test"])
    
    result = session_manager.stop_session("Completed successfully")
    
    assert result['description'] == "Test task"
    assert result['notes'] == "Completed successfully"
    assert result['duration'].total_seconds() > 0


def test_stop_session_no_active(session_manager):
    """Test stopping when no session is active."""
    with pytest.raises(ValueError, match="No active session"):
        session_manager.stop_session()


def test_get_current_session(session_manager):
    """Test getting current active session."""
    # No active session initially
    assert session_manager.get_current_session() is None
    
    # Start a session
    session_manager.start_session("Active task", ["test"])
    
    current = session_manager.get_current_session()
    assert current is not None
    assert current['description'] == "Active task"
    assert current['tags'] == ["test"]


def test_list_sessions(session_manager):
    """Test listing sessions with various filters."""
    # Create and complete some sessions
    session_manager.start_session("Task 1", ["backend"])
    session_manager.stop_session()
    
    session_manager.start_session("Task 2", ["frontend"])
    session_manager.stop_session()
    
    session_manager.start_session("Task 3", ["backend"])
    session_manager.stop_session()
    
    # List all
    all_sessions = session_manager.list_sessions()
    assert len(all_sessions) == 3
    
    # Filter by tag
    backend_sessions = session_manager.list_sessions(tag="backend")
    assert len(backend_sessions) == 2


def test_list_sessions_today(session_manager):
    """Test listing today's sessions."""
    session_manager.start_session("Today's task", ["test"])
    session_manager.stop_session()
    
    today_sessions = session_manager.list_sessions(today=True)
    assert len(today_sessions) == 1
    assert today_sessions[0]['description'] == "Today's task"


def test_search_sessions(session_manager):
    """Test searching sessions."""
    session_manager.start_session("Implement authentication", ["backend"])
    session_manager.stop_session()
    
    session_manager.start_session("Design UI", ["frontend"])
    session_manager.stop_session()
    
    results = session_manager.search_sessions("auth")
    assert len(results) == 1
    assert "authentication" in results[0]['description'].lower()


def test_delete_session(session_manager):
    """Test deleting a session."""
    result = session_manager.start_session("To delete", ["test"])
    session_id = result['id']
    session_manager.stop_session()
    
    # Delete it
    success = session_manager.delete_session(session_id)
    assert success
    
    # Verify it's gone
    sessions = session_manager.list_sessions()
    assert len(sessions) == 0


def test_session_stats(session_manager):
    """Test calculating session statistics."""
    # Create some completed sessions
    session_manager.start_session("Task 1", ["test"])
    session_manager.stop_session()
    
    session_manager.start_session("Task 2", ["test"])
    session_manager.stop_session()
    
    stats = session_manager.get_session_stats()
    
    assert stats['session_count'] == 2
    assert stats['total_minutes'] > 0
    assert stats['avg_minutes'] > 0


def test_tag_cleaning(session_manager):
    """Test that tags are cleaned and normalized."""
    result = session_manager.start_session(
        "Test task",
        ["Backend  ", "  Frontend", "API"]
    )
    
    # Tags should be trimmed
    assert result['tags'] == ["Backend  ", "Frontend", "API"]
