"""IT Career Explorer — запуск интерфейса, без аналитических решений."""

from html import escape

import streamlit as st

from demo.provider import get_fixtures
from ui.components import footer, goto, setup_style
from ui import views

st.set_page_config(page_title="IT Career Explorer", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
setup_style()
fixture = get_fixtures()

PAGES = ["Обзор рынка", "Специализации", "Формат работы", "Динамика зарплат", "Мои данные", "Мастерская"]
LABELS = {"Обзор рынка":"◈  Обзор рынка", "Специализации":"⌘  Специализации", "Формат работы":"◎  Формат работы", "Динамика зарплат":"↗  Динамика зарплат", "Мои данные":"▤  Мои данные", "Мастерская":"◇  Мастерская"}


def reset_demo():
    st.session_state["scenario"] = "global"
    st.session_state["salary_metric"] = "Средняя"
    st.session_state["sample_query"] = ""
    st.session_state["sample_levels"] = []
    st.session_state["top_n"] = 10


with st.sidebar:
    st.html('<div class="brand"><div class="brand-mark">↗</div><div><div class="brand-title">IT Career Explorer</div><div class="brand-sub">MAKE YOUR NEXT MOVE</div></div></div>')
    st.html('<div class="side-label">ИССЛЕДОВАНИЕ</div>')
    page = st.radio("Навигация", PAGES, format_func=lambda value: LABELS[value], key="page", label_visibility="collapsed")
    st.html('<div class="side-label">ФИЛЬТРЫ ДЕМОНСТРАЦИИ</div>')
    scenario = st.selectbox("Готовый срез", options=list(fixture["scenarios"]), format_func=lambda value: fixture["scenarios"][value]["label"], key="scenario", help="Переключает заранее подготовленные вымышленные результаты. Произвольные фильтры настоящего DataFrame подключим после твоих заданий.")
    metric_label = st.radio("Показатель графиков", ["Средняя", "Медиана"], horizontal=True, key="salary_metric", help="Меняет рейтинг специализаций и линию зарплат. Остальные графики имеют свои подписи.")
    st.button("Сбросить фильтры", icon=":material/restart_alt:", width="stretch", on_click=reset_demo, key="reset_demo")
    data = fixture["scenarios"][scenario]
    st.caption(f'{data["geography"]} · {data["period"]}  \n{data["format"]} · USD / год')
    done = st.session_state.get("lesson_1_complete", False)
    st.html(f'<div class="sidebar-note"><strong>Твой путь в аналитике</strong><br>{"Загрузка подключена ✓" if done else "Первый шаг: загрузка датасета"}<br>Одна функция — новый результат.</div>')
    st.button("В учебную мастерскую", icon=":material/school:", width="stretch", on_click=goto, args=("Мастерская",), key="open_workshop")
    st.caption("Демоданные вымышлены.  \nРеальные расчёты появятся с твоим кодом.")

metric = "mean" if metric_label == "Средняя" else "median"
badge = "ТВОЙ КОД + ДЕМО" if page == "Мои данные" else "УЧЕБНАЯ МАСТЕРСКАЯ" if page == "Мастерская" else "ДЕМОНСТРАЦИЯ"
st.html(f'<div class="topline"><span>Workspace &nbsp; / &nbsp; <b>{escape(page)}</b></span><span class="status-pill"><i class="status-dot"></i>{badge}</span></div>')

if page == "Обзор рынка":
    views.overview(data, fixture, metric)
elif page == "Специализации":
    views.roles(data, fixture, metric)
elif page == "Формат работы":
    views.work(data, fixture)
elif page == "Динамика зарплат":
    views.trends(data, fixture, metric)
elif page == "Мои данные":
    views.data_page(fixture, scenario)
else:
    views.workshop()
footer()
