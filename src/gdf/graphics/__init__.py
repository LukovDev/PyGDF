#
# graphics - Содержит скрипты отвечающие за графику.
#


# Импортируем:
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


# Утилиты написанные на Cython:
try:
    # Импортируем скомпилированную библиотеку графических утилит:
    from .graphics_utils import (
        _rot2d_vertices_rectangle_,
        _convert_quads_to_triangles_,
        _sprite_batch_2d_draw_,
        _atlas_texture_batch_2d_draw_,
        _sprite_batch_2d_render_,
        _atlas_texture_batch_2d_render_,
    )
except (ModuleNotFoundError, ImportError) as error:
    raise Exception(f"The compiled module could not be imported: {error}")


# Ошибка окна OpenGL:
class OpenGLWindowError(Exception): pass


# Неподдерживаемая указанная OpenGL версия:
class OpenGLContextNotSupportedError(OpenGLWindowError): pass


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
from .buffers   import GLQuery, SSBO, FrameBuffer, VBO
from .camera    import Camera2D, Camera3D
from .draw      import Draw2D, Draw3D
from .font      import FontFile, FontGenerator
from .image     import Image
from .imgui     import ImGUI, imgui_bundle, imgui
from .light     import Light2D
from .packer    import PackerTexture
from .particles import ParticleEffect2D
from .renderer  import Renderer2D
from .scene     import Scene
from .shader    import ShaderProgram
from .skybox    import SkyBox
from .sprite    import Sprite2D
from .texture   import Texture, Texture3D
from .window    import Window
