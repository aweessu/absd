"""Адаптер интерфейса. Вызывает код пользователя, но не решает его задачи."""

from pathlib import Path
import runpy

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def call_user_loader(path_text):
    """Перечитать функцию с диска, вызвать её, проверить контракт результата."""
    if not path_text.strip():
        raise ValueError("Укажи путь к файлу с датасетом.")
    path = Path(path_text.strip()).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    # run_path видит сохранённые изменения без перезапуска сервера.
    namespace = runpy.run_path(str(ROOT / "analysis" / "loader.py"))
    loader = namespace.get("load_dataset")
    if not callable(loader):
        raise TypeError("В analysis/loader.py должна быть функция load_dataset(path).")
    result = loader(str(path))
    if not isinstance(result, pd.DataFrame):
        raise TypeError("Ожидается pandas.DataFrame. Проверь, возвращает ли функция таблицу через return.")
    if result.empty:
        raise ValueError("Функция вернула пустой DataFrame. Проверь выбранный файл и способ чтения.")
    return result


def error_hint(error):
    """Подсказка без готового решения и без изменения пользовательского кода."""
    if isinstance(error, NotImplementedError):
        return "Сначала реализуй load_dataset(path) в analysis/loader.py и сохрани файл. Затем нажми кнопку ещё раз."
    if isinstance(error, FileNotFoundError):
        return "Файл не найден. Сравни путь в поле с реальным именем файла и проверь его расширение."
    if isinstance(error, UnicodeDecodeError):
        return "Не удалось прочитать символы файла. Подумай, в какой кодировке он сохранён."
    if isinstance(error, pd.errors.ParserError):
        return "Не удалось разделить строки на столбцы. Посмотри первые строки файла: совпадает ли разделитель с выбранным при чтении?"
    if isinstance(error, SyntaxError):
        return "Python не смог прочитать код. Проверь двоеточие, скобки и отступы около строки, указанной в деталях."
    if isinstance(error, NameError):
        return "Python не знает одно из имён. Проверь импорт библиотеки и написание переменных."
    if isinstance(error, (TypeError, ValueError)):
        return str(error)
    return "Загрузка остановилась. Посмотри тип ошибки и строку в деталях; попробуй объяснить, что ожидала эта операция. Код остался без изменений."
