#
# image.py - Создаёт класс изображения.
#


# Импортируем:
if True:
    import pygame


# Класс изображения:
class Image:
    def __init__(self, surface: pygame.Surface = None) -> None:
        self.width, self.height = 0, 0
        self.surface = None
        self.data = None

        if surface is not None: self.__update_image__(surface)

    # Обновляет данные о поверхности, её размере и данных:
    def __update_image__(self, surface: pygame.Surface = None) -> None:
        self.data = pygame.image.tostring(surface, "RGBA", False)
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.surface = surface

    # Загружаем изображение:
    def load(self, file_path: str) -> "Image":
        try: self.__update_image__(pygame.image.load(file_path))
        except Exception as error: raise Exception(f"Error in \"Image.load()\":\n{error}\n")
        return self

    # Сохраняем изображение:
    def save(self, file_path: str) -> "Image":
        try: pygame.image.save(self.surface, file_path)
        except Exception as error: raise Exception(f"Error in \"Image.save()\":\n{error}\n")
        return self

    # Изменить размер:
    def resize(self, width: int, height: int) -> "Image":
        self.surface = pygame.transform.scale(self.surface, (width, height))
        self.__update_image__(self.surface)
        return self
