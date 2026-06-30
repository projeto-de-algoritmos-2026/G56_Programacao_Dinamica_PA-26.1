"""Testes unitários para geração de links de lojas."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from store_links import (
    generate_store_links,
    generate_all_links,
    format_search_url,
    get_store_metadata,
    STORES,
)


class TestGenerateStoreLinks:
    def test_returns_all_stores(self):
        links = generate_store_links("RTX 4060")
        assert set(links.keys()) == set(STORES.keys())

    def test_links_are_strings(self):
        links = generate_store_links("i5-13400F")
        for url in links.values():
            assert isinstance(url, str)

    def test_links_start_with_https(self):
        links = generate_store_links("Ryzen 5 5600")
        for url in links.values():
            assert url.startswith("https://"), f"URL não começa com https: {url}"

    def test_search_term_in_url(self):
        links = generate_store_links("RTX 4060 8GB")
        for store, url in links.items():
            assert "RTX" in url or "4060" in url or "8GB" in url or "rtx" in url.lower(), (
                f"Nome não encontrado na URL da {store}: {url}"
            )

    def test_special_characters_encoded(self):
        links = generate_store_links("Core i7-13700K")
        for url in links.values():
            assert " " not in url, f"Espaço não codificado: {url}"

    def test_empty_search_term(self):
        links = generate_store_links("")
        assert len(links) == len(STORES)

    def test_portuguese_characters(self):
        links = generate_store_links("Placa de Vídeo RTX")
        for url in links.values():
            assert isinstance(url, str)


class TestGenerateAllLinks:
    def test_adds_store_links_field(self):
        items = [{"name": "RTX 4060", "store_search_name": "RTX 4060 8GB"}]
        result = generate_all_links(items)
        assert "store_links" in result[0]

    def test_falls_back_to_name(self):
        items = [{"name": "Intel Core i5-13400F"}]
        result = generate_all_links(items)
        assert "store_links" in result[0]
        assert len(result[0]["store_links"]) == len(STORES)

    def test_preserves_original_fields(self):
        items = [{"name": "GPU", "price_brl": 1500.0, "store_search_name": "GPU Test"}]
        result = generate_all_links(items)
        assert result[0]["price_brl"] == 1500.0

    def test_empty_list(self):
        result = generate_all_links([])
        assert result == []

    def test_multiple_items(self):
        items = [
            {"name": f"Part {i}", "store_search_name": f"Part {i}"}
            for i in range(5)
        ]
        result = generate_all_links(items)
        assert len(result) == 5
        for item in result:
            assert "store_links" in item


class TestFormatSearchUrl:
    def test_valid_store(self):
        url = format_search_url("KaBuM!", "RTX 4060")
        assert "kabum" in url.lower()
        assert "RTX" in url or "4060" in url or "rtx" in url.lower()

    def test_unknown_store_raises(self):
        with pytest.raises(ValueError):
            format_search_url("LojaInexistente", "GPU")

    def test_all_stores_work(self):
        for store in STORES:
            url = format_search_url(store, "test product")
            assert url.startswith("https://")


class TestGetStoreMetadata:
    def test_returns_all_stores(self):
        meta = get_store_metadata()
        assert set(meta.keys()) == set(STORES.keys())

    def test_has_icon_and_color(self):
        meta = get_store_metadata()
        for store, data in meta.items():
            assert "icon" in data, f"Sem ícone para {store}"
            assert "color" in data, f"Sem cor para {store}"

    def test_colors_are_hex_or_named(self):
        meta = get_store_metadata()
        for store, data in meta.items():
            color = data["color"]
            assert color.startswith("#") or color.isalpha(), (
                f"Cor inválida para {store}: {color}"
            )
