#
# music.py - Создаёт поддержку фоновой музыки. Основан на PyGame Mixer.
#


# Импортируем:
if True:
    import pygame
    pygame.init()


# Класс музыки:
class Music:
    def __init__(self) -> None:
        self.audio = None
        self.channels = []

    # Загрузить музыку:
    def load(self, file_path: str) -> "Music":
        # Пытаемся загрузить:
        try: self.audio = pygame.mixer.Sound(file_path)
        except Exception as error:
            raise Exception(f"Error in \"Music.load()\":\n{error}\n")

        return self

    # Проиграть музыку:
    def play(self, is_loop: bool = False) -> "Music":
        channel = self.audio.play(-1 if is_loop else 0)
        if channel is not None:
            self.channels.append(channel)
        return self

    # Остановить проигрывание музыки:
    def stop(self) -> "Music":
        if self.audio is None: return self

        self.audio.stop()
        return self

    # Поставить проигрывание музыки на паузу:
    def pause(self, channel: int = None) -> "Music":
        if channel is not None: channel.pause()
        else:
            for c in self.channels:
                c.pause()
        return self

    # Возобновить проигрывание музыки:
    def resume(self, channel: int = None) -> "Music":
        if channel is not None: channel.unpause()
        else:
            for c in self.channels:
                c.unpause()
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

    # Проигрывается ли сейчас музыка или нет:
    def get_playing(self, channel: int = None) -> bool:
        if channel is not None: return channel.get_busy()
        else:
            for c in self.channels:
                if c.get_busy(): return True
            return False

    # Освобождаем ресурсы:
    def destroy(self) -> None:
        if self.audio is None: return
        self.audio = None
