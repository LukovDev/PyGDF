#
# sprite.py - Создаёт класс спрайта. Просто позволяет отрисовывать текстуру.
#


# Импортируем:
if True:
    from .gl import *
    from .texture import Texture
    from ..math import *


# Класс спрайта:
class Sprite:
    def __init__(self, texture: Texture) -> None:
        self.texture = texture
        self.width = self.texture.width
        self.height = self.texture.height

    # Отрисовка:
    def render(self, x: float, y: float, width: int = None, height: int = None,
               angle: float = None, color: list = None) -> None:
        wdth, hght = width, height
        if color is None:  color = [1, 1, 1, 1]
        if width is None:  wdth = self.width
        if height is None: hght = self.height

        # Вращаем вершины спрайта:
        if angle is not None and angle != 0:
            center_x      = x + (wdth / 2)
            center_y      = y + (hght / 2)
            angle_rad     = -radians(angle)
            angle_rad_sin = sin(angle_rad)
            angle_rad_cos = cos(angle_rad)

            x1, y1 = ( x         - center_x), ( y         - center_y)
            x2, y2 = ((x + wdth) - center_x), ( y         - center_y)
            x3, y3 = ((x + wdth) - center_x), ((y + hght) - center_y)
            x4, y4 = ( x         - center_x), ((y + hght) - center_y)

            vertices = [
                (x1 * angle_rad_cos - y1 * angle_rad_sin) + center_x,
                (x1 * angle_rad_sin + y1 * angle_rad_cos) + center_y, 0, 1,
                (x2 * angle_rad_cos - y2 * angle_rad_sin) + center_x,
                (x2 * angle_rad_sin + y2 * angle_rad_cos) + center_y, 1, 1,
                (x3 * angle_rad_cos - y3 * angle_rad_sin) + center_x,
                (x3 * angle_rad_sin + y3 * angle_rad_cos) + center_y, 1, 0,
                (x4 * angle_rad_cos - y4 * angle_rad_sin) + center_x,
                (x4 * angle_rad_sin + y4 * angle_rad_cos) + center_y, 0, 0,
            ]
        else:
            vertices = [
                x       , y       , 0, 1,
                x + wdth, y       , 1, 1,
                x + wdth, y + hght, 1, 0,
                x       , y + hght, 0, 0,
            ]

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture.id)

        gl.glBegin(gl.GL_TRIANGLE_FAN)
        gl.glColor4f(*color)
        for index in range(len(vertices)//4):
            gl.glTexCoord2f(vertices[index*4+2], vertices[index*4+3])
            gl.glVertex2d(vertices[index*4], vertices[index*4+1])
        gl.glEnd()

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glDisable(gl.GL_TEXTURE_2D)

    # Удалить спрайт:
    def destroy(self) -> None:
        self.texture.destroy()
