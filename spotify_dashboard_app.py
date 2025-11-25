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
        "O dashboard *Spotify Data Storytelling* oferece uma visão interativa sobre padrões de consumo "
        "musical, tendências de popularidade, discrepâncias entre artistas, comportamento dos gêneros e "
        "evolução temporal dos lançamentos. As análises combinam estatística descritiva, storytelling e "
        "componentes IA-driven, permitindo uma leitura rica do catálogo filtrado."
    )


def texto_aba_overview():
    return (
        "A aba *Visão Geral* apresenta uma síntese do catálogo filtrado, com distribuição de popularidade, "
        "relação entre duração e engajamento e indicadores quantitativos centrais."
    )


def texto_aba_generos():
    return (
        "Na aba *Gêneros*, é possível comparar consistência, dispersão e relevância relativa de cada "
        "gênero musical, identificando estilos dominantes e nichos de cauda longa."
    )


def texto_aba_artistas():
    return (
        "A aba *Artistas* destaca consistência, volatilidade e presença na cauda longa, ajudando a "
        "identificar artistas estáveis, voláteis e concentrados em faixas de baixa popularidade."
    )


def texto_aba_tempo():
    return (
        "A aba *Linha do tempo* evidencia a evolução histórica dos lançamentos, permitindo visualizar "
        "a expansão do catálogo ao longo dos anos e a consolidação do streaming."
    )


def texto_aba_insights():
    return (
        "A aba *Insights IA* reúne interpretações automáticas sobre o catálogo filtrado, explorando "
        "tendências gerais, gêneros, artistas, duração, linha do tempo e cauda longa."
    )


def texto_dinamico_generos(generos, pop_media):
    generos_fmt = ", ".join(sorted(generos)) if generos else "nenhum gênero selecionado"
    return (
        f"Com os gêneros selecionados ({generos_fmt}), a popularidade média no filtro é de "
        f"{pop_media:.1f} pontos**. Esses estilos apresentam padrões específicos de engajamento e "
        "consistência dentro do catálogo."
    )


def texto_dinamico_periodo(ano_ini, ano_fim, qtd_faixas):
    return (
        f"O intervalo de lançamento *{ano_ini}–{ano_fim}* concentra *{qtd_faixas:,} faixas* no filtro atual. "
        "Esse recorte é fundamental para entender a evolução histórica do catálogo."
    )


def texto_dinamico_zero(pct_zero):
    return (
        f"No conjunto filtrado, *{pct_zero:.1f}%* das faixas possuem popularidade zero, "
        "o que reforça a presença da cauda longa típica de catálogos em plataformas de streaming."
    )


