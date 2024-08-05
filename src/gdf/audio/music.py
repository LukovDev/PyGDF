#
# music.py - Создаёт поддержку фоновой музыки. Основан на PyGame Mixer.
#


# Импортируем:
import pygame
pygame.init()


# Класс музыки:
class Music:
    def __init__(self) -> None:
        self.audio = None
        self.channel = None

    # Загрузить музыку:
    def load(self, file_path: str) -> "Music":
        # Пытаемся загрузить:
        try: self.audio = pygame.mixer.Sound(file_path)
        except Exception as error:
            raise Exception(f"Error in \"Music.load()\": {error}\n")

        return self

    # Проиграть музыку:
    def play(self, is_loop: bool = False) -> "Music":
        if self.channel is not None:
            self.channel.stop()
        self.channel = self.audio.play(-1 if is_loop else 0)
        return self

    # Остановить проигрывание музыки:
    def stop(self) -> "Music":
        if self.audio is None: return self

        self.audio.stop()
        return self

    # Поставить проигрывание музыки на паузу:
    def pause(self) -> "Music":
        self.channel.pause()
        return self

    # Возобновить проигрывание музыки:
    def resume(self) -> "Music":
        self.channel.unpause()
        return self

    # Установить громкость музыки:
    def set_volume(self, volume: float) -> "Music":
        if self.audio is None: return self
        self.audio.set_volume(volume)
        return self

    # Получить громкость музыки:
    def get_volume(self) -> float:
        if self.audio is None: return 0.0
        return self.audio.get_volume()

    # Активен ли проигрыватель или нет:
    def get_active(self) -> bool:
        if self.channel is not None:
            return self.channel.get_busy()
        return False

    # Освобождаем ресурсы:
    def destroy(self) -> None:
        if self.audio is None: return
        self.audio = None
        if self.channel is not None:
            self.channel.stop()
            self.channel = None
