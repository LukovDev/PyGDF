#
# animation.py - Создаёт класс для анимации.
#


# Импортируем:
if True:
    pass


# Класс 2D анимации:
class Animation2D:
    def __init__(self, frames: int, duration: float) -> None:
        self.frames    = frames    # Количество кадров анимации.
        self.duration  = duration  # Продолжительность кадра.
        self.count     = 0.0       # Счётчик кадров.
        self.is_paused = False     # На паузе.

    # Обновить анимацию:
    def update(self, delta_time: float) -> "Animation2D":
        # Если анимация не на паузе:
        if not self.is_paused:
            self.count += (1/self.duration/60) * (delta_time*60)

        # Если счётчик превысил количество кадров, обнуляем его:
        if self.get_frame() > self.frames - 1: self.count = 0.0

        return self

    # Запустить анимацию:
    def start(self) -> "Animation2D":
        self.resume()

        return self

    # Остановить анимацию и вернуть к первому кадру:
    def stop(self) -> "Animation2D":
        self.pause()
        self.reset()

        return self

    # Остановить анимацию:
    def pause(self) -> "Animation2D":
        self.is_paused = True

        return self

    # Возобновить анимацию:
    def resume(self) -> "Animation2D":
        self.is_paused = False

        return self

    # Вернуть к первому кадру:
    def reset(self) -> "Animation2D":
        self.count = 0.0

        return self

    # Получить кадр анимации:
    def get_frame(self) -> int:
        return int(self.count)
