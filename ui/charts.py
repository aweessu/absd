"""Plotly-представления готовых результатов. Аналитических расчётов нет."""

import plotly.graph_objects as go

PURPLE = "#a599ff"
TEAL = "#5ed9c1"
BLUE = "#7ba9f7"
GOLD = "#f2c77c"
COLORS = [TEAL, BLUE, PURPLE, GOLD]


def base(figure, height=310):
    figure.update_layout(
        height=height, margin=dict(l=12, r=18, t=24, b=22),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Arial, sans-serif", size=12, color="#98a3b9"),
        hoverlabel=dict(bgcolor="#222a3d", font_color="#f5f6ff", bordercolor="#424d68"),
        colorway=COLORS, dragmode="zoom", separators=". ",
        legend=dict(orientation="h", y=-0.22, x=0, font_size=11),
    )
    figure.update_xaxes(showgrid=False, zeroline=False, automargin=True)
    figure.update_yaxes(gridcolor="#252c3e", zeroline=False, automargin=True)
    return figure


def salary_trend(data, fixture, metric="mean"):
    values = data[f"trend_{metric}"]
    fig = go.Figure(go.Scatter(
        x=fixture["years"], y=values, mode="lines+markers", name="Зарплата",
        line=dict(color=PURPLE, width=3, shape="spline"),
        marker=dict(size=8, color=PURPLE, line=dict(color="#171b2b", width=3)),
        fill="tozeroy", fillcolor="rgba(165,153,255,0.08)",
        hovertemplate="%{x}<br>$%{y:,.0f} / год<extra></extra>",
    ))
    base(fig, 290)
    fig.update_yaxes(tickprefix="$", tickformat="~s", rangemode="normal")
    fig.update_xaxes(dtick=1)
    fig.update_layout(hovermode="x unified")
    return fig


def top_roles(data, fixture, metric="mean", top_n=7):
    values = data[f"roles_{metric}"][:top_n]
    names = fixture["roles"][:top_n]
    fig = go.Figure(go.Bar(
        x=values[::-1], y=names[::-1], orientation="h",
        marker=dict(color=["#51497f"] * (top_n - 1) + [PURPLE], cornerradius=5),
        text=values[::-1], texttemplate="$%{text:,.0f}", textposition="outside",
        textfont=dict(size=11, color="#c5cce1"), cliponaxis=False,
        hovertemplate="%{y}<br>$%{x:,.0f} / год<extra></extra>",
    ))
    base(fig, 290 if top_n <= 7 else 380)
    fig.update_layout(margin=dict(l=8, r=76, t=15, b=22), bargap=0.40)
    fig.update_xaxes(tickprefix="$", tickformat="~s", showgrid=True, gridcolor="#252c3e")
    fig.update_yaxes(showgrid=False, tickfont_color="#c2cadc")
    return fig


def salary_distribution(data, fixture):
    fig = go.Figure(go.Bar(
        x=fixture["histogram_bins"], y=data["histogram"],
        marker=dict(color=PURPLE, cornerradius=3),
        hovertemplate="$%{x} тыс.<br>Записей: %{y:,.0f}<extra></extra>",
    ))
    base(fig, 280)
    fig.update_layout(bargap=0.13)
    fig.update_xaxes(title="Годовая зарплата, тыс. USD", tickangle=-35)
    fig.update_yaxes(title="Записи")
    return fig


def experience_boxes(data, fixture):
    fig = go.Figure()
    for index, label in enumerate(fixture["levels"]):
        box = data["box"]
        fig.add_trace(go.Box(
            name=label, q1=[box["q1"][index]], median=[box["median"][index]],
            q3=[box["q3"][index]], lowerfence=[box["lower"][index]],
            upperfence=[box["upper"][index]], boxpoints=False,
            marker_color=COLORS[index], fillcolor=COLORS[index], opacity=0.85,
            line_width=1.6, showlegend=False,
        ))
    base(fig, 280)
    fig.update_yaxes(tickprefix="$", tickformat="~s")
    return fig


def company_heatmap(data, fixture):
    fig = go.Figure(go.Heatmap(
        z=data["heatmap"], x=["S · небольшая", "M · средняя", "L · крупная"],
        y=fixture["levels"], texttemplate="$%{z:,.0f}",
        textfont=dict(size=13, color="#f6f3ff"),
        colorscale=[[0,"#25283d"],[0.5,"#605497"],[1,"#9b89e8"]],
        xgap=6, ygap=6, showscale=False,
        hovertemplate="%{y} · %{x}<br>Средняя: $%{z:,.0f}<extra></extra>",
    ))
    base(fig, 290)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return fig


def work_donut(data):
    fig = go.Figure(go.Pie(
        labels=["Удалённо", "Гибрид", "Офис"], values=data["work_share"], hole=0.76,
        marker=dict(colors=[PURPLE, TEAL, "#46516c"], line=dict(color="#141925", width=4)),
        sort=False, direction="clockwise", textinfo="none",
        hovertemplate="%{label}: %{value}%<extra></extra>",
    ))
    base(fig, 245)
    fig.update_layout(
        margin=dict(l=10,r=10,t=8,b=20),
        annotations=[dict(text=f"<b>{data['metrics']['remote']}%</b><br><span style='font-size:12px'>удалённо</span>",
                          x=0.5,y=0.5,font=dict(size=29,color="#eff0fa"),showarrow=False)],
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.06),
    )
    return fig


def remote_scatter(data, fixture):
    points = data["scatter"]
    fig = go.Figure()
    for index, label in enumerate(fixture["levels"]):
        # Раскладка готовых точек по цветам — только отрисовка.
        selected = [i for i, level in enumerate(points["level"]) if level == index]
        fig.add_trace(go.Scatter(
            x=[points["ratio"][i] for i in selected], y=[points["salary"][i] for i in selected],
            name=label, mode="markers", marker=dict(size=12, color=COLORS[index], opacity=0.8),
            hovertemplate=f"{label}<br>Удалённость: %{{x}}%<br>$%{{y:,.0f}} / год<extra></extra>",
        ))
    base(fig, 330)
    fig.update_xaxes(tickvals=[0,50,100], ticktext=["Офис · 0%","Гибрид · 50%","Удалённо · 100%"], range=[-12,112])
    fig.update_yaxes(tickprefix="$",tickformat="~s")
    return fig


def growth(data, fixture):
    fig = go.Figure(go.Bar(
        x=fixture["years"][1:], y=data["trend_growth"][1:],
        marker=dict(color=TEAL, cornerradius=6), texttemplate="+%{y}%", textposition="outside",
        hovertemplate="%{x}: +%{y}%<extra></extra>",
    ))
    base(fig,290)
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    fig.update_layout(margin=dict(l=8,r=20,t=40,b=20),bargap=0.55)
    return fig
