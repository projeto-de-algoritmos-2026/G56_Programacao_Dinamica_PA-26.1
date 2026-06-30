"""
PC Build Optimizer — interface principal Streamlit.

Navegação via sidebar com 9 páginas:
  Home | Dataset | Montar PC | Notebook | Knapsack Iterativo |
  Knapsack Recursivo | Comparação | Find Solution | Links de Compra
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import time

from data_loader import load_pc_parts, load_laptops, load_from_upload, get_dataset_stats
from preprocessing import prepare_knapsack_inputs, apply_budget_step, filter_by_budget
from scoring import compute_part_score, compute_laptop_score
from compatibility import check_compatibility, get_compatibility_emoji
from knapsack_iterativo import knapsack_iterativo, get_dp_table_display
from knapsack_recursivo import knapsack_recursivo, get_memo_summary
from grouped_knapsack import grouped_knapsack, prepare_groups
from find_solution import (
    find_solution_from_dp,
    find_solution_from_memo,
    format_reconstruction_text,
)
from store_links import generate_store_links, get_store_metadata, generate_all_links
from charts import (
    chart_price_distribution,
    chart_score_by_category,
    chart_selected_parts,
    chart_budget_usage,
    chart_algorithm_comparison,
    chart_dp_table_heatmap,
    chart_laptop_ranking,
    chart_price_vs_score,
    chart_category_breakdown,
)
from metrics import compare_algorithms, format_metrics_table, efficiency_ratio
from utils import (
    USE_PROFILES, PRIORITIES, GAMES, BUDGET_PRESETS,
    CATEGORY_ICONS, format_brl, profile_label_to_key, priority_label_to_key,
    get_performance_tier, get_laptop_tier, sort_items_by_category, truncate_name,
)

st.set_page_config(
    page_title="PC Build Optimizer",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS customizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #7B68EE, #20B2AA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .card {
        background: #1a1f2e;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border: 1px solid #2d3748;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e, #2d3748);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #4a5568;
    }
    .store-btn {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        margin: 0.2rem;
        font-weight: 600;
        text-decoration: none;
        font-size: 0.85rem;
    }
    .category-badge {
        background: #2d3748;
        border-radius: 20px;
        padding: 0.2rem 0.7rem;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .compat-ok { color: #4CAF50; font-weight: 700; }
    .compat-warn { color: #FFC107; font-weight: 700; }
    .compat-err { color: #F44336; font-weight: 700; }
    .step-box {
        background: #1e2535;
        border-left: 4px solid #7B68EE;
        padding: 0.6rem 1rem;
        margin: 0.4rem 0;
        border-radius: 0 6px 6px 0;
    }
</style>
""", unsafe_allow_html=True)


# ─── Estado global ───────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "df_parts": None,
        "df_laptops": None,
        "last_build": None,           # resultado grouped knapsack
        "last_laptop": None,          # lista de notebooks ranqueados
        "last_iter_result": None,
        "last_rec_result": None,
        "last_iter_weights": [],
        "last_iter_values": [],
        "last_iter_names": [],
        "last_iter_cats": [],
        "last_budget": 5000,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


# ─── Helpers de carregamento ─────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _load_parts():
    return load_pc_parts()


@st.cache_data(show_spinner=False)
def _load_laptops():
    return load_laptops()


def get_parts() -> pd.DataFrame:
    if st.session_state["df_parts"] is None:
        st.session_state["df_parts"] = _load_parts()
    return st.session_state["df_parts"]


def get_laptops() -> pd.DataFrame:
    if st.session_state["df_laptops"] is None:
        st.session_state["df_laptops"] = _load_laptops()
    return st.session_state["df_laptops"]


# ════════════════════════════════════════════════════════════════════════════
# PÁGINAS
# ════════════════════════════════════════════════════════════════════════════

def page_home():
    st.markdown('<div class="main-title">🖥️ PC Build Optimizer</div>', unsafe_allow_html=True)
    st.markdown("#### Sistema inteligente para montagem de PC Gamer e seleção de notebooks")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card"><h4>🎯 O que é?</h4><p>Ferramenta que usa <b>Programação Dinâmica</b> (algoritmo Knapsack) para encontrar a configuração de PC ou notebook com melhor custo-benefício dentro do seu orçamento.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><h4>⚙️ Como funciona?</h4><p>Você informa orçamento, jogos desejados e perfil de uso. O sistema calcula automaticamente a melhor combinação de peças, maximizando o score de desempenho.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><h4>🧠 Algoritmos</h4><p>Dois algoritmos disponíveis: <b>Knapsack Iterativo</b> (bottom-up) e <b>Knapsack Recursivo com Memoization</b> (top-down). Compare desempenho e resultados.</p></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 Como usar")
    steps = [
        ("1️⃣", "Dataset", "Visualize e filtre os dados de peças e notebooks."),
        ("2️⃣", "Montar PC / Notebook", "Informe orçamento, jogos e perfil de uso."),
        ("3️⃣", "Knapsack", "Execute o algoritmo iterativo ou recursivo."),
        ("4️⃣", "Find Solution", "Veja o passo a passo da reconstrução da solução."),
        ("5️⃣", "Links de Compra", "Acesse links de busca nas principais lojas brasileiras."),
    ]
    cols = st.columns(len(steps))
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f'<div class="card" style="text-align:center"><div style="font-size:2rem">{num}</div><b>{title}</b><br><small>{desc}</small></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("🧮 O Algoritmo Knapsack")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("""
**Problema da Mochila (0/1 Knapsack):**

Dado um conjunto de itens com pesos e valores, e uma mochila com capacidade W,
escolha os itens que maximizem o valor total sem exceder a capacidade.

