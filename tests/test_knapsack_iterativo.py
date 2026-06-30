"""Testes unitários para o Knapsack Iterativo."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from knapsack_iterativo import knapsack_iterativo, get_dp_table_display


class TestKnapsackIterativo:
    def test_empty_input(self):
        result = knapsack_iterativo([], [], 100)
        assert result.value == 0
        assert result.selected_indices == []

    def test_single_item_fits(self):
        result = knapsack_iterativo([50], [10.0], 100)
        assert result.value == 10.0
        assert 0 in result.selected_indices

    def test_single_item_does_not_fit(self):
        result = knapsack_iterativo([200], [10.0], 100)
        assert result.value == 0.0
        assert result.selected_indices == []

    def test_classic_example(self):
        # Exemplo clássico: capacidade=10, itens com pesos [2,3,4,5] e valores [3,4,5,6]
        weights = [2, 3, 4, 5]
        values = [3.0, 4.0, 5.0, 6.0]
        result = knapsack_iterativo(weights, values, 10)
        assert result.value == pytest.approx(13.0)  # 4+3+6 ou 5+4+4...
        # Verifica que o valor ótimo é ≥ 13
        assert result.value >= 13.0

    def test_all_items_fit(self):
        weights = [1, 2, 3]
        values = [10.0, 20.0, 30.0]
        result = knapsack_iterativo(weights, values, 100)
        assert result.value == pytest.approx(60.0)
        assert len(result.selected_indices) == 3

    def test_no_items_fit(self):
        weights = [500, 600, 700]
        values = [10.0, 20.0, 30.0]
        result = knapsack_iterativo(weights, values, 100)
        assert result.value == 0.0
        assert result.selected_indices == []

    def test_reconstruction_consistency(self):
        weights = [3, 4, 5, 2]
        values = [5.0, 7.0, 8.0, 4.0]
        capacity = 8
        result = knapsack_iterativo(weights, values, capacity)

        # Valor reconstruído deve bater com dp[n][W]
        total_value = sum(values[i] for i in result.selected_indices)
        assert abs(total_value - result.value) < 0.01

        # Peso total não deve exceder a capacidade
        total_weight = sum(weights[i] for i in result.selected_indices)
        assert total_weight <= capacity

    def test_dp_table_dimensions(self):
        weights = [2, 3, 4]
        values = [3.0, 4.0, 5.0]
        capacity = 10
        result = knapsack_iterativo(weights, values, capacity)
        assert len(result.dp_table) == len(weights) + 1
        assert len(result.dp_table[0]) == capacity + 1

    def test_states_count(self):
        n = 5
        W = 20
        weights = [2] * n
        values = [1.0] * n
        result = knapsack_iterativo(weights, values, W)
        assert result.states_computed == n * (W + 1)

    def test_execution_time_is_positive(self):
        result = knapsack_iterativo([1, 2, 3], [1.0, 2.0, 3.0], 10)
        assert result.execution_time_ms >= 0

    def test_large_capacity(self):
        weights = [100, 200, 300]
        values = [10.0, 20.0, 30.0]
        result = knapsack_iterativo(weights, values, 500)
        assert result.value == pytest.approx(60.0)

    def test_duplicate_values(self):
        weights = [5, 5, 5]
        values = [10.0, 10.0, 10.0]
        result = knapsack_iterativo(weights, values, 10)
        assert result.value == pytest.approx(20.0)
        assert len(result.selected_indices) == 2


class TestGetDpTableDisplay:
    def test_small_table_not_truncated(self):
        dp = [[float(i * j) for j in range(5)] for i in range(5)]
        table, truncated = get_dp_table_display(dp, max_rows=10, max_cols=10)
        assert not truncated

    def test_large_table_truncated(self):
        dp = [[0.0] * 100 for _ in range(100)]
        table, truncated = get_dp_table_display(dp, max_rows=10, max_cols=10)
        assert truncated

    def test_display_includes_last_row(self):
        dp = [[float(i) for _ in range(5)] for i in range(20)]
        table, _ = get_dp_table_display(dp, max_rows=5, max_cols=5)
        # Última linha da tabela deve ser incluída
        assert table[-1][0] == dp[-1][0]
