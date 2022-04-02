# -*- coding: utf-8 -*-
import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer

import glob
import os
import platform
import traceback

from level import *
from editor import *

# TODO: pick different default per os
if platform.system() == "Windows":
    levels_folder = "~\Appdata\LocalLow\Patrick Traynor\Patrick's Parabox\custom_levels"
elif platform.system() == "Darwin": # Mac OS X
    levels_folder = "~/Library/Application Support/com.PatrickTraynor.PatricksParabox/custom_levels"
elif platform.system() == "Linux":
    levels_folder = "~/.config/unity3d/Patrick Traynor/Patrick's Parabox"

def main():
    global levels_folder
    
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    levels_search = ""
    files = None
    open_level_name = ""
    open_level = None
    error = None

    cursor_held = None

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        overlay_draw_list = imgui.get_overlay_draw_list()

        menu_choice = None
        with imgui.begin_main_menu_bar():
            with imgui.begin_menu("File", True) as menu:
                if menu.opened:
                    if imgui.menu_item("Open...")[0]:
                        menu_choice = "file.open"
                    if imgui.menu_item("Save", enabled = open_level != None)[0]:
                        save_data = open_level.save()
                        with open(open_level_name + ".txt", "x" if new else "w") as file:
                            file.write(save_data)
                    if imgui.menu_item("Save As...", enabled = open_level != None)[0]:
                        menu_choice = "file.saveas"
                    imgui.separator()
                    if imgui.menu_item("Quit")[0]:
                        break # while not window_should_close

        if menu_choice == "file.open":
            imgui.open_popup("file.open")
            file_choice = 0
        with imgui.begin_popup("file.open") as popup:
            if popup.opened:
                folder_changed, levels_folder = imgui.input_text("Levels folder", levels_folder, 256)
                search_changed, levels_search = imgui.input_text("Search", levels_search, 256)
                try:
                    if folder_changed or not files:
                        os.chdir(os.path.expanduser(levels_folder))
                        search_changed = True
                    if search_changed:
                        files = glob.glob(levels_search + "*.txt")
                        files = [file.removesuffix(".txt") for file in files]

                    _, file_choice = imgui.listbox("Levels", file_choice, files)

                    if imgui.button("Open"):
                        open_level_name = files[file_choice]
                        with open(open_level_name + ".txt") as file:
                            open_level = Level(open_level_name, file.read())
                        imgui.close_current_popup()

                except Exception as e:
                    imgui.text_ansi("Failed to load levels folder...")
                    imgui.text_ansi(str(e))
                    error = traceback.format_exc()
        
        if menu_choice == "file.saveas":
            imgui.open_popup("file.saveas")
            file_choice = 0
        with imgui.begin_popup("file.saveas") as popup:
            if popup.opened:
                folder_changed, levels_folder = imgui.input_text("Levels folder", levels_folder, 256)
                name_changed, open_level_name = imgui.input_text("Name", open_level_name, 256)
                try:
                    if folder_changed or not files:
                        os.chdir(os.path.expanduser(levels_folder))
                        search_changed = True
                    if search_changed:
                        files = glob.glob(levels_search + "*.txt")
                        files = [file.removesuffix(".txt") for file in files]
                    if name_changed:
                        file_choice = -1

                    clicked, file_choice = imgui.listbox("Levels", file_choice, files)
                    if clicked:
                        open_level_name = files[file_choice]

                    new = file_choice == -1
                    if imgui.button("Save New" if new else "Overwrite"):
                        save_data = open_level.save()
                        with open(open_level_name + ".txt", "x" if new else "w") as file:
                            file.write(save_data)
                        imgui.close_current_popup()

                except Exception as e:
                    imgui.text_ansi("Failed to load levels folder...")
                    imgui.text_ansi(str(e))
                    error = traceback.format_exc()

        if open_level:
            show_editor(open_level, overlay_draw_list)

        if error:
            imgui.text_ansi(error)

        gl.glClearColor(0.3, 0.3, 0.3, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()

def impl_glfw_init():
    width, height = 800, 600
    window_name = "Zygan's Parabox Editor"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window


if __name__ == "__main__":
    main()