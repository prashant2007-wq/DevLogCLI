"""
Command-line interface for DevLog.
Handles user interaction and command routing.
"""

import click
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import box

from devlog.session import SessionManager
from devlog.storage import Storage
from devlog.report import ReportGenerator
from devlog.utils import format_duration, get_time_ago, parse_date_string

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """DevLog - Track your coding sessions and productivity."""
    pass


@cli.command()
@click.argument('description')
@click.option('--tags', '-t', multiple=True, help='Tags for this session (can specify multiple times)')
def start(description: str, tags: tuple):
    """Start a new work session."""
    try:
        manager = SessionManager()
        session = manager.start_session(description, list(tags))
        
        console.print(f"✓ Session started at {session['start_time'].strftime('%I:%M %p')}", style="bold green")
        console.print(f"  Task: {description}")
        if tags:
            console.print(f"  Tags: {', '.join(tags)}", style="dim")
        console.print("\nStop this session with: devlog stop", style="dim")
    except ValueError as e:
        console.print(f"✗ Error: {e}", style="bold red")
        raise click.Abort()


@cli.command()
@click.option('--notes', '-n', help='Notes about what you accomplished')
def stop(notes: Optional[str]):
    """Stop the current work session."""
    try:
        manager = SessionManager()
        session = manager.stop_session(notes)
        
        console.print(f"✓ Session stopped", style="bold green")
        console.print(f"  Task: {session['description']}")
        console.print(f"  Duration: {format_duration(int(session['duration'].total_seconds() / 60))}", style="bold")
        if notes:
            console.print(f"  Notes: {notes}", style="dim")
    except ValueError as e:
        console.print(f"✗ Error: {e}", style="bold red")
        raise click.Abort()


@cli.command()
def status():
    """Show current session status."""
    manager = SessionManager()
    session = manager.get_current_session()
    
    if session:
        start_time = datetime.fromisoformat(session['start_time'])
        elapsed = datetime.now() - start_time
        elapsed_minutes = int(elapsed.total_seconds() / 60)
        
        console.print("⏱️  Active Session", style="bold blue")
        console.print(f"  Task: {session['description']}")
        console.print(f"  Started: {get_time_ago(start_time)}")
        console.print(f"  Duration: {format_duration(elapsed_minutes)}", style="bold")
        if session['tags']:
            console.print(f"  Tags: {', '.join(session['tags'])}", style="dim")
    else:
        console.print("No active session", style="dim")
        console.print("\nStart a session with: devlog start \"Your task description\"", style="dim")


@cli.command()
@click.option('--today', is_flag=True, help='Show only today\'s sessions')
@click.option('--days', '-d', type=int, help='Show sessions from last N days')
@click.option('--tag', '-t', help='Filter by tag')
@click.option('--limit', '-l', default=20, help='Maximum number of sessions to show')
def list(today: bool, days: Optional[int], tag: Optional[str], limit: int):
    """List past work sessions."""
    manager = SessionManager()
    sessions = manager.list_sessions(days=days, today=today, tag=tag, limit=limit)
    
    if not sessions:
        console.print("No sessions found", style="dim")
        return
    
    table = Table(box=box.ROUNDED)
    table.add_column("Date", style="cyan")
    table.add_column("Time", style="cyan")
    table.add_column("Duration", justify="right", style="green")
    table.add_column("Description")
    table.add_column("Tags", style="dim")
    
    for session in sessions:
        start_time = datetime.fromisoformat(session['start_time'])
        duration = format_duration(session['duration']) if session['duration'] else "In progress"
        tags_str = ", ".join(session['tags']) if session['tags'] else ""
        
        table.add_row(
            start_time.strftime("%b %d"),
            start_time.strftime("%I:%M %p"),
            duration,
            session['description'][:50],
            tags_str
        )
    
    console.print(table)
    
    if len(sessions) >= limit:
        console.print(f"\nShowing {limit} most recent sessions. Use --limit to see more.", style="dim")


@cli.command()
@click.argument('search_term')
@click.option('--limit', '-l', default=20, help='Maximum results')
def search(search_term: str, limit: int):
    """Search sessions by description or notes."""
    manager = SessionManager()
    sessions = manager.search_sessions(search_term, limit)
    
    if not sessions:
        console.print(f"No sessions found matching '{search_term}'", style="dim")
        return
    
    console.print(f"Found {len(sessions)} session(s) matching '{search_term}':\n", style="bold")
    
    for session in sessions:
        start_time = datetime.fromisoformat(session['start_time'])
        duration = format_duration(session['duration']) if session['duration'] else "In progress"
        
        console.print(f"• {start_time.strftime('%b %d, %I:%M %p')} - {duration}", style="cyan")
        console.print(f"  {session['description']}")
        if session['tags']:
            console.print(f"  Tags: {', '.join(session['tags'])}", style="dim")
        if session['notes']:
            console.print(f"  Notes: {session['notes']}", style="dim")
        console.print()


@cli.command()
@click.option('--today', is_flag=True, help='Report for today')
@click.option('--week', is_flag=True, help='Report for last 7 days')
@click.option('--month', is_flag=True, help='Report for last 30 days')
@click.option('--days', '-d', type=int, help='Report for last N days')
@click.option('--from', 'from_date', help='Start date (YYYY-MM-DD)')
@click.option('--to', 'to_date', help='End date (YYYY-MM-DD)')
@click.option('--by-tag', is_flag=True, help='Group by tags')
def report(today: bool, week: bool, month: bool, days: Optional[int], 
           from_date: Optional[str], to_date: Optional[str], by_tag: bool):
    """Generate productivity reports."""
    storage = Storage()
    generator = ReportGenerator(storage)
    
    start_date = None
    end_date = None
    
    if from_date:
        start_date = parse_date_string(from_date)
    if to_date:
        end_date = parse_date_string(to_date)
    
    if today:
        days = 1
    elif week:
        days = 7
    elif month:
        days = 30
    
    report_text = generator.generate_summary(
        days=days,
        start_date=start_date,
        end_date=end_date,
        by_tag=by_tag
    )
    
    console.print(report_text)


@cli.command()
@click.argument('session_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this session?')
def delete(session_id: int):
    """Delete a session by ID."""
    manager = SessionManager()
    
    if manager.delete_session(session_id):
        console.print(f"✓ Session {session_id} deleted", style="bold green")
    else:
        console.print(f"✗ Session {session_id} not found", style="bold red")


if __name__ == '__main__':
    cli()
