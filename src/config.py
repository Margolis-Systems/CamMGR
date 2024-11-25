import json


class Cameras:
    def __init__(self, name, cam_id):
        self.name = name
        self.id = cam_id


cameras = []
with open('src/config.json', 'r') as file:
    cnfg = json.loads(file.read())
for c in cnfg:
    cameras.append(Cameras(c['name'], c['id']))
