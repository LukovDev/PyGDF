#
# font.py - Создаёт классы для работы с графическим текстом.
#


# Импортируем:
import io
import os
import pygame
from .image import Image
from .texture import Texture


# Файл шрифта:
class FontFile:
    def __init__(self, file_path: str | io.BytesIO = None) -> None:
        self.path = file_path if isinstance(file_path, str) else None
        self.data = file_path if isinstance(file_path, io.BytesIO) else None

    # Загрузить шрифт:
    def load(self, file_path: str | io.BytesIO = None) -> "FontFile":
        self.path = file_path if isinstance(file_path, str) else self.path

        if isinstance(self.path, str):
            with open(self.path, "rb") as f:
                self.data = io.BytesIO(f.read())
        elif isinstance(file_path, io.BytesIO):
            self.data = file_path
        elif isinstance(self.data, io.BytesIO) and file_path is None and self.path is None:
            pass  # Значит мы уже загрузили данные шрифта.

        return self


# Класс генератора текста из шрифта:
class FontGenerator:
    def __init__(self, font: FontFile = None) -> None:
        self.font = font
        self.texture = None

    # Запечь текст шрифта, и получить новую текстуру:
    def get_texture_text(self,
                         text:      str,
                         font_size: int,
                         color:     list = None,
                         bg_color:  list = None,
                         padding_x: int  = 0,
                         padding_y: int  = 0,
                         smooth:    bool = True
                         ) -> Texture:
        # Настраиваем цвета:
        if color    is None: color    = [1, 1, 1, 1]
        if bg_color is None: bg_color = [0, 0, 0, 0]

        # Контролируем чтобы в цветах был альфа канал, даже если его не передают:
        if len(color)    < 4: color.append(1)
        if len(bg_color) < 4: bg_color.append(1)

        # Конвертируем цвета из 1-ричного в 256-ричный (0-255):
        color    = [c * 255 for c in color]
        bg_color = [c * 255 for c in bg_color]

        # Создаём экземпляр шрифта:
        if isinstance(self.font, FontFile):
            font = pygame.font.Font(io.BytesIO(self.font.data.getbuffer()), font_size)
        else: font = pygame.font.SysFont("Arial", font_size)

        # Создаём и получаем битмап текста из шрифта:
        bitmap = font.render(text, smooth, color[:3])
        bitmap.set_alpha(color[3])
        bitmap_size = bitmap.get_width()+padding_x*2, bitmap.get_height()+padding_y*2

        # Создаём фон текста, и рисуем на нём основной текст:
        text_image = Image(bitmap_size)
        text_image.fill(bg_color)
        text_image.draw(bitmap, padding_x, padding_y)

        # Создаём текстуру из битмапа:
        texture = Texture(Image((0, 0), surface=text_image))

        # Устанавливаем сглаживание текстуры:
        texture.set_linear() if smooth else texture.set_pixelized()

        return texture

    # Запечь текст шрифта на текстуре:
    def bake_texture(self,
                     text:      str,
                     font_size: int,
                     color:     list = None,
                     bg_color:  list = None,
                     padding_x: int  = 0,
                     padding_y: int  = 0,
                     smooth:    bool = True
                     ) -> "Font":
        # Удаляем старую текстуру текста:
        if self.texture is not None:
            self.texture.destroy()
            self.texture = None

        # Создаём текстуру текста:
        if self.texture is None:
            self.texture = self.get_texture_text(text, font_size, color, bg_color, padding_x, padding_y, smooth)

        return self

    # Получить текстуру:
    def get_texture(self) -> Texture:
        return self.texture

    # Получить ширину текста:
    def get_width(self) -> int:
        return self.texture.width if self.texture is not None else 0

    # Получить высоту текста:
    def get_height(self) -> int:
        return self.texture.height if self.texture is not None else 0

    # Удалить шрифт:
    def destroy(self) -> None:
        if self.texture is not None:
            self.texture.destroy()
