from PIL import Image
from desktopmagic.screengrab_win32 import (getRectAsImage, getScreenAsImage)
import win32gui
import numpy as np
import cv2
import pytesseract

class ImageReader():
    @staticmethod
    def read_area(im, area):
        return ImageReader.read(im, area["bounds"], area["rotation"], area["threshold"], area["psm"], area["whitelist"], area["customlang"])

    @staticmethod
    def read(im, bounds, rotation = 0, threshold = 127, psm = 7, whitelist = None, customlang = True):
        prepared = ImageReader.prepare_image(im, bounds, rotation, threshold)
        cv2.imwrite("temp.jpg", prepared)
        config = f"--oem 3 --psm {psm}"

        if whitelist:
            config += f' -c tessedit_char_whitelist="{whitelist}"'

        if customlang:
            config += f' -l rl'

        text = pytesseract.image_to_string(prepared, config=config)

        # Remove non whitelisted characters from read text
        if whitelist:
            text = ImageReader.__strip_non_whitelisted(text, whitelist)

        return text

    @staticmethod
    def prepare_image_area(im, area):
        return ImageReader.prepare_image(im, area["bounds"], area["rotation"], area["threshold"])

    @staticmethod
    def prepare_image(im, bounds, rotation = 0, threshold = 127):
        im = np.array(im)

        try:
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) # Convert to greyscale
        except:
            print("Already in grayscale")

        height, width = im.shape

        # Determine new bounds
        left = round(width * bounds[0])
        top = round(height * bounds[1])
        right = round(width * bounds[2])
        bottom = round(height * bounds[3])

        im = im[top:bottom, left:right] # Crop image

        try:
            im = ImageReader.__rotate_image(im, rotation) # Rotate image
        except:
            print("Can't rotate image")

        ret,im = cv2.threshold(im, threshold, 255, cv2.THRESH_BINARY_INV) # Apply threshold

        return im

    @staticmethod
    def screenshot(window_title = None):
        if window_title:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowPlacement(hwnd)[1] != 2:
                    rect = win32gui.GetWindowRect(hwnd)
                    screenshot = getRectAsImage(rect)
                    return screenshot
            else:
                print("Window not found!")
        else:
            screenshot = getScreenAsImage()
            return screenshot

    @staticmethod
    def __rotate_image(image, angle):
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result

    @staticmethod
    def __strip_non_whitelisted(s, whitelist):
        whitelist = set(whitelist)
        return "".join([c for c in s if c in whitelist])