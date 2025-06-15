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
        _sprite_batch_draw_,
        _sprite_batch_render_,
    )
except (ModuleNotFoundError, ImportError) as error:
    raise Exception(f"The compiled module could not be imported: {error}")


# Ошибка окна OpenGL:
class OpenGLWindowError(Exception): pass


# Неподдерживаемая указанная OpenGL версия:
class OpenGLContextNotSupportedError(OpenGLWindowError): pass


# Менеджер буферов для отслеживания запросов на их удаление (удаление происходит автоматически в конце цикла окна):
class BufferManager:
    TYPE_QUERY_BUFFER:          str = "qbo"
    TYPE_SHADER_STORAGE_BUFFER: str = "ssbo"
    TYPE_FRAME_BUFFER:          str = "fbo"
    TYPE_VERTEX_BUFFER:         str = "vbo"
    TYPE_INDEX_BUFFER:          str = "ibo"
    TYPE_VERTEX_ARRAY_BUFFER:   str = "vao"
    TYPE_TEXTURE_BUFFER:        str = "tbo"
    stack: dict = {v: [] for k, v in locals().items() if k.startswith("TYPE_")}

    # Добавить буфер в стек:
    @staticmethod
    def add(buffer_type: str, buffer_id: int) -> None:
        if buffer_id not in BufferManager.stack[buffer_type]:
            BufferManager.stack[buffer_type].append(buffer_id)

    # Удалить буфер из стека:
    @staticmethod
    def remove(buffer_type: str, buffer_id: int) -> None:
        if buffer_id in BufferManager.stack[buffer_type]:
            BufferManager.stack[buffer_type].remove(buffer_id)

    # Удалить все буферы за раз:
    @staticmethod
    def delete_buffers():
        _gl = gl.gl  # Получаем библиотеку gl из файла gl.py
        for key, values in dict(BufferManager.stack).items():
            if not values: continue  # Если нет значений, пропускаем.
            if key == BufferManager.TYPE_QUERY_BUFFER:
                _gl.glDeleteQueries(len(values), values)
            if key in [BufferManager.TYPE_VERTEX_BUFFER,
                       BufferManager.TYPE_INDEX_BUFFER,
                       BufferManager.TYPE_SHADER_STORAGE_BUFFER]:
                _gl.glDeleteBuffers(len(values), values)
            if key == BufferManager.TYPE_VERTEX_ARRAY_BUFFER:
                _gl.glDeleteVertexArrays(len(values), values)
            if key == BufferManager.TYPE_FRAME_BUFFER:
                _gl.glDeleteFramebuffers(len(values), values)
            if key == BufferManager.TYPE_TEXTURE_BUFFER:
                _gl.glDeleteTextures(len(values), values)
            BufferManager.stack[key] = []


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
from . import light
from . import packer
from . import particles
from . import render
from . import scene
from . import shader
from . import skybox
from . import sprite
from . import texture
from . import texunits
from . import window


# Импортируем основной функционал из скриптов:
from .animator  import Animator2D
from .atlas     import AtlasTexture
from .batch     import SpriteBatch
from .buffers   import BufferManager, GLQuery, SSBO, FrameBuffer, VBO, IBO, VAO
from .camera    import Camera2D, Camera3D
from .draw      import SimpleDraw
from .font      import FontFile, FontGenerator
from .image     import Image
from .light     import Light2D
from .packer    import PackerTexture
from .particles import ParticleEffect2D
from .render    import RenderPipeline, RenderCanvas
from .scene     import Scene
from .shader    import ShaderProgram
from .skybox    import Skybox
from .sprite    import Sprite2D, Sprite3D
from .texture   import Texture, Texture3D
from .texunits  import TextureUnits
from .window    import Window
