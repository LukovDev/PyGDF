#
# sprite.py - Создаёт класс спрайта. Просто позволяет отрисовывать текстуру.
#


# Импортируем:
if True:
    from .gl import *
    from .texture import Texture
    from .atlas import AtlasTexture
    from . import __rotate_vertices__


# Класс спрайта:
class Sprite2D:
    def __init__(self, texture: Texture | AtlasTexture) -> None:
        self.texture = texture
        self.id = self.texture.id
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
        gl.glColor(*color)

        # Структура текстурных координат:
        # LEFT  | BOTTOM
        # RIGHT | BOTTOM
        # RIGHT | TOP
        # LEFT  | TOP
        texcoords = [0, 1, 1, 1, 1, 0, 0, 0] if type(self.texture) is Texture else self.texture.texcoords

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
