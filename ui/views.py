"""Страницы приложения: представления готовых демосрезов и учебная интеграция."""

import csv
from html import escape
from io import StringIO
from pathlib import Path
import traceback

import streamlit as st

from demo.provider import get_sample_rows
from ui import charts
from ui.components import chart_heading, goto, heading, metric_card, money, plot
from ui.integration import call_user_loader, error_hint

ROOT = Path(__file__).resolve().parents[1]


def overview(data, fixture, metric):
    st.html('<div class="hero"><div class="eyebrow">EXPLORE YOUR NEXT MOVE</div><h1>Твоя карьера. В перспективе данных.</h1><p>Исследуй зарплаты, сравнивай направления и находи свой следующий шаг в IT.</p><div class="hero-tags"><span>Годовые зарплаты · USD</span><span>Интерактивная аналитика</span><span>Учебный проект</span></div></div>')
    st.html(f'<div class="context-line">Демосрез: <span>{escape(data["label"])}</span> &nbsp; / &nbsp; {escape(data["period"])} &nbsp; / &nbsp; Вымышленные значения</div>')
    stats = data["metrics"]
    for col, args in zip(st.columns(4), [
        ("Медианная зарплата", money(stats["median"]), "USD / год · готовое демозначение", "◈"),
        ("Средняя зарплата", money(stats["mean"]), "USD / год · готовое демозначение", "↗"),
        ("Записей в макете", f'{stats["records"]:,}'.replace(",", " "), "Условный объём выборки", "≡"),
        ("География", str(stats["countries"]), "Стран в выбранном демосрезе", "◎"),
    ]):
        with col:
            metric_card(*args)
    st.html('<div class="section-label">Зарплатный ландшафт</div><div class="section-caption">Наведи курсор на график, чтобы увидеть значения. Выдели область для увеличения.</div>')
    left, right = st.columns([1.12, 1])
    with left, st.container(border=True, key="trend-card"):
        chart_heading("Как меняются зарплаты", "История 2021–2025 · тот же регион и формат работы")
        plot(charts.salary_trend(data, fixture, metric), "overview_trend")
    with right, st.container(border=True, key="roles-card"):
        chart_heading("Специализации с высокими зарплатами", "Топ-7 · " + ("средняя" if metric == "mean" else "медианная") + " зарплата в год")
        plot(charts.top_roles(data, fixture, metric), "overview_roles")
    left, right = st.columns([1.12, 1])
    with left, st.container(border=True, key="distribution-card"):
        chart_heading("Распределение зарплат", "Готовая демонстрационная гистограмма")
        plot(charts.salary_distribution(data, fixture), "overview_histogram")
    with right, st.container(border=True, key="experience-card"):
        chart_heading("Опыт имеет значение", "Медиана, квартильный диапазон и границы · USD / год")
        plot(charts.experience_boxes(data, fixture), "overview_boxes")
    st.html(f'<div class="insight"><div class="insight-tag">CAREER NOTE</div><div class="insight-title">{escape(data["insight"])}</div><p>{escape(data["insight_text"])}</p></div>')


def roles(data, fixture, metric):
    heading("Найди своё направление", "Сравни специализации и посмотри, как опыт и компания меняют картину.", "ROLE EXPLORER")
    with st.container(border=True, key="role-explorer"):
        top_n = st.slider("Сколько специализаций показать", 3, 10, 10, key="top_n")
        chart_heading("Рейтинг специализаций", "Готовый деморейтинг · " + ("средняя" if metric == "mean" else "медианная") + " зарплата")
        plot(charts.top_roles(data, fixture, metric, top_n), "roles_full")
    left, right = st.columns([1, 1.15])
    with left, st.container(border=True, key="experience-card"):
        chart_heading("Диапазон зарплат по опыту", "Junior → Middle → Senior → Lead")
        plot(charts.experience_boxes(data, fixture), "roles_boxes")
    with right, st.container(border=True, key="heatmap-card"):
        chart_heading("Опыт × размер компании", "Тепловая карта · средняя зарплата, USD / год")
        plot(charts.company_heatmap(data, fixture), "roles_heatmap")