mensagens_explicativas = [
    "A popularidade tende a se concentrar em faixas mais recentes, com variações importantes por gênero.",
    "Artistas voláteis combinam grandes hits com um volume considerável de faixas de nicho.",
    "A cauda longa representa uma parcela expressiva do catálogo, com muitas faixas de baixa visibilidade.",
    "Gêneros como Pop, Latin e Indie mostram alta consistência de engajamento no conjunto analisado.",
    "Após 2010, observa-se um crescimento significativo no volume de lançamentos, alinhado à expansão do streaming.",
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
    if "data_lancamento" in df.columns:
        df["data_lancamento"] = pd.to_datetime(df["data_lancamento"])
    if "ano_lancamento" in df.columns:
        df["ano_lancamento"] = df["ano_lancamento"].astype(int)
    return df


def get_default_csv_path():
    candidates = [
        Path("data/spotify_semana2_tratado.csv"),
        Path("spotify_semana2_tratado.csv"),
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
    st.sidebar.warning(
        "Arquivo spotify_semana2_tratado.csv não encontrado automaticamente.\n\n"
        "Envie o arquivo tratado para continuar."
    )
    uploaded = st.sidebar.file_uploader(
        "Envie o arquivo spotify_semana2_tratado.csv",
        type=["csv"],
        accept_multiple_files=False,
    )
    if uploaded is None:
        st.stop()
    df = load_data(uploaded)
else:
    st.sidebar.success(f"Usando dataset: {csv_path}")
    df = load_data(csv_path)

# =========================================================
# Filtros básicos (sidebar)
# =========================================================

st.sidebar.subheader("🎛 Filtros")

generos = sorted(df["genero"].dropna().unique())
anos_min, anos_max = int(df["ano_lancamento"].min()), int(df["ano_lancamento"].max())

generos_sel = st.sidebar.multiselect(
    "Gêneros",
    options=generos,
    default=generos,
)

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
    step=1,
)

incluir_zero = st.sidebar.checkbox(
    "Incluir faixas com popularidade 0 nos gráficos principais",
    value=True,
)

# Aplicar filtros
mask = (
    df["genero"].isin(generos_sel)
    & (df["ano_lancamento"] >= ano_range[0])
    & (df["ano_lancamento"] <= ano_range[1])
    & (df["popularidade"] >= popularidade_min)
)

df_filt = df[mask].copy()

if df_filt.empty:
    st.error("Nenhuma faixa encontrada com os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

# =========================================================
# Cabeçalho e contexto geral
# =========================================================

st.title("🎧 Spotify Data Storytelling – Dashboard Final")

st.markdown(texto_introducao())

st.info(
    f"Dataset filtrado contém *{len(df_filt):,} faixas*, "
    f"no intervalo *{ano_range[0]}–{ano_range[1]}*, "
    f"em *{len(generos_sel)} gêneros* selecionados.",
    icon="ℹ",
)

# KPIs principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🎵 Total de faixas (filtro)", f"{len(df_filt):,}")

with col2:
    st.metric("⭐ Popularidade média", f"{df_filt["popularidade"].mean():.1f}")

with col3:
    pct_zero = (df_filt["popularidade"] == 0).mean() * 100
    st.metric("🧊 Faixas com popularidade 0", f"{pct_zero:.1f}%")

with col4:
    st.metric("⏱ Duração média (min)", f"{df_filt["duracao_min"].mean():.2f}")

st.markdown("---")

# =========================================================
# Abas principais
# =========================================================

tab_overview, tab_genres, tab_artists, tab_time, tab_insights = st.tabs(
    ["📌 Visão Geral", "🎼 Gêneros", "🎤 Artistas", "📅 Linha do tempo", "🤖 Insights IA"]
)

# ---------------------------------------------------------
# VISÃO GERAL
# ---------------------------------------------------------
with tab_overview:
    st.subheader("📌 Visão Geral do Catálogo Filtrado")
    st.markdown(texto_aba_overview())

    col_a, col_b = st.columns(2)

    # Histograma de popularidade
    with col_a:
        st.markdown("#### Distribuição da Popularidade")
        df_pop = df_filt.copy() if incluir_zero else df_filt[df_filt["popularidade"] > 0]
        fig_pop = px.histogram(
            df_pop,
            x="popularidade",
            nbins=20,
            labels={"popularidade": "Popularidade"},
        )
        fig_pop.update_layout(
            bargap=0.05,
            xaxis_title="Popularidade",
            yaxis_title="Quantidade de faixas",
        )
        st.plotly_chart(fig_pop, use_container_width=True)

    # Scatter duração x popularidade
    with col_b:
        st.markdown("#### Duração × Popularidade (por gênero)")
        df_scatter = df_filt.copy()
        if not incluir_zero:
            df_scatter = df_scatter[df_scatter["popularidade"] > 0]

        fig_scatter = px.scatter(
            df_scatter,
            x="duracao_min",
            y="popularidade",
            color="genero",
            hover_data=["faixa", "artista"],
            labels={
                "duracao_min": "Duração (minutos)",
                "popularidade": "Popularidade",
                "genero": "Gênero",
            },
        )
        fig_scatter.update_traces(marker=dict(size=6, opacity=0.7))
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("#### Leitura rápida")
    st.markdown(
        texto_dinamico_generos(generos_sel, df_filt["popularidade"].mean())
    )
    st.markdown(
        texto_dinamico_periodo(ano_range[0], ano_range[1], len(df_filt))
    )
    st.markdown(
        texto_dinamico_zero(pct_zero)
    )

# ---------------------------------------------------------
# GÊNEROS
# ---------------------------------------------------------
with tab_genres:
    st.subheader("🎼 Análise por Gênero")
    st.markdown(texto_aba_generos())

    df_gen = df_filt[df_filt["popularidade"] > 0].copy()
    if df_gen.empty:
        st.warning("Não há faixas com popularidade > 0 no filtro atual para análise por gênero.")
    else:
        col_g1, col_g2 = st.columns([2, 1])

        with col_g1:
            st.markdown("#### Boxplot de Popularidade por Gênero")
            fig_box = px.box(
                df_gen,
                x="popularidade",
                y="genero",
                points="suspectedoutliers",
                labels={"popularidade": "Popularidade", "genero": "Gênero"},
            )
            st.plotly_chart(fig_box, use_container_width=True)

        with col_g2:
            st.markdown("#### Estatísticas por Gênero")
            genre_stats = (
                df_gen.groupby("genero")["popularidade"]
                .agg(["count", "mean", "median", "min", "max"])
                .sort_values("mean", ascending=False)
            )
            st.dataframe(genre_stats, use_container_width=True)

        st.markdown(
            "Gêneros com *maior média* e *menor dispersão* tendem a ser mais consistentes "
            "em termos de engajamento. Gêneros com grande amplitude entre mínimo e máximo "
            "podem indicar catálogos mistos, combinando faixas muito populares e faixas de nicho."
        )

# ---------------------------------------------------------
# ARTISTAS
# ---------------------------------------------------------
with tab_artists:
    st.subheader("🎤 Análise por Artistas")
    st.markdown(texto_aba_artistas())

    df_non_zero = df_filt[df_filt["popularidade"] > 0].copy()
    if df_non_zero.empty:
        st.warning("Não há faixas com popularidade > 0 no filtro atual para análise de artistas.")
    else:
        artist_stats = (
            df_non_zero.groupby("artista")["popularidade"]
            .agg(["count", "mean", "min", "max"])
            .reset_index()
        )
        artist_stats["diferenca"] = artist_stats["max"] - artist_stats["min"]

        top_mean = (
            artist_stats[artist_stats["count"] >= 2]
            .sort_values("mean", ascending=False)
            .head(20)
        )

        col_a1, col_a2 = st.columns(2)

        with col_a1:
            st.markdown("#### Top 20 artistas por popularidade média (mín. 2 faixas)")
            if not top_mean.empty:
                fig_top_mean = px.bar(
                    top_mean.sort_values("mean"),
                    x="mean",
                    y="artista",
                    orientation="h",
                    labels={"mean": "Popularidade média", "artista": "Artista"},
                )
                st.plotly_chart(fig_top_mean, use_container_width=True)
            else:
                st.info("Nenhum artista com pelo menos 2 faixas no filtro atual.")

        with col_a2:
            st.markdown("#### Top 20 artistas com maior discrepância de popularidade")
            top_disc = artist_stats.sort_values("diferenca", ascending=False).head(20)
            if not top_disc.empty:
                fig_disc = px.bar(
                    top_disc.sort_values("diferenca"),
                    x="diferenca",
                    y="artista",
                    orientation="h",
                    labels={"diferenca": "Diferença (max - min)", "artista": "Artista"},
                )
                st.plotly_chart(fig_disc, use_container_width=True)
            else:
                st.info("Não há discrepância suficiente para análise de volatilidade de artistas.")

        st.markdown("#### Artistas com mais faixas de popularidade 0")
        zero_df = df_filt[df_filt["popularidade"] == 0]
        if zero_df.empty:
            st.info("Não há faixas com popularidade 0 no filtro atual.")
        else:
            zero_art = (
                zero_df.groupby("artista")
                .size()
                .reset_index(name="faixas_zero")
                .sort_values("faixas_zero", ascending=False)
                .head(20)
            )
            fig_zero = px.bar(
                zero_art.sort_values("faixas_zero"),
                x="faixas_zero",
                y="artista",
                orientation="h",
                labels={"faixas_zero": "Qtd. faixas com popularidade 0", "artista": "Artista"},
            )
            st.plotly_chart(fig_zero, use_container_width=True)

        st.markdown(
            "Artistas com alta média e baixa diferença (max - min) tendem a ser *consistentes*, "
            "enquanto artistas com grande discrepância indicam *volatilidade*, com alguns grandes "
            "hits e várias faixas de menor alcance. Artistas dominantes em faixas zero compõem a "
            "cauda longa do catálogo."
        )

# ---------------------------------------------------------
# LINHA DO TEMPO
# ---------------------------------------------------------
with tab_time:
    st.subheader("📅 Evolução dos Lançamentos ao Longo do Tempo")
    st.markdown(texto_aba_tempo())

    releases_per_year = (
        df_filt.groupby("ano_lancamento")
        .size()
        .reset_index(name="qtd_faixas")
        .sort_values("ano_lancamento")
    )

    fig_year = px.bar(
        releases_per_year,
        x="ano_lancamento",
        y="qtd_faixas",
        labels={
            "ano_lancamento": "Ano de lançamento",
            "qtd_faixas": "Quantidade de faixas",
        },
    )
    fig_year.update_layout(xaxis=dict(dtick=1))
    st.plotly_chart(fig_year, use_container_width=True)

    st.markdown(
        "A evolução dos lançamentos reforça o aumento do volume de produção musical ao longo das últimas décadas, "
        "com intensificação após 2010, em linha com a digitalização da indústria e a expansão do streaming."
    )

# ---------------------------------------------------------
# INSIGHTS IA
# ---------------------------------------------------------
with tab_insights:
    st.subheader("🤖 Insights IA sobre o Catálogo Filtrado")
    st.markdown(texto_aba_insights())

    col_i1, col_i2 = st.columns(2)

    with col_i1:
        st.markdown("### Síntese automática do filtro atual")
        st.markdown(texto_dinamico_generos(generos_sel, df_filt["popularidade"].mean()))
        st.markdown(texto_dinamico_periodo(ano_range[0], ano_range[1], len(df_filt)))
        st.markdown(texto_dinamico_zero(pct_zero))

    with col_i2:
        st.markdown("### Mensagem explicativa sugerida")
        st.info(gerar_mensagem_explicativa())

    st.markdown("---")
    st.markdown("### Interpretação IA-driven sugerida")
    st.markdown(
        "O conjunto filtrado indica uma dinâmica específica entre *consistência, **volatilidade* e "
        "*relevância histórica*. A combinação de gêneros selecionados, período de lançamento e distribuição "
        "de popularidade sugere padrões que podem orientar estratégias de curadoria, construção de playlists, "
        "promoção de catálogo e entendimento das tendências de consumo na plataforma."
    )

# ---------------------------------------------------------
# Rodapé
# ---------------------------------------------------------

st.markdown("---")
st.caption(
    "Dashboard final – Spotify Data Storytelling · Desenvolvido em Streamlit · Semana 4.2."
)
