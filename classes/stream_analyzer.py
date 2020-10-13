from enums.game_state import GameState
from enums.team import Team
from enums.sender import Sender
from classes.image_reader import ImageReader
from pydispatch import dispatcher
import re
import math
import time

class StreamAnalyzer():
    def __init__(self, config, window_title):
        self.config = config
        self.window_title = window_title
        self.screenshot = None
        self.__reset()
        self.run()

    def run(self):
        print("Stream analyzer started")
        self.__set_state(GameState.WAITING_FOR_GAME)

        while True:
            self.screenshot = ImageReader.screenshot(self.window_title)

            if self.screenshot == None:
                continue

            if self.state == GameState.WAITING_FOR_GAME:
                self.__analyze_waiting_for_game()
            elif self.state == GameState.KICKOFF:
                self.__analyze_kickoff()
            elif self.state == GameState.PLAYING:
                self.__analyze_playing()
            elif self.state == GameState.GOAL:
                self.__analyze_goal()
            elif self.state == GameState.OVERTIME:
                self.__analyze_overtime()
            elif self.state == GameState.END:
                self.__analyze_end()

    def __set_state(self, state, data = None):
        self.state = state
        dispatcher.send(message=data, signal=state, sender=Sender.STREAM_ANALYZER)

        if state.value in self.config["delays"]:
            time.sleep(self.config["delays"][state.value])

    def __analyze_waiting_for_game(self):
        game_time = self.__read_game_time()
        if game_time:
            if game_time["seconds"] == 300:
                self.game_time = game_time
                self.__set_state(GameState.KICKOFF)

    def __analyze_kickoff(self):
        kickoff_countdown = self.__read_kickoff_countdown()
        if kickoff_countdown != None:
            if kickoff_countdown == 0:
                self.__set_state(GameState.PLAYING)

        # Fallback: If "GO!" can't be detected, check if in game timer decreased (increased in OT)
        game_time = self.__read_game_time()
        if game_time:
            if (not game_time["overtime"] and game_time["seconds"] < self.game_time["seconds"]) or\
                (game_time["overtime"] and game_time["seconds"] > self.game_time["seconds"]):
                self.game_time = game_time
                self.__set_state(GameState.PLAYING)


    def __analyze_playing(self):
        game_time = self.__read_game_time()
        if game_time:
            if game_time["overtime"] and not self.game_time["overtime"]:
                self.__set_state(GameState.OVERTIME)

            self.game_time = game_time

        goals = self.__read_goals()
        if goals:
            if goals["scorer"] != None:
                self.goals = goals

                ot = " in overtime" if self.game_time['overtime'] else ""
                print(f"[{goals['blue']}-{goals['orange']}] {goals['scorer']} scored at {math.floor(self.game_time['seconds'] / 60)}:{self.game_time['seconds'] % 60}{ot}")

                self.__set_state(GameState.GOAL, goals["scorer"])
                
        if self.game_time["seconds"] == 0 and not self.game_time["overtime"]:
            if self.__has_team_won():
                self.__set_state(GameState.END, self.__get_winning_team())

    def __analyze_goal(self):
        if (self.game_time == 0 and self.goals[Team.ORANGE.value] == self.goals[Team.BLUE.value]) and not self.game_time["overtime"]:
            self.__set_state(GameState.OVERTIME)
        elif (self.game_time == 0 and self.goals[Team.ORANGE.value] != self.goals[Team.BLUE.value]) or self.game_time["overtime"]:
            self.__set_state(GameState.END, self.__get_winning_team())
        else:
            self.__set_state(GameState.KICKOFF)

    def __analyze_overtime(self):
        self.__set_state(GameState.KICKOFF)

    def __analyze_end(self):
        self.__reset()
        self.__set_state(GameState.WAITING_FOR_GAME)

    def __read_goals(self):
        goals_blue = self.__read_team_goals(Team.BLUE)
        if goals_blue == None:
            return

        goals_orange = self.__read_team_goals(Team.ORANGE)
        if goals_orange == None:
            return

        scorer = None
        if self.__has_team_scored(Team.BLUE, goals_blue):
            scorer = Team.BLUE
        elif self.__has_team_scored(Team.ORANGE, goals_orange):
            scorer = Team.ORANGE

        return { "blue": goals_blue, "orange": goals_orange, "scorer": scorer }

    def __read_team_goals(self, team):
        goals_text = ImageReader.read_area(self.screenshot, self.config["areas"][f"goals_{team.value}"])
        if goals_text:
            goals = int(goals_text)

            diff = abs(goals - self.goals[team.value])
            if diff <= 1:
                return goals

    def __has_team_scored(self, team, goals):
        diff = goals - self.goals[team.value]
        return diff == 1

    def __has_team_won(self):
        winner_text = ImageReader.read_area(self.screenshot, self.config["areas"]["winner"])
        if winner_text:
            return winner_text == "WINNER"

    def __get_winning_team(self):
        winner = Team.BLUE
        if self.goals[Team.ORANGE.value] > self.goals[Team.BLUE.value]:
            winner = Team.ORANGE

        return winner

    def __read_kickoff_countdown(self):
        text = ImageReader.read_area(self.screenshot, self.config["areas"]["kickoff"])

        match = re.match(r"([123]{1}|GO)(!)?", text)
        if match != None:
            if match[1] == "GO" or match[1] == "GO!":
                return 0
            else:
                return int(match[1])

    def __read_game_time(self):
        text = ImageReader.read_area(self.screenshot, self.config["areas"]["time"])

        if text == "OVERTIME" and not self.game_time["overtime"]:
            return { "seconds": 0, "overtime": True }

        match = re.match(r"[+]?([0-9]):([0-5][0-9])", text)
        if match != None:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            total_seconds = (minutes * 60) + seconds
            overtime = text[0] == "+"

            return { "seconds": total_seconds, "overtime": overtime }

    def __reset(self):
        self.state = None
        self.game_time = { "seconds": 0, "overtime": False }
        self.goals = { "blue": 0, "orange": 0, "scorer": None }
        self.overtime = False
