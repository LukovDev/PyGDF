#
# sound.py - Создаёт поддержку звуков. Основан на PyOpenAL.
#


# Импортируем:
import os
from .al import *
from ..math import *


# Все экземпляры звука:
_all_sounds_ = []


# Класс звука:
class Sound:
    def __init__(self, file_path: str = None) -> None:
        global _all_sounds_ ; _all_sounds_.append(self)

        self.path   = file_path if isinstance(file_path, str) else None
        self.buffer = None  # Основной звук.
        self.sounds = []    # Стек воспроизводимых звуков.

        # Скрытые параметры звука. Только для использования внутри класса:
        self._soundvars_ = {
            "paused-snd": None,
            "is-paused":  False,
            "is-loop":    False,
            "pitch":      1.0,
            "volume":     1.0,
            "min-dist":   100.0,
            "max-dist":   100000.0,
            "rolloff":    1.0,
            "min-volume": 0.0,
            "max-volume": 1.0,
            "position":   vec3(0.0),
            "velocity":   vec3(0.0),
            "relative":   False,
        }
        self._soundvars_copy_ = dict(self._soundvars_)

    # Проверить все звуки, чтобы удалить ненужные и освободить память:
    def _check_sounds_(self) -> None:
        psd_snd = self._soundvars_["paused-snd"]

        # Фильтруем звуки от тех, что больше не воспроизводятся:
        self.sounds = [s for s in self.sounds if (s.get_state() == al.AL_PLAYING or s == psd_snd) or s.destroy()]

        # Генератор выше, работает примерно так:
        # new_stack = []
        # for sound in self.sounds:
        #     if sound.get_state() == al.AL_PLAYING or sound == psd_snd: new_stack.append(sound)
        #     else: sound.destroy()
        # self.sounds = new_stack

        # Удаляем звук на паузе если больше не воспроизводится даже если не на паузе:
        if psd_snd is not None and psd_snd.get_state() != al.AL_PLAYING and not self._soundvars_["is-paused"]:
            if psd_snd in self.sounds: self.sounds.remove(psd_snd)
            psd_snd.destroy() ; self._soundvars_["paused-snd"] = None

    # Загрузить звук:
    def load(self, file_path: str = None) -> "Sound":
        self.path = file_path if isinstance(file_path, str) else self.path

        # Проверяем на наличие файла:
        if not os.path.isfile(self.path):
            raise FileNotFoundError(f"File not found: {self.path}")

        # Пытаемся загрузить:
        try: self.buffer = al.oalOpen(self.path).buffer  # Берём только буфер.
        except Exception as error:
            raise Exception(f"Error in \"Sound.load()\": {error}\n")

        self.set_min_distance(100.0)
        self.set_max_distance(100000.0)

        return self

    # Проиграть звук:
    def play(self, loop: bool = False, overlay: bool = True) -> "Sound":
        if self.buffer is None: return self  # Мы не можем создать звуки если буфера не существует.
        self._soundvars_["is-loop"] = loop
        self._check_sounds_()

        # Если не используем наложение звуков, очищаем все прошлые звуки чтобы воспроизвести только один звук:
        for s in self.sounds:
            if loop: s.set_looping(False)
            if not overlay: s.destroy()
        if not overlay: self.sounds.clear()

        # Пытаемся создать новый звук. Если произошла ошибка (например, выход за пределы памяти), ничего не делаем:
        try:
            # Создаём источник звука из буфера:
            sound = al.Source(self.buffer)

            # Устанавливаем параметры звука:
            sound.set_pitch(self._soundvars_["pitch"])
            sound.set_gain(self._soundvars_["volume"])
            sound.set_reference_distance(self._soundvars_["min-dist"])
            sound.set_max_distance(self._soundvars_["max-dist"])
            sound.set_rolloff_factor(self._soundvars_["rolloff"])
            sound.set_min_gain(self._soundvars_["min-volume"])
            sound.set_max_gain(self._soundvars_["max-volume"])
            sound.set_position(self._soundvars_["position"])
            sound.set_velocity(self._soundvars_["velocity"])
            sound.set_source_relative(self._soundvars_["relative"])
            sound.set_looping(self._soundvars_["is-loop"])

            # Воспроизводим звук и добавляем в список звуков:
            sound.play()
            self.sounds.append(sound)
        except Exception as e: pass

        self._soundvars_["is-paused"] = False
        return self

    # Остановить проигрывание звука:
    def stop(self, all: bool = False) -> "Sound":
        self._check_sounds_()
        if not self.sounds: return self

        [s.stop() for s in self.sounds] if all else self.sounds[-1].stop()
        self._check_sounds_()

        self._soundvars_["is-paused"] = False
        return self

    # Поставить проигрывание звука на паузу:
    def pause(self) -> "Sound":
        self._check_sounds_()
        if not self.sounds: return self

        if not self._soundvars_["is-paused"]:
            self._soundvars_["paused-snd"] = self.sounds[-1]
            paused_snd = self._soundvars_["paused-snd"]
            if paused_snd.get_state() == al.AL_PLAYING:
                self._soundvars_["paused-snd"].pause()
            self._soundvars_["is-paused"] = True
        return self

    # Возобновить проигрывание звука:
    def resume(self) -> "Sound":
        self._check_sounds_()
        if not self.sounds: return self

        if self._soundvars_["is-paused"]:
            paused_snd = self._soundvars_["paused-snd"]
            if paused_snd is not None and paused_snd.get_state() == al.AL_PAUSED:
                self._soundvars_["paused-snd"].play()
            self._soundvars_["is-paused"] = False
        return self

    # Перемотать к началу:
    def rewind(self) -> "Sound":
        self._check_sounds_()
        if not self.sounds: return self
        self.sounds[-1].rewind()
        return self

    # Установить скорость звука:
    def set_pitch(self, pitch: float) -> "Sound":
        self._soundvars_["pitch"] = abs(pitch)
        self._check_sounds_()
        if not self.sounds: return self
        for s in self.sounds: s.set_pitch(abs(pitch))
        return self

    # Получить скорость звука:
    def get_pitch(self) -> float:
        self._check_sounds_()
        return self._soundvars_["pitch"]

    # Установить громкость звука:
    def set_volume(self, volume: float) -> "Sound":
        self._soundvars_["volume"] = abs(volume)
        self._check_sounds_()
        if not self.sounds: return self
        for s in self.sounds: s.set_gain(abs(volume))
        return self

    # Получить громкость звука:
    def get_volume(self) -> float:
        self._check_sounds_()
        return self._soundvars_["volume"]

    # Установить расстояние, при котором звук будет воспроизводиться с максимальной громкостью без затухания:
    def set_min_distance(self, value: float) -> "Sound":
        self._soundvars_["min-dist"] = abs(value)
        self._check_sounds_()
        if not self.sounds: return self
        for s in self.sounds: s.set_reference_distance(abs(value))
        return self

    # Получить расстояние, при котором звук будет воспроизводиться с максимальной громкостью без затухания:
    def get_min_distance(self) -> float:
        self._check_sounds_()
        return self._soundvars_["min-dist"]

    # Установить максимальное расстояние на котором слышен звук:
    def set_max_distance(self, value: float) -> "Sound":
        self._soundvars_["max-dist"] = abs(value)
        self._check_sounds_()
        if not self.sounds: return self
        for s in self.sounds: s.set_max_distance(abs(value))
        return self

    # Получить максимальное расстояние на котором слышен звук:
    def get_max_distance(self) -> float:
        self._check_sounds_()
        return self._soundvars_["max-dist"]

    # Установить силу затухания звука с расстоянием:
    def set_rolloff_factor(self, value: float = 1.0) -> "Sound":
        self._soundvars_["rolloff"] = abs(value)
        self._check_sounds_()
        if not self.sounds: return self
        for s in self.sounds: s.set_rolloff_factor(abs(value))
        return self

    # Получить силу затухания звука с расстоянием:
    def get_rolloff_factor(self) -> float:
        self._check_sounds_()
        return self._soundvars_["rolloff"]

    # Установить минимальное значение громкости звука:
    def set_min_volume(self, value: float) -> "Sound":
        self._soundvars_["min-volume"] = abs(value)
        self._check_sounds_()
        if not self.sounds: return self
        for s in self.sounds: s.set_min_gain(abs(value))
        return self

    # Получить минимальное значение громкости звука:
    def get_min_volume(self) -> float:
        self._check_sounds_()
        return self._soundvars_["min-volume"]

    # Установить максимальное значение громкости звука:
    def set_max_volume(self, value: float) -> "Sound":
        self._soundvars_["max-volume"] = abs(value)
        self._check_sounds_()
        if not self.sounds: return self
        for s in self.sounds: s.set_max_gain(abs(value))
        return self

    # Получить максимальное значение громкости звука:
    def get_max_volume(self) -> float:
        self._check_sounds_()
        return self._soundvars_["max-volume"]

    # Установить позицию:
    def set_position(self, position: vec2 | vec3) -> "Sound":
        if position is None: position = vec3(0.0)
        self._soundvars_["position"] = position if isinstance(position, vec3) else vec3(position, 0.0)
        self._check_sounds_()
        if not self.sounds: return self
        for s in self.sounds: s.set_position(self._soundvars_["position"])
        return self

    # Получить позицию:
    def get_position(self) -> vec3:
        self._check_sounds_()
        return self._soundvars_["position"]

    # Установить скорость звука:
    def set_velocity(self, velocity: vec2 | vec3) -> "Sound":
        if velocity is None: velocity = vec3(0.0)
        self._soundvars_["velocity"] = velocity if isinstance(velocity, vec3) else vec3(velocity, 0.0)
        self._check_sounds_()
        if not self.sounds: return self
        for s in self.sounds: s.set_velocity(self._soundvars_["velocity"])
        return self

    # Получить скорость звука:
    def get_velocity(self) -> vec3:
        self._check_sounds_()
        return self._soundvars_["velocity"]

    # Установить звук относительно слушателя:
    def set_relative(self, is_relative: bool) -> "Sound":
        self._soundvars_["relative"] = is_relative
        self._check_sounds_()
        if not self.sounds: return self
        for s in self.sounds: s.set_source_relative(is_relative)
        return self

    # Получить звук относительно слушателя:
    def get_relative(self) -> bool:
        self._check_sounds_()
        return self._soundvars_["relative"]

    # Установить цикличность:
    def set_looping(self, is_loop: bool) -> "Sound":
        self._soundvars_["is-loop"] = is_loop
        self._check_sounds_()
        if not self.sounds: return self
        self.sounds[-1].set_looping(self._soundvars_["is-loop"])
        return self

    # Получить цикличность:
    def get_looping(self) -> bool:
        self._check_sounds_()
        return self._soundvars_["is-loop"]

    # Активен ли проигрыватель или нет:
    def get_active(self) -> bool:
        self._check_sounds_()
        if not self.sounds: return False
        return self.sounds[-1].get_state() == al.AL_PLAYING

    # Освобождаем ресурсы:
    def destroy(self) -> None:
        [s.destroy() for s in self.sounds] ; self.sounds.clear()
        self._soundvars_ = dict(self._soundvars_copy_)  # Сбрасываем параметры.

        if self.buffer is not None:
            # self.buffer.destroy()  # По неизвестной причине, нельзя вручную удалить буфер звука.
            self.buffer = None
