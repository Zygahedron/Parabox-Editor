import colorsys, imgui
from re import S

def draw_eyes(draw_list, x, y, width, height, solid, color=0x7f000000):
    size = min(width,height)
    if solid:
        draw_list.add_circle_filled(x + width/4, y + height/2, size/10, color)
        draw_list.add_circle_filled(x + width*3/4, y + height/2, size/10, color)
    else:
        draw_list.add_circle(x + width/4, y + height/2, size/10, color, thickness=size/20)
        draw_list.add_circle(x + width*3/4, y + height/2, size/10, color, thickness=size/20)

infinity_polyline = [
    (0.65, 0.65), (0.8, 0.65), (0.85, 0.5), (0.8, 0.35), (0.65, 0.35),
    (0.35, 0.65), (0.2, 0.65), (0.15, 0.5), (0.2, 0.35), (0.35, 0.35)
]
def draw_infinity(draw_list, x, y, width, height):
    draw_list.add_polyline([(x + u*width, y + v*height) for u, v in infinity_polyline], 0xffffffff, True, min(width,height)/10)

epsilon_polyline = [
    (0.7, 0.3), (0.4, 0.25), (0.3, 0.35), (0.4, 0.5), (0.6, 0.5),
    (0.6, 0.5), (0.4, 0.5), (0.3, 0.65), (0.4, 0.75), (0.7, 0.7)
]
def draw_epsilon(draw_list, x, y, width, height):
    draw_list.add_polyline([(x + u*width, y + v*height) for u, v in epsilon_polyline], 0xffffffff, False, min(width,height)/10)

def color_button(obj, h, s, v, name):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    if imgui.color_button(name, r, g, b, 1, width=20, height=20):
        obj.hue = h
        obj.sat = s
        obj.val = v

