#
# files.py - Позволяет работать с файлами.
#


# Импортируем:
import os
import json
import pygame
import zipfile
import requests
import tkinter as tk
from tkinter import filedialog
from .audio import Music, Sound
from .graphics.font import FontFile
from .graphics import Image, Texture, Sprite2D


# Загружаем изображение:
def load_image(file_path: str) -> Image:
    return Image((0, 0)).load(file_path)


# Сохраняем изображение:
def save_image(file_path: str, image: Image) -> None:
    image.save(file_path)


# Загружаем текстуру:
def load_texture(file_path: str, is_flip_y: bool = False) -> Texture:
    return Texture(Image((0, 0)).load(file_path), is_flip_y)


# Сохраняем текстуру:
def save_texture(file_path: str, texture: Texture) -> None:
    image = pygame.image.frombuffer(texture.get_data().tobytes(), (texture.width, texture.height), "RGBA")
    pygame.image.save(image, file_path)


# Загружаем файл:
def load_file(file_path: str, mode: str = "r+", encoding: str = "utf-8") -> str:
    with open(file_path, mode, encoding=encoding) as f: return str(f.read())


# Сохраняем файл:
def save_file(file_path: str, data: str, mode: str = "w+", encoding: str = "utf-8") -> None:
    with open(file_path, mode, encoding=encoding) as f: f.write(data)


# Загружаем json файл:
def load_json(file_path: str, mode: str = "r+", encoding: str = "utf-8") -> dict | list:
    with open(file_path, mode, encoding=encoding) as f: return json.load(f)


# Сохраняем json файл:
def save_json(file_path: str, data: dict | list, mode: str = "w+", encoding: str = "utf-8", indent: int = 4) -> None:
    with open(file_path, mode, encoding=encoding) as f: json.dump(data, f, indent=indent)


# Загружаем текстуру, а потом превращаем в спрайт:
def load_sprite(file_path: str, is_flip_y: bool = False) -> Sprite2D:
    return Sprite2D(load_texture(file_path, is_flip_y))


# Загружаем музыку:
def load_music(file_path: str) -> Music:
    return Music().load(file_path)


# Загружаем звук:
def load_sound(file_path: str) -> Sound:
    return Sound().load(file_path)


# Загрузить файл шрифта:
def load_font(file_path: str) -> FontFile:
    return FontFile(file_path).load()


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
def get_file_path_dialog(file_types: list[tuple] = [("all files:" "*.*")], icon_path: str = "") -> str:
    root = tk.Tk() ; root.withdraw()
    try: root.iconbitmap(icon_path)
    except Exception as error: pass
    if file_types: fp = filedialog.askopenfilename(filetypes=file_types)
    else: fp = filedialog.askopenfilename()
    root.destroy()
    return fp


# Получить содержимое файла из интернета по ссылке:
def read_url_file(url: str, chunk_size: int = 8192) -> str:
    data = ""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=chunk_size): data += chunk.decode()
    return data


# Получить содержимое json файла из интернета по ссылке:
def read_url_json(url: str, chunk_size: int = 8192) -> dict:
    return json.loads(read_url_file(url, chunk_size))


# Скачать файл из интернета по ссылке:
def download_url_file(url: str, file_path: str, chunk_size: int = 8192) -> None:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
