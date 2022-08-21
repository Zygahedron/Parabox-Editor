import imgui
from level import *
import style, glob, os, platform, traceback, colorsys, math, webbrowser, time
from pathlib import Path
from state import usefulmod, Design
import hubtools
class Editor:
    def __init__(self):
        self.cursor_held = None
        self.last_hovered = None
        self.hovered = None
        self.menuing = None
        self.clicked = None
        self.help_open = False
        self.new_size = [5,5]
        self.samples = [
            Wall(0, 0, 0, 0, 0, "_"),
            Floor(0, 0, "Button", ""),
            Block(None, 0, 0, "-1", 1, 1, 0.1, 0.8, 1, 1, 1, 0, 0, 0, 0, 0, 0),
            Block(None, 0, 0, "-1", 1, 1, 0.9, 1, 0.7, 1, 1, 1, 1, 0, 0, 0, 0),
        ]
        self.hub = hubtools.HubTools(self)
        self.levels_folder = ""
        if platform.system() == "Windows":
            self.levels_folder = "~\Appdata\LocalLow\Patrick Traynor\Patrick's Parabox\custom_levels"
        elif platform.system() == "Darwin": # Mac OS X
            self.levels_folder = "~/Library/Application Support/com.PatrickTraynor.PatricksParabox/custom_levels"
        elif platform.system() == "Linux":
            self.levels_folder = "~/.config/unity3d/Patrick Traynor/Patrick's Parabox/custom_levels"
        self.levels_folder_base = self.levels_folder
        self.levels_search = ""
        self.files = None
        self.file_choice = -1
        self.level_name = None
        self.level = None
        self.code_check = []
        self.did_code = False
        self.error = None
        self.open_warn = False
        self.level_invalid = False

        imgui.get_io().ini_file_name = b""

    def loadlevel(self):
        # Reset hubtools when we load a level
        self.hub = hubtools.HubTools(self)
        kwargs = {}
        self.level_name = self.files[self.file_choice]
        hub_parent = False
        level_number = 0
        credits = ''
        difficulty = 0
        possess_vfx = 0
        if self.level_name != 'hub.txt':
            hub_parent = os.path.exists('puzzle_data.txt')
        else:
            try:
                with open('credits.txt','r') as f:
                    credits = f.read()
            except:
                credits = ""
        if os.path.exists("area_data.txt"):
            kwargs["area_data"] = open('area_data.txt', 'r').read()
        if hub_parent:
            try:
                with open('puzzle_data.txt','r') as file:
                    puzzle_data = {line.split(' ')[0]:line.split(' ')[1:] for line in file.read().split('\n')}
                difficulty, possess_vfx, level_number = [int(n) for n in puzzle_data[Path(self.level_name).stem]]
            except (FileNotFoundError, KeyError):
                pass
        with open(self.level_name) as file:
            try:
                self.level = Level(self.level_name, file.read(), level_number, hub_parent, difficulty, bool(possess_vfx), credits, **kwargs)
            except Exception as Err:
                print(traceback.format_exc())
                self.level_invalid=True
                
                
    def save_level(self):
        save_data, is_hub, parent, level_number, areas, credits, possess_fx, difficulty = self.level.save()
        with open(self.level_name, "w" if os.path.exists(self.level_name) else "x") as file:
            file.write(save_data)
        if is_hub:
            with open('credits.txt','x' if not os.path.exists('credits.txt') else 'w') as f:
                f.write(credits)
            with open('area_data.txt','x' if not os.path.exists('area_data.txt') else 'w') as f:
                f.write('\n'.join([f'{name.replace(" ","_")} {music}' if name is not None else '' for name, music in areas]))
            if not os.path.exists('save0.txt'):
                with open('save0.txt','x'):
                    pass
            if len(areas) == 0:
                self.open_warn = True
        # TODO figure out what parent is
        elif parent:
            if not os.path.exists('puzzle_data.txt'):
                with open('puzzle_data.txt','x'):
                    pass
                puzzle_data = {}
            else:
                with open('puzzle_data.txt', "r") as file:
                    puzzle_data = {line.split(' ',1)[0]:line.split(' ',1)[1] for line in file.read().split('\n')}
            # Edits puzzle data for one file (no existence check needed)
            puzzle_data[Path(self.level_name).stem] = f'{difficulty} {possess_fx} {level_number}'
            with open('puzzle_data.txt', "w") as file:
                file.write('\n'.join([key + ' ' + value for key,value in puzzle_data.items()]))

    def main_loop(self, keyboard):
        overlay_draw_list = imgui.get_overlay_draw_list()
        io = imgui.get_io()
        if self.did_code:
            imgui.get_style().colors[imgui.COLOR_TEXT] = list(colorsys.hsv_to_rgb((time.time()/5)%1,1,1))+[1]
        menu_choice = None
        # Main Menu Bar
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                if imgui.menu_item("New", "ctrl+n")[0]:
                    self.level = Level("untitled", "version 4\n#\n")
                    self.level_name = None
                if imgui.menu_item("Open...", "ctrl+o")[0]:
                    menu_choice = "file.open"
                if imgui.menu_item("Save", "ctrl+s", enabled = (self.level != None and self.files != None and self.level_name != None))[0]:
                    self.save_level()
                if imgui.menu_item("Save As...", "ctrl+shift+s", enabled = self.level != None )[0]:
                    menu_choice = "file.saveas"
                imgui.separator()
                if imgui.menu_item("Quit")[0]:
                    return False
                imgui.end_menu()
            
            if imgui.begin_menu("Edit", self.level != None):
                self.level.edit_menu()
                imgui.end_menu()
            # Show hub tools menu and store data in hubstate
            if self.level and self.level.is_hub and imgui.begin_menu("Hub Tools"):
                self.hub.menu()
                imgui.end_menu()
            
            if imgui.begin_menu("Extra"):
                # UsefulMod Extra
                changed, value = imgui.checkbox("Enable UsefulMod", usefulmod.enabled)
                if changed:
                    usefulmod.enable(floor_types, value)
                changed, value = imgui.checkbox("Gridlines", Design.grid)
                if changed:
                    Design.grid = value
                changed, value = imgui.checkbox("True Duplication", Design.true_dupe)
                if changed:
                    Design.true_dupe = value
                if Design.grid:
                    if imgui.begin_menu("Gridlines Style"):
                        changed, value = imgui.color_edit4("Gridline Color",*Design.gridstyle)
                        if changed:
                            Design.gridstyle = value
                        changed, value = imgui.input_int("Gridline Width", Design.gridwidth)
                        if changed:
                            Design.gridwidth = value
                        imgui.end_menu()
                changed, value = imgui.checkbox("Block Debug Info", Design.placedebug)
                if changed:
                    Design.placedebug = value
                imgui.end_menu()
            
            
            if imgui.begin_menu("Help"):
                imgui.bullet_text("To create a new level, go to File > New.")
                imgui.bullet_text("Left click a tile in the palette to grab it, or click the plus to make a new box.")
                imgui.bullet_text("Holding down shift while placing a tile will let you draw multiple tiles at once,\nand while placing a box, it will let you place a clone of said box.")
                imgui.bullet_text("Holding down \"a\" while placing a tile will let you draw multiple tiles in one spot")
                imgui.bullet_text("Right click tiles, in the palette or in a box, to edit them.")
                imgui.bullet_text("If you're confused with making hubs, watch")
                imgui.same_line()
                if imgui.small_button("these videos"):
                    webbrowser.open('https://media.discordapp.net/attachments/958461471514312735/979195146287591434/Patricks_Parabox_2022-05-25_20-28-02.mp4')
                    time.sleep(0.05)
                    webbrowser.open('https://media.discordapp.net/attachments/958461471514312735/979195142873419836/Zygans_Parabox_Editor_2022-05-25_20-23-06.mp4')
                imgui.same_line()
                imgui.text("to get a gist of it.")
                imgui.indent()
                imgui.bullet_text("Custom hubs need")
                imgui.same_line()
                if imgui.small_button("this mod"):
                    webbrowser.open('https://github.com/plokmijnuhby/CustomHubs')
                imgui.same_line()
                imgui.text("to open in-game.")
                imgui.end_menu()
            imgui.end_main_menu_bar()
        # Shortcuts
        if io.key_ctrl:
            if keyboard.n.pressed:
                self.level = Level("untitled", "version 4\n#\n")
            if keyboard.o.pressed:
                menu_choice = "file.open"
            if keyboard.s.pressed and self.level != None:
                if io.key_shift or self.level_name == None:
                    menu_choice = "file.saveas"
                elif self.files != None:
                    self.save_level()
        # Secret 
        if keyboard.up.pressed:
            self.code_check.append('up')
        if keyboard.down.pressed:
            self.code_check.append('down')
        if keyboard.left.pressed:
            self.code_check.append('left')
        if keyboard.right.pressed:
            self.code_check.append('right')
        if keyboard.b.pressed:
            self.code_check.append('b')
        if keyboard.a.pressed:
            self.code_check.append('a')
        if keyboard.enter.pressed:
            self.code_check.append('enter')
        if len(self.code_check) == 11:
            if all([a==b for a, b in zip(self.code_check,['up','up','down','down','left','right','left','right','b','a','enter'])]):
                imgui.open_popup("secret.gui")
                self.did_code = not self.did_code
                if not self.did_code:
                    style.set(imgui.get_style())
                self.code_check = []
            else:
                self.code_check = self.code_check[1:]
        # Popup Initializers
        if self.open_warn:
            self.open_warn = False
            imgui.open_popup('save.hub.no_area_warn')
        if self.level_invalid:
            self.level_invalid = False
            imgui.open_popup('file.failed')
        if usefulmod.warn:
            usefulmod.warn = False
            imgui.open_popup("extra.useful")
        # Popups
        if imgui.begin_popup("secret.gui"):
            imgui.push_style_color(imgui.COLOR_TEXT, .702, 0, .42)
            imgui.text("""+------------------------+
|                        |
|                        |
|                        |
|     #            #     |
|    ###          ###    |
|   ## ##        ## ##   |
|                        |
|                        |
|       ##  ##  ##       |
|       ##########       |
|        ###  ###        |
|                        |
|                        |
+------------------------+

""")
            imgui.pop_style_color(1)
            imgui.text('Editor made with love by Zygan#0404\nInput the code again to turn off rainbow mode.')
            imgui.end_popup()
        if imgui.begin_popup('save.hub.no_area_warn'):
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 1.0, 0.0)
            imgui.text('   / \   ')
            imgui.text('  / | \  ')
            imgui.text(' /  .  \\ ')
            imgui.text('/_______\\')
            imgui.pop_style_color(1)
            imgui.text('')
            imgui.text('This hub is invalid because it has no area data.')
            imgui.text('Add area data like this:')
            imgui.text('1. Make a new block (Preferably with ID of -1 and/or with Special Effect 11)')
            imgui.text('2. Add a clone to every area in your hub to this block')
            imgui.text('3. Edit each clone to add the area name and music')
            imgui.end_popup()
        if imgui.begin_popup('file.failed'):
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 1.0, 0.0)
            imgui.text('   / \   ')
            imgui.text('  / | \  ')
            imgui.text(' /  .  \\ ')
            imgui.text('/_______\\')
            imgui.pop_style_color(1)
            imgui.text('')
            imgui.text('Invalid level file')
            imgui.end_popup()
        if imgui.begin_popup('extra.useful'):
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 1.0, 0.0)
            imgui.text('   / \   ')
            imgui.text('  / | \  ')
            imgui.text(' /  .  \\ ')
            imgui.text('/_______\\')
            imgui.pop_style_color(1)
            imgui.text('')
            imgui.text('UsefulMod level detected. Please Enable UsefulMod')
            imgui.text('or remove UsefulMod features from the level.')
            if imgui.button('Enable UsefulMod now'):
                usefulmod.enable(floor_types)
                imgui.close_current_popup()
            # Purge Features
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.0, 0.0)
            if imgui.button('Reload removing UsefulMod features'):
                usefulmod.purge = True
                self.loadlevel()
                imgui.close_current_popup()
            imgui.pop_style_color(1)
            
            imgui.end_popup()
        if menu_choice == "file.open":
            imgui.open_popup("file.open")
            self.file_choice = 0
        if imgui.begin_popup("file.open"):
            folder_changed, self.levels_folder = imgui.input_text("Levels folder", self.levels_folder, 256)
            search_changed, self.levels_search = imgui.input_text("Search", self.levels_search, 256)
            if folder_changed or not self.files:
                try:
                    os.chdir(os.path.expanduser(self.levels_folder))
                except:
                    os.chdir(os.path.expanduser(self.levels_folder_base))
                    self.levels_folder = self.levels_folder_base
                search_changed = True
            # TODO Enable non txt files from Extra
            if search_changed:
                self.files = ['..'] + glob.glob(self.levels_search + "*.txt") + glob.glob(self.levels_search + "*" + os.sep)
            clicked, self.file_choice = imgui.listbox("Levels", self.file_choice, 
            [path for path in self.files])
            if clicked:
                if not self.files[self.file_choice].endswith('.txt'):
                    self.levels_folder = os.path.relpath(os.path.join(self.levels_folder, self.files[self.file_choice]))
                    self.file_choice = 0
                    os.chdir(os.path.expanduser(self.levels_folder))
                    self.files = ['..'] + glob.glob(self.levels_search + "*.txt") + glob.glob(self.levels_search + "*" + os.sep)
                else:
                    # May need to catch here for non-levels as hubtools
                    self.loadlevel()
                    imgui.close_current_popup()
            imgui.end_popup()
        
        if menu_choice == "file.saveas":
            imgui.open_popup("file.saveas")
            self.file_choice = 0
            self.files = None
        if imgui.begin_popup("file.saveas"):
            if not self.level_name: self.level_name = "untitled.txt"
            folder_changed, self.levels_folder = imgui.input_text("Levels folder", self.levels_folder, 256)
            name_changed, self.level_name = imgui.input_text("Name", self.level_name, 256)
            try:
                if folder_changed or self.files is None:
                    try:
                        os.chdir(os.path.expanduser(self.levels_folder))
                    except:
                        os.chdir(os.path.expanduser(self.levels_folder_base))
                        self.levels_folder = self.levels_folder_base
                    self.files = ['..'] + glob.glob(self.levels_search + "*.txt") + glob.glob(self.levels_search + "*" + os.sep)
                if name_changed:
                    self.file_choice = -1
                clicked, self.file_choice = imgui.listbox("Levels", self.file_choice, self.files)
                is_directory = not self.files[self.file_choice].endswith('.txt')
                if clicked:
                    if is_directory:
                        self.levels_folder = os.path.relpath(os.path.join(self.levels_folder, self.files[self.file_choice]))
                        self.file_choice = 0
                        os.chdir(os.path.expanduser(self.levels_folder))
                        self.files = ['..'] + glob.glob(self.levels_search + "*.txt") + glob.glob(self.levels_search + "*" + os.sep)
                        clicked = False
                        self.file_choice = -1
                    else:
                        self.level_name = self.files[self.file_choice]
                if self.level_name in self.files:
                    self.file_choice = self.files.index(self.level_name)
                new = self.file_choice == -1
                if (imgui.button("Save New") if new else False) or clicked:
                    self.save_level()
                    imgui.close_current_popup()

            except Exception as e:
                imgui.text_ansi("Failed to load levels folder...")
                imgui.text_ansi(str(e))
                self.error = traceback.format_exc()
            imgui.end_popup()

        self.last_hovered = self.hovered
        self.hovered = None
        # use hubstate to determine what is open and what windows we need to make
        self.hub.show()
        if self.level:
            try:
                for block in self.level.blocks.values():
                    if block.fillwithwalls or block.width <= 0 or block.height <= 0:
                        if self.menuing and self.menuing[0] == block:
                            self.menuing = None
                        continue
                    if self.hub.hideBlocks():
                        continue
                    imgui.set_next_window_size(block.window_size, round((block.window_size - 24) / block.width * block.height + 43))
                    imgui.set_next_window_position(
                        (30 + int(block.id) * 150) % (imgui.get_io().display_size.x - 150),
                        50 + int((30 + int(block.id) * 150) / (imgui.get_io().display_size.x - 150))*200,
                        condition=imgui.APPEARING
                    )
                    if imgui.begin(str(block.id) + " : " + self.level.name):
                        if imgui.begin_child("nodrag", 0, 0, True, imgui.WINDOW_NO_MOVE):
                            draw_list = imgui.get_window_draw_list()
                            x, y = imgui.get_window_position()
                            x += 4
                            y += 4
                            w, h = imgui.get_content_region_available()
                            w += 8
                            block.draw(draw_list, x, y, w, w / block.width * block.height, self.level, -1, block.fliph)
                            pos = imgui.get_mouse_position()
                            px = int((pos.x - x) / (w / block.width))
                            py = block.height - int(math.ceil((pos.y - y) / max((h / block.height),0.01)))
                            shift = imgui.get_io().key_shift
                            if imgui.is_window_hovered():
                                self.hovered = (block, px, py)
                                if imgui.is_mouse_clicked() or (shift and imgui.is_mouse_down() and self.hovered != self.last_hovered):
                                    pickup = block.get_child(px, py)
                                    last_held = self.cursor_held
                                    if self.cursor_held:
                                        if shift:
                                            to_place = self.cursor_held.copy(self.level, True)
                                        else:
                                            to_place = self.cursor_held
                                            self.cursor_held = None
                                        block.place_child(px, py, to_place)
                                    if pickup:
                                        if last_held and ((type(pickup) == Floor) != (type(last_held) == Floor)) or keyboard.a.down:
                                            pass # only one is floor, they can coexist
                                        else:
                                            block.remove_child(pickup)
                                            if shift:
                                                pickup = None
                                            else:
                                                self.cursor_held = pickup
                                                self.clicked = self.hovered
                                elif not shift and imgui.is_mouse_released() and self.clicked and self.cursor_held and self.hovered != self.clicked:
                                    clash = block.get_child(px, py)
                                    if not clash or ((type(clash) == Floor) != (type(self.cursor_held) == Floor)):
                                        block.place_child(px, py, self.cursor_held)
                                        self.cursor_held = None
                                if imgui.is_mouse_released():
                                    self.clicked = None
                            if (self.menuing or self.hovered or [0])[0] == block:
                                if imgui.begin_popup_context_window():
                                    if not self.menuing:
                                        self.menuing = self.hovered
                                    parent, px, py = self.menuing
                                    has_floor = False
                                    first = True
                                    for block in parent.get_children(px, py):
                                        if first:
                                            first = False
                                        else:
                                            imgui.separator()
                                        if type(block) == Floor:
                                            has_floor = True
                                        block.menu(self.level)
                                    if not has_floor:
                                        if not first:
                                            imgui.separator()
                                        Floor.empty_menu(self.level, parent, px, py)
                                    imgui.end_popup()
                                else:
                                    self.menuing = None
                        imgui.end_child()
                        if type(block) == Block and block.window_size != imgui.get_window_width():
                            block.window_size = imgui.get_window_width()
                    imgui.end()
            except RuntimeError:
                pass

            window_size = imgui.get_io().display_size
            imgui.set_next_window_size(window_size.x - 60, 80, condition=imgui.APPEARING)
            imgui.set_next_window_position(30, window_size.y - 110, condition=imgui.APPEARING)
            if not self.hub.hidePalette() and imgui.begin("Palette"):
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
                        sample.draw(draw_list, x + (i % palette_width)*50, y + int(i / palette_width)*50, 40, 40, self.level, -0.5, False)
                        i += 1
                    for block in [self.level.blocks[i] for i in sorted(self.level.blocks.keys())]:
                        block.draw(draw_list, x + (i % palette_width)*50, y + int(i / palette_width)*50, 40, 40, self.level, -0.5, block.fliph)
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
                        self.hovered = (None, i)
                        if imgui.is_mouse_clicked():
                            if self.cursor_held:
                                self.cursor_held = None
                            else:
                                if i >= 0:
                                    if i < len(self.samples):
                                        self.cursor_held = self.samples[i].copy(self.level)
                                        self.clicked = self.hovered
                                    elif i < len(self.samples) + len(self.level.blocks):
                                        self.cursor_held = sorted(self.level.blocks.items())[i - len(self.samples)][1].copy(self.level)
                                        self.clicked = self.hovered
                                    elif i == len(self.samples) + len(self.level.blocks):
                                        while self.level.next_free in self.level.blocks:
                                            self.level.next_free += 1
                                        self.level.blocks[self.level.next_free] = Block(self.level, 0, 0, self.level.next_free, 5, 5, 0.6, 0.8, 1, 1, 0, 0, 0, 0, 0, 0, 0)

                    if (self.menuing or self.hovered or [0])[0] == None:
                        if imgui.begin_popup_context_window():
                            if not self.menuing:
                                self.menuing = self.hovered
                            _, i = self.menuing
                            if i < len(self.samples):
                                if type(self.samples[i]) == Wall:
                                    if imgui.selectable("Normal Wall")[0]:
                                        self.cursor_held = self.samples[i].copy(self.level)
                                    if imgui.selectable("Possessable Wall")[0]:
                                        self.cursor_held = self.samples[i].copy(self.level)
                                        self.cursor_held.possessable = 1
                                    if imgui.selectable("Player Wall")[0]:
                                        self.cursor_held = self.samples[i].copy(self.level)
                                        self.cursor_held.player = 1
                                        self.cursor_held.possessable = 1
                                elif type(self.samples[i]) == Floor:
                                    if imgui.selectable("Normal Button")[0]:
                                        self.cursor_held = self.samples[i].copy(self.level)
                                    if imgui.selectable("Player Button")[0]:
                                        self.cursor_held = self.samples[i].copy(self.level)
                                        self.cursor_held.type = "PlayerButton"
                                elif self.samples[i].player:
                                    pass
                                else:
                                    for color in Palette.pals[0].colors:
                                        h, s, v = Palette.pals[self.level.metadata["custom_level_palette"]].get_color(color)
                                        r, g, b = colorsys.hsv_to_rgb(h, s, v)
                                        if imgui.color_button(str(color), r, g, b, 1, width=20, height=20):
                                            self.cursor_held = self.samples[i].copy(self.level)
                                            self.cursor_held.hue, self.cursor_held.sat, self.cursor_held.val = color
                                            self.clicked = self.hovered
                                            self.menuing = None
                                        imgui.same_line()
                                    imgui.new_line()
                            elif i < len(self.samples) + len(self.level.blocks):
                                block = sorted(self.level.blocks.items())[i - len(self.samples)][1]
                                pickup = block.palette_menu(self.level)
                                if pickup:
                                    self.cursor_held = pickup
                                imgui.separator()
                                if imgui.selectable("Duplicate Block")[0]:
                                    while self.level.next_free in self.level.blocks:
                                        self.level.next_free += 1
                                    self.level.blocks[self.level.next_free] = block.full_copy(self.level, self.level.next_free)
                                if imgui.selectable("Delete Block")[0]:
                                    while len(block.children):
                                        block.remove_child(block.children[0])
                                    if block.parent:
                                        block.parent.remove_child(block)
                                    self.level.next_free = min(self.level.next_free, block.id)
                                    try:
                                        del self.level.blocks[block.id]
                                    except KeyError:
                                        pass
                            elif i < len(self.samples) + len(self.level.blocks) + 1:
                                while self.level.next_free in self.level.blocks:
                                    self.level.next_free += 1
                                changed, value = imgui.input_int("Width", self.new_size[0])
                                changed2, value2 = imgui.input_int("Height", self.new_size[1])
                                if changed and value >= 0:
                                    self.new_size[0] = value
                                if changed2 and value2 >= 0:
                                    self.new_size[1] = value2
                                for color in Palette.pals[0].colors:
                                    h, s, v = Palette.pals[self.level.metadata["custom_level_palette"]].get_color(color)
                                    r, g, b = colorsys.hsv_to_rgb(h, s, v)
                                    if imgui.color_button(str(color), r, g, b, 1, width=20, height=20):
                                        self.level.blocks[self.level.next_free] = Block(self.level, 0, 0, self.level.next_free, *self.new_size, color[0], color[1], color[2], 1, any([n==0 for n in self.new_size]), 0, 0, 0, 0, 0, 0)
                                        self.menuing = None
                                    imgui.same_line()
                                imgui.new_line()
                            imgui.end_popup()
                        else:
                            self.menuing = None
                imgui.end_child()
                imgui.end()

            if self.cursor_held:
                x, y = imgui.get_mouse_position()
                self.cursor_held.draw(overlay_draw_list, x - 10, y - 10, 20, 20, self.level, 0, False)
        # Error Debug
        # TODO Change error debug mechanisms
        if self.error:
            imgui.open_popup('Debug')
            if imgui.begin_popup('Debug'):
                imgui.text_ansi(self.error)
                imgui.end_popup()
            if imgui.is_mouse_clicked():
                self.error = None

        return True

    
