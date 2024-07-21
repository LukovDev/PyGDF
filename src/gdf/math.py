#
# math.py - Содержит импорты математических библиотек.
#


# Импортируем:
if True:
    import glm
    import math
    import numpy
    import numba
    import random
    from glm import *
    from math import *

    # Удаляем округление от glm:
    del round


# Класс двумерного вектора:
class vec2(glm.vec2): pass

# Класс трехмерного вектора:
class vec3(glm.vec3): pass

# Класс четырёхмерного вектора:
class vec4(glm.vec4): pass


# Килограмм в ньютонах:
KG_N = 9.80665


# Бесконечность:
INF = float("inf")
