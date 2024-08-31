#
# window.py - Создаёт класс окна в контексте OpenGL.
#


# Импортируем:
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
                 resizable:  bool  = True,
                 fullscreen: bool  = False,
                 min_size:   vec2  = vec2(0, 0),
                 max_size:   vec2  = vec2(float("inf"), float("inf")),
                 samples:    int   = 0,
                 gl_major:   int   = None,
                 gl_minor:   int   = None) -> None:
        self.clock = pygame.time.Clock()
        self.window = self
        self._winvars_ = {
            # Основные переменные:
            "title":      str(title),
            "icon":       icon,
            "width":      int(min(max(size.x, min_size.x), max_size.x)),
            "height":     int(min(max(size.y, min_size.y), max_size.y)),
            "vsync":      bool(vsync),
            "setted-fps": int(fps),
            "visible":    bool(visible),
            "titlebar":   bool(titlebar),
            "resizable":  bool(resizable),
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
            self._winvars_["monitor-size"].xy = vec2(pygame.display.Info().current_w, pygame.display.Info().current_h)
            self.set_title(self._winvars_["title"])
            self.set_icon(self._winvars_["icon"])

            # Устанавливаем версию OpenGL:
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, gl_major) if gl_major is not None else None
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, gl_minor) if gl_minor is not None else None

            # Мы используем контекст OpenGL с обратной совместимостью чтобы можно было использовать устаревшие функции:
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_COMPATIBILITY)

            # Устанавливаем мультисемплинг:
            self.set_samples(self._winvars_["samples"])

            # Создаём окно:
            self._recreate_((self._winvars_["width"], self._winvars_["height"]))
        except pygame.error:
            raise OpenGLContextNotSupportedError(f"OpenGL version {gl_major}.{gl_minor} is not supported.")
        except Exception as error:
            raise OpenGLWindowError(f"Error creating the window: {error}")

        # Включаем смешивание цветов:
        gl.glEnable(gl.GL_BLEND)
        
        # Устанавливаем режим смешивания:
        gl_set_blend_mode()  # ЭТО ФУНКЦИЯ НЕ ИЗ БИБЛИОТЕКИ OpenGL, А ИЗ ФАЙЛА gl.py!

        # Разрешаем установку размера точки через шейдер:
        gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)

        # Делаем нулевой текстурный юнит привязанным к нулевой текстуре:
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # Настраиваем соотношение сторон:
        self._reset_viewport_()

        # Инициализируем OpenAL:
        al.oalInit()

        # Инициализация времени программы:
        self._winvars_["start-time"] = time.time()

        # Вызываем старт программы:
        try:
            self.start()
        except KeyboardInterrupt: self.exit()

        # Основной цикл окна:
        while True:
            start_frame_time               = time.time()
            self._winvars_["mouse-scroll"] = vec2(0)
            self._winvars_["mouse-rel"]    = vec2(pygame.mouse.get_rel())
            self._winvars_["mouse-down"]   = [False, False, False]
            self._winvars_["mouse-up"]     = [False, False, False]
            self._winvars_["key-down"]     = []
            self._winvars_["key-up"]       = []
            scn                            = self._winvars_["current-scene"]

            # Проверяем установлена ли новая сцена. Если да, то сбрасываем окно просмотра:
            if self._winvars_["is-new-scene"]: self._winvars_["is-new-scene"] = False ; self._reset_viewport_()

            # Обработка событий под капотом:
            event_list = pygame.event.get()
            for event in event_list:
                # Если программу хотят закрыть:
                if event.type == pygame.QUIT: self.exit()

                # Проверка на то, изменился ли размер окна или нет:
                elif event.type == pygame.VIDEORESIZE:
                    wsize = list(event.dict["size"])
                    min_size = self._winvars_["min-size"]
                    max_size = self._winvars_["max-size"]

                    # Проверяем, вышел ли размер окна за пределы допущенного. Если да, то выставляем крайний размер:
                    if not (min_size.x <= wsize[0] <= max_size.x and min_size.y <= wsize[1] <= max_size.y):
                        wsize[0] = min(max(wsize[0], min_size.x), max_size.x)
                        wsize[1] = min(max(wsize[1], min_size.y), max_size.y)
                        wsize = int(wsize[0]), int(wsize[1])
                        self.set_size(*wsize)
                    else:  # Иначе, просто вызываем функцию изменения размера:
                        wsize = int(wsize[0]), int(wsize[1])
                        scn.resize(*wsize) if scn is not None and issubclass(type(scn), Scene) else self.resize(*wsize)

                    # Обновляем размер окна в переменных окна:
                    self._winvars_["width"], self._winvars_["height"] = wsize

                # Проверяем на то, развернуто окно или нет:
                elif event.type == pygame.ACTIVEEVENT:
                    if pygame.display.get_active() and not self._winvars_["window-active"]:
                        self._winvars_["window-active"] = True
                        scn.show() if scn is not None and issubclass(type(scn), Scene) else self.show()
                    elif not pygame.display.get_active() and self._winvars_["window-active"]:
                        self._winvars_["window-active"] = False
                        scn.hide() if scn is not None and issubclass(type(scn), Scene) else self.hide()

                # Если колёсико мыши провернулось:
                elif event.type == pygame.MOUSEWHEEL: self._winvars_["mouse-scroll"] = vec2(event.x, event.y)

                # Если нажимают кнопку мыши:
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._winvars_["mouse-down"] = [event.button-1 == 0, event.button-1 == 1, event.button-1 == 2]

                # Если отпускают кнопку мыши:
                elif event.type == pygame.MOUSEBUTTONUP:
                    self._winvars_["mouse-up"] = [event.button-1 == 0, event.button-1 == 1, event.button-1 == 2]

                # Если нажимают кнопку на клавиатуре:
                elif event.type == pygame.KEYDOWN:
                    self._winvars_["key-down"].append(event.key)

                # Если отпускают кнопку на клавиатуре:
                elif event.type == pygame.KEYUP:
                    self._winvars_["key-up"].append(event.key)

            # Обработка основных функций (обновление и отрисовка):
            try:
                # Если у нас установлена сцена:
                if scn is not None and issubclass(type(scn), Scene):
                    scn.update(self._winvars_["dtime"], event_list)
                    if not self._winvars_["is-exit"]: scn.render(self._winvars_["dtime"])

                # Если сцены нет, используем встроенные функции:
                else:
                    self.update(self._winvars_["dtime"], event_list)
                    if not self._winvars_["is-exit"]: self.render(self._winvars_["dtime"])
            except KeyboardInterrupt: self.exit()

            # Если хотят закрыть окно:
            if self._winvars_["is-exit"]:
                # Вызываем функцию удаления ресурсов у сцены, если та существует:
                if scn is not None and issubclass(type(scn), Scene): scn.destroy()
                self.destroy()  # Вызываем удаление пользовательских ресурсов.
                al.oalQuit()    # Закрываем OpenAL.
                pygame.quit()   # Закрываем окно PyGame.
                gc.collect()    # Собираем мусор (на всякий случай).
                return          # Возвращаемся из этого класса.

            # Делаем задержку между кадрами:
            self.clock.tick(self._winvars_["setted-fps"]) if not self._winvars_["vsync"] else self.clock.tick(0)

            # Получаем дельту времени (время кадра или же время обработки одного цикла окна):
            dt = time.time() - start_frame_time
            if dt > 0.0: self._winvars_["old-dtime"] = self._winvars_["dtime"] = dt
            else: self._winvars_["dtime"] = self._winvars_["old-dtime"]  # Использовать DT прошлого кадра.

    # Пересоздать окно (обновить режим окна):
    def _recreate_(self, size: tuple | vec2 = None, flags: int = None) -> None:
        if size is None: size = (self._winvars_["width"], self._winvars_["height"])
        flags = pygame.DOUBLEBUF | pygame.OPENGL
        flags |= pygame.SHOWN if self.get_visible() else pygame.HIDDEN
        if self.get_resizable():    flags |= pygame.RESIZABLE
        if self.get_fullscreen():   flags |= pygame.FULLSCREEN
        if not self.get_titlebar(): flags |= pygame.NOFRAME
        pygame.display.set_mode(size, flags, vsync=self.get_vsync())

    # Сбрасываем окно просмотра:
    def _reset_viewport_(self) -> None:
        gl.glViewport(0, 0, self._winvars_["width"], self._winvars_["height"])
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        wdth, hght = self._winvars_["width"]/2, self._winvars_["height"]/2
        glu.gluOrtho2D(-wdth, wdth, -hght, hght)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

    # ------------------------------------------------------ API: ------------------------------------------------------

    # Установить заголовок окна:
    def set_title(self, title: str) -> None:
        self._winvars_["title"] = title
        pygame.display.set_caption(title)

    # Получить заголовок окна:
    def get_title(self) -> str:
        return self._winvars_["title"]

    # Установить иконку окна:
    def set_icon(self, icon: Image) -> None:
        if icon is not None and not isinstance(icon, Image):
            raise OpenGLWindowError(
                f"Type Class error: You have specified a data type that is not "
                f"equal to the \"{Image}\" type (your type: \"{type(icon)}\").")

        # Создаём и устанавливаем прозрачную иконку только в том случае, если мы передали None:
        self._winvars_["icon"] = icon
        pygame.display.set_icon(Image((64, 64)).fill([0, 0, 0, 0]).surface if icon is None else icon.surface)

    # Получить иконку окна:
    def get_icon(self) -> Image:
        return self._winvars_["icon"]

    # Установить размер окна:
    def set_size(self, width: int, height: int) -> None:
        self._winvars_["width"] = int(width)
        self._winvars_["height"] = int(height)
        self._recreate_()
        self.resize(int(width), int(height))

    # Получить размер окна:
    @staticmethod
    def get_size() -> vec2:
        return vec2(pygame.display.get_window_size())

    # Установить VSync:
    def set_vsync(self, vsync: bool) -> None:
        self._winvars_["vsync"] = vsync
        self._recreate_()

    # Получить VSync:
    def get_vsync(self) -> bool:
        return self._winvars_["vsync"]

    # Установить FPS:
    def set_fps(self, fps: int) -> None:
        self._winvars_["setted-fps"] = int(fps)

    # Получить текущий FPS:
    def get_fps(self) -> float:
        return 1.0 / self._winvars_["dtime"]

    # Установить видимость окна:
    def set_visible(self, visible: bool) -> None:
        self._winvars_["visible"] = visible
        self._recreate_()
        if visible: self.show()
        else:       self.hide()

    # Получить видимость окна:
    def get_visible(self) -> bool:
        return self._winvars_["visible"]

    # Установить видимость заголовка окна:
    def set_titlebar(self, titlebar: bool) -> None:
        self._winvars_["titlebar"] = titlebar
        self._recreate_()

    # Получить видимость заголовка окна:
    def get_titlebar(self) -> bool:
        return self._winvars_["titlebar"]

    # Установить масштабируемость окна:
    def set_resizable(self, resizable: bool) -> None:
        self._winvars_["resizable"] = resizable
        self._recreate_()

    # Получить масштабируемость окна:
    def get_resizable(self) -> bool:
        return self._winvars_["resizable"]

    # Установить полноэкранный режим:
    def set_fullscreen(self, fullscreen: bool, size: tuple | vec2 = None) -> None:
        self._winvars_["fullscreen"] = fullscreen
        self.set_size(*size if size is not None else self.get_monitor_size())

    # Получить полноэкранный режим:
    def get_fullscreen(self) -> bool:
        return self._winvars_["fullscreen"]

    # Установить минимальный размер окна:
    def set_min_size(self, width: int, height: int) -> None:
        self._winvars_["min-size"] = vec2(int(width), int(height))

    # Получить минимальный размер окна:
    def get_min_size(self) -> vec2:
        return vec2(self._winvars_["min-size"])

    # Установить максимальный размер окна:
    def set_max_size(self, width: int, height: int) -> None:
        self._winvars_["max-size"] = vec2(int(width), int(height))

    # Получить максимальный размер окна:
    def get_max_size(self) -> vec2:
        return vec2(self._winvars_["max-size"])

    # Установить количество сэмплов антиалиазинга:
    def set_samples(self, samples: int) -> None:
        if not 0 <= samples <= 16:  # Если samples не в диапазоне от 0 до 16:
            raise OpenGLWindowError(
                f"Graphics Error: Samples must be set in the range from 0 to 16. You have set: {samples}")
        self._winvars_["samples"] = samples
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, self._winvars_["samples"])
        self._recreate_()

    # Получить количество сэмплов антиалиазинга:
    def get_samples(self) -> None:
        return self._winvars_["samples"]

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
        current_scene = self._winvars_["current-scene"]
        if current_scene is not None and issubclass(type(current_scene), Scene):
            current_scene.destroy()

        # Устанавливаем сцену:
        self._winvars_["current-scene"] = scene

        # Сбрасываем окно просмотра:
        self._winvars_["is-new-scene"] = True

        # Если мы установили сцену в виде None, то просто возвращаемся:
        if scene is None: return

        # Указываем ссылку на основное окно:
        self._winvars_["current-scene"].window = self

        # Вызываем старт сцены:
        try: self._winvars_["current-scene"].start()
        except KeyboardInterrupt: self.exit()

    # Получить текущую игровую сцену:
    def get_scene(self) -> Scene | None:
        return self._winvars_["current-scene"]

    # Получить размер монитора:
    def get_monitor_size(self) -> vec2:
        return vec2(self._winvars_["monitor-size"])

    # Получить ширину окна:
    def get_width(self) -> int:
        return int(self._winvars_["width"])

    # Получить высоту окна:
    def get_height(self) -> int:
        return int(self._winvars_["height"])

    # Получить центр окна. Координаты половины размера окна:
    def get_center(self) -> vec2:
        size = self.get_size()
        return vec2(size.x // 2, size.y // 2)

    # Получить установленный FPS:
    def get_setted_fps(self) -> int:
        return self._winvars_["setted-fps"]

    # Получить дельту времени:
    def get_delta_time(self) -> float:
        return self._winvars_["dtime"]

    # Получить время:
    def get_time(self) -> float:
        return time.time() - self._winvars_["start-time"]

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
        self.set_visible(False)
        self.clear(0, 0, 0)
        self._winvars_["is-exit"] = True

    # Очистка окна (цвета от 0 до 1):
    @staticmethod
    def clear(red: float = 0.0, green: float = 0.0, blue: float = 0.0) -> None:
        gl.glClearColor(abs(red), abs(green), abs(blue), 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    # Отрисовка окна:
    def display(self) -> None:
        pygame.display.flip()  # Меняем буферы кадра местами.
