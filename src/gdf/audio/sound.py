#
# sound.py - Создаёт поддержку звуков. Основан на PyOpenAL.
#


# Импортируем:
if True:
    from .al import *
    from ..math import *


# Класс звука:
class Sound:
    def __init__(self) -> None:
        self.sound = None
        self.__is_playing__ = False
        self.__is_paused__ = False
        self.__is_loop__ = False

    # Загрузить звук:
    def load(self, file_path: str) -> "Sound":
        # Пытаемся загрузить:
        try: self.sound = al.oalOpen(file_path)
        except Exception as error:
            raise Exception(f"Error in \"Sound.load()\": {error}\n")
        return self

    # Проиграть звук:
    def play(self, is_loop: bool = False) -> "Sound":
        if self.sound is None: return self

        self.set_looping(is_loop)
        self.rewind()
        self.sound.play()
        self.__is_playing__ = True
        self.__is_paused__ = False
        return self

    # Остановить проигрывание звука:
    def stop(self) -> "Sound":
        if self.sound is None: return self

        self.sound.stop()
        self.__is_playing__ = False
        self.__is_paused__ = False
        return self

    # Поставить проигрывание звука на паузу:
    def pause(self) -> "Sound":
        if self.sound is None: return self

        if self.__is_playing__:
            self.sound.pause()
            self.__is_paused__ = True
            self.__is_playing__ = False
        return self

    # Возобновить проигрывание звука:
    def resume(self) -> "Sound":
        if self.sound is None: return self

        if self.__is_paused__:
            self.sound.play()
            self.__is_paused__ = False
            self.__is_playing__ = True
        return self

    # Перемотать к началу:
    def rewind(self) -> "Sound":
        if self.sound is None: return self
        self.sound.rewind()
        return self

    # Установить скорость звука:
    def set_pitch(self, pitch: float) -> "Sound":
        if self.sound is None: return self
        self.sound.set_pitch(pitch)
        return self

    # Получить скорость звука:
    def get_pitch(self) -> float:
        if self.sound is None: return 0.0
        return self.sound.pitch

    # Установить громкость звука:
    def set_volume(self, volume: float) -> "Sound":
        if self.sound is None: return self
        self.sound.set_gain(volume)
        return self

    # Получить громкость звука:
    def get_volume(self) -> float:
        if self.sound is None: return 0.0
        return self.sound.gain

    # Установить расстояние, при котором звук будет воспроизводиться с максимальной громкостью без затухания:
    def set_min_distance(self, value: float) -> "Sound":
        if self.sound is None: return self
        self.sound.set_reference_distance(value)
        return self

    # Получить расстояние, при котором звук будет воспроизводиться с максимальной громкостью без затухания:
    def get_min_distance(self) -> float:
        if self.sound is None: return 0.0
        return self.sound.reference_distance

    # Установить максимальное расстояние на котором слышен звук:
    def set_max_distance(self, value: float) -> "Sound":
        if self.sound is None: return self
        self.sound.set_max_distance(value)
        return self

    # Получить максимальное расстояние на котором слышен звук:
    def get_max_distance(self) -> float:
        if self.sound is None: return 0.0
        return self.sound.max_distance

    # Установить силу затухания звука с расстоянием:
    def set_rolloff_factor(self, value: float = 1.0) -> "Sound":
        if self.sound is None: return self
        self.sound.set_rolloff_factor(value)
        return self

    # Получить силу затухания звука с расстоянием:
    def get_rolloff_factor(self) -> float:
        if self.sound is None: return 0.0
        return self.sound.rolloff_factor

    # Установить минимальное значение громкости звука:
    def set_min_volume(self, value: float) -> "Sound":
        if self.sound is None: return self
        self.sound.set_min_gain(abs(value))
        return self

    # Получить минимальное значение громкости звука:
    def get_min_volume(self) -> float:
        if self.sound is None: return 0.0
        return self.sound.min_gain

    # Установить максимальное значение громкости звука:
    def set_max_volume(self, value: float) -> "Sound":
        if self.sound is None: return self
        self.sound.set_max_gain(abs(value))
        return self

    # Получить максимальное значение громкости звука:
    def get_max_volume(self) -> float:
        if self.sound is None: return 0.0
        return self.sound.max_gain

    # Установить позицию:
    def set_position(self, position: vec3) -> "Sound":
        if self.sound is None: return self
        self.sound.set_position(position)
        return self

    # Получить позицию:
    def get_position(self) -> vec3:
        if self.sound is None: return vec3(0)
        return vec3(self.sound.position)

    # Установить скорость звука:
    def set_velocity(self, velocity: vec3) -> "Sound":
        if self.sound is None: return self
        self.sound.set_velocity(velocity)
        return self

    # Получить скорость звука:
    def get_velocity(self) -> vec3:
        if self.sound is None: return vec3(0)
        return vec3(self.sound.velocity)

    # Установить звук относительно слушателя:
    def set_relative(self, is_relative: bool) -> "Sound":
        if self.sound is None: return self
        self.sound.set_source_relative(is_relative)
        return self

    # Получить звук относительно слушателя:
    def get_relative(self) -> bool:
        if self.sound is None: return False
        return self.sound.relative

    # Установить цикличность:
    def set_looping(self, is_loop: bool) -> "Sound":
        if self.sound is None: return self
        self.__is_loop__ = is_loop
        self.sound.set_looping(self.__is_loop__)
        return self

    # Получить цикличность:
    def get_looping(self) -> bool:
        if self.sound is None: return False
        return self.__is_loop__

    # Активен ли проигрыватель или нет:
    def get_active(self) -> bool:
        if self.sound is None: return False
        return self.sound.get_state() == al.AL_PLAYING

    # Освобождаем ресурсы:
    def destroy(self) -> None:
        if self.sound is None: return
        self.sound.close()
        self.sound.destroy()
