#
# font.py - Создаёт классы для работы с графическим текстом.
#


# Импортируем:
if True:
    import os
    import pygame
    from .image import Image
    from .texture import Texture


# Класс генератора текста из шрифта:
class FontGenerator:
    def __init__(self, file_path: str = None) -> None:
        self.__font_path__ =  file_path
        self.texture = None

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
        # Настраиваем цвета:
        if color    is None: color    = [1, 1, 1, 1]
        if bg_color is None: bg_color = [0, 0, 0, 0]
        color    = [c * 255 for c in color]
        bg_color = [c * 255 for c in bg_color]

        # Удаляем старую текстуру текста:
        if self.texture is not None:
            self.texture.destroy()
            self.texture = None

        # Создаём экземпляр шрифта:
        if self.__font_path__ is not None and os.path.isfile(self.__font_path__):
            font = pygame.font.Font(self.__font_path__, font_size)
        else: font = pygame.font.SysFont("Arial", font_size)

        # Создаём и получаем битмап текста из шрифта:
        bitmap = font.render(text, smooth, color[:3])
        bitmap.set_alpha(color[3])
        bitmap_size = bitmap.get_width()+padding_x*2, bitmap.get_height()+padding_y*2

        # Создаём фон текста, и рисуем на нём основной текст:
        text_bitmap = pygame.Surface(bitmap_size, pygame.SRCALPHA)
        text_bitmap.fill(bg_color)
        text_bitmap.blit(bitmap, (padding_x, padding_y))

        # Создаём текстуру из битмапа:
        if self.texture is None: self.texture = Texture(Image(surface=text_bitmap))

        self.texture.set_linear() if smooth else self.texture.set_pixelized()

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
