#
# gl.py - Объединяет определённые импорты OpenGL.
#


# Импортируем:
from OpenGL import GL as gl
from OpenGL import GLU as glu
from OpenGL.GL import shaders as gls


# Установить режим смешивания:
def gl_set_blend_mode(sfactor: int = None, dfactor: int = None) -> None:
    """ Подсказка:
        Все возможные режимы для sfactor и dfactor функции glBlendFunc():
        DST - Существующий пиксель.
        SRC - Накладываемый пиксель.

        1.  GL_ZERO:                Фактор равен нулю.
        2.  GL_ONE:                 Фактор равен единице.
        3.  GL_SRC_COLOR:           Фактор равен цвету источника.
        4.  GL_DST_COLOR:           Фактор равен цвету приемника.
        5.  GL_SRC_ALPHA:           Фактор равен альфа-каналу источника.
        6.  GL_DST_ALPHA:           Фактор равен альфа-каналу приемника.
        7.  GL_ONE_MINUS_SRC_COLOR: Фактор равен единице минус цвет источника.
        8.  GL_ONE_MINUS_DST_COLOR: Фактор равен единице минус цвет приемника.
        9.  GL_ONE_MINUS_SRC_ALPHA: Фактор равен единице минус альфа-канал источника.
        10. GL_ONE_MINUS_DST_ALPHA: Фактор равен единице минус альфа-канал приемника.
    """

    # Простой режим смешивания. Альфа канал из фрагмента будет использоваться как коэффициент смешивания:
    sfactor = gl.GL_SRC_ALPHA           if sfactor is None else sfactor
    dfactor = gl.GL_ONE_MINUS_SRC_ALPHA if dfactor is None else dfactor

    # Устанавливаем режим:
    gl.glBlendFunc(sfactor, dfactor)
