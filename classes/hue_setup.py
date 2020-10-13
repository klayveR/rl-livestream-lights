from classes.config import Config
from classes.dialog import Dialog
from enums.game_state import GameState
from phue import Bridge
import requests

class HueSetup:
    def __init__(self, config):
        self.config = config

    def __get_bridges(self):
        bridges = []
        response = requests.get('https://discovery.meethue.com')
        if response and response.status_code == 200:
            res = response.json()
            
            for i in range(len(res)):
                if "id" in res[i] and "internalipaddress" in res[i]:
                    bridges.append(res[i]["internalipaddress"])

        return bridges

    def __select_lights(self, bridge, state):
        lights = bridge.get_light_objects('id')
        lights_names = []

        for i in lights:
            lights_names.append(lights[i].name)

        selection = Dialog.ask_for_list_item(lights_names, f"Please select the lights you'd like to use for the {state} event (comma-seperated list)",\
            allow_multiple=True, allow_none=True)

        index = 0
        selected_lights = []
        for i in lights:
            if index in selection:
                selected_lights.append(i)
            index += 1

        return selected_lights

    def __select_bridge(self, previous_ip = ""):
        if previous_ip != "":
            try:
                bridge = Bridge(previous_ip)
                bridge.connect()

                keep = Dialog.ask_yes_no(f"Would you like to keep using the Philips hue bridge you used before (IP address: {previous_ip})?")
                if keep:
                    return bridge
            except:
                pass

        print("Discovering Philips hue bridges in your current network...")
        bridges = self.__get_bridges()
        index = 0

        if len(bridges) == 0:
            print("Failed to discover a Philips hue bridge. Either bridge isn't connected to your current network or the request failed")
            return
        elif len(bridges) == 1:
            print(f"Philips hue bridge discovered (IP address: {bridges[index]})")
        else:
            index = Dialog.ask_for_list_item(bridges, "Multiple Philips hue bridges discovered. Please select the Philips hue bridge you'd like to use:")
            
        ip = bridges[index]
        
        successful_connection = False
        while not successful_connection:
            try:
                bridge = Bridge(ip)
                bridge.connect()
                self.config["hue"]["ip"] = ip
    
                print(f"Successfully connected to Philips hue bridge (IP address: {ip})")
                successful_connection = True

                return bridge
            except Exception as e:
                print(f"Failed to connect to bridge: {e}")
                Dialog.ask_confirmation("Please press the link button on the selected Philips hue bridge and continue")

    def is_setup_needed(self):
        return self.config["hue"]["ip"] == ""

    def start(self):
        bridge = self.__select_bridge(self.config["hue"]["ip"])
        if bridge:
            self.config["hue"]["ip"] = bridge.ip
            self.config["hue"]["lights"][GameState.IDLE.value] = self.__select_lights(bridge, GameState.IDLE.value)
            self.config["hue"]["lights"][GameState.KICKOFF.value] = self.__select_lights(bridge, GameState.KICKOFF.value)
            self.config["hue"]["lights"][GameState.PLAYING.value] = self.__select_lights(bridge, GameState.PLAYING.value)
            self.config["hue"]["lights"][GameState.GOAL.value] = self.__select_lights(bridge, GameState.GOAL.value)
            self.config["hue"]["lights"][GameState.END.value] = self.__select_lights(bridge, GameState.END.value)
            Config.save(self.config)

            return True

        return False

        
