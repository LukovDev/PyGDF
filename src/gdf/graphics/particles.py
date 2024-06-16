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
            texture      = particle_texture,
            position     = vec2(0, 0),
            direction    = vec2(0, 0),
            size         = vec2(1, 1),
            speed        = vec2(1, 3),
            damping      = 0.01,
            duration     = vec2(1, 2),
            count        = 128,
            gravity      = vec2(0, 0),
            is_infinite  = False,
            is_local_pos = False,
            is_dir_angle = False,
            angle_offset = 0.0
        ).create()
    """

    # Частица:
    class Particle:
        def __init__(self,
                     texture:  Texture | list,
                     position: vec2,
                     velocity: vec2,
                     size:     vec2,
                     time:     float
                     ) -> None:
            self.texture  = texture
            self.position = position
            self.velocity = velocity
            self.size     = size
            self.time     = time

        # Скорость перемещения частицы:
        @property
        def speed(self) -> float: return Utils2D.get_speed_vector(self.velocity)

    # Инициализация:
    def __init__(self,
                 texture:      Texture | list,
                 position:     vec2,
                 direction:    vec2,
                 size:         vec2,
                 speed:        vec2,
                 damping:      float,
                 duration:     vec2,
                 count:        int,
                 gravity:      vec2,
                 is_infinite:  bool  = True,
                 is_local_pos: bool  = False,
                 is_dir_angle: bool  = True,
                 angle_offset: float = 0.0
                 ) -> None:
        # Параметры отображения:
        self.texture      = texture         # Текстура частиц.
        self.is_dir_angle = is_dir_angle    # Поворачивать ли частицу в сторону направления движения.
        self.angle_offset = angle_offset    # Смещения угла поворота частицы.

        # Параметры частиц:
        self.position     = position        # Позиция эффекта частиц.
        self.direction    = direction       # Вектор направления частиц.
        self.size         = size            # Размер частиц.
        self.speed        = speed           # Начальная скорость частицы. Случайно от X до Y.
        self.damping      = damping         # Сила затухания скорости частицы.
        self.duration     = duration        # Сколько должна жить частица (в секундах). Случайно от X до Y.

        # Прочие параметры:
        self.count        = count           # Количество частиц.
        self.gravity      = gravity         # Сила гравитации на частицы.
        self.is_infinite  = is_infinite     # Бесконечные ли частицы.
        self.is_local_pos = is_local_pos    # Частицы в локальном пространстве.

        # Внутренние переменные класса:
        self.batch       = SpriteBatch2D()  # Пакетная отрисовка.
        self.__old_pos__ = position.xy      # Старая позиция
        self.__timer__   = 0.0              # Счётчик отсчитывающий время для создания новой частицы.
        self.particles   = None             # Список частиц.

    # Создать одну частицу. Используется строго внутри этого класса:
    def __create_particle__(self) -> None:
        a = random.uniform(0, 2*math.pi)  # Случайный угол.
        rdir = vec2(sin(a), cos(a))       # Случайный вектор.

        ptxt = self.texture if type(self.texture) is Texture else random.choice(self.texture)
        ppos = self.position.xy
        pvel = normalize(rdir+self.direction) * random.uniform(*self.speed.xy)
        psiz = self.size.xy
        ptfl = random.uniform(*self.duration.xy)

        # Частица:
        particle = SimpleParticleEffect2D.Particle(
            ptxt,  # Текстура частицы.
            ppos,  # Позиция.
            pvel,  # Вектор направления и скорости.
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
        dt = min(delta_time, 1/5)*60

        # Если количество частиц меньше установленного, создаём новые:
        if len(self.particles) < self.count and self.is_infinite:
            self.__timer__ -= delta_time
            while self.__timer__ <= 0.0:
                self.__create_particle__()
                self.__timer__ += (sum(self.duration) / 2) / self.count

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
            particle.velocity *= 1-(self.damping)

            # Перемещаем частичку в сторону её направления умноженное на её скорость:
            particle.position += normalize(particle.velocity) * particle.speed * dt
            if self.is_local_pos: particle.position += self.position - self.__old_pos__

        self.__old_pos__.xy = self.position.xy
        return self

    # Отрисовка частиц:
    def render(self, color: list = None) -> "SimpleParticleEffect2D":
        # Проходимся по частицам:
        self.batch.begin()
        for particle in self.particles:
            angl = Utils2D.get_angle_points(vec2(0), normalize(particle.velocity)) + 90 if self.is_dir_angle else 0.0

            # Рисуем частицу:
            self.batch.draw(
                sprite = particle.texture,
                x      = particle.position.x - (particle.size.x/2),
                y      = particle.position.y - (particle.size.y/2),
                width  = particle.size.x,
                height = particle.size.y,
                angle  = angl + self.angle_offset
            )
        self.batch.end()

        self.batch.render(color)
        return self

    # Удалить систему частиц:
    def destroy(self) -> None:
        if self.texture is None: return
        self.texture.destroy()
