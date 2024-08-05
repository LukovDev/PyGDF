#
# packer.py - Создаёт класс упаковщика текстур.
#


# Импортируем:
import pygame
from .image import Image
from .texture import Texture
from .atlas import AtlasTexture


# Упаковщик текстур:
class PackerTexture:
    def __init__(self) -> None:
        self.atlas    = None  # Текстура атласа.
        self.textures = {}    # Данные текстур в атласе (name: Texture). Образуется перед сборкой.
        self.tex_uv   = {}    # Текстурные координаты в атласе (name: list). Образуется после сборки.

    # Добавить текстуру в атлас:
    def add_texture(self, name: str, texture: Texture) -> "PackerTexture":
        self.textures[name] = texture
        return self

    # Удалить текстуру из текстур по имени:
    def remove_texture(self, name: str) -> "PackerTexture":
        if name in self.textures: del self.textures[name]
        return self

    # Получить текстуру из атласа:
    def get_texture(self, name: str) -> AtlasTexture:
        if name in self.textures and name in self.tex_uv:
            return AtlasTexture(self.atlas, self.textures[name].width, self.textures[name].height, self.tex_uv[name])
        else: raise KeyError(f"Texture \"{name}\" not found.")

    # Получить текстурные координаты определённой текстуры из атласа:
    def get_uv(self, name: str) -> list:
        if name in self.tex_uv: return self.tex_uv[name]
        else: raise KeyError(f"Texture \"{name}\" not found.")

    # Собрать атлас текстур:
    def pack(self, pixelized: bool = False, offset: int = 1) -> "PackerTexture":
        # INFO: offset применяется только по ширине, между текстурами.

        # Если текстура атласа уже была создана:
        if self.atlas is not None:
            self.atlas.destroy()
            self.tex_uv.clear()

        # Сортировка текстур по убыванию размеров:
        sorted_textures = sorted(self.textures.items(), key=lambda item: item[1].width * item[1].height, reverse=True)

        # Подсчёт размеров атласа:
        width = sum(texture.width for _, texture in sorted_textures) + (len(sorted_textures) - 1) * offset
        height = max(texture.height for _, texture in sorted_textures)

        # Создаём поверхность на которой будем рисовать текстуры:
        atlas = Image((width, height))

        # "Волшебный" алгоритм по расстановке текстур в атласе.
        # TODO: Этот алгоритм крайне не эффективен (по заполнению пустот). Его надо переделать.
        x_offset = 0
        for name, texture in sorted_textures:
            # Рисуем текстуру на атласе:
            atlas.draw(texture.image.surface, x_offset, 0)

            # Увеличиваем смещение x для следующей текстуры:
            x_offset += texture.width + offset

            # Добавляем UV-координаты:
            # Структура текстурных координат:
            # LEFT  | BOTTOM
            # RIGHT | BOTTOM
            # RIGHT | TOP
            # LEFT  | TOP
            self.tex_uv[name] = [
                (x_offset - texture.width - offset) / width, texture.height / height,
                (x_offset - offset)                 / width, texture.height / height,
                (x_offset - offset)                 / width, 0,
                (x_offset - texture.width - offset) / width, 0,
            ]

        # Создаём текстуру атласа:
        self.atlas = Texture(atlas)
        if pixelized: self.atlas.set_pixelized()
        return self

    # Удалить атлас текстур:
    def destroy(self) -> None:
        if self.atlas is None: return
        self.atlas.destroy()
