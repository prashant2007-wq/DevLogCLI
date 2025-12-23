"""
Report generation and formatting for DevLog.
Creates human-readable summaries of work sessions.
"""

from datetime import datetime, timedelta
from typing import Dict, List
from devlog.storage import Storage
from devlog.utils import format_duration


class ReportGenerator:
    """Generates formatted reports from session data."""
    
    def __init__(self, storage: Storage):
        """
        Initialize report generator.
        
        Args:
            storage: Storage instance to query data from
        """
        self.storage = storage
    
    def generate_summary(
        self,
        days: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        by_tag: bool = False
    ) -> str:
        """
        Generate a summary report of work sessions.
        
        Args:
            days: Last N days to include
            start_date: Custom start date
            end_date: Custom end date
            by_tag: Group results by tag
            
        Returns:
            Formatted report string
        """
        if days:
            start_date = datetime.now() - timedelta(days=days)
            end_date = datetime.now()
        
        period_desc = self._get_period_description(start_date, end_date, days)
        
        sessions = self.storage.get_sessions(
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        completed = [s for s in sessions if s['duration']]
        total_minutes = sum(s['duration'] for s in completed)
        
        report_lines = [
            f"DevLog Report - {period_desc}",
            "=" * 60,
            "",
            f"Total Sessions: {len(completed)}",
            f"Total Time: {format_duration(total_minutes)}",
            f"Average Session: {format_duration(total_minutes / len(completed)) if completed else '0m'}",
            ""
        ]
        
        if by_tag:
            tag_summary = self.storage.get_tag_summary(start_date, end_date)
            if tag_summary:
                report_lines.extend([
                    "Time by Tag:",
                    "-" * 60
                ])
                
                for tag, count, minutes in tag_summary:
                    percentage = (minutes / total_minutes * 100) if total_minutes > 0 else 0
                    report_lines.append(
                        f"  {tag:20} {format_duration(minutes):>10} "
                        f"({count} sessions, {percentage:.1f}%)"
                    )
                report_lines.append("")
        else:
            if completed:
                report_lines.extend([
                    "Recent Sessions:",
                    "-" * 60
                ])
                
                for session in completed[:10]:
                    start_time = datetime.fromisoformat(session['start_time'])
                    tags = session['tags'].split(',') if session['tags'] else []
                    tags_str = f" [{', '.join(tags)}]" if tags else ""
                    
                    report_lines.append(
                        f"  {start_time.strftime('%b %d, %I:%M %p')} - "
                        f"{format_duration(session['duration']):>6} - "
                        f"{session['description'][:40]}{tags_str}"
                    )
        
        return "\n".join(report_lines)
    
    def generate_day_report(self, date: datetime) -> str:
        """
        Generate detailed report for a specific day.
        
        Args:
            date: The date to generate report for
            
        Returns:
            Formatted daily report
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        sessions = self.storage.get_sessions(
            start_date=start_of_day,
            end_date=end_of_day,
            limit=100
        )
        
        completed = [s for s in sessions if s['duration']]
        total_minutes = sum(s['duration'] for s in completed)
        
        report_lines = [
            f"Daily Report - {date.strftime('%A, %B %d, %Y')}",
            "=" * 60,
            "",
            f"Sessions: {len(completed)}",
            f"Total Time: {format_duration(total_minutes)}",
            ""
        ]
        
        if completed:
            report_lines.append("Sessions:")
            report_lines.append("-" * 60)
            
            for session in completed:
                start_time = datetime.fromisoformat(session['start_time'])
                end_time = datetime.fromisoformat(session['end_time']) if session['end_time'] else None
                tags = session['tags'].split(',') if session['tags'] else []
                
                time_range = f"{start_time.strftime('%I:%M %p')}"
                if end_time:
                    time_range += f" - {end_time.strftime('%I:%M %p')}"
                
                report_lines.extend([
                    f"\n  {time_range}",
                    f"  Duration: {format_duration(session['duration'])}",
                    f"  Task: {session['description']}"
                ])
                
                if tags:
                    report_lines.append(f"  Tags: {', '.join(tags)}")
                
                if session['notes']:
                    report_lines.append(f"  Notes: {session['notes']}")
        else:
            report_lines.append("No completed sessions for this day.")
        
        return "\n".join(report_lines)
    
    def _get_period_description(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        days: Optional[int]
    ) -> str:
        """Get human-readable description of time period."""
        if days == 1:
            return "Today"
        elif days == 7:
            return "Last 7 Days"
        elif days == 30:
            return "Last 30 Days"
        elif start_date and end_date:
            return f"{start_date.strftime('%b %d')} to {end_date.strftime('%b %d, %Y')}"
        else:
            return "All Time"
