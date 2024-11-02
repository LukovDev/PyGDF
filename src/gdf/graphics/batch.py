#
# batch.py - Создаёт класс отрисовки по пакетно (отрисовки множества объектов за один вызов отрисовки).
#


# Импортируем:
from .gl import *
from .camera import Camera2D
from .sprite import Sprite2D
from .texture import Texture
from .atlas import AtlasTexture
from . import _rot2d_vertices_rectangle_, _render_sprite_batch_2d_, _render_atlas_texture_batch_2d_
from ..math import *
from ..utils import *


# Класс пакетной отрисовки спрайтов:
class SpriteBatch2D:
    """ Этот класс не поддерживает отрисовку текстур атласов. Для этого есть класс AtlasTextureBatch2D """

    def __init__(self, camera: Camera2D = None) -> None:
        self.camera          = camera  # Передайте 2D камеру если хотите увеличить скорость отрисовки.
        self.texture_batches = {}      # Словарь хранит уникальные текстурки, и их вершины.
        self._is_begin_      = False

    # Начать отрисовку:
    def begin(self) -> "SpriteBatch2D":
        if self._is_begin_:
            raise Exception(
                "Function \".end()\" was not called in the last iteration of the loop.\n"
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self._is_begin_ = True
        return self

    # Отрисовать спрайт:
    def draw(self,
             sprite:       Sprite2D | Texture,
             x:            float,
             y:            float,
             width:        float,
             height:       float,
             angle:        float = 0.0,
             cull_sprites: bool  = False
             ) -> "SpriteBatch2D":
        if not self._is_begin_:
            raise Exception(
                "The \".begin()\" function was not called "
                "before the \".draw()\" function.")

        # Если камера не видит ваш спрайт, то мы пропускаем отрисовку спрайта:
        # ЕСЛИ ПЫТАТЬСЯ ОТРИСОВАТЬ МНОГО СПРАЙТОВ ИСПОЛЬЗУЯ ПРОВЕРКУ НИЖЕ, ПРОИЗВОДИТЕЛЬНОСТЬ УПАДЁТ:
        if cull_sprites and self.camera is not None:
            czom, cmtr = self.camera.zoom, self.camera.meter
            sprad = max(abs(width), abs(height))/2 * 1.5
            cmrad = max(abs(self.camera.size.x*czom*cmtr), abs(self.camera.size.y*czom*cmtr))/100/2 * 1.5
            if not Intersects.circle_circle(vec2(x+width/2, y+height/2), sprad, self.camera.position.xy, cmrad):
                return

        # Вращаем вершины спрайта:
        if angle != 0.0: vertices = _rot2d_vertices_rectangle_(x, y, width, height, angle)
        else:
            vertices = [
                x        , y         ,  # Нижний левый угол.
                x + width, y         ,  # Нижний правый угол.
                x + width, y + height,  # Верхний правый угол.
                x        , y + height,  # Верхный левый угол.
            ]

        # Если текстурки нет в уникальных текстурках:
        if sprite.id not in self.texture_batches:
            self.texture_batches[sprite.id] = []

        # Добавляем новый полигон для текстуры:
        self.texture_batches[sprite.id].extend(vertices)

        return self

    # Закончить отрисовку:
    def end(self) -> "SpriteBatch2D":
        if self._is_begin_:
            self._is_begin_ = False
        else:
            raise Exception(
                "The \".begin()\" function was not called before the \".end()\" function."
            )
        return self

    # Отрисовать все спрайты:
    def render(self, color: list = None, clear_batch: bool = True) -> "SpriteBatch2D":
        if self._is_begin_:
            raise Exception(
                "You cannot call the \".render()\" function after \".begin()\" and not earlier than \".end()\""
            )

        gl.glColor(*[1, 1, 1] if color is None else color)

        # Рисуем пакет спрайтов через ускоренную функцию Cython:
        _render_sprite_batch_2d_(self.texture_batches)

        if clear_batch: self.texture_batches.clear()

        return self


# Класс пакетной отрисовки атласовых текстур:
class AtlasTextureBatch2D:
    """ Этот класс не поддерживает отрисовку спрайтов. Для этого есть класс SpriteBatch2D """

    def __init__(self, camera: Camera2D = None) -> None:
        self.camera          = camera  # Передайте 2D камеру если хотите увеличить скорость отрисовки.
        self.texture_batches = {}  # Словарь хранит уникальные текстурки, и их вершины.
        self._is_begin_      = False

    # Начать отрисовку:
    def begin(self) -> "AtlasTextureBatch2D":
        if self._is_begin_:
            raise Exception(
                "Function \".end()\" was not called in the last iteration of the loop.\n"
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self._is_begin_ = True
        return self

    # Отрисовать спрайт:
    def draw(self,
             texture:      AtlasTexture,
             x:            float,
             y:            float,
             width:        int,
             height:       int,
             angle:        float = 0.0,
             cull_sprites: bool  = False
             ) -> "AtlasTextureBatch2D":
        if not self._is_begin_:
            raise Exception(
                "The \".begin()\" function was not called "
                "before the \".draw()\" function.")

        # Если камера не видит ваш спрайт, то мы пропускаем отрисовку спрайта:
        # ЕСЛИ ПЫТАТЬСЯ ОТРИСОВАТЬ МНОГО СПРАЙТОВ ИСПОЛЬЗУЯ ПРОВЕРКУ НИЖЕ, ПРОИЗВОДИТЕЛЬНОСТЬ УПАДЁТ:
        if cull_sprites and self.camera is not None:
            czom, cmtr = self.camera.zoom, self.camera.meter
            sprad = max(abs(width), abs(height))/2 * 1.5
            cmrad = max(abs(self.camera.size.x*czom*cmtr), abs(self.camera.size.y*czom*cmtr))/100/2 * 1.5
            if not Intersects.circle_circle(vec2(x+width/2, y+height/2), sprad, self.camera.position.xy, cmrad):
                return

        # Вращаем вершины спрайта:
        if angle != 0.0: vertices = _rot2d_vertices_rectangle_(x, y, width, height, angle)
        else:
            vertices = [
                x        , y         ,  # Нижний левый угол.
                x + width, y         ,  # Нижний правый угол.
                x + width, y + height,  # Верхний правый угол.
                x        , y + height,  # Верхный левый угол.
            ]

        # Если текстурки нет в уникальных текстурках:
        if texture.texture.id not in self.texture_batches:
            self.texture_batches[texture.id] = ([], [])

        self.texture_batches[texture.id][0].extend(vertices)
        self.texture_batches[texture.id][1].extend(texture.texcoords)

        return self

    # Закончить отрисовку:
    def end(self) -> "AtlasTextureBatch2D":
        if self._is_begin_:
            self._is_begin_ = False
        else:
            raise Exception(
                "The \".begin()\" function was not called before the \".end()\" function."
            )
        return self

    # Отрисовать все спрайты:
    def render(self, color: list = None, clear_batch: bool = True) -> "AtlasTextureBatch2D":
        if self._is_begin_:
            raise Exception(
                "You cannot call the \".render()\" function after \".begin()\" and not earlier than \".end()\""
            )

        gl.glColor(*[1, 1, 1] if color is None else color)

        # Рисуем пакет спрайтов через ускоренную функцию Cython:
        _render_atlas_texture_batch_2d_(self.texture_batches)

        if clear_batch: self.texture_batches.clear()

        return self
