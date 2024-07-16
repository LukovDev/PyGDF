#
# graphics - Содержит скрипты отвечающие за графику.
#


# Импортируем:
if True:
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    from ..math import numba, numpy


# Ошибка окна OpenGL:
class OpenGLWindowError(Exception): pass


# Неподдерживаемая указанная OpenGL версия:
class OpenGLContextNotSupportedError(OpenGLWindowError): pass


# Ускоренная функция поворота вершин полигона спрайта:
@numba.njit
def __rotate_vertices__(x: float, y: float, width: int, height: int, angle: float) -> list:
    center_x      =  x + (width  / 2)
    center_y      =  y + (height / 2)
    angle_rad     = -numpy.radians(angle)
    angle_rad_sin =  numpy.sin(angle_rad)
    angle_rad_cos =  numpy.cos(angle_rad)

    # Предварительно вычисляем смещения:
    dx1, dy1 = x - center_x        , y - center_y
    dx2, dy2 = x + width - center_x, y - center_y
    dx3, dy3 = x + width - center_x, y + height - center_y
    dx4, dy4 = x - center_x        , y + height - center_y

    # Применяем поворот:
    x1 = dx1 * angle_rad_cos - dy1 * angle_rad_sin + center_x
    y1 = dx1 * angle_rad_sin + dy1 * angle_rad_cos + center_y
    x2 = dx2 * angle_rad_cos - dy2 * angle_rad_sin + center_x
    y2 = dx2 * angle_rad_sin + dy2 * angle_rad_cos + center_y
    x3 = dx3 * angle_rad_cos - dy3 * angle_rad_sin + center_x
    y3 = dx3 * angle_rad_sin + dy3 * angle_rad_cos + center_y
    x4 = dx4 * angle_rad_cos - dy4 * angle_rad_sin + center_x
    y4 = dx4 * angle_rad_sin + dy4 * angle_rad_cos + center_y

    return [x1, y1, x2, y2, x3, y3, x4, y4]


# Импортируем скрипты:
from . import animator
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
from . import scene
from . import shader
from . import skybox
from . import sprite
from . import texture
from . import window


# Импортируем основной функционал из скриптов:
from .animator  import Animator2D
from .atlas     import AtlasTexture
from .batch     import SpriteBatch2D, AtlasTextureBatch2D
from .buffers   import SSBO, FrameBuffer
from .camera    import Camera2D, Camera3D
from .draw      import Draw2D, Draw3D
from .font      import FontGenerator
from .image     import Image
from .imgui     import ImGUI
from .light     import Light2D
from .packer    import PackerTexture
from .particles import SimpleParticleEffect2D
from .renderer  import Renderer2D
from .scene     import Scene
from .shader    import ShaderProgram
from .skybox    import SkyBox
from .sprite    import Sprite2D
from .texture   import Texture
from .window    import Window
