"""
Geração de gráficos com Plotly para a interface Streamlit.
"""

from __future__ import annotations
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def chart_price_distribution(df: pd.DataFrame, title: str = "Distribuição de Preços") -> go.Figure:
    """Histograma de distribuição de preços."""
    fig = px.histogram(
        df,
        x="price_brl",
        nbins=30,
        title=title,
        labels={"price_brl": "Preço (R$)", "count": "Quantidade"},
        color_discrete_sequence=["#7B68EE"],
    )
    fig.update_layout(bargap=0.1, plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                      font_color="white", title_font_size=16)
    return fig


def chart_score_by_category(df: pd.DataFrame) -> go.Figure:
    """Box plot de score por categoria de peça."""
    fig = px.box(
        df,
        x="category",
        y="performance_score",
        color="category",
        title="Score de Desempenho por Categoria",
        labels={"performance_score": "Score", "category": "Categoria"},
    )
    fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
                      font_color="white", showlegend=False)
    return fig


def chart_selected_parts(selected_items: list[dict]) -> go.Figure:
    """Gráfico de barras com score e preço das peças escolhidas."""
    if not selected_items:
        return go.Figure()

    names = [item.get("name", "?")[:25] for item in selected_items]
    scores = [item.get("score", 0) for item in selected_items]
    prices = [item.get("price_brl", item.get("price_int", 0)) for item in selected_items]
    categories = [item.get("category", "") for item in selected_items]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Score por Peça", "Preço por Peça (R$)"),
    )
    fig.add_trace(
        go.Bar(x=names, y=scores, name="Score", marker_color="#7B68EE",
               text=[f"{s:.1f}" for s in scores], textposition="outside"),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(x=names, y=prices, name="Preço (R$)", marker_color="#20B2AA",
               text=[f"R${p:,.0f}" for p in prices], textposition="outside"),
        row=1, col=2,
    )
    fig.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white",
        title_text="Análise das Peças Escolhidas", height=400, showlegend=False,
    )
    fig.update_xaxes(tickangle=-30)
    return fig


def chart_budget_usage(used: float, remaining: float) -> go.Figure:
    """Gráfico de pizza mostrando orçamento usado x disponível."""
    labels = ["Orçamento Usado", "Orçamento Restante"]
    values = [used, max(remaining, 0)]
    colors = ["#FF6B6B", "#4CAF50"]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors),
        textinfo="label+percent",
        textfont_size=13,
    )])
    fig.update_layout(
        title="Distribuição do Orçamento",
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white",
        height=350,
    )
    return fig


def chart_algorithm_comparison(
    iter_time: float,
    rec_time: float,
    iter_states: int,
    rec_states: int,
    iter_value: float,
    rec_value: float,
) -> go.Figure:
    """Comparação lado a lado dos dois algoritmos Knapsack."""
    categories = ["Tempo (ms)", "Estados Calculados", "Valor Ótimo"]
    iter_vals = [iter_time, iter_states, iter_value]
    rec_vals = [rec_time, rec_states, rec_value]

    fig = go.Figure(data=[
        go.Bar(name="Iterativo", x=categories, y=iter_vals,
               marker_color="#7B68EE", text=[f"{v:.2f}" if i < 2 else f"{v:.1f}" for i, v in enumerate(iter_vals)],
               textposition="outside"),
        go.Bar(name="Recursivo (Memo)", x=categories, y=rec_vals,
               marker_color="#20B2AA", text=[f"{v:.2f}" if i < 2 else f"{v:.1f}" for i, v in enumerate(rec_vals)],
               textposition="outside"),
    ])
    fig.update_layout(
        barmode="group",
        title="Comparação: Knapsack Iterativo vs Recursivo",
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white",
        height=400,
    )
    return fig


def chart_dp_table_heatmap(
    table: list[list[float]],
    max_rows: int = 15,
    max_cols: int = 20,
) -> go.Figure:
    """Heatmap da tabela DP (amostrada para grandes matrizes)."""
    if not table:
        return go.Figure()

    # Amostragem uniforme
    n_rows = len(table)
    n_cols = len(table[0])
    row_step = max(1, n_rows // max_rows)
    col_step = max(1, n_cols // max_cols)

    sampled = [
        [table[r][c] for c in range(0, n_cols, col_step)]
        for r in range(0, n_rows, row_step)
    ]
    col_labels = list(range(0, n_cols, col_step))
    row_labels = list(range(0, n_rows, row_step))

    fig = go.Figure(data=go.Heatmap(
        z=sampled,
        x=col_labels,
        y=row_labels,
        colorscale="Viridis",
        colorbar=dict(title="Score"),
    ))
    fig.update_layout(
        title="Tabela DP — Knapsack (amostrada)",
        xaxis_title="Capacidade (orçamento)",
        yaxis_title="Índice do item",
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white",
        height=450,
    )
    return fig


def chart_laptop_ranking(laptops: list[dict], top_n: int = 5) -> go.Figure:
    """Gráfico de barras horizontais com ranking de notebooks."""
    if not laptops:
        return go.Figure()

    top = laptops[:top_n]
    names = [l.get("name", "?")[:30] for l in top]
    scores = [l.get("score", 0) for l in top]
    prices = [l.get("price_brl", 0) for l in top]

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Score", "Preço (R$)"))
    fig.add_trace(
        go.Bar(y=names, x=scores, orientation="h", marker_color="#7B68EE",
               text=[f"{s:.1f}" for s in scores], textposition="outside", name="Score"),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(y=names, x=prices, orientation="h", marker_color="#20B2AA",
               text=[f"R${p:,.0f}" for p in prices], textposition="outside", name="Preço"),
        row=1, col=2,
    )
    fig.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white",
        title="Ranking de Notebooks", height=350, showlegend=False,
    )
    return fig


def chart_price_vs_score(df: pd.DataFrame, color_col: str = "category") -> go.Figure:
    """Scatter plot: preço x score, colorido por categoria."""
    fig = px.scatter(
        df,
        x="price_brl",
        y="performance_score",
        color=color_col if color_col in df.columns else None,
        hover_name="name",
        title="Preço × Score de Desempenho",
        labels={"price_brl": "Preço (R$)", "performance_score": "Score"},
        size_max=15,
    )
    fig.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white",
    )
    return fig


def chart_category_breakdown(selected_items: list[dict]) -> go.Figure:
    """Pie chart com distribuição de custo por categoria."""
    if not selected_items:
        return go.Figure()

    cat_prices: dict[str, float] = {}
    for item in selected_items:
        cat = item.get("category", "Outro")
        price = float(item.get("price_brl", item.get("price_int", 0)))
        cat_prices[cat] = cat_prices.get(cat, 0) + price

    fig = go.Figure(data=[go.Pie(
        labels=list(cat_prices.keys()),
        values=list(cat_prices.values()),
        hole=0.4,
        textinfo="label+percent",
    )])
    fig.update_layout(
        title="Distribuição do Custo por Categoria",
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white",
        height=380,
    )
    return fig
