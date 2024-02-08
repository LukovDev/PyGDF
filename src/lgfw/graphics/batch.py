#
# batch.py - Создаёт класс отрисовки по пакетно (отрисовки множества объектов за один вызов отрисовки).
#


# Импортируем:
if True:
    import numpy as np
    from .gl import *
    from .sprite import Sprite
    from ..math import *


# Класс пакетной отрисовки спрайтов:
# Можно оптимизировать если урезать количество переключений между текстурками.
# Например, для каждой текстурки хранить все вершины спрайтов использующие её id.
# Типа, texture_id хранит n количество спрайтов использующие эту текстуру.
class SpriteBatch:
    def __init__(self, camera2d = None) -> None:
        self.camera2d     = camera2d  # Передайте 2D камеру если хотите увеличить скорость отрисовки.
        self.__is_begin__ = False
        self.vertices     = []
        self.texcoords    = []
        self.textures     = []

    # Очистить все списки и пр. и начать подготовку к отрисовке:
    def begin(self) -> None:
        if self.__is_begin__:
            raise Exception(
                "Function \".end()\" was not called in the last iteration of the loop.\n"
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self.__is_begin__  = True
        gl.glEnable(gl.GL_TEXTURE_2D)

    # Отрисовать спрайт:
    def draw(self, sprite: Sprite, x: float, y: float, width: int = None,
             height: int = None, angle: float = None, cull_sprites: bool = False) -> None:
        if not self.__is_begin__:
            raise Exception(
                "The \".begin()\" function was not called "
                "before the \".draw()\" function.")

        wdth, hght = width, height
        if width  is None: wdth = sprite.width
        if height is None: hght = sprite.height

        # Если камера не видит ваш спрайт, то мы пропускаем отрисовку спрайта:
        # ИНОГДА, ЭТО МОЖЕТ НАОБОРОТ ЗАНИЗИТЬ СКОРОСТЬ ОТРИСОВКИ!
        if cull_sprites and self.camera2d is not None:
            zoom, meter = self.camera2d.zoom, self.camera2d.meter / 100
            if not is_circle_rectangle((x+(wdth/2), y+(hght/2)), max(abs(wdth), abs(hght))/2 * 1.5,
                (self.camera2d.position.x-(self.camera2d.width*zoom)/2*meter,
                 self.camera2d.position.y-(self.camera2d.height*zoom)/2*meter,
                 self.camera2d.width*zoom*meter, self.camera2d.height*zoom*meter)): return

        # Вращаем вершины спрайта:
        if angle is not None and angle != 0:
            center_x      = x + (wdth / 2)
            center_y      = y + (hght / 2)
            angle_rad     = -radians(angle)
            angle_rad_sin = sin(angle_rad)
            angle_rad_cos = cos(angle_rad)
            x1, y1        = ( x         - center_x), ( y         - center_y)
            x2, y2        = ((x + wdth) - center_x), ( y         - center_y)
            x3, y3        = ((x + wdth) - center_x), ((y + hght) - center_y)
            x4, y4        = ( x         - center_x), ((y + hght) - center_y)

            self.vertices.extend([
                (x1 * angle_rad_cos - y1 * angle_rad_sin) + center_x,
                (x1 * angle_rad_sin + y1 * angle_rad_cos) + center_y,
                (x2 * angle_rad_cos - y2 * angle_rad_sin) + center_x,
                (x2 * angle_rad_sin + y2 * angle_rad_cos) + center_y,
                (x3 * angle_rad_cos - y3 * angle_rad_sin) + center_x,
                (x3 * angle_rad_sin + y3 * angle_rad_cos) + center_y,
                (x4 * angle_rad_cos - y4 * angle_rad_sin) + center_x,
                (x4 * angle_rad_sin + y4 * angle_rad_cos) + center_y,
            ])
        else:
            self.vertices.extend([
                x       , y       ,
                x + wdth, y       ,
                x + wdth, y + hght,
                x       , y + hght,
            ])

        self.texcoords.extend([0, 1, 1, 1, 1, 0, 0, 0])
        self.textures.append(sprite.texture.id)

    # Отрисовать все спрайты:
    def end(self) -> None:
        if self.__is_begin__: self.__is_begin__ = False
        else: raise Exception("The \".begin()\" function was not called before the \".end()\" function.")

        gl.glColor3f(1, 1, 1)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glVertexPointer(2, gl.GL_DOUBLE, 0, np.array(self.vertices))
        gl.glTexCoordPointer(2, gl.GL_DOUBLE, 0, np.array(self.texcoords))

        # Пройдитесь по каждой текстуре и отрендерьте все квадраты с этой текстурой:
        for index, texture in enumerate(self.textures):
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
            gl.glDrawArrays(gl.GL_TRIANGLE_FAN, index * 4, 4)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_TEXTURE_2D)

        self.vertices.clear()
        self.texcoords.clear()
        self.textures.clear()
