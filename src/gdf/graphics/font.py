#
# font.py - Создаёт классы для работы с графическим текстом.
#


# Импортируем:
if True:
    import pygame
    from .image import Image
    from .texture import Texture
    from .sprite import Sprite2D


# Получить какие шрифты есть в системе:
def get_fonts() -> list:
    return pygame.font.get_fonts()


# Получить адрес конкретного шрифта:
def match_font(font_name: str) -> str:
    return pygame.font.match_font(font_name)


# Класс шрифта:
class Font:
    def __init__(self, font_path: str, font_size: int) -> None:
        if font_path is not None and os.path.isfile(font_path):
            self.font = pygame.font.Font(font_path, font_size)
        else: self.font = pygame.font.SysFont("Arial", font_size)

    # Получить спрайт текста:
    def get_sprite(self, text: str, color: list, bg_color: list = None,
                   offset_x: int = 0, offset_y: int = 0, smooth: bool = True) -> Sprite2D:
        if bg_color is None: bg_color = [0, 0, 0, 0]
        srf = self.font.render(text, smooth, color[:3])
        srf.set_alpha(color[3])
        srf_size = srf.get_width()+offset_x*2, srf.get_height()+offset_y*2
        bg_surface = pygame.Surface(srf_size, pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        bg_surface.blit(srf, (offset_x, offset_y))
        texture = Texture(Image(surface=bg_surface))
        return Sprite2D(texture)


# Класс системного шрифта:
class SysFont:
    def __init__(self, font_name: str, font_size: int) -> None:
        self.font = pygame.font.SysFont(font_name, font_size)

    # Получить спрайт текста:
    def get_sprite(self, text: str, color: list, bg_color: list = None,
                   offset_x: int = 0, offset_y: int = 0, smooth: bool = True) -> Sprite2D:
        if bg_color is None: bg_color = [0, 0, 0, 0]
        srf = self.font.render(text, smooth, color[:3])
        srf.set_alpha(color[3])
        srf_size = srf.get_width()+offset_x*2, srf.get_height()+offset_y*2
        bg_surface = pygame.Surface(srf_size, pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        bg_surface.blit(srf, (offset_x, offset_y))
        texture = Texture(Image(surface=bg_surface))
        return Sprite2D(texture)
