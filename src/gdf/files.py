#
# files.py - Позволяет работать с файлами.
#


# Импортируем:
if True:
    import json
    import zipfile
    import tkinter as tk
    from tkinter import filedialog
    from .audio import Music, Sound
    from .graphics import Image, Texture, Sprite


# Класс исключения:
class IgnoreException(Exception): pass


# Загружаем изображение:
def load_image(file_path: str) -> Image: return Image().load(file_path)


# Сохраняем изображение:
def save_image(file_path: str, image: Image) -> bool:
    try: image.save(file_path)
    except IgnoreException: return False
    return True


# Загружаем текстуру:
def load_texture(file_path: str, is_flip_y: bool = False) -> Texture:
    return Texture(Image().load(file_path), is_flip_y)


# Сохраняем текстуру:
def save_texture(file_path: str, texture: Texture) -> bool:
    try: texture.image.save(file_path)
    except IgnoreException: return False
    return True


# Загружаем текстуру, а потом превращаем в спрайт:
def load_sprite(file_path: str, is_flip_y: bool = False) -> Sprite:
    return Sprite(load_texture(file_path, is_flip_y))


# Загружаем музыку:
def load_music(file_path: str) -> Music:
    return Music().load(file_path)


# Загружаем звук:
def load_sound(file_path: str) -> Sound:
    return Sound().load(file_path)


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


# Создаем zip-файл и добавляем файлы и папки из списка:
def create_zip_file(file_path: str, file_folder_list: list) -> None:
    with zipfile.ZipFile(file_path, "w") as zipf:
        for item in file_folder_list:
            if os.path.isfile(item):
                zipf.write(item, os.path.basename(item))
            elif os.path.isdir(item):
                for root, dirs, files in os.walk(item):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, os.path.join(item, "..")))


# Извлекаем файлы из zip-файла:
def extract_zip_file(file_path: str, output_dir: str) -> None:
    with zipfile.ZipFile(file_path, "r") as zf:
        zf.extractall(output_dir)


# Выбрать файл:
def get_file_path_gialog(file_types: list[tuple] = [("all files:" "*.*")], icon_path: str = "") -> str:
    root = tk.Tk() ; root.withdraw()
    try: root.iconbitmap(icon_path)
    except Exception as error: pass
    if file_types: fp = filedialog.askopenfilename(filetypes=file_types)
    else: fp = filedialog.askopenfilename()
    root.destroy()
    return fp
