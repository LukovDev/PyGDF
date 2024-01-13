#
# shader.py - Создаёт класс шейдерной программы.
#


# Импортируем:
if True:
    from .gl import *


# Класс шейдерной программы:
class ShaderProgram:
    def __init__(self, frag: str, vert: str = None, geom: str = None) -> None:
        self.frag = frag
        self.vert = vert
        self.geom = geom
        self.program = gls.glCreateProgram()

    # Получить индекс шейдерной программы:
    def compile(self) -> None:
        shaders = [
            gls.compileShader(self.frag, gl.GL_FRAGMENT_SHADER),
        ]

        if self.vert is not None: shaders.append(gls.compileShader(self.vert, gl.GL_VERTEX_SHADER))
        if self.geom is not None: shaders.append(gls.compileShader(self.geom, gl.GL_GEOMETRY_SHADER))

        self.program = gls.compileProgram(*shaders)

    # Используем шейдер:
    def begin(self) -> None:
        gl.glUseProgram(self.program)

    # Перестать использовать шейдер:
    def end(self) -> None:
        gl.glUseProgram(0)

    # Получить номер униформы шейдера:
    def get_uniform(self, name: str) -> int:
        return gl.glGetUniformLocation(self.program, name)

    # Установить значение для униформы типа bool:
    def uniform_bool(self, name: str, value: bool) -> None:
        location = self.get_uniform(name)
        if location != -1: gl.glUniform1i(location, value)

    # Установить значение для униформы типа float:
    def uniform_float(self, name: str, value: float) -> None:
        location = self.get_uniform(name)
        if location != -1: gl.glUniform1f(location, value)

    # Установить значение для униформы типа int:
    def uniform_int(self, name: str, value: int) -> None:
        location = self.get_uniform(name)
        if location != -1: gl.glUniform1i(location, value)

    # Установить значение для униформы типа vec2:
    def uniform_vec2(self, name: str, value) -> None:
        location = self.get_uniform(name)
        if location != -1: gl.glUniform2f(location, *value)

    # Установить значение для униформы типа vec3:
    def uniform_vec3(self, name: str, value) -> None:
        location = self.get_uniform(name)
        if location != -1: gl.glUniform3f(location, *value)

    # Установить значение для униформы типа vec4:
    def uniform_vec4(self, name: str, value) -> None:
        location = self.get_uniform(name)
        if location != -1: gl.glUniform4f(location, *value)

    # Установить значение для униформы типа mat2:
    def uniform_mat2(self, name: str, value) -> None:
        location = self.get_uniform(name)
        if location != -1: gl.glUniformMatrix2fv(location, 1, gl.GL_FALSE, value)

    # Установить значение для униформы типа mat3:
    def uniform_mat3(self, name: str, value) -> None:
        location = self.get_uniform(name)
        if location != -1: gl.glUniformMatrix3fv(location, 1, gl.GL_FALSE, value)

    # Установить значение для униформы типа mat4:
    def uniform_mat4(self, name: str, value) -> None:
        location = self.get_uniform(name)
        if location != -1: gl.glUniformMatrix4fv(location, 1, gl.GL_FALSE, value)

    # Удаление шейдера:
    def destroy(self) -> None:
        gl.glDeleteProgram(self.program)


# Класс вычислительного шейдера:
class ComputeShaderProgram:
    def __init__(self, compute: str) -> None:
        self.compute_src = compute
        self.program = gls.glCreateProgram()

    # Компиляция шейдера вычислений:
    def compile(self) -> None:
        self.program = gls.compileProgram(
            gls.compileShader(self.compute, gl.GL_COMPUTE_SHADER)
        )

    # Используем шейдер вычислений:
    def begin(self) -> None:
        gl.glUseProgram(self.program)

    # Отправка на выполнение ядра вычислений:
    def dispatch(self, num_groups_x, num_groups_y, num_groups_z) -> None:
        gl.glDispatchCompute(num_groups_x, num_groups_y, num_groups_z)

    # Перестать использовать шейдер вычислений:
    def end(self) -> None:
        gl.glUseProgram(0)

    # Получить номер униформы шейдера:
    def get_uniform(self, name: str) -> int:
        return gl.glGetUniformLocation(self.program, name)

    # Удаление шейдера:
    def destroy(self) -> None:
        gl.glDeleteProgram(self.program)
