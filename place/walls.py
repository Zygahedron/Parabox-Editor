from random import random
import imgui
from .utils import to_bool, draw_eyes

class Wall:
    id = None

    def __init__(self, x, y, player, possessable, playerorder, condition = None):
        self.x = int(x)
        self.y = int(y)
        self.player = int(player)
        self.blinkoffset = random()*26
        self.possessable = to_bool(possessable)
        self.playerorder = to_bool(playerorder)
        self.parent = None
        self.condition = condition

    def __repr__(self):
        return f'<Wall at ({self.x},{self.y}) inside of {self.parent}>'

    def save(self, level, indent, saved_blocks):
        line = ["Wall", int(self.x), int(self.y), int(self.player), int(self.possessable), int(self.playerorder), ('' if self.condition is None else self.condition)]
        return "\n" + "\t"*indent + " ".join(str(i) for i in line)

    def copy(self, level, held=False):
        return Wall(0, 0, self.player, self.possessable, self.playerorder, self.condition)
    
    def draw(self, draw_list, x, y, width, height, level, depth, flip):
        self.parent = self.parent if type(self.parent) is not tuple else self.parent[0]
        left = not self.parent or self.x != 0 and type(self.parent.get_child(self.x - 1, self.y)) != Wall
        right = not self.parent or self.x != self.parent.width-1 and type(self.parent.get_child(self.x + 1, self.y)) != Wall
        top = not self.parent or self.y != self.parent.height-1 and type(self.parent.get_child(self.x, self.y + 1)) != Wall
        bottom = not self.parent or self.y != 0 and type(self.parent.get_child(self.x, self.y - 1)) != Wall
        topleft = not self.parent or ((self.x != 0 and  self.y != self.parent.height-1) and type(self.parent.get_child(self.x - 1, self.y + 1)) != Wall)
        topright = not self.parent or ((self.x != self.parent.width-1 and self.y != self.parent.height-1) and type(self.parent.get_child(self.x + 1, self.y + 1)) != Wall)
        bottomleft = not self.parent or ((self.x != 0 and self.y != 0) and type(self.parent.get_child(self.x - 1, self.y - 1)) != Wall)
        bottomright = not self.parent or ((self.x != self.parent.width-1 and self.y != 0) and type(self.parent.get_child(self.x + 1, self.y - 1)) != Wall)
        top_and_left = 1 if top and left else 0
        top_and_right = 2 if top and right else 0
        bottom_and_left = 4 if bottom and left else 0
        bottom_and_right = 8 if bottom and right else 0
        if self.parent is not None and flip:
            x += width
            width *= -1
        draw_list.add_rect_filled(x, y, x + width, y + height, self.parent.color(level) if self.parent else 0xff7f7f7f, min(width, height)/4, top_and_left | top_and_right | bottom_and_left | bottom_and_right)
        if left:
            draw_list.add_rect_filled(x, y, x + width/5, y + height, self.parent.color(level, 1.25) if self.parent else 0xffbfbfbf, min(width, height)/4, top_and_left | bottom_and_left)
        if right:
            draw_list.add_rect_filled(x + width*4/5, y, x + width, y + height, self.parent.color(level, 0.75) if self.parent else 0xff3f3f3f, min(width, height)/4, top_and_right | bottom_and_right)
        if top:
            draw_list.add_rect_filled(x, y, x + width, y + height/5, self.parent.color(level, 1.25) if self.parent else 0xffbfbfbf, min(width, height)/4, top_and_left | top_and_right)
        if bottom:
            draw_list.add_rect_filled(x, y + height*4/5, x + width, y + height, self.parent.color(level, 0.75) if self.parent else 0xff3f3f3f, min(width, height)/4, bottom_and_left | bottom_and_right)
        if topleft and not (top or left):
            draw_list.add_rect_filled(x, y, x + width/5, y + height/5, self.parent.color(level, 1.25) if self.parent else 0xffbfbfbf, min(width, height)/4, top_and_left)
        if topright and not (top or right):
            draw_list.add_rect_filled(x + width*4/5, y, x + width, y + height/5, self.parent.color(level, 1.25) if self.parent else 0xff3f3f3f, min(width, height)/4, top_and_right)
        if bottomleft and not (bottom or left):
            draw_list.add_rect_filled(x, y + height*4/5, x + width/5, y + height, self.parent.color(level, 1.25) if self.parent else 0xffbfbfbf, min(width, height)/4, bottom_and_left)
        if bottomright and not (bottom or right):
            draw_list.add_rect_filled(x + width*4/5, y + height*4/5, x + width, y + height, self.parent.color(level, 0.75) if self.parent else 0xff3f3f3f, min(width, height)/4, bottom_and_right)
        if self.player:
            draw_eyes(draw_list, x, y, width, height, True, blink_offset = self.blinkoffset, order = self.playerorder)
        elif self.possessable:
            draw_eyes(draw_list, x, y, width, height, False)
    def menu(self, level):
        changed, value = imgui.checkbox("Player", self.player)
        if changed:
            self.player = value
        if self.player:
            imgui.indent()
            changed, value = imgui.input_int("Player Order", self.playerorder)
            if changed:
                self.playerorder = value
            imgui.unindent()
        changed, value = imgui.checkbox("Possessable", self.possessable)
        if changed:
            self.possessable = value
        if level.is_hub:
            self.condition = self.condition if self.condition is not None else '_'
            imgui.separator()
            changed, value = imgui.input_text("Removal Condition", self.condition, 256)
            if changed:
                self.condition = value if value != '_' else None
            if imgui.core.is_item_hovered():
                imgui.begin_tooltip()
                imgui.text('After what level should this wall be removed?')
                imgui.text('None: "_"')
                imgui.end_tooltip()
        else:
            self.condition = self.condition if self.condition != '_' else None
