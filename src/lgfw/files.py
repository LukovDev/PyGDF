#
# files.py - Позволяет работать с файлами.
#


# Импортируем:
if True:
    import json
    import tkinter as tk
    from tkinter import filedialog
    from .graphics import Image, Texture


# Класс исключения:
class IgnoreException(Exception): pass


# Загружаем изображение:
def load_image(file_path: str) -> Image: return Image(file_path)


# Сохраняем изображение:
def save_image(file_path: str, image: Image) -> bool:
    try: image.save(file_path)
    except IgnoreException: return False
    return True


# Загружаем текстуру:
def load_texture(file_path: str, is_flip_y: bool = False) -> Texture:
    return Texture(Image(file_path), is_flip_y)


# Сохраняем текстуру:
def save_texture(file_path: str, texture: Texture) -> bool:
    try: texture.image.save(file_path)
    except IgnoreException: return False
    return True


# Загружаем файл:
def load_file(file_path: str, mode: str = "r+", encoding: str = "utf-8") -> str:
    with open(file_path, mode, encoding=encoding) as f: return str(f.read())


# Сохраняем файл:
def save_file(file_path: str, data: str, mode: str = "w+", encoding: str = "utf-8") -> None:
    with open(file_path, mode, encoding=encoding) as f: f.write(data)


# Загружаем json файл:
def load_json(file_path: str, mode: str = "r+", encoding: str = "utf-8") -> dict:
    with open(file_path, mode, encoding=encoding) as f: return dict(json.load(f))


# Сохраняем json файл:
def save_json(file_path: str, data: dict, mode: str = "w+", encoding: str = "utf-8", indent: int = 4) -> None:
    with open(file_path, mode, encoding=encoding) as f: json.dump(data, f, indent=indent)


# Выбрать файл:
def get_file_path(file_types: list[tuple] = [("All:" "*.*")], icon_path: str = "") -> str:
    root = tk.Tk() ; root.withdraw()
    try: root.iconbitmap(icon_path)
    except Exception as error: pass
    if file_types: fp = filedialog.askopenfilename(filetypes=file_types)
    else: fp = filedialog.askopenfilename()
    root.destroy()
    return fp
