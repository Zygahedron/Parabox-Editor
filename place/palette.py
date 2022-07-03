from collections import OrderedDict
class Palette:
    def __init__(self, name, colors):
        self.name = name
        self.colors = colors

    def get_color(self, color):
        if self.colors == None: return color
        if color[1] == 0: return self.colors[0]
        if color[0] == 0.6: return self.colors[1]
        if color[0] == 0.4: return self.colors[2]
        if color[0] == 0.1: return self.colors[3]
        if color[0] == 0.9: return self.colors[4]
        if color[0] == 0.55: return self.colors[5]
        return color

Palette.pals = OrderedDict({
    -1: Palette("None", None),
    0: Palette("Default", [(0.0, 0.0, 0.8), (0.6, 0.8, 1.0), (0.4, 0.8, 1.0), (0.1, 0.8, 1.0), (0.9, 1.0, 0.7), (0.55, 0.8, 1.0),]),
    1: Palette("Eat", [(0.05, 0.6, 1.1), (0.63, 0.6, 1.0), (0.32, 0.55, 1.0), (0.12, 0.6, 1.0), (0.85, 0.53, 0.8), (0.55, 0.8, 1.0),]),
    2: Palette("Enter", [(0.6, 0.3, 0.8), (0.07, 0.7, 0.9), (0.42, 0.8, 0.85), (0.55, 0.8, 0.85), (0.93, 0.7, 0.75), (0.55, 0.8, 1.0),]),
    3: Palette("Cycle", [(0.68, 0.2, 0.6), (0.25, 0.7, 0.6), (0.13, 0.7, 0.8), (0.03, 0.7, 0.8), (0.73, 0.7, 0.82), (0.55, 0.8, 1.0),]),
    4: Palette("Empty", [(0.0, 0.08, 0.7), (0.6, 0.55, 0.8), (0.08, 0.75, 0.95), (0.21, 0.7, 0.8), (0.04, 0.8, 0.85), (0.55, 0.8, 1.0),]),
    5: Palette("Monochrome", [(0.0, 0.0, 0.5), (0.0, 0.0, 0.25), (0.0, 0.0, 0.85), (0.0, 0.0, 0.5), (0.0, 0.0, 0.5), (0.0, 0.0, 0.5),]),
    6: Palette("Reference", [(0.6, 0.6, 0.8), (0.55, 0.75, 0.7), (0.45, 0.75, 0.75), (0.13, 0.75, 0.85), (0.0, 0.7, 0.7), (0.55, 0.8, 1.0),]),
    7: Palette("Clone", [(0.6, 0.3, 0.75), (0.25, 0.83, 0.82), (0.16, 1.0, 0.75), (0.6, 0.7, 0.9), (0.96, 0.8, 0.7), (0.46, 0.7, 0.8),]),
    8: Palette("Flip", [(0.64, 0.6, 0.85), (0.68, 0.55, 0.9), (0.95, 0.6, 0.7), (0.45, 0.55, 0.8), (0.85, 0.6, 0.75), (0.58, 0.7, 0.8),]),
    9: Palette("Possess", [(0.13, 0.15, 0.7), (0.92, 1.0, 0.7), (0.22, 0.9, 0.8), (0.5, 0.7, 0.8), (0.8, 0.5, 0.85), (0.09, 0.9, 0.9),]),
    10: Palette("Camo", [(0.23, 0.6, 0.4), (0.33, 0.6, 0.6), (0.15, 0.8, 0.8), (0.1, 0.8, 0.8), (0.62, 0.7, 0.8), (0.46, 0.7, 0.8),]),
})