class Block:
    def __init__(self, x, y, id, width, height, hue, sat, val, zoomfactor, fillwithwalls, player, possessable, playerorder, fliph, floatinspace, specialeffect):
        self.x = int(x)
        self.y = int(y)
        self.id = id
        self.width = int(width)
        self.height = int(height)
        self.hue = float(hue)
        self.sat = float(sat)
        self.val = float(val)
        self.zoomfactor = float(zoomfactor)
        self.fillwithwalls = int(fillwithwalls)
        self.player = int(player)
        self.possessable = int(possessable)
        self.playerorder = int(playerorder)
        self.fliph = int(fliph)
        self.floatinspace = int(floatinspace)
        self.specialeffect = int(specialeffect)

        self.parent = None
        self.children = []

    def copy(self, held=False):
        if (held or self.parent): # if I already exist somewhere:
            if self.fillwithwalls: # duplicate solid blocks
                return self.full_copy()
            # return ref to self
            return self.make_ref()
        else: # if I don't exist anywhere:
            # no need to copy
            return self

    def full_copy(self, id=None):
        new = Block(0, 0, id if id else self.id, self.width, self.height, self.hue, self.sat, self.val, self.zoomfactor, self.fillwithwalls, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect)
        for child in self.children:
            new.place_child(child.x, child.y, child.copy())
        return new

    def make_ref(self, new=True):
        return Ref(0 if new else self.x, 0 if new else self.y, self.id, 0 if new else 1, 0, 0, 0, 0, "-1", self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect)
    
    def save(self, indent, saved_blocks, void=False):
        if self in saved_blocks and not self.fillwithwalls:
            return self.make_ref(False).save(indent, saved_blocks)
        else:
            saved_blocks.append(self)
        line = ["Block", self.x, self.y, self.id, self.width, self.height, self.hue, self.sat, self.val, self.zoomfactor, self.fillwithwalls, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect]
        block = "\n" + "\t"*indent + " ".join(str(i) for i in line)
        for child in self.children:
            if 0 <= child.x < self.width and 0 <= child.y < self.height:
                block += child.save(indent + 1, saved_blocks)
            else:
                pass # discard out of bounds children on save
        return block
    
    def draw(self, draw_list, x, y, width, height, level, depth):
        draw_list.add_rect_filled(x, y, x+width, y+height, self.color())
        if depth >= 0: # don't draw outer border on block windows
            draw_list.add_rect(x, y, x+width, y+height, 0xff000000, thickness=min(width,height)/20)

        if self.width > 0 and self.height > 0:
            inner_width = width / self.width
            inner_height = height / self.height
            if min(inner_width,inner_height) < 1 or depth > 10:
                return
            for child in self.children:
                child.draw(draw_list, x + child.x * inner_width, y + (self.height - 1 - child.y) * inner_height, inner_width, inner_height, level, depth + 1)

        if self.player:
            draw_eyes(draw_list, x, y, width, height, True)
        elif self.possessable:
            draw_eyes(draw_list, x, y, width, height, False)

        if min(width,height) > 15 and depth >= 0:
            draw_list.add_text(x + width/20, y + height/30, 0xffffffff, str(self.id))

    def color(self):
        r, g, b = colorsys.hsv_to_rgb(self.hue, self.sat, self.val / (1 if self.fillwithwalls else 2))
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

    def menu(self):
        if imgui.begin_menu("Change Block Type"):
            changed, value = imgui.input_int("Size", self.width)
            if changed:
                self.width = value
                self.height = value

            imgui.separator()
            clicked, state = imgui.checkbox("Flip Horizontally", self.fliph)
            if clicked:
                self.fliph = int(state)
            clicked, state = imgui.checkbox("Float in Space", self.floatinspace)
            if clicked:
                self.floatinspace = int(state)

            imgui.separator()
            if imgui.selectable("Normal")[0]:
                self.player = 0
                self.possessable = 0
                if self.fillwithwalls:
                    self.hue = 0.1
                    self.sat = 0.8
                    self.val = 1.0
            if imgui.selectable("Player")[0]:
                self.player = 1
                self.possessable = 1
                if self.fillwithwalls:
                    self.hue = 0.9
                    self.sat = 1.0
                    self.val = 0.7
            if imgui.selectable("Possessable")[0]:
                self.player = 0
                self.possessable = 1
                if self.fillwithwalls:
                    self.hue = 0.9
                    self.sat = 1.0
                    self.val = 0.7

            imgui.separator()
            imgui.separator()
            if self.fillwithwalls:
                if imgui.selectable("Convert to Enterable Room")[0]:
                    self.fillwithwalls = 0
                    self.width = 5
                    self.height = 5
                    self.hue = 0.6
                    self.sat = 0.8
                    self.val = 1.0
            else:
                if imgui.selectable("Convert to Solid Box")[0]:
                    self.fillwithwalls = 1
                    self.width = 1
                    self.height = 1
                    while len(self.children):
                        self.remove_child(self.children[0])
                    if self.possessable:
                        self.hue = 0.9
                        self.sat = 1.0
                        self.val = 0.7
                    else:
                        self.hue = 0.1
                        self.sat = 0.8
                        self.val = 1.0

            imgui.end_menu()

        if imgui.begin_menu("Change Block Color"):
            color_button(self, 0, 0, 0.5, "A")
            imgui.same_line()
            color_button(self, 0.6, 0.8, 1, "B")
            imgui.same_line()
            color_button(self, 0.4, 0.8, 1, "C")
            imgui.same_line()
            color_button(self, 0.1, 0.8, 1, "D")
            imgui.same_line()
            color_button(self, 0.9, 1, 0.7, "E")
            imgui.same_line()
            color_button(self, 0.55, 0.8, 1, "F")
            
            imgui.separator()
            changed, value = imgui.input_float("Hue", self.hue)
            if changed:
                self.hue = value
            changed, value = imgui.input_float("Saturation", self.sat)
            if changed:
                self.sat = value
            changed, value = imgui.input_float("Value", self.val)
            if changed:
                self.val = value

            imgui.end_menu()

        if imgui.begin_menu("Edit Block"):
            changed, value = imgui.input_text("ID", self.id, 64)
            if changed:
                self.id = value

            changed, value = imgui.input_int("Width", self.width)
            if changed:
                self.width = value
            changed, value = imgui.input_int("Height", self.height)
            if changed:
                self.height = value
            changed, value = imgui.input_float("Hue", self.hue)
            if changed:
                self.hue = value
            changed, value = imgui.input_float("Saturation", self.sat)
            if changed:
                self.sat = value
            changed, value = imgui.input_float("Value", self.val)
            if changed:
                self.val = value
            changed, value = imgui.input_float("Zoom Factor", self.zoomfactor)
            if changed:
                self.zoomfactor = value
            changed, value = imgui.input_int("Fill With Walls", self.fillwithwalls)
            if changed:
                self.fillwithwalls = value

            changed, value = imgui.input_int("Player", self.player)
            if changed:
                self.player = value
            changed, value = imgui.input_int("Possessable", self.possessable)
            if changed:
                self.possessable = value
            changed, value = imgui.input_int("Player Order", self.playerorder)
            if changed:
                self.playerorder = value
            changed, value = imgui.input_int("Flip Horizontally", self.fliph)
            if changed:
                self.fliph = value
            changed, value = imgui.input_int("Float in Space", self.floatinspace)
            if changed:
                self.floatinspace = value
            changed, value = imgui.input_int("Special Effect", self.specialeffect)
            if changed:
                self.specialeffect = value

            imgui.end_menu()

