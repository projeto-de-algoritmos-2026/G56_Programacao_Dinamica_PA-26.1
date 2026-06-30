"""PC Build Optimizer — interface Streamlit."""

import sys
import os
import uuid

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
from find_solution import find_solution_from_dp, find_solution_from_memo
from store_links import generate_store_links, get_store_metadata
from charts import (
    chart_selected_parts, chart_budget_usage, chart_algorithm_comparison,
    chart_dp_table_heatmap, chart_laptop_ranking, chart_category_breakdown,
)
from metrics import compare_algorithms, format_metrics_table, efficiency_ratio
from utils import (
    USE_PROFILES, PRIORITIES, GAMES,
    format_brl, profile_label_to_key, priority_label_to_key,
    get_performance_tier, get_laptop_tier, sort_items_by_category, truncate_name,
)

# ─── Configuração ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PC Build Optimizer",
    page_icon="assets/favicon.png" if os.path.exists("assets/favicon.png") else "data:,",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Font Awesome 6 + CSS global ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');
:root {
  --accent:   #7B68EE;
  --accent2:  #20B2AA;
  --bg-card:  #13182b;
  --bg-deep:  #0d1120;
  --border:   rgba(123,104,238,.18);
  --text-muted: #8899aa;
}
html,[class*="css"]{font-family:'Inter',system-ui,sans-serif;}

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg,#0f0c29,#1a1660,#0f0c29);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 3rem 2.5rem;
  text-align: center;
  margin-bottom: 1.8rem;
}
.hero h1 {
  font-size: 2.8rem; font-weight: 900; letter-spacing:-.5px;
  background: linear-gradient(135deg,#7B68EE,#20B2AA);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin: 0 0 .5rem;
}
.hero p { color: var(--text-muted); font-size:1.1rem; margin:0; }

/* ── Feature card ── */
.feat-card {
  border-radius: 14px; padding: 1.4rem 1.2rem;
  text-align: center; color: white;
  border: 1px solid rgba(255,255,255,.07);
  height: 100%;
}
.feat-card .ico { font-size: 2rem; margin-bottom: .6rem; }
.feat-card h4  { font-size: .95rem; font-weight: 700; margin: 0 0 .35rem; }
.feat-card p   { font-size: .82rem; opacity: .88; margin: 0; }

/* ── Step card ── */
.step-card {
  background: var(--bg-card);
  border-top: 3px solid var(--accent);
  border-radius: 10px; padding: 1rem;
  text-align: center; height: 100%;
}
.step-card .num { font-size: 1.6rem; font-weight: 900; color: var(--accent); }
.step-card p { font-size: .83rem; color: var(--text-muted); margin: .3rem 0 0; }

/* ── Part card ── */
.part-card {
  display: flex; align-items: center; gap: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px; padding: 1rem 1.2rem;
  margin-bottom: .6rem;
}
.part-ico {
  width: 52px; height: 52px; border-radius: 11px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.35rem; color: white;
}
.part-name { font-weight: 700; font-size: .94rem; }
.part-meta { font-size: .82rem; color: var(--text-muted); margin-top: .2rem; }
.part-price { color: #4CAF50; font-weight: 700; }
.part-score { color: var(--accent); }

/* ── Store buttons ── */
.store-btn {
  display: inline-flex; align-items: center;
  padding: .45rem 1rem; border-radius: 9px; margin: .2rem .15rem;
  font-size: .88rem; font-weight: 700; letter-spacing: .01em;
  color: white !important; text-decoration: none !important;
  transition: opacity .18s, transform .12s;
  box-shadow: 0 2px 8px rgba(0,0,0,.35);
}
.store-btn:hover { opacity: .88; transform: translateY(-1px); }

/* ── Cart item ── */
.cart-row {
  display: flex; align-items: center; gap: .8rem;
  padding: .65rem 0;
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.cart-ico {
  width: 40px; height: 40px; border-radius: 9px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; color: white;
}
.badge {
  display: inline-block; padding: .18rem .55rem;
  border-radius: 20px; font-size: .72rem; font-weight: 700;
  background: rgba(123,104,238,.18); color: #9b8eff;
}

/* ── Algo box ── */
.algo-code {
  background: #0d1117; border: 1px solid #30363d;
  border-radius: 10px; padding: 1rem 1.2rem;
  font-family: 'Courier New', monospace; font-size: .88rem;
  color: #e6edf3; white-space: pre; overflow-x: auto;
}

/* ── Step trace ── */
.step-trace {
  background: #141a2a; border-left: 4px solid var(--accent);
  border-radius: 0 9px 9px 0; padding: .7rem 1rem; margin: .35rem 0;
}
</style>
""", unsafe_allow_html=True)

# ─── Ícones Font Awesome por categoria ───────────────────────────────────────
CATEGORY_FA = {
    "CPU":         ("fa-microchip",   "linear-gradient(135deg,#667eea,#764ba2)", "#667eea"),
    "GPU":         ("fa-display",     "linear-gradient(135deg,#11998e,#38ef7d)", "#11998e"),
    "Motherboard": ("fa-server",      "linear-gradient(135deg,#f46b45,#eea849)", "#f46b45"),
    "RAM":         ("fa-memory",      "linear-gradient(135deg,#4facfe,#00f2fe)", "#4facfe"),
    "Storage":     ("fa-hard-drive",  "linear-gradient(135deg,#fa709a,#fee140)", "#fa709a"),
    "PSU":         ("fa-plug",        "linear-gradient(135deg,#30cfd0,#330867)", "#30cfd0"),
    "Case":        ("fa-box",         "linear-gradient(135deg,#a18cd1,#fbc2eb)", "#a18cd1"),
    "Cooler":      ("fa-fan",         "linear-gradient(135deg,#89f7fe,#66a6ff)", "#89f7fe"),
    "Notebook":    ("fa-laptop",      "linear-gradient(135deg,#667eea,#764ba2)", "#667eea"),
}
DEFAULT_FA = ("fa-puzzle-piece", "linear-gradient(135deg,#555,#777)", "#888")

# (color, favicon-domain) por loja
STORE_META = {
    "KaBuM!":        ("#c94b00",  "kabum.com.br"),
    "TerabyteShop":  ("#0050a8",  "terabyteshop.com.br"),
    "Pichau":        ("#5828c4",  "pichau.com.br"),
    "Amazon Brasil": ("#d4760c",  "amazon.com.br"),
    "Mercado Livre": "#a08900",
}

_FAVICON = "https://www.google.com/s2/favicons?domain={domain}&sz=32"

def _store_links_html(search_name: str) -> str:
    links = generate_store_links(search_name)
    parts = []
    for s, url in links.items():
        meta = STORE_META.get(s, ("#444", ""))
        color, domain = (meta if isinstance(meta, tuple) else (meta, ""))
        favicon = _FAVICON.format(domain=domain) if domain else ""
        img_tag = (
            f'<img src="{favicon}" '
            f'style="width:18px;height:18px;vertical-align:middle;'
            f'border-radius:4px;margin-right:.45rem;flex-shrink:0;" '
            f'onerror="this.style.display=\'none\'">'
            if favicon else ""
        )
        parts.append(
            f'<a href="{url}" target="_blank" class="store-btn" style="background:{color};">'
            f'{img_tag}{s}</a>'
        )
    return "".join(parts)

def _ico(fa_class: str, gradient: str, size: str = "1.3rem") -> str:
    return (
        f'<div class="part-ico" style="background:{gradient};">'
        f'<i class="fas {fa_class}" style="font-size:{size};"></i></div>'
    )

# ─── Estado global ───────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "df_parts": None, "df_laptops": None,
        "last_build": None, "last_laptop": None,
        "last_iter_result": None, "last_rec_result": None,
        "last_iter_weights": [], "last_iter_values": [],
        "last_iter_names": [], "last_iter_cats": [],
        "last_budget": 5000, "budget_pc": 5000, "budget_nb": 6000,
        "cart": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

@st.cache_data(show_spinner=False)
def _load_parts():   return load_pc_parts()
@st.cache_data(show_spinner=False)
def _load_laptops(): return load_laptops()

def get_parts()   -> pd.DataFrame:
    if st.session_state["df_parts"]   is None: st.session_state["df_parts"]   = _load_parts()
    return st.session_state["df_parts"]
def get_laptops() -> pd.DataFrame:
    if st.session_state["df_laptops"] is None: st.session_state["df_laptops"] = _load_laptops()
    return st.session_state["df_laptops"]

# ─── Carrinho ────────────────────────────────────────────────────────────────
def add_to_cart(item: dict, kind: str = "pc_part") -> bool:
    if any(c["name"] == item["name"] for c in st.session_state["cart"]):
        return False
    st.session_state["cart"].append({
        "id": str(uuid.uuid4()),
        "name": item.get("name", ""),
        "category": item.get("category", ""),
        "price": float(item.get("price_brl", item.get("price_int", 0))),
        "store_search_name": item.get("store_search_name", item.get("name", "")),
        "type": kind,
    })
    return True

def remove_from_cart(item_id: str):
    st.session_state["cart"] = [c for c in st.session_state["cart"] if c["id"] != item_id]

# ─── Selector de orçamento com presets ───────────────────────────────────────
def _budget_selector(key: str) -> int:
    presets = [2000, 3000, 5000, 8000, 12000]
    cols = st.columns(len(presets))
    for col, val in zip(cols, presets):
        with col:
            if st.button(f"R$ {val//1000}k", key=f"pre_{key}_{val}", use_container_width=True):
                st.session_state[key] = val
                st.rerun()
    budget = st.number_input(
        "Orçamento personalizado (R$)",
        min_value=500, max_value=100_000,
        value=st.session_state[key], step=500,
        key=f"ni_{key}",
    )
    st.session_state[key] = int(budget)
    return int(budget)

# ════════════════════════════════════════════════════════════════════════════
# HOME
# ════════════════════════════════════════════════════════════════════════════
def page_home():
    st.markdown("""
    <div class="hero">
      <h1>PC Build Optimizer</h1>
      <p>Monte o PC Gamer ideal ou encontre o notebook certo — algoritmos de
         Programação Dinâmica encontram a combinação ótima dentro do seu orçamento.</p>
    </div>""", unsafe_allow_html=True)

    # Feature cards
    feats = [
        ("fa-wallet",          "linear-gradient(135deg,#667eea,#764ba2)",
         "Orçamento inteligente",
         "O sistema distribui o orçamento entre as peças com maior retorno de desempenho."),
        ("fa-gamepad",         "linear-gradient(135deg,#11998e,#38ef7d)",
         "Otimizado para jogos",
         "O score é ajustado pelos títulos que você quer rodar — a GPU certa para cada jogo."),
        ("fa-cart-shopping",   "linear-gradient(135deg,#fa709a,#fee140)",
         "Carrinho de compras",
         "Salve as peças e acesse links de busca nas lojas com um clique."),
        ("fa-code-branch",     "linear-gradient(135deg,#30cfd0,#330867)",
         "Algoritmo Knapsack",
         "Solução exata por Programação Dinâmica — não é sugestão, é o ótimo global."),
    ]
    cols = st.columns(4)
    for col, (fa, grad, title, desc) in zip(cols, feats):
        with col:
            st.markdown(f"""
            <div class="feat-card" style="background:{grad};">
              <div class="ico"><i class="fas {fa}"></i></div>
              <h4>{title}</h4><p>{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Como funciona")
    steps = [
        ("fa-wallet",              "#7B68EE", "Defina o orçamento"),
        ("fa-sliders",             "#11998e", "Escolha jogos e perfil"),
        ("fa-gears",               "#f46b45", "Algoritmo otimiza"),
        ("fa-list-check",          "#fa709a", "Veja as peças"),
        ("fa-arrow-up-right-from-square", "#4facfe", "Compre nas lojas"),
    ]
    scols = st.columns(5)
    for col, (fa, color, label) in zip(scols, steps):
        with col:
            st.markdown(f"""
            <div class="step-card">
              <div class="num"><i class="fas {fa}" style="color:{color};font-size:1.4rem;"></i></div>
              <p>{label}</p>
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Algoritmos de Programação Dinâmica")

    t_over, t_iter, t_rec, t_cmp, t_fs = st.tabs([
        "Visão Geral", "Knapsack Iterativo",
        "Knapsack Recursivo", "Comparação", "Find Solution",
    ])
    with t_over: _tab_overview()
    with t_iter: _tab_iterativo()
    with t_rec:  _tab_recursivo()
    with t_cmp:  _tab_comparacao()
    with t_fs:   _tab_find_solution()


def _tab_overview():
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Problema da Mochila (Knapsack 0/1)**")
        st.markdown("""
Dado itens com **pesos** e **valores** e uma mochila de capacidade **W**,
escolha os itens que maximizem o valor sem exceder a capacidade.

| Conceito | Equivalente no PC Build |
|----------|------------------------|
| Capacidade W | Orçamento (R$) |
| Peso do item | Preço da peça |
| Valor do item | Score de desempenho |
| Grupo | Categoria (CPU, GPU…) |
        """)
        st.code(
            "OPT(0, w)  = 0\n"
            "OPT(i, w)  = OPT(i-1, w)                  se weight[i] > w\n"
            "OPT(i, w)  = max( OPT(i-1, w),\n"
            "                  OPT(i-1, w-wi) + vi )",
            language="text",
        )
    with c2:
        st.markdown("**Grouped Knapsack — uma peça por categoria**")
        st.code(
            "dp[g][w] = max(\n"
            "    dp[g-1][w],                         # pula o grupo\n"
            "    max{ dp[g-1][w-wi]+vi : i in g }    # escolhe 1 peça\n"
            ")",
            language="text",
        )
        st.markdown("""
**Score de cada peça:**
```
score = desempenho_base × peso_categoria
      + bônus por jogos selecionados
      + bônus custo-benefício (score/R$1000)
```
**Complexidade:** O(n × W) tempo e espaço.
        """)


def _tab_iterativo():
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Bottom-up — preenche a tabela DP linha a linha.**")
        st.code(
            "for i in range(1, n+1):\n"
            "    for w in range(W+1):\n"
            "        if weights[i-1] > w:\n"
            "            dp[i][w] = dp[i-1][w]\n"
            "        else:\n"
            "            dp[i][w] = max(\n"
            "                dp[i-1][w],\n"
            "                dp[i-1][w-weights[i-1]] + values[i-1]\n"
            "            )",
            language="python",
        )
        st.markdown("**Vantagens:** sem recursão, sem risco de stack overflow.  \n"
                    "**Desvantagem:** calcula todos os O(n × W) estados.")
    with c2:
        st.markdown("**Executar com dados reais:**")
        df = get_parts()
        b = st.number_input("Orçamento (R$)", 500, 10_000, 3000, 500, key="h_iter_b")
        mx = st.slider("Max. itens", 5, 30, 15, key="h_iter_mx")
        if st.button("Executar Iterativo", key="h_iter_run", type="primary"):
            df_f = filter_by_budget(df, b).copy()
            df_f["computed_score"] = df_f.apply(
                lambda r: compute_part_score(r, "gaming_aaa", "performance"), axis=1)
            df_f = df_f.nlargest(mx, "computed_score")
            ws, vs, ns, cs = prepare_knapsack_inputs(df_f, b, "computed_score")
            sw, sc, _ = apply_budget_step(ws, b)
            with st.spinner("Calculando..."):
                res = knapsack_iterativo(sw, vs, sc)
            st.session_state.update({
                "last_iter_result": res, "last_iter_weights": ws,
                "last_iter_values": vs, "last_iter_names": ns,
                "last_iter_cats": cs, "last_budget": int(b),
            })
        res = st.session_state.get("last_iter_result")
        if res:
            m1, m2, m3 = st.columns(3)
            m1.metric("Valor ótimo", f"{res.value:.2f}")
            m2.metric("Estados", f"{res.states_computed:,}")
            m3.metric("Tempo (ms)", f"{res.execution_time_ms:.3f}")
            st.plotly_chart(chart_dp_table_heatmap(res.dp_table), use_container_width=True)


def _tab_recursivo():
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Top-down com memoization — resolve subproblemas sob demanda.**")
        st.code(
            "memo = {}\ndef OPT(i, w):\n"
            "    if i == 0 or w == 0: return 0\n"
            "    if (i, w) in memo: return memo[(i,w)]  # cache\n\n"
            "    if weights[i-1] > w:\n"
            "        res = OPT(i-1, w)\n"
            "    else:\n"
            "        res = max(OPT(i-1, w),\n"
            "                  OPT(i-1, w-weights[i-1]) + values[i-1])\n"
            "    memo[(i, w)] = res\n"
            "    return res",
            language="python",
        )
    with c2:
        st.markdown("**Executar com dados reais:**")
        df = get_parts()
        b = st.number_input("Orçamento (R$)", 500, 10_000, 3000, 500, key="h_rec_b")
        mx = st.slider("Max. itens", 5, 20, 12, key="h_rec_mx")
        if st.button("Executar Recursivo", key="h_rec_run", type="primary"):
            df_f = filter_by_budget(df, b).copy()
            df_f["computed_score"] = df_f.apply(
                lambda r: compute_part_score(r, "gaming_aaa", "performance"), axis=1)
            df_f = df_f.nlargest(mx, "computed_score")
            ws, vs, ns, cs = prepare_knapsack_inputs(df_f, b, "computed_score")
            sw, sc, _ = apply_budget_step(ws, b, max_states=1000)
            with st.spinner("Calculando..."):
                res = knapsack_recursivo(sw, vs, sc)
            st.session_state.update({
                "last_rec_result": res, "last_iter_weights": ws,
                "last_iter_values": vs, "last_iter_names": ns,
                "last_iter_cats": cs, "last_budget": int(b),
            })
        res = st.session_state.get("last_rec_result")
        if res:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Valor ótimo", f"{res.value:.2f}")
            m2.metric("Estados", f"{res.states_computed:,}")
            m3.metric("Cache hits", f"{res.cache_hits:,}")
            m4.metric("Tempo (ms)", f"{res.execution_time_ms:.3f}")
            st.json(get_memo_summary(res.memo_table))


def _tab_comparacao():
    ir = st.session_state.get("last_iter_result")
    rr = st.session_state.get("last_rec_result")
    if ir is None or rr is None:
        st.info("Execute ambos os algoritmos nas abas anteriores para comparar.")
        return
    ws = st.session_state.get("last_iter_weights", [])
    cap = st.session_state.get("last_budget", 3000)
    im, rm = compare_algorithms(ir, rr, len(ws), cap)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Knapsack Iterativo**")
        for k, v in format_metrics_table(im).items(): st.markdown(f"- **{k}:** {v}")
    with c2:
        st.markdown("**Knapsack Recursivo (Memoization)**")
        for k, v in format_metrics_table(rm).items(): st.markdown(f"- **{k}:** {v}")
    ratios = efficiency_ratio(im, rm)
    st.plotly_chart(
        chart_algorithm_comparison(im.execution_time_ms, rm.execution_time_ms,
                                   im.states_computed, rm.states_computed,
                                   im.optimal_value, rm.optimal_value),
        use_container_width=True)
    st.markdown(f"""
| Critério | Iterativo | Recursivo | Melhor |
|----------|-----------|-----------|--------|
| Tempo | {im.execution_time_ms:.4f}ms | {rm.execution_time_ms:.4f}ms | {'Recursivo' if rm.execution_time_ms < im.execution_time_ms else 'Iterativo'} |
| Estados | {im.states_computed:,} | {rm.states_computed:,} | {'Recursivo' if rm.states_computed < im.states_computed else 'Iterativo'} |
| Memória | {im.memory_estimate_kb:.1f}KB | {rm.memory_estimate_kb:.1f}KB | {'Recursivo' if rm.memory_estimate_kb < im.memory_estimate_kb else 'Iterativo'} |
| Resultado ótimo | {im.optimal_value:.2f} | {rm.optimal_value:.2f} | {'Iguais' if ratios['same_optimal'] else 'Diferem'} |
    """)


def _tab_find_solution():
    st.markdown("""
**Reconstrução da solução** — percorre a tabela DP de trás para frente:
```
w = W
para i de n até 1:
    se dp[i][w] != dp[i-1][w]:
        incluir item i
        w = w - weight[i]
```
    """)
    ir = st.session_state.get("last_iter_result")
    rr = st.session_state.get("last_rec_result")
    ns = st.session_state.get("last_iter_names", [])
    ws = st.session_state.get("last_iter_weights", [])
    vs = st.session_state.get("last_iter_values", [])
    cs = st.session_state.get("last_iter_cats", [])
    lb = st.session_state.get("last_budget", 3000)
    if ir is None and rr is None:
        st.info("Execute um dos algoritmos primeiro.")
        return
    c1, c2 = st.columns([1, 2])
    with c1:
        use_custom = st.checkbox("Capacidade personalizada", key="fs_custom")
        cap = st.number_input("Capacidade (R$)", 100, lb, lb // 2, 100, key="fs_cap") if use_custom else None
        src = st.radio("Fonte", ["Iterativo", "Recursivo"], key="fs_src")
        run = st.button("Reconstruir solução", type="primary", key="fs_run")
    with c2:
        if run:
            if src == "Iterativo" and ir:
                fs = find_solution_from_dp(ir.dp_table, ws, vs, ns, cs, capacity=cap)
            elif rr:
                fs = find_solution_from_memo(rr.memo_table, ws, vs, ns, cs, capacity=cap)
            else:
                st.error("Execute o algoritmo selecionado primeiro.")
                return
            init = cap if cap else lb
            st.markdown(f"**Orçamento inicial: {format_brl(init)}**")
            for step in fs.steps:
                st.markdown(
                    f'<div class="step-trace"><b>Passo {step.step}:</b> '
                    f'<b>{step.item_name}</b> ({step.category}) — {format_brl(step.item_price)}<br>'
                    f'{format_brl(step.budget_before)} &minus; {format_brl(step.item_price)}'
                    f' = <b>{format_brl(step.budget_after)}</b></div>',
                    unsafe_allow_html=True,
                )
            st.divider()
            a, b_, c = st.columns(3)
            a.metric("Preço total", format_brl(fs.total_price))
            b_.metric("Score total", f"{fs.total_score:.2f}")
            c.metric("Restante", format_brl(fs.budget_remaining))


# ════════════════════════════════════════════════════════════════════════════
# MONTAR PC
# ════════════════════════════════════════════════════════════════════════════
def page_montar_pc():
    st.markdown('<h2 style="font-weight:900;">Montar PC Gamer</h2>', unsafe_allow_html=True)
    st.caption("O Grouped Knapsack seleciona exatamente uma peça ótima por categoria.")
    st.divider()

    df = get_parts()
    col_p, col_r = st.columns([1, 2])

    with col_p:
        st.markdown("**Orçamento**")
        budget = _budget_selector("budget_pc")
        st.divider()
        use_label = st.selectbox("Uso principal", list(USE_PROFILES.keys()), key="pc_use")
        priority_label = st.selectbox("Prioridade", list(PRIORITIES.keys()), key="pc_prio")
        st.divider()
        games = st.multiselect("Jogos desejados", GAMES, default=["CS2", "Valorant"], key="pc_games")
        st.divider()
        run = st.button("Otimizar configuração", type="primary", use_container_width=True)

    with col_r:
        if run:
            _run_pc(df, budget, use_label, priority_label, games)
        elif st.session_state["last_build"]:
            _show_build(st.session_state["last_build"])
        else:
            st.markdown("""
            <div style="background:#13182b;border-radius:14px;padding:3rem;text-align:center;
                 border:2px dashed rgba(123,104,238,.25);">
              <i class="fas fa-desktop" style="font-size:3rem;color:#7B68EE;"></i>
              <h3 style="color:#8899aa;margin-top:1rem;">Configure e otimize</h3>
              <p style="color:#667;font-size:.9rem;">
                Grouped Knapsack garante 1 peça por categoria<br>
                respeitando o orçamento informado.
              </p>
            </div>""", unsafe_allow_html=True)


def _run_pc(df, budget, use_label, priority_label, games):
    use_profile  = profile_label_to_key(use_label)
    priority     = priority_label_to_key(priority_label)
    try:
        with st.spinner("Calculando configuração ideal…"):
            df_f = filter_by_budget(df, budget).copy()
            df_f["computed_score"] = df_f.apply(
                lambda r: compute_part_score(r, use_profile, priority, games), axis=1)
            groups = prepare_groups(df_f, use_profile, priority)
            res    = grouped_knapsack(groups, int(budget))
        st.session_state["last_build"] = {
            "items": res.selected_items, "total_price": res.total_price,
            "total_score": res.total_value, "budget": budget,
            "exec_time": res.execution_time_ms,
        }
        st.session_state["last_budget"] = int(budget)
        _show_build(st.session_state["last_build"])
    except Exception as e:
        st.error(f"Erro na otimização: {e}")


def _show_build(build: dict):
    items       = build["items"]
    total_price = build["total_price"]
    total_score = build["total_score"]
    budget      = build["budget"]
    exec_time   = build["exec_time"]

    if not items:
        st.warning("Nenhuma configuração encontrada. Aumente o orçamento.")
        return

    st.success(f"Configuração encontrada em {exec_time:.1f}ms")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Preço total",        format_brl(total_price))
    m2.metric("Orçamento restante", format_brl(budget - total_price))
    m3.metric("Score total",        f"{total_score:.1f}")
    m4.metric("Tier",               get_performance_tier(total_score / max(len(items), 1)))

    st.divider()
    if st.button("Adicionar todas as peças ao carrinho", use_container_width=True):
        added = sum(1 for it in items if add_to_cart(it, "pc_part"))
        st.success(f"{added} peça(s) adicionada(s) ao carrinho.") if added else st.info("Todas já estão no carrinho.")

    st.markdown("**Peças escolhidas**")
    for item in sort_items_by_category(items):
        _part_row(item)

    st.divider()
    report = check_compatibility(items)
    st.markdown(f"**{get_compatibility_emoji(report)} Compatibilidade**")
    for e in report.errors:   st.error(e)
    for w in report.warnings: st.warning(w)
    if report.is_compatible and not report.warnings:
        st.success(report.summary)

    g1, g2 = st.columns(2)
    with g1: st.plotly_chart(chart_budget_usage(total_price, budget - total_price), use_container_width=True)
    with g2: st.plotly_chart(chart_category_breakdown(items), use_container_width=True)
    st.plotly_chart(chart_selected_parts(items), use_container_width=True)


def _part_row(item: dict):
    cat    = item.get("category", "")
    fa, gradient, accent = CATEGORY_FA.get(cat, DEFAULT_FA)
    name   = item.get("name", "")
    price  = float(item.get("price_brl", item.get("price_int", 0)))
    score  = item.get("score", 0)
    search = item.get("store_search_name", name)

    with st.expander(f"{cat}  —  {truncate_name(name, 52)}  ·  {format_brl(price)}"):
        ca, cb = st.columns([3, 1])
        with ca:
            st.markdown(
                f'<div class="part-card">'
                f'  {_ico(fa, gradient)}'
                f'  <div>'
                f'    <div class="part-name">{name}</div>'
                f'    <div class="part-meta">'
                f'      <span class="badge">{cat}</span>'
                f'      <span class="part-price" style="margin-left:.6rem;">{format_brl(price)}</span>'
                f'      <span class="part-score" style="margin-left:.6rem;">Score {score:.1f}</span>'
                f'    </div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown("Buscar nas lojas:")
            st.markdown(_store_links_html(search), unsafe_allow_html=True)
        with cb:
            if st.button("Adicionar ao carrinho", key=f"c_pc_{name[:18]}", use_container_width=True):
                st.success("Adicionado!") if add_to_cart(item, "pc_part") else st.info("Já no carrinho.")


# ════════════════════════════════════════════════════════════════════════════
# ESCOLHER NOTEBOOK
# ════════════════════════════════════════════════════════════════════════════
def page_notebook():
    st.markdown('<h2 style="font-weight:900;">Escolher Notebook</h2>', unsafe_allow_html=True)
    st.caption("Ranqueamento por score de desempenho dentro do orçamento.")
    st.divider()

    df = get_laptops()
    col_p, col_r = st.columns([1, 2])

    with col_p:
        st.markdown("**Orçamento**")
        budget = _budget_selector("budget_nb")
        st.divider()
        use_label      = st.selectbox("Uso principal", list(USE_PROFILES.keys()), key="nb_use")
        priority_label = st.selectbox("Prioridade",    list(PRIORITIES.keys()),   key="nb_prio")
        games          = st.multiselect("Jogos",        GAMES, default=["CS2"],    key="nb_games")
        st.divider()
        st.markdown("**Filtros**")
        min_ram    = st.selectbox("RAM mínima (GB)", [4, 8, 16, 32], index=1, key="nb_ram")
        min_ssd    = st.selectbox("SSD mínimo (GB)", [128, 256, 512, 1000], index=1, key="nb_ssd")
        gpu_ded    = st.checkbox("GPU dedicada obrigatória", key="nb_gpu")
        screen_opt = st.selectbox("Tela", ["Qualquer", "13–14\"", "15–16\"", "17\"+"], key="nb_scr")
        st.divider()
        run = st.button("Recomendar notebooks", type="primary", use_container_width=True)

    with col_r:
        if run:
            _run_nb(df, budget, use_label, priority_label, games, min_ram, min_ssd, gpu_ded, screen_opt)
        elif st.session_state["last_laptop"]:
            _show_nb(st.session_state["last_laptop"], budget)
        else:
            st.markdown("""
            <div style="background:#13182b;border-radius:14px;padding:3rem;text-align:center;
                 border:2px dashed rgba(123,104,238,.25);">
              <i class="fas fa-laptop" style="font-size:3rem;color:#7B68EE;"></i>
              <h3 style="color:#8899aa;margin-top:1rem;">Configure e recomende</h3>
            </div>""", unsafe_allow_html=True)


def _run_nb(df, budget, use_label, priority_label, games, min_ram, min_ssd, gpu_ded, screen_opt):
    up = profile_label_to_key(use_label)
    pr = priority_label_to_key(priority_label)
    with st.spinner("Analisando notebooks…"):
        f = df[df["price_brl"] <= budget].copy()
        f = f[f["ram_gb"] >= min_ram]
        f = f[f["storage_gb"] >= min_ssd]
        if gpu_ded:
            f = f[f["gpu"].str.lower().str.contains("rtx|gtx|rx ", na=False)]
        if screen_opt == "13–14\"":  f = f[(f["screen_size"]>=13)&(f["screen_size"]<15)]
        elif screen_opt == "15–16\"": f = f[(f["screen_size"]>=15)&(f["screen_size"]<17)]
        elif screen_opt == "17\"+":   f = f[f["screen_size"]>=17]
        if f.empty:
            st.warning("Nenhum notebook com esses filtros. Relaxe os requisitos."); return
        f["computed_score"] = f.apply(lambda r: compute_laptop_score(r, up, pr, games), axis=1)
        f = f.sort_values("computed_score", ascending=False).reset_index(drop=True)
        ranked = [
            {"name": r["name"], "category": "Notebook", "brand": r["brand"],
             "price_brl": float(r["price_brl"]), "cpu": r["cpu"], "gpu": r["gpu"],
             "ram_gb": float(r["ram_gb"]), "storage_gb": float(r["storage_gb"]),
             "screen_size": float(r["screen_size"]), "score": float(r["computed_score"]),
             "store_search_name": str(r.get("store_search_name", r["name"]))}
            for _, r in f.iterrows()
        ]
        st.session_state["last_laptop"] = ranked
    _show_nb(ranked, budget)


def _show_nb(ranked: list[dict], budget: float):
    if not ranked:
        st.warning("Nenhum notebook disponível.")
        return
    best = ranked[0]
    st.success(f"Melhor resultado: {best['name']}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Preço",  format_brl(best["price_brl"]))
    m2.metric("Score",  f"{best['score']:.1f}")
    m3.metric("Tier",   get_laptop_tier(best["score"]))
    st.divider()

    # Destaque — melhor notebook
    fa, gradient, accent = CATEGORY_FA.get("Notebook", DEFAULT_FA)
    st.markdown(
        f'<div class="part-card" style="border-color:{accent}55;">'
        f'  {_ico(fa, gradient, "1.5rem")}'
        f'  <div style="flex:1;">'
        f'    <div class="part-name" style="font-size:1.05rem;">{best["name"]}</div>'
        f'    <div class="part-meta">{best["cpu"]} &nbsp;·&nbsp; {best["gpu"]}</div>'
        f'    <div class="part-meta">RAM {best["ram_gb"]:.0f}GB &nbsp;·&nbsp;'
        f'    SSD {best["storage_gb"]:.0f}GB &nbsp;·&nbsp; Tela {best["screen_size"]}"</div>'
        f'    <div style="margin-top:.5rem;">'
        f'      <span class="part-price">{format_brl(best["price_brl"])}</span>'
        f'      <span class="part-score" style="margin-left:.6rem;">Score {best["score"]:.1f}</span>'
        f'    </div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(_store_links_html(best["store_search_name"]), unsafe_allow_html=True)
    if st.button("Adicionar ao carrinho", key="nb_best_cart"):
        st.success("Adicionado!") if add_to_cart(best, "notebook") else st.info("Já no carrinho.")

    st.divider()
    st.markdown("**Top 5**")
    for i, nb in enumerate(ranked[:5]):
        prefix = ["1.", "2.", "3.", "4.", "5."][i]
        with st.expander(f"{prefix}  {nb['name']}  ·  {format_brl(nb['price_brl'])}  ·  Score {nb['score']:.1f}"):
            ca, cb = st.columns([3, 1])
            with ca:
                st.markdown(f"**CPU:** {nb['cpu']}  &nbsp;·&nbsp;  **GPU:** {nb['gpu']}")
                st.markdown(f"**RAM:** {nb['ram_gb']:.0f}GB  |  **SSD:** {nb['storage_gb']:.0f}GB  |  **Tela:** {nb['screen_size']}\"")
                st.markdown(_store_links_html(nb["store_search_name"]), unsafe_allow_html=True)
            with cb:
                if st.button("Adicionar ao carrinho", key=f"nb_c_{i}", use_container_width=True):
                    st.success("Adicionado!") if add_to_cart(nb, "notebook") else st.info("Já no carrinho.")

    st.divider()
    st.plotly_chart(chart_laptop_ranking(ranked[:5]), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# CARRINHO
# ════════════════════════════════════════════════════════════════════════════
def page_carrinho():
    st.markdown('<h2 style="font-weight:900;">Carrinho de compras</h2>', unsafe_allow_html=True)
    st.caption("Itens salvos. Clique nos links para buscar nas lojas e comparar preços.")
    st.divider()

    cart: list[dict] = st.session_state.get("cart", [])
    if not cart:
        st.markdown("""
        <div style="background:#13182b;border-radius:14px;padding:3rem;text-align:center;
             border:2px dashed rgba(123,104,238,.25);">
          <i class="fas fa-cart-shopping" style="font-size:3rem;color:#7B68EE;"></i>
          <h3 style="color:#8899aa;margin-top:1rem;">Carrinho vazio</h3>
          <p style="color:#667;font-size:.9rem;">
            Acesse Montar PC ou Escolher Notebook e clique em<br>
            "Adicionar ao carrinho" nos itens de interesse.
          </p>
        </div>""", unsafe_allow_html=True)
        return

    total     = sum(c["price"] for c in cart)
    pc_items  = [c for c in cart if c["type"] == "pc_part"]
    nb_items  = [c for c in cart if c["type"] == "notebook"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total de itens",  len(cart))
    m2.metric("Peças de PC",     len(pc_items))
    m3.metric("Notebooks",       len(nb_items))
    m4.metric("Estimativa total", format_brl(total))
    st.divider()

    # Ações
    a1, a2, _ = st.columns([1, 1, 3])
    with a1:
        if st.button("Limpar carrinho", use_container_width=True):
            st.session_state["cart"] = []
            st.rerun()
    with a2:
        lines = ["PC Build Optimizer — Lista de Compras", "=" * 40]
        for c in cart:
            links = generate_store_links(c["store_search_name"])
            lines += [f"\n{c['category']}: {c['name']}",
                      f"Preco estimado: {format_brl(c['price'])}"]
            lines += [f"  {s}: {u}" for s, u in links.items()]
        st.download_button(
            "Exportar lista (.txt)", data="\n".join(lines),
            file_name="pc_build_lista.txt", mime="text/plain",
            use_container_width=True,
        )

    st.divider()
    if pc_items:
        st.markdown("**Peças de PC**")
        for item in pc_items: _cart_row(item)
    if nb_items:
        st.markdown("**Notebooks**")
        for item in nb_items: _cart_row(item)

    st.divider()
    st.markdown(
        f"Estimativa total: **{format_brl(total)}**  "
        f"_(preços estimados — consulte os links para valores atuais)_"
    )


def _cart_row(item: dict):
    cat = item.get("category", "")
    fa, gradient, accent = CATEGORY_FA.get(cat, DEFAULT_FA)
    name   = item["name"]
    price  = item["price"]
    search = item["store_search_name"]
    links  = generate_store_links(search)

    c_ico, c_info, c_links, c_del = st.columns([.6, 2, 4, .6])
    with c_ico:
        st.markdown(
            f'<div class="cart-ico" style="background:{gradient};margin-top:.3rem;">'
            f'<i class="fas {fa}"></i></div>',
            unsafe_allow_html=True,
        )
    with c_info:
        st.markdown(
            f'<div style="padding-top:.25rem;">'
            f'  <div style="font-weight:700;font-size:.9rem;">{truncate_name(name, 36)}</div>'
            f'  <div><span class="badge">{cat}</span>'
            f'  <span style="color:#4CAF50;font-weight:700;margin-left:.5rem;">{format_brl(price)}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c_links:
        st.markdown(
            f'<div style="padding-top:.3rem;">{_store_links_html(search)}</div>',
            unsafe_allow_html=True,
        )
    with c_del:
        if st.button("", icon=":material/delete:", key=f"del_{item['id']}", help="Remover"):
            remove_from_cart(item["id"])
            st.rerun()
    st.markdown('<hr style="margin:.15rem 0;border-color:rgba(255,255,255,.05);">', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# NAVEGAÇÃO
# ════════════════════════════════════════════════════════════════════════════
PAGES = {
    "Home":               page_home,
    "Montar PC":          page_montar_pc,
    "Escolher Notebook":  page_notebook,
    "Carrinho":           page_carrinho,
}


def main():
    cart_n = len(st.session_state.get("cart", []))

    def _label(k: str) -> str:
        if k == "Carrinho" and cart_n:
            return f"Carrinho  ({cart_n})"
        return k

    with st.sidebar:
        st.markdown("""
        <div style="padding:1.2rem 0 .5rem;text-align:center;">
          <i class="fas fa-desktop" style="font-size:2.2rem;color:#7B68EE;"></i>
          <div style="font-weight:900;font-size:1.05rem;margin-top:.4rem;
               background:linear-gradient(135deg,#7B68EE,#20B2AA);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            PC Build Optimizer
          </div>
        </div>""", unsafe_allow_html=True)
        st.divider()

        page = st.radio(
            "Navegação",
            list(PAGES.keys()),
            format_func=_label,
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("**Status da sessão**")
        def _s(ok): return "completo" if ok else "pendente"
        st.markdown(f"PC Gamer — {_s(st.session_state['last_build'])}")
        st.markdown(f"Notebook — {_s(st.session_state['last_laptop'])}")
        st.markdown(f"Knapsack Iterativo — {_s(st.session_state['last_iter_result'])}")
        st.markdown(f"Knapsack Recursivo — {_s(st.session_state['last_rec_result'])}")
        if cart_n:
            st.markdown(f"Carrinho — **{cart_n} item(s)**")
        st.divider()

        if st.button("Limpar sessão", use_container_width=True):
            for k in ["last_build","last_laptop","last_iter_result","last_rec_result"]:
                st.session_state[k] = None
            for k in ["last_iter_weights","last_iter_values","last_iter_names","last_iter_cats"]:
                st.session_state[k] = []
            st.rerun()

    PAGES[page]()


if __name__ == "__main__":
    main()
