#
# skybox.py - Создаёт класс для отрисовки неба используя 6 текстур.
#


# Импортируем:
from .gl import *
from .texture import Texture
from .camera import Camera3D
from .shader import ShaderProgram
from ..math import *


# Класс неба:
class SkyBox:
    # Класс кубического неба:
    class CubeMap:
        def __init__(self,
                     camera: Camera3D,
                     up:     Texture,
                     down:   Texture,
                     front:  Texture,
                     back:   Texture,
                     left:   Texture,
                     right:  Texture,
                     box_size: float = 1) -> None:
            self.camera = camera
            self.textures = [
                up, down,
                front, back,
                left, right
            ]

            s = box_size  # Половина размера куба неба.

            # Вершины скайбокса:
            self.vertices = [
                [-s, -s, -s, 0, 1], [+s, -s, -s, 1, 1], [+s, +s, -s, 1, 0], [-s, +s, -s, 0, 0],
                [-s, +s, +s, 1, 0], [+s, +s, +s, 0, 0], [+s, -s, +s, 0, 1], [-s, -s, +s, 1, 1],
                [-s, +s, -s, 0, 1], [+s, +s, -s, 1, 1], [+s, +s, +s, 1, 0], [-s, +s, +s, 0, 0],
                [+s, -s, -s, 1, 0], [-s, -s, -s, 0, 0], [-s, -s, +s, 0, 1], [+s, -s, +s, 1, 1],
                [-s, +s, -s, 1, 0], [-s, +s, +s, 0, 0], [-s, -s, +s, 0, 1], [-s, -s, -s, 1, 1],
                [+s, +s, +s, 1, 0], [+s, +s, -s, 0, 0], [+s, -s, -s, 0, 1], [+s, -s, +s, 1, 1]
            ]

        # Отрисовать скайбокс:
        def render(self) -> "SkyBox.CubeMap":
            def draw_face(vertices: list, texture) -> None:
                gl.glBindTexture(gl.GL_TEXTURE_2D, texture.id)
                gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
                gl.glBegin(gl.GL_QUADS)
                for vert in vertices: gl.glTexCoord2f(vert[3], vert[4]) ; gl.glVertex3d(vert[0], vert[1], vert[2])
                gl.glEnd()

            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            is_enabled_cull_face = True if gl.glIsEnabled(gl.GL_CULL_FACE) else False
            is_enabled_lighting = True if gl.glIsEnabled(gl.GL_LIGHTING) else False
            gl.glScale(1, 1, 1)
            gl.glTranslated(*self.camera.position.xyz)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_LIGHTING)
            gl.glEnable(gl.GL_CULL_FACE)
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glColor(1, 1, 1)

            draw_face(self.vertices[8:12],  self.textures[0])  # UP.
            draw_face(self.vertices[12:16], self.textures[1])  # DOWN.
            draw_face(self.vertices[:4],    self.textures[2])  # FRONT.
            draw_face(self.vertices[4:8],   self.textures[3])  # BACK.
            draw_face(self.vertices[16:20], self.textures[4])  # LEFT.
            draw_face(self.vertices[20:],   self.textures[5])  # RIGHT.

            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
            if not is_enabled_cull_face: gl.glDisable(gl.GL_CULL_FACE)
            if is_enabled_lighting: gl.glEnable(gl.GL_LIGHTING)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glPopMatrix()

            return self

    # Класс математически-вычисляемой атмосферы:
    class Atmosphere:
        def __init__(self,
                     camera:               Camera3D,
                     sun_direction:        vec3,
                     sun_radius:           float = 1.0,
                     sun_color:            vec3  = vec3(1, 1, 1),
                     sun_intensity:        float = 1.0,
                     planet_radius:        float = 6371000.0,
                     atmosphere_radius:    float = 6471000.0,
                     wavelengths:          vec3  = vec3(720, 530, 440),
                     coef_mie:             float = 0.000001,
                     height_rlh:           float = 10_000.0,
                     height_mie:           float = 1200.0,
                     g_mie:                float = 0.985,
                     box_size:             float = 1) -> None:
            self.camera = camera

            # Параметры:
            self.sun_direction     = sun_direction      # Направление солнца.
            self.sun_radius        = sun_radius         # Радиус солнца.
            self.sun_color         = sun_color          # Цвет солнца.
            self.sun_intensity     = sun_intensity      # Интенсивность свечения солнца.
            self.planet_radius     = planet_radius      # Радиус планеты.
            self.atmosphere_radius = atmosphere_radius  # Радиус атмосферы.
            self.wavelengths       = wavelengths        # Длины волн цвета атмосферы (в нм).
            self.coef_mie          = coef_mie           # Коэффициент Ми (сила рассеивания света).
            self.height_rlh        = height_rlh         # Высота Рэлеевского слоя (10 км).
            self.height_mie        = height_mie         # Высота Миевского слоя  (1.2 км).
            self.g_mie             = g_mie              # Предпочтительное направление рассеяния Ми.

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

            // Структура камеры:
            struct Camera3D {
                vec3  position;
                vec3  rotation;
                float fov;
            };

            // Структура солнца:
            struct Sun {
                vec3  direction;
                float radius;
                vec3  color;
                float intensity;
            };

            // Входные переменные:
            uniform vec2     u_resolution;                               // Размер окна.
            uniform Camera3D u_camera;                                   // 3D Камера.
            uniform Sun      u_sun;                                      // Солнце.
            uniform float    u_planet_radius     = 6371000.0;            // Радиус планеты.
            uniform float    u_atmosphere_radius = 6471000.0;            // Радиус атмосферы.
            uniform vec3     u_wavelengths       = vec3(720, 530, 440);  // Длины волн цвета атмосферы (в нм).
            uniform float    u_coef_mie          = 0.000001;             // Коэффициент Ми (сила рассеивания света).
            uniform float    u_hrlh              = 10000.0;              // Высота Рэлеевского слоя (10 км).
            uniform float    u_hmie              = 1200.0;               // Высота Миевского слоя  (1.2 км).
            uniform float    u_g_mie             = 0.758;                // Предпочтительное направление рассеяния Ми.

            // Константы:
            const float PI = 3.1415926;  // Значение числа Пи.
            const int   i_steps = 16;    // Количество шагов для основного луча.
            const int   j_steps = 8;     // Количество шагов для вторичного луча.

            // Матричный поворот по X:
            mat3 rotate_x(float angle) {
                float rad_angle = radians(angle);
                float s = sin(rad_angle);
                float c = cos(rad_angle);
                return mat3(1.0, 0.0, 0.0, 0.0, c, -s, 0.0, s, c);
            }

            // Матричный поворот по Y:
            mat3 rotate_y(float angle) {
                float rad_angle = radians(angle);
                float s = sin(rad_angle);
                float c = cos(rad_angle);
                return mat3(c, 0.0, s, 0.0, 1.0, 0.0, -s, 0.0, c);
            }

            // Матричный поворот по Z:
            mat3 rotate_z(float angle) {
                float rad_angle = radians(angle);
                float s = sin(rad_angle);
                float c = cos(rad_angle);
                return mat3(c, -s, 0.0, s, c, 0.0, 0.0, 0.0, 1.0);
            }

            // Преобразовать длину волны в коэффициент Рэлея:
            float wavelength_to_rayleigh_coef(float wavelength) {
                // Я бы не сказал что формула правильная, но для меня это сработало.
                return 5.5e-6 * (550.0 * 550.0) / (wavelength * wavelength);;
            }

            // Проверка на пересечение луча со сферой:
            vec2 rsi(vec3 r0, vec3 rd, float sr) {
                // Пересечение луча и сферы, предполагающее, что сфера центрирована в начале координат.
                // Пересечение отсутствует, когда result.x > result.y
                float a = dot(rd, rd);
                float b = 2.0 * dot(rd, r0);
                float c = dot(r0, r0) - (sr * sr);
                float d = (b*b) - 4.0*a*c;
                if (d < 0.0) return vec2(1e5,-1e5);
                return vec2(
                    (-b - sqrt(d))/(2.0*a),
                    (-b + sqrt(d))/(2.0*a)
                );
            }

            // Возвращает цвет пикселя атмосферы:
            vec3 atmosphere(vec3 rdir, vec3 lpos, vec3 sdir, float isun, float rplan,float ratmo,
                            vec3 k_rlh, float k_mie, float h_rlh, float h_mie, float g) {
                /* Параметры:
                - rdir:  Направление обзора (нормализованное) (ray direction).
                - lpos:  Позиция источника света              (light position).
                - sdir:  Направление на солнце                (sun position).
                - isun:  Интенсивность солнца                 (sun indensity).
                - rplan: Радиус планеты                       (radius planet).
                - ratmo: Радиус атмосферы                     (radius atmosphere).
                - k_rlh: Коэффициент рассеяния Рэлея (цвет Рэлеевского рассеяния).
                - k_mie: Коэффициент рассеяния Ми (цвет Миевского рассеяния).
                - h_rlh: Высота Рэлеевского слоя.
                - h_mie: Высота Миевского слоя.
                - g:     Предпочтительное направление рассеяния Ми.
                */

                // Нормализуйте положение солнца и направления обзора:
                sdir = normalize(sdir);
                rdir = normalize(rdir);

                // Вычислите размер шага основного луча:
                vec2 p = rsi(lpos, rdir, ratmo);
                if (p.x > p.y) return vec3(0);
                p.y = min(p.y, rsi(lpos, rdir, rplan).x);
                float iStepSize = (p.y - p.x) / float(i_steps);

                // Инициализируйте время основного луча:
                float iTime = 0.0;

                // Инициализируйте аккумуляторы для рассеяния Рэлея и Ми:
                vec3 totalRlh = vec3(0, 0, 0);
                vec3 totalMie = vec3(0, 0, 0);

                // Инициализируйте накопители оптической глубины для основного луча:
                float iOdRlh = 0.0;
                float iOdMie = 0.0;

                // Вычислите фазы Рэлея и Ми:
                float mu = dot(rdir, sdir);
                float mumu = mu * mu;
                float gg = g * g;
                float pRlh = 3.0/(i_steps*PI)*(1.0+mumu);
                float pMie = 3.0/(j_steps*PI)*((1.0-gg)*(mumu+1.0))/(pow(1.0+gg-2.0*mu*g, 1.5)*(2.0+gg));

                // Возьмите образец первичного луча:
                for (int i = 0; i < i_steps; i++) {

                    // Вычислите положение образца первичного луча:
                    vec3 iPos = lpos + rdir * (iTime + iStepSize * 0.5);

                    // Рассчитайте высоту образца:
                    float iHeight = length(iPos) - rplan;

                    // Рассчитайте оптическую глубину рассеяния Рэлея и Ми для этого шага:
                    float odStepRlh = exp(-iHeight / h_rlh) * iStepSize;
                    float odStepMie = exp(-iHeight / h_mie) * iStepSize;

                    // Накапливать оптическую глубину:
                    iOdRlh += odStepRlh;
                    iOdMie += odStepMie;

                    // Вычислите размер шага вторичного луча:
                    float jStepSize = rsi(iPos, sdir, ratmo).y / float(j_steps);

                    // Инициализируйте время вторичного луча:
                    float jTime = 0.0;

                    // Инициализируйте накопители оптической глубины для вторичного луча:
                    float jOdRlh = 0.0;
                    float jOdMie = 0.0;

                    // Возьмите образец вторичного луча:
                    for (int j = 0; j < j_steps; j++) {

                        // Вычислите положение образца вторичного луча:
                        vec3 jPos = iPos + sdir * (jTime + jStepSize * 0.5);

                        // Рассчитайте высоту образца:
                        float jHeight = length(jPos) - rplan;

                        // Накапливайте оптическую глубину:
                        jOdRlh += exp(-jHeight / h_rlh) * jStepSize;
                        jOdMie += exp(-jHeight / h_mie) * jStepSize;

                        // Увеличьте время вторичного луча:
                        jTime += jStepSize;
                    }

                    // Рассчитайте затухание:
                    vec3 attn = exp(-(k_mie * (iOdMie + jOdMie) + k_rlh * (iOdRlh + jOdRlh)));

                    // Накапливать рассеяние:
                    totalRlh += odStepRlh * attn;
                    totalMie += odStepMie * attn;

                    // Увеличьте время основного луча:
                    iTime += iStepSize;
                }

                // Рассчитайте и верните конечный цвет:
                return vec3(isun * (pRlh * k_rlh * totalRlh + pMie * k_mie * totalMie));
            }

            // Функция, возвращающая цвет солнца, если луч пересекает его позицию:
            vec4 get_sun(vec3 rdir, vec3 sun_dir, float sun_radius, vec3 sun_color, vec3 sky_color) {
                float scalar = smoothstep(0.0, 1.0, dot(rdir, normalize(sun_dir)));
                vec3 sun_col = mix(vec3(0.0), sun_color, smoothstep(0.0, 1.0, pow(scalar, 1.0/(sun_radius*0.000001))));
                return vec4(sun_col, 2.0*smoothstep(0.0, 1.0, (1.0+sun_dir.y)*length(sky_color))-1.0);
            }

            // Выходной цвет:
            out vec4 FragColor;

            // Основная функция:
            void main(void) {
                vec2 uv = (gl_FragCoord.xy / u_resolution.xy * 2.0 - 1.0) * u_resolution / u_resolution.y;
                uv *= tan(radians(u_camera.fov) / 2.0);

                vec3 rd = normalize(vec3(uv, -1.0));

                // Вращаем направление луча:
                rd *= rotate_z(-u_camera.rotation.z);
                rd *= rotate_x(+u_camera.rotation.x);
                rd *= rotate_y(-u_camera.rotation.y);

                // Получаем коэффициенты рассеяния Рэлея для каждой длины волны:
                vec3 k_rlh = vec3(
                    wavelength_to_rayleigh_coef(u_wavelengths.r),
                    wavelength_to_rayleigh_coef(u_wavelengths.g),
                    wavelength_to_rayleigh_coef(u_wavelengths.b)
                );

                // Позиция света:
                vec3 light_pos = vec3(0, u_planet_radius+1000, 0);

                // Высора Рэлеевского слоя:
                float h_rlh = max(u_hrlh+2000, 2000);

                // Высота Миевского слоя:
                float h_mie = max(u_hmie+1200, 1200);

                // Получаем цвет пикселя атмосферы:
                vec3 color = atmosphere(
                    rd,                          // Нормализованное направление взгляда камеры.
                    light_pos,                   // Размещение источника света (высота 6372 км).
                    normalize(u_sun.direction),  // Направлениеи солнца.
                    u_sun.intensity*32,          // Интенсивность солнца.
                    u_planet_radius,             // Радиус планеты в метрах (6371 км).
                    u_atmosphere_radius,         // Радиус атмосферы в метрах (высота 6471 км).
                    k_rlh,                       // Коэффициент рассеяния Рэлея.
                    u_coef_mie,                  // Коэффициент рассеяния Ми (как сильно рассеивается свет).
                    h_rlh,                       // Высота Рэлеевского слоя (минимум 2 км).
                    h_mie,                       // Высота Миевского слоя (минимум 1.2 км).
                    u_g_mie                      // Предпочтительное направление рассеяния Ми.
                );

                // Примените экспозицию (по умолчанию, атмосфера слишком яркая):
                color = 1.0 - exp(-1.0 * color);

                // Добавляем солнце:
                vec4 sun_color = get_sun(
                    rd,                          // Нормализованное направление взгляда камеры.
                    normalize(u_sun.direction),  // Направление солнца.
                    u_sun.radius,                // Радиус солнца.
                    u_sun.color,                 // Цвет солнца.
                    color                        // Цвет неба.
                );

                // Возвращаем цвет пикселя:
                FragColor = vec4(color, 1.0) + sun_color;
            }
            """

            # Компилируем шейдер:
            self.shader = ShaderProgram(frag=fragment_shader, vert=vertex_shader).compile()

            s = box_size  # Половина размера куба неба.

            # Вершины скайбокса:
            self.vertices = [
                [-s, -s, -s], [+s, -s, -s], [+s, +s, -s], [-s, +s, -s],
                [-s, +s, +s], [+s, +s, +s], [+s, -s, +s], [-s, -s, +s],
                [-s, +s, -s], [+s, +s, -s], [+s, +s, +s], [-s, +s, +s],
                [+s, -s, -s], [-s, -s, -s], [-s, -s, +s], [+s, -s, +s],
                [-s, +s, -s], [-s, +s, +s], [-s, -s, +s], [-s, -s, -s],
                [+s, +s, +s], [+s, +s, -s], [+s, -s, -s], [+s, -s, +s]
            ]

        # Отрисовать скайбокс:
        def render(self) -> "SkyBox.Atmosphere":
            def draw_face(vertices: list) -> None:
                gl.glBegin(gl.GL_QUADS)
                for vert in vertices: gl.glVertex3d(vert[0], vert[1], vert[2])
                gl.glEnd()

            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            is_enabled_cull_face = True if gl.glIsEnabled(gl.GL_CULL_FACE) else False
            is_enabled_lighting = True if gl.glIsEnabled(gl.GL_LIGHTING) else False
            gl.glScale(1, 1, 1)
            gl.glTranslated(*self.camera.position.xyz)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_LIGHTING)
            gl.glEnable(gl.GL_CULL_FACE)
            gl.glColor(1, 1, 1)

            self.shader.begin()

            # Обновляем параметры атмосферы:
            self.shader.set_uniform("u_resolution",        (self.camera.width, self.camera.height))
            self.shader.set_uniform("u_camera.position",   self.camera.position)
            self.shader.set_uniform("u_camera.rotation",   self.camera.rotation)
            self.shader.set_uniform("u_camera.fov",        float(self.camera.fov))
            self.shader.set_uniform("u_sun.direction",     self.sun_direction)
            self.shader.set_uniform("u_sun.radius",        self.sun_radius)
            self.shader.set_uniform("u_sun.color",         self.sun_color)
            self.shader.set_uniform("u_sun.intensity",     self.sun_intensity)
            self.shader.set_uniform("u_planet_radius",     self.planet_radius)
            self.shader.set_uniform("u_atmosphere_radius", self.atmosphere_radius)
            self.shader.set_uniform("u_wavelengths",       self.wavelengths)
            self.shader.set_uniform("u_coef_mie",          self.coef_mie)
            self.shader.set_uniform("u_hrlh",              self.height_rlh)
            self.shader.set_uniform("u_hmie",              self.height_mie)
            self.shader.set_uniform("u_g_mie",             self.g_mie)

            draw_face(self.vertices[8:12])   # UP.
            draw_face(self.vertices[12:16])  # DOWN.
            draw_face(self.vertices[:4])     # FRONT.
            draw_face(self.vertices[4:8])    # BACK.
            draw_face(self.vertices[16:20])  # LEFT.
            draw_face(self.vertices[20:])    # RIGHT.

            self.shader.end()

            if not is_enabled_cull_face: gl.glDisable(gl.GL_CULL_FACE)
            if is_enabled_lighting: gl.glEnable(gl.GL_LIGHTING)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glPopMatrix()

            return self
