#
# imgui.py - Обёртка PyImGUI[pygame].
#


# Импортируем:
import pygame
import imgui
from imgui import *
from imgui.integrations.pygame import PygameRenderer
from ..math import *


# Класс интерфейса:
class ImGUI:
    # Инициализация:
    def __init__(self, window_size: vec2, ini_file_name: str, renderer: any = None) -> None:
        self.ini_file_name = ini_file_name
        self.impl = None
        self.io   = None

        # Ссылка на функцию, которая отрисовывает интерфейс:
        self.renderer = renderer

        # Инициализация интерфейса:
        imgui.create_context()
        self.impl             = PygameRenderer()
        self.io               = imgui.get_io()
        self.io.display_size  = window_size.xy
        self.io.ini_file_name = self.ini_file_name.encode()
        imgui.load_ini_settings_from_disk(self.ini_file_name)
        self.io.ini_file_name = None

    # Вызывайте, когда хотите отрисовать интерфейс:
    def render(self) -> "ImGUI":
        imgui.new_frame()

        # Вызываем функцию отрисовки:
        if self.renderer is not None:
            self.renderer()

        imgui.render()
        self.impl.render(imgui.get_draw_data())
        imgui.end_frame()
        return self

    # Нужен для указания события по типу ввода или изменения размера окна:
    def event(self, event) -> "ImGUI":
        if event.type == pygame.VIDEORESIZE: return self
        self.impl.process_event(event)
        return self

    # Принудительно изменить размер интерфейса при изменении размера окна:
    def resize(self, width: int, height: int) -> "ImGUI":
        self.io.display_size = (width, height)
        return self

    # Сохранить весь интерфейс в ini файл:
    def save_gui(self) -> "ImGUI":
        self.io.ini_file_name = self.ini_file_name.encode()
        imgui.save_ini_settings_to_disk(self.ini_file_name)
        return self

    # Вызывайте, при закрытии окна:
    def destroy(self, save_gui: bool = True) -> None:
        if save_gui: self.save_gui()
