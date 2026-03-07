import pyautogui
import cv2
import numpy as np
from pathlib import Path
import logging
from typing import Optional, List, Tuple
import pyperclip

logger = logging.getLogger(__name__)

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available - falling back to alternative methods")


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


def extract_numbers(screenshot_path: str) -> Optional[int]:
    """
    Extract blue numeric code from a screenshot using Tesseract OCR with blue color detection.

    Args:
        screenshot_path: Path to the screenshot image file

    Returns:
        int: The numeric code found in blue color
        None: If no blue numbers are detected
    """
    try:
        # Load image
        img = cv2.imread(screenshot_path)
        if img is None:
            logger.error(f"Failed to load image: {screenshot_path}")
            return None

        # Convert to HSV for blue detection
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Blue color range (adjustable based on your specific blue shade)
        lower_blue = np.array([100, 100, 100])
        upper_blue = np.array([140, 255, 255])

        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Apply mask to extract blue regions
        resultado = cv2.bitwise_and(img, img, mask=mask)

        # Convert to grayscale
        gray = cv2.cvtColor(resultado, cv2.COLOR_BGR2GRAY)

        # Binarize the image
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

        # Use Tesseract OCR if available
        if TESSERACT_AVAILABLE and pytesseract is not None:
            # OCR configuration - only digits
            config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
            texto = pytesseract.image_to_string(thresh, config=config)
            
            # Clean result to keep only digits
            numeros = ''.join(filter(str.isdigit, texto))
            
            if numeros:
                codigo = int(numeros)
                logger.info(f"Found blue number code using Tesseract: {codigo}")
                return codigo
            else:
                logger.info("No digits found with Tesseract in blue region")
                # Fall back to alternative method
                return _extract_numbers_with_template_matching(thresh)
        else:
            logger.info("Tesseract not available - using alternative method")
            return _extract_numbers_with_template_matching(thresh)

    except Exception as e:
        logger.error(f"Error during blue number extraction: {e}")
        return None


def _extract_numbers_with_template_matching(binary_image: np.ndarray) -> Optional[int]:
    """
    Extract numbers using simple contour analysis when pytesseract is not available.
    This is a simplified fallback method.
    """
    try:
        # Find contours in the binary image
        contours, _ = cv2.findContours(
            binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Sort contours by x-coordinate to read left to right
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])

        digits = []
        for contour in contours:
            # Filter contours by size (to avoid noise)
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)

            # Simple heuristics to identify digits
            if area > 100 and w > 5 and h > 10:
                # Approximate aspect ratio for digits
                aspect_ratio = w / h
                if 0.3 < aspect_ratio < 0.8:
                    # Use simple shape analysis to guess the digit
                    digit = _recognize_digit_by_shape(contour)
                    if digit is not None:
                        digits.append(str(digit))

        if digits:
            code = int("".join(digits))
            logger.info(f"Found blue number code using shape analysis: {code}")
            return code

        return None

    except Exception as e:
        logger.error(f"Error in template matching fallback: {e}")
        return None


def _recognize_digit_by_shape(contour: np.ndarray) -> Optional[int]:
    """
    Simple digit recognition based on contour shape properties.
    This is a basic implementation - for better results, use pytesseract.
    """
    # Calculate contour properties
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)

    if perimeter == 0:
        return None

    # Approximate the contour
    epsilon = 0.02 * perimeter
    approx = cv2.approxPolyDP(contour, epsilon, True)

    # Use number of vertices as a simple heuristic
    vertices = len(approx)

    # This is a very simplified recognition logic
    # In practice, you'd want more sophisticated methods
    if vertices == 3:
        return 7  # 7 often looks like a triangle
    elif vertices == 4:
        return 0  # 0 and 4 can have 4 vertices
    elif vertices == 5:
        return 5  # 5 often has 5 vertices
    elif vertices >= 6:
        return 8  # 8 often has many vertices

    return None


def match_multiple_templates(
    screenshot_path: str, template_paths: List[str], threshold: float = 0.8
) -> Optional[Tuple[str, Tuple[int, int], float]]:
    """
    Find the best match among multiple template images.

    Args:
        screenshot_path: Path to the screenshot image file
        template_paths: List of paths to template images to search for
        threshold: Minimum threshold for considering a match

    Returns:
        None if no matches found
        Tuple (template_path, (x, y), score) of the best match
    """
    best_match = None
    best_score = 0

    for template_path in template_paths:
        result = match_template(screenshot_path, template_path, threshold=threshold)
        if result:
            # Get the actual match score for comparison
            score = _get_match_score(screenshot_path, template_path, result)
            if score > best_score:
                best_score = score
                best_match = (template_path, result, score)

    if best_match:
        template_path, (x, y), score = best_match
        logger.info(
            f"Best overall match: {template_path} at ({x}, {y}) with score {score:.3f}"
        )
        return best_match

    logger.info(f"No matches found among {len(template_paths)} templates")
    return None


def _get_match_score(
    screenshot_path: str, template_path: str, location: Tuple[int, int]
) -> float:
    """Get the actual match score for a specific location."""
    try:
        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)

        if screenshot is None or template is None:
            return 0.0

        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Get template dimensions
        h, w = template_gray.shape

        # Adjust location to top-left corner of template
        x, y = location
        x = max(0, x - w // 2)
        y = max(0, y - h // 2)

        # Ensure the template fits within the screenshot
        if y + h > screenshot_gray.shape[0] or x + w > screenshot_gray.shape[1]:
            return 0.0

        # Extract the region and calculate correlation
        screenshot_region = screenshot_gray[y : y + h, x : x + w]
        result = cv2.matchTemplate(
            screenshot_region, template_gray, cv2.TM_CCOEFF_NORMED
        )
        _, max_val, _, _ = cv2.minMaxLoc(result)

        return float(max_val)
    except Exception as e:
        logger.error(f"Error calculating match score: {e}")
        return 0.0

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
    print(scan())
