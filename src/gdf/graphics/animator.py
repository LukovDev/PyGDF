#
# animator.py - Создаёт класс для анимации.
#


# Класс 2D аниматора:
class Animator2D:
    def __init__(self, frames: int, duration: float) -> None:
        self.frames      = frames    # Количество кадров анимации.
        self.duration    = duration  # Продолжительность кадра в секундах.
        self.count       = 0.0       # Счётчик кадров.
        self._is_paused_ = False     # Анимация на паузе.

    # Обновить анимацию:
    def update(self, delta_time: float) -> "Animator2D":
        # Если анимация не на паузе:
        if not self._is_paused_:
            self.count += (1.0 / self.duration) * delta_time

        # Если счётчик превысил количество кадров, обнуляем его:
        if self.get_frame() > self.frames - 1: self.count = 0.0
        return self

    # Запустить анимацию:
    def start(self) -> "Animator2D":
        self.resume()
        return self

    # Остановить анимацию и вернуть к первому кадру:
    def stop(self) -> "Animator2D":
        self.pause()
        self.reset()
        return self

    # Остановить анимацию:
    def pause(self) -> "Animator2D":
        self._is_paused_ = True
        return self

    # Возобновить анимацию:
    def resume(self) -> "Animator2D":
        self._is_paused_ = False
        return self

    # Вернуть к первому кадру:
    def reset(self) -> "Animator2D":
        self.count = 0.0
        return self

    # Получить кадр анимации:
    def get_frame(self) -> int:
        return int(self.count)
