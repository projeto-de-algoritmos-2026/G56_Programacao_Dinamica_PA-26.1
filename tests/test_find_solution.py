"""Testes unitários para Find Solution / reconstrução."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from knapsack_iterativo import knapsack_iterativo
from knapsack_recursivo import knapsack_recursivo
from find_solution import (
    find_solution_from_dp,
    find_solution_from_memo,
    format_reconstruction_text,
    FindSolutionResult,
)


def _run_iter(weights, values, capacity):
    return knapsack_iterativo(weights, values, capacity)


def _run_rec(weights, values, capacity):
    return knapsack_recursivo(weights, values, capacity)


class TestFindSolutionFromDP:
    def test_empty_inputs(self):
        result = _run_iter([], [], 100)
        fs = find_solution_from_dp(result.dp_table, [], [], [], [], capacity=100)
        assert fs.steps == []
        assert fs.total_price == 0

    def test_single_item_reconstruction(self):
        weights = [300]
        values = [50.0]
        names = ["CPU Test"]
        cats = ["CPU"]
        r = _run_iter(weights, values, 500)
        fs = find_solution_from_dp(r.dp_table, weights, values, names, cats)
        assert len(fs.steps) == 1
        assert fs.steps[0].item_name == "CPU Test"
        assert fs.total_price == 300

    def test_classic_reconstruction(self):
        weights = [2, 3, 4, 5]
        values = [3.0, 4.0, 5.0, 6.0]
        names = [f"Item{i}" for i in range(4)]
        cats = ["A", "B", "C", "D"]
        capacity = 10
        r = _run_iter(weights, values, capacity)
        fs = find_solution_from_dp(r.dp_table, weights, values, names, cats, capacity=capacity)

        assert fs.total_price <= capacity
        assert abs(fs.total_score - r.value) < 0.01

    def test_custom_capacity(self):
        weights = [2, 3, 4]
        values = [3.0, 4.0, 5.0]
        names = ["A", "B", "C"]
        cats = ["x", "y", "z"]
        r = _run_iter(weights, values, 10)

        # Reconstrução com capacidade menor
        fs = find_solution_from_dp(r.dp_table, weights, values, names, cats, capacity=5)
        assert fs.initial_capacity == 5
        assert fs.total_price <= 5

    def test_budget_remaining_correct(self):
        weights = [3, 4]
        values = [5.0, 7.0]
        names = ["P1", "P2"]
        cats = ["A", "B"]
        capacity = 10
        r = _run_iter(weights, values, capacity)
        fs = find_solution_from_dp(r.dp_table, weights, values, names, cats, capacity=capacity)
        assert fs.budget_remaining == capacity - fs.total_price

    def test_steps_order(self):
        weights = [2, 3, 4]
        values = [3.0, 4.0, 5.0]
        names = ["GPU", "CPU", "RAM"]
        cats = ["GPU", "CPU", "RAM"]
        r = _run_iter(weights, values, 9)
        fs = find_solution_from_dp(r.dp_table, weights, values, names, cats)
        # Passos devem ser numerados sequencialmente
        for i, step in enumerate(fs.steps, start=1):
            assert step.step == i

    def test_reconstruction_matches_selected_indices(self):
        weights = [1, 2, 3, 4, 5]
        values = [1.0, 6.0, 10.0, 16.0, 5.0]
        names = [f"Item{i}" for i in range(5)]
        cats = ["A"] * 5
        capacity = 7
        r = _run_iter(weights, values, capacity)
        fs = find_solution_from_dp(r.dp_table, weights, values, names, cats, capacity=capacity)

        # Total value deve bater com dp[n][W]
        assert abs(fs.total_score - r.value) < 0.01


class TestFindSolutionFromMemo:
    def test_basic_reconstruction(self):
        weights = [3, 4, 5]
        values = [5.0, 7.0, 8.0]
        names = ["A", "B", "C"]
        cats = ["CPU", "GPU", "RAM"]
        capacity = 8
        r = _run_rec(weights, values, capacity)
        fs = find_solution_from_memo(r.memo_table, weights, values, names, cats, capacity=capacity)

        assert fs.total_price <= capacity
        # Valor deve ser não-negativo
        assert fs.total_score >= 0

    def test_uses_max_capacity_when_none(self):
        weights = [2, 3]
        values = [4.0, 6.0]
        names = ["X", "Y"]
        cats = ["A", "B"]
        capacity = 5
        r = _run_rec(weights, values, capacity)
        fs = find_solution_from_memo(r.memo_table, weights, values, names, cats, capacity=None)
        # Deve usar o maior w do memo
        assert fs.initial_capacity <= capacity


class TestFormatReconstructionText:
    def test_format_non_empty(self):
        weights = [300, 500]
        values = [70.0, 90.0]
        names = ["CPU", "GPU"]
        cats = ["CPU", "GPU"]
        r = _run_iter(weights, values, 1000)
        fs = find_solution_from_dp(r.dp_table, weights, values, names, cats)
        text = format_reconstruction_text(fs)
        assert "Orçamento inicial" in text
        assert "Preço total" in text

    def test_format_empty_steps(self):
        r = _run_iter([], [], 100)
        fs = find_solution_from_dp(r.dp_table, [], [], [], [], capacity=100)
        text = format_reconstruction_text(fs)
        assert "Orçamento inicial" in text
