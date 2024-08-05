#
# input.py - Создаёт класс системы ввода.
#


# Импортируем:
import pygame
from pygame import constants as Key
from pygame import constants as Event
from .graphics import Window
from .math import *


# Специальный класс для получения состояния клавиш мыши:
class MouseScancodes:
    def __init__(self, keycodes: list) -> None:
        self.keycodes = keycodes

    # Когда используют этот класс как итеративный объект:
    def __getitem__(self, keycode: int) -> bool:
        return self.keycodes[keycode]

    # Дополнительная информация об этом объекте:
    def __repr__(self) -> str:
        return f"MouseScancodes({list(self.keycodes)})"


# Специальный класс для получения состояния клавиш клавиатуры:
class KeyboardScancodes:
    def __init__(self, keycodes: list | pygame.key.ScancodeWrapper) -> None:
        self.keycodes = keycodes

    # Когда используют этот класс как итеративный объект:
    def __getitem__(self, keycode: int) -> bool:
        if isinstance(self.keycodes, pygame.key.ScancodeWrapper):
            return self.keycodes[keycode]
        return keycode in self.keycodes

    # Дополнительная информация об этом объекте:
    def __repr__(self) -> str:
        return f"KeyboardScancodes({list(self.keycodes)})"


# Класс-обработчик ввода:
class InputHandler:
    def __init__(self, window: Window) -> None:
        self.window = window

    # ----------------------------------------------------- Мышь: ------------------------------------------------------

    # Получить нажатие кнопок мыши:
    @staticmethod
    def get_mouse_pressed() -> MouseScancodes:
        return MouseScancodes(list(pygame.mouse.get_pressed()))

    # Получить нажатие кнопки мыши:
    def get_mouse_down(self) -> MouseScancodes:
        return MouseScancodes(self.window._winvars_["mouse-down"])

    # Получить отжатие кнопки мыши:
    def get_mouse_up(self) -> MouseScancodes:
        return MouseScancodes(self.window._winvars_["mouse-up"])

    # Установить позицию мыши:
    @staticmethod
    def set_mouse_pos(pos: tuple | vec2) -> None:
        pygame.mouse.set_pos(pos[0], pos[1])

    # Получить позицию мыши:
    @staticmethod
    def get_mouse_pos() -> vec2:
        return vec2(pygame.mouse.get_pos())

    # Получить смещение мыши за кадр:
    def get_mouse_rel(self) -> vec2:
        return vec2(self.window._winvars_["mouse-rel"])

    # Получить нахождение мыши над окном:
    @staticmethod
    def get_mouse_focused() -> bool:
        return pygame.mouse.get_focused()

    # Получить вращение колёсика мыши:
    def get_mouse_scroll(self) -> vec2:
        return vec2(self.window._winvars_["mouse-scroll"])

    # Установить видимость мыши:
    def set_mouse_visible(self, visible: bool) -> None:
        self.window._winvars_["mouse-visible"] = visible
        pygame.mouse.set_visible(visible)

    # Получить видимость мыши:
    def get_mouse_visible(self) -> bool:
        return self.window._winvars_["mouse-visible"]

    # -------------------------------------------------- Клавиатура: ---------------------------------------------------

    # Получить нажатие клавиш клавиатуры:
    @staticmethod
    def get_key_pressed() -> KeyboardScancodes:
        return KeyboardScancodes(pygame.key.get_pressed())

    # Получить нажатие клавиши клавиатуры:
    def get_key_down(self) -> KeyboardScancodes:
        return KeyboardScancodes(self.window._winvars_["key-down"])

    # Получить отжатие клавиши клавиатуры:
    def get_key_up(self) -> KeyboardScancodes:
        return KeyboardScancodes(self.window._winvars_["key-up"])
