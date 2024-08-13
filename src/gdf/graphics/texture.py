#
# texture.py - Создаёт класс текстуры.
#


# Импортируем:
import pygame
import numpy as np
from .gl import *
from .image import Image


# Класс текстуры:
class Texture:
    def __init__(self, image: Image, is_flip_y: bool = False, size: tuple = None) -> None:
        self.image  = image
        self.id     = int
        if image is None or image.surface is None:
            surface = pygame.Surface(size if size is not None else (1, 1))
        else: surface = image.surface
        self.data   = pygame.image.tostring(surface, "RGBA", is_flip_y)
        self.width  = surface.get_width()
        self.height = surface.get_height()
        self.id     = int(gl.glGenTextures(1))

        gl.glEnable(gl.GL_TEXTURE_2D)

        self.set_linear()
        self.set_filter([gl.GL_TEXTURE_WRAP_S, gl.GL_TEXTURE_WRAP_T], gl.GL_CLAMP_TO_EDGE)

        wdth, hght = self.width, self.height
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, wdth, hght, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, self.data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glDisable(gl.GL_TEXTURE_2D)

    # Использовать текстуру:
    def begin(self) -> "Texture":
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)
        return self

    # Не используем текстуру:
    def end(self) -> "Texture":
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glDisable(gl.GL_TEXTURE_2D)
        return self

    # Получить данные текстуры:
    def get_data(self) -> np.ndarray:
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)
        data = gl.glGetTexImage(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
        return np.frombuffer(data, np.uint8).reshape((self.height, self.width, 4))

    # Установить фильтрацию текстуры:
    def set_filter(self, name: int, param: int) -> "Texture":
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)
        if type(name) is list:
            for names in name: gl.glTexParameterf(gl.GL_TEXTURE_2D, names, param)
        else: gl.glTexParameterf(gl.GL_TEXTURE_2D, name, param)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        return self

    # Установить сглаживание текстуры:
    def set_linear(self) -> "Texture":
        self.set_filter([gl.GL_TEXTURE_MAG_FILTER, gl.GL_TEXTURE_MIN_FILTER], gl.GL_LINEAR)
        return self

    # Установить пикселизацию текстуры:
    def set_pixelized(self) -> "Texture":
        self.set_filter([gl.GL_TEXTURE_MAG_FILTER, gl.GL_TEXTURE_MIN_FILTER], gl.GL_NEAREST)
        return self

    # Удалить текстуру:
    def destroy(self) -> None:
        gl.glDeleteTextures(self.id)
