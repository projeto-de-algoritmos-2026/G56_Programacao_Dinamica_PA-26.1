"""
Knapsack 0/1 — implementação iterativa (bottom-up).

Recorrência:
    dp[i][w] = max(dp[i-1][w], dp[i-1][w - weight[i]] + value[i])

Complexidade: O(n * W) tempo e espaço (matriz completa armazenada para
permitir reconstrução da solução via backtracking).
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field


@dataclass
class KnapsackResult:
    value: float
    selected_indices: list[int]
    dp_table: list[list[float]]
    execution_time_ms: float
    states_computed: int
    n_items: int
    capacity: int


def knapsack_iterativo(
    weights: list[int],
    values: list[float],
    capacity: int,
) -> KnapsackResult:
    """
    Resolve o problema da mochila 0/1 de forma iterativa.

    Args:
        weights: lista de pesos (preços inteiros em centavos ou unidades).
        values:  lista de valores (scores de desempenho).
        capacity: capacidade máxima da mochila (orçamento).

    Returns:
        KnapsackResult com a tabela DP completa e os índices selecionados.
    """
    n = len(weights)
    W = capacity

    start = time.perf_counter()

    # Tabela (n+1) x (W+1) inicializada em 0
    dp: list[list[float]] = [[0.0] * (W + 1) for _ in range(n + 1)]

    states = 0
    for i in range(1, n + 1):
        wi = weights[i - 1]
        vi = values[i - 1]
        for w in range(W + 1):
            states += 1
            if wi > w:
                dp[i][w] = dp[i - 1][w]
            else:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - wi] + vi)

    elapsed_ms = (time.perf_counter() - start) * 1000

    selected = _reconstruct(dp, weights, values, n, W)

    return KnapsackResult(
        value=dp[n][W],
        selected_indices=selected,
        dp_table=dp,
        execution_time_ms=elapsed_ms,
        states_computed=states,
        n_items=n,
        capacity=W,
    )


def _reconstruct(
    dp: list[list[float]],
    weights: list[int],
    values: list[float],
    n: int,
    W: int,
) -> list[int]:
    """Reconstrói os índices dos itens selecionados a partir da tabela DP."""
    selected: list[int] = []
    w = W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(i - 1)  # índice base-0
            w -= weights[i - 1]
    return list(reversed(selected))


def get_dp_table_display(
    dp: list[list[float]],
    max_rows: int = 10,
    max_cols: int = 15,
) -> tuple[list[list[float]], bool]:
    """
    Retorna uma fatia da tabela DP para exibição.

    Returns:
        (tabela_reduzida, foi_truncada)
    """
    rows = len(dp)
    cols = len(dp[0]) if dp else 0

    row_step = max(1, rows // max_rows)
    col_step = max(1, cols // max_cols)

    sampled_rows = list(range(0, rows, row_step))
    sampled_cols = list(range(0, cols, col_step))

    # Garante que a última linha/coluna sempre apareça
    if rows - 1 not in sampled_rows:
        sampled_rows.append(rows - 1)
    if cols - 1 not in sampled_cols:
        sampled_cols.append(cols - 1)

    table = [[dp[r][c] for c in sampled_cols] for r in sampled_rows]
    truncated = rows > max_rows or cols > max_cols
    return table, truncated
