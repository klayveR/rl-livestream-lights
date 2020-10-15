from classes.stream_analyzer import StreamAnalyzer
from classes.config import Config
from classes.dialog import Dialog
from classes.window_selector import WindowSelector
from classes.hue_setup import HueSetup
from classes.event_handler import EventHandler
from classes.hue_lights import HueLights
from phue import Bridge
import threading
import sys

if __name__ == "__main__":
    config = Config.read()

    """
    hue_lights = HueLights(config["hue"]["ip"])

    presets = config["hue"]["presets"]
    hue_lights.transition([4,7,8], presets["white"], brightness=200)
    #hue_lights.flash_cycle([4,7,8], config["hue"]["presets"]["green"], cycles=3)
    hue_lights.flash_cycle([4,5,7,8], presets["blue"], presets["blue"], cycles=3, intensity=config["hue"]["flash"]["intensity"])
    hue_lights.flash([4,5,7,8], presets["orange"], presets["orange"], cycles=3, intensity=config["hue"]["flash"]["intensity"])
    hue_lights.restore()
    """

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

    ### START EVENT HANDLER ###
    ehThread = threading.Thread(target=EventHandler, args=[config])
    ehThread.start()

    ### WINDOW SELECTION ###
    window = WindowSelector.select()

    print()

    ### START STREAM ANALYZER ###
    analyzerThread = threading.Thread(target=StreamAnalyzer, args=[config, window])
    analyzerThread.start()
    