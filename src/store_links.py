"""
Geração de links de busca para lojas brasileiras de informática.

Os links levam o usuário diretamente para a página de busca de cada loja
com o nome da peça pré-preenchido. Nenhuma requisição é feita pelo sistema;
o usuário clica e abre no navegador.
"""

from __future__ import annotations
import urllib.parse


STORES = {
    "KaBuM!": {
        "url": "https://www.kabum.com.br/busca/{query}",
        "icon": "🛒",
        "color": "#FF6B00",
    },
    "TerabyteShop": {
        "url": "https://www.terabyteshop.com.br/busca?str={query}",
        "icon": "💾",
        "color": "#0056b3",
    },
    "Pichau": {
        "url": "https://www.pichau.com.br/search?q={query}",
        "icon": "🖥️",
        "color": "#6c3fff",
    },
    "Amazon Brasil": {
        "url": "https://www.amazon.com.br/s?k={query}",
        "icon": "📦",
        "color": "#FF9900",
    },
    "Mercado Livre": {
        "url": "https://lista.mercadolivre.com.br/{query}",
        "icon": "🟡",
        "color": "#FFE600",
    },
}


def generate_store_links(search_name: str) -> dict[str, str]:
    """
    Gera links de busca para todas as lojas cadastradas.

    Args:
        search_name: nome da peça para usar na busca (campo store_search_name).

    Returns:
        Dicionário {nome_da_loja: url_de_busca}.
    """
    encoded = urllib.parse.quote_plus(search_name)
    links: dict[str, str] = {}
    for store, config in STORES.items():
        links[store] = config["url"].format(query=encoded)
    return links


def generate_all_links(items: list[dict]) -> list[dict]:
    """
    Adiciona links de busca a cada item da lista.

    Args:
        items: lista de peças/notebooks com campo 'store_search_name' ou 'name'.

    Returns:
        Lista de dicionários com campo 'store_links' adicionado.
    """
    result = []
    for item in items:
        search_name = item.get("store_search_name") or item.get("name", "")
        store_links = generate_store_links(search_name)
        result.append({**item, "store_links": store_links})
    return result


def get_store_metadata() -> dict[str, dict]:
    """Retorna metadados das lojas (ícone, cor) para renderização na UI."""
    return {name: {"icon": cfg["icon"], "color": cfg["color"]} for name, cfg in STORES.items()}


def format_search_url(store_name: str, search_term: str) -> str:
    """
    Retorna a URL de busca formatada para uma loja específica.

    Args:
        store_name: nome exato da loja (chave em STORES).
        search_term: termo a pesquisar.

    Returns:
        URL pronta para abertura no navegador.
    """
    if store_name not in STORES:
        raise ValueError(f"Loja desconhecida: {store_name}")
    encoded = urllib.parse.quote_plus(search_term)
    return STORES[store_name]["url"].format(query=encoded)
