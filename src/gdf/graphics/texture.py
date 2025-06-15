#
# texture.py - Создаёт класс текстуры.
#


# Импортируем:
import pygame
import numpy as np
from .gl import *
from .image import Image
from . import BufferManager


# Класс обычной текстуры:
class Texture:
    def __init__(self,
                 image:          Image = None,
                 is_flip_y:      bool  = False,
                 size:           tuple = None,
                 use_mipmap:     bool  = False,
                 texture_format: int   = gl.GL_RGBA8,
                 data_format:    int   = gl.GL_RGBA,
                 data_type:      int   = gl.GL_UNSIGNED_BYTE) -> None:
        self.image = image
        if image is None or image.surface is None:
            surface = pygame.Surface(tuple(size) if size is not None else (1, 1))
        else: surface = image.surface

        self.data   = pygame.image.tostring(surface, "RGBA", is_flip_y)
        self.width  = surface.get_width()
        self.height = surface.get_height()
        self.id     = int(gl.glGenTextures(1))

        if texture_format == gl.GL_DEPTH_COMPONENT: self.data = None
        self.begin()
        self.set_linear(use_begin_end=False)
        self.set_filter([gl.GL_TEXTURE_WRAP_S, gl.GL_TEXTURE_WRAP_T], gl.GL_CLAMP_TO_EDGE, use_begin_end=False)
        self.set_data(self.width, self.height, self.data, texture_format, data_format, data_type, False)
        if use_mipmap: gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        self.end()

    # Использовать текстуру:
    def begin(self) -> "Texture":
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.id)
        return self

    # Не используем текстуру:
    def end(self) -> "Texture":
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        return self

    # Установить данные текстуры:
    def set_data(self, width: int, height: int, data: bytes|bytearray|np.ndarray = None,
                 texture_format: int = gl.GL_RGBA8, data_format: int = gl.GL_RGBA,
                 data_type: int = gl.GL_UNSIGNED_BYTE, use_begin_end: bool = True) -> "Texture":
        if width is None: width = self.width
        if height is None: height = self.height
        self.width, self.height = int(width), int(height)
        self.data = data
        if use_begin_end: self.begin()
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, texture_format, self.width, self.height, 0, data_format, data_type, data)
        if use_begin_end: self.end()
        return self

    # Получить данные текстуры:
    def get_data(self, use_begin_end: bool = True) -> np.ndarray:
        if use_begin_end: self.begin()
        data = gl.glGetTexImage(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
        if use_begin_end: self.end()
        return np.frombuffer(data, np.uint8).reshape((self.height, self.width, 4))

    # Установить фильтрацию текстуры:
    def set_filter(self, name: int|list[int,], param: int, use_begin_end: bool = True) -> "Texture":
        if use_begin_end: self.begin()
        if isinstance(name, list):
            for filter_type in name: gl.glTexParameterf(gl.GL_TEXTURE_2D, filter_type, param)
        else: gl.glTexParameterf(gl.GL_TEXTURE_2D, name, param)
        if use_begin_end: self.end()
        return self

    # Установить сглаживание текстуры:
    def set_linear(self, use_begin_end: bool = True) -> "Texture":
        self.set_filter([gl.GL_TEXTURE_MAG_FILTER, gl.GL_TEXTURE_MIN_FILTER], gl.GL_LINEAR, use_begin_end)
        return self

    # Установить пикселизацию текстуры:
    def set_pixelized(self, use_begin_end: bool = True) -> "Texture":
        self.set_filter([gl.GL_TEXTURE_MAG_FILTER, gl.GL_TEXTURE_MIN_FILTER], gl.GL_NEAREST, use_begin_end)
        return self

    # Удалить текстуру:
    def destroy(self) -> None:
        if self.id != 0:
            BufferManager.add(BufferManager.TYPE_TEXTURE_BUFFER, self.id)
            self.id = 0


# Класс 3D текстуры:
class Texture3D:
    def __init__(self,
                 size:           tuple[int, int, int],
                 data:           np.ndarray = None,
                 texture_format: int = gl.GL_RGBA8,
                 data_format:    int = gl.GL_RGBA,
                 data_type:      int = gl.GL_UNSIGNED_BYTE) -> None:
        if size is None: size = (1, 1, 1)
        self.width  = int(size[0])
        self.height = int(size[1])
        self.depth  = int(size[2])
        self.id     = int(gl.glGenTextures(1))

        self.begin()
        self.set_linear(use_begin_end=False)
        self.set_filter([gl.GL_TEXTURE_WRAP_S, gl.GL_TEXTURE_WRAP_T], gl.GL_CLAMP_TO_EDGE, use_begin_end=False)
        self.set_data(self.width, self.height, self.depth, data, texture_format, data_format, data_type, False)
        self.end()

    # Использовать текстуру:
    def begin(self) -> "Texture3D":
        gl.glBindTexture(gl.GL_TEXTURE_3D, self.id)
        return self

    # Отключить текстуру:
    def end(self) -> "Texture3D":
        gl.glBindTexture(gl.GL_TEXTURE_3D, 0)
        return self

    # Установить данные текстуры:
    def set_data(self, width: int, height: int, depth: int, data: np.ndarray = None,
                 texture_format: int = gl.GL_RGBA8, data_format: int = gl.GL_RGBA,
                 data_type: int = gl.GL_UNSIGNED_BYTE, use_begin_end: bool = True) -> "Texture3D":
        if width is None: width = self.width
        if height is None: height = self.height
        if depth is None: depth = self.depth
        wdth, hght, dpth = int(width), int(height), int(depth)
        self.width, self.height, self.depth = wdth, hght, dpth
        if use_begin_end: self.begin()
        gl.glTexImage3D(gl.GL_TEXTURE_3D, 0, texture_format, wdth, hght, dpth, 0, data_format, data_type, data)
        if use_begin_end: self.end()
        return self

    # Получить данные текстуры:
    def get_data(self, use_begin_end: bool = True) -> np.ndarray:
        if use_begin_end: self.begin()
        data = gl.glGetTexImage(gl.GL_TEXTURE_3D, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
        if use_begin_end: self.end()
        return np.frombuffer(data, np.uint8).reshape((self.depth, self.height, self.width, 4))

    # Установить фильтрацию текстуры:
    def set_filter(self, name: int|list[int,], param: int, use_begin_end: bool = True) -> "Texture":
        if use_begin_end: self.begin()
        if isinstance(name, list):
            for filter_type in name: gl.glTexParameterf(gl.GL_TEXTURE_3D, filter_type, param)
        else: gl.glTexParameterf(gl.GL_TEXTURE_3D, name, param)
        return self

    # Установить сглаживание текстуры:
    def set_linear(self, use_begin_end: bool = True) -> "Texture3D":
        return self.set_filter([gl.GL_TEXTURE_MAG_FILTER, gl.GL_TEXTURE_MIN_FILTER], gl.GL_LINEAR, use_begin_end)

    # Установить пикселизацию текстуры:
    def set_pixelized(self, use_begin_end: bool = True) -> "Texture3D":
        return self.set_filter([gl.GL_TEXTURE_MAG_FILTER, gl.GL_TEXTURE_MIN_FILTER], gl.GL_NEAREST, use_begin_end)

    # Удалить текстуру:
    def destroy(self) -> None:
        if self.id != 0:
            BufferManager.add(BufferManager.TYPE_TEXTURE_BUFFER, self.id)
            self.id = 0
