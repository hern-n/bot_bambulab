import pyautogui
from typing import Union, Tuple, List
import pyperclip
import logging
import winsound
import sys
import keyboard  
import time

logger = logging.getLogger(__name__)


def click_at_position(coordinates: Union[Tuple[int, int], List[int]]) -> None:
    """
    Move the mouse cursor to the specified coordinates and perform a right click.

    Args:
        coordinates: A tuple or list containing x and y coordinates (x, y)

    Raises:
        ValueError: If coordinates are not valid (must contain exactly 2 values)
        pyautogui.FailSafeException: If mouse moves to corner of screen (safety feature)
    """
    if len(coordinates) != 2:
        raise ValueError("Coordinates must contain exactly 2 values (x, y)")

    x, y = coordinates
    pyautogui.leftClick(x, y)


def paste_from_clipboard() -> bool:
    """
    Paste clipboard content at current mouse cursor position using Ctrl+V.

    This function uses the standard paste shortcut to handle special characters
    like @ symbols correctly, which pyautogui.typewrite may not process properly.

    Returns:
        bool: True if paste was successful, False otherwise
    """
    try:
        # Check if clipboard has content first
        clipboard_content = pyperclip.paste()

        if not clipboard_content:
            logger.warning("Clipboard is empty")
            return False

        logger.info(f"Pasting clipboard content: {repr(clipboard_content)}")

        # Use Ctrl+V shortcut for more reliable pasting of special characters
        pyautogui.hotkey("ctrl", "v")

        logger.info("Successfully pasted clipboard content")
        return True

    except pyperclip.PyperclipException as e:
        logger.error(f"Clipboard access error: {e}")
        return False
    except pyautogui.FailSafeException:
        logger.error("PyAutoGUI fail-safe triggered - mouse moved to corner")
        return False
    except Exception as e:
        logger.error(f"Error during paste operation: {e}")
        return False


def type_text(text: str) -> bool:
    """
    Type the given text as if a human were typing it.

    Args:
        text: The text string to type

    Returns:
        bool: True if typing was successful, False otherwise
    """
    try:
        if not text:
            logger.warning("Empty text provided")
            return False

        logger.info(f"Typing text: {repr(text)}")

        # Copy text to clipboard
        pyperclip.copy(text)

        # Paste at current cursor position
        pyautogui.hotkey("ctrl", "v")

        logger.info("Successfully typed text")
        return True

    except pyautogui.FailSafeException:
        logger.error("PyAutoGUI fail-safe triggered - mouse moved to corner")
        return False

    except Exception as e:
        logger.error(f"Error during typing operation: {e}")
        return False


def scroll_down(amount: int = 300) -> bool:
    """
    Scroll down the page simulating mouse wheel movement.

    Args:
        amount: Number of scroll units to scroll down (default: 300)

    Returns:
        bool: True if scrolling was successful, False otherwise
    """
    try:
        if amount <= 0:
            logger.warning("Scroll amount must be positive")
            return False

        logger.info(f"Scrolling down {amount} units")

        # Use negative value for scrolling down
        pyautogui.scroll(-amount)

        logger.info("Successfully scrolled down")
        return True

    except pyautogui.FailSafeException:
        logger.error("PyAutoGUI fail-safe triggered - mouse moved to corner")
        return False
    except Exception as e:
        logger.error(f"Error during scroll operation: {e}")
        return False


def go(x: int, y: int) -> bool:
    """
    Move the mouse cursor to the specified coordinates.

    Args:
        x: X coordinate to move to
        y: Y coordinate to move to

    Returns:
        bool: True if movement was successful, False otherwise
    """
    try:
        if not isinstance(x, int) or not isinstance(y, int):
            logger.error("Coordinates must be integers")
            return False

        logger.info(f"Moving mouse to coordinates ({x}, {y})")

        # Move mouse to specified coordinates
        pyautogui.moveTo(x, y)

        logger.info(f"Successfully moved mouse to ({x}, {y})")
        return True

    except pyautogui.FailSafeException:
        logger.error("PyAutoGUI fail-safe triggered - mouse moved to corner")
        return False
    except Exception as e:
        logger.error(f"Error during mouse movement: {e}")
        return False


def wait_for_human(message: str = "Presiona F2 para continuar...") -> None:
    """
    Play two beeps and wait for the user to press F2 to continue,
    or continue automatically after 25 seconds.
    """

    logger = logging.getLogger(__name__)
    logger.info("Playing alert beeps for human attention")

    winsound.MessageBeep(winsound.MB_OK)
    winsound.MessageBeep(winsound.MB_OK)

    print(message)

    timeout = 25
    start_time = time.time()

    while True:
        # Si presiona F2
        if keyboard.is_pressed("f2"):
            logger.info("Human pressed F2, continuing execution")
            break

        # Si pasan 25 segundos
        if time.time() - start_time > timeout:
            logger.info("Timeout reached (25s), continuing automatically")
            break

        time.sleep(0.1)  # evita consumir CPU