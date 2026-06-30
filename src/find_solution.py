"""
Find Solution — reconstrução passo a passo da solução do Knapsack.

Permite reconstruir os itens escolhidos dado um orçamento específico
ou o orçamento total usado na última execução. Mostra o passo a passo
de forma didática: capacidade restante após cada escolha.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ReconstructionStep:
    step: int
    item_name: str
    item_price: int
    budget_before: int
    budget_after: int
    score: float
    category: str


@dataclass
class FindSolutionResult:
    steps: list[ReconstructionStep]
    selected_items: list[dict]
    total_price: int
    total_score: float
    budget_used: int
    budget_remaining: int
    initial_capacity: int


def find_solution_from_dp(
    dp_table: list[list[float]],
    weights: list[int],
    values: list[float],
    names: list[str],
    categories: list[str],
    capacity: int | None = None,
) -> FindSolutionResult:
    """
    Reconstrói a solução a partir da tabela DP do Knapsack iterativo.

    Args:
        dp_table:  tabela DP completa [(n+1) x (W+1)].
        weights:   pesos dos itens.
        values:    valores dos itens.
        names:     nomes dos itens.
        categories: categorias dos itens.
        capacity:  capacidade para reconstrução; usa última coluna se None.

    Returns:
        FindSolutionResult com os passos de reconstrução.
    """
    n = len(weights)
    W = capacity if capacity is not None else len(dp_table[0]) - 1

    # Clamp para não ultrapassar o tamanho da tabela
    W = min(W, len(dp_table[0]) - 1)

    steps: list[ReconstructionStep] = []
    selected: list[dict] = []
    w = W
    step_num = 1

    for i in range(n, 0, -1):
        if w <= 0:
            break
        if dp_table[i][w] != dp_table[i - 1][w]:
            wi = weights[i - 1]
            vi = values[i - 1]
            name = names[i - 1] if i - 1 < len(names) else f"Item {i}"
            cat = categories[i - 1] if i - 1 < len(categories) else "—"

            steps.append(ReconstructionStep(
                step=step_num,
                item_name=name,
                item_price=wi,
                budget_before=w,
                budget_after=w - wi,
                score=vi,
                category=cat,
            ))
            selected.append({
                "name": name,
                "category": cat,
                "price_int": wi,
                "score": vi,
            })
            w -= wi
            step_num += 1

    steps = list(reversed(steps))
    selected = list(reversed(selected))

    # Renumera passos após a inversão para manter numeração sequencial
    for idx, step in enumerate(steps, start=1):
        step.step = idx

    total_price = sum(s.item_price for s in steps)
    total_score = sum(s.score for s in steps)

    return FindSolutionResult(
        steps=steps,
        selected_items=selected,
        total_price=total_price,
        total_score=total_score,
        budget_used=total_price,
        budget_remaining=W - total_price,
        initial_capacity=W,
    )


def find_solution_from_memo(
    memo: dict[tuple[int, int], float],
    weights: list[int],
    values: list[float],
    names: list[str],
    categories: list[str],
    capacity: int | None = None,
) -> FindSolutionResult:
    """
    Reconstrói a solução a partir do memo da versão recursiva.

    Args:
        memo:      dicionário {(i, w): valor} do Knapsack recursivo.
        weights:   pesos dos itens.
        values:    valores dos itens.
        names:     nomes dos itens.
        categories: categorias dos itens.
        capacity:  capacidade para reconstrução.

    Returns:
        FindSolutionResult com os passos de reconstrução.
    """
    n = len(weights)
    if capacity is None:
        # Usa o maior w que aparece no memo
        W = max((k[1] for k in memo.keys()), default=0)
    else:
        W = capacity

    def opt(i: int, w: int) -> float:
        if i == 0 or w == 0:
            return 0.0
        return memo.get((i, w), 0.0)

    steps: list[ReconstructionStep] = []
    selected: list[dict] = []
    w = W
    step_num = 1

    for i in range(n, 0, -1):
        if w <= 0:
            break
        if opt(i, w) != opt(i - 1, w):
            wi = weights[i - 1]
            vi = values[i - 1]
            name = names[i - 1] if i - 1 < len(names) else f"Item {i}"
            cat = categories[i - 1] if i - 1 < len(categories) else "—"

            steps.append(ReconstructionStep(
                step=step_num,
                item_name=name,
                item_price=wi,
                budget_before=w,
                budget_after=w - wi,
                score=vi,
                category=cat,
            ))
            selected.append({
                "name": name,
                "category": cat,
                "price_int": wi,
                "score": vi,
            })
            w -= wi
            step_num += 1

    steps = list(reversed(steps))
    selected = list(reversed(selected))

    for idx, step in enumerate(steps, start=1):
        step.step = idx

    total_price = sum(s.item_price for s in steps)
    total_score = sum(s.score for s in steps)

    return FindSolutionResult(
        steps=steps,
        selected_items=selected,
        total_price=total_price,
        total_score=total_score,
        budget_used=total_price,
        budget_remaining=W - total_price,
        initial_capacity=W,
    )


def format_reconstruction_text(result: FindSolutionResult) -> str:
    """Formata o passo a passo em texto legível."""
    lines = [f"**Orçamento inicial: R$ {result.initial_capacity:,.0f}**", ""]
    for step in result.steps:
        lines.append(
            f"Passo {step.step}: Escolheu **{step.item_name}** ({step.category}) "
            f"— R$ {step.item_price:,.0f}"
        )
        lines.append(
            f"&nbsp;&nbsp;&nbsp;&nbsp;R$ {step.budget_before:,.0f} "
            f"− R$ {step.item_price:,.0f} = "
            f"**R$ {step.budget_after:,.0f}**"
        )
        lines.append("")
    lines.append(f"**Orçamento restante: R$ {result.budget_remaining:,.0f}**")
    lines.append(f"**Preço total: R$ {result.total_price:,.0f}**")
    lines.append(f"**Score total: {result.total_score:.1f}**")
    return "\n".join(lines)
