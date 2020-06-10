import json, os

class HazedumperError(BaseException):
    pass

offsets = {}
try:
    offsets = json.loads(open("csgo.json", "r").read())
except:
    raise HazedumperError("Failed to load csgo.json, make sure to run hazedumper in the directory \"%s\"" % os.getcwd())