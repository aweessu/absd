"""Небольшие компоненты интерфейса."""

from html import escape
from pathlib import Path

import streamlit as st


def setup_style():
    st.html(f"<style>{Path(__file__).with_name('styles.css').read_text(encoding='utf-8')}</style>")


def heading(title, subtitle, eyebrow="CAREER INTELLIGENCE"):
    st.html(f'<div class="page-heading"><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>')


def chart_heading(title, subtitle):
    st.html(f'<div class="chart-title">{escape(title)}</div><div class="chart-subtitle">{escape(subtitle)}</div>')


def money(value):
    return "$" + f"{value:,.0f}".replace(",", " ")


def metric_card(label, value, foot, icon):
    st.html(f'<div class="metric-card"><span class="metric-icon">{escape(icon)}</span><div class="metric-label">{escape(label)}</div><div class="metric-value">{escape(value)}</div><div class="metric-foot">{escape(foot)}</div></div>')


def plot(figure, key):
    st.plotly_chart(figure, key=key, width="stretch", theme=None, config={
        "displaylogo": False, "responsive": True, "scrollZoom": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {"format": "png", "filename": f"career-explorer-demo-{key}", "scale": 2},
    })


def goto(page):
    st.session_state["page"] = page


def footer():
    st.html('<div class="footer"><span>IT CAREER EXPLORER <span style="color:#454f65">/</span> Учебный проект · Lab 12</span><span>Python + Pandas → твои исследования, твои выводы</span></div>')