```
OPT(i, w) = 0                          se i = 0
OPT(i, w) = OPT(i-1, w)               se weight[i] > w
OPT(i, w) = max(OPT(i-1, w),          caso contrário
                OPT(i-1, w-w[i]) + v[i])
```

**Adaptação para PC:** usamos o *Grouped Knapsack*, que garante que
exatamente uma peça de cada categoria seja escolhida.
        """)
    with col_r:
        st.markdown("""
**Modelagem:**

| Conceito | Mapeamento |
|----------|------------|
| Capacidade W | Orçamento (R$) |
| Peso do item | Preço da peça |
| Valor do item | Score de desempenho |
| Grupo | Categoria de peça |

**Score da peça:**
```
score = desempenho_base × peso_categoria
      + bônus por jogos
      + bônus por perfil de uso
      + bônus custo-benefício
```
        """)

    st.divider()
    st.subheader("📦 Exemplo de Uso")
    with st.expander("Ver exemplo completo"):
        st.markdown("""
**Cenário:** orçamento de R$5.000, uso: Jogos AAA, jogos: Cyberpunk 2077 + Elden Ring.

O sistema irá:
1. Calcular o score de cada peça considerando o perfil "Jogos AAA" e as GPUs pesadas exigidas pelos jogos.
2. Rodar o Grouped Knapsack para selecionar 1 peça de cada categoria.
3. Verificar compatibilidade (socket CPU/placa-mãe, memória, potência da fonte).
4. Exibir a configuração final com preço, score e links para comprar cada peça.

**Resultado esperado:** uma GPU discreta de boa performance (ex: RTX 4060), CPU mid-range, 16GB RAM, SSD NVMe e fonte com capacidade adequada.
        """)


def page_dataset():
    st.title("📊 Dataset")
    st.markdown("Visualize, filtre e faça upload dos dados de peças e notebooks.")

    tab1, tab2 = st.tabs(["🔧 Peças de PC", "💻 Notebooks"])

    with tab1:
        _dataset_tab_parts()
    with tab2:
        _dataset_tab_laptops()


def _dataset_tab_parts():
    st.subheader("Dataset de Peças de PC")

    uploaded = st.file_uploader(
        "Upload CSV de peças (opcional — substitui o dataset padrão)",
        type="csv", key="upload_parts",
    )
    if uploaded:
        try:
            df = load_from_upload(uploaded, "parts")
            st.session_state["df_parts"] = df
            st.success(f"Dataset carregado: {len(df)} peças.")
        except Exception as e:
            st.error(f"Erro ao carregar arquivo: {e}")

    df = get_parts()
    stats = get_dataset_stats(df, "parts")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Peças", stats["total_items"])
    c2.metric("Preço Mínimo", format_brl(stats["price_min"]))
    c3.metric("Preço Máximo", format_brl(stats["price_max"]))
    c4.metric("Preço Médio", format_brl(stats["price_mean"]))

    st.divider()
    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        cats = ["Todas"] + sorted(df["category"].unique().tolist())
        cat_filter = st.selectbox("Categoria", cats, key="parts_cat_filter")
    with col_f2:
        brand_opts = ["Todas"] + sorted(df["brand"].unique().tolist())
        brand_filter = st.selectbox("Marca", brand_opts, key="parts_brand_filter")
    with col_f3:
        max_price = int(df["price_brl"].max()) + 1
        price_range = st.slider("Faixa de Preço (R$)", 0, max_price, (0, max_price), key="parts_price")

    filtered = df.copy()
    if cat_filter != "Todas":
        filtered = filtered[filtered["category"] == cat_filter]
    if brand_filter != "Todas":
        filtered = filtered[filtered["brand"] == brand_filter]
    filtered = filtered[
        (filtered["price_brl"] >= price_range[0]) &
        (filtered["price_brl"] <= price_range[1])
    ]

    st.markdown(f"**{len(filtered)} peças encontradas**")
    st.dataframe(
        filtered[["name", "category", "brand", "price_brl", "performance_score", "socket"]],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.plotly_chart(chart_price_distribution(filtered, "Distribuição de Preços (filtrado)"),
                        use_container_width=True)
    with col_g2:
        if "category" in filtered.columns and filtered["category"].nunique() > 1:
            st.plotly_chart(chart_score_by_category(filtered), use_container_width=True)

    st.plotly_chart(chart_price_vs_score(filtered), use_container_width=True)


def _dataset_tab_laptops():
    st.subheader("Dataset de Notebooks")

    uploaded = st.file_uploader(
        "Upload CSV de notebooks (opcional)",
        type="csv", key="upload_laptops",
    )
    if uploaded:
        try:
            df = load_from_upload(uploaded, "laptops")
            st.session_state["df_laptops"] = df
            st.success(f"Dataset carregado: {len(df)} notebooks.")
        except Exception as e:
            st.error(f"Erro ao carregar arquivo: {e}")

    df = get_laptops()
    stats = get_dataset_stats(df, "laptops")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Notebooks", stats["total_items"])
    c2.metric("Preço Mínimo", format_brl(stats["price_min"]))
    c3.metric("Preço Máximo", format_brl(stats["price_max"]))
    c4.metric("Preço Médio", format_brl(stats["price_mean"]))

    st.divider()
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        brand_opts = ["Todas"] + sorted(df["brand"].unique().tolist())
        brand_filter = st.selectbox("Marca", brand_opts, key="laptop_brand_filter")
    with col_f2:
        max_p = int(df["price_brl"].max()) + 1
        price_range = st.slider("Faixa de Preço (R$)", 0, max_p, (0, max_p), key="laptop_price")

    filtered = df.copy()
    if brand_filter != "Todas":
        filtered = filtered[filtered["brand"] == brand_filter]
    filtered = filtered[
        (filtered["price_brl"] >= price_range[0]) &
        (filtered["price_brl"] <= price_range[1])
    ]

    st.markdown(f"**{len(filtered)} notebooks encontrados**")
    st.dataframe(
        filtered[["name", "brand", "price_brl", "cpu", "gpu", "ram_gb", "storage_gb", "screen_size", "performance_score"]],
        use_container_width=True, hide_index=True,
    )

    st.divider()
    st.plotly_chart(chart_price_distribution(filtered, "Distribuição de Preços (Notebooks)"),
                    use_container_width=True)
    st.plotly_chart(chart_price_vs_score(filtered, color_col="brand"), use_container_width=True)


def page_montar_pc():
    st.title("🔧 Montar PC Gamer")
    st.markdown("Configure as preferências e deixe o algoritmo escolher a melhor combinação de peças.")

    df = get_parts()

    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ Configurações do PC")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Parâmetros")

        budget = st.number_input(
            "Orçamento Total (R$)",
            min_value=1000, max_value=100000,
            value=5000, step=500,
            help="Valor máximo disponível para gastar em peças.",
        )

        preset_col1, preset_col2 = st.columns(2)
        with preset_col1:
            if st.button("R$ 3.000"):
                budget = 3000
        with preset_col2:
            if st.button("R$ 5.000"):
                budget = 5000
        preset_col3, preset_col4 = st.columns(2)
        with preset_col3:
            if st.button("R$ 8.000"):
                budget = 8000
        with preset_col4:
            if st.button("R$ 12.000"):
                budget = 12000

        st.markdown("---")
        use_label = st.selectbox("Uso Principal", list(USE_PROFILES.keys()))
        priority_label = st.selectbox("Prioridade", list(PRIORITIES.keys()))

        st.markdown("---")
        games = st.multiselect(
            "Jogos Desejados",
            GAMES,
            default=["CS2", "Valorant"],
            help="Selecione os jogos para otimizar as peças escolhidas.",
        )

        st.markdown("---")
        algorithm = st.radio(
            "Algoritmo",
            ["Grouped Knapsack (Recomendado)", "Knapsack Clássico (Comparação)"],
        )

        run_btn = st.button("🚀 Otimizar Configuração", type="primary", use_container_width=True)

    with col2:
        if run_btn:
            _run_pc_optimization(df, budget, use_label, priority_label, games, algorithm)
        elif st.session_state["last_build"] is not None:
            _display_build_result(st.session_state["last_build"], budget)
        else:
            st.info("Configure os parâmetros ao lado e clique em **Otimizar Configuração**.")
            st.markdown("""
