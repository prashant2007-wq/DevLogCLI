"""
Tests for CLI commands.
"""

import pytest
from click.testing import CliRunner
from devlog.cli import cli
import tempfile
import os


@pytest.fixture
def runner():
    """Create a CLI test runner with temporary database."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    runner = CliRunner()
    
    # Set environment variable for test database
    os.environ['DEVLOG_DB_PATH'] = db_path
    
    yield runner
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_cli_help(runner):
    """Test that help command works."""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'DevLog' in result.output


def test_start_command(runner):
    """Test starting a session via CLI."""
    result = runner.invoke(cli, ['start', 'Working on tests', '--tags', 'testing'])
    
    # Should succeed
    assert result.exit_code == 0
    assert 'Session started' in result.output


def test_start_command_multiple_tags(runner):
    """Test starting with multiple tags."""
    result = runner.invoke(cli, [
        'start', 
        'Backend work',
        '--tags', 'backend',
        '--tags', 'api'
    ])
    
    assert result.exit_code == 0
    assert 'Session started' in result.output


def test_stop_command(runner):
    """Test stopping a session."""
    # First start a session
    runner.invoke(cli, ['start', 'Test task'])
    
    # Then stop it
    result = runner.invoke(cli, ['stop'])
    
    assert result.exit_code == 0
    assert 'Session stopped' in result.output
    assert 'Duration' in result.output


def test_stop_command_with_notes(runner):
    """Test stopping with notes."""
    runner.invoke(cli, ['start', 'Test task'])
    
    result = runner.invoke(cli, ['stop', '--notes', 'Completed successfully'])
    
    assert result.exit_code == 0
    assert 'Session stopped' in result.output


def test_stop_without_active_session(runner):
    """Test stopping when no session is active."""
    result = runner.invoke(cli, ['stop'])
    
    # Should fail gracefully
    assert result.exit_code != 0
    assert 'No active session' in result.output


def test_status_no_session(runner):
    """Test status when no session is active."""
    result = runner.invoke(cli, ['status'])
    
    assert result.exit_code == 0
    assert 'No active session' in result.output


def test_status_with_active_session(runner):
    """Test status with an active session."""
    runner.invoke(cli, ['start', 'Active task', '--tags', 'test'])
    
    result = runner.invoke(cli, ['status'])
    
    assert result.exit_code == 0
    assert 'Active Session' in result.output
    assert 'Active task' in result.output


def test_list_command(runner):
    """Test listing sessions."""
    # Create a session
    runner.invoke(cli, ['start', 'Test task'])
    runner.invoke(cli, ['stop'])
    
    result = runner.invoke(cli, ['list'])
    
    assert result.exit_code == 0
    assert 'Test task' in result.output


def test_list_today(runner):
    """Test listing today's sessions."""
    runner.invoke(cli, ['start', 'Today task'])
    runner.invoke(cli, ['stop'])
    
    result = runner.invoke(cli, ['list', '--today'])
    
    assert result.exit_code == 0
    assert 'Today task' in result.output


def test_search_command(runner):
    """Test searching sessions."""
    # Create sessions
    runner.invoke(cli, ['start', 'Implement authentication'])
    runner.invoke(cli, ['stop'])
    
    runner.invoke(cli, ['start', 'Design UI'])
    runner.invoke(cli, ['stop'])
    
    result = runner.invoke(cli, ['search', 'auth'])
    
    assert result.exit_code == 0
    assert 'authentication' in result.output.lower()


def test_report_command(runner):
    """Test generating a report."""
    # Create a session
    runner.invoke(cli, ['start', 'Test task'])
    runner.invoke(cli, ['stop'])
    
    result = runner.invoke(cli, ['report', '--today'])
    
    assert result.exit_code == 0
    assert 'DevLog Report' in result.output
    assert 'Total Sessions' in result.output


def test_report_by_tag(runner):
    """Test report grouped by tags."""
    runner.invoke(cli, ['start', 'Backend work', '--tags', 'backend'])
    runner.invoke(cli, ['stop'])
    
    result = runner.invoke(cli, ['report', '--today', '--by-tag'])
    
    assert result.exit_code == 0
    assert 'Time by Tag' in result.output


def test_workflow(runner):
    """Test complete workflow: start, stop, list, report."""
    # Start a session
    result = runner.invoke(cli, ['start', 'Complete workflow test', '--tags', 'testing'])
    assert result.exit_code == 0
    
    # Check status
    result = runner.invoke(cli, ['status'])
    assert 'Active Session' in result.output
    
    # Stop session
    result = runner.invoke(cli, ['stop', '--notes', 'Test completed'])
    assert result.exit_code == 0
    
    # List sessions
    result = runner.invoke(cli, ['list', '--today'])
    assert 'Complete workflow test' in result.output
    
    # Generate report
    result = runner.invoke(cli, ['report', '--today'])
    assert 'DevLog Report' in result.output
