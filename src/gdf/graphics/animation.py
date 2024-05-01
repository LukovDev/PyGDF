#
# animation.py - Создаёт класс для анимации.
#


# Импортируем:
if True:
    pass


# Класс 2D анимации:
class Animation2D:
    def __init__(self, frames: int, duration: float) -> None:
        self.frames   = frames    # Количество кадров анимации.
        self.duration = duration  # Продолжительность кадра.
        self.count    = 0.0       # Счётчик кадров.

    # Обновить анимацию:
    def update(self, delta_time: float) -> "Animation2D":
        self.count += (1/self.duration/60) * (delta_time*60)

        # Если счётчик превысил количество кадров, обнуляем его:
        if self.get_frame() > self.frames - 1: self.count = 0.0

    # Получить кадр анимации:
    def get_frame(self) -> int:
        return int(self.count)
