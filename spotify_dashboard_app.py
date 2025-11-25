import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------------------------------------------------
# Configurações gerais da página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Spotify Data Storytelling – Dashboard Final",
    page_icon="🎧",
    layout="wide",
)

# =========================================================
# Funções de textos dinâmicos (IA-driven)
# =========================================================

def texto_introducao():
    return (
        "O dashboard Spotify Data Storytelling oferece uma visão interativa sobre padrões de consumo "
        "musical, tendências de popularidade, discrepâncias entre artistas, comportamento dos gêneros e "
        "evolução temporal dos lançamentos. As análises combinam estatística descritiva, storytelling e "
        "componentes IA-driven."
    )

def texto_aba_overview():
    return (
        "A aba Visão Geral apresenta uma síntese do catálogo filtrado, com distribuição de popularidade, "
        "relação entre duração e engajamento e indicadores quantitativos centrais."
    )

def texto_aba_generos():
    return (
        "Na aba Gêneros, é possível comparar consistência, dispersão e relevância relativa de cada "
        "gênero musical, identificando estilos dominantes e nichos de cauda longa."
    )

def texto_aba_artistas():
    return (
        "A aba Artistas destaca consistência, volatilidade e presença na cauda longa."
    )

def texto_aba_tempo():
    return (
        "A aba Linha do tempo evidencia a evolução histórica dos lançamentos e a consolidação do streaming."
    )

def texto_aba_insights():
    return (
        "A aba Insights IA reúne interpretações automáticas sobre tendências gerais, gêneros, artistas, "
        "duração, linha do tempo e cauda longa."
    )

def texto_dinamico_generos(generos, pop_media):
    generos_fmt = ", ".join(sorted(generos)) if generos else "nenhum gênero selecionado"
    return (
        f"Com os gêneros selecionados ({generos_fmt}), a popularidade média é de "
        f"{pop_media:.1f} pontos."
    )

def texto_dinamico_periodo(ano_ini, ano_fim, qtd_faixas):
    return (
        f"O intervalo {ano_ini}–{ano_fim} contém {qtd_faixas:,} faixas no filtro."
    )

def texto_dinamico_zero(pct_zero):
    return (
        f"No conjunto filtrado, {pct_zero:.1f}% das faixas têm popularidade zero "
        "— reforçando a cauda longa típica do streaming."
    )

mensagens_explicativas = [
    "A popularidade tende a se concentrar em faixas mais recentes.",
    "Artistas voláteis combinam hits com faixas de nicho.",
    "A cauda longa representa grande parte do catálogo.",
    "Pop, Latin e Indie mostram alta consistência de engajamento.",
    "Após 2010 há forte crescimento de lançamentos.",
]

def gerar_mensagem_explicativa():
    import random
    return random.choice(mensagens_explicativas)

# =========================================================
# Carregamento de dados
# =========================================================

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)

    df["data_lancamento"] = pd.to_datetime(df["data_lancamento"], errors="coerce")

    # 🔥 Garantia: SE o CSV não tiver ano_lancamento, cria agora.
    if "ano_lancamento" not in df.columns:
        df["ano_lancamento"] = df["data_lancamento"].dt.year

    df["ano_lancamento"] = df["ano_lancamento"].astype(int)

    return df

