# AGENTS.md - BambuLab Bot Development Guide

## Project Overview
Python 3.12 GUI automation bot using computer vision (OpenCV) and mouse automation (pyautogui) for screen interaction with graphical interfaces.

## Development Environment Setup
```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Unix/Linux)
source venv/bin/activate

# Install dependencies
pip install pyautogui opencv-python pyperclip keyboard

# Install dev dependencies
pip install black flake8 pytest pyflakes
```

## Build/Lint/Test Commands

### Running the Application
```bash
python src/main.py
python src/scanner.py
python -c "import src.scanner as s; print(s.scan())"
```

### Code Quality
```bash
black src/                    # Format code (line length: 88)
flake8 src/ --max-line-length=88
pyflakes src/
```

### Testing (Exploratory)
The `test/` folder contains exploratory tests for validating different technologies - NOT official project unit tests.
```bash
pytest                        # Run all tests
pytest test/                  # Run all exploratory tests
pytest test/test.py           # Run single test file
pytest test/agentmail_test.py::test_function_name  # Run single test function
pytest -v                     # Verbose output
pytest -k "agentmail"         # Run tests matching pattern
```

## Code Style Guidelines

### Python Standards
- PEP 8 compliant, formatted with Black (88 char line limit)
- Type hints required for function signatures
- Maximum line length: 88 characters

### Import Order
```python
# Standard library
import os
import sys
from typing import Optional, Tuple

# Third-party
import cv2
import pyautogui

# Local
from src.mouse import click_at_position
from src.scanner import scan
```

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Variables/functions | snake_case | `scan()`, `screenshot_path` |
| Classes | PascalCase | `ImageProcessor` |
| Constants | UPPER_SNAKE_CASE | `MATCH_THRESHOLD` |
| Private members | prefix `_` | `_private_method` |
| Modules | lowercase_snake.py | `scanner.py` |

### Type Hints
```python
def process_image(path: str, options: Optional[dict] = None) -> Tuple[bool, str]:
    pass
```

### Error Handling
```python
try:
    result = risky_operation()
except ValueError as e:
    logger.warning(f"Invalid input: {e}")
    return None
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

### Logging
```python
logger = logging.getLogger(__name__)

logger.info("Operation started")
logger.debug(f"Processing {count} items")
logger.error("Failed", exc_info=True)
```

## File Structure
```
bot_bambulab/
├── src/
│   ├── main.py           # Main automation entry point
│   ├── scanner.py        # Screenshot capture, template matching
│   ├── mouse.py          # Mouse automation (click, type, scroll)
│   └── agentmail_client.py  # AgentMail API client
├── elements/             # Template images for matching
├── screenshots/          # Captured screenshots
├── test/                 # Exploratory tests (not official unit tests)
├── skills/               # Agent skills
└── AGENTS.md
```

## Core Modules

### Scanner (`src/scanner.py`)
- `scan()`: Capture screenshot, save sequentially numbered PNG
- `match_template()`: Find template in screenshot (returns center coords)
- `image_exists()`: Check if template exists in screenshot (returns bool)
- `clear_screenshots()`: Remove all screenshots

### Mouse (`src/mouse.py`)
- `click_at_position((x, y))`: Left-click at coordinates
- `go(x, y)`: Move mouse to coordinates
- `type_text(text)`: Type text at cursor
- `paste_from_clipboard()`: Ctrl+V paste
- `scroll_down(amount)`: Scroll down

### AgentMail (`src/agentmail_client.py`)
- `create_inbox()`: Create a new email inbox
- `get_email(inbox_id)`: Get email address for inbox
- `get_code(inbox_id)`: Get verification code from inbox
- `delete_all_inboxes()`: Delete all inboxes

## Skills (AgentMail Integration)

This project includes skills for AgentMail - an API-first email platform for AI agents.

### What is AgentMail?
AgentMail gives AI agents their own email inboxes. Use it for:
- Creating inboxes programmatically
- Sending/receiving emails
- Managing attachments
- Real-time notifications via webhooks/websockets

### Skills Location
- Current skills: `agentmail-skills/agentmail/` (git submodule)

## Dependencies
- `pyautogui` - GUI automation
- `opencv-python` - Computer vision
- `pyperclip` - Clipboard access
- `keyboard` - Keyboard input detection
- `pytest` - Testing

## Security Notes
- Never commit screenshots with sensitive data
- Use `.env` for API keys (already in `.gitignore`)
- Validate image paths before processing
