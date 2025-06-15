#
# camera.py - Создаёт класс камеры.
#


# Импортируем:
from .gl import *
from .render import RenderPipeline
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
        self.width    = int(width)           # Ширина камеры.
        self.height   = int(height)          # Высота камеры.
        self.position = position             # Позиция камеры.
        self.angle    = angle                # Угол наклона камеры.
        self.zoom     = zoom                 # Масштаб камеры.
        self.meter    = meter                # Масштаб единицы измерения.
        self.size     = vec2(width, height)  # Размер камеры.

        wdth, hght = self.width/2 * self.meter/100, self.height/2 * self.meter/100
        self.view = ModelMatrix(-self.position.xy, self.angle, vec2(1.0/self.zoom))
        self.projection = ModelMatrix(matrix=glm.ortho(-wdth, wdth, -hght, hght, -1.0, 1.0))

        self._ui_begin_ = False
        self._ui_view_  = glm.translate(mat4(1.0), vec3(-self.size.xy/2, 0))
        self._old_size_ = self.size.xy

        # Установка ортогональной проекции:
        self.resize(width, height)

        # Масштабирование и перемещение:
        self.update()

    # Обновление камеры:
    def update(self) -> "Camera2D":
        self.view.set_matrix(mat4(1.0))
        if self.zoom != 0.0: self.view.scale(vec2(1.0/self.zoom))
        else: self.view.scale(vec2(0.0))
        self.view.rotate(self.angle, vec3(0, 0, 1))
        self.view.translate(-self.position.xy)

        # Устанавливаем активную камеру:
        RenderPipeline.camera = self

        # Обновляем данные матриц в шейдере по умолчанию:
        RenderPipeline.default_shader.begin()
        RenderPipeline.default_shader.set_uniform("u_view", self.view)
        RenderPipeline.default_shader.set_uniform("u_projection", self.projection)
        RenderPipeline.default_shader.end()
        return self

    # Изменение размера камеры:
    def resize(self, width: int, height: int) -> "Camera2D":
        self.width, self.height = int(width), int(height)
        self.size = vec2(int(width), int(height))
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glViewport(0, 0, self.width, self.height)
        wdth, hght = self.width/2 * self.meter/100, self.height/2 * self.meter/100
        self.projection.set_matrix(glm.ortho(-wdth, wdth, -hght, hght, -1.0, 1.0))
        return self

    # Вызывайте эту функцию, когда хотите отрисовать интерфейс:
    def ui_begin(self) -> "Camera2D":
        if self._ui_begin_:
            raise Exception(
                "Function \".ui_end()\" was not called in the last iteration of the loop.\n"
                "The function \".ui_begin()\" cannot be called, since the last one "
                "\".ui_begin()\" was not closed by the \".ui_end()\" function.")
        self._ui_begin_ = True
        if self.size.xy != self._old_size_.xy:
            self._ui_view_ = glm.translate(mat4(1.0), vec3(-self.size.xy/2, 0))
            self._old_size_ = self.size.xy
        # Обнуляем матрицу вида в шейдере по умолчанию:
        RenderPipeline.default_shader.begin()
        RenderPipeline.default_shader.set_uniform("u_view", self._ui_view_)
        RenderPipeline.default_shader.end()
        return self

    # Вызывайте эту функцию, когда закончили рисовать интерфейс:
    def ui_end(self) -> "Camera2D":
        if self._ui_begin_: self._ui_begin_ = False
        else: raise Exception("The \".ui_begin()\" function was not called before the \".ui_end()\" function.")
        # Возвращаем обратно матрицу вида в шейдере по умолчанию:
        RenderPipeline.default_shader.begin()
        RenderPipeline.default_shader.set_uniform("u_view", self.view)
        RenderPipeline.default_shader.end()
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
                 rotation: vec3  = vec3(0),  # X-Pitch, Y-Yaw, Z-Roll.
                 size:     vec3  = vec3(1),
                 fov:      int   = 60,
                 far:      float = 1000,
                 near:     float = 0.01) -> None:
        position = vec3(position.xy, 0.0) if isinstance(position, (vec2, glm.vec2)) else position
        rotation = vec3(rotation.xy, 0.0) if isinstance(rotation, (vec2, glm.vec2)) else rotation
        self.width    = int(width)   # Ширина камеры.
        self.height   = int(height)  # Высота камеры.
        self.position = position     # Позиция камеры.
        self.rotation = rotation     # Вращение камеры.
        self.size     = size         # Размер камеры.
        self.fov      = fov          # Угол обзора камеры.
        self.far      = far          # Дальнее отсечение.
        self.near     = near         # Ближнее отсечение.

        self._old_fov_ = self.fov  # Старый угол обзора.

        self.view = ModelMatrix()
        self.projection = ModelMatrix()
        self.projection.set_matrix(glm.perspective(radians(self.fov), self.width/self.height, self.near, self.far))

        self.up      = vec3(0, 1, 0)
        self.right   = vec3(1, 0, 0)
        self.forward = vec3(0, 0, 0)

        # Установка проверки глубины и отсечение невидимых сторон:
        self.set_depth_test(True)
        self.set_cull_faces(True)

        self.update()

    # Обновление камеры:
    def update(self, depth_test: bool = True, cull_faces: bool = True) -> "Camera3D":
        if any([isnan(v) for v in self.position.xyz]): self.position = vec3(0)
        self.fov  = clamp(self.fov, 0, 180)
        self.far  = max(self.far, 1.0)
        self.near = max(self.near, 0.00001)

        # Обновляем матрицу проекции в случае обновления угла обзора:
        if self.fov != self._old_fov_:
            self.projection.set_matrix(glm.perspective(radians(self.fov), self.width/self.height, self.near, self.far))
            self._old_fov_ = self.fov

        # Установка проверки глубины и отсечение невидимых сторон:
        self.set_depth_test(depth_test)
        self.set_cull_faces(cull_faces)

        self.view.set_matrix(mat4(1.0))
        self.view.scale(1.0/self.size)
        self.view.rotate(+self.rotation.z, vec3(0, 0, 1))  # Вращаем камеру по Z-оси.
        self.view.rotate(-self.rotation.x, vec3(1, 0, 0))  # Вращаем камеру по X-оси.
        self.view.rotate(+self.rotation.y, vec3(0, 1, 0))  # Вращаем камеру по Y-оси.
        self.view.translate(-self.position)

        # Устанавливаем активную камеру:
        RenderPipeline.camera = self

        # Обновляем данные матриц в шейдере по умолчанию:
        RenderPipeline.default_shader.begin()
        RenderPipeline.default_shader.set_uniform("u_view", self.view)
        RenderPipeline.default_shader.set_uniform("u_projection", self.projection)
        RenderPipeline.default_shader.end()
        return self

    # Изменение размера камеры:
    def resize(self, width: int, height: int) -> "Camera3D":
        self.width, self.height = int(width), int(height)
        gl.glViewport(0, 0, self.width, self.height)
        self.projection.set_matrix(glm.perspective(radians(self.fov), self.width/self.height, self.near, self.far))
        return self

    # Установить тест глубины:
    def set_depth_test(self, enabled: bool) -> "Camera3D":
        gl.glEnable(gl.GL_DEPTH_TEST) if enabled else gl.glDisable(gl.GL_DEPTH_TEST)
        return self

    # Установить отсечение сторон:
    def set_cull_faces(self, enabled: bool) -> "Camera3D":
        gl.glEnable(gl.GL_CULL_FACE) if enabled else gl.glDisable(gl.GL_CULL_FACE)
        return self

    # Освобождаем ресурсы:
    def destroy(self) -> None:
        pass  # Просто функция-затычка.
