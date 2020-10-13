from enum import Enum

class GameState(Enum):
    IDLE = "idle"
    KICKOFF = "kickoff"
    PLAYING = "playing"
    GOAL = "goal"
    REPLAY = "replay"
    END = "end"