#
# graphics - Содержит скрипты отвечающие за графику.
#


# Импортируем:
if True:
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

    import GPUtil
    import pygame
    from pygame import constants as Key
    from pygame import constants as Event
    from ..math import numba, radians, sin, cos

    # Получить название используемой видеокарты:
    def get_videocard_name() -> str: return GPUtil.getGPUs()[0].name if GPUtil.getGPUs() else "Built-in videocard"

    # Ускоренная функция поворота вершин спрайта:
    @numba.njit
    def __rotate_vertices__(x: float, y: float, width: int, height: int, angle: float) -> list:
        center_x      = x + (width / 2)
        center_y      = y + (height / 2)
        angle_rad     = -radians(angle)
        angle_rad_sin = sin(angle_rad)
        angle_rad_cos = cos(angle_rad)
        x1, y1        = ( x          - center_x), ( y           - center_y)
        x2, y2        = ((x + width) - center_x), ( y           - center_y)
        x3, y3        = ((x + width) - center_x), ((y + height) - center_y)
        x4, y4        = ( x          - center_x), ((y + height) - center_y)

        return [
            (x1 * angle_rad_cos - y1 * angle_rad_sin) + center_x,
            (x1 * angle_rad_sin + y1 * angle_rad_cos) + center_y,
            (x2 * angle_rad_cos - y2 * angle_rad_sin) + center_x,
            (x2 * angle_rad_sin + y2 * angle_rad_cos) + center_y,
            (x3 * angle_rad_cos - y3 * angle_rad_sin) + center_x,
            (x3 * angle_rad_sin + y3 * angle_rad_cos) + center_y,
            (x4 * angle_rad_cos - y4 * angle_rad_sin) + center_x,
            (x4 * angle_rad_sin + y4 * angle_rad_cos) + center_y,
        ]
    __rotate_vertices__(0, 0, 1, 1, 0.0)

    # Импортируем скрипты:
    from . import animation
    from . import atlas
    from . import batch
    from . import buffers
    from . import camera
    from . import draw
    from . import font
    from . import gl
    from . import image
    from . import imgui
    from . import light
    from . import packer
    from . import particles
    from . import renderer
    from . import shader
    from . import skybox
    from . import sprite
    from . import texture
    from . import window

    # Импортируем основной функционал из скриптов:
    from .animation import Animation2D
    from .atlas     import AtlasTexture
    from .batch     import SpriteBatch2D, AtlasTextureBatch2D
    from .buffers   import SSBO, FrameBuffer
    from .camera    import Camera2D, Camera3D
    from .draw      import Draw2D, Draw3D
    from .font      import Font, SysFont, get_fonts
    from .image     import Image
    from .imgui     import GUIAPI, PyImGUI
    from .light     import Light2D
    from .packer    import PackerTexture
    from .particles import ParticleEffect2D
    from .renderer  import Renderer2D
    from .shader    import ShaderProgram, ComputeShaderProgram
    from .skybox    import SkyBox
    from .sprite    import Sprite2D
    from .texture   import Texture
    from .window    import Window
