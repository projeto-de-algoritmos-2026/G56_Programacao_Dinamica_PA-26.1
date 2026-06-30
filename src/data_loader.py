"""
Carregamento e validação dos datasets de peças e notebooks.

Suporta:
  - Arquivos CSV locais (sample_pc_parts.csv, sample_laptops.csv).
  - Upload de CSV externo via interface Streamlit.
  - Mapeamento automático de colunas para o formato interno.
"""

from __future__ import annotations
import os
import io
import pandas as pd

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

PARTS_COLUMNS = [
    "id", "name", "category", "brand", "price_brl",
    "performance_score", "socket", "memory_type", "wattage", "store_search_name",
]

LAPTOP_COLUMNS = [
    "id", "name", "brand", "price_brl", "cpu", "gpu",
    "ram_gb", "storage_gb", "screen_size", "performance_score", "store_search_name",
]

# Mapeamentos de nomes alternativos de colunas → nome interno
PARTS_COLUMN_ALIASES: dict[str, str] = {
    "Price": "price_brl", "price": "price_brl", "Price_BRL": "price_brl",
    "Name": "name", "Component": "name", "Part": "name",
    "Category": "category", "Type": "category",
    "Brand": "brand", "Manufacturer": "brand",
    "Score": "performance_score", "Benchmark": "performance_score",
    "Performance": "performance_score",
    "Socket": "socket", "Chipset": "socket",
    "Memory_Type": "memory_type", "DDR": "memory_type",
    "Wattage": "wattage", "TDP": "wattage", "Power": "wattage",
}

LAPTOP_COLUMN_ALIASES: dict[str, str] = {
    "Price": "price_brl", "price": "price_brl", "Price_euros": "price_brl",
    "Company": "brand", "Brand": "brand",
    "Product": "name", "Name": "name",
    "Ram": "ram_gb", "RAM": "ram_gb", "Memory": "ram_gb",
    "Storage": "storage_gb", "SSD": "storage_gb", "HDD": "storage_gb",
    "Screen": "screen_size", "Inches": "screen_size", "screen_size_cm": "screen_size",
    "Cpu": "cpu", "CPU": "cpu", "Processor": "cpu",
    "Gpu": "gpu", "GPU": "gpu", "Graphics": "gpu",
    "Score": "performance_score", "Benchmark": "performance_score",
}


def load_pc_parts(path: str | None = None) -> pd.DataFrame:
    """
    Carrega o dataset de peças de PC.

    Args:
        path: caminho para o CSV; usa o arquivo padrão se None.

    Returns:
        DataFrame limpo e tipado.
    """
    if path is None:
        path = os.path.join(_DATA_DIR, "sample_pc_parts.csv")
    df = pd.read_csv(path)
    df = _normalize_columns(df, PARTS_COLUMN_ALIASES)
    df = _ensure_columns(df, PARTS_COLUMNS)
    df = _clean_parts(df)
    return df


def load_laptops(path: str | None = None) -> pd.DataFrame:
    """
    Carrega o dataset de notebooks.

    Args:
        path: caminho para o CSV; usa o arquivo padrão se None.

    Returns:
        DataFrame limpo e tipado.
    """
    if path is None:
        path = os.path.join(_DATA_DIR, "sample_laptops.csv")
    df = pd.read_csv(path)
    df = _normalize_columns(df, LAPTOP_COLUMN_ALIASES)
    df = _ensure_columns(df, LAPTOP_COLUMNS)
    df = _clean_laptops(df)
    return df


def load_from_upload(uploaded_file, file_type: str = "parts") -> pd.DataFrame:
    """
    Carrega um arquivo CSV enviado via Streamlit file_uploader.

    Args:
        uploaded_file: objeto retornado por st.file_uploader.
        file_type:     'parts' ou 'laptops'.

    Returns:
        DataFrame processado.
    """
    content = uploaded_file.read()
    df = pd.read_csv(io.BytesIO(content))

    if file_type == "parts":
        df = _normalize_columns(df, PARTS_COLUMN_ALIASES)
        df = _ensure_columns(df, PARTS_COLUMNS)
        df = _clean_parts(df)
    else:
        df = _normalize_columns(df, LAPTOP_COLUMN_ALIASES)
        df = _ensure_columns(df, LAPTOP_COLUMNS)
        df = _clean_laptops(df)

    return df


