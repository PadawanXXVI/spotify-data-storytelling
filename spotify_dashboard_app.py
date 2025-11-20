## 📊 Semana 3.3 — Protótipo inicial de dashboard (Streamlit)

Nesta etapa foi desenvolvido o **protótipo inicial do dashboard interativo** do projeto *Spotify Data Storytelling*, 
utilizando a biblioteca **Streamlit** como ferramenta de prototipação rápida.

O arquivo principal do app é:

- `spotify_dashboard_app.py`

Funcionalidades do protótipo:

- Carregamento do dataset `spotify_semana2_tratado.csv`;
- Filtros interativos por **gênero**, **ano de lançamento** e **popularidade mínima**;
- KPIs gerais (total de faixas filtradas, popularidade média, % de faixas com popularidade zero, duração média);
- Aba **Visão Geral** com:
  - histograma de popularidade,
  - dispersão duração × popularidade por gênero;
- Aba **Gêneros** com:
  - boxplot de popularidade por gênero,
  - tabela-resumo com estatísticas descritivas;
- Aba **Artistas** com:
  - top 20 artistas por popularidade média,
  - top 20 por discrepância (max–min),
  - artistas com mais faixas de popularidade zero;
- Aba **Linha do tempo** com:
  - gráfico de barras de lançamentos por ano.

O protótipo será refinado na Semana 4 para se tornar o dashboard final, mantendo esta estrutura como base de storytelling visual.
