#
# batch.py - Создаёт класс отрисовки по пакетно (отрисовки множества объектов за один вызов отрисовки).
#


# Импортируем:
if True:
    import numpy as np
    import numba as nb
    from .gl import *
    from .sprite import Sprite
    from ..math import *
    from ..utils import *


# Ускоренная функция поворота вершин спрайта:
@nb.njit
def __rotate_vertices__(x: float, y: float, wdth: int, hght: int, angle: float) -> list:
    center_x      = x + (wdth / 2)
    center_y      = y + (hght / 2)
    angle_rad     = -radians(angle)
    angle_rad_sin = sin(angle_rad)
    angle_rad_cos = cos(angle_rad)
    x1, y1        = ( x         - center_x), ( y         - center_y)
    x2, y2        = ((x + wdth) - center_x), ( y         - center_y)
    x3, y3        = ((x + wdth) - center_x), ((y + hght) - center_y)
    x4, y4        = ( x         - center_x), ((y + hght) - center_y)

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


# Класс пакетной отрисовки спрайтов:
class SpriteBatch:
    def __init__(self, camera2d = None) -> None:
        self.camera2d     = camera2d  # Передайте 2D камеру если хотите увеличить скорость отрисовки.
        self.__is_begin__ = False
        self.texture_batches = {}  # Словарь хранит уникальные текстурки, и их вершины.

    # Очистить все списки и пр. и начать подготовку к отрисовке:
    def begin(self) -> "SpriteBatch":
        if self.__is_begin__:
            raise Exception(
                "Function \".end()\" was not called in the last iteration of the loop.\n"
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self.__is_begin__  = True
        return self

    # Отрисовать спрайт:
    def draw(self, sprite: Sprite, x: float, y: float, width: int = 0, height: int = 0,
             angle: float = 0.0, cull_sprites: bool = False) -> "SpriteBatch":
        if not self.__is_begin__:
            raise Exception(
                "The \".begin()\" function was not called "
                "before the \".draw()\" function.")

        wdth, hght = width or sprite.width, height or sprite.height

        # Если камера не видит ваш спрайт, то мы пропускаем отрисовку спрайта:
        # ИНОГДА, ЭТО МОЖЕТ НАОБОРОТ ЗАНИЗИТЬ СКОРОСТЬ ОТРИСОВКИ!
        if cull_sprites and self.camera2d is not None:
            zoom, meter = self.camera2d.zoom, self.camera2d.meter / 100
            if not is_circle_rectangle((x+(wdth/2), y+(hght/2)), max(abs(wdth), abs(hght))/2 * 1.5,
                                       (self.camera2d.position.x-(self.camera2d.width*zoom)/2*meter,
                                        self.camera2d.position.y-(self.camera2d.height*zoom)/2*meter,
                                        self.camera2d.width*zoom*meter, self.camera2d.height*zoom*meter)): return

        # Вращаем вершины спрайта:
        if angle != 0.0:
            vertices = __rotate_vertices__(x, y, wdth, hght, angle)
        else:
            vertices = [
                x       , y       ,  # Нижний левый угол.
                x + wdth, y       ,  # Нижний правый угол.
                x + wdth, y + hght,  # Верхний правый угол.
                x       , y + hght,  # Верхный левый угол.
            ]
        
        # Если текстурки нет в уникальных текстурках:
        if sprite.texture.id not in self.texture_batches:
            self.texture_batches[sprite.texture.id] = []

        self.texture_batches[sprite.texture.id].extend(vertices)

        return self

    # Отрисовать все спрайты:
    def end(self) -> "SpriteBatch":
        if self.__is_begin__: self.__is_begin__ = False
        else: raise Exception("The \".begin()\" function was not called before the \".end()\" function.")

        gl.glColor(1, 1, 1)

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)

        # Пройдитесь по каждой текстуре и отрендерьте все квадраты с этой текстурой:
        for texture, vertices in self.texture_batches.items():
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
            gl.glVertexPointer(2, gl.GL_DOUBLE, 0, np.array(vertices))
            gl.glTexCoordPointer(2, gl.GL_DOUBLE, 0, np.array([0, 1, 1, 1, 1, 0, 0, 0]*(len(vertices) // 8)))
            gl.glDrawArrays(gl.GL_QUADS, 0, len(vertices) // 2)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_TEXTURE_2D)

        self.texture_batches.clear()

        return self