**Dica:** O algoritmo Grouped Knapsack garante que você receba exatamente uma peça
de cada categoria (CPU, GPU, placa-mãe, RAM, armazenamento, fonte, gabinete e cooler).

O score de cada peça é calculado com base no desempenho, no perfil de uso
escolhido e nos jogos selecionados.
            """)


def _run_pc_optimization(df, budget, use_label, priority_label, games, algorithm):
    use_profile = profile_label_to_key(use_label)
    priority = priority_label_to_key(priority_label)

    with st.spinner("Calculando configuração ideal..."):
        df_filtered = filter_by_budget(df, budget)
        df_filtered = df_filtered.copy()
        df_filtered["computed_score"] = df_filtered.apply(
            lambda r: compute_part_score(r, use_profile, priority, games), axis=1
        )

        if "Grouped" in algorithm:
            groups = prepare_groups(df_filtered, use_profile, priority)
            result = grouped_knapsack(groups, int(budget))
            build_items = result.selected_items
            total_price = result.total_price
            total_score = result.total_value
            exec_time = result.execution_time_ms
        else:
            weights, values, names, cats = prepare_knapsack_inputs(df_filtered, budget, "computed_score")
            scaled_w, scaled_cap, step = apply_budget_step(weights, budget)
            k_result = knapsack_iterativo(scaled_w, values, scaled_cap)
            st.session_state["last_iter_result"] = k_result
            st.session_state["last_iter_weights"] = weights
            st.session_state["last_iter_values"] = values
            st.session_state["last_iter_names"] = names
            st.session_state["last_iter_cats"] = cats
            st.session_state["last_budget"] = int(budget)

            build_items = [
                {
                    "name": names[i],
                    "category": cats[i],
                    "price_int": weights[i],
                    "price_brl": float(weights[i]),
                    "score": values[i],
                    "store_search_name": names[i],
                }
                for i in k_result.selected_indices
            ]
            total_price = sum(weights[i] for i in k_result.selected_indices)
            total_score = k_result.value
            exec_time = k_result.execution_time_ms

        st.session_state["last_build"] = {
            "items": build_items,
            "total_price": total_price,
            "total_score": total_score,
            "budget": budget,
            "exec_time": exec_time,
            "use_label": use_label,
            "priority_label": priority_label,
            "games": games,
        }
        st.session_state["last_budget"] = int(budget)

    _display_build_result(st.session_state["last_build"], budget)


def _display_build_result(build: dict, budget: float):
    items = build["items"]
    total_price = build["total_price"]
    total_score = build["total_score"]
    exec_time = build["exec_time"]

    if not items:
        st.warning("Nenhuma configuração encontrada para este orçamento. Tente aumentar o valor.")
        return

    st.success(f"Configuração encontrada em {exec_time:.2f}ms!")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Preço Total", format_brl(total_price))
    c2.metric("Orçamento Restante", format_brl(budget - total_price))
    c3.metric("Score Total", f"{total_score:.1f}")
    c4.metric("Tier", get_performance_tier(total_score / max(len(items), 1)))

    st.divider()
    st.subheader("🔩 Peças Escolhidas")
    items_sorted = sort_items_by_category(items)
    for item in items_sorted:
        cat = item.get("category", "")
        icon = CATEGORY_ICONS.get(cat, "🔧")
        price = float(item.get("price_brl", item.get("price_int", 0)))
        score = item.get("score", 0)
        name = item.get("name", "")
        search = item.get("store_search_name", name)

        with st.expander(f"{icon} {cat}: **{truncate_name(name, 50)}** — {format_brl(price)} | Score: {score:.1f}"):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                links = generate_store_links(search)
                st.markdown("**Links de compra:**")
                meta = get_store_metadata()
                link_html = " ".join([
                    f'<a href="{url}" target="_blank" class="store-btn" '
                    f'style="background:{meta[store]["color"]};color:white;">'
                    f'{meta[store]["icon"]} {store}</a>'
                    for store, url in links.items()
                ])
                st.markdown(link_html, unsafe_allow_html=True)
            with col_b:
                st.metric("Preço", format_brl(price))
                st.metric("Score", f"{score:.1f}")

    st.divider()
    compat_items = [
        {**item, "price_brl": float(item.get("price_brl", item.get("price_int", 0)))}
        for item in items
    ]
    report = check_compatibility(compat_items)
    emoji = get_compatibility_emoji(report)
    st.subheader(f"{emoji} Compatibilidade")
    if report.errors:
        for err in report.errors:
            st.error(err)
    if report.warnings:
        for warn in report.warnings:
            st.warning(warn)
    if report.is_compatible and not report.warnings:
        st.success(report.summary)

    st.divider()
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.plotly_chart(chart_selected_parts(items_sorted), use_container_width=True)
    with col_g2:
        st.plotly_chart(chart_budget_usage(total_price, budget - total_price), use_container_width=True)
    st.plotly_chart(chart_category_breakdown(items_sorted), use_container_width=True)


def page_notebook():
    st.title("💻 Escolher Notebook")
    st.markdown("Encontre o melhor notebook para suas necessidades dentro do orçamento.")

    df = get_laptops()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Parâmetros")
        budget = st.number_input(
            "Orçamento (R$)",
            min_value=1000, max_value=50000, value=6000, step=500,
        )
        use_label = st.selectbox("Uso Principal", list(USE_PROFILES.keys()), key="nb_use")
        priority_label = st.selectbox("Prioridade", list(PRIORITIES.keys()), key="nb_prio")
        games = st.multiselect("Jogos Desejados", GAMES, default=["CS2"], key="nb_games")

        st.markdown("---")
        st.markdown("**Filtros adicionais**")
        min_ram = st.selectbox("RAM Mínima (GB)", [4, 8, 16, 32], index=1)
        min_storage = st.selectbox("Armazenamento Mínimo (GB)", [128, 256, 512, 1000], index=1)
        require_dedicated_gpu = st.checkbox("GPU Dedicada Obrigatória", value=False)
        screen_opts = ["Qualquer", "13–14\"", "15–16\"", "17\"+"]
        screen_pref = st.selectbox("Tamanho de Tela", screen_opts)

        run_btn = st.button("🔍 Recomendar Notebooks", type="primary", use_container_width=True)

    with col2:
        if run_btn:
            _run_notebook_recommendation(
                df, budget, use_label, priority_label, games,
                min_ram, min_storage, require_dedicated_gpu, screen_pref,
            )
        elif st.session_state["last_laptop"] is not None:
            _display_laptop_result(st.session_state["last_laptop"], budget)
        else:
            st.info("Configure os parâmetros ao lado e clique em **Recomendar Notebooks**.")


def _run_notebook_recommendation(
    df, budget, use_label, priority_label, games,
    min_ram, min_storage, require_dedicated_gpu, screen_pref,
):
    use_profile = profile_label_to_key(use_label)
    priority = priority_label_to_key(priority_label)

    with st.spinner("Analisando notebooks..."):
        filtered = df[df["price_brl"] <= budget].copy()
        filtered = filtered[filtered["ram_gb"] >= min_ram]
        filtered = filtered[filtered["storage_gb"] >= min_storage]

        if require_dedicated_gpu:
            filtered = filtered[
                filtered["gpu"].str.lower().str.contains("rtx|gtx|rx ", na=False)
            ]

        if screen_pref == "13–14\"":
            filtered = filtered[(filtered["screen_size"] >= 13) & (filtered["screen_size"] < 15)]
        elif screen_pref == "15–16\"":
            filtered = filtered[(filtered["screen_size"] >= 15) & (filtered["screen_size"] < 17)]
        elif screen_pref == "17\"+":
            filtered = filtered[filtered["screen_size"] >= 17]

        if filtered.empty:
            st.warning("Nenhum notebook encontrado com esses filtros. Tente relaxar os requisitos.")
            return

        filtered["computed_score"] = filtered.apply(
            lambda r: compute_laptop_score(r, use_profile, priority, games), axis=1
        )
        filtered = filtered.sort_values("computed_score", ascending=False).reset_index(drop=True)

        ranked = []
        for _, row in filtered.iterrows():
            ranked.append({
                "name": row["name"],
                "brand": row["brand"],
                "price_brl": float(row["price_brl"]),
                "cpu": row["cpu"],
                "gpu": row["gpu"],
                "ram_gb": float(row["ram_gb"]),
                "storage_gb": float(row["storage_gb"]),
                "screen_size": float(row["screen_size"]),
                "score": float(row["computed_score"]),
                "performance_score": float(row["performance_score"]),
                "store_search_name": str(row.get("store_search_name", row["name"])),
            })

        st.session_state["last_laptop"] = ranked

    _display_laptop_result(ranked, budget)


def _display_laptop_result(ranked: list[dict], budget: float):
    if not ranked:
        st.warning("Nenhum notebook disponível.")
        return

    best = ranked[0]
    st.success(f"Melhor notebook encontrado: **{best['name']}**")

    c1, c2, c3 = st.columns(3)
    c1.metric("Preço", format_brl(best["price_brl"]))
    c2.metric("Score", f"{best['score']:.1f}")
    c3.metric("Tier", get_laptop_tier(best["score"]))

    st.divider()
    st.subheader("🥇 Melhor Escolha")
    with st.container():
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.markdown(f"### {best['name']}")
            st.markdown(f"**CPU:** {best['cpu']}  |  **GPU:** {best['gpu']}")
            st.markdown(f"**RAM:** {best['ram_gb']:.0f}GB  |  **Armazenamento:** {best['storage_gb']:.0f}GB  |  **Tela:** {best['screen_size']}\"")
            links = generate_store_links(best["store_search_name"])
            meta = get_store_metadata()
            link_html = " ".join([
                f'<a href="{url}" target="_blank" class="store-btn" '
                f'style="background:{meta[store]["color"]};color:white;">'
                f'{meta[store]["icon"]} {store}</a>'
                for store, url in links.items()
            ])
            st.markdown(link_html, unsafe_allow_html=True)
        with col_b:
            st.metric("Preço", format_brl(best["price_brl"]))
            st.metric("Score", f"{best['score']:.1f}")

    st.divider()
    st.subheader("🏆 Top 5 Notebooks")
    top5 = ranked[:5]
    for i, nb in enumerate(top5):
        medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
        with st.expander(f"{medal} {nb['name']} — {format_brl(nb['price_brl'])} | Score: {nb['score']:.1f}"):
            st.markdown(f"**CPU:** {nb['cpu']}  |  **GPU:** {nb['gpu']}")
            st.markdown(f"**RAM:** {nb['ram_gb']:.0f}GB | **SSD:** {nb['storage_gb']:.0f}GB | **Tela:** {nb['screen_size']}\"")
            links = generate_store_links(nb["store_search_name"])
            meta = get_store_metadata()
            link_html = " ".join([
                f'<a href="{url}" target="_blank" class="store-btn" '
                f'style="background:{meta[store]["color"]};color:white;">'
                f'{meta[store]["icon"]} {store}</a>'
                for store, url in links.items()
            ])
            st.markdown(link_html, unsafe_allow_html=True)

    st.divider()
    st.plotly_chart(chart_laptop_ranking(top5), use_container_width=True)
    df_display = pd.DataFrame(ranked).rename(columns={
        "name": "Nome", "brand": "Marca", "price_brl": "Preço (R$)",
        "cpu": "CPU", "gpu": "GPU", "ram_gb": "RAM (GB)",
        "storage_gb": "SSD (GB)", "screen_size": "Tela", "score": "Score",
    })
    st.dataframe(
        df_display[["Nome", "Marca", "Preço (R$)", "CPU", "GPU", "RAM (GB)", "SSD (GB)", "Tela", "Score"]],
        use_container_width=True, hide_index=True,
    )


def page_knapsack_iterativo():
    st.title("📐 Knapsack Iterativo (Bottom-Up)")

    with st.expander("📖 Explicação do Algoritmo", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
**Abordagem Bottom-Up (Iterativa)**

O algoritmo constrói a tabela DP de baixo para cima, calculando
todos os subproblemas na ordem crescente de i (itens) e w (capacidade).

**Recorrência:**
```
dp[0][w] = 0  ∀ w
dp[i][w] = dp[i-1][w]             se weight[i] > w
dp[i][w] = max(dp[i-1][w],        caso contrário
               dp[i-1][w-wi] + vi)
```

**Complexidade:**
- Tempo: O(n × W)
- Espaço: O(n × W) — tabela completa armazenada para reconstrução
            """)
        with col2:
            st.markdown("""
**Vantagens:**
- Sem overhead de chamadas recursivas
- Sem risco de stack overflow
- Calcula todos os subproblemas sistematicamente

**Desvantagens:**
- Sempre calcula todos os estados O(n × W)
- Uso de memória proporcional a n × W

**Implementação:**
```python
for i in range(1, n + 1):
    for w in range(W + 1):
        if weights[i-1] > w:
            dp[i][w] = dp[i-1][w]
        else:
            dp[i][w] = max(
                dp[i-1][w],
                dp[i-1][w - weights[i-1]] + values[i-1]
            )
```
            """)

    st.divider()
    st.subheader("▶️ Executar")

    df = get_parts()
    col1, col2, col3 = st.columns(3)
    with col1:
        budget_iter = st.number_input("Orçamento (R$)", 500, 50000, value=st.session_state.get("last_budget", 3000), step=500, key="iter_budget")
    with col2:
        use_label = st.selectbox("Perfil de uso", list(USE_PROFILES.keys()), key="iter_use")
    with col3:
        max_items = st.slider("Máx. itens para tabela", 5, 50, 20, key="iter_max")

    run_iter = st.button("▶️ Executar Knapsack Iterativo", type="primary")

    if run_iter:
        use_profile = profile_label_to_key(use_label)
        df_f = filter_by_budget(df, budget_iter).copy()
        df_f["computed_score"] = df_f.apply(
            lambda r: compute_part_score(r, use_profile, "performance"), axis=1
        )
        df_f = df_f.nlargest(max_items, "computed_score")

        weights, values, names, cats = prepare_knapsack_inputs(df_f, budget_iter, "computed_score")
        scaled_w, scaled_cap, step = apply_budget_step(weights, budget_iter)

        with st.spinner("Executando..."):
            result = knapsack_iterativo(scaled_w, values, scaled_cap)

        st.session_state["last_iter_result"] = result
        st.session_state["last_iter_weights"] = weights
        st.session_state["last_iter_values"] = values
        st.session_state["last_iter_names"] = names
        st.session_state["last_iter_cats"] = cats
        st.session_state["last_budget"] = int(budget_iter)

    result = st.session_state.get("last_iter_result")
    if result is None:
        st.info("Execute o algoritmo para ver os resultados.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Valor Ótimo", f"{result.value:.2f}")
    c2.metric("Itens Selecionados", len(result.selected_indices))
    c3.metric("Estados Calculados", f"{result.states_computed:,}")
    c4.metric("Tempo", f"{result.execution_time_ms:.4f} ms")

    st.divider()
    st.subheader("📋 Itens Selecionados")
    names = st.session_state["last_iter_names"]
    values_list = st.session_state["last_iter_values"]
    weights_list = st.session_state["last_iter_weights"]
    cats = st.session_state["last_iter_cats"]

    selected_data = []
    for idx in result.selected_indices:
        if idx < len(names):
            selected_data.append({
                "Nome": names[idx],
                "Categoria": cats[idx] if idx < len(cats) else "",
                "Preço (R$)": weights_list[idx],
                "Score": f"{values_list[idx]:.2f}",
            })
    if selected_data:
        st.dataframe(pd.DataFrame(selected_data), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🗂️ Tabela DP (amostrada)")
    table_display, truncated = get_dp_table_display(result.dp_table, max_rows=12, max_cols=12)
    if truncated:
        st.info("Tabela muito grande — exibindo amostra representativa.")

    st.plotly_chart(chart_dp_table_heatmap(result.dp_table), use_container_width=True)

    df_table = pd.DataFrame(
        table_display,
        columns=[f"w={c}" for c in range(len(table_display[0]))],
        index=[f"i={r}" for r in range(len(table_display))],
    )
    st.dataframe(df_table.round(2), use_container_width=True)


def page_knapsack_recursivo():
    st.title("🔁 Knapsack Recursivo com Memoization (Top-Down)")

    with st.expander("📖 Explicação do Algoritmo", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
**Abordagem Top-Down (Recursiva com Memoization)**

Parte do problema completo OPT(n, W) e resolve os subproblemas
sob demanda, armazenando os resultados no memo para evitar
recalcular estados já visitados.

**Recorrência:**
```
OPT(0, w) = 0            (caso base: sem itens)
OPT(i, 0) = 0            (caso base: sem capacidade)

OPT(i, w) = OPT(i-1, w)
    se weight[i] > w

OPT(i, w) = max(OPT(i-1, w),
                OPT(i-1, w-wi) + vi)
    caso contrário
```
            """)
        with col2:
            st.markdown("""
**Memoization:**
```python
memo = {}

def OPT(i, w):
    if i == 0 or w == 0:
        return 0
    if (i, w) in memo:
        return memo[(i, w)]  # cache hit!

    if weights[i-1] > w:
        result = OPT(i-1, w)
    else:
        result = max(OPT(i-1, w),
                     OPT(i-1, w-weights[i-1]) + values[i-1])

    memo[(i, w)] = result
    return result
```

**Vantagem:** calcula apenas os estados necessários,
potencialmente muito mais eficiente que o iterativo
quando poucos subproblemas são relevantes.
            """)

    st.divider()
    st.subheader("▶️ Executar")

    df = get_parts()
    col1, col2, col3 = st.columns(3)
    with col1:
        budget_rec = st.number_input("Orçamento (R$)", 500, 20000, value=st.session_state.get("last_budget", 3000), step=500, key="rec_budget")
    with col2:
        use_label = st.selectbox("Perfil de uso", list(USE_PROFILES.keys()), key="rec_use")
    with col3:
        max_items_rec = st.slider("Máx. itens", 5, 30, 15, key="rec_max")

    run_rec = st.button("▶️ Executar Knapsack Recursivo", type="primary")

    if run_rec:
        use_profile = profile_label_to_key(use_label)
        df_f = filter_by_budget(df, budget_rec).copy()
        df_f["computed_score"] = df_f.apply(
            lambda r: compute_part_score(r, use_profile, "performance"), axis=1
        )
        df_f = df_f.nlargest(max_items_rec, "computed_score")

        weights, values, names, cats = prepare_knapsack_inputs(df_f, budget_rec, "computed_score")
        scaled_w, scaled_cap, step = apply_budget_step(weights, budget_rec, max_states=1000)

        with st.spinner("Executando..."):
            result = knapsack_recursivo(scaled_w, values, scaled_cap)

        st.session_state["last_rec_result"] = result
        if st.session_state.get("last_iter_names") != names:
            st.session_state["last_iter_weights"] = weights
            st.session_state["last_iter_values"] = values
            st.session_state["last_iter_names"] = names
            st.session_state["last_iter_cats"] = cats
        st.session_state["last_budget"] = int(budget_rec)

    result = st.session_state.get("last_rec_result")
    if result is None:
        st.info("Execute o algoritmo para ver os resultados.")
        return

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Valor Ótimo", f"{result.value:.2f}")
    c2.metric("Itens Selecionados", len(result.selected_indices))
    c3.metric("Estados Calculados", f"{result.states_computed:,}")
    c4.metric("Cache Hits", f"{result.cache_hits:,}")
    c5.metric("Tempo", f"{result.execution_time_ms:.4f} ms")

    st.divider()
    st.subheader("📦 Sumário do Memo (cache)")
    memo_summary = get_memo_summary(result.memo_table)
    st.json(memo_summary)

    st.subheader("📋 Itens Selecionados")
    names = st.session_state["last_iter_names"]
    values_list = st.session_state["last_iter_values"]
    weights_list = st.session_state["last_iter_weights"]
    cats = st.session_state["last_iter_cats"]

    selected_data = []
    for idx in result.selected_indices:
        if idx < len(names):
            selected_data.append({
                "Nome": names[idx],
                "Categoria": cats[idx] if idx < len(cats) else "",
                "Preço (R$)": weights_list[idx],
                "Score": f"{values_list[idx]:.2f}",
            })
    if selected_data:
        st.dataframe(pd.DataFrame(selected_data), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("💾 Entradas do Memo (amostra)")
    memo_items = list(result.memo_table.items())[:50]
    df_memo = pd.DataFrame(
        [{"(i, w)": str(k), "OPT(i,w)": f"{v:.2f}"} for k, v in memo_items]
    )
    st.dataframe(df_memo, use_container_width=True, hide_index=True)


def page_comparacao():
    st.title("⚖️ Comparação: Iterativo vs Recursivo")

    iter_result = st.session_state.get("last_iter_result")
    rec_result = st.session_state.get("last_rec_result")

    if iter_result is None or rec_result is None:
        st.warning("Execute ambos os algoritmos (Knapsack Iterativo e Recursivo) para ver a comparação.")
        col1, col2 = st.columns(2)
        with col1:
            st.info("Vá para a aba **Knapsack Iterativo** e execute o algoritmo.")
        with col2:
            st.info("Vá para a aba **Knapsack Recursivo** e execute o algoritmo.")
        return

    weights = st.session_state.get("last_iter_weights", [])
    n_items = len(weights)
    capacity = st.session_state.get("last_budget", 3000)

    iter_m, rec_m = compare_algorithms(iter_result, rec_result, n_items, capacity)

    st.subheader("📊 Métricas Comparativas")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔷 Knapsack Iterativo")
        for k, v in format_metrics_table(iter_m).items():
            st.markdown(f"- **{k}:** {v}")
    with col2:
        st.markdown("#### 🔶 Knapsack Recursivo (Memoization)")
        for k, v in format_metrics_table(rec_m).items():
            st.markdown(f"- **{k}:** {v}")

    st.divider()
    ratios = efficiency_ratio(iter_m, rec_m)
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Razão de Tempo (iter/rec)", f"{ratios['time_ratio_iter_over_rec']:.3f}×")
    col_r2.metric("Razão de Estados (iter/rec)", f"{ratios['states_ratio_iter_over_rec']:.3f}×")
    col_r3.metric(
        "Mesmo Valor Ótimo",
        "✅ Sim" if ratios["same_optimal"] else "⚠️ Diferem",
    )

    st.divider()
    st.plotly_chart(
        chart_algorithm_comparison(
            iter_m.execution_time_ms,
            rec_m.execution_time_ms,
            iter_m.states_computed,
            rec_m.states_computed,
            iter_m.optimal_value,
            rec_m.optimal_value,
        ),
        use_container_width=True,
    )

    st.divider()
    st.subheader("📝 Análise")
    st.markdown(f"""
| Critério | Iterativo | Recursivo (Memo) | Vencedor |
|----------|-----------|-------------------|----------|
| Tempo de execução | {iter_m.execution_time_ms:.4f} ms | {rec_m.execution_time_ms:.4f} ms | {'Recursivo' if rec_m.execution_time_ms < iter_m.execution_time_ms else 'Iterativo'} |
| Estados calculados | {iter_m.states_computed:,} | {rec_m.states_computed:,} | {'Recursivo' if rec_m.states_computed < iter_m.states_computed else 'Iterativo'} |
| Memória estimada | {iter_m.memory_estimate_kb:.1f} KB | {rec_m.memory_estimate_kb:.1f} KB | {'Recursivo' if rec_m.memory_estimate_kb < iter_m.memory_estimate_kb else 'Iterativo'} |
| Valor ótimo | {iter_m.optimal_value:.2f} | {rec_m.optimal_value:.2f} | Empate |
| Cache hits (recursivo) | — | {rec_m.cache_hits:,} | — |

**Conclusão:** Ambos encontram o mesmo valor ótimo. O iterativo é mais previsível e elimina o risco de
stack overflow. O recursivo com memoization pode ser mais eficiente quando poucos subproblemas
são relevantes (esparso), aproveitando os cache hits.
    """)


def page_find_solution():
    st.title("🔍 Find Solution — Reconstrução da Solução")

    with st.expander("📖 Como funciona a reconstrução?", expanded=False):
        st.markdown("""
A **reconstrução da solução** percorre a tabela DP de trás para frente.

Para cada item `i` (do último ao primeiro):
- Verifica se `dp[i][w] ≠ dp[i-1][w]`
- Se diferente, o item `i` foi incluído na solução ótima
- Subtrai o peso do item da capacidade restante `w`
- Avança para o item anterior

O resultado é a lista de itens que compõem a solução ótima
para a capacidade especificada (ou o orçamento total).
        """)

    st.divider()
    iter_result = st.session_state.get("last_iter_result")
    rec_result = st.session_state.get("last_rec_result")
    names = st.session_state.get("last_iter_names", [])
    weights = st.session_state.get("last_iter_weights", [])
    values_list = st.session_state.get("last_iter_values", [])
    cats = st.session_state.get("last_iter_cats", [])
    last_budget = st.session_state.get("last_budget", 3000)

    if iter_result is None and rec_result is None:
        st.warning("Execute ao menos um dos algoritmos Knapsack antes de usar esta página.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        use_custom = st.checkbox("Usar orçamento personalizado")
        if use_custom:
            custom_cap = st.number_input("Capacidade (R$)", 100, last_budget, last_budget // 2, step=100)
        else:
            custom_cap = None
    with col2:
        source = st.radio("Fonte da tabela", ["Iterativo", "Recursivo (Memo)"])
    with col3:
        run_find = st.button("🔍 Reconstruir Solução", type="primary")

    if run_find:
        cap = custom_cap if use_custom and custom_cap else None

        if source == "Iterativo" and iter_result:
            fs_result = find_solution_from_dp(
                iter_result.dp_table,
                weights, values_list, names, cats,
                capacity=cap,
            )
        elif rec_result:
            fs_result = find_solution_from_memo(
                rec_result.memo_table,
                weights, values_list, names, cats,
                capacity=cap,
            )
        else:
            st.error("Resultado não disponível. Execute o algoritmo selecionado primeiro.")
            return

        st.divider()
        st.subheader("📋 Passo a Passo da Reconstrução")
        actual_cap = cap if cap else last_budget
        st.markdown(f"**Orçamento inicial: {format_brl(actual_cap)}**")

        for step in fs_result.steps:
            icon = CATEGORY_ICONS.get(step.category, "🔧")
            st.markdown(
                f'<div class="step-box">'
                f'<b>Passo {step.step}:</b> {icon} escolheu <b>{step.item_name}</b> ({step.category}) — {format_brl(step.item_price)}<br>'
                f'&nbsp;&nbsp;&nbsp;&nbsp;{format_brl(step.budget_before)} − {format_brl(step.item_price)} = <b>{format_brl(step.budget_after)}</b>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Preço Total", format_brl(fs_result.total_price))
        c2.metric("Score Total", f"{fs_result.total_score:.2f}")
        c3.metric("Orçamento Restante", format_brl(fs_result.budget_remaining))

        st.subheader("📦 Itens Escolhidos")
        if fs_result.selected_items:
            df_sel = pd.DataFrame(fs_result.selected_items)
            df_sel["price_int"] = df_sel["price_int"].apply(format_brl)
            df_sel = df_sel.rename(columns={"name": "Nome", "category": "Categoria",
                                            "price_int": "Preço", "score": "Score"})
            st.dataframe(df_sel, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum item selecionado para esta capacidade.")
    else:
        st.info("Clique em **Reconstruir Solução** para ver o passo a passo.")


def page_links_compra():
    st.title("🛒 Links de Compra")
    st.markdown("Encontre onde comprar as peças escolhidas nas principais lojas brasileiras.")

    build = st.session_state.get("last_build")
    laptop_list = st.session_state.get("last_laptop")

    tab1, tab2, tab3 = st.tabs(["🖥️ PC Montado", "💻 Notebooks", "🔍 Busca Manual"])

    with tab1:
        if not build or not build.get("items"):
            st.info("Monte um PC na aba **Montar PC** para ver os links das peças.")
        else:
            items = sort_items_by_category(build["items"])
            st.markdown(f"**{len(items)} peças — Total: {format_brl(build['total_price'])}**")
            _render_store_links_table(items)

    with tab2:
        if not laptop_list:
            st.info("Recomende notebooks na aba **Escolher Notebook** para ver os links.")
        else:
            top5 = laptop_list[:5]
            st.markdown(f"**Top {len(top5)} notebooks recomendados**")
            _render_store_links_table(top5)

    with tab3:
        st.subheader("Busca manual de qualquer produto")
        search_term = st.text_input("Nome do produto", placeholder="Ex: RTX 4070 12GB")
        if search_term:
            links = generate_store_links(search_term)
            meta = get_store_metadata()
            _render_links_buttons(search_term, links, meta)


def _render_store_links_table(items: list[dict]):
    meta = get_store_metadata()
    for item in items:
        name = item.get("name", "")
        cat = item.get("category", "")
        price = float(item.get("price_brl", item.get("price_int", 0)))
        search = item.get("store_search_name", name)
        icon = CATEGORY_ICONS.get(cat, "🔧")

        links = generate_store_links(search)
        with st.expander(f"{icon} {truncate_name(name, 50)} — {format_brl(price)}"):
            _render_links_buttons(search, links, meta)


def _render_links_buttons(search: str, links: dict, meta: dict):
    cols = st.columns(len(links))
    for col, (store, url) in zip(cols, links.items()):
        with col:
            st.markdown(
                f'<a href="{url}" target="_blank" class="store-btn" '
                f'style="background:{meta[store]["color"]};color:white;display:block;text-align:center;padding:0.5rem;">'
                f'{meta[store]["icon"]}<br>{store}</a>',
                unsafe_allow_html=True,
            )


# ════════════════════════════════════════════════════════════════════════════
# NAVEGAÇÃO PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════

PAGES = {
    "🏠 Home": page_home,
    "📊 Dataset": page_dataset,
    "🔧 Montar PC": page_montar_pc,
    "💻 Escolher Notebook": page_notebook,
    "📐 Knapsack Iterativo": page_knapsack_iterativo,
    "🔁 Knapsack Recursivo": page_knapsack_recursivo,
    "⚖️ Comparação": page_comparacao,
    "🔍 Find Solution": page_find_solution,
    "🛒 Links de Compra": page_links_compra,
}


def main():
    with st.sidebar:
        st.markdown("## 🖥️ PC Build Optimizer")
        st.divider()
        page_name = st.radio(
            "Navegação",
            list(PAGES.keys()),
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown("**Estado atual:**")
        st.markdown(f"{'✅' if st.session_state['last_build'] else '⬜'} PC Montado")
        st.markdown(f"{'✅' if st.session_state['last_laptop'] else '⬜'} Notebook Escolhido")
        st.markdown(f"{'✅' if st.session_state['last_iter_result'] else '⬜'} Knapsack Iterativo")
        st.markdown(f"{'✅' if st.session_state['last_rec_result'] else '⬜'} Knapsack Recursivo")
        st.divider()
        if st.button("🗑️ Limpar sessão"):
            for key in ["last_build", "last_laptop", "last_iter_result",
                        "last_rec_result", "last_iter_weights", "last_iter_values",
                        "last_iter_names", "last_iter_cats"]:
                st.session_state[key] = None if key not in ["last_iter_weights",
                                                             "last_iter_values",
                                                             "last_iter_names",
                                                             "last_iter_cats"] else []
            st.rerun()

    PAGES[page_name]()


if __name__ == "__main__":
    main()
