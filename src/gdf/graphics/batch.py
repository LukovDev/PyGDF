#
# batch.py - Создаёт класс отрисовки по пакетно (отрисовки множества объектов за один вызов отрисовки).
#


# Импортируем:
from .gl import *
from .atlas import AtlasTexture
from .buffers import VBO, IBO, VAO
from .sprite import Sprite2D
from .texture import Texture
from .render import RenderPipeline
from .texunits import TextureUnits
from ..math import *
from ..utils import *
from . import (
    _sprite_batch_draw_,
    _sprite_batch_render_,
)


# Класс пакетной отрисовки спрайтов:
class SpriteBatch:
    def __init__(self) -> None:
        self.max_verts = 4*2048    # По умолчанию буфер сможет хранить вершины для 2048 спрайтов.
        self.texture_vcount  = {}  # Словарь хранит уникальные текстурки и кол-во вершин для них.
        self.texture_batches = {}  # Словарь хранит уникальные текстурки и их вершины (и текстурные координаты).
        self._is_begin_ = False

        self.stride = 5 * 4  # Размер одной вершины в байтах. 5 это кол-во элементов а 4 это размер одного float.
        self.vbo = VBO(data=None, size=self.max_verts*self.stride, mode=gl.GL_DYNAMIC_DRAW)
        base     = numpy.array([0, 1, 2, 2, 3, 0], dtype=numpy.uint32)
        indices  = (numpy.arange(self.max_verts, dtype=numpy.uint32) * 4)[:,None] + base
        self.ibo = IBO(indices.ravel())
        self.vao = VAO()

        # Настраиваем буфер:
        self.vao.begin()  # Используем VAO.
        self.ibo.begin()  # Используем IBO.
        self.vbo.begin()  # Используем VBO.
        self.vao.attrib_pointer(0, count=3, stride=self.stride, offset=0)    # Вершина состоит из трёх чисел.
        self.vao.attrib_pointer(1, count=2, stride=self.stride, offset=3*4)  # Координаты состоят из двух чисел.
        self.vbo.end()  # Не используем VBO текстурных координат.
        self.vao.end()  # Не используем VAO.
        self.ibo.end()  # Не используем IBO.

        # Короткие функции для установки необходимых настроек:
        self._set_sampler_ = lambda i: RenderPipeline.default_shader.set_sampler("u_texture", TextureUnits.rebind(i, 0))
        self._vbo_setsubdata_ = lambda d, f, s: self.vbo.set_subdata(d, f, s, False)
        self._vbo_render_ = lambda: self.vbo.render_elements(count=self.max_verts*4, use_begin_end=False)

    # Начать отрисовку:
    def begin(self) -> "SpriteBatch":
        if self._is_begin_:
            raise Exception(
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self._is_begin_ = True
        return self

    # Добавить спрайт в пакет данных:
    def draw(self,
             sprite: Sprite2D|Texture|AtlasTexture|int,
             x:      float,
             y:      float,
             width:  float,
             height: float,
             angle:  float = 0.0) -> "SpriteBatch":
        if not self._is_begin_:
            raise Exception("The \".begin()\" function was not called before the \".draw()\" function.")

        # Текстурные координаты:
        texcoord = [
            0.0, 0.0,  # Левый нижний угол.
            1.0, 1.0,  # Верхний правый угол.
        ]

        # Добавляем спрайт в пакет текстур используя оптимизированную функцию на Cython:
        _sprite_batch_draw_(self.texture_batches, self.texture_vcount, texcoord, sprite, x, y, width, height, angle)
        return self

    # Закончить отрисовку:
    def end(self) -> "SpriteBatch":
        if self._is_begin_:
            self._is_begin_ = False
        else:
            raise Exception("The \".begin()\" function was not called before the \".end()\" function.")
        return self

    # Отрисовать все спрайты:
    def render(self, color: list = None, clear_batch: bool = True) -> "SpriteBatch":
        if self._is_begin_:
            raise Exception(
                "You cannot call the \".render()\" function after \".begin()\" and not earlier than \".end()\"")
        if color is None: color = vec4(1.0)
        if isinstance(color, (vec3, glm.vec3)): color = vec4(color, 1.0)

        # Подключаем необходимые буферы:
        self.vao.begin()
        self.vbo.begin()

        # Подключаем шейдер по умолчанию:
        RenderPipeline.default_shader.begin()
        RenderPipeline.default_shader.set_uniform("u_use_texture", True)
        RenderPipeline.default_shader.set_uniform("u_color", color)
        RenderPipeline.default_shader.set_uniform("u_model", mat4(1.0))

        # Получаем максимальное кол-во вершин в пакетах отрисовки:
        new_max_verts = max(self.texture_vcount.values()) if self.texture_vcount else 0

        # Если максимальное кол-во вершин в пакетах отрисовки больше нашего, выделяем память буфера заново:
        if new_max_verts > self.max_verts:
            new_size = int(new_max_verts * 1.5)
            self.vbo.set_data(None, new_size*self.stride, gl.GL_DYNAMIC_DRAW, False)
            self.max_verts = new_size

        # Рисуем пакеты спрайтов через ускоренную функцию на Cython:
        _sprite_batch_render_(
            self.texture_batches, self.texture_vcount,
            self._set_sampler_,
            self._vbo_setsubdata_,
            self._vbo_render_
        )

        # Отключаем шейдер по умолчанию:
        RenderPipeline.default_shader.end()

        # Отключаем необходимые буферы:
        self.vbo.end()
        self.vao.end()

        # Очищаем данные:
        if clear_batch:
            self.texture_batches.clear()
            self.texture_vcount.clear()
        return self

    # Установить размер буфера вручную:
    def set_size(self, size: int, mode: int = gl.GL_DYNAMIC_DRAW) -> "SpriteBatch":
        self.vbo.set_data(data=None, size=size, mode=mode)

    # Удалить пакетную отрисовку (буферы):
    def destroy(self) -> None:
        self.vbo.destroy()
        self.vao.destroy()

"""
# Класс пакетной отрисовки спрайтов:
class SpriteBatch2D:

    def __init__(self) -> None:
        self.texture_batches = {}  # Словарь хранит уникальные текстурки, и их вершины.
        self._is_begin_  = False

    # Начать отрисовку:
    def begin(self) -> "SpriteBatch2D":
        if self._is_begin_:
            raise Exception(
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self._is_begin_ = True
        return self

    # Отрисовать спрайт:
    def draw(self,
             sprite: Sprite2D|Texture|int,
             x:      float,
             y:      float,
             width:  float,
             height: float,
             angle:  float = 0.0) -> "SpriteBatch2D":
        if not self._is_begin_:
            raise Exception("The \".begin()\" function was not called before the \".draw()\" function.")

        # Добавляем спрайт в пакет текстур используя оптимизированную функцию на Cython:
        _sprite_batch_2d_draw_(self.texture_batches, sprite, x, y, width, height, angle)
        return self

    # Закончить отрисовку:
    def end(self) -> "SpriteBatch2D":
        if self._is_begin_:
            self._is_begin_ = False
        else:
            raise Exception("The \".begin()\" function was not called before the \".end()\" function.")
        return self

    # Отрисовать все спрайты:
    def render(self, color: list = None, clear_batch: bool = True) -> "SpriteBatch2D":
        if self._is_begin_:
            raise Exception(
                "You cannot call the \".render()\" function after \".begin()\" and not earlier than \".end()\""
            )

        gl.glColor(*[1, 1, 1] if color is None else color)

        # Рисуем пакет спрайтов через ускоренную функцию на Cython:
        _sprite_batch_2d_render_(self.texture_batches)

        if clear_batch: self.texture_batches.clear()
        return self


# Класс пакетной отрисовки атласовых текстур:
class AtlasTextureBatch2D:

    def __init__(self) -> None:
        self.texture_batches = {}  # Словарь хранит уникальные текстурки, и их вершины.
        self._is_begin_  = False

    # Начать отрисовку:
    def begin(self) -> "AtlasTextureBatch2D":
        if self._is_begin_:
            raise Exception(
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self._is_begin_ = True
        return self

    # Отрисовать спрайт:
    def draw(self,
             texture: AtlasTexture,
             x:       float,
             y:       float,
             width:   int,
             height:  int,
             angle:   float = 0.0) -> "AtlasTextureBatch2D":
        if not self._is_begin_:
            raise Exception("The \".begin()\" function was not called before the \".draw()\" function.")

        # Добавляем текстуру в пакет текстур используя оптимизированную функцию на Cython:
        _atlas_texture_batch_2d_draw_(self.texture_batches, texture.id, texture.texcoords, x, y, width, height, angle)
        return self

    # Закончить отрисовку:
    def end(self) -> "AtlasTextureBatch2D":
        if self._is_begin_:
            self._is_begin_ = False
        else:
            raise Exception("The \".begin()\" function was not called before the \".end()\" function.")
        return self

    # Отрисовать все спрайты:
    def render(self, color: list = None, clear_batch: bool = True) -> "AtlasTextureBatch2D":
        if self._is_begin_:
            raise Exception(
                "You cannot call the \".render()\" function after \".begin()\" and not earlier than \".end()\""
            )

        gl.glColor(*[1, 1, 1] if color is None else color)

        # Рисуем пакет спрайтов через ускоренную функцию на Cython:
        _atlas_texture_batch_2d_render_(self.texture_batches)

        if clear_batch: self.texture_batches.clear()
        return self
"""