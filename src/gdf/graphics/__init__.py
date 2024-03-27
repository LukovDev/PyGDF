#
# graphics - Содержит скрипты отвечающие за графику.
#


# Импортируем:
if True:
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

    import pygame
    from pygame import constants as Key
    from pygame import constants as Event

    # Импортируем скрипты:
    from . import atlas
    from . import batch
    from . import buffers
    from . import camera
    from . import draw
    from . import font
    from . import gl
    from . import image
    from . import packer
    from . import particles
    from . import shader
    from . import skybox
    from . import sprite
    from . import texture
    from . import window

    # Импортируем основной функционал из скриптов:
    from .atlas     import AtlasTexture
    from .batch     import SpriteBatch, AtlasTextureBatch
    from .buffers   import SSBO, FrameBuffer
    from .camera    import Camera2D, Camera3D
    from .draw      import Draw2D, Draw3D
    from .font      import Font, SysFont, get_fonts, match_font
    from .image     import Image
    from .packer    import PackerTexture
    from .particles import ParticleEffect2D
    from .shader    import ShaderProgram, ComputeShaderProgram
    from .skybox    import SkyBox
    from .sprite    import Sprite
    from .texture   import Texture
    from .window    import Window
