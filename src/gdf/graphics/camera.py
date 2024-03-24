#
# camera.py - Создаёт класс камеры.
#


# Импортируем:
if True:
    import numpy as np
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
        self.width    = width          # Ширина камеры.
        self.height   = height         # Высота камеры.
        self.position = position       # Позиция камеры.
        self.angle    = angle          # Угол наклона камеры.
        self.zoom     = zoom           # Масштаб камеры.
        self.meter    = meter          # Масштаб единицы измерения.
        self.size     = width, height  # Размер камеры.

        self.modelview = None
        self.projection = None

        # Установка ортогональной проекции:
        self.resize(width, height)

        # Масштабирование и перемещение:
        self.update()

    # Обновление камеры:
    def update(self) -> "Camera2D":
        # Масштабирование, вращение и перемещение:
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        if self.zoom != 0: gl.glScaled(1 / self.zoom, 1 / self.zoom, 1)
        else: gl.glScaled(0.0, 0.0, 0.0)
        gl.glRotatef(self.angle, False, False, True)
        gl.glTranslated(-self.position.x, -self.position.y, 0)

        self.modelview  = gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)
        self.projection = gl.glGetDoublev(gl.GL_PROJECTION_MATRIX)

        return self

    # Изменение размера камеры:
    def resize(self, width: int, height: int) -> "Camera2D":
        self.width = width
        self.height = height
        self.size = width, height
        gl.glDisable(gl.GL_DEPTH_TEST)
        # gl.glEnable(gl.GL_CULL_FACE)
        gl.glViewport(0, 0, self.width, self.height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        wdth, hght = width/2 * self.meter/100, height/2 * self.meter/100
        glu.gluOrtho2D(-wdth, wdth, -hght, hght)

        return self

    # Получить позицию точки из окна в мировом пространстве:
    def screen_to_world(self, point_pos: tuple) -> tuple:
        # Позиция нижнего левого угла камеры с учётом метра и зума камеры:
        camera_posx = self.position.x - ((self.width  * self.zoom) / 2) * (self.meter / 100)
        camera_posy = self.position.y - ((self.height * self.zoom) / 2) * (self.meter / 100)

        # Позиция точки с учётом метра и зума камеры (Y координату точки инвертируем):
        point_posx = (point_pos[0]                * (self.meter / 100)) * self.zoom
        point_posy = (-(point_pos[1]-self.height) * (self.meter / 100)) * self.zoom

        # Складываем и возвращаем результат:
        return camera_posx + point_posx, camera_posy + point_posy


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
                 yaw:      float = 0,
                 pitch:    float = 0) -> None:
        self.width    = width      # Ширина камеры.
        self.height   = height     # Высота камеры.
        self.position = position   # Позиция камеры.
        self.rotation = rotation   # Вращение камеры.
        self.scale    = scale      # Размер камеры.
        self.fov      = fov        # Угол обзора камеры.
        self.far      = far        # Дальнее отсечение.
        self.near     = near       # Ближнее отсечение.
        self.yaw      = -90+yaw    # Рыскание камеры.
        self.pitch    = pitch      # Тангаж камеры.
        self.size = width, height  # Размер камеры.

        self.modelview = None
        self.projection = None

        self.up      = vec3(0, 1, 0)
        self.right   = vec3(1, 0, 0)
        self.forward = vec3(0, 0, 0)

        gl.glEnable(gl.GL_DEPTH_TEST)
        self.apply()

    # Обновление камеры:
    def update(self) -> "Camera3D":
        self.rotation.xyz = self.rotation.x % 360, self.rotation.y % 360, self.rotation.z % 360

        if self.fov  > 179    : self.fov = 179
        if self.fov  < 1      : self.fov = 1
        if self.far  < 1      : self.far = 1
        if self.near < 0.0001 : self.near = 0.0001

        self.apply()

        self.modelview  = gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)
        self.projection = gl.glGetDoublev(gl.GL_PROJECTION_MATRIX)

        return self

    # Изменение размера камеры:
    def resize(self, width: int, height: int) -> "Camera3D":
        self.size = width, height
        self.width, self.height = width, height
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
        gl.glScaled(1 / self.scale.x, 1 / self.scale.y, 1 / self.scale.z)
        gl.glRotatef(-self.rotation.x, True, False, False)  # Вращаем камеру по X-оси.
        gl.glRotatef(-self.rotation.y, False, True, False)  # Вращаем камеру по Y-оси.
        gl.glRotatef(-self.rotation.z, False, False, True)  # Вращаем камеру по Z-оси.
        gl.glTranslatef(-self.position.x, -self.position.y, -self.position.z)

        return self
