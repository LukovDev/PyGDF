#
# environment.py - Создаёт класс окружающей среды звуков.
#


# Импортируем:
from .listener import Listener
from .sound import Sound
from ..math import *


# Класс звукового окружения:
class SoundEnvironment:
    def __init__(self, listener: Listener) -> None:
        self.listener = listener  # Слушатель.
        self.sounds   = []        # Список звуков.

    # Обновление среды:
    def update(self) -> "SoundEnvironment":
        for sound in self.sounds:
            # Устанавливаем громкость звука в зависимости от расстояния:
            distance = length(self.listener.position.xy-sound.get_position().xy)
            min_dst, max_dst, rolloff = sound.get_min_distance(), sound.get_max_distance(), sound.get_rolloff_factor()
            normal_val = (distance-max_dst)/(min_dst-max_dst) if min_dst != max_dst else distance-min_dst
            sound.set_volume(smoothstep(0.0, 1.0, normal_val**rolloff if distance < max_dst else 0.0))
        return self

    # Добавить новый звук в окружающую среду:
    def add(self,
            sound: Sound,
            min_distance: float = 100.0,
            max_distance: float = 100000.0,
            rolloff:      float = 1.0) -> "SoundEnvironment":
        sound.set_min_distance(min_distance)
        sound.set_max_distance(max_distance)
        sound.set_rolloff_factor(rolloff)
        self.sounds.append(sound)
        return self

    # Удалить звук из окружающей среды:
    def remove(self, sound: Sound) -> "SoundEnvironment":
        self.sounds = [l for l in self.sounds if l[0] != sound]
        return self

    # Освободить ресурсы удалив все звуки и слушателя:
    def destroy(self) -> None:
        for (sound, params) in self.sounds: sound.destroy()
        self.listener.destroy()
