#
# light.py - Создаёт поддержку освещения.
#


# Импортируем:
if True:
    # from .gl import *
    # from .camera import Camera2D
    # from .shader import ShaderProgram
    # from ..math import *
    ...


# Класс 2D освещения:
class Light2D:
    # Класс точечного источника света:
    class PointLight:
        def __init__(self) -> None:
            pass

    # # Класс световое окружение:
    # class LightEnvironment:
    #     def __init__(self, camera: Camera2D, ambient_intensity: float = 1.0, ambient_color: list = None) -> None:
    #         if ambient_color is None: ambient_color = [0.1, 0.1, 0.1]

    #         self.camera = camera                        # Ваша 2д камера.
    #         self.ambient_intensity = ambient_intensity  # Сила окружающего света.
    #         self.ambient_color     = ambient_color      # Цвет окружающего света.
    #         self.lights = []                            # Список источников света.

    #         # Вершинный шейдер:
    #         vertex_shader_main = """
    #         #version 330 core

    #         // Позиция вершины:
    #         layout (location = 0) in vec3 a_position;

    #         // Основная функция:
    #         void main(void) {
    #             gl_Position = vec4(a_position, 1.0);
    #         }
    #         """

    #         # Фрагментный шейдер точечного источника света:
    #         fragment_shader_point_light = """
    #         #version 330 core

    #         // Входные переменные:
    #         uniform vec2 u_resolution;  // Разрешение окна.
    #         uniform vec3 u_color;       // Цвет.

    #         // Выходной цвет:
    #         out vec4 FragColor;

    #         // Основная функция:
    #         void main(void) {
    #             vec2 uv = (gl_FragCoord.xy / u_resolution.xy * 2.0 - 1.0) * u_resolution / u_resolution.y;
                
    #             vec2 position = vec2(0, 0);
    #             float intensity = 1.0;
    #             vec3 color = vec3(1, 1, 1);
    #             float inner_radius = 0.25;
    #             float outer_radius = 1.0;

    #             float lightIntensity = 1.0-clamp((length(uv-position)-inner_radius)/(outer_radius-inner_radius), 0, 1);

    #             // Умножаем цвет источника света на интенсивность и добавляем его к окончательному цвету:
    #             vec3 finalColor = color * lightIntensity;

    #             // Задаем окончательный цвет:
    #             FragColor = vec4(finalColor, 1.0);
    #         }
    #         """

    #         # Компилируем шейдер:
    #         self.shader = ShaderProgram(frag=fragment_shader_point_light, vert=vertex_shader_main).compile()

    #         self.__vertices__ = [(-1, -1), (+1, -1), (+1, +1), (-1, +1)]

    #     # Отрисовываем световое окружение:
    #     def render(self) -> None:
    #         self.shader.begin()

    #         # Обновляем параметры шейдера:
    #         self.shader.set_uniform("u_resolution", (self.camera.width, self.camera.height))
    #         self.shader.set_uniform("u_color", [1, 0, 0])

    #         gl.glColor(1, 1, 1)
    #         gl.glBegin(gl.GL_QUADS)
    #         for v in self.__vertices__: gl.glVertex(*v)
    #         gl.glEnd()
    #         self.shader.end()

    #     # Удаляем световое окружение:
    #     def destroy(self) -> None:
    #         self.shader.destroy()

    # # Класс точечного источника света:
    # class PointLight:
    #     def __init__(self,
    #                  light_env:    "SimpleLight2D.LightEnvironment",
    #                  position:     vec2,
    #                  intensity:    float,
    #                  color:        list  = None,
    #                  inner_radius: float = 32,
    #                  outer_radius: float = 128
    #                  ) -> None:
    #         if color is None: color = [1, 1, 1]

    #         self.light_env    = light_env     # Световое окружение.
    #         self.position     = position      # Позиция источника света.
    #         self.intensity    = intensity     # Сила источника света.
    #         self.color        = color         # Цвет источника света.
    #         self.inner_radius = inner_radius  # Внутренний радиус освещения.
    #         self.outer_radius = outer_radius  # Внешний радиус освещения.
