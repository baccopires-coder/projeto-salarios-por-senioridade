import json
import urllib.request
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ======================================================================
# CAMINHOS (relativos à pasta onde está o app.py)
# ======================================================================
PASTA_PROJETO = Path(__file__).parent
CAMINHO_CSV = PASTA_PROJETO / "dados" / "final dataset - state of data 2025-2026 - kaggle.csv"
CAMINHO_GEOJSON = PASTA_PROJETO / "dados" / "brasil_estados.geojson"
URL_GEOJSON = (
    "https://raw.githubusercontent.com/codeforamerica/click_that_hood/"
    "master/public/data/brazil-states.geojson"
)

# ======================================================================
# CONFIGURAÇÃO DA PÁGINA
# ======================================================================
st.set_page_config(
    page_title="Quanto vale uma carreira em dados?",
    page_icon="📊",
    layout="wide",
)

# Paleta (azul e roxo predominantes)
AZUL = "#3B82F6"
AZUL_CLARO = "#60A5FA"
ROXO = "#8B5CF6"
ROXO_ESCURO = "#6D28D9"
INDIGO = "#6366F1"
ESCALA = [[0.0, "#2563EB"], [0.5, "#6366F1"], [1.0, "#A855F7"]]
CORES_CAT = [AZUL, ROXO, AZUL_CLARO, INDIGO, "#A78BFA", "#38BDF8", "#C084FC"]

