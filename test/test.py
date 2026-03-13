import scanner
import mouse
import time

time.sleep(4)
scanner.clear_screenshots()
scanner.scan()

current_element_number = 9

in_captcha_yet = scanner.image_exists("screenshots/1.png", f"elements/9.png", 0.99)

print(in_captcha_yet)