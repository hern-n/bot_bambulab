import logging
import time

import mouse
import scanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

time.sleep(4)
scanner.clear_screenshots()
scanner.scan()

current_element_number = 9

in_captcha_yet = scanner.image_exists("screenshots/1.png", f"elements/9.png", 0.99)

logger.info(f"In captcha: {in_captcha_yet}")