def work(data, fixture):
    heading("Работа в твоём ритме", "Офис, гибрид или удалёнка: исследуй готовые примеры распределений.", "WORK & LIFESTYLE")
    left, right = st.columns([0.85, 1.6])
    with left, st.container(border=True, key="work-card"):
        chart_heading("Формат работы", "Доли в выбранном демосрезе")
        plot(charts.work_donut(data), "work_donut")
    with right, st.container(border=True, key="scatter-card"):
        chart_heading("Зарплата и удалённость", "Пример точечного графика · цвет обозначает уровень опыта")
        plot(charts.remote_scatter(data, fixture), "work_scatter")
    for column, name, salary in zip(st.columns(3), ["Удалённо", "Гибрид", "Офис"], data["work_salary"]):
        with column:
            metric_card(name, money(salary) if salary is not None else "—", "Средняя в макете, USD / год" if salary is not None else "В этом срезе нет такой категории", "⌁")
    st.caption("Демонстрационные точки иллюстрируют вид графика. Связь между зарплатой и удалённостью ещё предстоит исследовать на твоих данных.")


def trends(data, fixture, metric):
    heading("Посмотри на большую картину", "История зарплат и динамика год к году для выбранных региона и формата работы.", "SALARY TRENDS")
    st.caption("На этой странице всегда показана история 2021–2025, даже если остальные разделы демосреза относятся только к 2025 году.")
    left, right = st.columns([1.3,1])
    with left, st.container(border=True, key="trend-card"):
        chart_heading("Зарплата по годам", "Средняя" if metric == "mean" else "Медиана")
        plot(charts.salary_trend(data,fixture,metric), "trends_line")
    with right, st.container(border=True, key="growth-card"):
        chart_heading("Рост средней зарплаты", "Год к году · заранее заданные демозначения")
        plot(charts.growth(data,fixture), "trends_growth")
    st.dataframe({"Год": fixture["years"], "Средняя, USD": data["trend_mean"], "Медиана, USD": data["trend_median"], "Рост средней, %": data["trend_growth"]}, hide_index=True, width="stretch", column_config={"Год": st.column_config.NumberColumn(format="%d")})
    st.caption("Для первого года рост не задан: в макете нет предыдущего года для сравнения.")


def sample_table(fixture, scenario):
    st.caption("Это небольшой вымышленный образец структуры данных. Показатели дашборда — отдельные готовые макеты и не рассчитаны из этих строк.")
    left, right = st.columns([1.4,1])
    query = left.text_input("Поиск по специализации", placeholder="Например, Data Engineer", key="sample_query")
    levels = right.multiselect("Уровень опыта", ["EN", "MI", "SE", "EX"], key="sample_levels", help="EN — Junior, MI — Middle, SE — Senior, EX — Lead. Пустой выбор означает все уровни.")
    rows = get_sample_rows(fixture, scenario, query, levels)
    if not rows:
        st.info("В демопримере нет совпадений. Измени поисковый запрос или уровень опыта.")
        return
    st.dataframe(rows, hide_index=True, width="stretch", column_config={
        "work_year": st.column_config.NumberColumn("Год", format="%d"),
        "job_title": "Специализация", "experience_level": "Опыт",
        "salary_in_usd": st.column_config.NumberColumn("USD / год", format="$ %d"),
        "remote_ratio": st.column_config.NumberColumn("Удалённость, %", format="%d"),
    }, column_order=["job_title","experience_level","salary_in_usd","work_year","employee_residence","remote_ratio","company_size","employment_type","salary","salary_currency","company_location"])
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(fixture["records"][0]))
    writer.writeheader()
    writer.writerows(rows)
    st.download_button("Скачать видимые демостроки", buffer.getvalue().encode("utf-8-sig"), file_name="career_explorer_DEMO.csv", mime="text/csv", icon=":material/download:")


