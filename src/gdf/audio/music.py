#
# music.py - Создаёт поддержку фоновой музыки. Основан на PyGame Mixer.
#


# Импортируем:
import io
import os
import pygame
pygame.init()


# Класс музыки:
class Music:
    def __init__(self, file_path: str | io.BytesIO = None) -> None:
        self.path    = file_path
        self.audio   = None
        self.channel = None
        self.is_loop = False

    # Загрузить музыку:
    def load(self, file_path: str | io.BytesIO = None) -> "Music":
        self.path = file_path if file_path is not None else self.path

        # Проверяем на наличие файла:
        if self.path is None or (isinstance(self.path, str) and not os.path.isfile(self.path)):
            raise FileNotFoundError(f"File not found: {self.path}")

        # Если мы передали не путь и не BytesIO, конвертируем в BytesIO:
        if not isinstance(self.path, str) and not isinstance(self.path, io.BytesIO):
            self.path = io.BytesIO(self.path)

        # Пытаемся загрузить:
        if self.path is None: return self
        try: self.audio = pygame.mixer.Sound(self.path)
        except Exception as error:
            raise Exception(f"Error in \"Music.load()\": {error}\n")

        return self

    # Проиграть музыку:
    def play(self, loop: bool = False, overlay: bool = True) -> "Music":
        if self.audio is None: return self
        if not overlay and self.channel is not None: self.channel.stop()
        self.is_loop = loop
        self.channel = self.audio.play(-1 if self.is_loop else 0)
        return self

    # Остановить проигрывание музыки:
    def stop(self) -> "Music":
        if self.audio is None: return self

        self.audio.stop()
        return self

    # Поставить проигрывание музыки на паузу:
    def pause(self) -> "Music":
        if self.channel is not None:
            self.channel.pause()
        return self

    # Возобновить проигрывание музыки:
    def resume(self) -> "Music":
        if self.channel is not None:
            self.channel.unpause()
        return self

    # Установить громкость музыки:
    def set_volume(self, volume: float) -> "Music":
        if self.audio is not None:
            self.audio.set_volume(volume)
        return self

    # Получить громкость музыки:
    def get_volume(self) -> float:
        if self.audio is None: return 0.0
        return self.audio.get_volume()

    # Установить цикличность:
    def set_looping(self, loop: bool) -> "Music":
        self.is_loop = loop
        return self

    # Получить цикличность:
    def get_looping(self) -> bool:
        return self.is_loop

    # Активен ли проигрыватель или нет:
    def get_active(self) -> bool:
        if self.channel is not None:
            return self.channel.get_busy()
        return False

    # Освобождаем ресурсы:
    def destroy(self) -> None:
        if self.channel is not None:
            self.channel.stop()
            self.channel = None
        if self.audio is not None:
            self.audio.stop()
            self.audio = None
