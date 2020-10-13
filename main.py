from classes.stream_analyzer import StreamAnalyzer
from classes.image_reader import ImageReader
from classes.config import Config
from classes.dialog import Dialog
from classes.window_selector import WindowSelector
from classes.hue_setup import HueSetup
from phue import Bridge
import time
import cv2
import sys

if __name__ == "__main__":
    config = Config.read()

    ### HUE SETUP ###
    hue_setup = HueSetup(config)
    setup_success = True
    if hue_setup.is_setup_needed():
        setup_success = hue_setup.start()
    else:
        start_setup = Dialog.ask_yes_no("Would you like to set up your Philips hue configuration again?")
        if start_setup:
            setup_success = hue_setup.start()

    if not setup_success:
        print("Setup was unsuccessful")
        sys.exit()

    ### WINDOW SELECTION ###
    window = WindowSelector.select()

    ### START STREAM ANALYZER ###
    analyzer = StreamAnalyzer(config, window)
    analyzer.start()
