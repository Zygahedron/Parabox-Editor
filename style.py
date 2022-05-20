import imgui

def set(style: imgui.core.GuiStyle):
    io = imgui.get_io()
    imgui.style_colors_dark(style)
    style.colors[imgui.COLOR_BORDER] = (0,0,0,0)
    style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0,0,0,0.5)
    style.colors[imgui.COLOR_TITLE_BACKGROUND] = (0.353,0,0.212,1)
    style.colors[imgui.COLOR_TITLE_BACKGROUND_COLLAPSED] = (0.353,0,0.212,1)
    style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.7,0,0.42,1)
    style.colors[imgui.COLOR_BUTTON_HOVERED] = (0.7,0,0.42,1)
    style.colors[imgui.COLOR_BUTTON_ACTIVE] = (1,1,1,1)
    style.colors[imgui.COLOR_BUTTON] = (0.353,0,0.212,1)
    style.colors[imgui.COLOR_FRAME_BACKGROUND] = (0.156,0,0.094,1)
    style.colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE] = (0.353,0,0.212,1)
    style.colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = (0.353,0,0.212,1)
    #Add more!