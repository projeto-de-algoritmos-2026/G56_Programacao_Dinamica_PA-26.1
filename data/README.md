# Datasets

Este diretório contém os dados usados pelo PC Build Optimizer.

## Arquivos incluídos

- `sample_pc_parts.csv` — 95 peças de PC com preços em BRL, scores de desempenho e atributos de compatibilidade.
- `sample_laptops.csv` — 40 notebooks com especificações, preços em BRL e scores de desempenho.

## Campos — Peças de PC

| Campo | Descrição |
|---|---|
| id | Identificador único |
| name | Nome completo da peça |
| category | CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Cooler |
| brand | Fabricante |
| price_brl | Preço estimado em reais |
| performance_score | Score de 0–100 baseado em benchmarks |
| socket | Soquete (ex: AM4, AM5, LGA1700) — para CPUs e placas-mãe |
| memory_type | Tipo de memória suportada — para placas-mãe |
| wattage | Consumo estimado (W) para CPUs/GPUs, capacidade para PSUs |
| store_search_name | Nome otimizado para busca nas lojas |

## Campos — Notebooks

| Campo | Descrição |
|---|---|
| id | Identificador único |
| name | Nome completo do notebook |
| brand | Fabricante |
| price_brl | Preço estimado em reais |
| cpu | Processador |
| gpu | Placa de vídeo |
| ram_gb | Memória RAM em GB |
| storage_gb | Armazenamento em GB |
| screen_size | Tamanho da tela em polegadas |
| performance_score | Score de 0–100 |
| store_search_name | Nome otimizado para busca nas lojas |

## Datasets públicos de referência (Kaggle)

- [Computer Parts — CPUs and GPUs](https://www.kaggle.com/datasets/iliassekkaf/computerparts)
- [PC Components Dataset](https://www.kaggle.com/datasets/sudhanshuy17/pccomponents)
- [PC Component Prices Comparison](https://www.kaggle.com/datasets/thedevastator/pc-component-prices-comparison)
- [Laptop Price](https://www.kaggle.com/datasets/muhammetvarl/laptop-price)
- [Laptops Price Dataset](https://www.kaggle.com/datasets/juanmerinobermejo/laptops-price-dataset)

## Como usar datasets externos

1. Baixe o CSV do Kaggle.
2. Ajuste os nomes das colunas para corresponder ao formato acima (ou use a funcionalidade de upload da interface).
3. Faça upload via a aba **Dataset** na interface web.
4. O sistema detecta automaticamente o formato e realiza o mapeamento.
