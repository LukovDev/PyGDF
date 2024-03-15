#
# shader.py - Создаёт класс шейдерной программы.
#


# Импортируем:
if True:
    from .gl import *
    from ..math import *


__texture_units__ = {}  # Словарь для хранения текстурных юнитов.


# Обёртка ошибки компиляции шейдеров:
class ShaderProgramError(RuntimeError): pass


# Класс шейдерной программы:
class ShaderProgram:
    def __init__(self, frag: str | int = None, vert: str | int = None, geom: str | int = None) -> None:
        self.frag = frag
        self.vert = vert
        self.geom = geom
        self.program = gls.glCreateProgram()

    # Скомпилировать шейдер:
    def compile(self) -> "ShaderProgram":
        shaders = []

        # Функция для компиляции шейдера с обработкой ошибок
        def compile_shader(source_code: str, shader_type: int) -> int:
            # Создаем пустой объект шейдера:
            shader = gl.glCreateShader(shader_type)

            # Передаем исходный код шейдера OpenGL:
            gl.glShaderSource(shader, [source_code])

            # Компилируем шейдер:
            gl.glCompileShader(shader)

            # Проверяем статус компиляции:
            if not gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS):
                # Если компиляция не удалась, получаем ошибку:
                error = gl.glGetShaderInfoLog(shader).decode()

                # Удаляем объект шейдера:
                gl.glDeleteShader(shader)

                # Выводим сообщение об ошибке:
                raise RuntimeError(error)
            return shader

        # Пытаемся скомпилировать шейдер:
        try:
            # Если фрагментный шейдер есть:
            if type(self.frag) is str: shaders.append(compile_shader(self.frag, gl.GL_FRAGMENT_SHADER))

            # Если вершинный шейдер есть:
            if type(self.vert) is str: shaders.append(compile_shader(self.vert, gl.GL_VERTEX_SHADER))

            # Если геометрический шейдер есть:
            if self.geom is not None: shaders.append(compile_shader(self.geom, gl.GL_GEOMETRY_SHADER))
        except RuntimeError as error:
            raise RuntimeError(f"Shader compilation failed: {error}")

        self.program = gls.compileProgram(*shaders)
        return self

    # Используем шейдер:
    def begin(self) -> None:
        gl.glUseProgram(self.program)

    # Не используем шейдер:
    def end(self) -> None:
        gl.glUseProgram(0)

    # Получить номер униформы шейдера:
    def get_uniform(self, name: str) -> int:
        return gl.glGetUniformLocation(self.program, name)

    # Установить значение для униформы в шейдере:
    def set_uniform(self, name: str, value: bool | int | float | list | tuple | numpy.ndarray) -> None:
        if isinstance(value, (glm.vec2, glm.vec3, glm.vec4)): value = list(value)
        if type(value) is numpy.ndarray: value = value.tolist()
        if type(value) is tuple: value = list(value)
        location = self.get_uniform(name)
        if location == -1: return

        # Тип bool:
        if type(value) is bool:
            gl.glUniform1i(location, value)

        # Тип int:
        if type(value) is int:
            gl.glUniform1i(location, value)

        # Тип float:
        if type(value) is float:
            gl.glUniform1f(location, value)

        # Тип vec2:
        if type(value) is list and len(value) == 2 and not type(value[0]) is list:
            gl.glUniform2f(location, *value[:2])

        # Тип vec3:
        if type(value) is list and len(value) == 3 and not type(value[0]) is list:
            gl.glUniform3f(location, *value[:3])

        # Тип vec4:
        if type(value) is list and len(value) == 4 and not type(value[0]) is list:
            gl.glUniform4f(location, *value[:4])

        # Тип mat2:
        if type(value) is list and len(value) == 2 and type(value[0]) is list:
            gl.glUniformMatrix2fv(location, 1, gl.GL_FALSE, value)

        # Тип mat3:
        if type(value) is list and len(value) == 3 and type(value[0]) is list:
            gl.glUniformMatrix3fv(location, 1, gl.GL_FALSE, value)

        # Тип mat4:
        if type(value) is list and len(value) == 4 and type(value[0]) is list:
            gl.glUniformMatrix4fv(location, 1, gl.GL_FALSE, value)

    # Установить значение для униформы типа sampler2d:
    def set_sampler2d(self, name: str, value: int) -> None:
        global __texture_units__
        location = self.get_uniform(name)
        if location == -1: return

        # Создаем элемент для текущего экземпляра класса, если его ещё нет:
        if id(self) not in __texture_units__: __texture_units__[id(self)] = {}

        # Ищем свободный текстурный юнит для униформы:
        if name not in __texture_units__[id(self)]:
            # Ищем свободный текстурный юнит:
            tunit = 1  # texture unit.
            while tunit in [unit for units in __texture_units__.values() for unit in units.values()]: tunit += 1
            
            # Сохраняем соответствие между именем униформы и текстурным юнитом:
            __texture_units__[id(self)][name] = tunit
        else: tunit = __texture_units__[id(self)][name]

        # Активируем текстурный юнит:
        gl.glActiveTexture(gl.GL_TEXTURE0 + tunit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, value)
        gl.glUniform1i(location, tunit)

        # Возвращаемся к нулевому текстурному юниту и нулевой текстуре:
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

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
