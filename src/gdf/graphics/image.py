#
# image.py - Создаёт класс изображения.
#


# Импортируем:
import pygame


# Класс изображения:
class Image:
    def __init__(self, size: tuple, surface: pygame.Surface = None) -> None:
        self.width   = size[0]
        self.height  = size[1]
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.data    = None

        if surface is not None: self._update_image_(surface)

    # Обновляет данные о поверхности, её размере и данных:
    def _update_image_(self, surface: pygame.Surface = None) -> None:
        if isinstance(surface, type(self)): surface = surface.surface
        self.data    = pygame.image.tostring(surface, "RGBA", False)
        self.width   = surface.get_width()
        self.height  = surface.get_height()
        self.surface = surface

    # Загружаем изображение:
    def load(self, file_path: str) -> "Image":
        try: self._update_image_(pygame.image.load(file_path))
        except Exception as error:
            raise Exception(f"Error in \"Image.load()\": {error}")
        return self

    # Сохраняем изображение:
    def save(self, file_path: str) -> "Image":
        try: pygame.image.save(self.surface, file_path)
        except Exception as error:
            raise Exception(f"Error in \"Image.save()\": {error}")
        return self

    # Установить альфа канал:
    def set_alpha(self, alpha: int) -> "Image":
        self.surface.set_alpha(abs(int(alpha)))
        return self

    # Закрасить изображение:
    def fill(self, color: list) -> "Image":
        if len(color) < 3: color = [0, 0, 0]
        self.surface.fill(color)
        return self

    # Нарисовать повехность на этом изображении:
    def draw(self, image: "Image", x: int, y: int) -> "Image":
        if not (isinstance(image, type(self)) or isinstance(image, pygame.Surface)):
            raise Exception(
                f"Type Class error: You have specified a data type that is not "
                f"equal to the \"{type(self)}\" type (your type: \"{type(image)}\").")

        if isinstance(image, pygame.Surface):
            self.surface.blit(image, (int(x), int(y)))
        elif isinstance(image, type(self)) and image.surface is not None:
            self.surface.blit(image.surface, (int(x), int(y)))
        return self

    # Изменить размер:
    def resize(self, width: int, height: int) -> "Image":
        self.surface = pygame.transform.scale(self.surface, (width, height))
        self._update_image_(self.surface)
        return self
