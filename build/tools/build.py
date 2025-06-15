#
# build.py - Компилирует вашу программу в бинарный файл при помощи pyinstaller.
#
# log-level: TRACE, DEBUG, INFO, WARN, ERROR, FATAL
#


# Импортируем:
import os
import sys
import json
import time
import site
import glob
import shutil
from importlib import resources
from threading import Thread


# Переменные (НЕ НАСТРАИВАЕМЫЕ):
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
wait_active   = True
wait_text     = "> wait... "
wait_text_len = len(wait_text)+1


# Ожидание:
def waiting() -> None:
    symbols = r"/─\|"
    while wait_active:
        for s in symbols:
            if not wait_active: continue
            print("\r"+wait_text+s, end="")
            time.sleep(0.1)


# Очищаем консоль:
def clear_console() -> None:
    if sys.platform == "win32":
        os.system("cls")
    elif sys.platform == "darwin":
        print("\033c", end="")
    else: os.system("clear")


# Основная функция:
def main() -> None:
    global wait_active, wait_text_len

    clear_console()  # Очищаем консоль.

    # Читаем конфигурационный файл сборки:
    with open("../config.json", "r+", encoding="utf-8") as f: config = json.load(f)

    # Преобразование данных конфигурации в переменные:
    main_file         = config["main-file"]
    program_icon      = config["program-icon"]
    program_name      = config["program-name"]
    console_disabled  = config["console-disabled"]
    data_folder       = config["data-folder"]
    pyinstaller_flags = config["pyinstaller-flags"]
    lg                = "--log-level "
    waiting_enabled   = any(flag in pyinstaller_flags for flag in [lg+"WARN", lg+"ERROR", lg+"FATAL"])
    path_separ        = ";" if sys.platform == "win32" else ":"

    # Отдельный поток для вывода ожидания:
    waiting_thread = Thread(target=waiting, daemon=True)
    if not waiting_enabled: wait_text_len = 0

    # Поиск gdf-ядра:
    gdf_path = ""
    for site_package in site.getsitepackages():
        matching_folders = glob.glob(os.path.join(site_package, "gdf"))
        if matching_folders: gdf_path = matching_folders[0]; break
    else: gdf_path = glob.glob("../../src/**/gdf", recursive=True)[0]

    # Генерация флагов компиляции:
    pyogg_data = f"{resources.files('pyogg')}{path_separ}pyogg"
    flags = f"--noconfirm --add-data \"{pyogg_data}\" -n=\"{program_name}\" --exclude-module setuptools.msvc "
    for flag in pyinstaller_flags: flags += f"{flag} "
    if console_disabled:           flags +=  "--noconsole " if sys.platform == "win32" else "--noconsole --windowed "
    if program_icon is not None:   flags += f"--icon=../../{program_icon} "

    # Добавляем папку библиотек звука в сборку в случае если сборка для MacOS. Потому что библиотеки OpenAL на маке нет:
    if sys.platform == "darwin": flags += f"--add-data \"{os.path.join(gdf_path, 'audio/')}{path_separ}gdf/audio/\""

    # Собираем проект:
    print(f"{' COMPILATION PROJECT ':─^80}\n")
    if waiting_enabled: waiting_thread.start()

    pyinst = "python3 -m PyInstaller" if sys.platform == "darwin" else "pyinstaller"
    os.system(f"{pyinst} {flags} ../../{main_file}")

    print(f"\r{' '*wait_text_len}\n> COMPILATION IS SUCCESSFUL!\n\n{'─'*80}\n\n")

    # Удаляем мусор и собираем всё в одну папку:
    print("Deleting temporary build files...")

    # Удаляем прочие лишние файлы и папки:
    if os.path.isdir("../out/"): shutil.rmtree("../out/")
    if os.path.isdir("build"): shutil.rmtree("build")
    for file in os.listdir():
        if file.endswith(".spec"): os.remove(file)

    # Копируем папку с данными:
    print("\n\n\nCopying the data folder...")

    # Копируем содержимое сборки и содержимое data папки в папку out:
    if os.path.isdir("dist/"):
        flags_list = flags.split()
        build_for_macos_app = sys.platform == "darwin" and console_disabled

        # Если это макос и программа собирается в один файл, копируем только пакет программы:
        if build_for_macos_app and ("--onefile" in flags_list or "-F" in flags_list):
            shutil.copytree(f"dist/{program_name}.app", f"../out/{program_name}.app", dirs_exist_ok=True)
        else: shutil.copytree("dist/", "../out/", dirs_exist_ok=True)
        shutil.rmtree("dist/")

        # Копируем папку данных в папку out либо если это макос и собираем в один файл, то в пакет программы:
        data_folder_name = os.path.basename(os.path.normpath(data_folder))
        macappdir = f"../out/{program_name}.app/Contents/MacOS/{data_folder_name}"
        shutil.copytree(f"../../{data_folder}", macappdir if build_for_macos_app else f"../out/{data_folder_name}")

    wait_active = False
    print("\rDone!"+' '*wait_text_len)

    print("\n\nOutput of build in folder: build/out/")


# Если этот скрипт запускают:
if __name__ == "__main__":
    main()
