"""
Utility functions for DevLog.
Shared helpers for formatting and data manipulation.
"""

from datetime import datetime, timedelta
from typing import Optional


def format_duration(minutes: int) -> str:
    """
    Format duration in minutes to human-readable string.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted string like "2h 30m" or "45m"
    """
    if minutes < 60:
        return f"{minutes}m"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes == 0:
        return f"{hours}h"
    
    return f"{hours}h {remaining_minutes}m"


def parse_time_delta(time_str: str) -> timedelta:
    """
    Parse a time delta string like "2h", "30m", "1h30m".
    
    Args:
        time_str: String representation of time
        
    Returns:
        timedelta object
        
    Raises:
        ValueError: If format is invalid
    """
    time_str = time_str.lower().strip()
    hours = 0
    minutes = 0
    
    if 'h' in time_str:
        parts = time_str.split('h')
        hours = int(parts[0])
        if len(parts) > 1 and parts[1]:
            minutes = int(parts[1].replace('m', ''))
    elif 'm' in time_str:
        minutes = int(time_str.replace('m', ''))
    else:
        raise ValueError("Time must include 'h' or 'm' (e.g., '2h' or '30m')")
    
    return timedelta(hours=hours, minutes=minutes)


def format_datetime(dt: datetime, include_time: bool = True) -> str:
    """
    Format datetime for display.
    
    Args:
        dt: Datetime to format
        include_time: Whether to include time component
        
    Returns:
        Formatted string
    """
    if include_time:
        return dt.strftime("%Y-%m-%d %I:%M %p")
    return dt.strftime("%Y-%m-%d")


def parse_date_string(date_str: str) -> datetime:
    """
    Parse various date string formats.
    
    Args:
        date_str: Date string (YYYY-MM-DD, today, yesterday)
        
    Returns:
        Parsed datetime
        
    Raises:
        ValueError: If format is invalid
    """
    date_str = date_str.lower().strip()
    
    if date_str == "today":
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_str == "yesterday":
        return (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    else:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "Invalid date format. Use YYYY-MM-DD, 'today', or 'yesterday'"
            )


def get_time_ago(dt: datetime) -> str:
    """
    Get human-readable "time ago" string.
    
    Args:
        dt: Past datetime
        
    Returns:
        String like "2 hours ago" or "3 days ago"
    """
    now = datetime.now()
    
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    
    delta = now - dt
    
    if delta.days > 0:
        if delta.days == 1:
            return "yesterday"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
    
    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    
    minutes = delta.seconds // 60
    if minutes > 0:
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    
    return "just now"
