import imgui
from level import *

cursor_held = None

samples = [
    Wall(0, 0, 0, 0, 0),
    Floor(0, 0, "Button", ""),
]

def show_editor(level, overlay_draw_list):
    global cursor_held
    hovered = None

    for block in level.blocks.values():
        if block.fillwithwalls:
            continue
        imgui.set_next_window_size(130, 150, condition=imgui.APPEARING)
        imgui.set_next_window_position(
            (30 + int(block.id) * 150) % (imgui.get_io().display_size.x - 150),
            50 + int((30 + int(block.id) * 150) / (imgui.get_io().display_size.x - 150))*50,
            condition=imgui.APPEARING
        )
        if imgui.begin(str(block.id) + " : " + level.name):
            if imgui.begin_child("nodrag", 0, 0, True, imgui.WINDOW_NO_MOVE):
                draw_list = imgui.get_window_draw_list()
                x, y = imgui.get_window_position()
                x += 2
                y += 2
                w, h = imgui.get_content_region_available()
                w += 12
                block.draw(draw_list, x, y, w, level)

                pos = imgui.get_mouse_position()
                px = int((pos.x - x) / (w / block.width))
                py = block.height - 1 - int((pos.y - y) / (w / block.width))
                if imgui.is_window_hovered():
                    hovered = (block, px, py)
                    if imgui.is_mouse_clicked():
                        pickup = block.get_child(px, py)
                        last_held = cursor_held
                        if cursor_held:
                            if imgui.get_io().key_shift:
                                to_place = cursor_held.copy(True)
                            else:
                                to_place = cursor_held
                                cursor_held = None
                            block.place_child(px, py, to_place)
                        if pickup:
                            if last_held and ((type(pickup) == Floor) != (type(last_held) == Floor)):
                                pass # only one is floor, they can coexist
                            else:
                                block.remove_child(pickup)
                                if imgui.get_io().key_shift:
                                    pickup = None
                                else:
                                    cursor_held = pickup

                if (level.menuing or hovered or [0])[0] == block:
                    if imgui.begin_popup_context_window():
                        if not level.menuing:
                            level.menuing = hovered
                        parent, px, py = level.menuing
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
                        level.menuing = None
            imgui.end_child()
        imgui.end()

    window_size = imgui.get_io().display_size
    imgui.set_next_window_size(window_size.x - 60, 80, condition=imgui.APPEARING)
    imgui.set_next_window_position(30, window_size.y - 110, condition=imgui.APPEARING)
    if imgui.begin("Palette"):
        if imgui.begin_child("nodrag", 0, 0, False, imgui.WINDOW_NO_MOVE):

            w, h = imgui.get_content_region_available()
            palette_width = int(w / 50)
            draw_list = imgui.get_window_draw_list()
            x, y = imgui.get_window_position()
            x += 2
            y += 2

            i = 0
            for sample in samples:
                sample.draw(draw_list, x + (i % palette_width)*50, y + int(i / palette_width)*50, 40, level)
                i += 1
            for id, block in sorted(level.blocks.items()):
                block.draw(draw_list, x + (i % palette_width)*50, y + int(i / palette_width)*50, 40, level)
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
                    if cursor_held:
                        cursor_held = None
                    else:
                        if i >= 0:
                            if i < len(samples):
                                cursor_held = samples[i].copy()
                            elif i < len(samples) + len(level.blocks):
                                cursor_held = sorted(level.blocks.items())[i - len(samples)][1].copy()
                            elif i == len(samples) + len(level.blocks):
                                while str(level.next_free) in level.blocks:
                                    level.next_free += 1
                                level.blocks[str(level.next_free)] = Block(0, 0, str(level.next_free), 5, 5, 0.6, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0)

            if (level.menuing or hovered or [0])[0] == None:
                if imgui.begin_popup_context_window():
                    if not level.menuing:
                        level.menuing = hovered
                    _, i = level.menuing
                    block = sorted(level.blocks.items())[i - len(samples)][1]
                    block.menu()
                    imgui.separator()
                    if imgui.selectable("Delete Block")[0]:
                        while len(block.children):
                            block.remove_child(block.children[0])
                        if block.parent:
                            block.parent.remove_child(block)
                        del level.blocks[block.id]
                    imgui.end_popup()
                else:
                    level.menuing = None
            imgui.end_child()
        imgui.end()

    if cursor_held:
        x, y = imgui.get_mouse_position()
        cursor_held.draw(overlay_draw_list, x - 10, y - 10, 20, level)