import imgui
import math
from random import random
from state import Design, usefulmod
from .utils import to_bool, draw_infinity, draw_epsilon, draw_shine, draw_eyes, draw_weight, draw_pin, useful_change, special_effects

class Ref:
    def __init__(self, level, x, y, id, exitblock, infexit, infexitnum, infenter, infenternum, infenterid, player, possessable, playerorder, fliph, floatinspace, specialeffect, area_name = None, **kwargs):
        self.level = level
        self.x = int(x)
        self.y = int(y)
        self.id = int(id)
        self.exitblock = to_bool(exitblock)
        if self.exitblock and not "decoy" in kwargs and self.id in level.blocks:
            block = level.blocks[self.id]
            if block.exitref:
                # Revoke exit privileges
                block.exitref.exitblock = False
            block.exitref = self
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
        if level.is_hub and area_name is not None:
            self.area_name = area_name.replace(' ','_')
        else:
            self.area_name = None
        if "music" in kwargs and area_name in kwargs["music"]:
            self.level.music[self.id] = kwargs["music"][area_name]
        else: self.area_music = 0
        # UsefulMod (Always Enabled Internal)
        if not "purge" in kwargs:
            if "usefulTags" in kwargs:
                self.usefulTags = kwargs["usefulTags"]
            else:
                self.usefulTags = []
        else:
                self.usefulTags = []
        # Tell the world you (the block you reference) that you exist
        if self.id in level.blocks:
            orig = level.blocks[self.id]
            orig.refs.add(self)
            # Prevent 10000 unused refs in a blocks ref array without causing too much
            # trouble for large ref amounts by checking for unused refs if ref length is a
            # square number more than 15
            if len(orig.refs) >= 16:
                num = math.sqrt(len(orig.refs))
                if num == int(num):
                    # get ref function purges dead refs
                    orig.get_refs()
    # UsefulMod (Always Enabled Internal)
    def get_music(self, default=None):
        try:
            music = self.get_orig().music
            if music is None: return default
            else: return music
        except:
            return None
    def set_music(self, music):
        try:
            self.get_orig().music = music
        except:
            pass
    def get_useful(self):
        return {"usefulTags": self.usefulTags.copy()}
    def is_block_ref(self):
        return self.exitblock and not self.infenter and not self.infexit
    def get_orig(self):
        return self.level.blocks[self.id]
    def __repr__(self):
        return f'<Reference of ID {self.id} at ({self.x},{self.y}) inside of {f"<{self.parent.__class__.__name__} of ID {self.parent.id}>" if self.parent is not None else None}>'

    def copy(self, level, held=False): # return non-exit copy
        return Ref(level, 0, 0, self.id, 0, self.infexit, self.infexitnum, self.infenter, self.infenternum, self.infenterid, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect, self.area_name, **self.get_useful())

    def save(self, level, indent, saved_blocks):
        line = ["Ref", 
            int(self.x), 
            int(self.y), 
            int(self.id), 
            int(self.exitblock), 
            int(self.infexit), 
            int(self.infexitnum), 
            int(self.infenter), 
            int(self.infenternum), 
            int(self.infenterid), 
            int(self.player), 
            int(self.possessable), 
            int(self.playerorder), 
            int(self.fliph), 
            int(self.floatinspace), 
            int(self.specialeffect),
            self.area_name.replace(' ','_') if self.area_name is not None else ''
        ]
        refText = "\n" + "\t"*indent + " ".join(str(i) for i in line)
        # UsefulMod (Always Enabled Internal)
        for useTag in self.usefulTags:
            refText = "\n" + "\t"*indent + str(useTag) + refText
        return refText

    def draw(self, draw_list, x, y, width, height, level, depth, fliph):
        
        border = min(width,height)/Design.thick
        border_padding = (min(width,height)/Design.thick) * depth<=3
        if self.id in level.blocks:
            orig = level.blocks[self.id]
            if self.is_block_ref():
                orig.draw(draw_list, x, y, width, height, level, depth, fliph)
                return
            draw_list.add_rect_filled(x+border_padding/3, y+border_padding/3, x+width-border_padding/3, y+height-border_padding/3, orig.color(level, 1 if orig.fillwithwalls else 0.5))
            draw_list.add_rect(x+border_padding/2, y+border_padding/2, x+width-border_padding/2, y+height-border_padding/2, 0xff000000, thickness=border)
            orig.draw_children(draw_list, x, y, width, height, level, depth, fliph ^ self.fliph)
        else:
            draw_list.add_text(x + width/20, y + height/30, 0xffffffff, "Invalid Reference!")
            draw_list.add_rect(x, y, x+width, y+height, 0xff000000, thickness=border)

        if self.infexit:
            draw_list.add_rect_filled(x+border_padding/2, y+border_padding/2, x+width-border_padding/2, y+height-border_padding/2, 0x3f000000)
            draw_list.add_rect(x+border_padding/2, y+border_padding/2, x+width-border_padding/2, y+height-border_padding/2, 0xff00ffff, thickness=border)
            if self.infexitnum == 0:
                draw_infinity(draw_list, x, y, width, height)
            else:
                w = width / (self.infexitnum + 1) * 1.8
                h = height / (self.infexitnum + 1)
                h2 = h * 1.8
                for i in range(self.infexitnum + 1):
                    draw_infinity(draw_list, x + width/2 - w/2, y + (h - h2)/2 + i*h, w, h2)
        else:
            if (self.infenter): #or (exit and exit.infenter):
                infenternum = self.infenternum #if self.exitblock else exit.infenternum
                w = width / (infenternum + 1) * 1.3
                h = height / (infenternum + 1)
                h2 = h * 1.3
                for i in range(infenternum + 1):
                    draw_epsilon(draw_list, x + width/2 - w/2, y + (h - h2)/2 + i*h, w, h2)
            draw_list.add_rect(x, y, x + width, y + height, 0xff3f3f3f, thickness=border)
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

        # UsefulMod (Always Enabled Internal)
        if self.usefulTags and "?WEI" in self.usefulTags:
            draw_weight(draw_list, x, y, width, height)
        if self.usefulTags and "?PIN" in self.usefulTags:
            draw_pin(draw_list, x, y, width, height)
        if min(width,height) > 15 and depth >= 0:
            draw_list.add_text(x + width/20, y + height/30, 0xffffffff, str(self.id))

    def menu(self, level):
        if Design.placedebug:
            imgui.bullet_text(str(self))
        if self.is_block_ref() and not Design.hub:
            self.get_orig().menu(level)
            return
        changed, value = imgui.input_int("ID", self.id)
        if changed:
            self.id = value

        changed, value = imgui.checkbox("Exit Block", to_bool(self.exitblock))
        if changed:
            orig = level.blocks[self.id]
            if orig:
                if value:
                    if orig.exitref:
                        orig.exitref.exitblock = False
                    orig.exitref = self
                elif orig.exitref == self:
                    orig.exitref = None
                self.exitblock = value
            
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

        # UsefulMod (Conditional UI)
        if usefulmod.enabled and imgui.begin_menu("UsefulMod"):
            changed, value = imgui.checkbox("Inf Enter Allowed", "?AIE" in self.usefulTags)
            if changed:
                useful_change(self, "?AIE", bool(value))
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
        if level.is_hub:
            imgui.separator()
            changed, value = imgui.input_text("Area Name", self.area_name if self.area_name is not None else '', 256)
            if changed:
                self.area_name = value if value != '' else None
            changed, value = imgui.combo("Area Music",  self.get_music(-1) + 1, ["None", "Intro", "Enter", "Empty", "Eat", "Reference", "Center", "Clone", "Transfer", "Open", "Flip", "Cycle", "Swap", "Player", "Possess", "Wall", "Infinite Exit", "Infinite Enter", "Multi Infinite", "Reception", "Appendix", "Pause (buggy)", "Credits"])
            if changed:
                self.get_orig().music = value - 1
