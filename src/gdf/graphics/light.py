#
# light.py - Создаёт поддержку освещения.
#


# Импортируем:
from .gl import *
from .camera import Camera2D
from .shader import ShaderProgram
from .sprite import Sprite2D
from .texture import Texture
from .renderer import Renderer2D
from .batch import SpriteBatch2D
from ..math import *


# Класс 2D освещения:
class Light2D:
    # Класс слоя освещения:
    class LightLayer:
        def __init__(self,
                     camera:    Camera2D,
                     ambient:   list  = None,
                     intensity: float = 1.0,
                     mix_level: float = 0.0
                     ) -> None:
            ambient = [0, 0, 0, 0.5] if ambient is None else ambient

            self.camera              = camera                 # Ваша 2D камера.
            self.ambient             = ambient                # Цвет окружающего света.
            self.intensity           = intensity              # Яркость всего освещения.
            self.mix_level           = mix_level              # Сила смешивания окружающего света и источников света.
            self.lights              = []                     # Список источников света.
            self.batch               = SpriteBatch2D(camera)  # Пакетная отрисовка спрайтов.
            self.ambient_framebuffer = Renderer2D(camera)     # Кадровый буфер окружающего освещения.
            self.light_framebuffer   = Renderer2D(camera)     # Кадровый буфер источников света.

            # Шейдер:
            self.shader = ShaderProgram(
                vert="""
                #version 330 core

                layout (location = 0) in vec3 a_position;

                void main(void) {
                    gl_Position = vec4(a_position, 1.0);
                }
                """,
                frag="""
                #version 330 core

                uniform sampler2D u_ambient_texture;
                uniform sampler2D u_light_texture;
                uniform vec2      u_resolution;
                uniform float     u_intensity;
                uniform float     u_mix_level;

                out vec4 FragColor;

                void main(void) {
                    vec2 TexCoords = gl_FragCoord.xy / u_resolution.xy;

                    // Ограничиваем параметр смешивания:
                    float mix_level = clamp(u_mix_level, 0.0, 1.0);

                    // Получаем цвета пикселей из текстур:
                    vec4 ambient_color = texture(u_ambient_texture, TexCoords);
                    vec4 light_color = texture(u_light_texture, TexCoords);

                    // Альфа цвета пикселей (из их суммарной средней яркости):
                    float light_alpha = (light_color.r+light_color.g+light_color.b+light_color.a)/4.0*u_intensity;
                    float ambient_alpha = (ambient_color.r+ambient_color.g+ambient_color.b+ambient_color.a)/4.0;

                    // Основной смешанный цвет:
                    vec3 color = mix(
                        // Смешивание окружающего освещения и источников света (без "дымки"):
                        mix(ambient_color.rgb, light_color.rgb, ambient_alpha+light_alpha),

                        // Складывание окружающего освещения и источников света для создания "дымки":
                        ambient_color.rgb + light_color.rgb,
                    mix_level);

                    // Основной смешанный альфа цвет:
                    float alpha = mix(ambient_color.a-light_alpha, ambient_color.a-light_color.a, mix_level);

                    FragColor = vec4(color, alpha);
                }
                """
            ).compile()

            # Старый размер камеры:
            self._old_size_ = (self.camera.width, self.camera.height)

        # Отрисовываем световое окружение:
        def render(self, color: list = None) -> "Light2D.LightLayer":
            # Если размер камеры отличается от старого размера:
            if self._old_size_ != (self.camera.width, self.camera.height):
                self.ambient_framebuffer.resize(self.camera.width, self.camera.height)
                self.light_framebuffer.resize(self.camera.width, self.camera.height)
                self._old_size_ = (self.camera.width, self.camera.height)

            # Ограничиваем альфа-канал окружения от 0 до 1:
            self.ambient[3] = clamp(self.ambient[3], 0.0, 1.0)

            # Закрашиваем текстуру окружающего света и текстуру освещения:
            self.ambient_framebuffer.clear(self.ambient)
            self.light_framebuffer.clear([0, 0, 0, 0])

            # Начинаем рисовать источники света:
            self.light_framebuffer.begin()

            # Рисуем источники света:
            self.batch.begin()
            for light in self.lights:
                if type(light) is Light2D.PointLight:
                    light._render_()

                # Если это спрайтовый источник света:
                elif type(light) is Light2D.SpriteLight:
                    if light.color == [1, 1, 1]:
                        self.batch.draw(
                            light.sprite,
                            light.position.x - light.size.x / 2,
                            light.position.y - light.size.y / 2,
                            light.size.x, light.size.y, light.angle
                        )
                    else:
                        light.sprite.render(
                            light.position.x - light.size.x / 2,
                            light.position.y - light.size.y / 2,
                            light.size.x, light.size.y,
                            light.angle, light.color
                        )
            self.batch.end()
            self.batch.render(color)

            # Рисуем слой света:
            self.light_framebuffer.end()

            self.shader.begin()
            self.shader.set_sampler2d("u_ambient_texture", self.ambient_framebuffer.texture)  # Текстура окружения.
            self.shader.set_sampler2d("u_light_texture",   self.light_framebuffer.texture)    # Текстура освещения.
            self.shader.set_uniform  ("u_resolution",      self.camera.size.xy)         # Размер окна.
            self.shader.set_uniform  ("u_intensity",       self.intensity)         # Яркость всего света.
            self.shader.set_uniform  ("u_mix_level",       self.mix_level)         # Смешивание света и окружения.
            self.ambient_framebuffer.render_shader()
            self.shader.end()

            return self

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

            // Матрицы камеры:
            uniform mat4 u_modelview;
            uniform mat4 u_projection;

            // Позиция вершины:
            layout (location = 0) in vec3 a_position;

            // Основная функция:
            void main(void) {
                gl_Position = u_projection * u_modelview * vec4(a_position, 1.0);
            }
            """

            # Фрагментный шейдер:
            fragment_shader = """
            #version 330 core

            // Входные переменные:
            uniform vec2  u_resolution;     // Размер окна.
            uniform vec2  u_cam_position;   // Позиция камеры.
            uniform float u_cam_zoom;       // Масштаб камеры.

            // Параметры источника света:
            uniform vec2  u_position;       // Позиция источника света.
            uniform float u_intensity;      // Сила альфа канала внутри круга.
            uniform vec4  u_ambient_color;  // Фоновый цвет света.
            uniform vec3  u_color_inner;    // Цвет источника света внутри.
            uniform vec3  u_color_outer;    // Цвет источника света снаружи.
            uniform float u_inner_radius;   // Внутренний радиус.
            uniform float u_outer_radius;   // Внешний радиус.

            // Выходной цвет:
            out vec4 FragColor;

            // Основная функция:
            void main(void) {
                // Настраиваем систему координат шейдера:
                vec2 position = (u_position - u_cam_position) * (1.0 / u_cam_zoom);
                vec2 uv = (((gl_FragCoord.xy - position) / u_resolution.xy) - 0.5) * u_resolution.xy * 2;

                vec3  color;  // Финальный цвет пикселя.
                float alpha;  // Альфа финального пикселя.

                float inner_rad = u_inner_radius * (1.0 / u_cam_zoom);  // Настраиваем внутренний радиус.
                float outer_rad = u_outer_radius * (1.0 / u_cam_zoom);  // Настраиваем наружный радиус.

                // Если вдруг внутренний радиус будет больше чем наружный:
                if (inner_rad >= outer_rad) {
                    inner_rad = outer_rad;
                }

                // Вычисляем альфа канал:
                alpha = smoothstep(inner_rad, outer_rad, length(uv));

                // Вычисляем цвет пикселя:
                color = mix(u_color_inner, u_color_outer, alpha);

                // Задаём окончательный цвет:
                FragColor = vec4(color.rgb, 1.0 - alpha) * min(u_intensity * 0.9, 0.9);
            }
            """

            self.layer        = layer         # Слой освещения.
            self.position     = position      # Позиция источника света.
            self.intensity    = intensity     # Интенсивность света.
            self.color_inner  = color_inner   # Цвет внутри.
            self.color_outer  = color_outer   # Цвет снаружи.
            self.inner_radius = inner_radius  # Внутренний радиус освещения.
            self.outer_radius = outer_radius  # Внешний радиус освещения.

            # Шейдер источника света:
            self.shader = ShaderProgram(frag=fragment_shader, vert=vertex_shader).compile()

            # Добавляем этот источник света в список источников света:
            self.layer.lights.append(self)

        # Отрисовать источник света:
        def _render_(self) -> None:
            """ Эта функция не нуждается в ручном вызове. Она вызывается в слое света автоматически. """

            self.shader.begin()

            # Устанавливаем переменные шейдера:
            # Входные переменные:
            self.shader.set_uniform("u_modelview",     self.layer.camera.modelview)
            self.shader.set_uniform("u_projection",    self.layer.camera.projection)
            self.shader.set_uniform("u_resolution",    [self.layer.camera.width, self.layer.camera.height])
            self.shader.set_uniform("u_cam_position",  self.layer.camera.position.xy)
            self.shader.set_uniform("u_cam_zoom",      self.layer.camera.zoom)

            # Параметры источника света:
            self.shader.set_uniform("u_position",      self.position.xy)
            self.shader.set_uniform("u_intensity",     self.intensity)
            self.shader.set_uniform("u_ambient_color", self.layer.ambient)
            self.shader.set_uniform("u_color_inner",   self.color_inner)
            self.shader.set_uniform("u_color_outer",   self.color_outer)
            self.shader.set_uniform("u_inner_radius",  float(self.inner_radius))
            self.shader.set_uniform("u_outer_radius",  float(self.outer_radius))

            # Рисуем шейдер:
            w = h = self.outer_radius / 2 ; x, y = self.position.xy
            verts = [(-w + x, -h + y), (+w + x, -h + y), (+w + x, +h + y), (-w + x, +h + y)]

            gl.glColor(1, 1, 1)
            gl.glBegin(gl.GL_QUADS)
            for i in range(4): gl.glVertex(*verts[i])
            gl.glEnd()
            self.shader.end()

        # Удалить этот источник света из слоя света:
        def destroy(self) -> None:
            if self in self.layer.lights:
                self.layer.lights.remove(self)

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

        # Удалить этот источник света из слоя света:
        def destroy(self) -> None:
            if self in self.layer.lights:
                self.layer.lights.remove(self)
