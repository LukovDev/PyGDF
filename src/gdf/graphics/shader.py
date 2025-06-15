#
# shader.py - Создаёт класс шейдерной программы.
#


# Импортируем:
from .gl import *
from ..math import *


# Обёртка ошибки компиляции шейдеров:
class ShaderCompileError(RuntimeError): pass


# Обёртка ошибки связывания шейдеров:
class ShaderLinkingError(RuntimeError): pass


# Класс шейдерной программы:
class ShaderProgram:
    def __init__(self, vert: str = None, frag: str = None, geom: str = None) -> None:
        self.vert = vert
        self.frag = frag
        self.geom = geom
        self.id = None
        self._is_begin_ = False
        self._id_before_begin_ = None
        self._uniform_value_cache_    = {}  # Кэш значений униформ.
        self._location_uniform_cache_ = {}  # Кэш позиций uniform.
        self._texunit_uniform_cache_  = {}  # Кэш привязки текстурных юнитов к названиям униформов.

    # Скомпилировать шейдер:
    def compile(self) -> "ShaderProgram":
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
                raise ShaderCompileError(error)
            return shader

        # Компилируем и добавляем шейдеры:
        shaders = []
        try:
            if isinstance(self.vert, str): shaders.append(compile_shader(self.vert, gl.GL_VERTEX_SHADER))
            if isinstance(self.frag, str): shaders.append(compile_shader(self.frag, gl.GL_FRAGMENT_SHADER))
            if isinstance(self.geom, str): shaders.append(compile_shader(self.geom, gl.GL_GEOMETRY_SHADER))
        except RuntimeError as error:
            raise ShaderCompileError(error)

        # Линкуем программу:
        self.id = gl.glCreateProgram()
        for shader in shaders: gl.glAttachShader(self.id, shader)
        gl.glLinkProgram(self.id)

        # Проверяем статус линковки:
        if not gl.glGetProgramiv(self.id, gl.GL_LINK_STATUS):
            error = gl.glGetProgramInfoLog(self.id).decode()
            gl.glDeleteProgram(self.id)
            raise ShaderLinkingError(error)

        # Удаляем отдельные шейдеры:
        for shader in shaders:
            gl.glDetachShader(self.id, shader)
            gl.glDeleteShader(shader)
        return self

    # Используем шейдер:
    def begin(self) -> "ShaderProgram":
        if self._is_begin_:
            raise Exception(
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self._id_before_begin_ = gl.glGetIntegerv(gl.GL_CURRENT_PROGRAM)
        gl.glUseProgram(self.id)
        self._is_begin_ = True
        return self

    # Не используем шейдер:
    def end(self) -> "ShaderProgram":
        if self._is_begin_: self._is_begin_ = False
        else:
            raise Exception("The \".begin()\" function was not called before the \".end()\" function.")
        if self._id_before_begin_ is not None:
            gl.glUseProgram(self._id_before_begin_)
        else: gl.glUseProgram(0)
        return self

    # Получить номер униформы шейдера:
    def get_location(self, name: str) -> int:
        if not self._is_begin_:
            raise Exception("The \".begin()\" function was not called before the \".get_location()\" function.")

        # Если название униформы есть в кэше, используем данные оттуда:
        if name in self._location_uniform_cache_:
            return self._location_uniform_cache_[name]

        # Кэширование вызова glGetUniformLocation:
        location = gl.glGetUniformLocation(self.id, name)
        self._location_uniform_cache_[name] = location
        return location

    # Установить значение для униформы в шейдере:
    def set_uniform(self, name: str, value: bool|int|float|list|tuple|numpy.ndarray,
                    location: int = None) -> "ShaderProgram":
        if not self._is_begin_:
            raise Exception("The \".begin()\" function was not called before the \".set_uniform()\" function.")
        if location is None: location = self.get_location(name)
        if location == -1: return self

        # Проверка входных значений:
        if hasattr(value, "to_list"): value = value.to_list()
        if isinstance(value, tuple): value = list(value)
        if isinstance(value, numpy.ndarray): value = value.tolist()

        # Если униформа есть в кэше и значение такое же, значит оно такое же и в шейдере. Поэтому ничего не делаем:
        if location in self._uniform_value_cache_ and value == self._uniform_value_cache_[location]: return self

        # Тип bool/int:
        if isinstance(value, bool) or isinstance(value, int):
            self._uniform_value_cache_[location] = value  # Кэшируем значение.
            gl.glUniform1i(location, value)

        # Тип float:
        elif isinstance(value, float):
            self._uniform_value_cache_[location] = value  # Кэшируем значение.
            gl.glUniform1f(location, value)

        # Тип vec2:
        elif isinstance(value, list) and len(value) == 2 and not isinstance(value[0], list):
            self._uniform_value_cache_[location] = value  # Кэшируем значение.
            gl.glUniform2f(location, *value)

        # Тип vec3:
        elif isinstance(value, list) and len(value) == 3 and not isinstance(value[0], list):
            self._uniform_value_cache_[location] = value  # Кэшируем значение.
            gl.glUniform3f(location, *value)

        # Тип vec4:
        elif isinstance(value, list) and len(value) == 4 and not isinstance(value[0], list):
            self._uniform_value_cache_[location] = value  # Кэшируем значение.
            gl.glUniform4f(location, *value)

        # Тип mat2:
        elif isinstance(value, list) and len(value) == 2 and isinstance(value[0], list):
            # Не кэшируем потому что большой массив данных.
            gl.glUniformMatrix2fv(location, 1, gl.GL_FALSE, value)

        # Тип mat3:
        elif isinstance(value, list) and len(value) == 3 and isinstance(value[0], list):
            # Не кэшируем потому что большой массив данных.
            gl.glUniformMatrix3fv(location, 1, gl.GL_FALSE, value)

        # Тип mat4:
        elif isinstance(value, list) and len(value) == 4 and isinstance(value[0], list):
            # Не кэшируем потому что большой массив данных.
            gl.glUniformMatrix4fv(location, 1, gl.GL_FALSE, value)

        # Тип ModelMatrix:
        elif isinstance(value, ModelMatrix):
            # Не кэшируем потому что большой массив данных.
            gl.glUniformMatrix4fv(location, 1, gl.GL_FALSE, value.matrix_list())

        # Иначе, если неизвестный тип данных:
        else: raise ValueError(f"Unsupported data type. Your data type: {type(value)}, not supported.")
        return self

    # Установить значение для униформы вроде sampler:
    def set_sampler(self, name: str, unit_id: int) -> "ShaderProgram":
        if not self._is_begin_:
            raise Exception("The \".begin()\" function was not called before the \".set_sampler()\" function.")
        location = self.get_location(name)
        if location == -1: return self

        # Если имя униформы есть в кэше и оно равняется указанному юниту, ничего не делаем:
        if self._texunit_uniform_cache_.get(name) == unit_id: return self

        # Иначе обновляем запись в кэше:
        self._texunit_uniform_cache_[name] = unit_id
        gl.glUniform1i(location, unit_id)
        return self

    # Удаление шейдера:
    def destroy(self) -> None:
        self._uniform_value_cache_.clear()
        self._location_uniform_cache_.clear()
        self._texunit_uniform_cache_.clear()
        if self.id is not None:
            gl.glDeleteProgram(self.id)
            self.id = None
