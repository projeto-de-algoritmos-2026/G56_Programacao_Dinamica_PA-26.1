# 🖥️ PC Build Optimizer

> Sistema inteligente para montagem de PC Gamer e seleção de notebooks usando Programação Dinâmica.

---

## Vídeo de Apresentação

[![Assista à demonstração do sistema](https://img.youtube.com/vi/Mg9q_6k3Q5Y/maxresdefault.jpg)](https://youtu.be/Mg9q_6k3Q5Y)

---

## Descrição

PC Build Optimizer é uma aplicação web interativa que resolve o problema de escolha de componentes de computador como um **problema de otimização combinatória**, utilizando o algoritmo clássico da **Mochila (Knapsack)** e sua variação por grupos (**Grouped Knapsack / Multiple Choice Knapsack**).

O usuário informa seu orçamento, os jogos que deseja rodar, o perfil de uso e a prioridade de compra. O sistema encontra automaticamente a **configuração ótima** de peças ou o **melhor notebook** dentro das restrições definidas, maximizando um score composto de desempenho e custo-benefício.

---

## Objetivo

Dado um orçamento fixo e preferências de uso, encontrar a combinação de peças de PC (ou notebook) que **maximiza o score de desempenho/custo-benefício**, garantindo:

- Exatamente uma peça por categoria (CPU, GPU, Placa-mãe, RAM, Armazenamento, Fonte, Gabinete, Cooler).
- Compatibilidade básica entre os componentes.
- Respeito ao orçamento total.

---

## Motivação

Montar um PC é uma tarefa que envolve dezenas de decisões simultâneas — escolher entre centenas de peças com preços, desempenhos e compatibilidades diferentes. O problema é análogo ao **Knapsack Problem**, onde cada peça tem um "peso" (preço) e um "valor" (score de desempenho), e a capacidade da mochila é o orçamento disponível.

A extensão natural para PC Building é o **Grouped Knapsack**: em vez de escolher livremente qualquer subconjunto de itens, é preciso escolher **exatamente um item por grupo** (categoria de peça), garantindo uma configuração completa e funcional.

---

## Como o sistema ajuda o usuário

1. **Informações de entrada:** orçamento, jogos, perfil de uso e prioridade.
2. **Cálculo automático:** o algoritmo encontra a configuração ótima em milissegundos.
3. **Resultado transparente:** peças escolhidas, preço total, score e justificativa.
4. **Verificação de compatibilidade:** alertas de incompatibilidade entre socket, memória e potência.
5. **Links de compra:** links diretos de busca nas principais lojas brasileiras (KaBuM!, Terabyte, Pichau, Amazon Brasil, Mercado Livre).
6. **Comparação de algoritmos:** execute o iterativo e o recursivo lado a lado e compare tempo, estados e memória.

---

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| Montar PC Gamer | Seleciona peças por Grouped Knapsack e exibe configuração completa |
| Escolher Notebook | Ranqueia notebooks por score dentro do orçamento |
| Knapsack Iterativo | Bottom-up com tabela DP completa e heatmap |
| Knapsack Recursivo | Top-down com memoization e sumário do cache |
| Comparação | Métricas lado a lado dos dois algoritmos |
| Find Solution | Reconstrução passo a passo da solução |
| Links de Compra | Links de busca em 5 lojas brasileiras |
| Upload de CSV | Substitua o dataset padrão por qualquer arquivo CSV |
| Filtros de Dataset | Filtre por categoria, marca e faixa de preço |
| Gráficos interativos | Distribuição de preços, score por categoria, orçamento usado |

---

## Modos disponíveis

### Montar PC Gamer

O usuário informa:
- Orçamento total (ex: R$ 5.000)
- Perfil de uso (Jogos AAA, Programação, Edição de Vídeo, etc.)
- Jogos desejados (Cyberpunk 2077, CS2, Valorant, etc.)
- Prioridade (Melhor Desempenho, Melhor Custo-Benefício, etc.)

O sistema retorna:
- Configuração completa com 1 peça por categoria
- Preço total e orçamento restante
- Score total da configuração
- Verificação de compatibilidade
- Links de busca para cada peça

### Escolher Notebook

O usuário informa:
- Orçamento
- Perfil de uso e jogos
- Filtros: RAM mínima, armazenamento mínimo, GPU dedicada, tamanho de tela

O sistema retorna:
- Melhor notebook dentro do orçamento
- Top 5 notebooks ranqueados por score
- Especificações completas
- Links de compra

---

## Programação Dinâmica

O núcleo do sistema usa **Programação Dinâmica (DP)** para resolver o problema de seleção de componentes de forma exata e eficiente.

A DP garante que a solução encontrada é **globalmente ótima** — não apenas localmente boa. Isso é impossível com algoritmos gulosos simples, que podem perder combinações melhores por decisões locais subótimas.

---

## Knapsack (Mochila 0/1)

**Modelagem:**

| Conceito Knapsack | Equivalente no PC Build |
|---|---|
| Capacidade W | Orçamento total (R$) |
| Peso do item | Preço da peça (R$) |
| Valor do item | Score de desempenho |
| Item selecionado | Peça incluída na configuração |

**Recorrência:**

```
dp[0][w] = 0   para todo w

dp[i][w] = dp[i-1][w]                          se weight[i] > w
dp[i][w] = max(dp[i-1][w],                     caso contrário
               dp[i-1][w - weight[i]] + value[i])
```

**Complexidade:** O(n × W) tempo, O(n × W) espaço.

---

## Grouped Knapsack

Para garantir que a configuração final tenha exatamente uma peça de cada categoria, o sistema usa o **Grouped Knapsack (Multiple Choice Knapsack)**:

```
dp[g][w] = max(dp[g-1][w],
               max{ dp[g-1][w - wi] + vi : item i ∈ grupo g, wi ≤ w })
```

Onde cada grupo `g` é uma categoria de peça (CPU, GPU, RAM, etc.).

**Propriedades:**
- Escolhe **no máximo um** item por grupo.
- Respeita o orçamento global.
- Maximiza o score total.
- Permite configuração incompleta quando o orçamento não cobre todos os grupos.

---

## Knapsack Iterativo

Implementação **bottom-up** que preenche a tabela DP linha por linha:

```python
for i in range(1, n + 1):
    for w in range(W + 1):
        if weights[i-1] > w:
            dp[i][w] = dp[i-1][w]
        else:
            dp[i][w] = max(dp[i-1][w],
                           dp[i-1][w - weights[i-1]] + values[i-1])
```

**Vantagens:** sem overhead de chamadas recursivas, sem risco de stack overflow, previsível.

**Complexidade:** O(n × W) tempo e espaço.

---

## Knapsack Recursivo com Memoization

Implementação **top-down** que resolve subproblemas sob demanda e armazena resultados:

```python
def OPT(i, w):
    if i == 0 or w == 0:
        return 0
    if (i, w) in memo:
        return memo[(i, w)]   # cache hit

    if weights[i-1] > w:
        result = OPT(i-1, w)
    else:
        result = max(OPT(i-1, w),
                     OPT(i-1, w - weights[i-1]) + values[i-1])

    memo[(i, w)] = result
    return result
```

**Vantagens:** calcula apenas os subproblemas necessários; pode ser significativamente mais rápido quando o espaço de estados é esparso.

**Complexidade:** O(n × W) no pior caso, frequentemente melhor na prática.

---

## Find Solution

A **reconstrução da solução** percorre a tabela DP (ou o memo) de trás para frente:

```
w = W
para i de n até 1:
    se dp[i][w] ≠ dp[i-1][w]:
        incluir item i
        w = w - weight[i]
```

O sistema também suporta reconstrução para uma **capacidade personalizada** — o usuário pode informar um valor menor que o orçamento original (ex: `Find Solution(3000)` com orçamento de 5000).

O resultado é exibido em **passo a passo** com o orçamento restante após cada escolha.

---

## Modelagem do problema

### Desktop (Grouped Knapsack)

1. Carrega o dataset de peças.
2. Calcula o score de cada peça com base no perfil de uso, jogos e prioridade.
3. Agrupa as peças por categoria.
4. Executa o Grouped Knapsack com orçamento = capacidade.
5. Reconstrói a solução e verifica compatibilidade.
6. Exibe configuração com links de compra.

### Notebook (Knapsack clássico + ranking)

1. Filtra notebooks dentro do orçamento e filtros do usuário.
2. Calcula o score de cada notebook.
3. Ordena por score descendente.
4. Exibe top 5 com especificações e links.

---

## Cálculo do score

O score de cada peça ou notebook é calculado pela fórmula:

```
score = desempenho_base × peso_categoria
      + bônus_jogos
      + bônus_utilidade
      + bônus_custo_benefício
```

Onde:

- **desempenho_base:** valor de 0–100 do campo `performance_score` (baseado em benchmarks reais ou estimativas).
- **peso_categoria:** multiplicador do perfil de uso para cada categoria. Ex: para "Jogos AAA", GPU tem peso 2.0; para "Programação", CPU tem peso 1.5.
- **bônus_jogos:** média dos bônus de cada jogo selecionado para a categoria da peça. Ex: Cyberpunk 2077 dá +10 para GPU.
- **bônus_custo_benefício:** `performance_score / (price_brl / 1000)` — quanto de desempenho o usuário recebe por R$ 1000.

O score final é usado como "valor" no Knapsack, de forma que o algoritmo maximize o desempenho total dentro do orçamento.

---

## Compatibilidade básica

O sistema verifica automaticamente:

| Regra | Implementação |
|---|---|
| CPU AMD + Placa-mãe AMD | Verifica campo `socket` (AM4/AM5) ou heurística pelo nome |
| CPU Intel + Placa-mãe Intel | Verifica socket (LGA1700) ou heurística |
| RAM DDR4/DDR5 | Compara `memory_type` da placa-mãe com o nome da RAM |
| Potência da fonte | Estima consumo de CPU + GPU e verifica se a fonte tem 20% de folga |
| Categorias obrigatórias | Alerta se CPU, Placa-mãe, RAM, Armazenamento, Fonte ou Gabinete estiver ausente |

**Nota:** quando o dataset não possui os campos de socket ou tipo de memória, o sistema aplica heurísticas baseadas no nome da peça (ex: presença de "B450", "AM4", "LGA1700" no nome).

---

## Datasets usados

| Dataset | Conteúdo | Fonte |
|---|---|---|
| `sample_pc_parts.csv` | 95 peças de PC com preços estimados em BRL | Compilado de referências públicas |
| `sample_laptops.csv` | 40 notebooks com especificações e preços BRL | Compilado de referências públicas |

### Datasets públicos de referência (Kaggle)

- [Computer Parts — CPUs and GPUs](https://www.kaggle.com/datasets/iliassekkaf/computerparts)
- [PC Components Dataset](https://www.kaggle.com/datasets/sudhanshuy17/pccomponents)
- [PC Component Prices Comparison](https://www.kaggle.com/datasets/thedevastator/pc-component-prices-comparison)
- [Laptop Price](https://www.kaggle.com/datasets/muhammetvarl/laptop-price)
- [Laptops Price Dataset](https://www.kaggle.com/datasets/juanmerinobermejo/laptops-price-dataset)

### Como baixar datasets externos

1. Acesse o link do dataset no Kaggle.
2. Clique em **Download** (requer conta Kaggle gratuita).
3. Extraia o CSV.
4. Na interface web, vá para **Dataset → Upload CSV** e faça o upload.
5. O sistema detecta e mapeia automaticamente as colunas.

---

## Como rodar com Docker

```bash
git clone https://github.com/projeto-de-algoritmos-2026/G56_Programacao_Dinamica_PA-26.1.git
cd G56_Programacao_Dinamica_PA-26.1

docker compose up --build
```

Acesse: [http://localhost:8501](http://localhost:8501)

Para parar:

```bash
docker compose down
```

---

## Como rodar localmente

**Requisitos:** Python 3.10+

```bash
git clone https://github.com/projeto-de-algoritmos-2026/G56_Programacao_Dinamica_PA-26.1.git
cd G56_Programacao_Dinamica_PA-26.1

pip install -r requirements.txt

streamlit run src/app.py
```

Acesse: [http://localhost:8501](http://localhost:8501)

---

## Como usar a interface

### Navegação

Use o menu lateral esquerdo para navegar entre as páginas.

### Fluxo recomendado

1. **Home** — leia a explicação do sistema e dos algoritmos.
2. **Dataset** — explore os dados ou faça upload do seu CSV.
3. **Montar PC** — informe orçamento, jogos e perfil; clique em "Otimizar Configuração".
4. **Knapsack Iterativo / Recursivo** — execute os algoritmos individualmente para ver a tabela DP.
5. **Comparação** — compare tempo, estados e memória dos dois algoritmos.
6. **Find Solution** — veja o passo a passo da reconstrução da solução.
7. **Links de Compra** — acesse as lojas para comprar as peças recomendadas.

---

## Exemplos de uso

### Exemplo 1 — PC Gamer Intermediário

```
Orçamento: R$ 5.000
Perfil: Jogos AAA
Jogos: Cyberpunk 2077, Elden Ring
Prioridade: Melhor Desempenho
```

Resultado esperado: RTX 4060 + Ryzen 5 5600 + 16GB DDR4 + SSD NVMe + B550 + Fonte 650W + Gabinete mid-tower.

### Exemplo 2 — Notebook para Programação

```
Orçamento: R$ 6.000
Perfil: Programação
RAM mínima: 16GB
GPU Dedicada: Não obrigatória
```

Resultado esperado: notebook com CPU i5/i7 ou Ryzen 5/7, 16GB RAM, SSD 512GB.

### Exemplo 3 — PC de Entrada para Estudos

```
Orçamento: R$ 3.000
Perfil: Estudos
Jogos: Minecraft, The Sims
Prioridade: Melhor Custo-Benefício
```

Resultado esperado: configuração sem GPU dedicada (vídeo integrado), CPU mid-range, 8–16GB RAM.

---

## Estrutura do projeto

```
.
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── src/
│   ├── app.py                  # Interface Streamlit principal
│   ├── data_loader.py          # Carregamento e validação de datasets
│   ├── preprocessing.py        # Pré-processamento e escala de dados
│   ├── scoring.py              # Cálculo de score de peças e notebooks
│   ├── compatibility.py        # Verificação de compatibilidade
│   ├── knapsack_iterativo.py   # Knapsack bottom-up
│   ├── knapsack_recursivo.py   # Knapsack top-down com memoization
│   ├── grouped_knapsack.py     # Grouped Knapsack para montagem de PC
│   ├── find_solution.py        # Reconstrução da solução
│   ├── store_links.py          # Geração de links de busca em lojas
│   ├── charts.py               # Gráficos Plotly
│   ├── metrics.py              # Métricas e comparação de algoritmos
│   └── utils.py                # Utilitários e constantes
├── data/
│   ├── sample_pc_parts.csv
│   ├── sample_laptops.csv
│   └── README.md
├── assets/
│   └── screenshots/
└── tests/
    ├── test_knapsack_iterativo.py
    ├── test_knapsack_recursivo.py
    ├── test_grouped_knapsack.py
    ├── test_find_solution.py
    └── test_store_links.py
```

---

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.11 | Linguagem principal |
| Streamlit 1.35 | Interface web interativa |
| Pandas 2.2 | Manipulação de dados |
| Plotly 5.22 | Gráficos interativos |
| NumPy 1.26 | Cálculos numéricos |
| Pytest 8.2 | Testes unitários |
| Docker | Containerização |

---

## Testes

Execute todos os testes com:

```bash
pytest tests/ -v
```

Cobertura dos testes:

| Módulo | Testes |
|---|---|
| `knapsack_iterativo.py` | Casos base, reconstrução, dimensões da tabela, estados calculados |
| `knapsack_recursivo.py` | Equivalência com iterativo, cache hits, memoization |
| `grouped_knapsack.py` | Um item por grupo, respeito ao orçamento, maximização de valor |
| `find_solution.py` | Passo a passo, capacidade personalizada, consistência com DP |
| `store_links.py` | Geração de URLs, encoding de caracteres especiais, lojas válidas |

---

## Limitações

- Os preços no dataset de exemplo são **estimativas** baseadas em valores de mercado; não refletem preços em tempo real.
- A **compatibilidade** é verificada de forma simplificada — não cobre todos os casos reais (ex: compatibilidade de velocidade de RAM, número de slots, etc.).
- O Grouped Knapsack opera com preços em **inteiros** (arredondamento para R$ 1) — diferenças de centavos são desconsideradas.
- Para orçamentos muito altos (acima de R$ 50.000), a tabela DP é automaticamente reduzida em resolução (passo de R$ 10 ou mais) para manter desempenho.
- O sistema **não realiza scraping** de preços reais — os links gerados levam para buscas nos sites das lojas.

---

## Trabalhos futuros

- Integração com APIs de preços em tempo real (ex: KaBuM! API, Mercado Livre API).
- Suporte a restrições adicionais: número de slots de RAM, TDP máximo por slot de PCIe, compatibilidade de altura de cooler com gabinete.
- Modo "upgrade" — o usuário informa as peças que já possui e o sistema otimiza apenas o que falta.
- Exportação da configuração em PDF ou compartilhamento via link.
- Score histórico — comparar configurações salvas ao longo do tempo.
- Suporte a múltiplos idiomas.

---

## Licença

MIT License — sinta-se à vontade para usar, modificar e distribuir.
