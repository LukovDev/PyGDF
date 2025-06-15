#
# font.py - Создаёт классы для работы с графическим текстом.
#


# Импортируем:
import io
import os
import pygame
from .gl import *
from .image import Image
from .texture import Texture
from ..math import *


# Файл шрифта:
class FontFile:
    def __init__(self, file_path: str|io.BytesIO = None) -> None:
        self.path = file_path

    # Загрузить шрифт:
    def load(self, file_path: str|io.BytesIO = None) -> "FontFile":
        self.path = file_path if file_path is not None else self.path

        # Проверяем на наличие файла:
        if self.path is None or (isinstance(self.path, str) and not os.path.isfile(self.path)):
            raise FileNotFoundError(f"File not found: {self.path}")

        # Если мы передали не путь и не BytesIO, конвертируем в BytesIO:
        if not isinstance(self.path, str) and not isinstance(self.path, io.BytesIO):
            self.path = io.BytesIO(self.path)

        # Пытаемся загрузить:
        try:
            if isinstance(self.path, io.BytesIO): return self
            with open(self.path, "rb") as f:
                self.path = io.BytesIO(f.read())
        except Exception as error:
            raise Exception(f"Error in \"FontFile.load()\": {error}")
        return self


# Класс генератора текста из шрифта:
class FontGenerator:
    def __init__(self, font: FontFile = None) -> None:
        self.font = font
        self.texture = Texture()

    # Сгенерировать текстуру с текстом:
    def generate(self,
                 text:      str,
                 font_size: int,
                 color:     list = None,
                 bg_color:  list = None,
                 padding_x: int  = 0,
                 padding_y: int  = 0,
                 smooth:    bool = True) -> "FontGenerator":
        # Настраиваем цвета:
        if color is None: color = [1, 1, 1, 1]
        if bg_color is None: bg_color = [0, 0, 0, 0]

        # Контролируем чтобы в цветах был альфа канал, даже если его не передают:
        if len(color) < 4: color.append(1)
        if len(bg_color) < 4: bg_color.append(1)

        # Конвертируем цвета из 1-ричного в 256-ричный (0-255):
        color = [c * 255 for c in color]
        bg_color = [c * 255 for c in bg_color]

        # Создаём экземпляр шрифта:
        if isinstance(self.font, FontFile) and self.font.path is not None:
            font = pygame.font.Font(io.BytesIO(self.font.path.getbuffer()), font_size)
        else: font = pygame.font.SysFont("Arial", font_size)

        # Создаём и получаем битмап текста из шрифта:
        bitmap = font.render(text, smooth, color[:3])
        bitmap.set_alpha(color[3])
        bmpsize = (bitmap.get_width()+padding_x*2, bitmap.get_height()+padding_y*2)

        # Создаём фон текста, и рисуем на нём основной текст:
        img = Image(size=bmpsize)
        img.fill(bg_color)
        img.draw(bitmap, padding_x, padding_y)

        # Создаём текстуру из битмапа:
        if self.texture is None:
            self.texture = Texture(Image(surface=img))
        else:
            self.texture.image = img
            self.texture.set_data(bmpsize[0], bmpsize[1], img.data, gl.GL_RGBA8, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)

        # Устанавливаем сглаживание текстуры:
        self.texture.set_linear() if smooth else self.texture.set_pixelized()
        return self

    # Получить ширину текста:
    def get_width(self) -> int:
        return self.texture.width if self.texture is not None else 0

    # Получить высоту текста:
    def get_height(self) -> int:
        return self.texture.height if self.texture is not None else 0

    # Получить размер текстуры текста:
    def get_size(self) -> vec2:
        return vec2(self.get_width(), self.get_height())

    # Удалить шрифт:
    def destroy(self) -> None:
        if self.texture is not None:
            self.texture.destroy()
