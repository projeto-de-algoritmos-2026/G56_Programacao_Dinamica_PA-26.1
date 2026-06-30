"""
Métricas e comparações entre execuções dos algoritmos Knapsack.
"""

from __future__ import annotations
import sys
from dataclasses import dataclass


@dataclass
class AlgorithmMetrics:
    name: str
    execution_time_ms: float
    states_computed: int
    optimal_value: float
    n_items_selected: int
    memory_estimate_kb: float
    cache_hits: int = 0


def estimate_memory_iterativo(n: int, W: int) -> float:
    """Estima o uso de memória da tabela DP iterativa em KB."""
    bytes_used = (n + 1) * (W + 1) * 8  # float64 = 8 bytes
    return bytes_used / 1024


def estimate_memory_recursivo(states_computed: int) -> float:
    """Estima o uso de memória do memo recursivo em KB."""
    # ~80 bytes por entrada no dict (chave tupla + valor float + overhead)
    bytes_used = states_computed * 80
    return bytes_used / 1024


def compare_algorithms(
    iter_result,
    rec_result,
    n_items: int,
    capacity: int,
) -> tuple[AlgorithmMetrics, AlgorithmMetrics]:
    """
    Gera métricas comparativas entre os dois algoritmos.

    Args:
        iter_result: KnapsackResult do iterativo.
        rec_result:  KnapsackRecursivoResult do recursivo.
        n_items:     número de itens de entrada.
        capacity:    capacidade da mochila.

    Returns:
        (metrics_iterativo, metrics_recursivo)
    """
    mem_iter = estimate_memory_iterativo(n_items, capacity)
    mem_rec = estimate_memory_recursivo(rec_result.states_computed)

    iter_metrics = AlgorithmMetrics(
        name="Knapsack Iterativo",
        execution_time_ms=iter_result.execution_time_ms,
        states_computed=iter_result.states_computed,
        optimal_value=iter_result.value,
        n_items_selected=len(iter_result.selected_indices),
        memory_estimate_kb=mem_iter,
    )

    rec_metrics = AlgorithmMetrics(
        name="Knapsack Recursivo (Memoization)",
        execution_time_ms=rec_result.execution_time_ms,
        states_computed=rec_result.states_computed,
        optimal_value=rec_result.value,
        n_items_selected=len(rec_result.selected_indices),
        memory_estimate_kb=mem_rec,
        cache_hits=rec_result.cache_hits,
    )

    return iter_metrics, rec_metrics


def format_metrics_table(metrics: AlgorithmMetrics) -> dict:
    """Converte AlgorithmMetrics para dicionário de exibição."""
    return {
        "Algoritmo": metrics.name,
        "Tempo (ms)": f"{metrics.execution_time_ms:.4f}",
        "Estados Calculados": f"{metrics.states_computed:,}",
        "Valor Ótimo": f"{metrics.optimal_value:.2f}",
        "Itens Selecionados": metrics.n_items_selected,
        "Memória Estimada (KB)": f"{metrics.memory_estimate_kb:.1f}",
        "Cache Hits": metrics.cache_hits,
    }


def efficiency_ratio(iter_m: AlgorithmMetrics, rec_m: AlgorithmMetrics) -> dict:
    """Calcula razões de eficiência entre os dois algoritmos."""
    time_ratio = (
        iter_m.execution_time_ms / rec_m.execution_time_ms
        if rec_m.execution_time_ms > 0 else 1.0
    )
    states_ratio = (
        iter_m.states_computed / rec_m.states_computed
        if rec_m.states_computed > 0 else 1.0
    )
    return {
        "time_ratio_iter_over_rec": round(time_ratio, 3),
        "states_ratio_iter_over_rec": round(states_ratio, 3),
        "same_optimal": abs(iter_m.optimal_value - rec_m.optimal_value) < 0.01,
    }
