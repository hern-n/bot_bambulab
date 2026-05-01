# AGENTS.md - BambuLab Bot Development Guide

Python 3.12+ GUI automation bot using computer vision (OpenCV) and mouse automation (pyautogui) for screen interaction with graphical interfaces.

## Development Environment

```bash
# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Unix/Linux

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
python src/scanner.py
```

## Build/Lint/Test Commands

### Code Quality
```bash
black src/                     # Format code (line length: 88)
flake8 src/ --max-line-length=88
pyflakes src/
```

### Testing
The `test/` folder contains exploratory tests for validating technologies - NOT official unit tests.

```bash
pytest                          # Run all tests
pytest test/                    # Run all tests in directory
pytest test/test.py             # Run single test file
pytest test/agentmail_test.py::test_function_name  # Run single test function
pytest -v                      # Verbose output
pytest -k "pattern"            # Run tests matching pattern
```

## Code Style Guidelines

### Python Standards
- PEP 8 compliant, formatted with Black (88 char line limit)
- Type hints required for function signatures
- Maximum line length: 88 characters
- Docstrings for all public functions and modules

### Import Order
1. Standard library (`import logging`, `import os`, `from typing import Optional`)
2. Third-party (`import cv2`, `import pyautogui`)
3. Local imports (`import scanner`, `from src.mouse import go`)

```python
import logging
import os
from typing import Optional, Tuple

import cv2
import numpy as np
import pyautogui

import scanner
from src.mouse import click_at_position
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
    ...

def match_template(
    screenshot_path: str,
    model_image_path: str,
    threshold: float = 0.85,
) -> Optional[Tuple[int, int]]:
    ...
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

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
```

**Never use `print()`** - always use the logging module:
- `logger.debug()` - detailed debug information
- `logger.info()` - general information
- `logger.warning()` - warnings
- `logger.error()` - errors

## File Structure
```
bot_bambulab_edge/
├── src/
│   ├── main.py              # Main automation entry point
│   ├── scanner.py           # Screenshot capture, template matching
│   ├── mouse.py             # Mouse/keyboard automation
│   └── agentmail_client.py  # AgentMail API client
├── elements/                # Template images for OpenCV matching
├── screenshots/             # Captured screenshots
├── test/                    # Exploratory tests
├── config.json              # Automation configuration
├── requirements.txt         # Dependencies
└── AGENTS.md                # This file
```

## Core Modules

### Scanner (`src/scanner.py`)
- `scan() -> str`: Capture screenshot, save sequentially numbered PNG
- `match_template(screenshot, model, threshold) -> Optional[Tuple[int, int]]`: Find template in screenshot, returns center coords
- `image_exists(screenshot, model, threshold) -> bool`: Check if template exists
- `clear_screenshots() -> int`: Remove all screenshots, returns count

### Mouse (`src/mouse.py`)
- `click_at_position(coordinates)`: Left-click at (x, y)
- `go(x, y) -> bool`: Move mouse to coordinates
- `type_text(text) -> bool`: Type text via clipboard paste
- `paste_from_clipboard() -> bool`: Ctrl+V paste
- `scroll_down(amount=300) -> bool`: Scroll down
- `wait_for_human(image_model)`: Play beeps, wait for user/CAPTCHA resolution

### AgentMail (`src/agentmail_client.py`)
- `create_inbox() -> str`: Create inbox, return inbox_id
- `get_email(inbox_id) -> Optional[str]`: Get email HTML body
- `get_code(html) -> Optional[int]`: Extract 6-digit verification code
- `delete_inbox(inbox_id)`: Delete single inbox
- `delete_all_inboxes()`: Delete all inboxes
- `list_inboxes() -> list[tuple]`: List all inboxes

## Dependencies
| Package | Purpose |
|---------|---------|
| pyautogui | GUI automation |
| opencv-python | Computer vision |
| pyperclip | Clipboard access |
| keyboard | Keyboard input |
| pytest | Testing |
| agentmail | Email API client |

## Security Notes
- Never commit screenshots with sensitive data
- Use `.env` for API keys (in `.gitignore`)
- Validate image paths before processing
- pyautogui fail-safe: move mouse to screen corner to abort
