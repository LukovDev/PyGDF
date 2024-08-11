#
# math.py - Содержит импорты математических библиотек.
#


# Импортируем:
import glm
import math
import numpy
import random
import decimal
from glm import *
from math import *


# Удаляем округление от glm:
del round


# Класс чисел двойной точности:
class double:
    limit = 1e+308  # Лимит максимального значения для x64 систем. Значение большее лимита превращается в бесконечность.
    decimal.getcontext().prec = 308  # 308 это максимальная точность (и размер) для x64 систем.

    def __init__(self, value):
        try:
            self._value_ = value._value_ if isinstance(value, double) else decimal.Decimal(value)
        except (decimal.Overflow, OverflowError):
            self._value_ = decimal.Decimal("inf" if value >= 0 else "-inf")
        except TypeError:
            raise TypeError(f"Your data type ({type(value)}) is not supported.")

    # Дополнительная информация об этом объекте:
    def __repr__(self) -> str:
        return f"double({self._value_})"

    # Преобразовать значение в строку:
    def __str__(self) -> str:
        if   self._value_ == decimal.Decimal("inf"):  return "inf"
        elif self._value_ == decimal.Decimal("-inf"): return "-inf"
        return str(self._value_)

    # Преобразовать значение в float:
    def __float__(self) -> float:
        return float(self._value_)

    # Преобразовать значение в int:
    def __int__(self) -> int:
        return int(self._value_)

    # Преобразовать значение в bool:
    def __bool__(self) -> bool:
        return bool(self._value_)

    # Сложить значение к значению:
    def __add__(self, other) -> double:
        try:
            return self._operation_(self._value_ + self._convert_(other))
        except (decimal.InvalidOperation, decimal.Overflow, OverflowError):
            return double("inf" if self._value_ >= 0 else "-inf")

    # Вычесть значение к значению:
    def __sub__(self, other) -> double:
        try:
            return self._operation_(self._value_ - self._convert_(other))
        except (decimal.InvalidOperation, decimal.Overflow, OverflowError):
            return double("inf" if self._value_ >= 0 else "-inf")

    # Умножить значение на значение:
    def __mul__(self, other) -> double:
        try:
            return self._operation_(self._value_ * self._convert_(other))
        except (decimal.InvalidOperation, decimal.Overflow, OverflowError):
            return double("inf" if self._value_ >= 0 else "-inf")

    # Делить значение на значение:
    def __truediv__(self, other) -> double:
        try:
            return self._operation_(self._value_ / self._convert_(other))
        except (decimal.DivisionByZero, decimal.InvalidOperation, decimal.Overflow, OverflowError):
            return double("inf" if self._value_ >= 0 else "-inf")

    # Целочисленное деление значения на значение:
    def __floordiv__(self, other) -> double:
        try:
            return self._operation_(self._value_ // self._convert_(other))
        except (decimal.InvalidOperation, decimal.Overflow, OverflowError):
            return double("inf" if self._value_ >= 0 else "-inf")

    # Остаток от деления значения на значение:
    def __mod__(self, other) -> double:
        try:
            return self._operation_(self._value_ % self._convert_(other))
        except (decimal.DivisionByZero, decimal.InvalidOperation, decimal.Overflow, OverflowError):
            return double("inf" if self._value_ >= 0 else "-inf")

    # Возведение в степень значения на значение:
    def __pow__(self, other) -> double:
        try:
            return self._operation_(self._value_ ** self._convert_(other))
        except (decimal.InvalidOperation, decimal.Overflow, OverflowError):
            return double("inf" if self._value_ >= 0 else "-inf")

    # Сравнивает два объекта на равенство:
    def __eq__(self, other) -> bool:
        if isinstance(other, double):
            return self._value_ == other._value_
        return self._value_ == decimal.Decimal(other)

    # Сравнивает, меньше ли текущий объект, чем другой:
    def __lt__(self, other) -> bool:
        if isinstance(other, double):
            return self._value_ < other._value_
        return self._value_ < decimal.Decimal(other)

    # Сравнивает, меньше ли текущий объект или равен другому:
    def __le__(self, other) -> bool:
        if isinstance(other, double):
            return self._value_ <= other._value_
        return self._value_ <= decimal.Decimal(other)

    # Сравнивает, больше ли текущий объект, чем другой:
    def __gt__(self, other) -> bool:
        if isinstance(other, double):
            return self._value_ > other._value_
        return self._value_ > decimal.Decimal(other)

    # Сравнивает, больше ли текущий объект или равен другому:
    def __ge__(self, other) -> bool:
        if isinstance(other, double):
            return self._value_ >= other._value_
        return self._value_ >= decimal.Decimal(other)

    # Возвращает объект с отрицательным значением:
    def __neg__(self) -> double:
        return double(-self._value_)

    # Возвращает объект с положительным значением (по умолчанию):
    def __pos__(self) -> double:
        return self

    # Возвращает объект с абсолютным значением:
    def __abs__(self) -> double:
        return double(abs(self._value_))

    # Округляет значение до n знаков после запятой:
    def __round__(self, n: int = 0) -> double:
        try:
            return double(self._value_.quantize(decimal.Decimal(f"1e-{n}"), rounding=decimal.ROUND_HALF_UP))
        except decimal.InvalidOperation:
            return double("inf" if self._value_ >= 0 else "-inf")

    # Округляет значение до целого числа в сторону нуля:
    def __trunc__(self) -> int:
        return int(self._value_)

    # Округляет значение вниз до ближайшего целого числа:
    def __floor__(self) -> int:
        return int(self._value_.to_integral_value_(decimal.ROUND_FLOOR))

    # Округляет значение вверх до ближайшего целого числа:
    def __ceil__(self) -> int:
        return int(self._value_.to_integral_value_(decimal.ROUND_CEILING))

    # Возвращает хеш объекта:
    def __hash__(self) -> int:
        return hash(float(self))

    # Форматирует объект как строку согласно указанному формату:
    def __format__(self, format_spec) -> str:
        return format(float(self), format_spec)

    # Проверяет, превышает ли результат арифметической операции заданный лимит:
    def _operation_(self, result) -> double:
        if abs(result) > decimal.Decimal(double.limit):
            return double("inf") if result > 0 else double("-inf")
        return double(result)

    # Преобразует другой объект типа double или значение в тип decimal.Decimal:
    def _convert_(self, other) -> decimal.Decimal:
        return other._value_ if isinstance(other, double) else decimal.Decimal(other)


# Класс двумерного вектора:
class vec2(glm.vec2): pass


# Класс трехмерного вектора:
class vec3(glm.vec3): pass


# Класс четырёхмерного вектора:
class vec4(glm.vec4): pass


# Килограмм в ньютонах:
KG_N = 9.80665
