#
# imgui.py - Обёртка imgui_bundle (с собственным рендерером pygame на основе SDL2Renderer).
#


# Импортируем:
import os
import pygame
import imgui_bundle
from imgui_bundle import imgui
from imgui_bundle.python_backends.opengl_backend import ProgrammablePipelineRenderer
from typing import Dict
from .gl import *
from ..math import *


# Кастомный рендерер для imgui_bundle на основе SDL2Renderer:
class PygameRenderer(ProgrammablePipelineRenderer):
    key_map: Dict[int, imgui.Key]
    modifier_map: Dict[int, imgui.Key]
    MOUSE_WHEEL_OFFSET_SCALE = 0.5

    def __init__(self) -> None:
        super(PygameRenderer, self).__init__()
        self._gui_time = None
        self._map_keys()

    def _map_keys(self) -> None:
        self.key_map = {}
        key_map = self.key_map
        key_map[pygame.K_TAB] = imgui.Key.tab
        key_map[pygame.K_LEFT] = imgui.Key.left_arrow
        key_map[pygame.K_RIGHT] = imgui.Key.right_arrow
        key_map[pygame.K_UP] = imgui.Key.up_arrow
        key_map[pygame.K_DOWN] = imgui.Key.down_arrow
        key_map[pygame.K_PAGEUP] = imgui.Key.page_up
        key_map[pygame.K_PAGEDOWN] = imgui.Key.page_down
        key_map[pygame.K_HOME] = imgui.Key.home
        key_map[pygame.K_END] = imgui.Key.end
        key_map[pygame.K_INSERT] = imgui.Key.insert
        key_map[pygame.K_DELETE] = imgui.Key.delete
        key_map[pygame.K_BACKSPACE] = imgui.Key.backspace
        key_map[pygame.K_SPACE] = imgui.Key.space
        key_map[pygame.K_RETURN] = imgui.Key.enter
        key_map[pygame.K_ESCAPE] = imgui.Key.escape
        key_map[pygame.K_KP_ENTER] = imgui.Key.keypad_enter
        key_map[pygame.K_a] = imgui.Key.a
        key_map[pygame.K_c] = imgui.Key.c
        key_map[pygame.K_v] = imgui.Key.v
        key_map[pygame.K_x] = imgui.Key.x
        key_map[pygame.K_y] = imgui.Key.y
        key_map[pygame.K_z] = imgui.Key.z

        self.modifier_map = {}
        self.modifier_map[pygame.K_LCTRL] = imgui.Key.mod_ctrl
        self.modifier_map[pygame.K_RCTRL] = imgui.Key.mod_ctrl
        self.modifier_map[pygame.K_LSHIFT] = imgui.Key.mod_shift
        self.modifier_map[pygame.K_RSHIFT] = imgui.Key.mod_shift
        self.modifier_map[pygame.K_LALT] = imgui.Key.mod_alt
        self.modifier_map[pygame.K_RALT] = imgui.Key.mod_alt
        self.modifier_map[pygame.K_LSUPER] = imgui.Key.mod_super
        self.modifier_map[pygame.K_RSUPER] = imgui.Key.mod_super

    def process_event(self, event) -> bool:
        io = self.io

        if event.type == pygame.MOUSEMOTION:
            io.mouse_pos = event.pos
            return True
        if event.type == pygame.MOUSEWHEEL:
            io.add_mouse_wheel_event(event.x * self.MOUSE_WHEEL_OFFSET_SCALE, event.y * self.MOUSE_WHEEL_OFFSET_SCALE)
            return True

        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
            imgui_button = None
            if event.button == 1: imgui_button = 0  # Left mouse button
            elif event.button == 3: imgui_button = 1  # Right mouse button
            elif event.button == 2: imgui_button = 2  # Middle mouse button

            if imgui_button is not None:
                io.add_mouse_button_event(imgui_button, event.type == pygame.MOUSEBUTTONDOWN)
            return True

        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if event.key in self.key_map:
                imgui_key = self.key_map[event.key]
                down = event.type == pygame.KEYDOWN
                io.add_key_event(imgui_key, down)
            if event.key in self.modifier_map:
                imgui_key = self.modifier_map[event.key]
                io.add_key_event(imgui_key, event.type == pygame.KEYDOWN)
            return True

        if event.type == pygame.TEXTINPUT:
            for char in event.text: io.add_input_character(ord(char))
            return True

        if event.type == pygame.VIDEORESIZE:
            io.display_size = event.size
            return True

    def process_inputs(self) -> None:
        io = imgui.get_io()
        current_time = pygame.time.get_ticks() / 1000.0
        if self._gui_time: io.delta_time = current_time - self._gui_time
        else: io.delta_time = 1.0 / 60.0
        if io.delta_time <= 0.0: io.delta_time = 1.0 / 1000.0
        self._gui_time = current_time


# Класс интерфейса:
class ImGUI:
    # Инициализация:
    def __init__(self, window_size: vec2, ini_file_path: str, renderer: any = None) -> None:
        self.ini_file_path = ini_file_path if isinstance(ini_file_path, str) else ""
        self.impl = None
        self.io   = None

        # Ссылка на функцию, которая отрисовывает интерфейс:
        self.renderer = renderer

        # Инициализация интерфейса:
        imgui.create_context()
        self.impl = PygameRenderer()
        self.io   = imgui.get_io()

        # Настройка:
        self.io.config_flags |= imgui.ConfigFlags_.docking_enable  # Включаем docking.
        self.io.display_size = tuple(window_size.xy)
        self.load()  # Загружаем конфигурацию если есть.

    # Вызывайте, когда хотите отрисовать интерфейс:
    def render(self) -> "ImGUI":
        self.impl.process_inputs()  # Помогает быть независимым от FPS.
        imgui.new_frame()

        # Вызываем функцию отрисовки:
        if self.renderer is not None: self.renderer()

        # Завершаем отрисовку интерфейса:
        imgui.render()
        imgui.end_frame()
        self.impl.render(imgui.get_draw_data())
        return self

    # Нужен для указания события по типу ввода или изменения размера окна:
    def event(self, event) -> "ImGUI":
        self.impl.process_event(event)
        return self

    # Установить шрифт:
    def set_font(self, file_path: str, font_size: int = 14, smooth: bool = False) -> "ImGUI":
        # Если не передали шрифт, то устанавливаем шрифт по умолчанию:
        if file_path is None:
            self.io.fonts.clear()
            self.io.font_default = self.io.fonts.add_font_default()
            self.impl.refresh_font_texture()
            return self

        # Проверяем на наличие файла:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Устанавливаем шрифт:
        self.io.fonts.clear()
        self.io.font_default = self.io.fonts.add_font_from_file_ttf(file_path, int(font_size))
        self.impl.refresh_font_texture()

        # Устанавливаем сглаживание шрифта:
        if not smooth:
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.io.fonts.tex_id)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        return self

    # Загружаем настройки интерфейса:
    def load(self) -> "ImGUI":
        self.io.set_ini_filename(self.ini_file_path)
        imgui.load_ini_settings_from_disk(self.ini_file_path)
        return self

    # Сохранить весь интерфейс в ini файл:
    def save(self) -> "ImGUI":
        self.io.set_ini_filename(self.ini_file_path)
        imgui.save_ini_settings_to_disk(self.ini_file_path)
        return self

    # Вызывайте, при закрытии окна:
    def destroy(self, save_gui: bool = True) -> None:
        if save_gui: self.save()
        imgui.destroy_context()