st.markdown(
    f"""
    <style>
    .stApp {{
        background: radial-gradient(circle at 10% 0%, #1B2350 0%, #0B1020 45%);
    }}

    /* ---------- Título ---------- */
    h1.titulo {{
        background: linear-gradient(90deg, {AZUL_CLARO}, {ROXO});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0;
        line-height: 1.15;
    }}
    h1.titulo span.sub {{
        display: block;
        font-size: 1.15rem;
        font-weight: 500;
        margin-top: 6px;
        opacity: .9;
    }}

    /* ---------- Cards de métricas ---------- */
    [data-testid="stMetric"] {{
        background: linear-gradient(135deg, rgba(59,130,246,.18), rgba(139,92,246,.22));
        border: 1px solid rgba(139,92,246,.35);
        border-radius: 16px;
        padding: 16px 20px;
        min-height: 112px;
        box-shadow: 0 6px 24px rgba(99,102,241,.15);
    }}
    [data-testid="stMetricLabel"] {{ color: #B8C1EC; }}
    [data-testid="stMetric"] {{
        overflow: hidden;
        box-sizing: border-box;
        width: 100%;
    }}
    [data-testid="stMetric"] > div {{
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
    }}
    [data-testid="stMetricValue"] {{ font-size: 1.7rem; }}
    /* texto longo (ex.: nome do cargo) quebra em várias linhas dentro do card */
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {{
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        max-width: 100% !important;
        line-height: 1.2 !important;
        word-break: break-word !important;
        overflow-wrap: anywhere !important;
    }}
    /* 4º card (cargo): fonte um pouco menor para caber melhor */
    [data-testid="stColumn"]:nth-child(4) [data-testid="stMetricValue"] {{
        font-size: 1.3rem;
    }}

    /* ---------- Barra lateral ---------- */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #141B34 0%, #1B1540 100%);
        border-right: 1px solid rgba(139,92,246,.25);
    }}
    [data-testid="stSidebar"] label p {{
        color: #C7D2FE;
        font-weight: 600;
        letter-spacing: .3px;
    }}

    /* ---------- Filtros em "pílulas" (azul/roxo translúcido) ---------- */
    [data-testid="stSidebar"] [data-testid="stPills"] button,
    [data-testid="stSidebar"] button[data-testid^="stBaseButton-pills"],
    [data-testid="stSidebar"] button[kind="pills"] {{
        background: linear-gradient(135deg, rgba(59,130,246,.14), rgba(139,92,246,.18)) !important;
        border: 1px solid rgba(139,92,246,.35) !important;
        color: #C7D2FE !important;
        border-radius: 999px !important;
        padding: 4px 14px !important;
        backdrop-filter: blur(4px);
        transition: all .18s ease;
    }}
    [data-testid="stSidebar"] [data-testid="stPills"] button:hover,
    [data-testid="stSidebar"] button[data-testid^="stBaseButton-pills"]:hover,
    [data-testid="stSidebar"] button[kind="pills"]:hover {{
        background: linear-gradient(135deg, rgba(59,130,246,.28), rgba(139,92,246,.32)) !important;
        border-color: {AZUL_CLARO} !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }}
    /* selecionado: mais intenso, ainda translúcido */
    [data-testid="stSidebar"] button[data-testid="stBaseButton-pillsActive"],
    [data-testid="stSidebar"] button[kind="pillsActive"],
    [data-testid="stSidebar"] [data-testid="stPills"] button[aria-checked="true"],
    [data-testid="stSidebar"] [data-testid="stPills"] button[aria-pressed="true"] {{
        background: linear-gradient(135deg, rgba(59,130,246,.50), rgba(139,92,246,.60)) !important;
        border: 1px solid rgba(167,139,250,.85) !important;
        color: #FFFFFF !important;
        font-weight: 600;
        box-shadow: 0 0 14px rgba(139,92,246,.35);
    }}

    span[data-baseweb="tag"] {{ background-color: {ROXO_ESCURO} !important; }}
    hr {{ border-color: rgba(139,92,246,.3); }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ======================================================================
# CARREGAMENTO E TRATAMENTO DOS DADOS
# ======================================================================
# A pesquisa informa o salário em FAIXAS. Para calcular médias, usamos o
# ponto médio de cada faixa (estimativa).
PONTO_MEDIO = {
    "Menos de R$ 1.000/mês": 500,
    "de R$ 1.001/mês a R$ 2.000/mês": 1500,
    "de R$ 2.001/mês a R$ 3.000/mês": 2500,
    "de R$ 3.001/mês a R$ 4.000/mês": 3500,
    "de R$ 4.001/mês a R$ 6.000/mês": 5000,
    "de R$ 6.001/mês a R$ 8.000/mês": 7000,
    "de R$ 8.001/mês a R$ 12.000/mês": 10000,
    "de R$ 12.001/mês a R$ 16.000/mês": 14000,
    "de R$ 16.001/mês a R$ 20.000/mês": 18000,
    "de R$ 20.001/mês a R$ 25.000/mês": 22500,
    "de R$ 25.001/mês a R$ 30.000/mês": 27500,
    "de R$ 25.001/mês a R$ 3000/mês": 27500,  # erro de digitação na base
    "de R$ 30.001/mês a R$ 40.000/mês": 35000,
    "Acima de R$ 40.001/mês": 45000,
}
ORDEM_FAIXAS = [
    "Menos de R$ 1.000/mês", "de R$ 1.001/mês a R$ 2.000/mês",
    "de R$ 2.001/mês a R$ 3.000/mês", "de R$ 3.001/mês a R$ 4.000/mês",
    "de R$ 4.001/mês a R$ 6.000/mês", "de R$ 6.001/mês a R$ 8.000/mês",
    "de R$ 8.001/mês a R$ 12.000/mês", "de R$ 12.001/mês a R$ 16.000/mês",
    "de R$ 16.001/mês a R$ 20.000/mês", "de R$ 20.001/mês a R$ 25.000/mês",
    "de R$ 25.001/mês a R$ 30.000/mês", "de R$ 30.001/mês a R$ 40.000/mês",
    "Acima de R$ 40.001/mês",
]
ORDEM_NIVEL = ["Júnior", "Pleno", "Sênior", "Especialista/Staff+"]

# Porte da empresa (aproximação da classificação do SEBRAE por nº de funcionários,
# ajustada às faixas da pesquisa): micro, pequena, média e grande.
PORTE_POR_FAIXA = {
    "de 1 a 5": "Micro (1–10)",
    "de 6 a 10": "Micro (1–10)",
    "de 11 a 50": "Pequena (11–50)",
    "de 51 a 100": "Média (51–100)",
    "de 101 a 500": "Grande (100+)",
    "de 501 a 1.000": "Grande (100+)",
    "de 1.001 a 3.000": "Grande (100+)",
    "Acima de 3.000": "Grande (100+)",
}
ORDEM_TAMANHO = ["Micro (1–10)", "Pequena (11–50)", "Média (51–100)", "Grande (100+)"]

ORDEM_EXPERIENCIA = [
    "Menos de 1 ano", "de 1 a 2 anos", "de 3 a 4 anos", "de 5 a 6 anos",
    "de 7 a 10 anos", "Mais de 10 anos",
]

COLUNAS = {
    "1.g_vive_no_brasil": "vive_brasil",
    "1.i.1_uf_onde_mora": "uf",
    "1.i.2_regiao_onde_mora": "regiao",
    "2.a_situação_de_trabalho": "contrato",
    "2.c_numero_de_funcionarios": "tamanho_empresa",
    "2.f_cargo_atual": "cargo",
    "2.g_nivel": "senioridade",
    "2.h_faixa_salarial": "faixa_salarial",
    "2.i_tempo_de_experiencia_em_dados": "experiencia",
    "2.q_modelo_de_trabalho_atual": "modelo_trabalho",
}


@st.cache_data
def carregar_dados():
    df = pd.read_csv(CAMINHO_CSV, usecols=list(COLUNAS)).rename(columns=COLUNAS)
    df = df[df["vive_brasil"] == 1].copy()                 # somente Brasil
    df = df.dropna(subset=["faixa_salarial"])              # precisa ter salário
    df["salario"] = df["faixa_salarial"].map(PONTO_MEDIO)
    df["tamanho_empresa"] = (
        df["tamanho_empresa"]
        .replace({"de 501 a 100": "de 501 a 1.000"})       # erro de digitação
        .map(PORTE_POR_FAIXA)                              # micro / pequena / média / grande
    )
    df["modelo_trabalho"] = (
        df["modelo_trabalho"]
        .str.replace("Modelo ", "", regex=False)
        .str.replace(r"\s*\(.*\)", "", regex=True)         # remove parênteses longos
        .str.capitalize()
    )
    return df


@st.cache_data
def carregar_geojson():
    """Usa o arquivo local se existir; senão baixa da internet."""
    if CAMINHO_GEOJSON.exists():
        return json.loads(CAMINHO_GEOJSON.read_text(encoding="utf-8"))
    with urllib.request.urlopen(URL_GEOJSON) as resposta:
        return json.load(resposta)


df = carregar_dados()
geojson_brasil = carregar_geojson()


def moeda(valor):
    """Formata em reais: R$ 10.000"""
    return "R$ " + f"{valor:,.0f}".replace(",", ".")


def milhar(valor):
    """Formata inteiro com ponto de milhar: 1.234"""
    return f"{valor:,}".replace(",", ".")


def estilizar(fig, titulo):
    fig.update_layout(
        title=titulo,
        title_x=0.02,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E8ECFF",
        margin=dict(l=10, r=10, t=60, b=10),
        coloraxis_showscale=False,
    )
    fig.update_xaxes(gridcolor="rgba(139,92,246,.15)")
    fig.update_yaxes(gridcolor="rgba(139,92,246,.15)")
    return fig


# ======================================================================
# BARRA LATERAL (FILTROS)
# ======================================================================
st.sidebar.header("🔍 Filtros")
st.sidebar.caption("Clique para selecionar. Sem nenhuma seleção, todos os valores são considerados.")


def filtro(rotulo, coluna, ordem=None):
    """Filtro em pílulas. Se nada for selecionado, considera todas as opções."""
    if ordem:
        opcoes = [o for o in ordem if o in df[coluna].unique()]
    else:
        opcoes = sorted(df[coluna].dropna().unique())
    selecao = st.sidebar.pills(rotulo, opcoes, selection_mode="multi", key=f"filtro_{coluna}")
    return selecao if selecao else opcoes


regioes_sel = filtro("Região", "regiao")
niveis_sel = filtro("Senioridade", "senioridade", ORDEM_NIVEL)
contratos_sel = filtro("Tipo de contrato", "contrato")
tamanhos_sel = filtro("Porte da empresa", "tamanho_empresa", ORDEM_TAMANHO)

# ======================================================================
# FILTRAGEM
# ======================================================================
df_f = df[
    df["regiao"].isin(regioes_sel)
    & df["senioridade"].isin(niveis_sel)
    & df["contrato"].isin(contratos_sel)
    & df["tamanho_empresa"].isin(tamanhos_sel)
]

# ======================================================================
# CONTEÚDO PRINCIPAL
# ======================================================================
st.markdown(
    '<h1 class="titulo">📊 Quanto vale uma carreira em dados?'
    '<span class="sub">Salários por área, região e senioridade no Brasil '
    "(State of Data 2025-2026)</span></h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "Análise da pesquisa **State of Data 2025/2026** com profissionais que vivem no Brasil. "
    "Use os filtros à esquerda para refinar a análise."
)
st.caption(
    "💡 O salário na pesquisa é informado em faixas mensais; os valores abaixo usam o ponto médio de cada faixa. "
    "O porte da empresa é uma aproximação por número de funcionários: micro (até 10), pequena (11–50), "
    "média (51–100) e grande (acima de 100)."
)

# --- KPIs ---
st.subheader("Métricas gerais (salário mensal em R$)")

total_base = len(df)

if not df_f.empty:
    salario_medio = df_f["salario"].mean()
    analisados = len(df_f)
    cargo_freq = df_f["cargo"].mode()[0] if df_f["cargo"].notna().any() else "—"
    cargo_freq = cargo_freq.replace("/", "/\u200b")  # permite quebra de linha após "/"
else:
    salario_medio = analisados = 0
    cargo_freq = "—"

pct_base = (analisados / total_base * 100) if total_base else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Salário médio", moeda(salario_medio))
c2.metric(
    "Dados analisados",
    milhar(analisados),
    help=f"Respondentes que atendem aos filtros atuais ({pct_base:.1f}% da base).",
)
c3.metric("Total de respondentes", milhar(total_base))
c4.metric("Cargo mais frequente", cargo_freq)

st.markdown("---")

# --- Gráficos ---
st.subheader("Gráficos")

if df_f.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
else:
    g1, g2 = st.columns(2)

    # 1) Top 10 cargos por salário médio (mínimo de 10 respondentes por cargo)
    with g1:
        por_cargo = (
            df_f.dropna(subset=["cargo"])
            .groupby("cargo")["salario"]
            .agg(["mean", "count"])
            .query("count >= 10")
            .nlargest(10, "mean")
            .sort_values("mean")
            .reset_index()
        )
        if por_cargo.empty:
            st.info("Poucos dados por cargo com os filtros atuais (mínimo de 10 respondentes).")
        else:
            fig = px.bar(
                por_cargo, x="mean", y="cargo", orientation="h", color="mean",
                color_continuous_scale=ESCALA,
                labels={"mean": "Salário médio (R$/mês)", "cargo": ""},
                custom_data=["count"],
            )
            fig.update_traces(hovertemplate="%{y}<br>Média: R$ %{x:,.0f}<br>Respondentes: %{customdata[0]}")
            st.plotly_chart(estilizar(fig, "Top 10 cargos por salário médio"), width="stretch")

    # 2) Distribuição por faixa salarial
    with g2:
        faixas = (
            df_f["faixa_salarial"].value_counts()
            .reindex(ORDEM_FAIXAS, fill_value=0).reset_index()
        )
        faixas.columns = ["faixa", "quantidade"]
        faixas["faixa"] = (
            faixas["faixa"].str.replace("/mês", "", regex=False)
            .str.replace("de R$ ", "", regex=False)
            .str.replace(" a R$ ", " – ", regex=False)
        )
        fig = px.bar(
            faixas, x="faixa", y="quantidade", color="quantidade",
            color_continuous_scale=ESCALA,
            labels={"faixa": "Faixa salarial (R$/mês)", "quantidade": "Respondentes"},
        )
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(estilizar(fig, "Distribuição por faixa salarial"), width="stretch")

    g3, g4 = st.columns(2)

    # 3) Modelo de trabalho
    with g3:
        modelo = df_f["modelo_trabalho"].value_counts().reset_index()
        modelo.columns = ["modelo", "quantidade"]
        fig = px.pie(
            modelo, names="modelo", values="quantidade", hole=0.55,
            color_discrete_sequence=CORES_CAT,
        )
        fig.update_traces(textinfo="percent", marker=dict(line=dict(color="#0B1020", width=2)))
        fig = estilizar(fig, "Proporção por modelo de trabalho")
        fig.update_layout(legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, width="stretch")

    # 4) Mapa do Brasil: salário médio por estado
    with g4:
        por_uf = (
            df_f.dropna(subset=["uf"]).groupby("uf")["salario"]
            .agg(["mean", "count"]).query("count >= 10").reset_index()
        )
        if por_uf.empty:
            st.info("Poucos dados por estado com os filtros atuais (mínimo de 10 respondentes).")
        else:
            fig = px.choropleth(
                por_uf, geojson=geojson_brasil, locations="uf",
                featureidkey="properties.sigla", color="mean",
                color_continuous_scale=ESCALA,
                labels={"mean": "Salário médio (R$/mês)", "uf": "Estado", "count": "Respondentes"},
                custom_data=["count"],
            )
            fig.update_traces(
                hovertemplate="<b>%{location}</b><br>Média: R$ %{z:,.0f}<br>Respondentes: %{customdata[0]}<extra></extra>",
                marker_line_color="#0B1020", marker_line_width=0.8,
            )
            # camada base cinza com todos os estados (aparecem os sem dados)
            todas_ufs = [f["properties"]["sigla"] for f in geojson_brasil["features"]]
            base = go.Choropleth(
                geojson=geojson_brasil, locations=todas_ufs, z=[0] * len(todas_ufs),
                featureidkey="properties.sigla", showscale=False, hoverinfo="skip",
                colorscale=[[0, "#232B4D"], [1, "#232B4D"]],
                marker_line_color="#0B1020", marker_line_width=0.8,
            )
            fig.add_trace(base)
            fig.data = (fig.data[-1],) + fig.data[:-1]  # base atrás do mapa colorido
            fig.update_geos(
                fitbounds="geojson", visible=False,
                bgcolor="rgba(0,0,0,0)",
            )
            fig = estilizar(fig, "Salário médio por estado (mín. 10 respondentes)")
            fig.update_layout(
                coloraxis_showscale=True,
                coloraxis_colorbar=dict(title="R$/mês", thickness=12, len=0.7),
                geo=dict(bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig, width="stretch")
            st.caption("Estados em cinza escuro têm menos de 10 respondentes com os filtros atuais.")

    g5, g6 = st.columns(2)

    # 5) Salário médio por senioridade
    with g5:
        por_nivel = (
            df_f.dropna(subset=["senioridade"]).groupby("senioridade")["salario"]
            .mean().reindex(ORDEM_NIVEL).dropna().reset_index()
        )
        fig = px.bar(
            por_nivel, x="senioridade", y="salario", color="salario",
            color_continuous_scale=ESCALA,
            labels={"senioridade": "", "salario": "Salário médio (R$/mês)"},
        )
        st.plotly_chart(estilizar(fig, "Salário médio por senioridade"), width="stretch")

    # 6) Salário médio por tempo de experiência em dados
    with g6:
        por_exp = (
            df_f.groupby("experiencia")["salario"].mean()
            .reindex(ORDEM_EXPERIENCIA).dropna().reset_index()
        )
        fig = px.line(
            por_exp, x="experiencia", y="salario", markers=True,
            labels={"experiencia": "Experiência em dados", "salario": "Salário médio (R$/mês)"},
        )
        fig.update_traces(line=dict(color=ROXO, width=4), marker=dict(size=11, color=AZUL_CLARO))
        st.plotly_chart(estilizar(fig, "Salário médio por tempo de experiência"), width="stretch")

# --- Tabela ---
st.subheader("Dados detalhados")
st.dataframe(
    df_f.drop(columns=["vive_brasil"]).rename(columns={
        "uf": "UF", "regiao": "Região", "contrato": "Contrato",
        "tamanho_empresa": "Porte da empresa", "cargo": "Cargo",
        "senioridade": "Senioridade", "faixa_salarial": "Faixa salarial",
        "experiencia": "Experiência em dados", "modelo_trabalho": "Modelo de trabalho",
        "salario": "Salário estimado (R$)",
    }),
    width="stretch",
)

