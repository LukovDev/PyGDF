#
# light.py - Создаёт поддержку освещения.
#


# Импортируем:
if True:
    from .gl import *
    from .draw import Draw2D
    from .camera import Camera2D
    from .shader import ShaderProgram
    from ..math import *


# Класс 2D освещения:
class Light2D:
    # Слой света. Просто текстура на которой отрисовываются все источники света:
    class RenderLayer:
        def __init__(self, camera: Camera2D, ambient: list = None) -> None:
            if ambient is None: ambient = [0, 0, 0, 0]

            self.camera        = camera   # Ваша 2д камера.
            self.ambient_color = ambient  # Цвет окружающего света.
            self.lights = []              # Список источников света.

            # Вершинный шейдер:
            vertex_shader = """
            #version 330 core

            // Позиция вершины:
            layout (location = 0) in vec3 a_position;

            // Основная функция:
            void main(void) {
                gl_Position = vec4(a_position, 1.0);
            }
            """

            # Фрагментный шейдер точечного источника света:
            fragment_shader = """
            #version 330 core

            // Входные переменные:
            uniform vec2 u_resolution;  // Разрешение окна.
            uniform int  u_type;        // Тип освещения.

            // Общие параметры источника света:
            uniform vec2 u_position;    // Позиция источника света.
            uniform vec3 u_color;       // Цвет источника света.
            uniform vec4 u_ambient;     // Цвет окружения.

            // Point Light:
            uniform float u_inner_radius;  // Внутренний радиус где яркость 100%.
            uniform float u_outer_radius;  // Внешний радиус где яркость 0%.

            // Выходной цвет:
            out vec4 FragColor;

            // Основная функция:
            void main(void) {
                vec2 uv = ((gl_FragCoord.xy / u_resolution.xy) - 0.5) * u_resolution.xy;

                // Итоговый цвет пикселя:
                vec4 final_color;

                // Тип освещения 1 - Point Light:
                if (u_type == 1) {
                    // Высчитываем яркость пикселя:
                    float innrad = u_inner_radius;
                    float intensity = clamp((length(uv-u_position)-innrad)/(u_outer_radius-innrad), 0, 1);

                    // Умножаем цвет источника света на интенсивность и добавляем его к окончательному цвету:
                    final_color = vec4(u_color * (1.0 - intensity), length(u_color));

                    // Если вдруг внутренний радиус будет больше чем наружный, то мы просто рисуем обычный круг:
                    if (u_inner_radius >= u_outer_radius) {
                        if (length(uv-u_position) <= u_outer_radius)
                            final_color = vec4(u_color.rgb, 1.0);
                        else final_color = u_ambient;
                    }
                }

                // Задаем окончательный цвет:
                FragColor = final_color;
            }
            """

            # Компилируем шейдер:
            self.shader = ShaderProgram(frag=fragment_shader, vert=vertex_shader).compile()

        # Отрисовываем световое окружение:
        def render(self) -> None:
            self.shader.begin()

            # Обновляем параметры шейдера:
            self.shader.set_uniform("u_resolution", (self.camera.width, self.camera.height))
            self.shader.set_uniform("u_type", 1)
            self.shader.set_uniform("u_position", vec2(0, 0))
            self.shader.set_uniform("u_color", vec3(1, 1, 1))
            self.shader.set_uniform("u_ambient", vec4(0, 0, 0, 0.5))
            self.shader.set_uniform("u_inner_radius", 16.0)
            self.shader.set_uniform("u_outer_radius", 128.0)

            Draw2D.quads([1, 1, 1], [(-1, -1), (+1, -1), (+1, +1), (-1, +1)])
            self.shader.end()

        # Удаляем световое окружение:
        def destroy(self) -> None:
            self.shader.destroy()

    # Класс точечного источника света:
    class PointLight:
        def __init__(self) -> None:
            pass

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
