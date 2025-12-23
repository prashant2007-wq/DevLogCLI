# DevLog - Developer Activity Tracker

A lightweight CLI tool for tracking coding sessions and generating productivity insights. Never forget what you worked on during standup again.

## Problem Statement

As developers, we often struggle to recall what we worked on throughout the day or week. DevLog solves this by providing a simple way to log work sessions with tags, durations, and notes, then query that data later.

## Features

- 🚀 Start/stop timed work sessions
- 🏷️ Tag sessions by project, task type, or category
- 📊 Generate daily, weekly, and monthly reports
- 🔍 Search through past sessions
- 💾 Local SQLite storage (no cloud, your data stays private)
- 📈 Productivity metrics and time breakdowns

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/devlog.git
cd devlog

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

## Quick Start

```bash
# Start a new session
devlog start "Working on authentication" --tags backend,api

# Stop current session
devlog stop

# View today's sessions
devlog list --today

# Generate weekly report
devlog report --week

# Search sessions
devlog search "authentication"
```

## Usage Examples

### Starting a Session
```bash
devlog start "Implementing user login" --tags backend,security
# Output: Session started at 2:30 PM
```

### Stopping a Session
```bash
devlog stop --notes "Completed OAuth integration, need to add tests"
# Output: Session ended. Duration: 2h 15m
```

### Listing Sessions
```bash
# Today's work
devlog list --today

# Last 7 days
devlog list --days 7

# Filter by tag
devlog list --tag backend
```

### Generating Reports
```bash
# Weekly summary
devlog report --week

# Monthly breakdown by tag
devlog report --month --by-tag

# Custom date range
devlog report --from 2024-01-01 --to 2024-01-31
```

## Technical Decisions

### Why SQLite?
- Zero configuration required
- Fast for CLI workloads
- Perfect for single-user local data
- Easy to backup (just copy the .db file)

### Why Click for CLI?
- Industry standard for Python CLIs
- Excellent documentation and testing support
- Built-in validation and type conversion
- Clean decorator-based API

### Architecture
- **Separation of concerns**: CLI layer, business logic, and storage are independent
- **Testability**: Each module can be tested in isolation
- **Extensibility**: Easy to add new commands or storage backends

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Structure
- `cli.py` - Command-line interface and user interaction
- `session.py` - Session management and business logic
- `storage.py` - Database operations and queries
- `report.py` - Report generation and formatting
- `utils.py` - Shared utilities and helpers

## Future Improvements

- Export reports to CSV/JSON
- Git integration (auto-detect branch/repo)
- Pomodoro timer integration
- Team sharing features (optional cloud sync)
- VSCode/IDE extensions

## Contributing

This is a portfolio project, but suggestions are welcome! Open an issue to discuss potential changes.

## License

MIT License - feel free to use this code for learning or as a base for your own projects.

---

**Author Note**: Built as a code sample for the MLH Fellowship application. This project demonstrates practical CLI development, database design, testing practices, and solving a real problem I encountered in my own workflow.
