import colorsys, time, imgui
from math import cos, pi, floor
from re import S
from random import random
from collections import OrderedDict

def to_bool(val):
    try:
        return bool(int(val))
    except:
        return val == "True"

def draw_mouth(order,draw_list,x,y,width,height,color=0x7f000000):
    size = min(width,height)
    if order <= 0 or size < 15:
        return
    elif order == 1:
        draw_list.add_polyline([[x+a*width,y+b*height] for a,b in [
            [.411,.699],
            [.470,.616],
            [.514,.596],
            [.555,.651]]], color, False, size/15)
    elif order == 2:
        draw_list.add_rect_filled(x+(.363)*width,y+(.644)*height,x+(.630)*width,y+(.699)*height, color)
    elif order == 3:
        draw_list.add_polyline([[x+a*width,y+b*height] for a,b in [
            [.4,.6],
            [.5,.7],
            [.6,.6]]], color, False, size/15)
    elif order == 4:
        draw_list.add_polyline([[x+a*width,y+b*height] for a,b in [
            [.4,.640],
            [.6,.707]]], color, False, size/15)
    elif order == 5:
        draw_list.add_circle_filled(x+(.541)*width,y+(.685)*height, size/15, color, num_segments=size//4)
    else:
        draw_list.add_rect_filled(x+(.4)*width,y+(.59)*height,x+(.6)*width,y+(.72)*height, color)

def draw_eyes(draw_list, x, y, width, height, solid, color=0x7f000000, blink_offset=0, order=-1):
    size = min(width,height)
    if size < 15:
        return
    draw_mouth(order,draw_list,x,y,width,height,color)
    if solid:
        #patrick told me (balt) the code behind blinking in dms, thanks to him <3
        if floor(((time.time())*7.12)+blink_offset)%26 == 0:
            draw_list.add_polyline([(x + (1*width)/8, y + (7*height/16)), (x + (3*width)/8, y + (7*height/16))], color, thickness=size/15)
            draw_list.add_polyline([(x + (5*width)/8, y + (7*height/16)), (x + (7*width)/8, y + (7*height/16))], color, thickness=size/15)
        else:
            draw_list.add_circle_filled(x + width/4, y + (7*height/16), size/10, color, num_segments=size//4)
            draw_list.add_circle_filled(x + width*3/4, y + (7*height/16), size/10, color, num_segments=size//4)
    else:
        draw_list.add_circle(x + width/4, y + (7*height/16), size/10, color, num_segments=size//4, thickness=size/20)
        draw_list.add_circle(x + width*3/4, y + (7*height/16), size/10, color, num_segments=size//4, thickness=size/20)

infinity_polyline = [
    (0.65, 0.65), (0.8, 0.65), (0.85, 0.5), (0.8, 0.35), (0.65, 0.35),
    (0.35, 0.65), (0.2, 0.65), (0.15, 0.5), (0.2, 0.35), (0.35, 0.35)
]
def draw_infinity(draw_list, x, y, width, height):
    draw_list.add_polyline([(x + u*width, y + v*height) for u, v in infinity_polyline], 0xffffffff, True, min(width,height)/10)

epsilon_polyline = [
    (0.7, 0.3), (0.4, 0.25), (0.3, 0.35), (0.4, 0.5), (0.6, 0.5)
]
def draw_epsilon(draw_list, x, y, width, height):
    draw_list.add_polyline([(x + u*width, y + v*height) for u, v in epsilon_polyline], 0xffffffff, False, min(width,height)/10)
    draw_list.add_polyline([(x + u*width, y + (1-v)*height) for u, v in epsilon_polyline], 0xffffffff, False, min(width,height)/10)

def half_cos(t):
    t = t % (2*pi)
    if t < pi:
        return (1 + cos(t))/2
    elif t < 1.5*pi:
        return 0
    else:
        return 1

def draw_shine(draw_list, x, y, width, height, rtl):
    t = time.perf_counter() * 2.5
    if (t + 0.5) % (2*pi) < pi + 0.5:
        if rtl:
            draw_list.add_rect_filled(x + half_cos(t)*width, y, x + half_cos(t + 0.5)*width, y + height, 0x7fffffff)
        else:
            draw_list.add_rect_filled(x + (1 - half_cos(t))*width, y, x + (1 - half_cos(t + 0.5))*width, y + height, 0x7fffffff)

special_effects = {
    0: 'None',
    2: 'Right flip effect',
    3: 'Left flip effect',
    8: 'Draw symbol for Inner Push / Extrude / Priority being different than the default',
    11: 'Don\'t show box in ASCII grid mode',
    12: 'Don\'t draw border when in Infinite Exit/Enter void'
}

floor_types = ['None','Button','PlayerButton','FastTravel','Info']

class Block:
    def __init__(self, x, y, id, width, height, hue, sat, val, zoomfactor, fillwithwalls, player, possessable, playerorder, fliph, floatinspace, specialeffect):
        self.x = int(x)
        self.y = int(y)
        self.id = int(id)
        self.width = int(width)
        self.height = int(height)
        self.hue = float(hue)
        self.sat = float(sat)
        self.val = float(val)
        self.zoomfactor = float(zoomfactor)
        self.fillwithwalls = to_bool(fillwithwalls)
        self.player = to_bool(player)
        self.possessable = to_bool(possessable)
        self.playerorder = int(playerorder)
        self.fliph = to_bool(fliph)
        self.floatinspace = to_bool(floatinspace)
        self.specialeffect = int(specialeffect)
        self.blinkoffset = random()*26
        self.parent = None
        self.children = []
        self.window_size = 25

    def __repr__(self):
        return f'<Block of ID {self.id} at ({self.x},{self.y}) inside of {f"<{self.parent.__class__.__name__} of ID {self.parent.id} at ({self.x},{self.y})>" if self.parent is not None else None} with {len(self.children)} children>'

    def copy(self, held=False):
        if self.fillwithwalls: return self.full_copy() # duplicate solid blocks
        if (held or self.parent): # if I already exist somewhere:
            # return ref to self
            return self.make_ref()
        else: # if I don't exist anywhere:
            # no need to copy
            return self

    def full_copy(self, id=None):
        return Block(0, 0, id if id else self.id, self.width, self.height, self.hue, self.sat, self.val, self.zoomfactor, self.fillwithwalls, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect)

    def make_ref(self, new=True):
        return Ref(0 if new else self.x, 0 if new else self.y, self.id, 0 if new else 1, 0, 0, 0, 0, "-1", self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect)
    
    def save(self, indent, saved_blocks):
        if self in saved_blocks and not self.fillwithwalls:
            return self.make_ref(False).save(indent, saved_blocks)
        else:
            saved_blocks.append(self)
        line = ["Block", int(self.x), int(self.y), int(self.id), int(self.width), int(self.height), f"{self.hue:1.3g}", f"{self.sat:1.3g}", f"{self.val:1.3g}", f"{self.zoomfactor:1.3g}", int(self.fillwithwalls), int(self.player), int(self.possessable), int(self.playerorder), int(self.fliph), int(self.floatinspace), int(self.specialeffect)]
        block = "\n" + "\t"*indent + " ".join(str(i) for i in line)
        for child in self.children:
            if 0 <= child.x < self.width and 0 <= child.y < self.height:
                block += child.save(indent + 1, saved_blocks)
            else:
                pass # discard out of bounds children on save
        return block

    def draw_children(self, draw_list, x, y, width, height, level, depth, fliph):
        if self.width > 0 and self.height > 0:
            inner_width = width / self.width
            inner_height = height / self.height
            if min(inner_width,inner_height) < 1 or depth > 10:
                return
            for child in self.children:
                if fliph:
                    child.draw(draw_list, x + (self.width - 1 - child.x) * inner_width, y + (self.height - 1 - child.y) * inner_height, inner_width, inner_height, level, depth + 1, True)
                else:
                    child.draw(draw_list, x + child.x * inner_width, y + (self.height - 1 - child.y) * inner_height, inner_width, inner_height, level, depth + 1, False)
    
    def draw(self, draw_list, x, y, width, height, level, depth, fliph):
        draw_list.add_rect_filled(x, y, x+width, y+height, self.color(level, 1 if self.fillwithwalls else 0.5))
        if depth >= 0: # don't draw outer border on block windows
            draw_list.add_rect(x, y, x+width, y+height, 0xff000000, thickness=min(width,height)/20)

        self.draw_children(draw_list, x, y, width, height, level, depth, fliph ^ self.fliph)

        if self.fliph and depth >= 0:
            draw_shine(draw_list, x, y, width, height, fliph ^ self.fliph)
        if self.specialeffect in [2,3]:
            draw_shine(draw_list, x, y, width, height, self.specialeffect == 3)
        if self.player:
            draw_eyes(draw_list, x, y, width, height, True, blink_offset = self.blinkoffset, order = self.playerorder)
        elif self.possessable:
            draw_eyes(draw_list, x, y, width, height, False)

        if min(width,height) > 15 and depth >= 0:
            draw_list.add_text(x + width/20, y + height/30, 0xffffffff, str(self.id))

    def color(self, level, brightness=1):
        color = Palette.pals[level.metadata["custom_level_palette"]].get_color((self.hue, self.sat, self.val))
        r, g, b = colorsys.hsv_to_rgb(color[0], color[1], color[2] * brightness)
        return imgui.get_color_u32_rgba(r, g, b, 1)

    def get_children(self, x, y):
        children = []
        for child in self.children:
            if child.x == x and child.y == y:
                children.append(child)
        return children

    def get_child(self, x, y):
        # only one child, prioritizes non-floor
        floor = None
        for child in self.children:
            if child.x == x and child.y == y:
                if type(child) == Floor:
                    floor = child
                else:
                    return child
        return floor

    def remove_child(self, child):
        child.parent = None
        self.children.remove(child)
        return child

    def place_child(self, x, y, child):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        if type(child) == Floor:
            self.children.append(child)
        else:
            self.children.insert(0, child)
        child.parent = self
        child.x = x
        child.y = y

    def menu(self, level):
        changed, value = imgui.input_int("ID", self.id)
        if changed:
            delta = value - self.id
            while value in [block.id for block in level.blocks.values()]:
                value += delta
            self.id = value
        changed, value = imgui.input_int("Width", self.width)
        if changed:
            if value != 0:
                self.window_size = (self.window_size/value)*self.width
            self.width = value
        changed, value = imgui.input_int("Height", self.height)
        if changed:
            self.height = max(value,0)
        changed, value = imgui.input_float("Zoom Factor", self.zoomfactor)
        if changed:
            self.zoomfactor = value
        if imgui.begin_menu("Change Block Color"):
            for color in Palette.pals[0].colors:
                h, s, v = Palette.pals[level.metadata["custom_level_palette"]].get_color(color)
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                if imgui.color_button(str(color), r, g, b, 1, width=20, height=20):
                    self.hue = color[0]
                    self.sat = color[1]
                    self.val = color[2]
                imgui.same_line()
            imgui.new_line()
            imgui.separator()

            r, g, b = colorsys.hsv_to_rgb(self.hue, self.sat, self.val)
            changed, (r, g, b) = imgui.color_edit3("Color", r, g, b, imgui.COLOR_EDIT_HSV | imgui.COLOR_EDIT_FLOAT)
            if changed:
                self.hue, self.sat, self.val = colorsys.rgb_to_hsv(r, g, b)
            imgui.end_menu()
        changed, value = imgui.checkbox("Fill With Walls", to_bool(self.fillwithwalls))
        if changed:
            self.fillwithwalls = int(value)
            if value:
                while len(self.children) != 0: #for whatever reason, iterating through self.children stops early, and i gotta do it more than once. :/
                    for child in self.children:
                        self.remove_child(child)
        changed, value = imgui.checkbox("Player", to_bool(self.player))
        if changed:
            self.player = int(value)
        if self.player:
            imgui.indent()
            changed, value = imgui.input_int("Player Order", self.playerorder)
            if changed:
                self.playerorder = value
            imgui.unindent()
        changed, value = imgui.checkbox("Possessable", to_bool(self.possessable))
        if changed:
            self.possessable = int(value)
        changed, value = imgui.checkbox("Flip Horizontally", to_bool(self.fliph))
        if changed:
            self.fliph = int(value)
        changed, value = imgui.checkbox("Float in Space", to_bool(self.floatinspace))
        if changed:
            self.floatinspace = int(value)
        changed, value = imgui.combo("Special Effect", list(special_effects.keys()).index(self.specialeffect), list(special_effects.values()))
        if changed:
            self.specialeffect = list(special_effects.keys())[value]
    
    def palette_menu(self, level):
        self.menu(level)
        imgui.separator()
        if imgui.selectable('Create Clone')[0]:
            return Ref(0,0,self.id,0,0,0,0,0,0,0,0,0,0,0,0)
        if imgui.selectable('Create Infinite Exit')[0]:
            return Ref(0,0,self.id,1,1,0,0,0,0,0,0,0,0,0,0)
        if imgui.selectable('Create Infinite Enter')[0]:
            while level.next_free in level.blocks:
                level.next_free += 1
            level.blocks[level.next_free] = Block(0,0,level.next_free,5,5,self.hue,self.sat,self.val,1,0,0,0,0,0,0,0)
            return Ref(0,0,level.next_free,1,0,0,1,0,self.id,0,0,0,0,0,0)

class Ref:
    def __init__(self, x, y, id, exitblock, infexit, infexitnum, infenter, infenternum, infenterid, player, possessable, playerorder, fliph, floatinspace, specialeffect):
        self.x = int(x)
        self.y = int(y)
        self.id = int(id)
        self.exitblock = to_bool(exitblock)
        self.infexit = to_bool(infexit)
        self.infexitnum = int(infexitnum)
        self.infenter = to_bool(infenter)
        self.infenternum = int(infenternum)
        self.infenterid = int(infenterid)
        self.player = to_bool(player)
        self.possessable = to_bool(possessable)
        self.playerorder = int(playerorder)
        self.fliph = to_bool(fliph)
        self.floatinspace = to_bool(floatinspace)
        self.specialeffect = int(specialeffect)
        self.blinkoffset = random()*26
        self.parent = None

    def __repr__(self):
        return f'<Reference of ID {self.id} at ({self.x},{self.y}) inside of {f"<{self.parent.__class__.__name__} of ID {self.parent.id}>" if self.parent is not None else None}>'

    def copy(self, held=False): # return non-exit copy
        return Ref(0, 0, self.id, 0, self.infexit, self.infexitnum, self.infenter, self.infenternum, self.infenterid, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect)

    def save(self, indent, saved_blocks):
        line = ["Ref", int(self.x), int(self.y), int(self.id), int(self.exitblock), int(self.infexit), int(self.infexitnum), int(self.infenter), int(self.infenternum), int(self.infenterid), int(self.player), int(self.possessable), int(self.playerorder), int(self.fliph), int(self.floatinspace), int(self.specialeffect)]
        return "\n" + "\t"*indent + " ".join(str(i) for i in line)

    def draw(self, draw_list, x, y, width, height, level, depth, fliph):

        if self.id in level.blocks:
            orig = level.blocks[self.id]
            draw_list.add_rect_filled(x, y, x+width, y+height, orig.color(level, 1 if orig.fillwithwalls else 0.5))
            draw_list.add_rect(x, y, x+width, y+height, 0xff000000, thickness=min(width,height)/20)
            orig.draw_children(draw_list, x, y, width, height, level, depth, fliph ^ self.fliph)
        else:
            draw_list.add_text(x + width/20, y + height/30, 0xffffffff, "Invalid Reference!")
            draw_list.add_rect(x, y, x+width, y+height, 0xff000000, thickness=min(width,height)/20)

        if self.infexit:
            draw_list.add_rect_filled(x, y, x + width, y + height, 0x3f000000)
            draw_list.add_rect(x, y, x + width, y + height, 0xff00ffff, thickness=min(width,height)/20)
            if self.infexitnum == 0:
                draw_infinity(draw_list, x, y, width, height)
            else:
                w = width / (self.infexitnum + 1) * 1.8
                h = height / (self.infexitnum + 1)
                h2 = h * 1.8
                for i in range(self.infexitnum + 1):
                    draw_infinity(draw_list, x + width/2 - w/2, y + (h - h2)/2 + i*h, w, h2)
        else:
            if self.infenter:
                w = width / (self.infenternum + 1) * 1.3
                h = height / (self.infenternum + 1)
                h2 = h * 1.3
                for i in range(self.infenternum + 1):
                    draw_epsilon(draw_list, x + width/2 - w/2, y + (h - h2)/2 + i*h, w, h2)
            draw_list.add_rect(x, y, x + width, y + height, 0xff3f3f3f, thickness=min(width,height)/20)
            if not self.exitblock:
                draw_list.add_rect_filled(x, y, x + width, y + height, 0x3fffffff)

        if self.fliph:
            draw_shine(draw_list, x, y, width, height, fliph ^ self.fliph)
        if self.specialeffect in [2,3]:
            draw_shine(draw_list, x, y, width, height, self.specialeffect == 3)
        if self.player:
            draw_eyes(draw_list, x, y, width, height, True, blink_offset = self.blinkoffset, order = self.playerorder)
        elif self.possessable:
            draw_eyes(draw_list, x, y, width, height, False)

        if min(width,height) > 15 and depth >= 0:
            draw_list.add_text(x + width/20, y + height/30, 0xffffffff, str(self.id))

    def menu(self, level):
        changed, value = imgui.input_int("ID", self.id)
        if changed:
            self.id = value

        changed, value = imgui.checkbox("Exit Block", to_bool(self.exitblock))
        if changed:
            self.exitblock = int(value)
        changed, value = imgui.combo("Reference Type", 2 if not (self.infexit or self.infenter) else int(self.infenter), ['Infinite Exit','Infinite Enter','Clone'])
        if changed:
            self.infexit = int(value == 0)
            self.infenter = int(value == 1)
        if self.infexit or self.infenter:
            imgui.indent()
            changed, value = imgui.input_int("Layer", self.infexitnum if self.infexit else self.infenternum)
            if changed:
                if self.infexit:
                    self.infexitnum = max(value,0)
                else:
                    self.infenternum = max(value,0)
            if self.infenter:
                changed, value = imgui.input_int("From ID", self.infenterid)
                if changed:
                    self.infenterid = value
            imgui.unindent()
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
        changed, value = imgui.checkbox("Flip Horizontally", self.fliph)
        if changed:
            self.fliph = value
        changed, value = imgui.checkbox("Float in Space", self.floatinspace)
        if changed:
            self.floatinspace = value
        changed, value = imgui.combo("Special Effect", list(special_effects.keys()).index(self.specialeffect), list(special_effects.values()))
        if changed:
            self.specialeffect = list(special_effects.keys())[value]

class Wall:
    id = None

    def __init__(self, x, y, player, possessable, playerorder):
        self.x = int(x)
        self.y = int(y)
        self.player = int(player)
        self.blinkoffset = random()*26
        self.possessable = to_bool(possessable)
        self.playerorder = to_bool(playerorder)
        self.parent = None

    def __repr__(self):
        return f'<Wall at ({self.x},{self.y}) inside of {self.parent}>'

    def save(self, indent, saved_blocks):
        line = ["Wall", int(self.x), int(self.y), int(self.player), int(self.possessable), int(self.playerorder)]
        return "\n" + "\t"*indent + " ".join(str(i) for i in line)

    def copy(self, held=False):
        return Wall(0, 0, self.player, self.possessable, self.playerorder)
    
    def draw(self, draw_list, x, y, width, height, level, depth, flip):
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

fast_travel_polyline = [
    (0.4, 0.35), (0.5, 0.25), (0.6, 0.35)
]
class Floor:
    id = None

    def __init__(self, x, y, floor_type, extra_data):
        self.x = int(x)
        self.y = int(y)
        self.type = floor_type
        self.floor_index = floor_types.index(floor_type)
        self.extra_data = extra_data
        self.parent = None

    def __repr__(self):
        return f'<Floor of type {self.type} at ({self.x},{self.y}) inside of {self.parent}>'

    def copy(self, held=False):
        return Floor(0, 0, self.type, self.extra_data)

    def save(self, indent, saved_blocks):
        line = ["Floor", int(self.x), int(self.y), self.type]
        if self.extra_data and self.extra_data != "":
            line.append(self.extra_data.replace(" ","_").replace('\n','\\n'))
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

        if border:
            draw_list.add_rect(x + width/10, y + height/10, x + width*9/10, y + height*9/10, color, thickness=min(width,height)/20)

    def menu(self, level):
        changed, value = imgui.combo("Floor Type",self.floor_index,floor_types)
        if changed:
            self.type = floor_types[value]
            self.floor_index = value
        if self.type == "None":
            self.parent.remove_child(self)
        changed, value = imgui.input_text_multiline("Extra Data", self.extra_data, 2048)
        if changed:
            self.extra_data = value
    
    def empty_menu(parent, px, py):
        changed, value = imgui.combo("Floor Type",0,floor_types)
        if changed:
            if floor_types[value] != "None":
                parent.place_child(px, py, Floor(px, py, floor_types[value], ""))

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

class Level:
    def __init__(self, name, data):
        self.name = name
        self.roots = []
        self.blocks = {}
        self.next_free = 0
        [metadata, data] = data.split("\n#\n")

        metadata = [e.split(" ", 1) for e in metadata.split("\n")]
        self.metadata = {e[0]: e[1] for e in metadata}
        if not "attempt_order" in self.metadata: self.metadata["attempt_order"] = "push,enter,eat,possess"
        read_metadata = self.metadata["attempt_order"].split(",")
        self.metadata["attempt_order"] = [[a,True] for a in read_metadata]
        self.metadata["attempt_order"].extend([[a,False] for a in ['push','enter','eat','possess'] if a not in read_metadata])
        self.metadata["shed"] = "shed" in self.metadata and self.metadata["shed"] == "1"
        self.metadata["inner_push"] = "inner_push" in self.metadata and self.metadata["inner_push"] == "1"
        if not "draw_style" in self.metadata: self.metadata["draw_style"] = "normal"
        self.metadata["custom_level_music"] = -1 if "custom_level_music" not in self.metadata else int(self.metadata["custom_level_music"])
        self.metadata["custom_level_palette"] = -1 if "custom_level_palette" not in self.metadata else int(self.metadata["custom_level_palette"])

        data = data.split("\n")
        indent = 0
        last_block = None
        parent = None
        ref_exits = {}
        for line in data:
            trimmed = line.replace("\t","")
            last_indent = indent
            indent = len(line) - len(trimmed)
            if indent == last_indent:
                pass
            elif indent == 0:
                parent = None
            elif indent > last_indent:
                if type(last_block) == Block:
                    parent = last_block
                else:
                    raise "Error parsing level: Indent after non-Block"
            elif indent < last_indent:
                for _ in range(last_indent - indent):
                    parent = parent.parent

            args = trimmed.split(" ")
            block_type = args.pop(0)
            if block_type == "Block":
                [x, y, id, width, height, hue, sat, val, zoomfactor, fillwithwalls, player, possessable, playerorder, fliph, floatinspace, specialeffect, *_] = args
                block = Block(x, y, id, width, height, hue, sat, val, zoomfactor, fillwithwalls, player, possessable, playerorder, fliph, floatinspace, specialeffect)
                block.parent = parent
                if parent:
                    parent.place_child(int(x), int(y), block)
                else:
                    self.roots.append(block)
                last_block = block
                if fillwithwalls != "1":
                    if not int(id) in self.blocks:
                        self.blocks[int(id)] = block
                    else:
                        print("duplicate block with id " + id)
            elif block_type == "Ref":
                [x, y, id, exitblock, infexit, infexitnum, infenter, infenternum, infenterid, player, possessable, playerorder, fliph, floatinspace, specialeffect, *_] = args
                ref = Ref(x, y, id, exitblock, infexit, infexitnum, infenter, infenternum, infenterid, player, possessable, playerorder, fliph, floatinspace, specialeffect)
                if int(exitblock) and not int(infenter):
                    ref_exits[int(id)] = ref
                if parent:
                    parent.place_child(int(x), int(y), ref)
                else:
                    self.roots.append(ref)
                last_block = ref
            elif block_type == "Wall":
                [x, y, player, possessable, playerorder, *_] = args
                wall = Wall(x, y, player, possessable, playerorder)
                if parent:
                    parent.place_child(int(x), int(y), wall)
                else:
                    print("Discarding wall at root level")
                last_block = wall
            elif block_type == "Floor":
                [x, y, floor_type, *rest] = args
                floor = Floor(x, y, floor_type, " ".join(rest))
                if parent:
                    parent.place_child(int(x), int(y), floor)
                else:
                    print("Discarding floor at root level")
                last_block = floor
                
            else:
                pass
        
        # replace exitable refs with original blocks
        for id, ref in ref_exits.items():
            parent = ref.parent
            if parent is not None:
                parent.remove_child(ref)
                parent.place_child(ref.x, ref.y, self.blocks[id])

    def save(self):
        data = "version 4\n"
        if ",".join([a[0] for a in self.metadata["attempt_order"]]) != "push,enter,eat,possess" or not all([a[1] for a in self.metadata["attempt_order"]]):
            data += "attempt_order " + ",".join([a[0] for a in self.metadata["attempt_order"] if a[1]]) + "\n"
        if self.metadata["shed"]:
            data += "shed 1\n"
        if self.metadata["inner_push"]:
            data += "inner_push 1\n"
        if self.metadata["draw_style"] != "normal":
            data += "draw_style " + self.metadata["draw_style"] + "\n"
        if self.metadata["custom_level_music"] != -1:
            data += "custom_level_music " + str(self.metadata["custom_level_music"]) + "\n"
        if self.metadata["custom_level_palette"] != -1:
            data += "custom_level_palette " + str(self.metadata["custom_level_palette"]) + "\n"

        data += "#\n"
        to_save = list(self.blocks.values())
        saved_blocks = []
        seen = []
        while len(to_save):
            current = to_save[0]
            seen.append(current)
            while current.parent and not (current.parent in seen):
                current = current.parent
                seen.append(current)
            data += current.save(0, saved_blocks)
            for block in saved_blocks:
                if block in to_save:
                    to_save.remove(block)

        return data

    def edit_menu(self):
        changed, value = imgui.combo("Palette", self.metadata["custom_level_palette"] + 1, [p.name for p in Palette.pals.values()])
        if changed:
            self.metadata["custom_level_palette"] = value - 1 # off by 1 for None (-1)
        changed, value = imgui.combo("Music", self.metadata["custom_level_music"] + 1, ["None", "Intro", "Enter", "Empty", "Eat", "Reference", "Center", "Clone", "Transfer", "Open", "Flip", "Cycle", "Swap", "Player", "Possess", "Wall", "Infinite Exit", "Infinite Enter", "Multi Infinite", "Reception", "Appendix", "Pause (buggy)", "Credits"])
        if changed:
            self.metadata["custom_level_music"] = value - 1 # off by 1 for None (-1)

        style = 0
        if self.metadata["draw_style"] == "tui": style = 1
        if self.metadata["draw_style"] == "grid": style = 2
        if self.metadata["draw_style"] == "oldstyle": style = 3
        changed, value = imgui.combo("Draw Style", style, ["Normal", "ASCII", "Grid", "Dev Graphics (Gallery)"])
        if changed:
            if value == 0: self.metadata["draw_style"] = "normal"
            if value == 1: self.metadata["draw_style"] = "tui"
            if value == 2: self.metadata["draw_style"] = "grid"
            if value == 3: self.metadata["draw_style"] = "oldstyle"

        imgui.separator()

        changed, value = imgui.checkbox("Extrude / Shed", self.metadata["shed"])
        if changed:
            self.metadata["shed"] = value
        changed, value = imgui.checkbox("Inner Push", self.metadata["inner_push"])
        if changed:
            self.metadata["inner_push"] = value
        if imgui.begin_menu("Priority / Attempt Order"):
            excluded = {}
            order = self.metadata["attempt_order"]
            for i, item in enumerate(order):
                if not item[1]:
                    excluded[i] = item[0]
                    continue
                item = item[0]
                if imgui.arrow_button(item + "-u", imgui.DIRECTION_UP) and i != 0:
                    order[i], order[i-1] = order[i-1], order[i]
                imgui.same_line()
                if imgui.arrow_button(item + "-d", imgui.DIRECTION_DOWN) and i != len(order) - 1:
                    order[i], order[i+1] = order[i+1], order[i]
                imgui.same_line()
                if imgui.checkbox(item,order[i][1])[0]:
                    order[i][1] = False
            if len(excluded) not in [0,4]:
                imgui.separator()
            for i, item in excluded.items():
                if imgui.checkbox(item,order[i][1])[0]:
                    order[i][1] = True
            imgui.end_menu()