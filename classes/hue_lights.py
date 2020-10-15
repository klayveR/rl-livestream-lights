from phue import Bridge

class HueLights():
    def __init__(self, ip):
        self.bridge = Bridge(ip)
        self.lights = self.bridge.get_light_objects("id")
        self.light_states = self.get_light_states()

    def get_light_states(self, light_ids = None):
        states = {}

        if light_ids != None:
            for id in light_ids:
                state = self.get_light_state(id)
                if state != None:
                    states[id] = state
        else:
            for id, light in self.lights.items():
                state = self.get_light_state(id)
                if state != None:
                    states[id] = state

        return states

    def get_light_state(self, id, include_brightness = True):
        state = {}
        if self.lights[id].colormode == "ct":
            state = {
                "bri": self.lights[id].brightness,
                "ct": self.lights[id].colortemp
            }
        elif self.lights[id].colormode == "xy":
            state = {
                "bri": self.lights[id].brightness,
                "xy": self.lights[id].xy,
            }
        elif self.lights[id].colormode == "hs":
            state = {
                "bri": self.lights[id].brightness,
                "hue": self.lights[id].hue,
                "sat": self.lights[id].saturation,
            }

        if not include_brightness:
            state.pop("bri", None)

        return state
    
    def transition(self, light_ids, preset, speed = 3, brightness = None):
        preset["transitiontime"] = speed
        preset["on"] = True

        if brightness:
            preset["bri"] = brightness

        self.bridge.set_light(light_ids, preset)

    def restore(self):
        for id, state in self.light_states.items():
            self.transition(id, state, speed=10)

    def flash_cycle(self, light_ids, preset, preset_after, brightness = 254, brightness_after = 254, cycles = 3, intensity = 0.8):
        self.darken(light_ids, speed=0, percentage=1)

        for x in range(0, cycles):
            for id in light_ids:
                self.transition(id, preset, speed=0, brightness=brightness)
                self.darken(id, speed=1, percentage=intensity, brightness=brightness)

        self.transition(light_ids, preset_after, speed=10, brightness=brightness_after)

    def flash(self, light_ids, preset, preset_after, brightness = 254, brightness_after = 254, cycles = 3, intensity = 0.8):
        self.darken(light_ids, speed=0, percentage=1)

        for x in range(0, cycles):
            self.transition(light_ids, preset, speed=3, brightness=brightness)
            self.darken(light_ids, speed=1, percentage=intensity, brightness=brightness)

        self.transition(light_ids, preset_after, speed=10, brightness=brightness_after)

    def darken(self, light_ids, speed = 3, percentage = 1, brightness = 254):
        cmd = {
            "bri": round(brightness - (brightness * percentage)),
            "transitiontime": speed
        }

        self.bridge.set_light(light_ids, cmd)


