import time
import imgui
from .walls import Wall
from .utils import floor_types, draw_eyes
fast_travel_polyline = [
    (0.4, 0.35), (0.5, 0.25), (0.6, 0.35)
]
class Floor:
    id = None

    def __init__(self, x, y, floor_type, extra_data):
        self.x = int(x)
        self.y = int(y)
        self.type = floor_type
        try:
            self.floor_index = floor_types.index(floor_type)
        except ValueError:
            self.floor_index = -1
        self.extra_data = extra_data
        self.parent = None

    def __repr__(self):
        return f'<Floor of type {self.type} at ({self.x},{self.y}) inside of {self.parent}>'

    def copy(self, level, held=False):
        return Floor(0, 0, self.type, self.extra_data)

    def save(self, level, indent, saved_blocks):
        line = ["Floor", int(self.x), int(self.y), self.type]
        if self.extra_data and self.extra_data != "":
            line.append(str(self.extra_data).replace(" ","_").replace('\n','\\n'))
        return "\n" + "\t"*indent + " ".join(str(i) for i in line)

    def draw(self, draw_list, x, y, width, height, level, depth, flip):
        border = True
        color = self.parent.color(level) if self.parent else 0x7fffffff

        if self.type == "PlayerButton":
            draw_eyes(draw_list, x + width/10, y + height/10, width * 8/10, height * 8/10, True, color, blink_offset = ((time.time())*-7.12+1))
            other = self.parent.get_child(self.x, self.y) if self.parent else None
            if other and type(other) != Floor and other.player:
                draw_list.add_rect(x, y, x+width, y+height, 0xffffffff, thickness=min(width,height)/20)
        elif self.type == "Button":
            other = self.parent.get_child(self.x, self.y) if self.parent else None
            if other and type(other) != Floor and type(other) != Wall and not other.player:
                draw_list.add_rect(x, y, x+width, y+height, 0xffffffff, thickness=min(width,height)/20)
        elif self.type == "FastTravel":
            border = False
            draw_list.add_polyline([(x + u*width, y + v*height) for u, v in fast_travel_polyline], color, closed=True, thickness=min(width,height)/7)
            draw_list.add_polyline([(x + u*width, y + (1-v)*height) for u, v in fast_travel_polyline], color, closed=True, thickness=min(width,height)/7)
        elif self.type == "Info":
            draw_list.add_rect_filled(x + 0.45*width, y + 0.45*height, x + 0.55*width, y + 0.8*height, color)
            draw_list.add_circle_filled(x + 0.5*width, y + 0.3*height, min(width,height)/15, color)
        elif self.type == "Portal":
            draw_list.add_rect_filled(x + 0.3*width, y + 0.2*height, x + 0.4*width, y + 0.8*height, color)
            draw_list.add_rect_filled(x + 0.3*width, y + 0.8*height, x + 0.7*width, y + 0.7*height, color)
        # UsefulMod (Always Enabled Internal)
        elif self.type == "PlayerButtont":
            color = 0x7f0000ff
            draw_eyes(draw_list, x + width/10, y + height/10, width * 8/10, height * 8/10, True, color, blink_offset = ((time.time())*-7.12+1))
            other = self.parent.get_child(self.x, self.y) if self.parent else None
            if other and type(other) != Floor and other.player:
                draw_list.add_rect(x, y, x+width, y+height, 0x7f0000ff, thickness=min(width,height)/20)
        elif self.type == "Buttont":
            color = 0x7f0000ff
        if border:
            draw_list.add_rect(x + width/10, y + height/10, x + width*9/10, y + height*9/10, color, thickness=min(width,height)/20)

    def menu(self, level):
        changed, value = imgui.combo("Floor Type",self.floor_index,floor_types)
        if changed:
            self.type = floor_types[value]
            self.floor_index = value
        if self.type == "None":
            self.parent.remove_child(self)
        if self.type == 'Info':
            changed, value = imgui.input_text_multiline("Info Text", self.extra_data, 2048)
            if changed:
                self.extra_data = value
        elif self.type == 'Portal':
            if not level.is_hub:
                imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.2, 0.2)
                imgui.text('Non-hub levels will not load if they have a Portal floor in them!')
                imgui.pop_style_color(1)
            else:
                changed, value = imgui.input_text("Level Name", str(self.extra_data), 256)
            if changed:
                self.extra_data = value
    def empty_menu(level, parent, px, py):
        changed, value = imgui.combo("Floor Type",0,floor_types)
        if changed:
            if floor_types[value] != "None":
                parent.place_child(px, py, Floor(px, py, floor_types[value], ""))