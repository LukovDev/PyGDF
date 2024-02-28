#
# window.py - Создаёт класс окна (OpenGL).
#


# Импортируем:
if True:
    import gc
    import os
    import time
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    import pygame
    import numpy as np

    from .gl import *
    from .image import Image


# Класс окна:
class Window:
    # ------------------ Приведённые ниже функции должны быть записаны в унаследованном классе: ------------------------

    # Вызывается при создании окна:
    def start(self) -> None:
        pass

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, events: list) -> None:
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

    # Вызывается при закрытии окна:
    def destroy(self) -> None:
        pass

    # ------------------------------------------- Внутренние функции класса: -------------------------------------------

    # Вызывается при наследовании класса или создания его экземпляра:
    def __init__(self,
                 title:      str   = "OpenGL Window",
                 icon:       Image = None,
                 size:       tuple = (960, 540),
                 vsync:      bool  = False,
                 fps:        int   = 60,
                 visible:    bool  = True,
                 fullscreen: bool  = False,
                 min_size:   tuple = (0, 0),
                 max_size:   tuple = (float("inf"), float("inf")),
                 samples:    int   = 0,
                 gl_major:   int   = 3,
                 gl_minor:   int   = 3) -> None:
        self.clock = pygame.time.Clock()
        self.window = self
        self.__params__ = {
            "title": title,
            "icon": icon,
            "width": size[0],
            "height": size[1],
            "vsync": vsync,
            "visible": visible,
            "fullscreen": fullscreen,
            "settled-fps": fps,
            "window-active": False,
            "monitor-size": (),
            "mouse-scroll": [0.0, 0.0],
            "mouse-rel": [0, 0],
            "mouse-pressed": [False, False, None],
            "mouse-visible": True,
            "opengl-version": "",
            "delta-time": 1 / 60,
            "time": time.time(),
            "min-size": min_size,
            "max-size": max_size,
            "exiting": False,
            "samples": samples
        }

        pygame.init()
        self.__params__["monitor-size"] = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.set_title(self.__params__["title"])
        self.set_icon(self.__params__["icon"])

        # Создаём окно:
        if True:
            wins, fins = size, list(size)
            mins, maxs = min_size, max_size
            fins[0] = max(mins[0], min(maxs[0], wins[0]))
            fins[1] = max(mins[1], min(maxs[1], wins[1]))

            visible_flag = pygame.SHOWN if self.get_visible() else pygame.HIDDEN
            mode_flags = pygame.FULLSCREEN | visible_flag if self.get_fullscreen() else visible_flag
            self.__set_mode__(mode_flags, self.get_vsync(), fins)

            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, gl_major)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, gl_minor)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

        # Настройка OpenGL:
        if True:
            # Получаем версию OpenGL:
            self.__params__["opengl-version"] = gl.glGetString(gl.GL_VERSION).decode()

            # Включаем поддержку альфа канала:
            gl.glEnable(gl.GL_ALPHA_TEST)

            # Включаем смешивание цветов (например, для альфа канала):
            gl.glEnable(gl.GL_BLEND)
            
            # Позволяет смешивать цвета:
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

            # Включаем сглаживание точек чтобы вместо квадратов были круги:
            gl.glEnable(gl.GL_POINT_SMOOTH)

            # Разрешаем установку размера точки через шейдер:
            gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)

            # Делаем нулевой текстурный юнит привязанным к нулевой текстуре:
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

            # Включаем сглаживание линий:
            # gl.glEnable(gl.GL_LINE_SMOOTH)

            # # Включаем тест глубины:
            # gl.glEnable(gl.GL_DEPTH_TEST)

            # # Включаем отображение треугольников только с одной стороны:
            # gl.glEnable(gl.GL_CULL_FACE)

            # Настраиваем соотношение сторон:
            gl.glViewport(0, 0, self.get_size()[0], self.get_size()[1])
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            aspect_ratio = self.get_size()[0] / self.get_size()[1]
            glu.gluOrtho2D(-aspect_ratio, aspect_ratio, -1, 1)
            gl.glMatrixMode(gl.GL_MODELVIEW)

        self.start()

        # Основной цикл окна:
        while True:
            # Если хотят закрыть окно:
            if self.__params__["exiting"]:
                self.destroy()
                pygame.quit()
                gc.collect()
                return

            start_time = self.get_time()
            self.__params__["mouse-scroll"] = [0.0, 0.0]
            self.__params__["mouse-rel"] = pygame.mouse.get_rel()
            self.__params__["mouse-pressed"][1:] = [False, None]

            # Цикл, собирающий события:
            event_list = pygame.event.get()
            for event in event_list:
                # Если программу хотят закрыть:
                if event.type == pygame.QUIT: self.exit()

                # Проверка на то, изменился ли размер окна или нет:
                elif event.type == pygame.VIDEORESIZE:
                    window_size = list(event.dict["size"])
                    self.__params__["width"], self.__params__["height"] = window_size
                    if not self.__check_size__(*window_size): self.resize(*window_size)

                # Проверяем на то, развернуто окно или нет:
                elif event.type == pygame.ACTIVEEVENT:
                    if pygame.display.get_active() and not self.__params__["window-active"]:
                        self.__params__["window-active"] = True ; self.show()
                    elif not pygame.display.get_active() and self.__params__["window-active"]:
                        self.__params__["window-active"] = False ; self.hide()

                # Если колёсико мыши провернулось:
                elif event.type == pygame.MOUSEWHEEL: self.__params__["mouse-scroll"] = event.x, event.y

                # # Если отпускают клавишу:
                # elif event.type == pygame.KEYUP:
                #     # Если нажимают на F11:
                #     if event.key == pygame.K_F11:
                #         self.set_size(*self.get_monitor_size())
                #         self.set_fullscreen(not self.get_fullscreen())

                # Если нажимают любую кнопку мыши:
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.__params__["mouse-pressed"] = [True, False, event.button-1]

                # Если отпускают любую кнопку мыши
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.__params__["mouse-pressed"] = [False, True, event.button-1]

            # Вызываем функцию цикла:
            try: self.update(self.get_delta_time(), event_list)
            except KeyboardInterrupt: self.exit()

            # Обновляем дельту времени:
            self.__params__["delta-time"] = self.get_time() - start_time

    # Установить режим окна:
    def __set_mode__(self, flags: int, vsync: bool, size: tuple = None) -> None:
        self.set_samples(self.__params__["samples"])
        if size is None: size = (self.__params__["width"], self.__params__["height"])
        flags = pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE + flags
        pygame.display.set_mode(size, flags, vsync=vsync)

    # Проверяем размер окна на минимальный и максимальный размеры.
    # Возвращает логическое значение разницы конечного размера, и размера окна:
    def __check_size__(self, width: int, height: int) -> bool:
        wins, fins = (width, height), list((width, height))
        mins, maxs = self.get_min_size(), self.get_max_size()
        fins[0] = max(mins[0], min(maxs[0], wins[0]))
        fins[1] = max(mins[1], min(maxs[1], wins[1]))
        if fins != wins: self.set_size(*fins) ; return True
        return False

    # -------------------------------------------------- API окна: -----------------------------------------------------

    # Установить заголовок окна:
    def set_title(self, title: str) -> None:
        self.__params__["title"] = title
        pygame.display.set_caption(title)

    # Получить заголовок окна:
    def get_title(self) -> str:
        return self.__params__["title"]

    # Установить иконку окна:
    def set_icon(self, icon: Image) -> None:
        if icon is None: return
        self.__params__["icon"] = icon
        pygame.display.set_icon(icon.surface)

    # Получить иконку окна:
    def get_icon(self) -> Image:
        return self.__params__["icon"]

    # Установить размер окна:
    def set_size(self, width: int, height: int) -> None:
        self.__params__["width"] = width
        self.__params__["height"] = height
        if self.get_visible(): visible = pygame.SHOWN
        else: visible = pygame.HIDDEN
        if self.get_fullscreen(): self.__set_mode__(pygame.FULLSCREEN | visible, self.get_vsync())
        else: self.__set_mode__(visible, self.get_vsync())
        self.resize(width, height)

    # Получить размер окна:
    @staticmethod
    def get_size() -> tuple:
        return pygame.display.get_window_size()

    # Получить ширину окна:
    @staticmethod
    def get_width() -> int:
        return pygame.display.get_window_size()[0]

    # Получить высоту окна:
    @staticmethod
    def get_height() -> int:
        return pygame.display.get_window_size()[1]

    # Получить центр окна. Координаты половины размера окна:
    @staticmethod
    def get_center() -> tuple:
        size = pygame.display.get_window_size()
        return (size[0] // 2, size[1] // 2)

    # Получить соотношение сторон окна:
    @staticmethod
    def get_aspect_ratio() -> tuple:
        size = pygame.display.get_window_size()
        return size[0] / size[1], size[1] / size[0]

    # Установить минимальный размер окна:
    def set_min_size(self, width: int, height: int) -> None:
        self.__params__["min-size"] = width, height

    # Получить минимальный размер окна:
    def get_min_size(self) -> tuple:
        return self.__params__["min-size"]

    # Установить максимальный размер окна:
    def set_max_size(self, width: int, height: int) -> None:
        self.__params__["max-size"] = width, height

    # Получить максимальный размер окна:
    def get_max_size(self) -> tuple:
        return self.__params__["max-size"]

    # Получить размер монитора:
    def get_monitor_size(self) -> tuple:
        return self.__params__["monitor-size"]

    # Установить VSync:
    def set_vsync(self, vsync: bool) -> None:
        self.__params__["vsync"] = vsync
        visible_flag = pygame.SHOWN if self.get_visible() else pygame.HIDDEN
        mode_flags = pygame.FULLSCREEN | visible_flag if self.get_fullscreen() else visible_flag
        self.__set_mode__(mode_flags, vsync)

    # Получить VSync:
    def get_vsync(self) -> bool:
        return self.__params__["vsync"]

    # Установить FPS:
    def set_fps(self, fps: int) -> None:
        self.__params__["settled-fps"] = fps

    # Получить текущий FPS:
    def get_fps(self) -> float:
        return 1 / self.get_delta_time()

    # Получить установленный FPS:
    def get_settled_fps(self) -> int:
        return self.__params__["settled-fps"]

    # Показать окно:
    def show_window(self) -> None:
        self.__params__["visible"] = True
        visible_flag = pygame.SHOWN
        mode_flags = pygame.FULLSCREEN | visible_flag if self.get_fullscreen() else visible_flag
        self.__set_mode__(mode_flags, self.get_vsync())
        self.show()

    # Спрятать окно:
    def hide_window(self) -> None:
        self.__params__["visible"] = False
        visible_flag = pygame.HIDDEN
        mode_flags = pygame.FULLSCREEN | visible_flag if self.get_fullscreen() else visible_flag
        self.__set_mode__(mode_flags, self.get_vsync())
        self.hide()

    # Установить видимость окна:
    def set_visible(self, visible: bool) -> None:
        self.__params__["visible"] = visible
        if visible: self.show_window()
        else: self.hide_window()

    # Получить видимость окна:
    def get_visible(self) -> bool:
        return self.__params__["visible"]

    # Установить полноэкранный режим:
    def set_fullscreen(self, is_fullscreen: bool, size: tuple = None) -> None:
        self.__params__["fullscreen"] = is_fullscreen
        visible_flag = pygame.SHOWN if self.get_visible() else pygame.HIDDEN
        mode_flags = pygame.FULLSCREEN | visible_flag if is_fullscreen else visible_flag
        size = size if size is not None else (0, 0)
        self.__set_mode__(mode_flags, self.get_vsync(), size)
        self.resize(*self.get_size())

    # Получить полноэкранный режим:
    def get_fullscreen(self) -> bool:
        return self.__params__["fullscreen"]

    # Установить количество сэмплов антиалиазинга:
    def set_samples(self, samples: int) -> None:
        if not 0 <= samples <= 16:  # Если samples не в диапазоне от 0 до 16:
            raise Exception(f"Graphics Error: Samples must be set in the range from 0 to 16. You have set: {samples}")
        self.__params__["samples"] = samples
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, self.__params__["samples"])

    # Получить количество сэмплов антиалиазинга:
    def get_samples(self) -> None:
        return self.__params__["samples"]

    # Установить конфигурацию окна:
    def set_config(self, title: str, icon: Image, size: list | tuple,
                   vsync: bool, fps: int, visible: bool, min_size: tuple = (0, 0),
                   max_size: tuple = (float("inf"), float("inf")), samples: int = 0) -> None:
        self.set_title(title)
        self.set_icon(icon)
        self.set_size(*size)
        self.set_vsync(vsync)
        self.set_fps(fps)
        self.set_visible(visible)
        self.set_min_size(*min_size)
        self.set_max_size(*max_size)
        self.set_samples(samples)

    # Получить конфигурацию окна:
    def get_config(self) -> list:
        return [
            self.get_title(), self.get_icon(), self.get_size(),
            self.get_vsync(), self.get_fps(), self.get_visible(),
            self.get_min_size(), self.get_max_size(), self.get_samples()
        ]

    # Получить дельту времени:
    def get_delta_time(self) -> float:
        return self.__params__["delta-time"]

    # Получить время:
    def get_time(self) -> float:
        return time.time() - self.__params__["time"]

    # Установить позицию мыши:
    @staticmethod
    def set_mouse_pos(pos: tuple | list) -> None:
        pygame.mouse.set_pos(pos[0], pos[1])

    # Получить позицию мыши:
    @staticmethod
    def get_mouse_pos() -> tuple:
        return pygame.mouse.get_pos()

    # Получить смещение мыши за кадр:
    def get_mouse_rel(self) -> tuple:
        return self.__params__["mouse-rel"]

    # Получить нажатие клавиш мыши:
    @staticmethod
    def get_mouse_pressed() -> list:
        return list(pygame.mouse.get_pressed())

    # Получить нажатие кнопки мыши:
    def get_mouse_button_down(self, button: int = None) -> bool:
        a = self.__params__["mouse-pressed"][0]
        b = self.get_mouse_pressed()
        if button is not None and b is not None: return a and b[button]
        return a

    # Получить отжатие кнопки мыши:
    def get_mouse_button_up(self, button: int = None) -> bool:
        a = self.__params__["mouse-pressed"][1]
        b = self.__params__["mouse-pressed"][2]
        if button is not None and b is not None: return a and button == b
        return a

    # Получить вращение мыши:
    def get_mouse_scroll(self) -> tuple:
        return tuple(self.__params__["mouse-scroll"])

    # Установить видимость курсора мыши:
    def set_mouse_visible(self, visible: bool) -> None:
        self.__params__["mouse-visible"] = visible
        pygame.mouse.set_visible(visible)

    # Получить видимость курсора мыши:
    def get_mouse_visible(self) -> bool:
        return self.__params__["mouse-visible"]

    # Получить нажатие клавиш клавиатуры:
    @staticmethod
    def get_key_pressed() -> pygame.key.ScancodeWrapper:
        return pygame.key.get_pressed()
    
    # Получить версию OpenGL:
    def get_opengl_version(self) -> str:
        return self.__params__["opengl-version"]

    # Получить кадр как изображение:
    def get_frame_image(self, front: bool = False) -> Image:
        # Всего есть 2 буфера. Отображаемый на экране и тот что в процессе рисовки:
        if front: gl.glReadBuffer(gl.GL_FRONT)  # Передний (отображаемый) буфер.
        else:     gl.glReadBuffer(gl.GL_BACK)   # Задний (в процессе рисовки) буфер.
        w, h = s = self.get_size()
        p = np.frombuffer(gl.glReadPixels(0, 0, *s, gl.GL_RGB, gl.GL_UNSIGNED_BYTE), dtype=np.uint8).reshape((h, w, 3))
        return Image(surface=pygame.surfarray.make_surface(np.rot90(p, k=-1, axes=(0, 1))))

    # Вызовите, когда хотите закрыть окно:
    def exit(self) -> None:
        self.__params__["exiting"] = True

    # Очистка окна (цвета от 0 до 1):
    @staticmethod
    def clear(red: float = 0, green: float = 0, blue: float = 0) -> None:
        gl.glClearColor(abs(red), abs(green), abs(blue), 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    # Очистка окна (цвета от 0 до 255):
    def clear255(self, red: int = 0, green: int = 0, blue: int = 0) -> None:
        self.clear(red=(red % 256)/255, green=(green % 256)/255, blue=(blue % 256)/255)

    # Отрисовка окна:
    def display(self) -> None:
        pygame.display.flip()
        if not self.__params__["vsync"]: self.clock.tick(self.__params__["settled-fps"])
        else: self.clock.tick(0)
