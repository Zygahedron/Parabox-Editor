import imgui, colorsys
from place.walls import Wall
from .utils import to_bool, draw_epsilon, draw_shine, draw_eyes, draw_weight, draw_pin, useful_change, special_effects, inbounds
from state import Design, UIstate, usefulmod
from .palette import Palette
from .ref import Ref
from .floor import Floor
from random import random
import math
from usefull.keywords import savekeys, umenu
class Block:
    def __init__(self, level, x, y, id, width, height, hue, sat, val, zoomfactor, fillwithwalls, player, possessable, playerorder, fliph, floatinspace, specialeffect, **kwargs):
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
        self.fliph = int(fliph)
        self.floatinspace = to_bool(floatinspace)
        self.specialeffect = int(specialeffect)
        self.blinkoffset = random()*26
        self.parent = None
        self.children = []
        self.window_size = 130
        self.exitref = None
        self.refs = set()
        self.level = level
        self.show = True
        self.music = None
        # UsefulMod (Internal)
        if "usefulTags" in kwargs: self.usefulTags = kwargs["usefulTags"]
        else: self.usefulTags = []
        if "usefulVal" in kwargs: self.usefulVal = kwargs["usefulVal"]
        else: self.usefulVal = {}
    # UsefulMod (Always Enabled Internal)
    # TODO fix usefulget.0
    def get_useful(self):
        return {"usefulTags": self.usefulTags.copy(), "usefulVal": self.usefulVal}
    def __repr__(self):
        return f'<Block of ID {self.id} at ({self.x},{self.y}) inside of {f"<{self.parent.__class__.__name__} of ID {self.parent.id} at ({self.x},{self.y})>" if self.parent is not None else None} with {len(self.children)} children>'
    def get_refs(self):
        for ref in self.refs.copy():
            # This won't remove ref blocks (I checked)
            if ref.parent == None or ref.id != self.id:
                self.refs.remove(ref)
        return self.refs
    def copy(self, level=None, held=False):

        if self.fillwithwalls: return self.full_copy(level) # duplicate solid blocks
        # TODO why?
        if (held or self.parent or (self.exitref and self.exitref.id == self.id and self.exitref.parent is not None)): # if I already exist somewhere:
            # Check if I exist out bounds of a parent remove and return block
            if self.parent and not inbounds(self):
                self.parent.remove_child(self)
                return self
            elif (self.exitref and self.exitref.id == self.id and self.exitref.parent is not None):
                if not inbounds(self.exitref):
                    self.exitref.parent.remove_child(self.exitref)
                    return self
            # return ref to self
            return self.make_ref(level)
        else: # if I don't exist anywhere:
            return self

    def full_copy(self, level, id=None):
        if self.fillwithwalls or not Design.true_dupe: return Block(level, 0, 0, id if id else self.id, self.width, self.height, self.hue, self.sat, self.val, self.zoomfactor, self.fillwithwalls, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect, **self.get_useful())
        base = Block(level, 0, 0, id if id else self.id, self.width, self.height, self.hue, self.sat, self.val, self.zoomfactor, self.fillwithwalls, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect, **self.get_useful())
        for place in self.children:
            check = type(place)
            if check == Floor or check == Wall:
                base.place_child(place.x, place.y, place.copy(None))
            if check == Block:
                if place.id == -1:
                    base.place_child(place.x, place.y, place.copy(None))
            if check == Ref and place.exitblock == False:
                base.place_child(place.x, place.y, place.copy(level))
        return base

    def make_ref(self, level, new=True, saved=False):
        options = {}
        if saved:
            options["decoy"] = True
        # A decoy is a version of the block that is gaurenteed not to be a clone as it is a ref only made
        # For saving
        return Ref(level, 0 if new else self.x, 0 if new else self.y, self.id, 0 if new else 1, 0, 0, 0, 0, -1, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect, **options)
    
    def save(self, level, indent, saved_blocks):
        if self in saved_blocks and not self.fillwithwalls:
            # Rely on decoy to add useful to self
            ref = self.make_ref(level, False, True).save(level, indent, saved_blocks)
            self.exitref = None
            return ref
        else:
            saved_blocks.append(self)

        # No longer adding ref
        line = ["Block", int(self.x), int(self.y), int(self.id), int(self.width), int(self.height), f"{self.hue:1.3g}", f"{self.sat:1.3g}", f"{self.val:1.3g}", f"{self.zoomfactor:1.3g}", int(self.fillwithwalls), int(self.player), int(self.possessable), int(self.playerorder), int(self.fliph), int(self.floatinspace), int(self.specialeffect)]
        block = "\n" + "\t"*indent + " ".join(str(i) for i in line)

        # UsefulMod (Always Enabled Internal)
        block = savekeys(self, indent) + block

        for child in self.children:
            if 0 <= child.x < self.width and 0 <= child.y < self.height:
                block += child.save(level, indent + 1, saved_blocks)
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
                if not inbounds(child):
                    continue
                if fliph:
                    child.draw(draw_list, x + (self.width - 1 - child.x) * inner_width, y + (self.height - 1 - child.y) * inner_height, inner_width, inner_height, level, depth + 1, True)
                else:
                    child.draw(draw_list, x + child.x * inner_width, y + (self.height - 1 - child.y) * inner_height, inner_width, inner_height, level, depth + 1, False)
    
    def draw(self, draw_list, x, y, width, height, level, depth, fliph):
        
        border_padding = 0
        
        draw_list.add_rect_filled(x+border_padding/1.5, y+border_padding/1.5, x+width-border_padding/1.25, y+height-border_padding/1.25, self.color(level, 1 if self.fillwithwalls else 0.5))
        if depth >= 0: # don't draw outer border on block windows
            draw_list.add_rect(x+border_padding/2, y+border_padding/2, x+width-border_padding/2, y+height-border_padding/2, 0xff000000, thickness=0)
            self.draw_children(draw_list, x+border_padding, y+border_padding, width-2*border_padding, height-2*border_padding, level, depth, fliph ^ self.fliph)
        else:
            if Design.grid:
                for vert in range(1,self.width):
                    draw_list.add_line(x+vert*width/self.width,y,x+vert*width/self.width,y+height,imgui.get_color_u32_rgba(*Design.gridstyle), Design.gridwidth)
                for horz in range(1,self.height):
                    draw_list.add_line(x,y+horz*height/self.height,x+height,y+horz*height/self.height,imgui.get_color_u32_rgba(*Design.gridstyle), Design.gridwidth)
            self.draw_children(draw_list, x, y, width, height, level, depth, fliph ^ self.fliph)
        
        if self.exitref and depth > -1:
            if self.exitref.infenter:
                w = width / (self.exitref.infenternum + 1) * 1.3
                h = height / (self.exitref.infenternum + 1)
                h2 = h * 1.3
                for i in range(self.exitref.infenternum + 1):
                    draw_epsilon(draw_list, x + width/2 - w/2, y + (h - h2)/2 + i*h, w, h2)
                #draw_list.add_rect(x, y, x + width, y + height, 0xff3f3f3f, thickness=border)
                #draw_list.add_rect_filled(x, y, x + width, y + height, 0x3fffffff)


        if self.fliph and depth >= 0:
            draw_shine(draw_list, x, y, width, height, fliph ^ self.fliph)
        # Useful Mod (Always Enabled Internal)
        # TODO uncomment
        if True: # depth >= 0:
            if self.usefulTags and "?WEI" in self.usefulTags:
                draw_weight(draw_list, x, y, width, height)
            if self.usefulTags and "?PIN" in self.usefulTags:
                draw_pin(draw_list, x, y, width, height)
        if self.specialeffect in [2,3]:
            draw_shine(draw_list, x, y, width, height, self.specialeffect == 3)
        if self.player:
            draw_eyes(draw_list, x, y, width, height, True, blink_offset = self.blinkoffset, order = self.playerorder)
        elif self.possessable:
            draw_eyes(draw_list, x, y, width, height, False)

        if min(width,height) > 15 and depth > -1:
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

    def place_child(self, x, y, child, refcheck=True):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        if type(child) == Floor:
            self.children.append(child)
            child.parent = self
        else:
            self.children.insert(0, child)
            child.parent = self
            # check if exitref but could be normal block
            if type(child) == Ref and (child.exitblock and not child.infexit and not child.infenter 
                and refcheck and child.id in self.level.blocks and not Design.hub):
                self.remove_child(child)
                self.place_child(x, y, self.level.blocks[child.id])
                return
            # See if block is deep child of itself
            # If so, change child self to exit ref
            if type(child) == Block:
                # If block being put in self
                if child.id == self.id:
                    self.remove_child(self)
                    exit_ref = self.make_ref(self.level, False)
                    self.place_child(x, y, exit_ref, False)
                    return
                # Check for deep child
                elif self.parent:
                    turn_ref = False
                    curr = self.parent
                    while curr != None:
                        if curr.id == self.id:
                            turn_ref = True
                            break
                        curr = curr.parent
                    if turn_ref:
                        parent = self.parent
                        parent.remove_child(self)
                        exit_ref = self.make_ref(self.level, False)
                        parent.place_child(exit_ref.x, exit_ref.y, exit_ref, False)
        child.x = x
        child.y = y

    def menu(self, level):
        if Design.placedebug:
            imgui.bullet_text(str(self))
            imgui.bullet_text("Exit:"+str(self.exitref))
            imgui.bullet_text("Par:"+str(self.parent))
            imgui.bullet_text("Music:"+str(self.music))
        try:
            changed, value = imgui.input_int("ID", self.id, flags=imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
            if changed:
                if not UIstate.focused:
                    UIstate.focused = True
                    delta = math.copysign(1, value - self.id)
                    while value in [block.id for block in level.blocks.values()] :
                        value += delta
                    # Get refs before our ID changes
                    
                    refs = self.get_refs()
                    level.blocks.pop(self.id, None)
                    self.id = value
                    level.blocks[self.id] = self
                    for ref in refs:
                        ref.id = value
                    UIstate.focused = False
        except:
            pass
        changed, value = imgui.input_int("Width", self.width)
        if changed and value > 0:
            self.width = value
            if imgui.get_io().key_shift:
                self.height = value
        changed, value = imgui.input_int("Height", self.height)
        if changed and value > 0:
            self.height = value
            if imgui.get_io().key_shift:
                self.width = value
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
        # UsefulMod (Conditional UI)
        if usefulmod.enabled:
            umenu(self,imgui)

    
    def palette_menu(self, level):
        self.menu(level)
        imgui.separator()
        if imgui.selectable('Create Clone')[0]:
            return Ref(level, 0,0,self.id,0,0,0,0,0,0,0,0,0,0,0,0)
        if imgui.selectable('Create Infinite Exit')[0]:
            return Ref(level, 0,0,self.id,0,1,0,0,0,0,0,0,0,0,0,0)
        if imgui.selectable('Create Infinite Enter')[0]:
            while level.next_free in level.blocks:
                level.next_free += 1
            level.blocks[level.next_free] = Block(level,0,0,level.next_free,5,5,self.hue,self.sat,self.val,1,0,0,0,0,0,0,0)
            return Ref(level,0,0,level.next_free,1,0,0,1,0,self.id,0,0,0,0,0,0)