def get_default_csv_path():
    candidates = [
        Path("data/spotify_semana3_final.csv"),
        Path("spotify_semana3_final.csv"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None

# ---------------------------------------------------------
# Entrada de dados
# ---------------------------------------------------------

st.sidebar.title("⚙ Configurações do Catálogo")

csv_path = get_default_csv_path()

if csv_path is None:
    st.sidebar.warning("Arquivo não encontrado automaticamente. Envie o CSV tratado.")
    uploaded = st.sidebar.file_uploader("Envie o CSV tratado", type=["csv"])
    if uploaded is None:
        st.stop()
    df = load_data(uploaded)
else:
    st.sidebar.success(f"Usando dataset: {csv_path}")
    df = load_data(csv_path)

# =========================================================
# Filtros
# =========================================================

st.sidebar.subheader("🎛 Filtros")

generos = sorted(df["genero"].dropna().unique())
anos_min, anos_max = int(df["ano_lancamento"].min()), int(df["ano_lancamento"].max())

generos_sel = st.sidebar.multiselect("Gêneros", options=generos, default=generos)

ano_range = st.sidebar.slider(
    "Ano de lançamento",
    min_value=anos_min,
    max_value=anos_max,
    value=(anos_min, anos_max),
    step=1,
)

popularidade_min = st.sidebar.slider(
    "Popularidade mínima",
    min_value=int(df["popularidade"].min()),
    max_value=int(df["popularidade"].max()),
    value=int(df["popularidade"].min()),
)

incluir_zero = st.sidebar.checkbox(
    "Incluir faixas com popularidade 0",
    value=True,
)

mask = (
    df["genero"].isin(generos_sel)
    & df["ano_lancamento"].between(ano_range[0], ano_range[1])
    & (df["popularidade"] >= popularidade_min)
)

df_filt = df[mask].copy()

if df_filt.empty:
    st.error("Nenhuma faixa encontrada com esses filtros.")
    st.stop()

# =========================================================
# Cabeçalho
# =========================================================

st.title("🎧 Spotify Data Storytelling – Dashboard Final")
st.markdown(texto_introducao())

pct_zero = (df_filt["popularidade"] == 0).mean() * 100

st.info(
    f"{len(df_filt):,} faixas** | "
    f"{len(generos_sel)} gêneros** | "
    f"Período *{ano_range[0]}–{ano_range[1]}* | "
    f"{pct_zero:.1f}% com popularidade 0",
    icon="ℹ",
)

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🎵 Total de faixas", f"{len(df_filt):,}")

with col2:
    st.metric("⭐ Popularidade média", f"{df_filt['popularidade'].mean():.1f}")

with col3:
    st.metric("🧊 % Faixas zero", f"{pct_zero:.1f}%")

with col4:
    st.metric("⏱ Duração média (min)", f"{df_filt['duracao_min'].mean():.2f}")

st.markdown("---")

# =========================================================
# Abas
# =========================================================

tab_overview, tab_genres, tab_artists, tab_time, tab_insights = st.tabs(
    ["📌 Visão Geral", "🎼 Gêneros", "🎤 Artistas", "📅 Linha do tempo", "🤖 Insights IA"]
)

# ---------------------------------------------------------
# VISÃO GERAL
# ---------------------------------------------------------
with tab_overview:
    st.subheader("📌 Visão Geral")
    st.markdown(texto_aba_overview())

    col_a, col_b = st.columns(2)

    with col_a:
        fig_pop = px.histogram(df_filt, x="popularidade", nbins=20)
        st.plotly_chart(fig_pop, use_container_width=True)

    with col_b:
        df_scatter = df_filt[df_filt["popularidade"] > 0] if not incluir_zero else df_filt
        fig_scatter = px.scatter(
            df_scatter,
            x="duracao_min",
            y="popularidade",
            color="genero",
            hover_data=["faixa", "artista"],
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------------------------------------
# GÊNEROS
# ---------------------------------------------------------
with tab_genres:
    st.subheader("🎼 Por Gênero")
    st.markdown(texto_aba_generos())

    df_gen = df_filt[df_filt["popularidade"] > 0]
    if not df_gen.empty:
        fig_box = px.box(df_gen, x="popularidade", y="genero")
        st.plotly_chart(fig_box, use_container_width=True)

        genre_stats = (
            df_gen.groupby("genero")["popularidade"]
            .agg(["count", "mean", "median", "min", "max"])
        )
        st.dataframe(genre_stats)

# ---------------------------------------------------------
# ARTISTAS
# ---------------------------------------------------------
with tab_artists:
    st.subheader("🎤 Artistas")
    st.markdown(texto_aba_artistas())

    df_non_zero = df_filt[df_filt["popularidade"] > 0]

    artist_stats = (
        df_non_zero.groupby("artista")["popularidade"]
        .agg(["count", "mean", "min", "max"])
        .reset_index()
    )
    artist_stats["diferenca"] = artist_stats["max"] - artist_stats["min"]

    top_mean = artist_stats[artist_stats["count"] >= 2].sort_values("mean", ascending=False).head(20)

    fig_top = px.bar(top_mean, x="mean", y="artista", orientation="h")
    st.plotly_chart(fig_top, use_container_width=True)

# ---------------------------------------------------------
# LINHA DO TEMPO
# ---------------------------------------------------------
with tab_time:
    st.subheader("📅 Linha do Tempo")
    st.markdown(texto_aba_tempo())

    releases = (
        df_filt.groupby("ano_lancamento")
        .size()
        .reset_index(name="qtd_faixas")
    )

    fig_year = px.bar(releases, x="ano_lancamento", y="qtd_faixas")
    st.plotly_chart(fig_year, use_container_width=True)

# ---------------------------------------------------------
# INSIGHTS IA
# ---------------------------------------------------------
with tab_insights:
    st.subheader("🤖 Insights IA")
    st.markdown(texto_aba_insights())

    col_i1, col_i2 = st.columns(2)

    with col_i1:
        st.markdown("### Síntese automática")
        st.markdown(texto_dinamico_generos(generos_sel, df_filt["popularidade"].mean()))
        st.markdown(texto_dinamico_periodo(ano_range[0], ano_range[1], len(df_filt)))
        st.markdown(texto_dinamico_zero(pct_zero))

    with col_i2:
        st.markdown("### Insight sugerido")
        st.info(gerar_mensagem_explicativa())

# ---------------------------------------------------------
# Rodapé
# ---------------------------------------------------------
st.markdown("---")
st.caption("Dashboard final – Spotify Data Storytelling · Semana 4.2")
