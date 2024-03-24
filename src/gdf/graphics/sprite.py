#
# sprite.py - Создаёт класс спрайта. Просто позволяет отрисовывать текстуру.
#


# Импортируем:
if True:
    from .gl import *
    from .texture import Texture
    from .atlas import AtlasTexture
    from ..math import *


# Ускоренная функция поворота вершин спрайта:
@numba.njit
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


# Класс спрайта:
class Sprite:
    def __init__(self, texture: Texture | AtlasTexture) -> None:
        self.texture = texture
        self.id = self.texture.id
        self.width  = self.texture.width
        self.height = self.texture.height

    # Отрисовка:
    def render(self, x: float, y: float, width: int = 0, height: int = 0,
               angle: float = 0.0, color: list = None) -> "Sprite":
        if color is None:  color = [1, 1, 1, 1]

        wdth, hght = width or self.width, height or self.height

        # Вращаем вершины спрайта:
        if angle != 0.0:
            vertices = __rotate_vertices__(x, y, wdth, hght, angle)
        else:
            vertices = [
                x       , y       ,
                x + wdth, y       ,
                x + wdth, y + hght,
                x       , y + hght,
            ]

        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture.id)

        gl.glBegin(gl.GL_QUADS)
        gl.glColor4f(*color)

        # Структура текстурных координат:
        # LEFT  | BOTTOM
        # RIGHT | BOTTOM
        # RIGHT | TOP
        # LEFT  | TOP
        texcoords = [0, 1, 1, 1, 1, 0, 0, 0] if type(self.texture) is Texture else self.texture.texcoords

        for index in range(0, len(vertices), 2):
            gl.glTexCoord2f(texcoords[index], texcoords[index+1])
            gl.glVertex2d(vertices[index], vertices[index+1])
        gl.glEnd()

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glDisable(gl.GL_TEXTURE_2D)

        return self

    # Удалить спрайт:
    def destroy(self) -> None:
        self.texture.destroy()
