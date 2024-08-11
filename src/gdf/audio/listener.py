#
# listener.py - Создаёт класс слушателя. Нужен для звуков. Основан на PyOpenAL.
#


# Импортируем:
from .al import *
from ..math import *


# Класс слушателя:
class Listener:
    def __init__(self,
                 position: vec3  = vec3(0, 0, 0),
                 look_at:  vec3  = vec3(0, 0, -1),
                 up:       vec3  = vec3(0, 1, 0),
                 volume:   float = 1.0) -> None:
        self.position = position
        self.look_at = look_at
        self.up = up
        self.volume = volume

        self.listener = al.Listener()
        self.listener.set_position(self.position)
        self.listener.set_orientation(list(self.look_at) + list(self.up))

    # Обновление слушателя:
    def update(self) -> "Listener":
        self.listener.set_position(self.position)
        self.listener.set_orientation(list(self.look_at) + list(self.up))
        self.listener.set_gain(abs(self.volume))
        return self

    # Установить позицию слушателя:
    def set_position(self, position: vec3) -> "Listener":
        self.position = position.xyz
        return self

    # Получить позицию слушателя:
    def get_position(self) -> vec3:
        return self.position

    # Установить ориентацию:
    def set_orientation(self, look_at: vec3, up: vec3) -> "Listener":
        self.look_at = look_at.xyz
        self.up = up.xyz
        return self

    # Получить ориентацию:
    def get_orientation(self) -> tuple[vec3, vec3]:
        return self.look_at, self.up

    # Установить громкость слушателя (усиление слуха):
    def set_volume(self, volume: float) -> "Listener":
        self.volume = volume
        return self

    # Установить громкость слушателя (усиление слуха):
    def get_volume(self) -> float:
        return self.volume

    # Освобождаем ресурсы:
    def destroy(self) -> None:
        pass  # Просто функция-затычка.
