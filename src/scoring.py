"""
Cálculo de score para peças de PC e notebooks.

Score geral:
    score = desempenho_base * peso_categoria
            + bonus_jogos
            + bonus_utilidade
            + bonus_custo_beneficio

- desempenho_base: valor de 0-100 do campo performance_score.
- bonus_jogos: soma dos bônus por jogo selecionado x adequação da peça.
- bonus_utilidade: bônus do perfil de uso x peso da categoria.
- bonus_custo_beneficio: performance_score / (price_brl / 1000).
"""

from __future__ import annotations
import pandas as pd

# Perfis de uso e os pesos por categoria
USE_PROFILE_WEIGHTS: dict[str, dict[str, float]] = {
    "gaming_competitive": {
        "CPU": 1.3, "GPU": 1.8, "RAM": 1.1, "Storage": 0.9,
        "Motherboard": 0.8, "PSU": 0.7, "Case": 0.5, "Cooler": 1.0,
    },
    "gaming_aaa": {
        "CPU": 1.2, "GPU": 2.0, "RAM": 1.2, "Storage": 1.0,
        "Motherboard": 0.8, "PSU": 0.8, "Case": 0.5, "Cooler": 1.0,
    },
    "study": {
        "CPU": 1.2, "GPU": 0.5, "RAM": 1.3, "Storage": 1.2,
        "Motherboard": 0.9, "PSU": 0.6, "Case": 0.5, "Cooler": 0.7,
    },
    "programming": {
        "CPU": 1.5, "GPU": 0.6, "RAM": 1.4, "Storage": 1.3,
        "Motherboard": 0.9, "PSU": 0.6, "Case": 0.5, "Cooler": 0.8,
    },
    "engineering": {
        "CPU": 1.5, "GPU": 1.0, "RAM": 1.5, "Storage": 1.2,
        "Motherboard": 0.9, "PSU": 0.7, "Case": 0.5, "Cooler": 0.9,
    },
    "video_editing": {
        "CPU": 1.4, "GPU": 1.3, "RAM": 1.6, "Storage": 1.4,
        "Motherboard": 0.9, "PSU": 0.8, "Case": 0.5, "Cooler": 1.0,
    },
    "design": {
        "CPU": 1.3, "GPU": 1.2, "RAM": 1.4, "Storage": 1.2,
        "Motherboard": 0.8, "PSU": 0.7, "Case": 0.5, "Cooler": 0.8,
    },
    "streaming": {
        "CPU": 1.5, "GPU": 1.5, "RAM": 1.3, "Storage": 1.1,
        "Motherboard": 0.9, "PSU": 0.8, "Case": 0.5, "Cooler": 1.0,
    },
    "general": {
        "CPU": 1.0, "GPU": 0.8, "RAM": 1.0, "Storage": 1.0,
        "Motherboard": 0.8, "PSU": 0.6, "Case": 0.5, "Cooler": 0.7,
    },
}

# Jogos e as categorias mais impactadas
GAME_BONUSES: dict[str, dict[str, float]] = {
    "Fortnite":            {"GPU": 8, "CPU": 6, "RAM": 3},
    "Valorant":            {"CPU": 8, "GPU": 5, "RAM": 3},
    "CS2":                 {"CPU": 7, "GPU": 5, "RAM": 3},
    "GTA V":               {"GPU": 7, "CPU": 5, "RAM": 5},
    "Minecraft":           {"CPU": 6, "RAM": 5, "GPU": 3},
    "League of Legends":   {"CPU": 6, "GPU": 4, "RAM": 3},
    "Warzone":             {"GPU": 9, "CPU": 6, "RAM": 6},
    "Cyberpunk 2077":      {"GPU": 10, "CPU": 5, "RAM": 6},
    "Red Dead Redemption 2":{"GPU": 9, "CPU": 5, "RAM": 6},
    "EA FC":               {"GPU": 6, "CPU": 5, "RAM": 3},
    "The Sims":            {"CPU": 4, "RAM": 5, "GPU": 3},
    "Elden Ring":          {"GPU": 8, "CPU": 5, "RAM": 5},
}

PRIORITY_MULTIPLIERS: dict[str, dict[str, float]] = {
    "performance":    {"perf": 1.5, "cb": 0.5},
    "cost_benefit":   {"perf": 0.8, "cb": 1.5},
    "lowest_price":   {"perf": 0.5, "cb": 2.0},
    "future_upgrade": {"perf": 1.2, "cb": 0.8},
    "low_power":      {"perf": 0.9, "cb": 1.0},
    "portability":    {"perf": 1.0, "cb": 1.0},
}


