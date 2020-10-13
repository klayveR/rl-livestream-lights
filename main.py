from classes.stream_analyzer import StreamAnalyzer
from classes.config import Config
from classes.dialog import Dialog
from classes.window_selector import WindowSelector
from classes.hue_setup import HueSetup
from classes.event_handler import EventHandler
import threading
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

    print()

    ### START EVENT HANDLER ###
    ehThread = threading.Thread(target=EventHandler, args=[config])
    ehThread.start()

    ### START STREAM ANALYZER ###
    analyzerThread = threading.Thread(target=StreamAnalyzer, args=[config, window])
    analyzerThread.start()
    