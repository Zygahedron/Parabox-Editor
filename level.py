import os
import imgui
from random import random
from pathlib import Path
from state import usefulmod
from place.walls import Wall
from place.utils import * 
from place.palette import Palette
from place.floor import Floor
from place.block import Block
from place.ref import Ref
class Level:
    def __init__(self, name, data, level_number = -1, hub_parent = False, difficulty: int = 0, possess_fx = False, credits = ''):
        self.name = name
        self.is_hub = name == 'hub.txt'
        self.hub_parent = hub_parent
        self.level_number = level_number
        self.difficulty = int(difficulty)
        self.possess_fx = possess_fx
        self.blocks = {}
        self.next_free = 0
        self.credits = credits
        # UsefulState
        useful_warn = False
        #
        try:
            [metadata, data] = data.split("\n#\n")
        except ValueError:
            raise Exception('Selected file isn\'t a level!')
        # Split metadata into [first_word, rest_of_line]
        metadata = [e.split(" ", 1) for e in metadata.split("\n")]
        # Self.metadata = {metadata_key: metadata_value}
        self.metadata = {e[0]: e[1] for e in metadata}
        
        # Set Set attempt order 
        if not "attempt_order" in self.metadata: self.metadata["attempt_order"] = "push,enter,eat,possess"
        read_metadata = self.metadata["attempt_order"].split(",")
        self.metadata["attempt_order"] = [[a,True] for a in read_metadata]
        self.metadata["attempt_order"].extend([[a,False] for a in ['push','enter','eat','possess'] if a not in read_metadata])
        
        # Set shed,inner_push, and draw_style
        self.metadata["shed"] = "shed" in self.metadata and self.metadata["shed"] == "1"
        self.metadata["inner_push"] = "inner_push" in self.metadata and self.metadata["inner_push"] == "1"
        if not "draw_style" in self.metadata: self.metadata["draw_style"] = "normal"
        
        self.metadata["custom_level_music"] = -1 if "custom_level_music" not in self.metadata else int(self.metadata["custom_level_music"])
        self.metadata["custom_level_palette"] = -1 if "custom_level_palette" not in self.metadata else int(self.metadata["custom_level_palette"])
        
        # UsefulMod (Internal)
        for usefulmetadata in ["winfz_sensitivity", "white_eyes", "banish_fix", "ifzeat_fix", "epsi_fix"]:
            self.metadata[usefulmetadata] = usefulmetadata in self.metadata and self.metadata[usefulmetadata] == "1" and not usefulmod.purge
            if self.metadata[usefulmetadata] and not usefulmod.purge:
                useful_warn = True
        
        data = data.split("\n")
        indent = 0
        last_block = None
        parent = None
        refs = []
        kwargs = {"usefulTags":[]}
        for line in data:
            # UsefulState
            if usefulmod.purge:
                kwargs["purge"] = True
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
                    raise Exception('Error parsing level: Indent after non-Block')
            elif indent < last_indent:
                for _ in range(last_indent - indent):
                    parent = parent.parent

            args = trimmed.split(" ")
            block_type = args.pop(0)
            if block_type == "Block":
                block = Block(self, *args, **kwargs)
                # For UsefulMod
                kwargs = {"usefulTags":[]}
                block.parent = parent
                if parent:
                    parent.place_child(int(block.x), int(block.y), block)
                last_block = block
                if block.fillwithwalls != 1:
                    if not int(block.id) in self.blocks:
                        self.blocks[int(block.id)] = block
                    else:
                        print("duplicate block with id " + str(block.id))
            elif block_type == "Ref":
                ref = Ref(self, *args, **kwargs)
                kwargs = {"usefulTags":[]}
                if not int(ref.infenter):
                    refs.append(ref)
                if parent:
                    parent.place_child(int(ref.x), int(ref.y), ref)
                else: 
                    # TODO this is a fatal loading error. Add debug message
                    pass
                last_block = ref
            elif block_type == "Wall":
                if len(args) > 6:
                    wall = Wall(*args[:5],"_".join(args[5:]))
                else:
                    wall = Wall(*args)
                if parent:
                    parent.place_child(int(wall.x), int(wall.y), wall)
                else:
                    print("Discarding wall at root level")
                last_block = wall
            elif block_type == "Floor":
                floor = Floor(*args[:3], " ".join(args[3:]).replace("_"," ").replace('\\n','\n'))
                if parent:
                    parent.place_child(int(floor.x), int(floor.y), floor)
                else:
                    print("Discarding floor at root level")
                last_block = floor
            # UsefulMod (Always Enabled Internal)
            elif len(block_type) > 0 and block_type[0]=="?":
                useful_warn = True
                if block_type == "?WRP":
                    kwargs["usefulWrap"]=int(args[0].strip)
                else:
                    kwargs["usefulTags"].append(block_type)
            else:
                pass
        for ref in refs:
            # Some refs may not have been added to their blocks because the block did not exist when they were made.
            # Add them again manually (set so no duplicates)
            if ref.id in self.blocks:
                self.blocks[ref.id].refs.add(ref)
        if useful_warn and not usefulmod.enabled and not usefulmod.purge:
            usefulmod.warn = True
        usefulmod.purge = False


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
        # UsefulMod
        if self.metadata["winfz_sensitivity"]:
            data += "winfz_sensitivity 1\n"
        if self.metadata["white_eyes"]:
            data += "white_eyes 1\n"
        if self.metadata["banish_fix"]:
            data += "banish_fix 1\n"
        if self.metadata["ifzeat_fix"]:
            data += "ifzeat_fix 1\n"
        if self.metadata["epsi_fix"]:
            data += "epsi_fix 1\n"
        data += "#\n"
        
        to_save = list(self.blocks.values())
        # print(to_save[0].children)
        saved_blocks = []
        seen = []
        areas = []
        area_ids = []
        while len(to_save):
            current = to_save[0]
            seen.append(current)
            while current.parent and not (current.parent in seen):
                current = current.parent
                seen.append(current)
            if self.is_hub:
                if os.path.exists(f'{Path(self.name).stem}.png'):
                    os.remove(f'{Path(self.name).stem}.png')
                for child in current.children:
                    if type(child) == Ref:
                        if child.id not in area_ids:
                            areas.append([child.area_name, child.area_music])
                            area_ids.append(child.id)
            data += current.save(self, 0, saved_blocks)
            for block in saved_blocks:
                if block in to_save:
                    to_save.remove(block)
        return data, self.is_hub, self.hub_parent, self.level_number, areas, self.credits, int(self.possess_fx), self.difficulty

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
        
        # UsefulMod (Conditional UI)
        if usefulmod.enabled:
            imgui.separator() 
        if usefulmod.enabled and imgui.begin_menu("UsefulMod"):
            changed, value = imgui.checkbox("WInfZ Sensitivity", self.metadata["winfz_sensitivity"])
            if changed:
                self.metadata["winfz_sensitivity"] = value
            changed, value = imgui.checkbox("White Eyes", self.metadata["white_eyes"])
            if changed:
                self.metadata["white_eyes"] = value
            changed, value = imgui.checkbox("Banish Fix", self.metadata["banish_fix"])
            if changed:
                self.metadata["banish_fix"] = value
            changed, value = imgui.checkbox("Inf Zone Eat Fix", self.metadata["ifzeat_fix"])
            if changed:
                self.metadata["ifzeat_fix"] = value
            changed, value = imgui.checkbox("Epsilon Fix", self.metadata["epsi_fix"])
            if changed:
                self.metadata["epsi_fix"] = value
            imgui.end_menu()
        imgui.separator()
        if not self.hub_parent:
            changed, value = imgui.checkbox("Hub Level", self.is_hub)
            if changed:
                self.is_hub = value
        if not self.is_hub:
            changed, value = imgui.checkbox("Has Parent Hub", self.hub_parent)
            if changed:
                self.hub_parent = value
            if self.hub_parent:
                changed, value = imgui.input_int("Level Number", self.level_number)
                if changed:
                    self.level_number = value
                changed, value = imgui.combo("Border", self.difficulty, ['Normal','Hard','Special'])
                if changed:
                    self.difficulty = value
                changed, value = imgui.checkbox("Possess Effect on Start", self.possess_fx)
                if changed:
                    self.possess_fx = value
        else:
            changed, value = imgui.input_text_multiline("Credits", self.credits,100000)
            if changed:
                self.credits = value