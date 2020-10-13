from enum import Enum

class GameState(Enum):
    WAITING_FOR_GAME = "waiting_for_game"
    KICKOFF = "kickoff"
    PLAYING = "playing"
    GOAL = "goal"
    OVERTIME = "overtime"
    END = "end"
