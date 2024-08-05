#
# atlas.py - Создаёт класс текстуры, которую можно получить из упаковщика текстур.
#


# Импортируем:
from .texture import Texture


# Класс текстуры атласа:
class AtlasTexture:
    def __init__(self, atlas: Texture, width: int, height: int, texcoords: list) -> None:
        self.texture   = atlas
        self.id        = atlas.id
        self.width     = width
        self.height    = height
        self.texcoords = texcoords
