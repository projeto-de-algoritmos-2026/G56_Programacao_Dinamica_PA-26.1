"""PC Build Optimizer — interface Streamlit redesenhada."""

import sys
import os
import uuid
import time as _time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd

from data_loader import load_pc_parts, load_laptops, load_from_upload, get_dataset_stats
from preprocessing import prepare_knapsack_inputs, apply_budget_step, filter_by_budget
from scoring import compute_part_score, compute_laptop_score
from compatibility import check_compatibility, get_compatibility_emoji
from knapsack_iterativo import knapsack_iterativo, get_dp_table_display
from knapsack_recursivo import knapsack_recursivo, get_memo_summary
from grouped_knapsack import grouped_knapsack, prepare_groups
from find_solution import find_solution_from_dp, find_solution_from_memo, format_reconstruction_text
from store_links import generate_store_links, get_store_metadata
from charts import (
    chart_price_distribution, chart_score_by_category, chart_selected_parts,
    chart_budget_usage, chart_algorithm_comparison, chart_dp_table_heatmap,
    chart_laptop_ranking, chart_price_vs_score, chart_category_breakdown,
)
from metrics import compare_algorithms, format_metrics_table, efficiency_ratio
from utils import (
    USE_PROFILES, PRIORITIES, GAMES, CATEGORY_ICONS,
    format_brl, profile_label_to_key, priority_label_to_key,
    get_performance_tier, get_laptop_tier, sort_items_by_category, truncate_name,
)

