#
# shader.py - Создаёт класс шейдерной программы.
#


# Импортируем:
if True:
    from .gl import *


# Флаги:
SHD_DEFAULT = 2  # По умолчанию.
SHD_MINIMUM = 3  # Минимальный.
SHD_SIMPLE  = 4  # Простой.


# Минимальный фрагментный шейдер:
MINIMUM_FRAGMENT_SHD = """
#version 430 core

// Выходной цвет:
out vec4 FragColor;

// Основная функция:
void main(void) {
    FragColor = vec4(0, 0, 0, 1);
}
"""


# Минимальный вершинный шейдер:
MINIMUM_VERTEX_SHD = """
#version 430 core

// Позиция вершины:
layout (location = 0) in vec3 a_position;

// Основная функция:
void main(void) {
    gl_Position = vec4(a_position, 1.0);
}
"""


# Простой фрагментный шейдер:
SIMPLE_FRAGMENT_SHD = """
#version 430 core

// Выходной цвет:
out vec4 FragColor;

// Основная функция:
void main(void) {
    FragColor = vec4(0, 0, 0, 1);
}
"""


# Простой вершинный шейдер:
SIMPLE_VERTEX_SHD = """
#version 430 core

// Входные переменные:
uniform mat4 u_modelview;   // Матрица модель-вида.
uniform mat4 u_projection;  // Матрица проекции.

// Позиция вершины:
layout (location = 0) in vec3 a_position;

// Основная функция:
void main(void) {
    gl_Position = u_projection * u_modelview * vec4(a_position, 1.0);
}
"""


# Класс шейдерной программы:
class ShaderProgram:
    def __init__(self, frag: str | int = None, vert: str | int = None, geom: str | int = None) -> None:
        self.frag = frag
        self.vert = vert
        self.geom = geom
        self.program = gls.glCreateProgram()

    # Получить индекс шейдерной программы:
    def compile(self) -> "ShaderProgram":
        shaders = []

        # Если нет фрагментного и вершинного шейдера:
        if self.frag is None and self.vert is None:
            shaders = [
                gls.compileShader(MINIMUM_FRAGMENT_SHD, gl.GL_FRAGMENT_SHADER),
                gls.compileShader(MINIMUM_VERTEX_SHD, gl.GL_VERTEX_SHADER)
            ]

        # Если мы хотим использовать минимальный фрагментный шейдер:
        if self.frag == SHD_MINIMUM:
            shaders.append(gls.compileShader(MINIMUM_FRAGMENT_SHD, gl.GL_FRAGMENT_SHADER))

        # Если мы хотим использовать простой фрагментный шейдер:
        if self.frag == SHD_SIMPLE:
            shaders.append(gls.compileShader(SIMPLE_FRAGMENT_SHD, gl.GL_FRAGMENT_SHADER))

        # Если мы хотим использовать минимальный вершинный шейдер:
        if self.vert == SHD_MINIMUM:
            shaders.append(gls.compileShader(MINIMUM_VERTEX_SHD, gl.GL_VERTEX_SHADER))

        # Если мы хотим использовать простой вершинный шейдер:
        if self.vert == SHD_SIMPLE:
            shaders.append(gls.compileShader(SIMPLE_VERTEX_SHD, gl.GL_VERTEX_SHADER))

        # Если фрагментный шейдер есть:
        if type(self.frag) is str: shaders.append(gls.compileShader(self.frag, gl.GL_FRAGMENT_SHADER))

        # Если вершинный шейдер есть:
        if type(self.vert) is str: shaders.append(gls.compileShader(self.vert, gl.GL_VERTEX_SHADER))

        # Если геометрический шейдер есть:
        if self.geom is not None: shaders.append(gls.compileShader(self.geom, gl.GL_GEOMETRY_SHADER))

        self.program = gls.compileProgram(*shaders)
        return self

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
    def compile(self) -> "ComputeShaderProgram":
        self.program = gls.compileProgram(
            gls.compileShader(self.compute, gl.GL_COMPUTE_SHADER))
        return self

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
