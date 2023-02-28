class UIstate:
    focused = False
class Design:
    thick = 200
    grid = False
    gridstyle = (0,0,0,.2)
    gridwidth = 1
    placedebug = False
    true_dupe = False
    hub = False
class UsefulMod:
    def __init__(self):
        self.warn = False
        # Do not modify directly. Call self.enable or self.disable.
        self.enabled = False
        self.purge = False
    def enable(self, floor_types, state=True):
        self.enabled = state
        if state:
            for tag in ["Buttont", "PlayerButtont"]:
                if tag not in floor_types:
                    floor_types.append(tag)
        else:
            for tag in ["Buttont", "PlayerButtont"]:
                floor_types.remove(tag)
    def disable(self, floor_types, state=True):
        self.enabled = not state
        if state:
            for tag in ["Buttont", "PlayerButtont"]:
                floor_types.remove(tag)
        else:
            for tag in ["Buttont", "PlayerButtont"]:
                if tag not in floor_types:
                    floor_types.append(tag)
usefulmod = UsefulMod()