def _normalize_columns(df: pd.DataFrame, aliases: dict[str, str]) -> pd.DataFrame:
    """Renomeia colunas usando os mapeamentos de alias."""
    rename_map = {col: aliases[col] for col in df.columns if col in aliases}
    return df.rename(columns=rename_map)


def _ensure_columns(df: pd.DataFrame, expected: list[str]) -> pd.DataFrame:
    """Adiciona colunas faltantes com valores padrão."""
    for col in expected:
        if col not in df.columns:
            if col in ("price_brl", "performance_score", "ram_gb",
                       "storage_gb", "screen_size", "wattage"):
                df[col] = 0.0
            elif col == "id":
                df[col] = range(1, len(df) + 1)
            else:
                df[col] = ""
    return df


def _clean_parts(df: pd.DataFrame) -> pd.DataFrame:
    """Limpeza e tipagem do dataset de peças."""
    df = df.copy()
    df["price_brl"] = pd.to_numeric(df["price_brl"], errors="coerce").fillna(0)
    df["performance_score"] = pd.to_numeric(df["performance_score"], errors="coerce").fillna(50)
    df["wattage"] = pd.to_numeric(df["wattage"], errors="coerce").fillna(0)

    df = df[df["price_brl"] > 0].copy()
    df["name"] = df["name"].fillna("Sem nome").astype(str)
    df["category"] = df["category"].fillna("Outro").astype(str)
    df["brand"] = df["brand"].fillna("").astype(str)
    df["socket"] = df["socket"].fillna("").astype(str)
    df["memory_type"] = df["memory_type"].fillna("").astype(str)
    df["store_search_name"] = df.apply(
        lambda r: r["store_search_name"] if r["store_search_name"] else r["name"],
        axis=1,
    ).astype(str)
    df = df.reset_index(drop=True)
    return df


def _clean_laptops(df: pd.DataFrame) -> pd.DataFrame:
    """Limpeza e tipagem do dataset de notebooks."""
    df = df.copy()
    df["price_brl"] = pd.to_numeric(df["price_brl"], errors="coerce").fillna(0)
    df["performance_score"] = pd.to_numeric(df["performance_score"], errors="coerce").fillna(50)
    df["ram_gb"] = pd.to_numeric(df["ram_gb"], errors="coerce").fillna(8)
    df["storage_gb"] = pd.to_numeric(df["storage_gb"], errors="coerce").fillna(256)
    df["screen_size"] = pd.to_numeric(df["screen_size"], errors="coerce").fillna(15.6)

    df = df[df["price_brl"] > 0].copy()
    df["name"] = df["name"].fillna("Sem nome").astype(str)
    df["brand"] = df["brand"].fillna("").astype(str)
    df["cpu"] = df["cpu"].fillna("").astype(str)
    df["gpu"] = df["gpu"].fillna("").astype(str)
    df["store_search_name"] = df.apply(
        lambda r: r["store_search_name"] if r["store_search_name"] else r["name"],
        axis=1,
    ).astype(str)
    df = df.reset_index(drop=True)
    return df


def get_dataset_stats(df: pd.DataFrame, dataset_type: str = "parts") -> dict:
    """Retorna estatísticas básicas do dataset para exibição na interface."""
    stats: dict = {
        "total_items": len(df),
        "price_min": df["price_brl"].min(),
        "price_max": df["price_brl"].max(),
        "price_mean": df["price_brl"].mean(),
        "price_median": df["price_brl"].median(),
    }
    if dataset_type == "parts" and "category" in df.columns:
        stats["categories"] = df["category"].value_counts().to_dict()
    if dataset_type == "laptops" and "brand" in df.columns:
        stats["brands"] = df["brand"].value_counts().to_dict()
    return stats
