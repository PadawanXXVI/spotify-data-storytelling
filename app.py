import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------------------------------------------------
# Configuração geral da página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Spotify Data Storytelling",
    page_icon="🎧",
    layout="wide",
)

# ---------------------------------------------------------
# Carregamento de dados (com cache REAL)
# ---------------------------------------------------------
@st.cache_data(show_spinner="Carregando dados…")
def load_csv(path):
    df = pd.read_csv(path, encoding="utf-8")
    df["data_lancamento"] = pd.to_datetime(df["data_lancamento"], errors="coerce")
    df["ano_lancamento"] = df["ano_lancamento"].fillna(0).astype(int)
    return df


def localizar_csv():
    candidatos = [
        "data/spotify_semana3_final.csv",
        "spotify_semana3_final.csv",
        "data/spotify_semana2_tratado.csv",
        "spotify_semana2_tratado.csv",
    ]
    for c in candidatos:
        if Path(c).exists():
            return c
    return None


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------
st.sidebar.title("⚙ Configurações")

csv_path = localizar_csv()

if csv_path:
    st.sidebar.success(f"Dataset carregado: {csv_path}")
    df = load_csv(csv_path)
else:
    uploaded = st.sidebar.file_uploader("Envie seu CSV tratado", type=["csv"])
    if uploaded:
        df = load_csv(uploaded)
    else:
        st.warning("Envie um arquivo CSV para iniciar o dashboard.")
        st.stop()

# ---------------------------------------------------------
# Filtros
# ---------------------------------------------------------
generos = sorted(df["genero"].dropna().unique())
anos_min, anos_max = int(df["ano_lancamento"].min()), int(df["ano_lancamento"].max())

generos_sel = st.sidebar.multiselect("Gêneros", generos, default=generos)

ano_range = st.sidebar.slider(
    "Ano de lançamento",
    anos_min, anos_max, (anos_min, anos_max)
)

popularidade_min = st.sidebar.slider(
    "Popularidade mínima",
    int(df["popularidade"].min()),
    int(df["popularidade"].max()),
    int(df["popularidade"].min())
)

incluir_zero = st.sidebar.checkbox(
    "Incluir faixas com popularidade 0", value=True
)

mask = (
    df["genero"].isin(generos_sel)
    & (df["ano_lancamento"] >= ano_range[0])
    & (df["ano_lancamento"] <= ano_range[1])
    & (df["popularidade"] >= popularidade_min)
)

df_filt = df[mask]

if df_filt.empty:
    st.error("Nenhuma faixa encontrada com esses filtros.")
    st.stop()

# ---------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------
st.title("🎧 Spotify Data Storytelling – Dashboard Final")

st.info(
    f"{len(df_filt):,} faixas filtradas · "
    f"{len(generos_sel)} gêneros · "
    f"Período {ano_range[0]}–{ano_range[1]}"
)

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de faixas", f"{len(df_filt):,}")
col2.metric("Popularidade média", f"{df_filt['popularidade'].mean():.1f}")
col3.metric("Faixas zero (%)", f"{(df_filt['popularidade']==0).mean()*100:.1f}%")
col4.metric("Duração média (min)", f"{df_filt['duracao_min'].mean():.2f}")

st.markdown("---")

# ---------------------------------------------------------
# Gráficos
# ---------------------------------------------------------
aba1, aba2, aba3, aba4 = st.tabs([
    "Visão Geral", "Gêneros", "Artistas", "Linha do Tempo"
])

with aba1:
    st.subheader("Distribuição da Popularidade")
    df_pop = df_filt if incluir_zero else df_filt[df_filt["popularidade"] > 0]
    fig = px.histogram(df_pop, x="popularidade", nbins=20)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Duração × Popularidade")
    fig2 = px.scatter(
        df_filt,
        x="duracao_min",
        y="popularidade",
        color="genero",
        hover_data=["faixa", "artista"]
    )
    st.plotly_chart(fig2, use_container_width=True)

with aba2:
    st.subheader("Boxplot por Gênero")
    df_gen = df_filt[df_filt["popularidade"] > 0]
    if not df_gen.empty:
        fig3 = px.box(df_gen, x="popularidade", y="genero")
        st.plotly_chart(fig3, use_container_width=True)

with aba3:
    st.subheader("Top Artistas")
    df_nonzero = df_filt[df_filt["popularidade"] > 0]
    if not df_nonzero.empty:
        top = df_nonzero.groupby("artista")["popularidade"].mean().nlargest(20)
        fig4 = px.bar(top.sort_values(), orientation="h")
        st.plotly_chart(fig4, use_container_width=True)

with aba4:
    st.subheader("Lançamentos por Ano")
    releases = df_filt.groupby("ano_lancamento").size().reset_index(name="qtd")
    fig5 = px.bar(releases, x="ano_lancamento", y="qtd")
    st.plotly_chart(fig5, use_container_width=True)

# ---------------------------------------------------------
# Rodapé
# ---------------------------------------------------------
st.caption("Dashboard desenvolvido para o projeto Spotify Data Storytelling – Senac DF")
