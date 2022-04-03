import imgui
from level import *

import glob
import os
import platform
import traceback
class Editor:
    def __init__(self):
        self.cursor_held = None

        self.samples = [
            Wall(0, 0, 0, 0, 0),
            Floor(0, 0, "Button", ""),
        ]
        
        if platform.system() == "Windows":
            self.levels_folder = "~\Appdata\LocalLow\Patrick Traynor\Patrick's Parabox\custom_levels"
        elif platform.system() == "Darwin": # Mac OS X
            self.levels_folder = "~/Library/Application Support/com.PatrickTraynor.PatricksParabox/custom_levels"
        elif platform.system() == "Linux":
            self.levels_folder = "~/.config/unity3d/Patrick Traynor/Patrick's Parabox"

        self.levels_search = ""
        self.files = None
        self.file_choice = 0
        self.level_name = None
        self.level = None

        self.error = None

    def main_loop(self):
        overlay_draw_list = imgui.get_overlay_draw_list()

        menu_choice = None
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                if imgui.menu_item("New")[0]:
                    self.level = Level("untitled", "version 4\n#\n")
                if imgui.menu_item("Open...")[0]:
                    menu_choice = "file.open"
                if imgui.menu_item("Save", enabled = self.level != None)[0]:
                    save_data = self.level.save()
                    with open(self.level_name + ".txt", "w" if os.path.exists(self.level_name + ".txt") else "x") as file:
                        file.write(save_data)
                if imgui.menu_item("Save As...", enabled = self.level != None)[0]:
                    menu_choice = "file.saveas"
                imgui.separator()
                if imgui.menu_item("Quit")[0]:
                    return False

                imgui.end_menu()
            
            if imgui.begin_menu("Edit", self.level != None):
                self.level.edit_menu()
                imgui.end_menu()
            imgui.end_main_menu_bar()

        if menu_choice == "file.open":
            imgui.open_popup("file.open")
            self.file_choice = 0
        if imgui.begin_popup("file.open"):
            folder_changed, self.levels_folder = imgui.input_text("Levels folder", self.levels_folder, 256)
            search_changed, self.levels_search = imgui.input_text("Search", self.levels_search, 256)
            try:
                if folder_changed or not self.files:
                    os.chdir(os.path.expanduser(self.levels_folder))
                    search_changed = True
                if search_changed:
                    self.files = glob.glob(self.levels_search + "*.txt")
                    self.files = [file.removesuffix(".txt") for file in self.files]

                _, self.file_choice = imgui.listbox("Levels", self.file_choice, self.files)

                if imgui.button("Open"):
                    self.level_name = self.files[self.file_choice]
                    with open(self.level_name + ".txt") as file:
                        self.level = Level(self.level_name, file.read())
                    imgui.close_current_popup()

            except Exception as e:
                imgui.text_ansi("Failed to load levels folder...")
                imgui.text_ansi(str(e))
                self.error = traceback.format_exc()
            imgui.end_popup()
        
        if menu_choice == "file.saveas":
            imgui.open_popup("file.saveas")
            self.file_choice = 0
        if imgui.begin_popup("file.saveas"):
            folder_changed, self.levels_folder = imgui.input_text("Levels folder", self.levels_folder, 256)
            name_changed, self.level_name = imgui.input_text("Name", self.level_name, 256)
            try:
                if folder_changed or not self.files:
                    os.chdir(os.path.expanduser(self.levels_folder))
                    self.files = glob.glob("*.txt")
                    self.files = [file.removesuffix(".txt") for file in self.files]
                if name_changed:
                    self.file_choice = -1

                clicked, self.file_choice = imgui.listbox("Levels", self.file_choice, self.files)
                if clicked:
                    self.level_name = self.files[self.file_choice]

                new = self.file_choice == -1
                if imgui.button("Save New" if new else "Overwrite"):
                    save_data = self.level.save()
                    with open(self.level_name + ".txt", "x" if new else "w") as file:
                        file.write(save_data)
                    imgui.close_current_popup()

            except Exception as e:
                imgui.text_ansi("Failed to load levels folder...")
                imgui.text_ansi(str(e))
                self.error = traceback.format_exc()
            imgui.end_popup()

        hovered = None

        if self.level:
            for block in self.level.blocks.values():
                if block.fillwithwalls:
                    continue
                imgui.set_next_window_size(130, 150, condition=imgui.APPEARING)
                imgui.set_next_window_position(
                    (30 + int(block.id) * 150) % (imgui.get_io().display_size.x - 150),
                    50 + int((30 + int(block.id) * 150) / (imgui.get_io().display_size.x - 150))*50,
                    condition=imgui.APPEARING
                )
                if imgui.begin(str(block.id) + " : " + self.level.name):
                    if imgui.begin_child("nodrag", 0, 0, True, imgui.WINDOW_NO_MOVE):
                        draw_list = imgui.get_window_draw_list()
                        x, y = imgui.get_window_position()
                        x += 2
                        y += 2
                        w, h = imgui.get_content_region_available()
                        w += 12
                        block.draw(draw_list, x, y, w, self.level)

                        pos = imgui.get_mouse_position()
                        px = int((pos.x - x) / (w / block.width))
                        py = block.height - 1 - int((pos.y - y) / (w / block.width))
                        if imgui.is_window_hovered():
                            hovered = (block, px, py)
                            if imgui.is_mouse_clicked():
                                pickup = block.get_child(px, py)
                                last_held = self.cursor_held
                                if self.cursor_held:
                                    if imgui.get_io().key_shift:
                                        to_place = self.cursor_held.copy(True)
                                    else:
                                        to_place = self.cursor_held
                                        self.cursor_held = None
                                    block.place_child(px, py, to_place)
                                if pickup:
                                    if last_held and ((type(pickup) == Floor) != (type(last_held) == Floor)):
                                        pass # only one is floor, they can coexist
                                    else:
                                        block.remove_child(pickup)
                                        if imgui.get_io().key_shift:
                                            pickup = None
                                        else:
                                            self.cursor_held = pickup

                        if (self.level.menuing or hovered or [0])[0] == block:
                            if imgui.begin_popup_context_window():
                                if not self.level.menuing:
                                    self.level.menuing = hovered
                                parent, px, py = self.level.menuing
                                has_floor = False
                                first = True
                                for block in parent.get_children(px, py):
                                    if first:
                                        first = False
                                    else:
                                        imgui.separator()
                                    if type(block) == Floor:
                                        has_floor = True
                                    block.menu()
                                if not has_floor:
                                    if not first:
                                        imgui.separator()
                                    Floor.empty_menu(parent, px, py)
                                imgui.end_popup()
                            else:
                                self.level.menuing = None
                    imgui.end_child()
                imgui.end()

            window_size = imgui.get_io().display_size
            imgui.set_next_window_size(window_size.x - 60, 80, condition=imgui.APPEARING)
            imgui.set_next_window_position(30, window_size.y - 110, condition=imgui.APPEARING)
            if imgui.begin("Palette"):
                if imgui.begin_child("nodrag", 0, 0, False, imgui.WINDOW_NO_MOVE):

                    w, h = imgui.get_content_region_available()
                    palette_width = int(w / 50)
                    if palette_width == 0:
                        palette_width = 1 # prevent divide by 0 error when palette is too skinny
                    draw_list = imgui.get_window_draw_list()
                    x, y = imgui.get_window_position()
                    x += 2
                    y += 2

                    i = 0
                    for sample in self.samples:
                        sample.draw(draw_list, x + (i % palette_width)*50, y + int(i / palette_width)*50, 40, self.level)
                        i += 1
                    for id, block in sorted(self.level.blocks.items()):
                        block.draw(draw_list, x + (i % palette_width)*50, y + int(i / palette_width)*50, 40, self.level)
                        i += 1
                    px, py = x + (i % palette_width)*50, y + int(i / palette_width)*50
                    draw_list.add_rect(px, py, px + 40, py + 40, 0x7fffffff, thickness=2)
                    draw_list.add_rect_filled(px + 10, py + 18, px + 30, py + 22, 0xffafafaf)
                    draw_list.add_rect_filled(px + 18, py + 10, px + 22, py + 30, 0xffafafaf)

                    if imgui.is_window_hovered():
                        pos = imgui.get_mouse_position()
                        px = int((pos.x - x) / 50)
                        py = int((pos.y - y) / 50)
                        i = px + py*palette_width
                        hovered = (None, i)
                        if imgui.is_mouse_clicked():
                            if self.cursor_held:
                                self.cursor_held = None
                            else:
                                if i >= 0:
                                    if i < len(self.samples):
                                        self.cursor_held = self.samples[i].copy()
                                    elif i < len(self.samples) + len(self.level.blocks):
                                        self.cursor_held = sorted(self.level.blocks.items())[i - len(self.samples)][1].copy()
                                    elif i == len(self.samples) + len(self.level.blocks):
                                        while str(self.level.next_free) in self.level.blocks:
                                            self.level.next_free += 1
                                        self.level.blocks[str(self.level.next_free)] = Block(0, 0, str(self.level.next_free), 5, 5, 0.6, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0)

                    if (self.level.menuing or hovered or [0])[0] == None:
                        if imgui.begin_popup_context_window():
                            if not self.level.menuing:
                                self.level.menuing = hovered
                            _, i = self.level.menuing
                            if i < len(self.samples):
                                if type(self.samples[i]) == Wall:
                                    if imgui.selectable("Normal Wall")[0]:
                                        self.cursor_held = self.samples[i].copy()
                                    if imgui.selectable("Possessable Wall")[0]:
                                        self.cursor_held = self.samples[i].copy()
                                        self.cursor_held.possessable = 1
                                    if imgui.selectable("Player Wall")[0]:
                                        self.cursor_held = self.samples[i].copy()
                                        self.cursor_held.player = 1
                                        self.cursor_held.possessable = 1
                                elif type(self.samples[i]) == Floor:
                                    if imgui.selectable("Normal Button")[0]:
                                        self.cursor_held = self.samples[i].copy()
                                    if imgui.selectable("Player Button")[0]:
                                        self.cursor_held = self.samples[i].copy()
                                        self.cursor_held.type = "PlayerButton"
                            elif i < len(self.samples) + len(self.level.blocks):
                                block = sorted(self.level.blocks.items())[i - len(self.samples)][1]
                                block.menu()
                                imgui.separator()
                                if imgui.selectable("Duplicate Block")[0]:
                                    while str(self.level.next_free) in self.level.blocks:
                                        self.level.next_free += 1
                                    new = self.level.blocks[str(self.level.next_free)] = Block(0, 0, str(self.level.next_free), block.width, block.height, block.hue, block.sat, block.val, block.zoomfactor, block.fillwithwalls, block.player, block.possessable, block.playerorder, block.fliph, block.floatinspace, block.specialeffect)
                                    for child in block.children:
                                        new.place_child(child.x, child.y, child.copy())
                                if imgui.selectable("Delete Block")[0]:
                                    while len(block.children):
                                        block.remove_child(block.children[0])
                                    if block.parent:
                                        block.parent.remove_child(block)
                                    del self.level.blocks[block.id]
                            elif i < len(self.samples) + len(self.level.blocks) + 1:
                                while str(self.level.next_free) in self.level.blocks:
                                    self.level.next_free += 1
                                if imgui.selectable("Add Enterable Block")[0]:
                                    self.level.blocks[str(self.level.next_free)] = Block(0, 0, str(self.level.next_free), 5, 5, 0.6, 0.8, 1, 1, 0, 0, 0, 0, 0, 0, 0)
                                if imgui.selectable("Add Player")[0]:
                                    self.level.blocks[str(self.level.next_free)] = Block(0, 0, str(self.level.next_free), 1, 1, 0.9, 1, 0.7, 1, 1, 1, 1, 0, 0, 0, 0)
                                if imgui.selectable("Add Solid Box")[0]:
                                    self.level.blocks[str(self.level.next_free)] = Block(0, 0, str(self.level.next_free), 1, 1, 0.1, 0.8, 1, 1, 1, 0, 0, 0, 0, 0, 0)
                            imgui.end_popup()
                        else:
                            self.level.menuing = None
                    imgui.end_child()
                imgui.end()

            if self.cursor_held:
                x, y = imgui.get_mouse_position()
                self.cursor_held.draw(overlay_draw_list, x - 10, y - 10, 20, self.level)

        if self.error:
            imgui.text_ansi(self.error)

        return True