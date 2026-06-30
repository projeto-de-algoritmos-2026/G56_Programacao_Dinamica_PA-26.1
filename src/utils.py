"""
Utilitários gerais do projeto.
"""

from __future__ import annotations
import re


USE_PROFILES = {
    "Jogos Competitivos": "gaming_competitive",
    "Jogos AAA": "gaming_aaa",
    "Estudos": "study",
    "Programação": "programming",
    "Engenharia": "engineering",
    "Edição de Vídeo": "video_editing",
    "Design": "design",
    "Streaming": "streaming",
    "Uso Geral": "general",
}

PRIORITIES = {
    "Melhor Desempenho": "performance",
    "Melhor Custo-Benefício": "cost_benefit",
    "Menor Preço": "lowest_price",
    "Upgrade Futuro": "future_upgrade",
    "Baixo Consumo": "low_power",
    "Portabilidade": "portability",
}

GAMES = [
    "Fortnite", "Valorant", "CS2", "GTA V", "Minecraft",
    "League of Legends", "Warzone", "Cyberpunk 2077",
    "Red Dead Redemption 2", "EA FC", "The Sims", "Elden Ring",
]

BUDGET_PRESETS = [2000, 3000, 4000, 5000, 6000, 8000, 10000, 12000, 15000, 20000]

CATEGORY_ICONS = {
    "CPU": "🔲",
    "GPU": "🎮",
    "Motherboard": "🔌",
    "RAM": "💾",
    "Storage": "💿",
    "PSU": "⚡",
    "Case": "🖥️",
    "Cooler": "❄️",
}

CATEGORY_ORDER = ["CPU", "GPU", "Motherboard", "RAM", "Storage", "PSU", "Case", "Cooler"]


def format_brl(value: float) -> str:
    """Formata um valor como moeda BRL."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def profile_label_to_key(label: str) -> str:
    return USE_PROFILES.get(label, "general")


def priority_label_to_key(label: str) -> str:
    return PRIORITIES.get(label, "performance")


def extract_wattage_from_name(name: str) -> int:
    """Extrai a potência em Watts do nome de uma fonte, se disponível."""
    match = re.search(r"(\d{3,4})\s*[Ww]", name)
    return int(match.group(1)) if match else 0


def truncate_name(name: str, max_len: int = 35) -> str:
    """Trunca nomes longos para exibição em tabelas."""
    return name if len(name) <= max_len else name[:max_len - 3] + "..."


def get_performance_tier(score: float) -> str:
    """Classifica o score em faixa de desempenho."""
    if score >= 90:
        return "🔥 Extremo"
    if score >= 75:
        return "⚡ Alto"
    if score >= 55:
        return "✅ Médio-Alto"
    if score >= 40:
        return "📊 Médio"
    return "💡 Entrada"


def get_laptop_tier(score: float) -> str:
    """Classifica notebooks por tier de desempenho."""
    if score >= 200:
        return "🔥 Premium Gamer"
    if score >= 150:
        return "⚡ Gamer"
    if score >= 100:
        return "✅ Intermediário"
    if score >= 70:
        return "📊 Básico"
    return "💡 Ultraleve"


def sort_items_by_category(items: list[dict]) -> list[dict]:
    """Ordena itens pela ordem padrão de categorias."""
    order = {cat: i for i, cat in enumerate(CATEGORY_ORDER)}
    return sorted(items, key=lambda x: order.get(x.get("category", ""), 99))
