"""
Pré-processamento dos dados antes de rodar o Knapsack.

Responsável por:
  - Filtrar peças por orçamento.
  - Normalizar preços para inteiros (centavos ou arredondados).
  - Remover duplicatas e peças inválidas.
  - Preparar listas de pesos e valores para os algoritmos.
"""

from __future__ import annotations
import pandas as pd
import numpy as np


PRICE_SCALE = 1  # trabalha em BRL inteiro; muda para 10 se quiser precisão de R$0,10


def prepare_knapsack_inputs(
    df: pd.DataFrame,
    budget: float,
    score_col: str = "computed_score",
) -> tuple[list[int], list[float], list[str], list[str]]:
    """
    Prepara as listas de entrada para os algoritmos de Knapsack.

    Args:
        df:         DataFrame com colunas 'price_brl' e score_col.
        budget:     orçamento total (float BRL).
        score_col:  coluna com o score já calculado.

    Returns:
        (weights, values, names, categories)
        weights   — preços como inteiros (em BRL).
        values    — scores como floats.
        names     — nomes das peças.
        categories — categorias das peças.
    """
    df = df.copy()
    df = df[df["price_brl"] <= budget].copy()
    df = df[df[score_col] > 0].copy()
    df = df.drop_duplicates(subset=["name"]).copy()

    weights = [int(round(p * PRICE_SCALE)) for p in df["price_brl"]]
    values = [float(v) for v in df[score_col]]
    names = list(df["name"].astype(str))
    categories = list(df["category"].astype(str)) if "category" in df.columns else [""] * len(df)

    return weights, values, names, categories


def filter_by_budget(df: pd.DataFrame, budget: float) -> pd.DataFrame:
    """Remove itens mais caros do que o orçamento."""
    return df[df["price_brl"] <= budget].copy()


def normalize_scores(df: pd.DataFrame, score_col: str = "computed_score") -> pd.DataFrame:
    """Normaliza o score para o intervalo [0, 100] para comparação visual."""
    df = df.copy()
    min_s = df[score_col].min()
    max_s = df[score_col].max()
    if max_s > min_s:
        df[f"{score_col}_norm"] = (df[score_col] - min_s) / (max_s - min_s) * 100
    else:
        df[f"{score_col}_norm"] = 50.0
    return df


def reduce_budget_resolution(budget: float, max_states: int = 5000) -> int:
    """
    Reduz a resolução do orçamento para manter a tabela DP em tamanho razoável.

    Quando o orçamento é muito alto, usar granularidade de R$10 ou R$100
    em vez de R$1 para não explodir a memória.

    Returns:
        Capacidade inteira ajustada.
    """
    capacity = int(budget)
    if capacity <= max_states:
        return capacity
    step = max(1, capacity // max_states)
    return capacity // step


def scale_prices(prices: list[float], step: int = 1) -> list[int]:
    """Converte preços para inteiros usando o passo de escala."""
    return [max(1, int(round(p / step))) for p in prices]


def get_budget_step(budget: float, max_states: int = 3000) -> int:
    """Calcula o step ideal para manter a tabela DP dentro do limite de estados."""
    capacity = int(budget)
    if capacity <= max_states:
        return 1
    step = max(1, capacity // max_states)
    return step


def apply_budget_step(
    weights: list[int],
    budget: float,
    max_states: int = 3000,
) -> tuple[list[int], int, int]:
    """
    Aplica escala de step no orçamento e nos pesos.

    Returns:
        (scaled_weights, scaled_capacity, step)
    """
    step = get_budget_step(budget, max_states)
    scaled_weights = [max(1, w // step) for w in weights]
    scaled_capacity = int(budget) // step
    return scaled_weights, scaled_capacity, step
