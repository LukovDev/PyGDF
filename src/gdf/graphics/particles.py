#
# particles.py - Создаёт класс частиц.
#


# Импортируем:
if True:
    from .batch import SpriteBatch2D
    from .camera import Camera2D
    from .texture import Texture
    from ..math import *
    from ..utils import Utils2D


# Класс 2D частиц:
class SimpleParticleEffect2D:
    """ Пример использования:
        particles = SimpleParticleEffect2D(
            texture       = particle_texture,
            position      = vec2(0, 0),
            direction     = vec2(0, 0),
            start_size    = vec2(16, 16),
            end_size      = vec2(16, 16),
            speed         = vec2(3, 10),
            damping       = 0.01,
            duration      = vec2(1, 2),
            count         = 512,
            gravity       = vec2(0, 0),
            start_angle   = 0.0,
            end_angle     = 0.0,
            is_infinite   = False,
            is_local_pos  = False,
            is_dir_angle  = False,
            custom_update = None
        ).create()

        # Пример собственной функции обновления частиц:
        def custom_update(delta_time: float, particles: list) -> None:
            pass
    """

    # Частица:
    class Particle:
        def __init__(self,
                     texture:  Texture | list,
                     position: vec2,
                     velocity: vec2,
                     angle:    float,
                     size:     vec2,
                     time:     float
                     ) -> None:
            self.texture     = texture
            self.position    = position
            self.velocity    = velocity
            self.angle       = angle
            self.size        = size
            self.time        = time
            self.static_time = time

        # Скорость перемещения частицы:
        @property
        def speed(self) -> float: return Utils2D.get_speed_vector(self.velocity)

    # Инициализация:
    def __init__(self,
                 texture:       Texture | list,
                 position:      vec2,
                 direction:     vec2,
                 start_size:    vec2,
                 end_size:      vec2,
                 speed:         vec2,
                 damping:       float,
                 duration:      vec2,
                 count:         int,
                 gravity:       vec2,
                 start_angle:   float = 0.0,
                 end_angle:     float = 0.0,
                 is_infinite:   bool  = True,
                 is_local_pos:  bool  = False,
                 is_dir_angle:  bool  = True,
                 custom_update: any   = None
                 ) -> None:

        # Параметры:
        self.texture       = texture        # Текстура частиц.
        self.position      = position       # Позиция эффекта частиц.
        self.direction     = direction      # Вектор направления частиц.
        self.start_size    = start_size     # Начальный размер частиц.
        self.end_size      = end_size       # Конечный размер частиц.
        self.speed         = speed          # Начальная скорость частицы. Случайно от X до Y.
        self.damping       = damping        # Сила затухания скорости частицы.
        self.duration      = duration       # Сколько должна жить частица (в секундах). Случайно от X до Y.
        self.count         = count          # Количество частиц.
        self.gravity       = gravity        # Сила гравитации.
        self.start_angle   = start_angle    # Начальный угол частицы.
        self.end_angle     = end_angle      # Конечный угол частицы.
        self.is_infinite   = is_infinite    # Бесконечные ли частицы.
        self.is_local_pos  = is_local_pos   # Частицы в локальном пространстве.
        self.is_dir_angle  = is_dir_angle   # Поворачивать ли частицу в сторону направления движения.
        self.custom_update = custom_update  # Кастомный обновлятор частиц.

        # Внутренние переменные класса:
        self.particles = None  # Список частиц.
        self.__partvars__ = {
            "batch":   SpriteBatch2D(),
            "old-pos": position.xy,
            "timer":   0.0,
        }

    # Создать одну частицу. Используется строго внутри этого класса:
    def __create_particle__(self) -> None:
        a = random.uniform(0, 2*math.pi)  # Случайный угол.
        rdir = vec2(sin(a), cos(a))       # Случайный вектор.

        ptxt = self.texture if type(self.texture) is Texture else random.choice(self.texture)
        ppos = self.position.xy
        pvel = normalize(rdir+self.direction) * random.uniform(*self.speed.xy)
        pang = self.start_angle
        psiz = self.start_size.xy
        ptfl = random.uniform(*self.duration.xy)

        # Частица:
        particle = SimpleParticleEffect2D.Particle(
            ptxt,  # Текстура частицы.
            ppos,  # Позиция.
            pvel,  # Вектор направления и скорости.
            pang,  # Угол поворота.
            psiz,  # Размер.
            ptfl   # Время жизни частицы.
        )

        # Добавляем частицу к другим частицам:
        self.particles.append(particle)

    # Создать эффект частиц:
    def create(self) -> "SimpleParticleEffect2D":
        if self.particles is None: self.particles = []

        for i in range(0 if self.is_infinite else self.count-len(self.particles)):
            self.__create_particle__()

        return self

    # Обновление частиц:
    def update(self, delta_time: float) -> "SimpleParticleEffect2D":
        if self.custom_update is not None: self.custom_update(delta_time, self.particles) ; return

        dt = min(delta_time, 1/5)*60

        # Если количество частиц меньше установленного, создаём новые:
        if len(self.particles) < self.count and self.is_infinite:
            self.__partvars__["timer"] -= delta_time
            while self.__partvars__["timer"] <= 0.0:
                self.__create_particle__()
                self.__partvars__["timer"] += (sum(self.duration) / 2) / self.count

        # Урезаем лишние частицы:
        self.particles = self.particles[:self.count]

        # Проходимся по частицам:
        for particle in self.particles:
            # Время жизни частицы. Если время вышло, удаляем частицу:
            particle.time -= delta_time
            if particle.time <= 0.0:
                self.particles.remove(particle)
                if self.is_infinite: self.__create_particle__()

            # Применяем гравитацию к направлению частицы:
            particle.velocity += self.gravity * dt
            particle.velocity *= 1.0 - self.damping

            # Перемещаем частичку в сторону её направления умноженное на её скорость:
            particle.position += normalize(particle.velocity) * particle.speed * dt
            if self.is_local_pos: particle.position += self.position - self.__partvars__["old-pos"]

            # Статическое время жизни частицы:
            pst = particle.static_time

            # Вращаем частицу:
            particle.angle += (self.end_angle/pst if pst > 0.0 else 0.0) * delta_time

            # Меняем размер:
            particle.size.xy += ((self.end_size.xy - self.start_size.xy) / pst) * delta_time

        self.__partvars__["old-pos"].xy = self.position.xy
        return self

    # Отрисовка частиц:
    def render(self, color: list = None) -> "SimpleParticleEffect2D":
        # Проходимся по частицам:
        self.__partvars__["batch"].begin()
        for particle in self.particles:
            angl = Utils2D.get_angle_points(vec2(0), normalize(particle.velocity)) + 90 if self.is_dir_angle else 0.0

            # Рисуем частицу:
            self.__partvars__["batch"].draw(
                sprite = particle.texture,
                x      = particle.position.x - (particle.size.x/2),
                y      = particle.position.y - (particle.size.y/2),
                width  = particle.size.x,
                height = particle.size.y,
                angle  = angl + particle.angle
            )
        self.__partvars__["batch"].end()

        self.__partvars__["batch"].render(color)
        return self

    # Удалить систему частиц:
    def destroy(self) -> None:
        if self.texture is None: return
        self.texture.destroy()
