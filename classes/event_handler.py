from enums.sender import Sender
from enums.game_state import GameState
from enums.team import Team
from classes.hue_lights import HueLights
from pydispatch import dispatcher
import time

class EventHandler():
    def __init__(self, config):
        self.config = config
        self.presets = self.config["hue"]["presets"]
        self.light_ids = self.config["hue"]["lights"]
        self.flash = self.config["hue"]["flash"]
        self.brightness = self.config["hue"]["brightness"]

        self.hue_lights = HueLights(self.config["hue"]["ip"])

        self.hue_lights.transition(self.light_ids, self.presets["green"], speed=5, brightness=254)
        self.hue_lights.restore()
        
        dispatcher.connect(self.handle_waiting_for_game, signal=GameState.WAITING_FOR_GAME, sender=Sender.STREAM_ANALYZER)
        dispatcher.connect(self.handle_kickoff, signal=GameState.KICKOFF, sender=Sender.STREAM_ANALYZER)
        dispatcher.connect(self.handle_playing, signal=GameState.PLAYING, sender=Sender.STREAM_ANALYZER)
        dispatcher.connect(self.handle_goal, signal=GameState.GOAL, sender=Sender.STREAM_ANALYZER)
        dispatcher.connect(self.handle_overtime, signal=GameState.OVERTIME, sender=Sender.STREAM_ANALYZER)
        dispatcher.connect(self.handle_end, signal=GameState.END, sender=Sender.STREAM_ANALYZER)
        
        self.run()

    def run(self):
        while True:
            time.sleep(0.1)

    def handle_waiting_for_game(self, message):
        print(f'Event handler received WAITING_FOR_GAME, data: {message}')
        self.hue_lights.restore()

    def handle_kickoff(self, message):
        print(f'Event handler received KICKOFF, data: {message}')
        self.hue_lights.transition(self.light_ids, self.presets["white"], speed=10, brightness=self.brightness["kickoff"])

    def handle_playing(self, message):
        print(f'Event handler received PLAYING, data: {message}')
        self.hue_lights.transition(self.light_ids, self.presets["white"], speed=10, brightness=self.brightness["playing"])

    def handle_goal(self, message):
        print(f'Event handler received GOAL, data: {message}')

        preset = self.presets["blue"]

        if message == Team.ORANGE:
            preset = self.presets["orange"]

        if self.flash["mode"] == 1:
            self.hue_lights.flash(self.light_ids, preset, preset, cycles=self.flash["cycles"],\
                intensity=self.flash["intensity"], brightness=self.brightness["goal"])
        elif self.flash["mode"] == 2:
            self.hue_lights.flash_cycle(self.light_ids, preset, preset, cycles=self.flash["cycles"],\
                intensity=self.flash["intensity"], brightness=self.brightness["goal"])
        else:
            self.hue_lights.transition(self.light_ids, preset, speed=1, brightness=self.brightness["goal"])

    def handle_overtime(self, message):
        print(f'Event handler received OVERTIME, data: {message}')
        self.hue_lights.transition(self.light_ids, self.presets["white"], speed=5, brightness=254)

    def handle_end(self, message):
        print(f'Event handler received END, data: {message}')

        preset = self.presets["blue"]

        if message == Team.ORANGE:
            preset = self.presets["orange"]

        self.hue_lights.transition(self.light_ids, preset, speed=5, brightness=254)