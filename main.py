# -*- coding: utf-8 -*-
# import multiprocessing
# import glfw
from sdl2 import *
import ctypes
import OpenGL.GL as gl

import imgui
# from imgui.integrations.glfw import GlfwRenderer
from imgui.integrations.sdl2 import SDL2Renderer

import glob
import os
import platform
import traceback
import time

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
    window, gl_context = impl_pysdl2_init()
    impl = SDL2Renderer(window)

    levels_search = ""
    files = None
    open_level_name = ""
    open_level = None
    error = None

    cursor_held = None

    running = True
    event = SDL_Event()
    last_time = time.time()
    while running:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                running = False
                break
            impl.process_event(event)
        # glfw.poll_events()
        impl.process_inputs()

        if time.time() <= last_time:
            continue
        last_time = time.time()

        imgui.new_frame()

        overlay_draw_list = imgui.get_overlay_draw_list()

        menu_choice = None
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                if imgui.menu_item("New")[0]:
                    open_level = Level("untitled", "version 4\n#\n")
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

                imgui.end_menu()
            imgui.end_main_menu_bar()

        if menu_choice == "file.open":
            imgui.open_popup("file.open")
            file_choice = 0
        if imgui.begin_popup("file.open"):
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
            imgui.end_popup()
        
        if menu_choice == "file.saveas":
            imgui.open_popup("file.saveas")
            file_choice = 0
        if imgui.begin_popup("file.saveas"):
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
            imgui.end_popup()

        if open_level:
            show_editor(open_level, overlay_draw_list)

        if error:
            imgui.text_ansi(error)

        gl.glClearColor(0.3, 0.3, 0.3, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        # glfw.swap_buffers(window)
        SDL_GL_SwapWindow(window)

    impl.shutdown()
    # glfw.terminate()
    SDL_GL_DeleteContext(gl_context)
    SDL_DestroyWindow(window)
    SDL_Quit()

def impl_pysdl2_init():
    width, height = 800, 600
    window_name = "Zygan's Parabox Editor"

    if SDL_Init(SDL_INIT_EVERYTHING) < 0:
        print("Error: SDL could not initialize! SDL Error: " + SDL_GetError().decode("utf-8"))
        exit(1)

    SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)
    SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24)
    SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 8)
    SDL_GL_SetAttribute(SDL_GL_ACCELERATED_VISUAL, 1)
    SDL_GL_SetAttribute(SDL_GL_MULTISAMPLEBUFFERS, 1)
    SDL_GL_SetAttribute(SDL_GL_MULTISAMPLESAMPLES, 16)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 4)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 1)
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)

    SDL_SetHint(SDL_HINT_MAC_CTRL_CLICK_EMULATE_RIGHT_CLICK, b"1")
    SDL_SetHint(SDL_HINT_VIDEO_HIGHDPI_DISABLED, b"1")

    window = SDL_CreateWindow(window_name.encode('utf-8'),
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              width, height,
                              SDL_WINDOW_OPENGL|SDL_WINDOW_RESIZABLE)

    if window is None:
        print("Error: Window could not be created! SDL Error: " + SDL_GetError().decode("utf-8"))
        exit(1)

    gl_context = SDL_GL_CreateContext(window)
    if gl_context is None:
        print("Error: Cannot create OpenGL Context! SDL Error: " + SDL_GetError().decode("utf-8"))
        exit(1)

    SDL_GL_MakeCurrent(window, gl_context)
    if SDL_GL_SetSwapInterval(1) < 0:
        print("Warning: Unable to set VSync! SDL Error: " + SDL_GetError().decode("utf-8"))
        exit(1)

    return window, gl_context


if __name__ == "__main__":
    # # pyinstaller infinite loop fix???
    # multiprocessing.freeze_support()
    print("A")
    main()