#
# light.py - Создаёт поддержку освещения.
#


# Импортируем:
if True:
    from .gl import *
    from .draw import Draw2D
    from .camera import Camera2D
    from .shader import ShaderProgram
    from .sprite import Sprite2D
    from .batch import SpriteBatch2D
    from .texture import Texture
    from .renderer import Renderer2D
    from ..math import *
    from ..utils import get_only_type_list


# Класс 2D освещения:
class Light2D:
    # Класс слоя освещения:
    class LightLayer:
        def __init__(self, camera: Camera2D, ambient: list = None) -> None:
            if ambient is None: ambient = [0, 0, 0, 0.5]

            self.camera   = camera                 # Ваша 2D камера.
            self.ambient  = ambient                # Цвет окружающего света.
            self.lights   = []                     # Список источников света.
            self.batch    = SpriteBatch2D(camera)  # Пакетная отрисовка спрайтов.
            self.renderer = Renderer2D(camera)     # Конвейер рендеринга.

        # Отрисовываем световое окружение:
        def render(self, s, t) -> None:
            # Закрашиваем текстуру кадрового буфера в фоновый цвет освещения:
            self.renderer.fill(self.ambient)
            
            # Предварительно рисуем точечные источники света:
            self.batch.begin()
            for light in get_only_type_list(self.lights, Light2D.PointLight):
                light.__update__()
                self.batch.draw(
                    light.renderer.texture,
                    light.position.x - light.outer_radius / 2,
                    light.position.y - light.outer_radius / 2,
                    light.outer_radius, light.outer_radius)
            self.batch.end()

            # Начинаем рисовать источники света в окружении (слое света):
            self.renderer.begin()
            
            # Устанавливаем специальный режим смешивания:
            gl_set_blend_mode(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

            # Рисуем точечные источники света:
            self.batch.render()

            # Рисуем спрайтовыые источники света:
            for light in get_only_type_list(self.lights, Light2D.SpriteLight):
                light.sprite.render(
                    light.position.x - light.size.x / 2,
                    light.position.y - light.size.y / 2,
                    light.size.x, light.size.y,
                    light.angle, light.color
                )

            # Возвращаем обычный режим смешивания:
            gl_set_blend_mode()

            # Рисуем слой света:
            self.renderer.end()
            self.renderer.render()

        # Вызывается при изменении размера окна:
        def resize(self, width: int, height: int) -> None:
            self.renderer.resize(width, height)

        # Удаляем световое окружение:
        def destroy(self) -> None:
            self.shader.destroy()

    # Класс точечного источника света:
    class PointLight:
        def __init__(self,
                     layer:        "Light2D.LightLayer",
                     position:     vec2,
                     intensity:    float = 0.5,
                     color_inner:  list = None,
                     color_outer:  list = None,
                     inner_radius: float = 32,
                     outer_radius: float = 128
                     ) -> None:
            if color_inner is None: color_inner = [1, 1, 1]
            if color_outer is None: color_outer = [1, 1, 1]

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

            # Фрагментный шейдер:
            fragment_shader = """
            #version 330 core

            // Входные переменные:
            uniform vec4  u_ambient_color;  // Фоновый цвет света.
            uniform float u_inner_alpha;    // Сила альфа канала внутри круга.
            uniform vec3  u_color_inner;    // Цвет источника света внутри.
            uniform vec3  u_color_outer;    // Цвет источника света снаружи.
            uniform float u_inner_radius;   // Внутренний радиус где яркость 100%.
            uniform float u_outer_radius;   // Внешний радиус где яркость 0%.

            // Выходной цвет:
            out vec4 FragColor;

            // Основная функция:
            void main(void) {
                vec2 uv = ((gl_FragCoord.xy / u_outer_radius) - 0.5) * u_outer_radius * 2;

                vec3  color;  // Финальный цвет пикселя.
                float alpha;  // Альфа финального пикселя.

                // Вычисляем альфа канал:
                alpha = clamp((length(uv)-u_inner_radius)/(u_outer_radius-u_inner_radius), 0, 1);

                // Высчитываем цвет пикселя:
                color = mix(u_color_inner, u_color_outer, alpha);

                // Если вдруг внутренний радиус будет больше чем наружный, то мы просто рисуем обычный круг:
                if (u_inner_radius >= u_outer_radius && length(uv) <= u_outer_radius) {
                    color = u_color_inner.rgb;
                }

                // Если мы вышли за радиус круга, рисуем фоновый цвет:
                if (length(uv) >= u_outer_radius) {
                    FragColor = u_ambient_color;
                    return;
                }

                // Задаём окончательный цвет:
                FragColor = mix(vec4(color, mix(0.0, u_inner_alpha, 1.0-alpha)), u_ambient_color, alpha);
            }
            """

            self.layer        = layer         # Слой освещения.
            self.position     = position      # Позиция источника света.
            self.intensity    = intensity     # Интенсивность света.
            self.color_inner  = color_inner   # Цвет внутри.
            self.color_outer  = color_outer   # Цвет снаружи.
            self.inner_radius = inner_radius  # Внутренний радиус освещения.
            self.outer_radius = outer_radius  # Внешний радиус освещения.

            # Старые размеры внутреннего и наружного радиуса:
            self.__old_inner_radius__ = self.inner_radius
            self.__old_outer_radius__ = self.outer_radius

            # Конвейер рендеринга источника света:
            self.renderer = Renderer2D(self.layer.camera)
            self.renderer.resize(self.outer_radius, self.outer_radius)

            # Шейдер источника света:
            self.shader = ShaderProgram(frag=fragment_shader, vert=vertex_shader).compile()

            # Обновляем шейдер и рисуем его на текстурке:
            self.__update__()

            # Добавляем этот источник света в список источников света:
            self.layer.lights.append(self)

        # Обновить источник света:
        def __update__(self) -> None:
            """ Эта функция не нуждается в ручном вызове. Она вызывается в слое света автоматически. """

            # Указываем основные параметры:
            self.shader.begin()
            self.shader.set_uniform("u_ambient_color", self.layer.ambient)
            self.shader.set_uniform("u_inner_alpha",   self.intensity)
            self.shader.set_uniform("u_color_inner",   self.color_inner)
            self.shader.set_uniform("u_color_outer",   self.color_outer)
            self.shader.set_uniform("u_inner_radius",  float(self.inner_radius))
            self.shader.set_uniform("u_outer_radius",  float(self.outer_radius))
            self.shader.end()

            # Меняем размер текстуры шейдера, если наружный радиус или внутренний радиус были изменены:
            if self.__old_inner_radius__ != self.inner_radius or self.__old_outer_radius__ != self.outer_radius:
                self.renderer.resize(self.outer_radius, self.outer_radius)
                self.__old_inner_radius__ = self.inner_radius
                self.__old_outer_radius__ = self.outer_radius

            # Рисуем шейдер на текстурке:
            self.renderer.fill()
            self.renderer.begin()
            self.shader.begin()
            Draw2D.quads([1, 1, 1], [(-1, -1), (+1, -1), (+1, +1), (-1, +1)])
            self.shader.end()
            self.renderer.end()

    # Класс спрайтного источника света:
    class SpriteLight:
        def __init__(self,
                     layer:    "SpriteLight.LightLayer",
                     sprite:   Sprite2D | Texture,
                     position: vec2,
                     angle:    float,
                     size:     vec2,
                     color:    list = None,
                     ) -> None:
            """
                Заметки насчёт спрайта освещения:
                1. Сама по себе текстура может быть цветной, но так же её цвет можно указать в параметре color.
                2. Если вы хотите указывать цвет спрайта света, сделайте цвет картинки спрайта белой.
            """
            
            if color is None: color = [1, 1, 1]

            self.layer    = layer     # Слой освещения.
            self.position = position  # Позиция источника света.
            self.angle    = angle     # Угол наклона источника света.
            self.size     = size      # Размер источника света.
            self.color    = color     # Цвет света.
            self.sprite   = sprite    # Спрайт света.

            # Добавляем этот источник света в список источников света:
            self.layer.lights.append(self)
