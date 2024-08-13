#
# shader.py - Создаёт класс шейдерной программы.
#


# Импортируем:
from .gl import *
from ..math import *


_texture_units_ = {}  # Словарь для хранения текстурных юнитов.


# Обёртка ошибки компиляции шейдеров:
class ShaderProgramError(RuntimeError): pass


# Класс шейдерной программы:
class ShaderProgram:
    def __init__(self, frag: str | int = None, vert: str | int = None, geom: str | int = None) -> None:
        self.frag = frag
        self.vert = vert
        self.geom = geom
        self.program = gls.glCreateProgram()
        self._id_before_begin_ = gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM)

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
    def begin(self) -> "ShaderProgram":
        self._id_before_begin_ = gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM)
        gl.glUseProgram(self.program)

        return self

    # Не используем шейдер:
    def end(self) -> "ShaderProgram":
        gl.glUseProgram(self._id_before_begin_)
        return self

    # Получить номер униформы шейдера:
    def get_uniform(self, name: str) -> int:
        return gl.glGetUniformLocation(self.program, name)

    # Установить значение для униформы в шейдере:
    def set_uniform(self, name: str, value: bool | int | float | list | tuple | numpy.ndarray) -> "ShaderProgram":
        if isinstance(value, (glm.vec2, glm.vec3, glm.vec4, tuple)): value = list(value)
        if type(value) is numpy.ndarray: value = value.tolist()
        location = self.get_uniform(name)
        if location == -1: return

        # Тип bool:
        if type(value) is bool:
            gl.glUniform1i(location, value)

        # Тип int:
        elif type(value) is int:
            gl.glUniform1i(location, value)

        # Тип float:
        elif type(value) is float:
            gl.glUniform1f(location, value)

        # Тип vec2:
        elif type(value) is list and len(value) == 2 and not type(value[0]) is list:
            gl.glUniform2f(location, *value[:2])

        # Тип vec3:
        elif type(value) is list and len(value) == 3 and not type(value[0]) is list:
            gl.glUniform3f(location, *value[:3])

        # Тип vec4:
        elif type(value) is list and len(value) == 4 and not type(value[0]) is list:
            gl.glUniform4f(location, *value[:4])

        # Тип mat2:
        elif type(value) is list and len(value) == 2 and type(value[0]) is list:
            gl.glUniformMatrix2fv(location, 1, gl.GL_FALSE, value)

        # Тип mat3:
        elif type(value) is list and len(value) == 3 and type(value[0]) is list:
            gl.glUniformMatrix3fv(location, 1, gl.GL_FALSE, value)

        # Тип mat4:
        elif type(value) is list and len(value) == 4 and type(value[0]) is list:
            gl.glUniformMatrix4fv(location, 1, gl.GL_FALSE, value)

        # Иначе, если неизвестный тип данных:
        else: raise ValueError(f"Unsupported data type. Your data type: {type(value)}, not supported.")

        return self

    # Установить значение для униформы типа sampler2d:
    def set_sampler2d(self, name: str, value: int) -> "ShaderProgram":
        global _texture_units_
        location = self.get_uniform(name)
        if location == -1: return

        # Создаем элемент для текущего экземпляра класса, если его ещё нет:
        if id(self) not in _texture_units_: _texture_units_[id(self)] = {}

        # Ищем свободный текстурный юнит для униформы:
        if name not in _texture_units_[id(self)]:
            # Ищем свободный текстурный юнит:
            tunit = 1  # texture unit.
            while tunit in [unit for units in _texture_units_.values() for unit in units.values()]: tunit += 1
            
            # Сохраняем соответствие между именем униформы и текстурным юнитом:
            _texture_units_[id(self)][name] = tunit
        else: tunit = _texture_units_[id(self)][name]

        # Активируем текстурный юнит:
        gl.glActiveTexture(gl.GL_TEXTURE0 + tunit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, value)
        gl.glUniform1i(location, tunit)

        # Возвращаемся к нулевому текстурному юниту и нулевой текстуре:
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        return self

    # Удаление шейдера:
    def destroy(self) -> None:
        gl.glDeleteProgram(self.program)


# Класс вычислительного шейдера:
""" Блок кода не был проверен на правильность реализации, и был вырезан из ядра.
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
    def begin(self) -> "ComputeShaderProgram":
        gl.glUseProgram(self.program)

        return self

    # Отправка на выполнение ядра вычислений:
    def dispatch(self, num_groups_x, num_groups_y, num_groups_z) -> "ComputeShaderProgram":
        gl.glDispatchCompute(num_groups_x, num_groups_y, num_groups_z)

        return self

    # Перестать использовать шейдер вычислений:
    def end(self) -> "ComputeShaderProgram":
        gl.glUseProgram(0)

        return self

    # Получить номер униформы шейдера:
    def get_uniform(self, name: str) -> int:
        return gl.glGetUniformLocation(self.program, name)

    # Удаление шейдера:
    def destroy(self) -> None:
        gl.glDeleteProgram(self.program)
"""