class Ref:
    def __init__(self, x, y, id, exitblock, infexit, infexitnum, infenter, infenternum, infenterid, player, possessable, playerorder, fliph, floatinspace, specialeffect):
        self.x = int(x)
        self.y = int(y)
        self.id = id
        self.exitblock = int(exitblock)
        self.infexit = int(infexit)
        self.infexitnum = int(infexitnum)
        self.infenter = int(infenter)
        self.infenternum = int(infenternum)
        self.infenterid = infenterid
        self.player = int(player)
        self.possessable = int(possessable)
        self.playerorder = int(playerorder)
        self.fliph = int(fliph)
        self.floatinspace = int(floatinspace)
        self.specialeffect = int(specialeffect)

        self.parent = None

    def copy(self, held=False): # return non-exit copy
        return Ref(0, 0, self.id, 0, self.infexit, self.infexitnum, self.infenter, self.infenternum, self.infenterid, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect)

    def save(self, indent, saved_blocks, void=False):
        line = ["Ref", self.x, self.y, self.id, self.exitblock, self.infexit, self.infexitnum, self.infenter, self.infenternum, self.infenterid, self.player, self.possessable, self.playerorder, self.fliph, self.floatinspace, self.specialeffect]
        return "\n" + "\t"*indent + " ".join(str(i) for i in line)

    def draw(self, draw_list, x, y, width, height, level, depth):
        if self.id in level.blocks:
            level.blocks[self.id].draw(draw_list, x, y, width, height, level, depth)
        else:
            draw_list.add_text(x + width/20, y + height/30, 0xffffffff, "Invalid Reference!")
        if self.infexit:
            draw_list.add_rect_filled(x, y, x + width, y + height, 0x3f000000)
            draw_list.add_rect(x, y, x + width, y + height, 0xff00ffff, thickness=min(width,height)/20)
            draw_infinity(draw_list, x, y, width, height)
        else:
            if self.infenter:
                draw_epsilon(draw_list, x, y, width, height)
            draw_list.add_rect(x, y, x + width, y + height, 0xff3f3f3f, thickness=min(width,height)/20)
            if not self.exitblock:
                draw_list.add_rect_filled(x, y, x + width, y + height, 0x3fffffff)

    def menu(self):
        if imgui.begin_menu("Change Reference Type"):
            # if imgui.selectable("Make Exitable", enabled = self.exitblock == 0)[0]:
            #     self.exitblock = 1
                # TODO: make this also make the others not exitable
                # complication: replace this with the real one *if* it's not an epsilon
            clicked, state = imgui.checkbox("Flip Horizontally", self.fliph)
            if clicked:
                self.fliph = int(state)
            clicked, state = imgui.checkbox("Float in Space", self.floatinspace)
            if clicked:
                self.floatinspace = int(state)
            imgui.separator()

            if imgui.selectable("Clone")[0]:
                self.infexit = 0
                self.infexitnum = 0
                self.infenter = 0
                self.infenternum = 0
                self.infenterid = "-1"
            if imgui.selectable("Infinite Exit")[0]:
                self.infexit = 1
                self.infexitnum = 0
                self.infenter = 0
                self.infenternum = 0
                self.infenterid = "-1"
            if self.infexit:
                changed, value = imgui.input_int("-> Layer", self.infexitnum)
                if changed:
                    self.infexitnum = value
            if imgui.selectable("Infinite Enter")[0]:
                self.infexit = 0
                self.infexitnum = 0
                self.infenter = 1
                self.infenternum = 0
                self.infenterid = self.id
            if self.infenter:
                changed, value = imgui.input_int("-> Layer", self.infenternum)
                if changed:
                    self.infenternum = value
                changed, value = imgui.input_text("-> From ID", self.infenterid, 64)
                if changed:
                    self.infenterid = value
            imgui.separator()

            if imgui.selectable("Normal")[0]:
                self.player = 0
                self.possessable = 0
            if imgui.selectable("Player")[0]:
                self.player = 1
                self.possessable = 1
            if imgui.selectable("Possessable")[0]:
                self.player = 0
                self.possessable = 1

            imgui.end_menu()

        if imgui.begin_menu("Edit Reference"):
            changed, value = imgui.input_text("ID", self.id, 64)
            if changed:
                self.id = value

            changed, value = imgui.input_int("Exit Block", self.exitblock)
            if changed:
                self.exitblock = value
            changed, value = imgui.input_int("Infinite Exit", self.infexit)
            if changed:
                self.infexit = value
            changed, value = imgui.input_int("-> Layer", self.infexitnum)
            if changed:
                self.infexitnum = value
            changed, value = imgui.input_int("Infinite Enter", self.infenter)
            if changed:
                self.infenter = value
            changed, value = imgui.input_int("-> Layer", self.infenternum)
            if changed:
                self.infenternum = value
            changed, value = imgui.input_text("-> From ID", self.infenterid, 64)
            if changed:
                self.infenterid = value

            changed, value = imgui.input_int("Player", self.player)
            if changed:
                self.player = value
            changed, value = imgui.input_int("Possessable", self.possessable)
            if changed:
                self.possessable = value
            changed, value = imgui.input_int("Player Order", self.playerorder)
            if changed:
                self.playerorder = value
            changed, value = imgui.input_int("Flip Horizontally", self.fliph)
            if changed:
                self.fliph = value
            changed, value = imgui.input_int("Float in Space", self.floatinspace)
            if changed:
                self.floatinspace = value
            changed, value = imgui.input_int("Special Effect", self.specialeffect)
            if changed:
                self.specialeffect = value

            imgui.end_menu()