# ─── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="PC Build Optimizer",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS Global ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero-banner {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 20px;
    padding: 3rem 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    border: 1px solid rgba(123,104,238,0.3);
    box-shadow: 0 8px 32px rgba(123,104,238,0.2);
}
.hero-title {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #7B68EE, #20B2AA, #7B68EE);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.hero-sub {
    color: #a0aec0;
    font-size: 1.15rem;
    margin-top: 0.5rem;
}
.feature-card {
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 1rem;
    transition: transform 0.2s;
}
.feature-card:hover { transform: translateY(-4px); }
.part-card {
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    border: 1px solid rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    gap: 1rem;
}
.part-icon {
    font-size: 2.5rem;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    flex-shrink: 0;
}
.store-link-btn {
    display: inline-block;
    padding: 0.35rem 0.75rem;
    border-radius: 8px;
    margin: 0.15rem;
    font-weight: 600;
    text-decoration: none !important;
    font-size: 0.82rem;
    color: white !important;
    transition: opacity 0.2s;
}
.store-link-btn:hover { opacity: 0.85; }
.cart-item {
    background: #1a1f2e;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    border: 1px solid rgba(123,104,238,0.25);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    background: rgba(123,104,238,0.25);
    color: #9b8eff;
}
.step-card {
    background: #1e2535;
    border-left: 4px solid #7B68EE;
    padding: 0.8rem 1.2rem;
    margin: 0.4rem 0;
    border-radius: 0 10px 10px 0;
}
.algo-box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1.2rem;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    color: #e6edf3;
    white-space: pre;
    overflow-x: auto;
}
.compat-ok { color: #4CAF50; font-weight: 700; }
.compat-warn { color: #FFC107; font-weight: 700; }
.compat-err { color: #F44336; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ─── Paleta de gradientes por categoria ─────────────────────────────────────
CATEGORY_GRADIENT = {
    "CPU":         ("linear-gradient(135deg,#667eea,#764ba2)", "#667eea"),
    "GPU":         ("linear-gradient(135deg,#11998e,#38ef7d)", "#11998e"),
    "Motherboard": ("linear-gradient(135deg,#f46b45,#eea849)", "#f46b45"),
    "RAM":         ("linear-gradient(135deg,#4facfe,#00f2fe)", "#4facfe"),
    "Storage":     ("linear-gradient(135deg,#fa709a,#fee140)", "#fa709a"),
    "PSU":         ("linear-gradient(135deg,#30cfd0,#330867)", "#30cfd0"),
    "Case":        ("linear-gradient(135deg,#a18cd1,#fbc2eb)", "#a18cd1"),
    "Cooler":      ("linear-gradient(135deg,#89f7fe,#66a6ff)", "#89f7fe"),
}
STORE_COLORS = {
    "KaBuM!":       "#FF6B00",
    "TerabyteShop": "#0056b3",
    "Pichau":       "#6c3fff",
    "Amazon Brasil":"#FF9900",
    "Mercado Livre":"#e6a817",
}

# ─── Estado global ───────────────────────────────────────────────────────────
def _init_state():
    defaults: dict = {
        "df_parts": None,
        "df_laptops": None,
        "last_build": None,
        "last_laptop": None,
        "last_iter_result": None,
        "last_rec_result": None,
        "last_iter_weights": [],
        "last_iter_values": [],
        "last_iter_names": [],
        "last_iter_cats": [],
        "last_budget": 5000,
        "budget_pc": 5000,
        "budget_nb": 6000,
        "cart": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ─── Dados ───────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _load_parts():  return load_pc_parts()
@st.cache_data(show_spinner=False)
def _load_laptops(): return load_laptops()

def get_parts() -> pd.DataFrame:
    if st.session_state["df_parts"] is None:
        st.session_state["df_parts"] = _load_parts()
    return st.session_state["df_parts"]

def get_laptops() -> pd.DataFrame:
    if st.session_state["df_laptops"] is None:
        st.session_state["df_laptops"] = _load_laptops()
    return st.session_state["df_laptops"]

# ─── Carrinho ────────────────────────────────────────────────────────────────
def add_to_cart(item: dict, item_type: str = "pc_part"):
    cart: list = st.session_state["cart"]
    if any(c["name"] == item["name"] for c in cart):
        return False  # já está no carrinho
    cart.append({
        "id": str(uuid.uuid4()),
        "name": item.get("name", ""),
        "category": item.get("category", ""),
        "price": float(item.get("price_brl", item.get("price_int", 0))),
        "store_search_name": item.get("store_search_name", item.get("name", "")),
        "type": item_type,
    })
    return True

def remove_from_cart(item_id: str):
    st.session_state["cart"] = [c for c in st.session_state["cart"] if c["id"] != item_id]

def add_build_to_cart(items: list[dict]):
    added = 0
    for item in items:
        if add_to_cart(item, "pc_part"):
            added += 1
    return added

# ─── Helpers de UI ───────────────────────────────────────────────────────────
def _store_links_html(search_name: str) -> str:
    links = generate_store_links(search_name)
    parts = []
    for store, url in links.items():
        color = STORE_COLORS.get(store, "#555")
        parts.append(
            f'<a href="{url}" target="_blank" class="store-link-btn" '
            f'style="background:{color};">{store}</a>'
        )
    return " ".join(parts)

def _part_card_html(item: dict) -> str:
    cat = item.get("category", "")
    gradient, accent = CATEGORY_GRADIENT.get(cat, ("linear-gradient(135deg,#444,#666)", "#888"))
    icon = CATEGORY_ICONS.get(cat, "🔧")
    name = item.get("name", "")
    price = float(item.get("price_brl", item.get("price_int", 0)))
    score = item.get("score", 0)
    return (
        f'<div class="part-card" style="background:rgba(255,255,255,0.03);">'
        f'  <div class="part-icon" style="background:{gradient};">{icon}</div>'
        f'  <div style="flex:1;">'
        f'    <div style="font-weight:700;font-size:0.95rem;">{name}</div>'
        f'    <div style="display:flex;gap:1rem;margin-top:0.3rem;">'
        f'      <span class="badge" style="background:rgba(255,255,255,0.08);color:#aaa;">{cat}</span>'
        f'      <span style="color:#4CAF50;font-weight:700;">{format_brl(price)}</span>'
        f'      <span style="color:#7B68EE;">Score {score:.1f}</span>'
        f'    </div>'
        f'  </div>'
        f'</div>'
    )

def _budget_selector(key: str, default: int = 5000) -> int:
    """Seletor de orçamento com presets + input numérico."""
    presets = [2000, 3000, 5000, 8000, 12000]
    cols = st.columns(len(presets))
    for col, val in zip(cols, presets):
        with col:
            if st.button(f"R$ {val//1000}k", key=f"preset_{key}_{val}", use_container_width=True):
                st.session_state[key] = val
                st.rerun()
    budget = st.number_input(
        "Orçamento personalizado (R$)",
        min_value=500, max_value=100000,
        value=st.session_state[key],
        step=500,
        key=f"ni_{key}",
    )
    st.session_state[key] = int(budget)
    return int(budget)

# ════════════════════════════════════════════════════════════════════════════
# PÁGINA: HOME
# ════════════════════════════════════════════════════════════════════════════
def page_home():
    # Banner principal
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🖥️ PC Build Optimizer</div>
        <div class="hero-sub">
            Monte o PC Gamer perfeito ou escolha o notebook ideal dentro do seu orçamento.<br>
            Algoritmos de Programação Dinâmica encontram a combinação ótima de peças.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Cards de funcionalidades
    c1, c2, c3, c4 = st.columns(4)
    features = [
        ("🎯", "linear-gradient(135deg,#667eea,#764ba2)",
         "Orçamento inteligente", "Informe quanto quer gastar e o sistema distribui entre as melhores peças."),
        ("🎮", "linear-gradient(135deg,#11998e,#38ef7d)",
         "Otimizado para jogos", "Score ajustado pelos jogos que você quer rodar — GPU certa para cada título."),
        ("🛒", "linear-gradient(135deg,#fa709a,#fee140)",
         "Carrinho de compras", "Salve as peças e acesse links de busca nas lojas com um clique."),
        ("🧮", "linear-gradient(135deg,#30cfd0,#330867)",
         "Algoritmo Knapsack", "Solução exata por Programação Dinâmica — não é sugestão, é o ótimo."),
    ]
    for col, (icon, grad, title, desc) in zip([c1, c2, c3, c4], features):
        with col:
            st.markdown(f"""
            <div class="feature-card" style="background:{grad};color:white;">
                <div style="font-size:2.5rem;margin-bottom:0.5rem;">{icon}</div>
                <div style="font-weight:800;font-size:1rem;margin-bottom:0.4rem;">{title}</div>
                <div style="font-size:0.85rem;opacity:0.9;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # Como funciona — visual
    st.subheader("🗺️ Como funciona")
    s1, s2, s3, s4, s5 = st.columns(5)
    steps_info = [
        ("1️⃣", "#7B68EE", "Defina o orçamento"),
        ("2️⃣", "#11998e", "Escolha jogos e uso"),
        ("3️⃣", "#f46b45", "O algoritmo otimiza"),
        ("4️⃣", "#fa709a", "Veja as peças escolhidas"),
        ("5️⃣", "#4facfe", "Compre nas lojas"),
    ]
    for col, (num, color, label) in zip([s1, s2, s3, s4, s5], steps_info):
        with col:
            st.markdown(f"""
            <div style="text-align:center;padding:1rem;background:#1a1f2e;border-radius:12px;
                        border-top:4px solid {color};">
                <div style="font-size:1.8rem;">{num}</div>
                <div style="font-size:0.85rem;margin-top:0.3rem;color:#a0aec0;">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # Algoritmos — seção educacional com tabs
    st.subheader("🧮 Algoritmos de Programação Dinâmica")
    st.markdown("Toda a lógica de seleção de peças é baseada em **Programação Dinâmica**. Explore cada algoritmo abaixo:")

    algo_tab, iter_tab, rec_tab, comp_tab, fs_tab = st.tabs([
        "📖 Visão Geral",
        "📐 Knapsack Iterativo",
        "🔁 Knapsack Recursivo",
        "⚖️ Comparação",
        "🔍 Find Solution",
    ])

    with algo_tab:
        _home_overview()
    with iter_tab:
        _home_knapsack_iterativo()
    with rec_tab:
        _home_knapsack_recursivo()
    with comp_tab:
        _home_comparacao()
    with fs_tab:
        _home_find_solution()


def _home_overview():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
**O Problema da Mochila (Knapsack 0/1)**

Dado um conjunto de itens com **pesos** e **valores**, e uma mochila
com **capacidade W**, escolha os itens que maximizem o valor total
sem exceder a capacidade.

**No PC Build Optimizer:**

| Conceito | Equivalente |
|----------|-------------|
| Capacidade W | Orçamento (R$) |
| Peso do item | Preço da peça |
| Valor do item | Score de desempenho |
| Grupo | Categoria (CPU, GPU, ...) |

**Recorrência:**
        """)
        st.code("""
OPT(0, w)  = 0
OPT(i, w)  = OPT(i-1, w)          se weight[i] > w
OPT(i, w)  = max( OPT(i-1, w),
                  OPT(i-1, w-wi) + vi )
        """, language="text")
    with col2:
        st.markdown("""
**Grouped Knapsack (para montagem de PC)**

Para garantir exatamente **uma peça por categoria**, usamos o
Multiple Choice Knapsack:

```
dp[g][w] = max(
    dp[g-1][w],                         # pula o grupo
    max{ dp[g-1][w-wi]+vi : i ∈ grupo g } # escolhe uma peça
)
```

**Score de cada peça:**
```
score = desempenho_base × peso_categoria
      + bônus_jogos
      + bônus_custo_benefício
```

**Complexidade:**
- Iterativo: O(n × W) tempo e espaço
- Recursivo Memo: O(n × W) pior caso, frequentemente melhor
        """)


def _home_knapsack_iterativo():
    st.markdown("### Knapsack Iterativo (Bottom-Up)")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
Preenche a tabela DP de baixo para cima, calculando todos os subproblemas
na ordem crescente de `i` (itens) e `w` (capacidade).

**Vantagens:** sem overhead recursivo, sem risco de stack overflow.

**Desvantagem:** sempre calcula todos os O(n × W) estados.
        """)
        st.code("""
for i in range(1, n+1):
    for w in range(W+1):
        if weights[i-1] > w:
            dp[i][w] = dp[i-1][w]
        else:
            dp[i][w] = max(
                dp[i-1][w],
                dp[i-1][w - weights[i-1]] + values[i-1]
            )
        """, language="python")
    with col2:
        st.markdown("**Executar com dados do dataset:**")
        df = get_parts()
        budget_i = st.number_input("Orçamento (R$)", 500, 10000, 3000, 500, key="home_iter_b")
        max_i = st.slider("Máx. itens", 5, 30, 15, key="home_iter_max")
        if st.button("▶️ Executar Iterativo", key="home_iter_run"):
            df_f = filter_by_budget(df, budget_i).copy()
            df_f["computed_score"] = df_f.apply(
                lambda r: compute_part_score(r, "gaming_aaa", "performance"), axis=1
            )
            df_f = df_f.nlargest(max_i, "computed_score")
            weights, values, names, cats = prepare_knapsack_inputs(df_f, budget_i, "computed_score")
            sw, sc, step = apply_budget_step(weights, budget_i)
            with st.spinner("Calculando..."):
                res = knapsack_iterativo(sw, values, sc)
            st.session_state["last_iter_result"] = res
            st.session_state["last_iter_weights"] = weights
            st.session_state["last_iter_values"] = values
            st.session_state["last_iter_names"] = names
            st.session_state["last_iter_cats"] = cats
            st.session_state["last_budget"] = int(budget_i)
            st.success(f"Valor ótimo: {res.value:.2f} | Tempo: {res.execution_time_ms:.3f}ms | Estados: {res.states_computed:,}")
        res = st.session_state.get("last_iter_result")
        if res:
            c1, c2, c3 = st.columns(3)
            c1.metric("Valor Ótimo", f"{res.value:.2f}")
            c2.metric("Estados", f"{res.states_computed:,}")
            c3.metric("Tempo", f"{res.execution_time_ms:.3f}ms")
            st.plotly_chart(chart_dp_table_heatmap(res.dp_table), use_container_width=True)


def _home_knapsack_recursivo():
    st.markdown("### Knapsack Recursivo com Memoization (Top-Down)")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("""
Resolve subproblemas **sob demanda** — só calcula o que é necessário.
Resultados já calculados ficam no `memo` (cache), eliminando recálculos.

**Vantagem:** pode calcular bem menos que O(n × W) quando o espaço é esparso.
        """)
        st.code("""
memo = {}
def OPT(i, w):
    if i == 0 or w == 0: return 0
    if (i, w) in memo:
        return memo[(i, w)]   # cache hit!

    if weights[i-1] > w:
        res = OPT(i-1, w)
    else:
        res = max(OPT(i-1, w),
                  OPT(i-1, w-weights[i-1]) + values[i-1])

    memo[(i, w)] = res
    return res
        """, language="python")
    with col2:
        st.markdown("**Executar com dados do dataset:**")
        df = get_parts()
        budget_r = st.number_input("Orçamento (R$)", 500, 10000, 3000, 500, key="home_rec_b")
        max_r = st.slider("Máx. itens", 5, 20, 12, key="home_rec_max")
        if st.button("▶️ Executar Recursivo", key="home_rec_run"):
            df_f = filter_by_budget(df, budget_r).copy()
            df_f["computed_score"] = df_f.apply(
                lambda r: compute_part_score(r, "gaming_aaa", "performance"), axis=1
            )
            df_f = df_f.nlargest(max_r, "computed_score")
            weights, values, names, cats = prepare_knapsack_inputs(df_f, budget_r, "computed_score")
            sw, sc, step = apply_budget_step(weights, budget_r, max_states=1000)
            with st.spinner("Calculando..."):
                res = knapsack_recursivo(sw, values, sc)
            st.session_state["last_rec_result"] = res
            st.session_state["last_iter_weights"] = weights
            st.session_state["last_iter_values"] = values
            st.session_state["last_iter_names"] = names
            st.session_state["last_iter_cats"] = cats
            st.session_state["last_budget"] = int(budget_r)
            st.success(f"Valor ótimo: {res.value:.2f} | Cache hits: {res.cache_hits:,} | Tempo: {res.execution_time_ms:.3f}ms")
        res = st.session_state.get("last_rec_result")
        if res:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Valor Ótimo", f"{res.value:.2f}")
            c2.metric("Estados", f"{res.states_computed:,}")
            c3.metric("Cache Hits", f"{res.cache_hits:,}")
            c4.metric("Tempo", f"{res.execution_time_ms:.3f}ms")
            memo_s = get_memo_summary(res.memo_table)
            st.json(memo_s)


def _home_comparacao():
    st.markdown("### Comparação: Iterativo × Recursivo")
    iter_r = st.session_state.get("last_iter_result")
    rec_r = st.session_state.get("last_rec_result")
    if iter_r is None or rec_r is None:
        st.info("Execute ambos os algoritmos nas abas **Knapsack Iterativo** e **Knapsack Recursivo** para comparar.")
        return
    weights = st.session_state.get("last_iter_weights", [])
    capacity = st.session_state.get("last_budget", 3000)
    iter_m, rec_m = compare_algorithms(iter_r, rec_r, len(weights), capacity)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔷 Iterativo")
        for k, v in format_metrics_table(iter_m).items():
            st.markdown(f"- **{k}:** {v}")
    with col2:
        st.markdown("#### 🔶 Recursivo (Memoization)")
        for k, v in format_metrics_table(rec_m).items():
            st.markdown(f"- **{k}:** {v}")

    ratios = efficiency_ratio(iter_m, rec_m)
    st.plotly_chart(
        chart_algorithm_comparison(
            iter_m.execution_time_ms, rec_m.execution_time_ms,
            iter_m.states_computed, rec_m.states_computed,
            iter_m.optimal_value, rec_m.optimal_value,
        ),
        use_container_width=True,
    )
    st.markdown(f"""
| Critério | Iterativo | Recursivo | Vencedor |
|----------|-----------|-----------|----------|
| Tempo | {iter_m.execution_time_ms:.4f}ms | {rec_m.execution_time_ms:.4f}ms | {'Recursivo' if rec_m.execution_time_ms < iter_m.execution_time_ms else 'Iterativo'} |
| Estados | {iter_m.states_computed:,} | {rec_m.states_computed:,} | {'Recursivo' if rec_m.states_computed < iter_m.states_computed else 'Iterativo'} |
| Memória | {iter_m.memory_estimate_kb:.1f}KB | {rec_m.memory_estimate_kb:.1f}KB | {'Recursivo' if rec_m.memory_estimate_kb < iter_m.memory_estimate_kb else 'Iterativo'} |
| Resultado | {iter_m.optimal_value:.2f} | {rec_m.optimal_value:.2f} | {'✅ Iguais' if ratios['same_optimal'] else '⚠️ Diferem'} |
    """)


def _home_find_solution():
    st.markdown("### Find Solution — Reconstrução Passo a Passo")
    st.markdown("""
A reconstrução percorre a tabela DP de **trás para frente**:

```
w = W
para i de n até 1:
    se dp[i][w] ≠ dp[i-1][w]:
        incluir item i
        w = w − weight[i]
```

Se o usuário informar uma capacidade personalizada (ex: R$3.000 dentro de um orçamento de R$5.000),
a reconstrução usa essa capacidade menor.
    """)
    iter_r = st.session_state.get("last_iter_result")
    rec_r = st.session_state.get("last_rec_result")
    names = st.session_state.get("last_iter_names", [])
    weights = st.session_state.get("last_iter_weights", [])
    values_l = st.session_state.get("last_iter_values", [])
    cats = st.session_state.get("last_iter_cats", [])
    last_budget = st.session_state.get("last_budget", 3000)

    if iter_r is None and rec_r is None:
        st.info("Execute um dos algoritmos para usar Find Solution.")
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        use_custom = st.checkbox("Capacidade personalizada", key="fs_custom")
        cap = None
        if use_custom:
            cap = st.number_input("Capacidade (R$)", 100, last_budget, last_budget // 2, 100, key="fs_cap")
        source = st.radio("Fonte", ["Iterativo", "Recursivo (Memo)"], key="fs_src")
        run_fs = st.button("🔍 Reconstruir", type="primary", key="fs_run")

    with col2:
        if run_fs:
            if source == "Iterativo" and iter_r:
                fs = find_solution_from_dp(iter_r.dp_table, weights, values_l, names, cats, capacity=cap)
            elif rec_r:
                fs = find_solution_from_memo(rec_r.memo_table, weights, values_l, names, cats, capacity=cap)
            else:
                st.error("Execute o algoritmo selecionado primeiro."); return

            initial = cap if cap else last_budget
            st.markdown(f"**Orçamento inicial: {format_brl(initial)}**")
            for step in fs.steps:
                icon = CATEGORY_ICONS.get(step.category, "🔧")
                st.markdown(
                    f'<div class="step-card">'
                    f'<b>Passo {step.step}:</b> {icon} <b>{step.item_name}</b> — {format_brl(step.item_price)}<br>'
                    f'&nbsp;&nbsp;{format_brl(step.budget_before)} − {format_brl(step.item_price)} = '
                    f'<b>{format_brl(step.budget_after)}</b></div>',
                    unsafe_allow_html=True,
                )
            st.divider()
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Preço Total", format_brl(fs.total_price))
            mc2.metric("Score Total", f"{fs.total_score:.2f}")
            mc3.metric("Orçamento Restante", format_brl(fs.budget_remaining))


# ════════════════════════════════════════════════════════════════════════════
# PÁGINA: MONTAR PC
# ════════════════════════════════════════════════════════════════════════════
def page_montar_pc():
    st.markdown('<div style="font-size:2rem;font-weight:900;">🔧 Montar PC Gamer</div>', unsafe_allow_html=True)
    st.markdown("Configure as preferências — o algoritmo escolhe a **melhor peça de cada categoria**.")
    st.divider()

    df = get_parts()
    col_param, col_result = st.columns([1, 2])

    with col_param:
        st.markdown("### ⚙️ Parâmetros")
        budget = _budget_selector("budget_pc", 5000)

        st.markdown("---")
        use_label = st.selectbox("Uso Principal", list(USE_PROFILES.keys()), key="pc_use")
        priority_label = st.selectbox("Prioridade", list(PRIORITIES.keys()), key="pc_prio")

        st.markdown("---")
        games = st.multiselect(
            "🎮 Jogos Desejados",
            GAMES,
            default=["CS2", "Valorant"],
            key="pc_games",
        )

        st.markdown("---")
        run_btn = st.button("🚀 Otimizar Configuração", type="primary", use_container_width=True)

    with col_result:
        if run_btn:
            _run_pc_optimization(df, budget, use_label, priority_label, games)
        elif st.session_state["last_build"] is not None:
            _display_build_result(st.session_state["last_build"])
        else:
            st.markdown("""
            <div style="background:#1a1f2e;border-radius:16px;padding:2.5rem;text-align:center;
                        border:2px dashed rgba(123,104,238,0.3);">
                <div style="font-size:3rem;">🖥️</div>
                <h3 style="color:#a0aec0;">Configure e clique em Otimizar</h3>
                <p style="color:#718096;">O sistema usa <b>Grouped Knapsack</b> para selecionar<br>
                exatamente uma peça ótima de cada categoria.</p>
            </div>
            """, unsafe_allow_html=True)


def _run_pc_optimization(df, budget, use_label, priority_label, games):
    use_profile = profile_label_to_key(use_label)
    priority = priority_label_to_key(priority_label)

    try:
        with st.spinner("Calculando configuração ideal com Grouped Knapsack..."):
            df_f = filter_by_budget(df, budget).copy()
            df_f["computed_score"] = df_f.apply(
                lambda r: compute_part_score(r, use_profile, priority, games), axis=1
            )
            groups = prepare_groups(df_f, use_profile, priority)
            result = grouped_knapsack(groups, int(budget))

        st.session_state["last_build"] = {
            "items": result.selected_items,
            "total_price": result.total_price,
            "total_score": result.total_value,
            "budget": budget,
            "exec_time": result.execution_time_ms,
            "use_label": use_label,
            "priority_label": priority_label,
            "games": games,
        }
        st.session_state["last_budget"] = int(budget)
        _display_build_result(st.session_state["last_build"])

    except Exception as e:
        st.error(f"Erro na otimização: {e}")


def _display_build_result(build: dict):
    items: list[dict] = build["items"]
    total_price = build["total_price"]
    total_score = build["total_score"]
    exec_time = build["exec_time"]
    budget = build["budget"]

    if not items:
        st.warning("Nenhuma configuração encontrada para este orçamento. Tente aumentar o valor.")
        return

    # Métricas principais
    st.success(f"✅ Configuração encontrada em {exec_time:.2f}ms")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Preço Total", format_brl(total_price))
    m2.metric("Orçamento Restante", format_brl(budget - total_price))
    m3.metric("Score Total", f"{total_score:.1f}")
    m4.metric("Tier", get_performance_tier(total_score / max(len(items), 1)))

    st.divider()

    # Botão: adicionar tudo ao carrinho
    if st.button("🛒 Adicionar todas as peças ao carrinho", use_container_width=True):
        added = add_build_to_cart(items)
        if added:
            st.success(f"{added} peça(s) adicionada(s) ao carrinho!")
        else:
            st.info("Todas as peças já estão no carrinho.")

    st.markdown("### 🔩 Peças Escolhidas")
    items_sorted = sort_items_by_category(items)

    for item in items_sorted:
        cat = item.get("category", "")
        gradient, accent = CATEGORY_GRADIENT.get(cat, ("linear-gradient(135deg,#555,#777)", "#888"))
        icon = CATEGORY_ICONS.get(cat, "🔧")
        name = item.get("name", "")
        price = float(item.get("price_brl", item.get("price_int", 0)))
        score = item.get("score", 0)
        search = item.get("store_search_name", name)

        with st.expander(f"{icon}  {cat} — {name[:50]}  ·  {format_brl(price)}"):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                # Card visual
                st.markdown(
                    f'<div class="part-card" style="background:{gradient}20;border:1px solid {accent}44;">'
                    f'  <div class="part-icon" style="background:{gradient};">{icon}</div>'
                    f'  <div><b style="font-size:1rem;">{name}</b><br>'
                    f'  <span style="color:{accent};">{format_brl(price)}</span>'
                    f'  &nbsp;·&nbsp; Score {score:.1f}</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown("**Buscar nas lojas:**")
                st.markdown(_store_links_html(search), unsafe_allow_html=True)
            with col_b:
                if st.button("🛒 Adicionar", key=f"cart_pc_{name[:20]}", use_container_width=True):
                    if add_to_cart(item, "pc_part"):
                        st.success("Adicionado!")
                    else:
                        st.info("Já está no carrinho.")

    st.divider()

    # Compatibilidade
    report = check_compatibility(items)
    emoji = get_compatibility_emoji(report)
    st.markdown(f"### {emoji} Compatibilidade")
    for err in report.errors:
        st.error(err)
    for warn in report.warnings:
        st.warning(warn)
    if report.is_compatible and not report.warnings:
        st.success(report.summary)

    # Gráficos
    gcol1, gcol2 = st.columns(2)
    with gcol1:
        st.plotly_chart(chart_budget_usage(total_price, budget - total_price), use_container_width=True)
    with gcol2:
        st.plotly_chart(chart_category_breakdown(items_sorted), use_container_width=True)
    st.plotly_chart(chart_selected_parts(items_sorted), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PÁGINA: NOTEBOOK
# ════════════════════════════════════════════════════════════════════════════
def page_notebook():
    st.markdown('<div style="font-size:2rem;font-weight:900;">💻 Escolher Notebook</div>', unsafe_allow_html=True)
    st.markdown("Encontre o melhor notebook para suas necessidades dentro do orçamento.")
    st.divider()

    df = get_laptops()
    col_param, col_result = st.columns([1, 2])

    with col_param:
        st.markdown("### ⚙️ Parâmetros")
        budget = _budget_selector("budget_nb", 6000)

        st.markdown("---")
        use_label = st.selectbox("Uso Principal", list(USE_PROFILES.keys()), key="nb_use")
        priority_label = st.selectbox("Prioridade", list(PRIORITIES.keys()), key="nb_prio")
        games = st.multiselect("🎮 Jogos Desejados", GAMES, default=["CS2"], key="nb_games")

        st.markdown("---")
        st.markdown("**Filtros**")
        min_ram = st.selectbox("RAM Mínima (GB)", [4, 8, 16, 32], index=1, key="nb_ram")
        min_ssd = st.selectbox("SSD Mínimo (GB)", [128, 256, 512, 1000], index=1, key="nb_ssd")
        gpu_ded = st.checkbox("GPU Dedicada Obrigatória", key="nb_gpu")
        screen_opts = ["Qualquer", "13–14\"", "15–16\"", "17\"+"]
        screen_pref = st.selectbox("Tela", screen_opts, key="nb_screen")

        run_btn = st.button("🔍 Recomendar Notebooks", type="primary", use_container_width=True)

    with col_result:
        if run_btn:
            _run_notebook_recommendation(df, budget, use_label, priority_label,
                                         games, min_ram, min_ssd, gpu_ded, screen_pref)
        elif st.session_state["last_laptop"] is not None:
            _display_laptop_result(st.session_state["last_laptop"], budget)
        else:
            st.markdown("""
            <div style="background:#1a1f2e;border-radius:16px;padding:2.5rem;text-align:center;
                        border:2px dashed rgba(123,104,238,0.3);">
                <div style="font-size:3rem;">💻</div>
                <h3 style="color:#a0aec0;">Configure e clique em Recomendar</h3>
                <p style="color:#718096;">O sistema ranqueia os notebooks por score e<br>
                mostra o top 5 dentro do seu orçamento.</p>
            </div>
            """, unsafe_allow_html=True)


def _run_notebook_recommendation(df, budget, use_label, priority_label,
                                  games, min_ram, min_ssd, gpu_ded, screen_pref):
    use_profile = profile_label_to_key(use_label)
    priority = priority_label_to_key(priority_label)

    with st.spinner("Analisando notebooks..."):
        f = df[df["price_brl"] <= budget].copy()
        f = f[f["ram_gb"] >= min_ram]
        f = f[f["storage_gb"] >= min_ssd]
        if gpu_ded:
            f = f[f["gpu"].str.lower().str.contains("rtx|gtx|rx ", na=False)]
        if screen_pref == "13–14\"":
            f = f[(f["screen_size"] >= 13) & (f["screen_size"] < 15)]
        elif screen_pref == "15–16\"":
            f = f[(f["screen_size"] >= 15) & (f["screen_size"] < 17)]
        elif screen_pref == "17\"+":
            f = f[f["screen_size"] >= 17]

        if f.empty:
            st.warning("Nenhum notebook encontrado com esses filtros. Relaxe os requisitos.")
            return

        f["computed_score"] = f.apply(
            lambda r: compute_laptop_score(r, use_profile, priority, games), axis=1
        )
        f = f.sort_values("computed_score", ascending=False).reset_index(drop=True)

        ranked = [
            {
                "name": row["name"],
                "category": "Notebook",
                "brand": row["brand"],
                "price_brl": float(row["price_brl"]),
                "cpu": row["cpu"],
                "gpu": row["gpu"],
                "ram_gb": float(row["ram_gb"]),
                "storage_gb": float(row["storage_gb"]),
                "screen_size": float(row["screen_size"]),
                "score": float(row["computed_score"]),
                "store_search_name": str(row.get("store_search_name", row["name"])),
            }
            for _, row in f.iterrows()
        ]
        st.session_state["last_laptop"] = ranked

    _display_laptop_result(ranked, budget)


def _display_laptop_result(ranked: list[dict], budget: float):
    if not ranked:
        st.warning("Nenhum notebook disponível.")
        return

    best = ranked[0]
    st.success(f"✅ Melhor notebook: **{best['name']}**")

    m1, m2, m3 = st.columns(3)
    m1.metric("Preço", format_brl(best["price_brl"]))
    m2.metric("Score", f"{best['score']:.1f}")
    m3.metric("Tier", get_laptop_tier(best["score"]))

    st.divider()

    # Melhor escolha em destaque
    gradient = "linear-gradient(135deg,#667eea,#764ba2)"
    st.markdown(f"""
    <div class="part-card" style="background:{gradient}22;border:1px solid #667eea55;padding:1.5rem;">
        <div class="part-icon" style="background:{gradient};font-size:2rem;">💻</div>
        <div>
            <div style="font-weight:800;font-size:1.1rem;">🥇 {best['name']}</div>
            <div style="margin-top:0.4rem;color:#a0aec0;">
                {best['cpu']} &nbsp;·&nbsp; {best['gpu']}<br>
                RAM {best['ram_gb']:.0f}GB &nbsp;·&nbsp; SSD {best['storage_gb']:.0f}GB
                &nbsp;·&nbsp; Tela {best['screen_size']}\"
            </div>
            <div style="margin-top:0.5rem;">
                <span style="color:#4CAF50;font-weight:700;font-size:1.1rem;">{format_brl(best['price_brl'])}</span>
                &nbsp;·&nbsp; Score {best['score']:.1f}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(_store_links_html(best["store_search_name"]), unsafe_allow_html=True)
    if st.button("🛒 Adicionar ao carrinho", key="nb_add_best"):
        if add_to_cart(best, "notebook"):
            st.success("Adicionado ao carrinho!")
        else:
            st.info("Já está no carrinho.")

    st.divider()
    st.markdown("### 🏆 Top 5 Notebooks")
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, nb in enumerate(ranked[:5]):
        with st.expander(f"{medals[i]}  {nb['name']}  ·  {format_brl(nb['price_brl'])}  ·  Score {nb['score']:.1f}"):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**CPU:** {nb['cpu']}  &nbsp;·&nbsp;  **GPU:** {nb['gpu']}")
                st.markdown(f"**RAM:** {nb['ram_gb']:.0f}GB  |  **SSD:** {nb['storage_gb']:.0f}GB  |  **Tela:** {nb['screen_size']}\"")
                st.markdown(_store_links_html(nb["store_search_name"]), unsafe_allow_html=True)
            with col_b:
                if st.button("🛒 Adicionar", key=f"nb_cart_{i}", use_container_width=True):
                    if add_to_cart(nb, "notebook"):
                        st.success("Adicionado!")
                    else:
                        st.info("Já está no carrinho.")

    st.divider()
    st.plotly_chart(chart_laptop_ranking(ranked[:5]), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PÁGINA: CARRINHO
# ════════════════════════════════════════════════════════════════════════════
def page_carrinho():
    st.markdown('<div style="font-size:2rem;font-weight:900;">🛒 Carrinho de Compras</div>', unsafe_allow_html=True)
    st.markdown("Peças e notebooks que você salvou. Clique nos links para buscar nas lojas.")
    st.divider()

    cart: list[dict] = st.session_state.get("cart", [])

    if not cart:
        st.markdown("""
        <div style="background:#1a1f2e;border-radius:16px;padding:3rem;text-align:center;
                    border:2px dashed rgba(123,104,238,0.3);">
            <div style="font-size:3.5rem;">🛒</div>
            <h3 style="color:#a0aec0;">Carrinho vazio</h3>
            <p style="color:#718096;">
                Acesse <b>Montar PC</b> ou <b>Escolher Notebook</b> e clique em
                "Adicionar ao Carrinho" nos itens que interessar.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Sumário
    total = sum(c["price"] for c in cart)
    pc_items = [c for c in cart if c["type"] == "pc_part"]
    nb_items = [c for c in cart if c["type"] == "notebook"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total no Carrinho", f"{len(cart)} itens")
    col2.metric("Peças de PC", len(pc_items))
    col3.metric("Notebooks", len(nb_items))
    col4.metric("Estimativa Total", format_brl(total))

    st.divider()

    # Ações globais
    a1, a2, a3 = st.columns([1, 1, 3])
    with a1:
        if st.button("🗑️ Limpar tudo", use_container_width=True):
            st.session_state["cart"] = []
            st.rerun()
    with a2:
        # Exportar como texto para copiar
        export_lines = [f"PC Build Optimizer — Lista de Compras\n{'='*40}"]
        for c in cart:
            links = generate_store_links(c["store_search_name"])
            export_lines.append(f"\n{c['category']}: {c['name']}")
            export_lines.append(f"Preço estimado: {format_brl(c['price'])}")
            for store, url in links.items():
                export_lines.append(f"  {store}: {url}")
        export_text = "\n".join(export_lines)
        st.download_button(
            "📋 Exportar lista",
            data=export_text,
            file_name="pc_build_lista.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.divider()

    # Seção: Peças de PC
    if pc_items:
        st.markdown("### 🔧 Peças de PC")
        for item in pc_items:
            _render_cart_item(item)

    # Seção: Notebooks
    if nb_items:
        st.markdown("### 💻 Notebooks")
        for item in nb_items:
            _render_cart_item(item)

    st.divider()
    st.markdown(f"**Estimativa total: {format_brl(total)}** _(preços estimados — consulte os links para valores atuais)_")


def _render_cart_item(item: dict):
    cat = item.get("category", "")
    gradient, accent = CATEGORY_GRADIENT.get(cat, ("linear-gradient(135deg,#667eea,#764ba2)", "#667eea"))
    icon = CATEGORY_ICONS.get(cat, "💻")
    name = item.get("name", "")
    price = item.get("price", 0.0)
    search = item.get("store_search_name", name)
    links = generate_store_links(search)
    meta = get_store_metadata()

    col_info, col_links, col_del = st.columns([3, 4, 1])
    with col_info:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:0.8rem;padding:0.5rem 0;">'
            f'  <div style="width:44px;height:44px;border-radius:10px;background:{gradient};'
            f'       display:flex;align-items:center;justify-content:center;font-size:1.5rem;">{icon}</div>'
            f'  <div>'
            f'    <div style="font-weight:700;">{name[:45]}</div>'
            f'    <div style="color:#a0aec0;font-size:0.85rem;">'
            f'      <span class="badge">{cat}</span> &nbsp; {format_brl(price)}'
            f'    </div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_links:
        st.markdown(
            "<div style='padding-top:0.3rem;'>"
            + " ".join([
                f'<a href="{url}" target="_blank" class="store-link-btn" '
                f'style="background:{STORE_COLORS.get(store,"#555")};">{store}</a>'
                for store, url in links.items()
            ])
            + "</div>",
            unsafe_allow_html=True,
        )
    with col_del:
        if st.button("✕", key=f"del_{item['id']}", help="Remover do carrinho"):
            remove_from_cart(item["id"])
            st.rerun()
    st.markdown('<hr style="margin:0.2rem 0;border-color:rgba(255,255,255,0.06);">', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# NAVEGAÇÃO PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════
PAGES = {
    "🏠 Home": page_home,
    "🔧 Montar PC": page_montar_pc,
    "💻 Escolher Notebook": page_notebook,
    "🛒 Carrinho": page_carrinho,
}


def main():
    cart_count = len(st.session_state.get("cart", []))
    cart_label = f"🛒 Carrinho ({cart_count})" if cart_count else "🛒 Carrinho"

    page_labels = {
        "🏠 Home": "🏠 Home",
        "🔧 Montar PC": "🔧 Montar PC",
        "💻 Escolher Notebook": "💻 Escolher Notebook",
        "🛒 Carrinho": cart_label,
    }

    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0 0.5rem;">
            <div style="font-size:2.5rem;">🖥️</div>
            <div style="font-weight:900;font-size:1.1rem;background:linear-gradient(135deg,#7B68EE,#20B2AA);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                PC Build Optimizer
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        page_name = st.radio(
            "Navegação",
            list(PAGES.keys()),
            format_func=lambda x: page_labels[x],
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("**Status:**")
        st.markdown(f"{'✅' if st.session_state['last_build'] else '⬜'} PC Configurado")
        st.markdown(f"{'✅' if st.session_state['last_laptop'] else '⬜'} Notebook Selecionado")
        st.markdown(f"{'✅' if st.session_state['last_iter_result'] else '⬜'} Knapsack Iterativo")
        st.markdown(f"{'✅' if st.session_state['last_rec_result'] else '⬜'} Knapsack Recursivo")
        if cart_count:
            st.markdown(f"🛒 **{cart_count} item(s) no carrinho**")
        st.divider()

        if st.button("🗑️ Limpar sessão", use_container_width=True):
            for k in ["last_build", "last_laptop", "last_iter_result", "last_rec_result"]:
                st.session_state[k] = None
            for k in ["last_iter_weights", "last_iter_values", "last_iter_names", "last_iter_cats"]:
                st.session_state[k] = []
            st.rerun()

    PAGES[page_name]()


if __name__ == "__main__":
    main()
