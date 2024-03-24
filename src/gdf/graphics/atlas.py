#
# atlas.py - Создаёт поддержку атласов текстур.
#


# Импортируем:
if True:
    import pygame
    from .texture import Image, Texture


# Класс атласа текстур:
class AtlasTexture: pass  # Реализовать.
    # def __init__(self) -> None:
    #     self.atlas = None   # Текстура атласа.
    #     self.textures = {}  # Данные текстур в атласе.
    #     self.tex_uv = {}    # Текстурные координаты в атласе.

    # # Добавить текстуру в атлас:
    # def add_texture(self, name: str, texture: Texture) -> "AtlasTexture":
    #     self.textures[name] = texture

    #     return self

    # # Получить текстуру из атласа:
    # def get_texture(self, name: str) -> list:
    #     return self.tex_uv[name]

    # # Собрать атлас текстур:
    # def build(self) -> "AtlasTexture":
    #     # Сортировка текстур по убыванию размеров
    #     sorted_textures = sorted(self.textures.values(), key=lambda tex: tex.width * tex.height, reverse=True)

    #     # Подсчёт размеров атласа:
    #     width = sum(texture.width for texture in sorted_textures)
    #     height = max(texture.height for texture in sorted_textures)

    #     # Рисуем текстуры на атласе:
    #     atlas = pygame.Surface((width, height))
    #     x_offset = 0
    #     for texture in sorted_textures:
    #         atlas.blit(texture.image.surface, (x_offset, 0))
    #         # self.tex_uv[texture.name] = [(x_offset, 0), (x_offset + texture.width, 0),
    #         #                               (x_offset + texture.width, texture.height), (x_offset, texture.height)]
    #         x_offset += texture.width

    #     self.atlas = Texture(Image(atlas)).set_pixelized()
    #     return self

    # # Удалить атлас текстур:
    # def destroy(self) -> None:
    #     if self.atlas is None: return

    #     self.atlas.destroy()
