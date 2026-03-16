import logging
from pathlib import Path
from typing import Optional, Tuple

import cv2
import pyautogui

logger = logging.getLogger(__name__)


def scan() -> str:
    """
    Take a screenshot and save it to the screenshots folder.

    The screenshot filename will be a sequential number based on the count
    of existing screenshots in the folder.

    Returns:
        str: Path to the saved screenshot file
    """
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)

    # Count existing screenshots
    existing_files = [f for f in screenshots_dir.iterdir() if f.is_file()]
    next_number = len(existing_files) + 1

    # Generate filename and take screenshot
    filename = f"{next_number}.png"
    filepath = screenshots_dir / filename

    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)

    return str(filepath)


def image_exists(
    screenshot_path: str, model_image_path: str, threshold: float = 0.85
) -> bool:
    """
    Check if a model image exists within a screenshot.

    Args:
        screenshot_path: Path to the screenshot image file
        model_image_path: Path to the model image file to search for
        threshold: Matching threshold (0.0 to 1.0), higher means stricter matching

    Returns:
        bool: True if the model image is found in the screenshot, False otherwise
    """
    result = match_template(screenshot_path, model_image_path, threshold)

    if result:
        return True
    else:
        return False


def match_template(
    screenshot_path: str,
    model_image_path: str,
    threshold: float = 0.85,
) -> Optional[Tuple[int, int]]:
    """
    Find the location(s) of a model image within a screenshot using OpenCV template
    matching.

    Args:
        screenshot_path: Path to the screenshot image file
        model_image_path: Path to the model image file to search for
        threshold: Matching threshold (0.0 to 1.0), higher means stricter matching

    Returns:
        None if no match found
        Tuple (x, y) if one match found
    """
    try:
        # Load images
        screenshot = cv2.imread(screenshot_path)
        model_image = cv2.imread(model_image_path)

        if screenshot is None or model_image is None:
            logger.error(
                f"Failed to load images: screenshot={screenshot_path}, "
                f"model={model_image_path}"
            )
            return None

        # Convert to grayscale for better matching
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        model_gray = cv2.cvtColor(model_image, cv2.COLOR_BGR2GRAY)

        # Get dimensions of model image
        h, w = model_gray.shape

        # Perform template matching with multiple methods for better accuracy
        methods = [
            (cv2.TM_CCOEFF_NORMED, "CCOEFF_NORMED"),
            (cv2.TM_CCORR_NORMED, "CCORR_NORMED"),
        ]

        best_matches = []

        for method, method_name in methods:
            result = cv2.matchTemplate(screenshot_gray, model_gray, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # For correlation methods, higher is better
            best_val = max_val
            best_loc = max_loc

            # Only consider if it meets threshold
            if best_val >= threshold:
                best_matches.append((best_val, best_loc, method_name))
                logger.debug(f"{method_name}: score={best_val:.3f} at {best_loc}")

        if not best_matches:
            logger.info(
                f"No matches found for model image {model_image_path} in "
                f"screenshot {screenshot_path} (threshold: {threshold})"
            )
            return None

        # Sort by score (highest first) and take the best match
        best_matches.sort(key=lambda x: x[0], reverse=True)
        best_score, (x, y), method_used = best_matches[0]

        # Get center of the matched region (more accurate for clicking)
        center_x = x + w // 2
        center_y = y + h // 2

        logger.info(
            f"Best match: {method_used} score={best_score:.3f} at "
            f"center ({center_x}, {center_y})"
        )
        return int(center_x), int(center_y)

    except Exception as e:
        logger.error(f"Error during image matching: {e}")
        return None


def clear_screenshots() -> int:
    """
    Remove all .png files from the screenshots directory.

    Returns:
        int: Number of files removed
    """
    screenshots_dir = Path("screenshots")

    if not screenshots_dir.exists():
        logger.info("Screenshots directory does not exist")
        return 0

    # Find all .png files
    png_files = list(screenshots_dir.glob("*.png"))

    if not png_files:
        logger.info("No .png files found to clean")
        return 0

    # Remove all .png files
    removed_count = 0
    for png_file in png_files:
        try:
            png_file.unlink()
            removed_count += 1
            logger.debug(f"Removed: {png_file}")
        except OSError as e:
            logger.error(f"Failed to remove {png_file}: {e}")

    logger.info(f"Cleaned {removed_count} screenshot files")
    return removed_count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = scan()
    logger.info(f"Screenshot saved: {result}")