class Wall:
    id = None

    def __init__(self, x, y, player, possessable, playerorder):
        self.x = int(x)
        self.y = int(y)
        self.player = int(player)
        self.possessable = int(possessable)
        self.playerorder = int(playerorder)

        self.parent = None

    def save(self, indent, saved_blocks, void=False):
        line = ["Wall", self.x, self.y, self.player, self.possessable, self.playerorder]
        return "\n" + "\t"*indent + " ".join(str(i) for i in line)

    def copy(self, held=False):
        return Wall(0, 0, self.player, self.possessable, self.playerorder)
    
    def draw(self, draw_list, x, y, width, height, level, depth):
        draw_list.add_rect_filled(x + width/10, y + height/10, x + width*9/10, y + height*9/10, self.color())

        if self.player:
            draw_eyes(draw_list, x, y, width, height, True)
        elif self.possessable:
            draw_eyes(draw_list, x, y, width, height, False)

    def color(self):
        if not self.parent: return 0xff7f7f7f
        r, g, b = colorsys.hsv_to_rgb(self.parent.hue, self.parent.sat, self.parent.val)
        return imgui.get_color_u32_rgba(r, g, b, 1)

    def menu(self):
        if imgui.begin_menu("Change Wall Type"):
            if imgui.selectable("Normal")[0]:
                self.player = 0
                self.possessable = 0
            if imgui.selectable("Player")[0]:
                self.player = 1
                self.possessable = 1
            if imgui.selectable("Possessable")[0]:
                self.player = 0
                self.possessable = 1

            imgui.end_menu()

        if imgui.begin_menu("Edit Wall"):
            changed, value = imgui.input_int("Player", self.player)
            if changed:
                self.player = value
            changed, value = imgui.input_int("Possessable", self.possessable)
            if changed:
                self.possessable = value
            changed, value = imgui.input_int("Player Order", self.playerorder)
            if changed:
                self.playerorder = value

            imgui.end_menu()

