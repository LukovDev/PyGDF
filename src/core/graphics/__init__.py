#
# graphics - Содержит скрипты отвечающие за графику.
#


# Импортируем:
if True:
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    from pygame import constants as key
    import pygame

    # Импортируем скрипты:
    from . import batch
    from . import camera
    from . import draw
    from . import font
    from . import gl
    from . import image
    from . import mesh
    from . import shader
    from . import skybox
    from . import sprite
    from . import texture
    from . import window

    # Импортируем основной функционал из скриптов:
    from .batch   import SpriteBatch
    from .camera  import Camera2D, Camera3D
    from .draw    import Draw2D
    from .font    import Font, SysFont, get_fonts, match_font
    from .image   import Image
    from .mesh    import BaseMesh
    from .shader  import ShaderProgram, ComputeShaderProgram
    from .skybox  import SkyBox
    from .sprite  import Sprite
    from .texture import Texture
    from .window  import Window
