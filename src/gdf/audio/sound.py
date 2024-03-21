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
        self.is_paused = False
        self.is_loop = False

    # Загрузить звук:
    def load(self, file_path: str) -> "Sound":
        # Пытаемся загрузить:
        try: self.sound = al.oalOpen(file_path)
        except Exception as error:
            raise Exception(f"Error in \"Sound.load()\":\n{error}\n")

        return self

    # Проиграть звук:
    def play(self, is_loop: bool = False) -> "Sound":
        if self.sound is None: return self

        self.set_looping(is_loop)
        self.to_rewind()
        self.sound.play()

        return self

    # Остановить проигрывание звука:
    def stop(self) -> "Sound":
        if self.sound is None: return self

        self.sound.stop()

        return self

    # Поставить проигрывание звука на паузу:
    def pause(self) -> "Sound":
        if self.sound is None: return self

        self.sound.pause()
        self.is_paused = True

        return self

    # Возобновить проигрывание звука:
    def resume(self) -> "Sound":
        if self.sound is None: return self

        if self.is_paused:
            self.sound.play()
            self.is_paused = False

        return self

    # Перемотать к началу:
    def to_rewind(self) -> "Sound":
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
    def set_gain(self, volume: float) -> "Sound":
        if self.sound is None: return self

        self.sound.set_gain(volume)

        return self

    # Получить громкость звука:
    def get_gain(self) -> float:
        if self.sound is None: return 0.0

        return self.sound.gain

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

    # Установить расстояние, при котором звук будет воспроизводиться с максимальной громкостью без затухания:
    def set_reference_distance(self, value: float) -> "Sound":
        if self.sound is None: return self

        self.sound.set_reference_distance(value)

        return self

    # Получить расстояние, при котором звук будет воспроизводиться с максимальной громкостью без затухания:
    def get_reference_distance(self) -> float:
        if self.sound is None: return 0.0

        return self.sound.reference_distance

    # Установить минимальное значение громкости звука:
    def set_min_gain(self, value: float) -> "Sound":
        if self.sound is None: return self

        self.sound.set_min_gain(value)

        return self

    # Получить минимальное значение громкости звука:
    def get_min_gain(self) -> float:
        if self.sound is None: return 0.0

        return self.sound.min_gain

    # Установить максимальное значение громкости звука:
    def set_max_gain(self, value: float) -> "Sound":
        if self.sound is None: return self

        self.sound.set_max_gain(value)

        return self

    # Получить максимальное значение громкости звука:
    def get_max_gain(self) -> float:
        if self.sound is None: return 0.0

        return self.sound.max_gain

    # Установить коэффициент усиления звука за пределами внешней границы конуса направленности:
    def set_cone_outer_gain(self, value: float) -> "Sound":
        if self.sound is None: return self

        self.sound.set_cone_outer_gain(value)

        return self

    # Получить коэффициент усиления звука за пределами внешней границы конуса направленности:
    def get_cone_outer_gain(self, value: float) -> float:
        if self.sound is None: return 0.0

        return self.sound.cone_outer_gain

    # Установить угол, определяющий внешнюю границу конуса направленности источника звука:
    def set_cone_inner_angle(self, value: float) -> "Sound":
        if self.sound is None: return self

        self.sound.set_cone_inner_angle(value)

        return self

    # Получить угол, определяющий внешнюю границу конуса направленности источника звука:
    def get_cone_inner_angle(self, value: float) -> float:
        if self.sound is None: return 0.0

        return self.sound.cone_inner_angle

    # Установить угол, определяющий внутреннюю границу конуса направленности источника звука:
    def set_cone_outer_angle(self, value: float) -> "Sound":
        if self.sound is None: return self

        self.sound.set_cone_outer_angle(value)

        return self

    # Получить угол, определяющий внутреннюю границу конуса направленности источника звука:
    def get_cone_outer_angle(self, value: float) -> float:
        if self.sound is None: return 0.0

        return self.sound.cone_outer_angle

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

    # Установить направление источника звука:
    def set_direction(self, direction: vec3) -> "Sound":
        if self.sound is None: return self

        self.sound.set_direction(direction)

        return self

    # Получить направление источника звука:
    def get_direction(self) -> vec3:
        if self.sound is None: return vec3(0)

        return vec3(self.sound.direction)

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

        self.is_loop = is_loop
        self.sound.set_looping(self.is_loop)

        return self

    # Получить цикличность:
    def get_looping(self) -> bool:
        if self.sound is None: return False

        return self.is_loop

    # Проигрывается ли сейчас звук или нет:
    def get_playing(self, channel: int = None) -> bool:
        if self.sound is None: return False

        return self.sound.get_state() == al.AL_PLAYING

    # Освобождаем ресурсы:
    def destroy(self) -> "Sound":
        if self.sound is None: return self
        self.sound.close()
        self.sound.destroy()

        return self
