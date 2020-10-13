from enums.sender import Sender
from enums.game_state import GameState
from pydispatch import dispatcher
import time

class EventHandler():
    def __init__(self, config):
        self.config = config

        dispatcher.connect(self.handle_waiting_for_game, signal=GameState.WAITING_FOR_GAME, sender=Sender.STREAM_ANALYZER)
        dispatcher.connect(self.handle_kickoff, signal=GameState.KICKOFF, sender=Sender.STREAM_ANALYZER)
        dispatcher.connect(self.handle_playing, signal=GameState.PLAYING, sender=Sender.STREAM_ANALYZER)
        dispatcher.connect(self.handle_goal, signal=GameState.GOAL, sender=Sender.STREAM_ANALYZER)
        dispatcher.connect(self.handle_overtime, signal=GameState.OVERTIME, sender=Sender.STREAM_ANALYZER)
        dispatcher.connect(self.handle_end, signal=GameState.END, sender=Sender.STREAM_ANALYZER)
        
        self.run()

    def run(self):
        print("Event Handler started")
        while True:
            time.sleep(0.1)

    def handle_waiting_for_game(self, message):
        print(f'Event handler received WAITING_FOR_GAME, data: {message}')

    def handle_kickoff(self, message):
        print(f'Event handler received KICKOFF, data: {message}')

    def handle_playing(self, message):
        print(f'Event handler received PLAYING, data: {message}')

    def handle_goal(self, message):
        print(f'Event handler received GOAL, data: {message}')

    def handle_overtime(self, message):
        print(f'Event handler received OVERTIME, data: {message}')

    def handle_end(self, message):
        print(f'Event handler received END, data: {message}')