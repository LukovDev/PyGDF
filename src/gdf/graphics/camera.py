#
# camera.py - Создаёт класс камеры.
#


# Импортируем:
from .gl import *
from ..math import *


# Класс 2D камеры:
class Camera2D:
    def __init__(self,
                 width:    int,
                 height:   int,
                 position: vec2,
                 angle:    float = 0.0,
                 zoom:     float = 1.0,
                 meter:    float = 100) -> None:
        self.width    = width                # Ширина камеры.
        self.height   = height               # Высота камеры.
        self.position = position             # Позиция камеры.
        self.angle    = angle                # Угол наклона камеры.
        self.zoom     = zoom                 # Масштаб камеры.
        self.meter    = meter                # Масштаб единицы измерения.
        self.size     = vec2(width, height)  # Размер камеры.

        self.modelview  = None
        self.projection = None

        self._is_ui_begin_ = False

        # Установка ортогональной проекции:
        self.resize(width, height)

        # Масштабирование и перемещение:
        self.update()

    # Обновление камеры:
    def update(self) -> "Camera2D":
        # Масштабирование, вращение и перемещение:
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        if self.zoom != 0: gl.glScale(1.0 / self.zoom, 1.0 / self.zoom, 1.0)
        else: gl.glScale(0.0, 0.0, 0.0)
        gl.glRotate(self.angle, False, False, True)
        gl.glTranslate(-self.position.x, -self.position.y, 0)

        self.modelview  = gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)
        self.projection = gl.glGetDoublev(gl.GL_PROJECTION_MATRIX)

        return self

    # Изменение размера камеры:
    def resize(self, width: int, height: int) -> "Camera2D":
        self.width = int(width)
        self.height = int(height)
        self.size = vec2(int(width), int(height))
        gl.glDisable(gl.GL_DEPTH_TEST)
        # gl.glEnable(gl.GL_CULL_FACE)  # Вырезать невидимые грани.
        gl.glViewport(0, 0, self.width, self.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        wdth, hght = self.width/2 * self.meter/100, self.height/2 * self.meter/100
        glu.gluOrtho2D(-wdth, wdth, -hght, hght)

        return self

    # Вызывайте эту функцию, когда хотите отрисовать интерфейс:
    def ui_begin(self) -> "Camera2D":
        if self._is_ui_begin_:
            raise Exception(
                "Function \".ui_end()\" was not called in the last iteration of the loop.\n"
                "The function \".ui_begin()\" cannot be called, since the last one "
                "\".ui_begin()\" was not closed by the \".ui_end()\" function.")
        self._is_ui_begin_  = True

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glTranslate(-self.width/2, -self.height/2, 0)
        return self

    # Вызывайте эту функцию, когда закончили рисовать интерфейс:
    def ui_end(self) -> "Camera2D":
        if self._is_ui_begin_: self._is_ui_begin_ = False
        else: raise Exception("The \".ui_begin()\" function was not called before the \".ui_end()\" function.")

        gl.glPopMatrix()
        return self

    # Освобождаем ресурсы:
    def destroy(self) -> None:
        pass  # Просто функция-затычка.


# Класс 3D камеры:
class Camera3D:
    def __init__(self,
                 width:    int,
                 height:   int,
                 position: vec3,
                 rotation: vec3  = vec3(0),
                 scale:    vec3  = vec3(1),
                 fov:      int   = 60,
                 far:      float = 1000,
                 near:     float = 0.01,
                 yaw:      float = 0.0,
                 pitch:    float = 0.0) -> None:
        self.width    = width      # Ширина камеры.
        self.height   = height     # Высота камеры.
        self.position = position   # Позиция камеры.
        self.rotation = rotation   # Вращение камеры.
        self.scale    = scale      # Размер камеры.
        self.fov      = fov        # Угол обзора камеры.
        self.far      = far        # Дальнее отсечение.
        self.near     = near       # Ближнее отсечение.
        self.yaw      = -90 + yaw  # Рыскание камеры.
        self.pitch    = pitch      # Тангаж камеры.
        # self.roll     = roll       # Крен камеры. TODO: Сделать крен камеры.

        self.modelview  = None
        self.projection = None

        self.up      = vec3(0, 1, 0)
        self.right   = vec3(1, 0, 0)
        self.forward = vec3(0, 0, 0)

        gl.glEnable(gl.GL_DEPTH_TEST)
        self.apply()

    # Обновление камеры:
    def update(self) -> "Camera3D":
        self.rotation.xyz = self.rotation.x % 360, self.rotation.y % 360, self.rotation.z % 360

        self.fov  = clamp(self.fov, 0, 180)
        self.far  = max(self.far, 1)
        self.near = max(self.near, 0.0001)

        self.apply()

        self.modelview  = gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)
        self.projection = gl.glGetDoublev(gl.GL_PROJECTION_MATRIX)
        return self

    # Изменение размера камеры:
    def resize(self, width: int, height: int) -> "Camera3D":
        self.width, self.height = int(width), int(height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glViewport(0, 0, self.width, self.height)
        glu.gluPerspective(self.fov, float(self.width) / self.height, self.near, self.far)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        return self

    # Применить настройки камеры:
    def apply(self) -> "Camera3D":
        # Преобразуем вектор направления:
        self.forward = normalize(vec3(
                cos(radians(self.pitch)) * cos(radians(self.yaw)),
                sin(radians(self.pitch)),
                cos(radians(self.pitch)) * sin(radians(self.yaw))
            )
        )

        # Преобразование forward, right, up в yaw, pitch, roll и преобразование их в градусы:
        self.rotation.xyz = vec3(
            degrees(asin(self.forward.y)),                     # PITCH в градусах.
            degrees(atan2(-self.forward.x, -self.forward.z)),  # YAW в градусах.
            degrees(atan2(self.right.y, self.up.y))            # ROLL в градусах.
        )

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glViewport(0, 0, self.width, self.height)
        glu.gluPerspective(self.fov, float(self.width) / self.height, self.near, self.far)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glScale(1 / self.scale.x, 1 / self.scale.y, 1 / self.scale.z)
        gl.glRotate(-self.rotation.x, True, False, False)  # Вращаем камеру по X-оси.
        gl.glRotate(-self.rotation.y, False, True, False)  # Вращаем камеру по Y-оси.
        gl.glRotate(-self.rotation.z, False, False, True)  # Вращаем камеру по Z-оси.
        gl.glTranslate(-self.position.x, -self.position.y, -self.position.z)

        return self

    # Освобождаем ресурсы:
    def destroy(self) -> None:
        pass  # Просто функция-затычка.
