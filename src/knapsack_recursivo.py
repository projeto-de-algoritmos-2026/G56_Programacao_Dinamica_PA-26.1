"""
Knapsack 0/1 — implementação recursiva com memoization (top-down).

Recorrência:
    OPT(i, w) = 0                                        se i == 0
    OPT(i, w) = OPT(i-1, w)                             se weight[i] > w
    OPT(i, w) = max(OPT(i-1, w),
                    OPT(i-1, w - weight[i]) + value[i]) caso contrário

A memoization evita recalcular subproblemas já resolvidos, reduzindo a
complexidade de exponencial para O(n * W).
"""

from __future__ import annotations
import sys
import time
from functools import lru_cache
from dataclasses import dataclass


@dataclass
class KnapsackRecursivoResult:
    value: float
    selected_indices: list[int]
    execution_time_ms: float
    states_computed: int
    cache_hits: int
    n_items: int
    capacity: int
    memo_table: dict[tuple[int, int], float]


def knapsack_recursivo(
    weights: list[int],
    values: list[float],
    capacity: int,
) -> KnapsackRecursivoResult:
    """
    Resolve o Knapsack 0/1 de forma recursiva com memoization.

    Args:
        weights:  lista de pesos dos itens.
        values:   lista de valores dos itens.
        capacity: capacidade máxima da mochila.

    Returns:
        KnapsackRecursivoResult com o valor ótimo e os itens selecionados.
    """
    n = len(weights)
    memo: dict[tuple[int, int], float] = {}
    states_computed = [0]
    cache_hits = [0]

    sys.setrecursionlimit(max(10000, n * capacity + 100))

    def opt(i: int, w: int) -> float:
        if i == 0 or w == 0:
            return 0.0

        key = (i, w)
        if key in memo:
            cache_hits[0] += 1
            return memo[key]

        states_computed[0] += 1

        if weights[i - 1] > w:
            result = opt(i - 1, w)
        else:
            skip = opt(i - 1, w)
            take = opt(i - 1, w - weights[i - 1]) + values[i - 1]
            result = max(skip, take)

        memo[key] = result
        return result

    start = time.perf_counter()
    best_value = opt(n, capacity)
    elapsed_ms = (time.perf_counter() - start) * 1000

    selected = _reconstruct_recursive(weights, values, memo, n, capacity)

    return KnapsackRecursivoResult(
        value=best_value,
        selected_indices=selected,
        execution_time_ms=elapsed_ms,
        states_computed=states_computed[0],
        cache_hits=cache_hits[0],
        n_items=n,
        capacity=capacity,
        memo_table=memo,
    )


def _reconstruct_recursive(
    weights: list[int],
    values: list[float],
    memo: dict[tuple[int, int], float],
    n: int,
    W: int,
) -> list[int]:
    """Reconstrói os itens selecionados percorrendo o memo de trás para frente."""

    def opt_cached(i: int, w: int) -> float:
        if i == 0 or w == 0:
            return 0.0
        return memo.get((i, w), 0.0)

    selected: list[int] = []
    w = W
    for i in range(n, 0, -1):
        if opt_cached(i, w) != opt_cached(i - 1, w):
            selected.append(i - 1)  # índice base-0
            w -= weights[i - 1]

    return list(reversed(selected))


def get_memo_summary(memo: dict[tuple[int, int], float]) -> dict:
    """Retorna estatísticas do cache de memoization."""
    if not memo:
        return {"total_entries": 0, "max_i": 0, "max_w": 0, "max_value": 0.0}

    keys = list(memo.keys())
    return {
        "total_entries": len(memo),
        "max_i": max(k[0] for k in keys),
        "max_w": max(k[1] for k in keys),
        "max_value": max(memo.values()),
    }
