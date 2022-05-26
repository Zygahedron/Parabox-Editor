# -*- coding: utf-8 -*-
import multiprocessing
# import glfw
from sdl2 import *
import ctypes
import OpenGL.GL as gl

import imgui
# from imgui.integrations.glfw import GlfwRenderer
from imgui.integrations.sdl2 import SDL2Renderer

import time

from editor import *
import style as imgui_style

class Key:
    def __init__(self):
        self.pressed = False
        self.down = False
        self.released = False
class Keyboard:
    def __init__(self):
        self.n = Key()
        self.b = Key()
        self.a = Key()
        self.o = Key()
        self.s = Key()
        self.up = Key()
        self.left = Key()
        self.down = Key()
        self.right = Key()
        self.enter = Key()

        self.map = {
            SDL_SCANCODE_A: self.a,
            SDL_SCANCODE_B: self.b,
            SDL_SCANCODE_N: self.n,
            SDL_SCANCODE_O: self.o,
            SDL_SCANCODE_S: self.s,
            SDL_SCANCODE_UP: self.up,
            SDL_SCANCODE_DOWN: self.down,
            SDL_SCANCODE_LEFT: self.left,
            SDL_SCANCODE_RIGHT: self.right,
            SDL_SCANCODE_RETURN: self.enter
        }
keyboard = Keyboard()

def main():
    global levels_folder
    
    imgui.create_context()
    window, gl_context = impl_pysdl2_init()
    impl = SDL2Renderer(window)
    style = imgui.get_style()
    imgui_style.set(style)
    editor = Editor()

    running = True
    event = SDL_Event()
    last_time = time.time()
    while running:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                running = False
                break
            if event.type == SDL_KEYDOWN:
                if event.key.keysym.scancode in keyboard.map:
                    keyboard.map[event.key.keysym.scancode].pressed = True
                    keyboard.map[event.key.keysym.scancode].down = True
            if event.type == SDL_KEYUP:
                if event.key.keysym.scancode in keyboard.map:
                    keyboard.map[event.key.keysym.scancode].released = True
                    keyboard.map[event.key.keysym.scancode].down = False
            impl.process_event(event)
        # glfw.poll_events()
        impl.process_inputs()

        if time.time() <= last_time:
            continue
        last_time = time.time()

        if not SDL_GetWindowFlags(window) & SDL_WINDOW_MOUSE_FOCUS:
            continue

        imgui.new_frame()

        if not editor.main_loop(keyboard):
            break

        for key in keyboard.map.values():
            key.pressed = False
            key.released = False

        gl.glClearColor(0.1, 0.1, 0.1, 1)
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
        # exit(1)

    return window, gl_context


if __name__ == "__main__":
    # pyinstaller infinite loop fix???
    multiprocessing.freeze_support()
    main()