from classes.config import Config
from classes.dialog import Dialog
from classes.hue_lights import HueLights
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

    def __select_lights(self, bridge):
        lights = bridge.get_light_objects('id')
        lights_names = []

        for i in lights:
            lights_names.append(lights[i].name)

        selection = Dialog.ask_for_list_item(lights_names, f"Please select the lights you'd like to use (comma-seperated list)",\
            allow_multiple=True, allow_none=False)

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
            self.config["hue"]["lights"] = self.__select_lights(bridge)

            custom_colors = Dialog.ask_yes_no(f"Would you like to use custom light colors?")
            if custom_colors:
                hue_lights = HueLights(self.config["hue"]["ip"])
                setup_light_id = self.config["hue"]["lights"][0]
                setup_light = hue_lights.lights[setup_light_id]
                Dialog.ask_confirmation(f"Please set your '{setup_light.name}' light to the color you want while playing")
                self.config["hue"]["presets"]["white"] = hue_lights.get_light_state(setup_light_id, include_brightness=False)
                Dialog.ask_confirmation(f"Please set your '{setup_light.name}' light to the color you want when blue scores")
                self.config["hue"]["presets"]["blue"] = hue_lights.get_light_state(setup_light_id, include_brightness=False)
                Dialog.ask_confirmation(f"Please set your '{setup_light.name}' light to the color you want when orange scores")
                self.config["hue"]["presets"]["orange"] = hue_lights.get_light_state(setup_light_id, include_brightness=False)

            custom_brightness = Dialog.ask_yes_no(f"Would you like to use custom light brightness?")
            if custom_brightness:
                self.config["hue"]["brightness"]["kickoff"] = Dialog.ask_number_in_range\
                    ("How bright should the lights be during kickoff? (Default: 160)", 0, 254)
                self.config["hue"]["brightness"]["playing"] = Dialog.ask_number_in_range\
                    ("How bright should the lights be while playing? (Default: 80)", 0, 254)
                self.config["hue"]["brightness"]["goal"] = Dialog.ask_number_in_range\
                    ("How bright should the lights be when a goal is scored? (Default: 254)", 0, 254)
                self.config["hue"]["brightness"]["end"] = Dialog.ask_number_in_range\
                    ("How bright should the lights be at the end of the match? (Default: 254)", 0, 254)

            flash_modes = ["No flashing", "All lights flash simultaneously", "Lights flash individually one after another"]
            self.config["hue"]["flash"]["mode"] = Dialog.ask_for_list_item(flash_modes,\
                "Please select the flash mode that should be used when a goal is scored (Default: 2):")

            if self.config["hue"]["flash"]["mode"] != 0:
                self.config["hue"]["flash"]["cycles"] = Dialog.ask_number_in_range\
                    ("How many times should each light flash? (Default: 3)", 0, 10)
                intensity = Dialog.ask_number_in_range("How intense should the flashing be? (Default: 70)", 0, 100)
                self.config["hue"]["flash"]["intensity"] = intensity / 100

            Config.save(self.config)

            return True

        return False

        
