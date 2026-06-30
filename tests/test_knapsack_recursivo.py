"""Testes unitários para o Knapsack Recursivo com Memoization."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from knapsack_recursivo import knapsack_recursivo, get_memo_summary


class TestKnapsackRecursivo:
    def test_empty_input(self):
        result = knapsack_recursivo([], [], 100)
        assert result.value == 0.0
        assert result.selected_indices == []

    def test_single_item_fits(self):
        result = knapsack_recursivo([50], [15.0], 100)
        assert result.value == pytest.approx(15.0)
        assert 0 in result.selected_indices

    def test_single_item_does_not_fit(self):
        result = knapsack_recursivo([200], [15.0], 100)
        assert result.value == 0.0
        assert result.selected_indices == []

    def test_classic_example_matches_iterative(self):
        from knapsack_iterativo import knapsack_iterativo
        weights = [2, 3, 4, 5]
        values = [3.0, 4.0, 5.0, 6.0]
        capacity = 10

        rec_result = knapsack_recursivo(weights, values, capacity)
        iter_result = knapsack_iterativo(weights, values, capacity)

        assert abs(rec_result.value - iter_result.value) < 0.01

    def test_all_items_fit(self):
        weights = [1, 2, 3]
        values = [10.0, 20.0, 30.0]
        result = knapsack_recursivo(weights, values, 100)
        assert result.value == pytest.approx(60.0)

    def test_no_items_fit(self):
        result = knapsack_recursivo([500, 600], [10.0, 20.0], 100)
        assert result.value == 0.0

    def test_reconstruction_consistency(self):
        weights = [3, 4, 5, 2]
        values = [5.0, 7.0, 8.0, 4.0]
        capacity = 8
        result = knapsack_recursivo(weights, values, capacity)

        total_value = sum(values[i] for i in result.selected_indices)
        assert abs(total_value - result.value) < 0.01

        total_weight = sum(weights[i] for i in result.selected_indices)
        assert total_weight <= capacity

    def test_memo_is_populated(self):
        result = knapsack_recursivo([2, 3, 4], [3.0, 4.0, 5.0], 10)
        assert len(result.memo_table) > 0

    def test_cache_hits_are_non_negative(self):
        result = knapsack_recursivo([2, 3, 4, 5], [3.0, 4.0, 5.0, 6.0], 15)
        assert result.cache_hits >= 0

    def test_states_computed_less_than_or_equal_to_iterative(self):
        weights = [2, 3, 4, 5]
        values = [3.0, 4.0, 5.0, 6.0]
        capacity = 10
        rec = knapsack_recursivo(weights, values, capacity)
        # Estados calculados nunca deve exceder n*W
        assert rec.states_computed <= len(weights) * capacity

    def test_execution_time_is_positive(self):
        result = knapsack_recursivo([1, 2, 3], [1.0, 2.0, 3.0], 10)
        assert result.execution_time_ms >= 0

    def test_results_match_iterative_various(self):
        from knapsack_iterativo import knapsack_iterativo
        test_cases = [
            ([1, 2, 3], [2.0, 3.0, 4.0], 5),
            ([5, 4, 3, 2], [10.0, 8.0, 6.0, 4.0], 7),
            ([10, 20, 30], [60.0, 100.0, 120.0], 50),
        ]
        for weights, values, cap in test_cases:
            rec = knapsack_recursivo(weights, values, cap)
            itr = knapsack_iterativo(weights, values, cap)
            assert abs(rec.value - itr.value) < 0.01, (
                f"Mismatch: rec={rec.value}, iter={itr.value} for cap={cap}"
            )


class TestGetMemoSummary:
    def test_empty_memo(self):
        summary = get_memo_summary({})
        assert summary["total_entries"] == 0

    def test_populated_memo(self):
        memo = {(1, 5): 10.0, (2, 10): 20.0, (3, 15): 30.0}
        summary = get_memo_summary(memo)
        assert summary["total_entries"] == 3
        assert summary["max_i"] == 3
        assert summary["max_w"] == 15
        assert summary["max_value"] == pytest.approx(30.0)
