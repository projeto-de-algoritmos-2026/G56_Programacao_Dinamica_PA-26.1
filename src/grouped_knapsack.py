"""
Grouped Knapsack (Multiple Choice Knapsack) para montagem de PC.

Em vez de escolher livremente qualquer item, o algoritmo escolhe
no máximo um item por grupo (categoria de peça). Isso garante que
a configuração final tenha exatamente uma CPU, uma GPU, etc.

Recorrência para G grupos e capacidade W:
    dp[g][w] = max(dp[g-1][w],
                   max over items i in group g: dp[g-1][w - wi] + vi)

Complexidade: O(G * max_group_size * W) — linear no número de grupos
em vez de exponencial.
"""

from __future__ import annotations
import time
from dataclasses import dataclass


REQUIRED_CATEGORIES = ["CPU", "Motherboard", "RAM", "Storage", "PSU", "Case"]
OPTIONAL_CATEGORIES = ["GPU", "Cooler"]


@dataclass
class GroupedKnapsackResult:
    total_value: float
    total_price: int
    selected_items: list[dict]
    execution_time_ms: float
    states_computed: int
    capacity_used: int
    capacity_remaining: int


def grouped_knapsack(
    groups: dict[str, list[dict]],
    capacity: int,
    required_categories: list[str] | None = None,
) -> GroupedKnapsackResult:
    """
    Executa o Grouped Knapsack para montagem de PC.

    Args:
        groups:    dicionário {categoria: [itens]} onde cada item tem
                   'price_int' (peso) e 'score' (valor).
        capacity:  orçamento total em unidades inteiras.
        required_categories: categorias obrigatórias na configuração.

    Returns:
        GroupedKnapsackResult com os itens escolhidos e métricas.
    """
    if required_categories is None:
        required_categories = REQUIRED_CATEGORIES

    group_names = list(groups.keys())
    G = len(group_names)
    W = capacity

    start = time.perf_counter()
    states = 0

    # dp[g][w] = melhor score usando os primeiros g grupos e orçamento w
    # Armazenamos G+1 linhas para reconstrução
    dp: list[list[float]] = [[0.0] * (W + 1) for _ in range(G + 1)]
    # choice[g][w] = índice do item escolhido no grupo g para o estado (g,w)
    choice: list[list[int]] = [[-1] * (W + 1) for _ in range(G + 1)]

    for g in range(1, G + 1):
        group_key = group_names[g - 1]
        items = groups[group_key]

        for w in range(W + 1):
            states += 1
            # Opção 1: não escolher nenhum item deste grupo
            dp[g][w] = dp[g - 1][w]
            choice[g][w] = -1

            # Opção 2: escolher um item do grupo
            for idx, item in enumerate(items):
                wi = item["price_int"]
                vi = item["score"]
                if wi <= w:
                    candidate = dp[g - 1][w - wi] + vi
                    if candidate > dp[g][w]:
                        dp[g][w] = candidate
                        choice[g][w] = idx

    elapsed_ms = (time.perf_counter() - start) * 1000

    selected = _reconstruct_grouped(dp, choice, groups, group_names, G, W)

    total_price = sum(item["price_int"] for item in selected)
    total_value = sum(item["score"] for item in selected)

    return GroupedKnapsackResult(
        total_value=total_value,
        total_price=total_price,
        selected_items=selected,
        execution_time_ms=elapsed_ms,
        states_computed=states,
        capacity_used=total_price,
        capacity_remaining=W - total_price,
    )


def _reconstruct_grouped(
    dp: list[list[float]],
    choice: list[list[int]],
    groups: dict[str, list[dict]],
    group_names: list[str],
    G: int,
    W: int,
) -> list[dict]:
    """Backtracking pela tabela DP para recuperar os itens selecionados."""
    selected: list[dict] = []
    w = W
    for g in range(G, 0, -1):
        idx = choice[g][w]
        if idx >= 0:
            group_key = group_names[g - 1]
            item = groups[group_key][idx]
            selected.append({**item, "category": group_key})
            w -= item["price_int"]
    return list(reversed(selected))


def prepare_groups(
    df_parts,
    use_profile: str = "gaming",
    priority: str = "performance",
) -> dict[str, list[dict]]:
    """
    Converte o DataFrame de peças em grupos para o Grouped Knapsack.

    Args:
        df_parts:    DataFrame com colunas padrão de peças.
        use_profile: perfil de uso para ajuste de score.
        priority:    prioridade (performance, cost_benefit, etc.).

    Returns:
        Dicionário {categoria: [lista de itens com price_int e score]}.
    """
    from scoring import compute_part_score  # evita importação circular

    groups: dict[str, list[dict]] = {}
    for category, group_df in df_parts.groupby("category"):
        items = []
        for _, row in group_df.iterrows():
            score = compute_part_score(row, use_profile, priority)
            items.append({
                "name": row["name"],
                "brand": row.get("brand", ""),
                "price_int": int(row["price_brl"]),
                "price_brl": float(row["price_brl"]),
                "score": score,
                "performance_score": float(row.get("performance_score", 50)),
                "socket": str(row.get("socket", "")),
                "memory_type": str(row.get("memory_type", "")),
                "wattage": float(row.get("wattage", 0)),
                "store_search_name": str(row.get("store_search_name", row["name"])),
            })
        # Ordena por score descendente para reconstrução mais rápida
        items.sort(key=lambda x: x["score"], reverse=True)
        groups[str(category)] = items

    return groups
