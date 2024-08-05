#
# scene.py - Создаёт класс сцены.
#


# Класс сцены:
class Scene:
    window = None

    # ------------------ Приведённые ниже функции должны быть записаны в унаследованном классе: ------------------------

    # Вызывается при переключении на эту сцену:
    def start(self) -> None:
        pass

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, event_list: list) -> None:
        pass

    # Вызывается каждый кадр (игровая отрисовка):
    def render(self, delta_time: float) -> None:
        pass

    # Вызывается при изменении размера окна:
    def resize(self, width: int, height: int) -> None:
        pass

    # Вызывается при разворачивании окна:
    def show(self) -> None:
        pass

    # Вызывается при сворачивании окна:
    def hide(self) -> None:
        pass

    # Вызывается при закрытии сцены:
    def destroy(self) -> None:
        pass
