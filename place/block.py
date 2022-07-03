import imgui, colorsys
from .utils import to_bool, draw_epsilon, draw_shine, draw_eyes, draw_weight, draw_pin, useful_change, special_effects
from state import Design, usefulmod
from .palette import Palette
from .ref import Ref
from .floor import Floor
from random import random
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
        self.fliph = to_bool(fliph)
        self.floatinspace = to_bool(floatinspace)
        self.specialeffect = int(specialeffect)
        self.blinkoffset = random()*26
        self.parent = None
        self.children = []
        self.window_size = 130
        self.exit = None
        self.refs = []
        self.level = level
        # UsefulMod (Internal)
        if not "purge" in kwargs:
            if "usefulTags" in kwargs:
                self.usefulTags = kwargs["usefulTags"]
            else:
                self.usefulTags = []
            if "usefulWrap" in kwargs:
                self.usefulWrap = kwargs["usefulWrap"]
            else:
                self.usefulWrap = 0
        else:
            self.usefulTags = []
            self.usefulWrap = 0
    # UsefulMod (Always Enabled Internal)
    def get_useful(self):
        return {"usefulTags": self.usefulTags.copy(), "usefulWrap": self.usefulWrap}
    def __repr__(self):
        return f'<Block of ID {self.id} at ({self.x},{self.y}) inside of {f"<{self.parent.__class__.__name__} of ID {self.parent.id} at ({self.x},{self.y})>" if self.parent is not None else None} with {len(self.children)} children>'
    def get_refs(self):
        for ref in self.refs:
            if ref.parent == None or ref.id != self.id:
                self.refs.remove(ref)
        return self.refs
    def copy(self, level, held=False):

        if self.fillwithwalls: return self.full_copy(level) # duplicate solid blocks
        if (held or self.parent or (self.exit and self.exit.id == self.id and self.exit.parent is not None)): # if I already exist somewhere:
            # return ref to self
            return self.make_ref(level)
        else: # if I don't exist anywhere:
            # check if I have an exitblock
            return self

    def full_copy(self, level, id=None):
        return Block(level, 0, 0, id if id else self.id, self.width, self.height, self.hue, self.sat, self.val, self.zoomfactor, self.fillwithwalls, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect, **self.get_useful())

    def make_ref(self, level, new=True, saved=False):
        options = {"usefulTags":[]}
        for tag in self.usefulTags:
            if tag in ["?AIE","?WEI","?ANT","?PIN"]:
                options["usefulTags"].append(tag)
        if saved:
            options["decoy"] = True
        return Ref(level, 0 if new else self.x, 0 if new else self.y, self.id, 0 if new else 1, 0, 0, 0, 0, -1, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect, **options)
    
    def save(self, level, indent, saved_blocks):
        if self in saved_blocks and not self.fillwithwalls:
            ref = self.make_ref(level, False, True).save(level, indent, saved_blocks)
            self.exit = None
            return ref
        else:
            saved_blocks.append(self)
        line = ["Block", int(self.x), int(self.y), int(self.id), int(self.width), int(self.height), f"{self.hue:1.3g}", f"{self.sat:1.3g}", f"{self.val:1.3g}", f"{self.zoomfactor:1.3g}", int(self.fillwithwalls), int(self.player), int(self.possessable), int(self.playerorder), int(self.fliph), int(self.floatinspace), int(self.specialeffect)]
        block = "\n" + "\t"*indent + " ".join(str(i) for i in line)
        # UsefulMod (Always Enabled Internal)
        for useTag in self.usefulTags:
            block = "\n" + "\t"*indent + str(useTag) + block
        if self.usefulWrap > 0:
            block = "\n" + "\t"*indent + "?WRP "+ str(self.usefulWrap) + block
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
                if fliph:
                    child.draw(draw_list, x + (self.width - 1 - child.x) * inner_width, y + (self.height - 1 - child.y) * inner_height, inner_width, inner_height, level, depth + 1, True)
                else:
                    child.draw(draw_list, x + child.x * inner_width, y + (self.height - 1 - child.y) * inner_height, inner_width, inner_height, level, depth + 1, False)
    
    def draw(self, draw_list, x, y, width, height, level, depth, fliph):
        
        border = min(width,height)/Design.thick
        border_padding = (min(width,height)/Design.thick) * depth<=5
        
        draw_list.add_rect_filled(x+border_padding/1.5, y+border_padding/1.5, x+width-border_padding/1.25, y+height-border_padding/1.25, self.color(level, 1 if self.fillwithwalls else 0.5))
        if depth >= 0: # don't draw outer border on block windows
            draw_list.add_rect(x+border_padding/2, y+border_padding/2, x+width-border_padding/2, y+height-border_padding/2, 0xff000000, thickness=border+1)
            self.draw_children(draw_list, x+border_padding, y+border_padding, width-2*border_padding, height-2*border_padding, level, depth, fliph ^ self.fliph)
        else:
            if Design.grid:
                for vert in range(1,self.width):
                    draw_list.add_line(x+vert*width/self.width,y,x+vert*width/self.width,y+height,imgui.get_color_u32_rgba(*Design.gridstyle), Design.gridwidth)
                for horz in range(1,self.height):
                    draw_list.add_line(x,y+horz*height/self.height,x+height,y+horz*height/self.height,imgui.get_color_u32_rgba(*Design.gridstyle), Design.gridwidth)
            self.draw_children(draw_list, x, y, width, height, level, depth, fliph ^ self.fliph)
        
        if self.exit and depth > -1:
            if self.exit.infenter:
                w = width / (self.exit.infenternum + 1) * 1.3
                h = height / (self.exit.infenternum + 1)
                h2 = h * 1.3
                for i in range(self.exit.infenternum + 1):
                    draw_epsilon(draw_list, x + width/2 - w/2, y + (h - h2)/2 + i*h, w, h2)
                #draw_list.add_rect(x, y, x + width, y + height, 0xff3f3f3f, thickness=border)
                #draw_list.add_rect_filled(x, y, x + width, y + height, 0x3fffffff)


        if self.fliph and depth >= 0:
            draw_shine(draw_list, x, y, width, height, fliph ^ self.fliph)
        # Useful Mod (Always Enabled Internal)
        if depth >= 0:
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
        else:
            self.children.insert(0, child)
            child.parent = self
            # check if exitref but could be normal block
            if type(child) == Ref and child.exitblock and not child.infexit and not child.infenter and refcheck:
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
            imgui.bullet_text("Exit:"+str(self.exit))
            imgui.bullet_text("Par:"+str(self.parent))
        changed, value = imgui.input_int("ID", self.id)
        if changed:
            delta = value - self.id
            while value in [block.id for block in level.blocks.values()]:
                value += delta
            self.id = value
        changed, value = imgui.input_int("Width", self.width)
        if changed and value > 0:
            self.width = value
        changed, value = imgui.input_int("Height", self.height)
        if changed and value > 0:
            self.height = value
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
        if usefulmod.enabled and imgui.begin_menu("UsefulMod"):
            changed, value = imgui.input_int("Wrap", int(self.usefulWrap))
            if changed: 
                self.usefulWrap = value
            changed, value = imgui.checkbox("Camera Follow", "?PCF" in self.usefulTags)
            if changed:
                useful_change(self, "?PCF", bool(value))
            changed, value = imgui.checkbox("Inf Zone", "?IFZ" in self.usefulTags)
            if changed:
                useful_change(self, "?IFZ", bool(value))
            changed, value = imgui.checkbox("Weighted", "?WEI" in self.usefulTags)
            if changed:
                useful_change(self, "?WEI", bool(value))
            changed, value = imgui.checkbox("Anti", "?ANT" in self.usefulTags)
            if changed:
                useful_change(self, "?ANT", bool(value))
            changed, value = imgui.checkbox("Pinned", "?PIN" in self.usefulTags)
            if changed:
                useful_change(self, "?PIN", bool(value))
            imgui.end_menu()

    
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