def compute_part_score(
    row: pd.Series,
    use_profile: str = "gaming_aaa",
    priority: str = "performance",
    selected_games: list[str] | None = None,
) -> float:
    """
    Calcula o score de uma peça de PC.

    Args:
        row:           linha do DataFrame com dados da peça.
        use_profile:   chave do perfil de uso.
        priority:      chave da prioridade.
        selected_games: lista de jogos selecionados pelo usuário.

    Returns:
        Score float normalizado (maior é melhor).
    """
    category = str(row.get("category", "CPU"))
    perf_score = float(row.get("performance_score", 50))
    price = float(row.get("price_brl", 1))

    # Peso da categoria pelo perfil de uso
    weights = USE_PROFILE_WEIGHTS.get(use_profile, USE_PROFILE_WEIGHTS["general"])
    cat_weight = weights.get(category, 1.0)

    # Bônus por jogo
    game_bonus = 0.0
    if selected_games:
        for game in selected_games:
            bonuses = GAME_BONUSES.get(game, {})
            game_bonus += bonuses.get(category, 0)
        game_bonus /= max(len(selected_games), 1)

    # Custo-benefício: score por cada R$ 1000 gastos
    cb_score = perf_score / (price / 1000) if price > 0 else 0

    # Multiplicadores de prioridade
    prio = PRIORITY_MULTIPLIERS.get(priority, PRIORITY_MULTIPLIERS["performance"])
    perf_mult = prio["perf"]
    cb_mult = prio["cb"]

    score = (perf_score * cat_weight * perf_mult) + game_bonus + (cb_score * cb_mult * 0.5)
    return round(score, 4)


def compute_laptop_score(
    row: pd.Series,
    use_profile: str = "gaming_aaa",
    priority: str = "performance",
    selected_games: list[str] | None = None,
) -> float:
    """
    Calcula o score de um notebook considerando todas as suas especificações.

    Args:
        row:           linha do DataFrame com dados do notebook.
        use_profile:   perfil de uso.
        priority:      prioridade de seleção.
        selected_games: jogos selecionados pelo usuário.

    Returns:
        Score float (maior é melhor).
    """
    base_perf = float(row.get("performance_score", 50))
    price = float(row.get("price_brl", 1))
    ram = float(row.get("ram_gb", 8))
    storage = float(row.get("storage_gb", 256))
    screen = float(row.get("screen_size", 15.6))
    gpu_name = str(row.get("gpu", "")).lower()
    cpu_name = str(row.get("cpu", "")).lower()

    # Bônus por RAM
    ram_bonus = min((ram / 8) * 5, 20)

    # Bônus por armazenamento
    storage_bonus = min((storage / 256) * 3, 15)

    # Bônus por GPU dedicada
    gpu_bonus = 0.0
    if "rtx" in gpu_name or "rx" in gpu_name or "gtx" in gpu_name:
        gpu_bonus = 15
        if "4060" in gpu_name or "3070" in gpu_name or "3080" in gpu_name:
            gpu_bonus = 25
        elif "4070" in gpu_name or "4080" in gpu_name or "4090" in gpu_name:
            gpu_bonus = 35

    # Perfil de uso
    profile_bonus = _laptop_profile_bonus(use_profile, gpu_name, cpu_name, ram, storage)

    # Bônus por jogos
    game_bonus = _laptop_game_bonus(selected_games, gpu_name, cpu_name, ram)

    # Custo-benefício
    cb_score = base_perf / (price / 1000) if price > 0 else 0

    prio = PRIORITY_MULTIPLIERS.get(priority, PRIORITY_MULTIPLIERS["performance"])
    perf_mult = prio["perf"]
    cb_mult = prio["cb"]

    score = (
        base_perf * perf_mult
        + ram_bonus
        + storage_bonus
        + gpu_bonus
        + profile_bonus
        + game_bonus
        + cb_score * cb_mult * 0.3
    )
    return round(score, 4)


def _laptop_profile_bonus(
    profile: str,
    gpu: str,
    cpu: str,
    ram: float,
    storage: float,
) -> float:
    """Bônus extra para o perfil de uso no notebook."""
    bonus = 0.0
    if profile in ("gaming_competitive", "gaming_aaa"):
        if "rtx" in gpu or "rx" in gpu or "gtx" in gpu:
            bonus += 10
        if "i7" in cpu or "i9" in cpu or "ryzen 7" in cpu or "ryzen 9" in cpu:
            bonus += 8
    elif profile in ("programming", "engineering"):
        if ram >= 16:
            bonus += 10
        if storage >= 512:
            bonus += 5
        if "i7" in cpu or "ryzen 7" in cpu:
            bonus += 8
    elif profile == "video_editing":
        if ram >= 16:
            bonus += 12
        if storage >= 512:
            bonus += 8
        if "rtx" in gpu or "rx" in gpu:
            bonus += 10
    elif profile == "study":
        bonus += 5  # notebooks leves em geral
    return bonus


def _laptop_game_bonus(
    games: list[str] | None,
    gpu: str,
    cpu: str,
    ram: float,
) -> float:
    """Bônus baseado nos jogos selecionados."""
    if not games:
        return 0.0
    bonus = 0.0
    heavy_games = {"Cyberpunk 2077", "Red Dead Redemption 2", "Warzone", "Elden Ring"}
    competitive_games = {"Valorant", "CS2", "League of Legends", "Fortnite"}

    has_dedicated_gpu = "rtx" in gpu or "gtx" in gpu or "rx" in gpu

    for game in games:
        if game in heavy_games:
            if has_dedicated_gpu:
                bonus += 8
        elif game in competitive_games:
            if "i5" in cpu or "i7" in cpu or "ryzen 5" in cpu or "ryzen 7" in cpu:
                bonus += 5

    return bonus / max(len(games), 1)
