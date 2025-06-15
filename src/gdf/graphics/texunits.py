#
# texunits.py - Создаёт класс текстурных юнитов для шейдеров.
#


# Импортируем:
from .gl import *
from .texture import Texture, Texture3D


# Все текстурные юниты заняты:
class TextureUnitsAllBusy(Exception): pass


# Класс текстурных юнитов (это глобальный класс. Не создавайте экземпляры!):
class TextureUnits:
    # Юниты хранят индексы привязанных текстур (id unit: id texture):
    _units_: dict = {i: None for i in range(16)}  # Количество юнитов обычно от 16 до 32+.

    # Инициализировать юниты (только после создания окна! Эта функция вызывается автоматически в классе окна!):
    @staticmethod
    def _init_units_() -> None:
        TextureUnits._units_ = {i: None for i in range(gl.glGetIntegerv(gl.GL_MAX_TEXTURE_IMAGE_UNITS))}

    # Привязать текстуру к юниту:
    @staticmethod
    def bind(texture: Texture|Texture3D|int, texture_type: int = gl.GL_TEXTURE_2D) -> int:
        if isinstance(texture, (Texture, Texture3D)):
            if isinstance(texture, Texture3D):
                texture_type = gl.GL_TEXTURE_3D
            texture = texture.id

        # Возвращает индекс юнита к которому привязана текстура.
        for unit, texid in TextureUnits._units_.items():
            if texid == texture: return unit  # Если такая текстура уже привязана, возвращаем её юнит.
            # Привязываем к первому свободному юниту:
            if texid is None:
                gl.glActiveTexture(gl.GL_TEXTURE0+unit)
                gl.glBindTexture(texture_type, texture)
                gl.glActiveTexture(gl.GL_TEXTURE0)
                TextureUnits._units_[unit] = texture
                return unit  # Возвращаем айди юнита к которому привязались.
        used_units = f"{TextureUnits.get_busy_units()} of {TextureUnits.get_count_units()}"
        raise TextureUnitsAllBusy(f"There are no free units to bind (used {used_units}).")

    # Отвязать текстуру от юнита:
    @staticmethod
    def unbind(texture: Texture|Texture3D|int) -> int|None:
        if isinstance(texture, (Texture, Texture3D)): texture = texture.id

        # Возвращает индекс юнита от которого отвязалась текстура.
        for unit, texid in TextureUnits._units_.items():
            if texid == texture:
                gl.glActiveTexture(gl.GL_TEXTURE0+unit)
                gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
                gl.glActiveTexture(gl.GL_TEXTURE0)
                TextureUnits._units_[unit] = None
                return unit  # Возвращаем айди юнита от которого отвязались.
        return None

    # Перепривязать текстуру к конкретному юниту:
    @staticmethod
    def rebind(texture: Texture|Texture3D|int, unit_id: int, texture_type: int = gl.GL_TEXTURE_2D) -> int|None:
        if isinstance(texture, (Texture, Texture3D)):
            if isinstance(texture, Texture3D):
                texture_type = gl.GL_TEXTURE_3D
            texture = texture.id

        if unit_id in TextureUnits._units_:
            gl.glActiveTexture(gl.GL_TEXTURE0+unit_id)
            gl.glBindTexture(texture_type, texture)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            TextureUnits._units_[unit_id] = texture
            return unit_id
        return None

    # Получить айди юнита к которому привязана текстура:
    @staticmethod
    def get_unit_id(texture: Texture|Texture3D) -> int|None:
        if isinstance(texture, (Texture, Texture3D)): texture = texture.id
        return next((k for k, v in TextureUnits._units_.items() if v == texture), None)

    # Получить айди текстуры по айди юнита:
    @staticmethod
    def get_texture_id(unit_id: int) -> int|None:
        return next((v for k, v in TextureUnits._units_.items() if k == unit_id), None)

    # Получить список всех свободных юнитов:
    @staticmethod
    def get_free_units() -> list:
        return [k for k, v in TextureUnits._units_.items() if v is None]

    # Получить список всех занятых юнитов:
    @staticmethod
    def get_busy_units() -> list:
        return [k for k, v in TextureUnits._units_.items() if v is not None]

    # Получить количество всех юнитов:
    @staticmethod
    def get_count_units() -> int:
        return len(TextureUnits._units_)
