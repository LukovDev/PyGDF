#
# graphics - Содержит скрипты отвечающие за графику.
#


# Импортируем:
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


# Ускоренная функция поворота вершин полигона спрайта:
try:
    # Импортируем скомпилированную библиотеку r2d_verts_c:
    from .r2d_verts_c import _rot2d_vertices_rectangle_ as _rotate_vertices_
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
