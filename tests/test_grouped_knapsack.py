"""Testes unitários para o Grouped Knapsack."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from grouped_knapsack import grouped_knapsack


def _make_groups(**kwargs) -> dict:
    """Helper para criar grupos de itens."""
    groups = {}
    for cat, items in kwargs.items():
        groups[cat] = [
            {"name": f"{cat}_{i}", "price_int": p, "price_brl": float(p), "score": s,
             "performance_score": s, "socket": "", "memory_type": "", "wattage": 0.0,
             "store_search_name": f"{cat}_{i}"}
            for i, (p, s) in enumerate(items)
        ]
    return groups


class TestGroupedKnapsack:
    def test_empty_groups(self):
        result = grouped_knapsack({}, 1000)
        assert result.total_value == 0
        assert result.selected_items == []

    def test_single_group_single_item(self):
        groups = _make_groups(CPU=[(500, 80.0)])
        result = grouped_knapsack(groups, 1000)
        assert result.total_value == pytest.approx(80.0)
        assert result.total_price == 500
        assert len(result.selected_items) == 1

    def test_single_group_item_too_expensive(self):
        groups = _make_groups(CPU=[(2000, 100.0)])
        result = grouped_knapsack(groups, 1000)
        assert result.total_value == 0.0
        assert result.selected_items == []

    def test_picks_best_item_from_group(self):
        groups = _make_groups(GPU=[
            (500, 60.0),
            (800, 90.0),
            (1200, 95.0),
        ])
        result = grouped_knapsack(groups, 1000)
        # Deve escolher o de score 90 (800) pois 1200 > 1000
        assert result.total_price <= 1000
        assert result.total_value >= 90.0

    def test_one_item_per_group(self):
        groups = _make_groups(
            CPU=[(300, 70.0), (500, 85.0)],
            GPU=[(600, 80.0), (400, 65.0)],
            RAM=[(200, 60.0)],
        )
        result = grouped_knapsack(groups, 1100)
        cats_chosen = [item["category"] for item in result.selected_items]
        assert len(cats_chosen) == len(set(cats_chosen)), "Escolheu mais de um item por categoria"

    def test_respects_budget(self):
        groups = _make_groups(
            CPU=[(400, 70.0)],
            GPU=[(700, 90.0)],
            RAM=[(300, 50.0)],
        )
        budget = 1200
        result = grouped_knapsack(groups, budget)
        assert result.total_price <= budget

    def test_maximizes_value(self):
        # Verifica que o resultado é realmente ótimo para um caso pequeno
        groups = _make_groups(
            A=[(1, 10.0), (2, 15.0), (3, 18.0)],
            B=[(1, 8.0), (2, 12.0), (3, 16.0)],
        )
        result = grouped_knapsack(groups, 4)
        # Melhor: A[1]=15 (w=2) + B[1]=12 (w=2) = 27 com w=4
        assert result.total_value >= 27.0

    def test_execution_time_positive(self):
        groups = _make_groups(CPU=[(500, 80.0)], GPU=[(800, 90.0)])
        result = grouped_knapsack(groups, 2000)
        assert result.execution_time_ms >= 0

    def test_capacity_remaining(self):
        groups = _make_groups(CPU=[(300, 70.0)])
        result = grouped_knapsack(groups, 1000)
        assert result.capacity_remaining == 1000 - result.total_price

    def test_multiple_groups_all_chosen(self):
        groups = _make_groups(
            CPU=[(300, 70.0)],
            GPU=[(400, 85.0)],
            RAM=[(200, 55.0)],
            Storage=[(250, 60.0)],
        )
        result = grouped_knapsack(groups, 2000)
        assert len(result.selected_items) == 4
        assert result.total_price == 300 + 400 + 200 + 250

    def test_skip_group_if_not_affordable(self):
        groups = _make_groups(
            CPU=[(300, 70.0)],
            GPU=[(1500, 95.0)],  # caro demais para um orçamento de 500
        )
        result = grouped_knapsack(groups, 500)
        assert result.total_price <= 500
        # GPU não deve ser escolhida
        cats = [item["category"] for item in result.selected_items]
        assert "GPU" not in cats