def personal_data():
    st.caption("Таблица ниже появляется только из твоей функции. Демографики в остальных разделах пока используют вымышленные значения.")
    with st.container(border=True, key="load-card"):
        chart_heading("Подключи свой датасет", "Задание 1 · analysis/loader.py → load_dataset(path)")
        path_text = st.text_input("Путь к CSV или TXT", value="data/global_tech_salary.txt", key="dataset_path", help="Относительный путь считается от папки проекта. Можно указать абсолютный путь.")
        st.caption("Рядом с исходным документом датасета не было. Помести свой файл в data/ и реализуй функцию загрузки.")
        if st.button("Загрузить моим кодом", type="primary", icon=":material/upload_file:", key="load_user"):
            # При новой неудачной попытке старый результат не выдаётся за новый.
            st.session_state.pop("user_frame", None)
            st.session_state.pop("loaded_path", None)
            st.session_state["lesson_1_complete"] = False
            try:
                result = call_user_loader(path_text)
            except Exception as error:
                st.session_state["load_error"] = (error_hint(error), traceback.format_exc())
            else:
                st.session_state["user_frame"] = result
                st.session_state["loaded_path"] = path_text
                st.session_state["lesson_1_complete"] = True
                st.session_state.pop("load_error", None)
            st.rerun()
    if "load_error" in st.session_state:
        hint, details = st.session_state["load_error"]
        st.warning(hint)
        with st.expander("Технические детали ошибки"):
            st.code(details, language="text")
    if "user_frame" in st.session_state:
        st.success("Таблица получена из твоей функции. Первое задание подключено к интерфейсу.")
        st.caption(f"Показан результат последней успешной загрузки: {st.session_state['loaded_path']}. После изменения кода нажми кнопку загрузки снова.")
        st.dataframe(st.session_state["user_frame"], width="stretch", hide_index=True)
        st.info("Проверь названия столбцов: они должны быть разделены корректно. Затем покажи свою функцию в чате — разберём результат и перейдём дальше.")
    elif "load_error" not in st.session_state:
        st.info("Здесь появится твой DataFrame. Начни с одного небольшого шага — загрузки файла.")


def data_page(fixture, scenario):
    heading("От файла к исследованию", "Посмотри структуру демоданных или подключи результат своей первой функции.", "DATA WORKSPACE")
    mode = st.radio("Источник таблицы", ["Мои данные", "Демопример"], horizontal=True, key="data_mode", label_visibility="collapsed")
    if mode == "Мои данные":
        personal_data()
    else:
        sample_table(fixture, scenario)


def workshop():
    heading("Собери аналитику своими руками", "Один шаг за раз. Каждая твоя функция становится частью приложения.", "LEARNING STUDIO")
    left, right = st.columns([1.5, 1])
    with left, st.container(border=True, key="task-card"):
        done = st.session_state.get("lesson_1_complete", False)
        st.caption("ВЫПОЛНЕНО · результат подключён" if done else "ТЕКУЩЕЕ ЗАДАНИЕ · 01")
        st.subheader("Загрузи свой первый датасет")
        st.write("Приложению нужна таблица из файла. Реализуй функцию `load_dataset(path)` в `analysis/loader.py`.")
        st.markdown("**Вход:** путь к CSV/TXT-файлу.  \n**Результат:** `pandas.DataFrame` с содержимым файла.  \n**Зачем:** это источник данных для будущего исследования.")
        st.write("Помести файл в data/, посмотри его разделитель, напиши функцию и сохрани изменения. Пока достаточно только загрузки.")
        st.code("load_dataset(path) → pandas.DataFrame", language="text")
        st.button("Открыть мои данные", icon=":material/arrow_forward:", type="primary", on_click=goto, args=("Мои данные",), key="task_open_data")
        with st.expander("Первая подсказка"):
            st.write("Найди в Pandas функцию для чтения текстовой таблицы. Обрати внимание на разделитель и помни: показать таблицу через print и вернуть её из функции — разные действия.")
        with st.expander("Как понять, что получилось"):
            st.write("После кнопки «Загрузить моим кодом» появилась таблица с отдельными столбцами и понятными заголовками. Покажи свою функцию в чате, чтобы мы проверили результат.")
    with right:
        chart_heading("Маршрут исследования", "Разделы лабораторной · задания будем открывать постепенно")
        for number, title, description in [
            ("01", "Знакомство с данными", "Сейчас: загрузка файла"),
            ("02", "Преобразования таблиц", "Следующий блок лабораторной"),
            ("03", "Группировки и сравнения", "После предыдущего блока"),
            ("04", "Визуальное исследование", "Твои результаты на графиках"),
            ("05", "Изменения во времени", "Тренды и динамика зарплат"),
        ]:
            st.html(f'<div class="lesson-step"><span class="step-num">{number}</span><div><div class="step-title">{title}</div><div class="step-desc">{description}</div></div></div>')
        st.caption("Ты пишешь Python и Pandas. Я создаю интерфейс, подключаю твои функции и помогаю подсказками.")
    with st.expander("О проекте и демонстрации"):
        st.write("Основано на Lab 12: загрузка, преобразования, агрегации, графики и временные ряды. Все текущие графики используют вручную подготовленные вымышленные результаты. Демо не содержит решения аналитических заданий.")
        st.markdown("Справочники интерфейса: [Streamlit](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart), [Plotly](https://plotly.com/python/).")
        st.caption("Прогресс первого задания хранится только в текущей сессии браузера. Твой код и датасет остаются на диске.")
