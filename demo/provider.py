"""Чтение готовых UI-макетов. Здесь намеренно нет Pandas и агрегаций.

Сводки записаны вручную в fixtures.json. Таблица — отдельный образец
структуры, а не исходные строки для расчёта демонстрационных сводок.
"""

import json
from pathlib import Path

FIXTURES = Path(__file__).with_name("fixtures.json")


def get_fixtures():
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def get_sample_rows(fixtures, scenario, query="", levels=()):
    """Только поиск по вымышленным карточкам для демонстрации UI-фильтров."""
    rows = fixtures["records"]
    if scenario == "us":
        rows = [row for row in rows if row["employee_residence"] == "US" and row["work_year"] == 2025]
    elif scenario == "europe":
        rows = [row for row in rows if row["employee_residence"] in {"DE", "GB", "ES", "FR", "NL", "PL"} and row["work_year"] == 2025]
    elif scenario == "remote":
        rows = [row for row in rows if row["remote_ratio"] == 100 and row["work_year"] == 2025]
    if levels:
        rows = [row for row in rows if row["experience_level"] in levels]
    if query.strip():
        rows = [row for row in rows if query.strip().casefold() in row["job_title"].casefold()]
    return rows
