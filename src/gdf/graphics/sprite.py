#
# sprite.py - Создаёт класс спрайта. Просто позволяет отрисовывать текстуру.
#


# Импортируем:
from .gl import *
from .texture import Texture
from .atlas import AtlasTexture
from . import _rotate_vertices_


# Класс спрайта:
class Sprite2D:
    def __init__(self, texture: Texture | AtlasTexture = None) -> None:
        self.texture = texture
        self.id      = 0
        self.width   = 1
        self.height  = 1

        # Если текстурка указана:
        if self.texture is not None:
            self.id     = self.texture.id
            self.width  = self.texture.width
            self.height = self.texture.height

    # Отрисовка:
    def render(self,
               x:      float,
               y:      float,
               width:  int = 0,
               height: int = 0,
               angle:  float = 0.0,
               color:  list = None
               ) -> "Sprite2D":
        if color is None: color = [1, 1, 1]

        # Если текстурка указана:
        if self.texture is not None:
            self.id     = self.texture.id
            self.width  = self.texture.width
            self.height = self.texture.height

        wdth, hght = width or self.width, height or self.height

        # Вращаем вершины спрайта:
        if angle != 0.0:
            vertices = _rotate_vertices_(x, y, wdth, hght, angle)
        else:
            vertices = [
                x       , y       ,
                x + wdth, y       ,
                x + wdth, y + hght,
                x       , y + hght,
            ]

        # Структура текстурных координат:
        # LEFT  | BOTTOM
        # RIGHT | BOTTOM
        # RIGHT | TOP
        # LEFT  | TOP
        if type(self.texture) is Texture or self.texture is None:
            texcoords = [0, 1, 1, 1, 1, 0, 0, 0]
        else: texcoords = self.texture.texcoords

        # Рисуем спрайт:
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)

        gl.glColor(*color)
        gl.glBegin(gl.GL_QUADS)
        for index in range(0, len(vertices), 2):
            gl.glTexCoord(texcoords[index], texcoords[index+1])
            gl.glVertex(vertices[index], vertices[index+1])
        gl.glEnd()

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glDisable(gl.GL_TEXTURE_2D)

        return self

    # Удалить спрайт:
    def destroy(self) -> None:
        self.texture.destroy()
