import json

class Config:
    @staticmethod
    def read():
        with open("config.json") as f:
            return(json.load(f))

    @staticmethod
    def save(data):
        with open("config.json", "w") as f:
            json.dump(data, f, indent=4)