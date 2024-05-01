#
# font.py - Создаёт классы для работы с графическим текстом.
#


# Импортируем:
if True:
    import os
    import pygame
    from .image import Image
    from .texture import Texture
    from .sprite import Sprite2D


# Получить какие шрифты есть в системе:
def get_fonts() -> list:
    return pygame.font.get_fonts()


# Класс шрифта:
class Font:
    def __init__(self, font_path: str, font_size: int) -> None:
        if font_path is not None and os.path.isfile(font_path):
            self.font = pygame.font.Font(font_path, font_size)
        else: self.font = pygame.font.SysFont("Arial", font_size)
        self.texture = None

    # Получить текстуру текста:
    def get_texture(self, text: str, color: list, bg_color: list = None,
                   offset_x: int = 0, offset_y: int = 0, smooth: bool = True) -> Sprite2D:
        if bg_color is None: bg_color = [0, 0, 0, 0]
        bg_color = bg_color[0]*255, bg_color[1]*255, bg_color[2]*255, bg_color[3]*255
        color = color[0]*255, color[1]*255, color[2]*255, color[3]*255
        srf = self.font.render(text, smooth, color[:3])
        srf.set_alpha(color[3])
        srf_size = srf.get_width()+offset_x*2, srf.get_height()+offset_y*2
        bg_surface = pygame.Surface(srf_size, pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        bg_surface.blit(srf, (offset_x, offset_y))
        if self.texture is not None:
            self.texture.destroy()
            self.texture = None
        if self.texture is None:
            self.texture = Texture(Image(surface=bg_surface))
        return self.texture


# Класс системного шрифта:
class SysFont:
    def __init__(self, font_name: str, font_size: int) -> None:
        self.font = pygame.font.SysFont(font_name, font_size)
        self.texture = None

    # Получить текстуру текста:
    def get_texture(self, text: str, color: list, bg_color: list = None,
                   offset_x: int = 0, offset_y: int = 0, smooth: bool = True) -> Sprite2D:
        if bg_color is None: bg_color = [0, 0, 0, 0]
        bg_color = bg_color[0]*255, bg_color[1]*255, bg_color[2]*255, bg_color[3]*255
        color = color[0]*255, color[1]*255, color[2]*255, color[3]*255
        srf = self.font.render(text, smooth, color[:3])
        srf.set_alpha(color[3])
        srf_size = srf.get_width()+offset_x*2, srf.get_height()+offset_y*2
        bg_surface = pygame.Surface(srf_size, pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        bg_surface.blit(srf, (offset_x, offset_y))
        if self.texture is not None:
            self.texture.destroy()
            self.texture = None
        if self.texture is None:
            self.texture = Texture(Image(surface=bg_surface))
        return self.texture
