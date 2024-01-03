#
# texture.py - Создаёт класс текстуры.
#


# Импортируем:
if True:
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    import pygame
    from .gl import *
    from .image import Image


# Класс текстуры:
class Texture:
    def __init__(self, image: Image, is_flip_y: bool = False) -> None:
        self.image  = image
        self.id     = int
        self.data   = pygame.image.tostring(image.surface, "RGBA", is_flip_y)
        self.width  = image.width
        self.height = image.height
        self.id     = int(gl.glGenTextures(1))

        gl.glEnable(gl.GL_TEXTURE_2D)

        self.set_filter()
        self.set_filter([gl.GL_TEXTURE_WRAP_S, gl.GL_TEXTURE_WRAP_T], gl.GL_CLAMP_TO_EDGE)

        wdth, hght = self.width, self.height
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, wdth, hght, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, self.data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glDisable(gl.GL_TEXTURE_2D)

    # Установить фильтрацию текстуры:
    def set_filter(self, name=[gl.GL_TEXTURE_MAG_FILTER, gl.GL_TEXTURE_MIN_FILTER], param=gl.GL_LINEAR) -> "Texture":
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)
        if type(name) is list:
            for names in name: gl.glTexParameterf(gl.GL_TEXTURE_2D, names, param)
        else: gl.glTexParameterf(gl.GL_TEXTURE_2D, name, param)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        return self

    # Установить пикселизацию текстуры:
    def set_pixelized(self) -> "Texture":
        return self.set_filter([gl.GL_TEXTURE_MAG_FILTER, gl.GL_TEXTURE_MIN_FILTER], gl.GL_NEAREST)

    # Удалить текстуру:
    def destroy(self) -> None:
        gl.glDeleteTextures(self.id)
