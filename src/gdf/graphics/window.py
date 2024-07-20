#
# window.py - Создаёт класс окна (OpenGL).
#


# Импортируем:
if True:
    import gc
    import time
    import pygame

    from .gl import *
    from .image import Image
    from .scene import Scene
    from . import OpenGLWindowError, OpenGLContextNotSupportedError

    from ..audio.al import *

    from ..math import vec2, numpy as np


# Класс окна:
class Window:
    # --------------------- Приведённые ниже функции должны быть записаны в унаследованном классе: ---------------------

    # Создать окно:
    def init(self) -> None:
        pass

    # Вызывается при создании окна:
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

    # Вызывается при закрытии окна:
    def destroy(self) -> None:
        pass

    # ------------------------------------------- Внутренние функции класса: -------------------------------------------

    # Вызывается при наследовании класса или создания его экземпляра:
    def __init__(self,
                 title:      str   = "OpenGL Window",
                 icon:       Image = None,
                 size:       vec2  = vec2(960, 540),
                 vsync:      bool  = False,
                 fps:        int   = 60,
                 visible:    bool  = True,
                 titlebar:   bool  = True,
                 fullscreen: bool  = False,
                 min_size:   vec2  = vec2(0, 0),
                 max_size:   vec2  = vec2(float("inf"), float("inf")),
                 samples:    int   = 0,
                 gl_major:   int   = None,
                 gl_minor:   int   = None) -> None:
        self.clock = pygame.time.Clock()
        self.window = self
        self.__winvars__ = {
            # Основные переменные:
            "title":      str(title),
            "icon":       icon,
            "width":      int(min(max(size.x, min_size.x), max_size.x)),
            "height":     int(min(max(size.y, min_size.y), max_size.y)),
            "vsync":      bool(vsync),
            "setted-fps": int(fps),
            "visible":    bool(visible),
            "titlebar":   bool(titlebar),
            "fullscreen": bool(fullscreen),
            "min-size":   vec2(min_size),
            "max-size":   vec2(max_size),
            "samples":    int(samples),

            # Внутренние переменные (ИСПОЛЬЗУЮТСЯ ТОЛЬКО ВНУТРИ КЛАССА):
            "window-active":  False,
            "monitor-size":   vec2(0),
            "win-size-bf-fs": [int(size.x), int(size.y)],
            "mouse-rel":      vec2(0),
            "mouse-down":     [False, False, False],
            "mouse-up":       [False, False, False],
            "mouse-scroll":   vec2(0),
            "mouse-visible":  True,
            "key-down":       [],
            "key-up":         [],
            "dtime":          1/60,
            "old-dtime":      1/60,
            "is-exit":        False,
            "start-time":     0.0,
            "current-scene":  None,
            "is-new-scene":   False,
        }

        # Создание окна:
        try:
            pygame.init()
            self.__winvars__["monitor-size"].xy = vec2(pygame.display.Info().current_w, pygame.display.Info().current_h)
            self.set_title(self.__winvars__["title"])
            self.set_icon(self.__winvars__["icon"])

            # Устанавливаем версию OpenGL:
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, gl_major) if gl_major is not None else None
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, gl_minor) if gl_minor is not None else None

            # Мы используем контекст OpenGL с обратной совместимостью чтобы можно было использовать устаревшие функции:
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_COMPATIBILITY)

            # Устанавливаем мультисемплинг:
            self.set_samples(self.__winvars__["samples"])

            # Создаём окно:
            self.__recreate__((self.__winvars__["width"], self.__winvars__["height"]))
        except pygame.error:
            raise OpenGLContextNotSupportedError(f"OpenGL version {gl_major}.{gl_minor} is not supported.")
        except Exception as error:
            raise OpenGLWindowError(f"Error creating the window: {error}")
        finally:
            # Удаляем лишние переменные, чтобы те больше не мешались в логике окна:
            del title, icon, size, vsync, fps, visible, fullscreen, min_size, max_size, samples, gl_major, gl_minor
            gc.collect()

        # Настройка OpenGL:
        if True:
            # Включаем смешивание цветов:
            gl.glEnable(gl.GL_BLEND)
            
            # Устанавливаем режим смешивания:
            gl_set_blend_mode()

            # Разрешаем установку размера точки через шейдер:
            gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)

            # Делаем нулевой текстурный юнит привязанным к нулевой текстуре:
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

            # Настраиваем соотношение сторон:
            self.__reset_viewport__()

        # Инициализируем OpenAL:
        al.oalInit()

        # Инициализация времени программы:
        self.__winvars__["start-time"] = time.time()

        # Вызываем старт программы:
        try: self.start()
        except KeyboardInterrupt: self.exit()

        # Основной цикл окна:
        while True:
            start_frame_time                 = time.time()
            self.__winvars__["mouse-scroll"] = vec2(0)
            self.__winvars__["mouse-rel"]    = vec2(pygame.mouse.get_rel())
            self.__winvars__["mouse-down"]   = [False, False, False]
            self.__winvars__["mouse-up"]     = [False, False, False]
            self.__winvars__["key-down"]     = []
            self.__winvars__["key-up"]       = []
            scn                              = self.__winvars__["current-scene"]

            # Если хотят закрыть окно:
            if self.__winvars__["is-exit"]:
                # Вызываем функцию удаления ресурсов у сцены, если та существует:
                if scn is not None and issubclass(type(scn), Scene): scn.destroy()
                self.destroy()  # Вызываем удаление пользовательских ресурсов.
                al.oalQuit()    # Закрываем OpenAL.
                pygame.quit()   # Закрываем окно PyGame.
                gc.collect()    # Собираем мусор (на всякий случай).
                return          # Возвращаемся из этого класса.

            # Проверяем установлена ли новая сцена. Если да, то сбрасываем окно просмотра:
            if self.__winvars__["is-new-scene"]: self.__winvars__["is-new-scene"] = False ; self.__reset_viewport__()

            # Обработка событий под капотом:
            event_list = pygame.event.get()
            for event in event_list:
                # Если программу хотят закрыть:
                if event.type == pygame.QUIT: self.exit()

                # Проверка на то, изменился ли размер окна или нет:
                elif event.type == pygame.VIDEORESIZE:
                    wsize = list(event.dict["size"])
                    min_size = self.__winvars__["min-size"]
                    max_size = self.__winvars__["max-size"]

                    # Проверяем, вышел ли размер окна за пределы допущенного. Если да, то выставляем крайний размер:
                    if not (min_size.x <= wsize[0] <= max_size.x and min_size.y <= wsize[1] <= max_size.y):
                        wsize[0] = min(max(int(wsize[0]), int(min_size.x)), int(max_size.x))
                        wsize[1] = min(max(int(wsize[1]), int(min_size.y)), int(max_size.y))
                        wsize = int(wsize[0]), int(wsize[1])
                        self.set_size(*wsize)
                    else:  # Иначе, просто вызываем функцию изменения размера:
                        wsize = int(wsize[0]), int(wsize[1])
                        scn.resize(*wsize) if scn is not None and issubclass(type(scn), Scene) else self.resize(*wsize)

                    # Обновляем размер окна в переменных окна:
                    self.__winvars__["width"], self.__winvars__["height"] = wsize

                # Проверяем на то, развернуто окно или нет:
                elif event.type == pygame.ACTIVEEVENT:
                    if pygame.display.get_active() and not self.__winvars__["window-active"]:
                        self.__winvars__["window-active"] = True
                        scn.show() if scn is not None and issubclass(type(scn), Scene) else self.show()
                    elif not pygame.display.get_active() and self.__winvars__["window-active"]:
                        self.__winvars__["window-active"] = False
                        scn.hide() if scn is not None and issubclass(type(scn), Scene) else self.hide()

                # Если колёсико мыши провернулось:
                elif event.type == pygame.MOUSEWHEEL: self.__winvars__["mouse-scroll"] = vec2(event.x, event.y)

                # Если нажимают кнопку мыши:
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.__winvars__["mouse-down"] = [event.button-1 == 0, event.button-1 == 1, event.button-1 == 2]

                # Если отпускают кнопку мыши:
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.__winvars__["mouse-up"] = [event.button-1 == 0, event.button-1 == 1, event.button-1 == 2]

                # Если нажимают кнопку на клавиатуре:
                elif event.type == pygame.KEYDOWN:
                    self.__winvars__["key-down"].append(event.key)

                # Если отпускают кнопку на клавиатуре:
                elif event.type == pygame.KEYUP:
                    self.__winvars__["key-up"].append(event.key)

            # Обработка основных функций (обновление и отрисовка):
            try:
                # Если у нас установлена сцена:
                if scn is not None and issubclass(type(scn), Scene):
                    scn.update(self.__winvars__["dtime"], event_list)
                    scn.render(self.__winvars__["dtime"])

                # Если сцены нет, используем встроенные функции:
                else:
                    self.update(self.__winvars__["dtime"], event_list)
                    self.render(self.__winvars__["dtime"])
            except KeyboardInterrupt: self.exit()

            # Делаем задержку между кадрами:
            self.clock.tick(self.__winvars__["setted-fps"]) if not self.__winvars__["vsync"] else self.clock.tick(0)

            # Получаем дельту времени (время кадра или же время обработки одного цикла окна):
            dt = time.time() - start_frame_time
            if dt > 0.0: self.__winvars__["old-dtime"] = self.__winvars__["dtime"] = dt
            else: self.__winvars__["dtime"] = self.__winvars__["old-dtime"]  # Использовать DT прошлого кадра.

    # Пересоздать окно (обновить режим окна):
    def __recreate__(self, size: tuple | vec2 = None, flags: int = None) -> None:
        if size is None: size = (self.__winvars__["width"], self.__winvars__["height"])
        flags = pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        flags |= pygame.SHOWN if self.get_visible() else pygame.HIDDEN
        if self.get_fullscreen():   flags |= pygame.FULLSCREEN
        if not self.get_titlebar(): flags |= pygame.NOFRAME
        pygame.display.set_mode(size, flags, vsync=self.get_vsync())

    # Сбрасываем окно просмотра:
    def __reset_viewport__(self) -> None:
        gl.glViewport(0, 0, self.__winvars__["width"], self.__winvars__["height"])
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        wdth, hght = self.__winvars__["width"]/2, self.__winvars__["height"]/2
        glu.gluOrtho2D(-wdth, wdth, -hght, hght)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

    # ------------------------------------------------------ API: ------------------------------------------------------

    # Установить заголовок окна:
    def set_title(self, title: str) -> None:
        self.__winvars__["title"] = title
        pygame.display.set_caption(title)

    # Получить заголовок окна:
    def get_title(self) -> str:
        return self.__winvars__["title"]

    # Установить иконку окна:
    def set_icon(self, icon: Image) -> None:
        if icon is not None and not isinstance(icon, Image):
            raise OpenGLWindowError(
                f"Type Class error: You have specified a data type that is not "
                f"equal to the \"{Image}\" type (your type: \"{type(icon)}\").")

        # Создаём и устанавливаем прозрачную иконку только в том случае, если мы передали None:
        self.__winvars__["icon"] = icon
        pygame.display.set_icon(Image((64, 64)).fill([0, 0, 0, 0]).surface if icon is None else icon.surface)

    # Получить иконку окна:
    def get_icon(self) -> Image:
        return self.__winvars__["icon"]

    # Установить размер окна:
    def set_size(self, width: int, height: int) -> None:
        self.__winvars__["width"] = int(width)
        self.__winvars__["height"] = int(height)
        self.__recreate__()
        self.resize(int(width), int(height))

    # Получить размер окна:
    @staticmethod
    def get_size() -> vec2:
        return vec2(pygame.display.get_window_size())

    # Установить VSync:
    def set_vsync(self, vsync: bool) -> None:
        self.__winvars__["vsync"] = vsync
        self.__recreate__()

    # Получить VSync:
    def get_vsync(self) -> bool:
        return self.__winvars__["vsync"]

    # Установить FPS:
    def set_fps(self, fps: int) -> None:
        self.__winvars__["setted-fps"] = int(fps)

    # Получить текущий FPS:
    def get_fps(self) -> float:
        return 1.0 / self.__winvars__["dtime"]

    # Установить видимость окна:
    def set_visible(self, visible: bool) -> None:
        self.__winvars__["visible"] = visible
        self.__recreate__()
        if visible: self.show()
        else:       self.hide()

    # Получить видимость окна:
    def get_visible(self) -> bool:
        return self.__winvars__["visible"]

    # Установить видимость заголовка окна:
    def set_titlebar(self, titlebar: bool) -> None:
        self.__winvars__["titlebar"] = titlebar
        self.__recreate__()

    # Получить видимость заголовка окна:
    def get_titlebar(self) -> bool:
        return self.__winvars__["titlebar"]

    # Установить полноэкранный режим:
    def set_fullscreen(self, is_fullscreen: bool, size: tuple | vec2 = None) -> None:
        self.__winvars__["fullscreen"] = is_fullscreen
        self.set_size(*size if size is not None else self.get_monitor_size())

    # Получить полноэкранный режим:
    def get_fullscreen(self) -> bool:
        return self.__winvars__["fullscreen"]

    # Установить минимальный размер окна:
    def set_min_size(self, width: int, height: int) -> None:
        self.__winvars__["min-size"] = vec2(int(width), int(height))

    # Получить минимальный размер окна:
    def get_min_size(self) -> vec2:
        return vec2(self.__winvars__["min-size"])

    # Установить максимальный размер окна:
    def set_max_size(self, width: int, height: int) -> None:
        self.__winvars__["max-size"] = vec2(int(width), int(height))

    # Получить максимальный размер окна:
    def get_max_size(self) -> vec2:
        return vec2(self.__winvars__["max-size"])

    # Установить количество сэмплов антиалиазинга:
    def set_samples(self, samples: int) -> None:
        if not 0 <= samples <= 16:  # Если samples не в диапазоне от 0 до 16:
            raise OpenGLWindowError(
                f"Graphics Error: Samples must be set in the range from 0 to 16. You have set: {samples}")
        self.__winvars__["samples"] = samples
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, self.__winvars__["samples"])
        self.__recreate__()

    # Получить количество сэмплов антиалиазинга:
    def get_samples(self) -> None:
        return self.__winvars__["samples"]

    # Установить конфигурацию окна:
    def set_config(self, title: str, icon: Image, size: vec2, vsync: bool, fps: int,
                   visible: bool, min_size: vec2 = vec2(0), max_size: vec2 = vec2(float("inf"),
                   float("inf")), samples: int = 0) -> None:
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

    # Установить игровую сцену:
    def set_scene(self, scene: Scene) -> None:
        # Если устанавливаемая сцена не сцена:
        if scene is not None and not issubclass(type(scene), Scene):
            raise OpenGLWindowError(
                f"The specified scene is not a scene. Your scene has a \"{type(scene)}\" "
                f"data type, which is not a \"{Scene}\" data type."
            )

        # Если уже установленная сцена существует:
        current_scene = self.__winvars__["current-scene"]
        if current_scene is not None and issubclass(type(current_scene), Scene):
            current_scene.destroy()

        # Устанавливаем сцену:
        self.__winvars__["current-scene"] = scene

        # Сбрасываем окно просмотра:
        self.__winvars__["is-new-scene"] = True

        # Если мы установили сцену в виде None, то просто возвращаемся:
        if scene is None: return

        # Указываем ссылку на основное окно:
        self.__winvars__["current-scene"].window = self

        # Вызываем старт сцены:
        try: self.__winvars__["current-scene"].start()
        except KeyboardInterrupt: self.exit()

    # Получить текущую игровую сцену:
    def get_scene(self) -> Scene | None:
        return self.__winvars__["current-scene"]

    # Получить размер монитора:
    def get_monitor_size(self) -> vec2:
        return vec2(self.__winvars__["monitor-size"])

    # Получить ширину окна:
    def get_width(self) -> int:
        return int(self.__winvars__["width"])

    # Получить высоту окна:
    def get_height(self) -> int:
        return int(self.__winvars__["height"])

    # Получить центр окна. Координаты половины размера окна:
    def get_center(self) -> vec2:
        size = self.get_size()
        return vec2(size.x // 2, size.y // 2)

    # Получить установленный FPS:
    def get_setted_fps(self) -> int:
        return self.__winvars__["setted-fps"]

    # Получить дельту времени:
    def get_delta_time(self) -> float:
        return self.__winvars__["dtime"]

    # Получить время:
    def get_time(self) -> float:
        return time.time() - self.__winvars__["start-time"]

    # Получить версию OpenGL:
    def get_opengl_version(self) -> str:
        return gl.glGetString(gl.GL_VERSION).decode("utf-8")

    # Получить рендерер OpenGL:
    def get_opengl_renderer(self) -> str:
        return gl.glGetString(gl.GL_RENDERER).decode("utf-8")

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
        self.__winvars__["is-exit"] = True

    # Очистка окна (цвета от 0 до 1):
    @staticmethod
    def clear(red: float = 0, green: float = 0, blue: float = 0) -> None:
        gl.glClearColor(abs(red), abs(green), abs(blue), 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    # Отрисовка окна:
    def display(self) -> None:
        pygame.display.flip()  # Меняем буферы кадра местами.
