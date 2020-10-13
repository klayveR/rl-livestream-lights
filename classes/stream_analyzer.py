from enums.game_state import GameState
from enums.team import Team
from classes.image_reader import ImageReader
import re
import time

class StreamAnalyzer():
    def __init__(self, config, window_title):
        self.config = config
        self.window_title = window_title
        self.screenshot = None
        self.running = False
        self.__reset()

    def start(self):
        if not self.running:
            self.running = True
            self.__monitor()

    def stop(self):
        if self.running:
            self.running = False

    def __set_state(self, state, data = None):
        print(f"Setting state to {state}, data: {data}")
        self.state = state

        if state.value in self.config["delays"]:
            time.sleep(self.config["delays"][state.value])

    def __monitor(self):
        self.__set_state(GameState.IDLE)

        while True:
            if not self.running:
                break

            self.screenshot = ImageReader.screenshot(self.window_title)

            if self.screenshot == None:
                continue

            if self.state == GameState.IDLE:
                self.__monitor_idle()
            elif self.state == GameState.KICKOFF:
                self.__monitor_kickoff()
            elif self.state == GameState.PLAYING:
                self.__monitor_playing()
            elif self.state == GameState.GOAL:
                self.__monitor_goal()
            elif self.state == GameState.REPLAY:
                self.__monitor_replay()
            elif self.state == GameState.END:
                self.__monitor_end()

    def __monitor_idle(self):
        game_time = self.__read_game_time()
        if game_time:
            if game_time["seconds"] == 300:
                self.game_time = game_time
                self.__set_state(GameState.KICKOFF)

    def __monitor_kickoff(self):
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


    def __monitor_playing(self):
        game_time = self.__read_game_time()
        if game_time:
            self.game_time = game_time

        goals = self.__read_goals()
        if goals:
            if goals["scorer"] != None:
                self.goals = goals
                self.__set_state(GameState.GOAL, goals["scorer"])

        if self.game_time["seconds"] == 0 and not self.game_time["overtime"]:
            if self.__has_team_won():
                self.__set_state(GameState.END, self.__get_winning_team())

    def __monitor_goal(self):
        if (self.game_time == 0 and self.goals[Team.ORANGE.value] != self.goals[Team.BLUE.value]) or self.game_time["overtime"]:
            self.__set_state(GameState.END, self.__get_winning_team())
        else:
            self.__set_state(GameState.KICKOFF)

    def __monitor_end(self):
        self.__set_state(GameState.IDLE)

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

        match = re.match(r"([123]{1}|GO)", text)
        if match != None:
            if match[1] == "GO":
                return 0
            else:
                return int(match[1])

    def __read_game_time(self):
        text = ImageReader.read_area(self.screenshot, self.config["areas"]["time"])
        match = re.match(r"[+]?([0-9]):([0-5][0-9])", text)
        if match != None:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            total_seconds = (minutes * 60) + seconds
            overtime = text[0] == "+"

            return { "seconds": total_seconds, "overtime": overtime }

    def __reset(self):
        self.state = None
        self.time = { "seconds": 0, "overtime": False }
        self.goals = { "blue": 0, "orange": 0, "scorer": None }
        self.overtime = False
