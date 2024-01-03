#
# image.py - Создаёт класс изображения.
#


# Импортируем:
if True:
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    import pygame


# Класс изображения:
class Image:
    def __init__(self, path: str = "", surface: pygame.Surface = None) -> None:
        self.width, self.height = 0, 0
        self.surface = None
        self.data = None

        if surface is not None: self.__update_image__(surface)
        elif path != "": self.load(path)

    # Обновляет данные о поверхности, её размере и данных:
    def __update_image__(self, surface: pygame.Surface = None) -> None:
        self.data = pygame.image.tostring(surface, "RGBA", False)
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.surface = surface

    # Загружаем изображение:
    def load(self, path: str) -> None:
        try: self.__update_image__(pygame.image.load(path))
        except Exception as error: raise Exception(f"Error in \"Image.load()\":\n{error}\n")

    # Сохраняем изображение:
    def save(self, path: str) -> None:
        try: pygame.image.save(self.surface, filename=path)
        except Exception as error: raise Exception(f"Error in \"Image.save()\":\n{error}\n")

    # Изменить размер:
    def resize(self, width: int, height: int) -> None:
        self.surface = pygame.transform.scale(self.surface, (width, height))
        self.__update_image__(self.surface)
