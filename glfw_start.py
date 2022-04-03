# -*- coding: utf-8 -*-
import multiprocessing
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

    editor = Editor()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        if not editor.main_loop():
            break

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
    # pyinstaller infinite loop fix???
    multiprocessing.freeze_support()
    main()