class Floor:
    id = None

    def __init__(self, x, y, floor_type, extra_data):
        self.x = int(x)
        self.y = int(y)
        self.type = floor_type
        self.extra_data = extra_data

        self.parent = None

    def copy(self, held=False):
        return Floor(0, 0, self.type, self.extra_data)

    def save(self, indent, saved_blocks, void=False):
        line = ["Floor", self.x, self.y, self.type]
        return "\n" + "\t"*indent + " ".join(str(i) for i in line)

    def draw(self, draw_list, x, y, width, height, level, depth):
        draw_list.add_rect(x + width/10, y + height/10, x + width*9/10, y + height*9/10, 0x7fffffff, thickness=min(width,height)/20)

        if self.type == "PlayerButton":
            draw_eyes(draw_list, x + width/10, y + height/10, width * 8/10, height * 8/10, True, 0x7fffffff)
            other = self.parent.get_child(self.x, self.y) if self.parent else None
            if other and type(other) != Floor and other.player:
                draw_list.add_rect(x, y, x+width, y+height, 0xffffffff, thickness=min(width,height)/20)
        elif self.type == "Button":
            other = self.parent.get_child(self.x, self.y) if self.parent else None
            if other and type(other) != Floor and type(other) != Wall and not other.player:
                draw_list.add_rect(x, y, x+width, y+height, 0xffffffff, thickness=min(width,height)/20)

    def menu(self):
        if imgui.begin_menu("Change Floor Type"):
            if imgui.selectable("Button")[0]:
                self.type = "Button"
            if imgui.selectable("Player Button")[0]:
                self.type = "PlayerButton"
            if imgui.selectable("None")[0]:
                self.parent.remove_child(self)

            imgui.end_menu()

        if imgui.begin_menu("Edit Floor"):
            changed, value = imgui.input_text("Type", self.type, 64)
            if changed:
                self.type = value
            changed, value = imgui.input_text("Extra Data", self.extra_data, 64)
            if changed:
                self.extra_data = value

            imgui.end_menu()
    
    def empty_menu(parent, px, py):
        if imgui.begin_menu("Change Floor Type"):
            if imgui.selectable("Button")[0]:
                parent.place_child(px, py, Floor(px, py, "Button", ""))
            if imgui.selectable("Player Button")[0]:
                parent.place_child(px, py, Floor(px, py, "PlayerButton", ""))
            if imgui.selectable("None")[0]:
                pass # already none

            imgui.end_menu()

class Level:
    def __init__(self, name, data):
        self.name = name
        self.roots = []
        self.blocks = {}
        self.next_free = 0

        [self.metadata, data] = data.split("\n#\n")
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
                if not id in self.blocks:
                    self.blocks[id] = block
                else:
                    print("duplicate block with id " + id)
            elif block_type == "Ref":
                [x, y, id, exitblock, infexit, infexitnum, infenter, infenternum, infenterid, player, possessable, playerorder, fliph, floatinspace, specialeffect, *_] = args
                ref = Ref(x, y, id, exitblock, infexit, infexitnum, infenter, infenternum, infenterid, player, possessable, playerorder, fliph, floatinspace, specialeffect)
                if int(exitblock) and not int(infenter):
                    ref_exits[id] = ref
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
            parent.remove_child(ref)
            parent.place_child(ref.x, ref.y, self.blocks[id])

    def save(self):
        to_save = list(self.blocks.values())
        saved_blocks = []
        str = self.metadata + "\n#"
        # save blocks with no parents
        for block in to_save:
            if not block.parent:
                str += block.save(0, saved_blocks)
        for block in saved_blocks:
            if block in to_save:
                to_save.remove(block)
        saved_blocks = []
        # save blocks with recursive parents
        while len(to_save):
            str += to_save[0].save(0, saved_blocks, True)
            for block in saved_blocks:
                if block in to_save:
                    to_save.remove(block)
            saved_blocks = []

        return str.replace(".0", "")

    def edit_menu(self):
        changed, value = imgui.input_text_multiline("Metadata", self.metadata, 2048)
        if changed:
            self.metadata = value