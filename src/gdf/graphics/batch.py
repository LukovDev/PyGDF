#
# batch.py - Создаёт класс отрисовки по пакетно (отрисовки множества объектов за один вызов отрисовки).
#


# Импортируем:
if True:
    from .gl import *
    from .camera import Camera2D
    from .sprite import Sprite2D
    from .texture import Texture
    from .atlas import AtlasTexture
    from . import __rotate_vertices__
    from ..math import *
    from ..utils import *


# Класс пакетной отрисовки спрайтов:
class SpriteBatch2D:
    """ Этот класс не поддерживает отрисовку текстур атласов. Для этого есть класс AtlasTextureBatch2D """

    def __init__(self, camera: Camera2D = None) -> None:
        self.camera          = camera  # Передайте 2D камеру если хотите увеличить скорость отрисовки.
        self.texture_batches = {}      # Словарь хранит уникальные текстурки, и их вершины.
        self.__is_begin__    = False

    # Начать отрисовку:
    def begin(self) -> "SpriteBatch2D":
        if self.__is_begin__:
            raise Exception(
                "Function \".end()\" was not called in the last iteration of the loop.\n"
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self.__is_begin__ = True
        return self

    # Отрисовать спрайт:
    def draw(self,
             sprite:       Sprite2D | Texture,
             x:            float,
             y:            float,
             width:        int,
             height:       int,
             angle:        float = 0.0,
             cull_sprites: bool  = False
             ) -> "SpriteBatch2D":
        if not self.__is_begin__:
            raise Exception(
                "The \".begin()\" function was not called "
                "before the \".draw()\" function.")

        # Если камера не видит ваш спрайт, то мы пропускаем отрисовку спрайта:
        # ИНОГДА, ЭТО МОЖЕТ НАОБОРОТ ЗАНИЗИТЬ СКОРОСТЬ ОТРИСОВКИ!
        if cull_sprites and self.camera is not None:
            zoom, meter = self.camera.zoom, self.camera.meter / 100
            if not Intersects.circle_rectangle(vec2(x+(width/2), y+(height/2)), max(abs(width), abs(height))/2 * 1.5,
                                               (self.camera.position.x-(self.camera.width*zoom)/2*meter,
                                               self.camera.position.y-(self.camera.height*zoom)/2*meter,
                                               self.camera.width*zoom*meter, self.camera.height*zoom*meter)): return

        # Вращаем вершины спрайта:
        if angle != 0.0: vertices = __rotate_vertices__(x, y, width, height, angle)
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
        if self.__is_begin__:
            self.__is_begin__ = False
        else:
            raise Exception(
                "The \".begin()\" function was not called before the \".end()\" function."
            )

        return self

    # Отрисовать все спрайты:
    def render(self, color: list = None) -> "SpriteBatch2D":
        if self.__is_begin__:
            raise Exception(
                "You cannot call the \".render()\" function after \".begin()\" and not earlier than \".end()\""
            )

        gl.glColor(*[1, 1, 1] if color is None else color)

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)

        # Пройдитесь по каждой текстуре и отрендерьте все квадраты с этой текстурой:
        for texture, vertices in self.texture_batches.items():
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
            gl.glVertexPointer(2, gl.GL_DOUBLE, 0, numpy.array(vertices))
            gl.glTexCoordPointer(2, gl.GL_DOUBLE, 0, numpy.array([0, 1, 1, 1, 1, 0, 0, 0] * (len(vertices) // 8)))
            gl.glDrawArrays(gl.GL_QUADS, 0, len(vertices) // 2)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_TEXTURE_2D)

        self.texture_batches.clear()

        return self


# Класс пакетной отрисовки атласовых текстур:
class AtlasTextureBatch2D:
    """ Этот класс не поддерживает отрисовку спрайтов. Для этого есть класс SpriteBatch2D """

    def __init__(self, camera: Camera2D = None) -> None:
        self.camera          = camera  # Передайте 2D камеру если хотите увеличить скорость отрисовки.
        self.texture_batches = {}  # Словарь хранит уникальные текстурки, и их вершины.
        self.__is_begin__    = False

    # Начать отрисовку:
    def begin(self) -> "AtlasTextureBatch2D":
        if self.__is_begin__:
            raise Exception(
                "Function \".end()\" was not called in the last iteration of the loop.\n"
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self.__is_begin__ = True
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
        if not self.__is_begin__:
            raise Exception(
                "The \".begin()\" function was not called "
                "before the \".draw()\" function.")

        # Если камера не видит ваш спрайт, то мы пропускаем отрисовку спрайта:
        # ИНОГДА, ЭТО МОЖЕТ НАОБОРОТ ЗАНИЗИТЬ СКОРОСТЬ ОТРИСОВКИ!
        if cull_sprites and self.camera is not None:
            zoom, meter = self.camera.zoom, self.camera.meter / 100
            if not Intersects.circle_rectangle(vec2(x+(width/2), y+(height/2)), max(abs(width), abs(height))/2 * 1.5,
                                               (self.camera.position.x-(self.camera.width*zoom)/2*meter,
                                               self.camera.position.y-(self.camera.height*zoom)/2*meter,
                                               self.camera.width*zoom*meter, self.camera.height*zoom*meter)): return

        # Вращаем вершины спрайта:
        if angle != 0.0: vertices = __rotate_vertices__(x, y, width, height, angle)
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
    def end(self, color: list = None) -> "AtlasTextureBatch2D":
        if self.__is_begin__:
            self.__is_begin__ = False
        else:
            raise Exception(
                "The \".begin()\" function was not called before the \".end()\" function."
            )

    # Отрисовать все спрайты:
    def render(self, color: list = None) -> "AtlasTextureBatch2D":
        if self.__is_begin__:
            raise Exception(
                "You cannot call the \".render()\" function after \".begin()\" and not earlier than \".end()\""
            )

        gl.glColor(*[1, 1, 1] if color is None else color)

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)

        # Пройдитесь по каждой текстуре и отрендерьте все квадраты с этой текстурой:
        for texture, (vertices, texcoords) in self.texture_batches.items():
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
            gl.glVertexPointer(2, gl.GL_DOUBLE, 0, numpy.array(vertices))
            gl.glTexCoordPointer(2, gl.GL_DOUBLE, 0, numpy.array(texcoords))
            gl.glDrawArrays(gl.GL_QUADS, 0, len(vertices) // 2)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_TEXTURE_2D)

        self.texture_batches.clear()

        return self
