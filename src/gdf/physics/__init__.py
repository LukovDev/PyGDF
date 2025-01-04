#
# physics - Содержит скрипты отвечающие за физику.
#


# Импортируем:
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


# Утилиты написанные на Cython:
try:
    from .physics_utils import (
        _p2d_mesh_create_segments_from_verts_,
        _p2d_mesh_get_vertices_,
        _p2d_collision_handler_begin_,
        _p2d_collision_handler_end_,
        _p2d_space_object_query_,
        _p2d_space_find_near_object_,
        _p2d_space_find_objects_,
    )
except (ModuleNotFoundError, ImportError) as error:
    raise Exception(f"The compiled module could not be imported: {error}")


# Импортируем скрипты:
from . import phys2d


# Импортируем основной функционал из скриптов:
from .phys2d import Physics2D, PhysicsError
