import streamlit as st          
import pandas as pd              
import plotly.graph_objects as go 
import plotly.express as px      
from datetime import datetime    
import requests                 
import io                  

st.set_page_config(
    page_title="Funil de Acionamentos – Santander",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #e0e0e0; }

    .titulo-principal {
        font-size: 24px;
        font-weight: 800;
        color: #EC0000;
        letter-spacing: 1px;
        border-bottom: 2px solid #EC0000;
        padding-bottom: 8px;
        margin-bottom: 20px;
    }

    .kpi-card {
        flex: 1 1 auto;
        width: 100%;
        min-width: 120px;
        background: #1c1f2e;
        border-left: 4px solid #EC0000;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 10px;
        height: auto;
        min-height: 85px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-size: 18px; font-weight: 800; color: #ffffff; line-height: 1.2; white-space: normal; word-break: break-word; }
    .kpi-sub   { font-size: 10px; color: #aaa; margin-top: 4px; word-break: break-word; }

    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #EC0000;
        margin-top: 20px;
        margin-bottom: 10px;
        border-left: 4px solid #EC0000;
        padding-left: 10px;
    }

    .badge-comparar {
        background: #2a1f1f;
        border: 1px solid #EC0000;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
        color: #ffaaaa;
        margin-bottom: 8px;
        display: inline-block;
    }

    section[data-testid="stSidebar"] { background-color: #161925; }

    .stTabs [data-baseweb="tab-list"] { background-color: #1c1f2e; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { color: #aaa; }
    .stTabs [aria-selected="true"] { color: #EC0000 !important; border-bottom: 2px solid #EC0000; }
    
    div[data-testid="column"] {
        min-width: 130px !important;
    }
</style>
""", unsafe_allow_html=True)


URL_ARQUIVO = "https://docs.google.com/spreadsheets/d/1P5KCkDHbheZsaNvcJgewOGjXfrasuuib/export?format=xlsx"
NOME_SHEET = "BD"

@st.cache_data(show_spinner="⏳ Carregando base de dados...", ttl=600)
def carregar_dados(url: str) -> pd.DataFrame:
    resposta = requests.get(url, timeout=120)
    resposta.raise_for_status() 
    
    df = pd.read_excel(io.BytesIO(resposta.content), sheet_name=NOME_SHEET, dtype=str)
    df.columns = [col.strip() for col in df.columns]
    return df

try:
    df_raw = carregar_dados(URL_ARQUIVO)
except Exception as e:
    st.error(f"""
     **Erro ao carregar o arquivo do Google Drive!**

    Verifique se a URL está acessível e se você tem permissão:
    `{URL_ARQUIVO}`
    
    Detalhes do erro: {e}
    """)
    st.stop() 

df = df_raw.copy()

if "DIA UTIL" in df.columns:
    df["DIA UTIL"] = pd.to_numeric(df["DIA UTIL"], errors="coerce").fillna(0).astype(int)

COLUNAS_NUMERICAS = [
    "CLIENTE", "CARTEIRA/BASE",
    "QTD DISCAGENS", "QTD CLIENTES DISCADOS", "$ DISCAGENS",
    "QTD ALÔ",       "QTD CLIENTES ALO",       "$ ALÔ",
    "QTD CPC",       "$ CPC",
    "QTD CPC NOVO",  "$ CPC NOVO",
    "QTD PROPOSTAS", "$ PROPOSTA MOVIMENTADAS",
    "QTD APROVAÇÃO", "$ APROVAÇÃO",
    "PAGOS", "CASH NOVO", "CONTÁBIL",
]

for col in COLUNAS_NUMERICAS:
    if col in df.columns:
        df[col] = (
            df[col].astype(str)
            .str.replace(r"[R\$\s\.]", "", regex=True)
            .str.replace(",", ".")
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/b/b8/Banco_Santander_Logotipo.svg",
    width=160,
)
st.sidebar.markdown("---")
st.sidebar.markdown("## Filtros")

macros_disponiveis = sorted(df["MACRO"].dropna().unique().tolist()) if "MACRO" in df.columns else []
macro_filtro = st.sidebar.multiselect("Macro Região", options=macros_disponiveis, default=macros_disponiveis)

if not macro_filtro:
    macro_filtro = macros_disponiveis

segmentos_disponiveis = sorted(df["SEGMENTO"].dropna().unique().tolist()) if "SEGMENTO" in df.columns else []
segmento_filtro = st.sidebar.multiselect("Segmento", options=segmentos_disponiveis, default=segmentos_disponiveis)

if not segmento_filtro:
    segmento_filtro = segmentos_disponiveis

st.sidebar.markdown("---")
visao_funil = st.sidebar.radio("📊 Visão do Funil", options=["# Quantidade", "R$ Contábil"], index=0, help="Alterna o funil entre quantidade de registros e valores contábeis (R$)",)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Dia Útil")

dias_uteis_disponiveis = sorted(df["DIA UTIL"].dropna().unique().tolist()) if "DIA UTIL" in df.columns else []

modo_dia = st.sidebar.radio("Modo de visualização", options=["📆 Acumulado (todos os dias)", "🔍 Filtrar por dia", "⚖️ Comparar dois dias"], index=0,)

dia_selecionado   = None
dia_comparar_a    = None
dia_comparar_b    = None
modo_comparativo  = False

if modo_dia == "🔍 Filtrar por dia":
    dia_selecionado = st.sidebar.selectbox("Selecione o Dia Útil", options=dias_uteis_disponiveis)

elif modo_dia == "⚖️ Comparar dois dias":
    modo_comparativo = True
    col_a, col_b = st.sidebar.columns(2)
    dia_comparar_a = col_a.selectbox("Dia A", options=dias_uteis_disponiveis, index=0)
    dia_comparar_b = col_b.selectbox("Dia B", options=dias_uteis_disponiveis, index=min(1, len(dias_uteis_disponiveis)-1))

st.sidebar.markdown("---")
st.sidebar.caption(" Os dados são atualizados diariamente pelo fluxo de consolidação.")

def aplicar_filtros(dataframe: pd.DataFrame, dia: int = None) -> pd.DataFrame:
    df_f = dataframe.copy()
    if "MACRO" in df_f.columns and macro_filtro:
        df_f = df_f[df_f["MACRO"].isin(macro_filtro)]
    if "SEGMENTO" in df_f.columns and segmento_filtro:
        df_f = df_f[df_f["SEGMENTO"].isin(segmento_filtro)]
    if dia is not None and "DIA UTIL" in df_f.columns:
        df_f = df_f[df_f["DIA UTIL"] == dia]
    return df_f

if modo_comparativo:
    df_filtrado = aplicar_filtros(df)
    df_dia_a = aplicar_filtros(df, dia_comparar_a)
    df_dia_b = aplicar_filtros(df, dia_comparar_b)
elif dia_selecionado is not None:
    df_filtrado = aplicar_filtros(df, dia_selecionado)
else:
    df_filtrado = aplicar_filtros(df)

def calcular_kpis(dataframe: pd.DataFrame) -> dict:
    def soma(col):
        return dataframe[col].sum() if col in dataframe.columns else 0
    def soma_int(col):
        return int(soma(col))

    qtd_clientes   = soma_int("CLIENTE")
    qtd_discagens  = soma_int("QTD DISCAGENS")
    qtd_cli_disc   = soma_int("QTD CLIENTES DISCADOS")
    qtd_alo        = soma_int("QTD ALÔ")
    qtd_cli_alo    = soma_int("QTD CLIENTES ALO")
    qtd_cpc        = soma_int("QTD CPC")
    qtd_cpc_novo   = soma_int("QTD CPC NOVO")
    qtd_propostas  = soma_int("QTD PROPOSTAS")
    qtd_aprovacao  = soma_int("QTD APROVAÇÃO")
    qtd_pagos      = soma_int("PAGOS")

    val_carteira   = soma("CARTEIRA/BASE")
    val_discagens  = soma("$ DISCAGENS")
    val_alo        = soma("$ ALÔ")
    val_cpc        = soma("$ CPC")
    val_cpc_novo   = soma("$ CPC NOVO")
    val_propostas  = soma("$ PROPOSTA MOVIMENTADAS")
    val_aprovacao  = soma("$ APROVAÇÃO")
    val_cash_novo  = soma("CASH NOVO")
    val_contabil   = soma("CONTÁBIL")

    def pct(num, den): return (num / den * 100) if den > 0 else 0

    return {
        "qtd_clientes":  qtd_clientes,
        "qtd_discagens": qtd_discagens,
        "qtd_cli_disc":  qtd_cli_disc,
        "qtd_alo":       qtd_alo,
        "qtd_cli_alo":   qtd_cli_alo,
        "qtd_cpc":       qtd_cpc,
        "qtd_cpc_novo":  qtd_cpc_novo,
        "qtd_propostas": qtd_propostas,
        "qtd_aprovacao": qtd_aprovacao,
        "qtd_pagos":     qtd_pagos,
        "val_carteira":  val_carteira,
        "val_discagens": val_discagens,
        "val_alo":       val_alo,
        "val_cpc":       val_cpc,
        "val_cpc_novo":  val_cpc_novo,
        "val_propostas": val_propostas,
        "val_aprovacao": val_aprovacao,
        "val_cash_novo": val_cash_novo,
        "val_contabil":  val_contabil,
        "pct_acionado":  pct(qtd_cli_disc, qtd_clientes),
        "pct_alo_base":  pct(qtd_cli_alo,  qtd_clientes),
        "pct_cpc_base":  pct(qtd_cpc,      qtd_clientes),
        "pct_cpc_novo":  pct(qtd_cpc_novo, qtd_clientes),
        "pct_proposta":  pct(qtd_propostas,qtd_clientes),
        "pct_aprovado":  pct(qtd_aprovacao,qtd_clientes),
        "pct_pagos":     pct(qtd_pagos,    qtd_clientes),
        "pct_alo_disc":  pct(qtd_alo,       qtd_discagens),
        "pct_cpc_alo":   pct(qtd_cpc,       qtd_cli_alo),
        "pct_prop_cpc":  pct(qtd_propostas, qtd_cpc),
        "pct_aprov_prop":pct(qtd_aprovacao, qtd_propostas),
        "pct_pago_aprov":pct(qtd_pagos,     qtd_aprovacao),
        "pct_cont_acion":pct(val_discagens, val_carteira),
        "pct_cont_alo":  pct(val_alo,       val_carteira),
        "pct_cont_cpc":  pct(val_cpc,       val_carteira),
        "pct_cont_cpcn": pct(val_cpc_novo,  val_carteira),
        "pct_cont_prop": pct(val_propostas, val_carteira),
        "pct_cont_aprov":pct(val_aprovacao, val_carteira),
        "pct_cont_pagos":pct(val_cash_novo, val_carteira),
    }

kpis = calcular_kpis(df_filtrado)

def kpi_card(col, label: str, valor: str, sub: str = ""):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{valor.replace("R$", "R$ ")}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

if modo_comparativo:
    subtitulo = f"Comparando Dia Útil {dia_comparar_a} × Dia Útil {dia_comparar_b}"
elif dia_selecionado:
    subtitulo = f"Dia Útil {dia_selecionado}"
else:
    subtitulo = "Acumulado – Todos os Dias Úteis"

st.markdown(f"""
<div class="titulo-principal">
    FUNIL DE ACIONAMENTOS – SANTANDER &nbsp;|&nbsp; {subtitulo}
</div>
""", unsafe_allow_html=True)

if modo_comparativo:
    kpis_a = calcular_kpis(df_dia_a)
    kpis_b = calcular_kpis(df_dia_b)

    st.markdown(f'<div class="badge-comparar">⚖️ Comparando: Dia Útil {dia_comparar_a} vs Dia Útil {dia_comparar_b}</div>', unsafe_allow_html=True)

    col_a, sep, col_b = st.columns([10, 1, 10])

    with col_a:
        st.markdown(f'<div class="section-title">📅 Dia Útil {dia_comparar_a}</div>', unsafe_allow_html=True)
        
        row1 = st.columns(3)
        kpi_card(row1[0], "CLIENTES",   f"{kpis_a['qtd_clientes']:,.0f}")
        kpi_card(row1[1], "DISCAGENS",  f"{kpis_a['qtd_discagens']:,.0f}", f"{kpis_a['qtd_cli_disc']:,.0f} únicos")
        kpi_card(row1[2], "ALÔ",        f"{kpis_a['qtd_alo']:,.0f}",      f"{kpis_a['qtd_cli_alo']:,.0f} únicos")

        row2 = st.columns(2)
        kpi_card(row2[0], "CPC",        f"{kpis_a['qtd_cpc']:,.0f}",      f"Novo: {kpis_a['qtd_cpc_novo']:,.0f}")
        kpi_card(row2[1], "PAGOS",      f"{kpis_a['qtd_pagos']:,.0f}")

        row3 = st.columns(2)
        kpi_card(row3[0], "% ACIONADO",  f"{kpis_a['pct_acionado']:.1f}%", "sobre base")
        kpi_card(row3[1], "% ALÔ",       f"{kpis_a['pct_alo_base']:.1f}%", "sobre base")

        row4 = st.columns(2)
        kpi_card(row4[0], "% PROPOSTA",  f"{kpis_a['pct_proposta']:.2f}%", "sobre base")
        kpi_card(row4[1], "CASH NOVO",   f"R$ {kpis_a['val_cash_novo']:,.0f}")

    with sep:
        st.markdown("<div style='border-left:2px solid #EC0000;height:100%;margin:0 auto;'></div>", unsafe_allow_html=True)

    with col_b:
        st.markdown(f'<div class="section-title">📅 Dia Útil {dia_comparar_b}</div>', unsafe_allow_html=True)
        
        row1 = st.columns(3)
        kpi_card(row1[0], "CLIENTES",   f"{kpis_b['qtd_clientes']:,.0f}")
        kpi_card(row1[1], "DISCAGENS",  f"{kpis_b['qtd_discagens']:,.0f}", f"{kpis_b['qtd_cli_disc']:,.0f} únicos")
        kpi_card(row1[2], "ALÔ",        f"{kpis_b['qtd_alo']:,.0f}",      f"{kpis_b['qtd_cli_alo']:,.0f} únicos")

        row2 = st.columns(2)
        kpi_card(row2[0], "CPC",        f"{kpis_b['qtd_cpc']:,.0f}",      f"Novo: {kpis_b['qtd_cpc_novo']:,.0f}")
        kpi_card(row2[1], "PAGOS",      f"{kpis_b['qtd_pagos']:,.0f}")

        row3 = st.columns(2)
        kpi_card(row3[0], "% ACIONADO",  f"{kpis_b['pct_acionado']:.1f}%", "sobre base")
        kpi_card(row3[1], "% ALÔ",       f"{kpis_b['pct_alo_base']:.1f}%", "sobre base")

        row4 = st.columns(2)
        kpi_card(row4[0], "% PROPOSTA",  f"{kpis_b['pct_proposta']:.2f}%", "sobre base")
        kpi_card(row4[1], "CASH NOVO",   f"R$ {kpis_b['val_cash_novo']:,.0f}")
        
    st.markdown("---")

    st.markdown('<div class="section-title">📊 Comparativo por Etapa</div>', unsafe_allow_html=True)

    etapas = ["Discagens", "Alô", "CPC", "CPC Novo", "Propostas", "Aprovadas", "Pagos"]
    vals_a = [kpis_a["qtd_discagens"], kpis_a["qtd_alo"], kpis_a["qtd_cpc"],
              kpis_a["qtd_cpc_novo"], kpis_a["qtd_propostas"], kpis_a["qtd_aprovacao"], kpis_a["qtd_pagos"]]
    vals_b = [kpis_b["qtd_discagens"], kpis_b["qtd_alo"], kpis_b["qtd_cpc"],
              kpis_b["qtd_cpc_novo"], kpis_b["qtd_propostas"], kpis_b["qtd_aprovacao"], kpis_b["qtd_pagos"]]

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name=f"DU {dia_comparar_a}", x=etapas, y=vals_a,
                              marker_color="#EC0000", text=vals_a, textposition="outside"))
    fig_comp.add_trace(go.Bar(name=f"DU {dia_comparar_b}", x=etapas, y=vals_b,
                              marker_color="#ff9999", text=vals_b, textposition="outside"))
    fig_comp.update_layout(
        barmode="group", paper_bgcolor="#1c1f2e", plot_bgcolor="#1c1f2e",
        font=dict(color="#e0e0e0"), height=380,
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    st.stop()

st.markdown('<div class="section-title">📊 Visão Quantidade – Funil de Acionamento</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
kpi_card(c1, "CLIENTES",    f"{kpis['qtd_clientes']:,.0f}",    "Base total")
kpi_card(c2, "DISCAGENS",   f"{kpis['qtd_discagens']:,.0f}",   f"{kpis['qtd_cli_disc']:,.0f} únicos")
kpi_card(c3, "ALÔ",         f"{kpis['qtd_alo']:,.0f}",         f"{kpis['qtd_cli_alo']:,.0f} únicos")
kpi_card(c4, "CPC",         f"{kpis['qtd_cpc']:,.0f}",         f"Novo: {kpis['qtd_cpc_novo']:,.0f}")
kpi_card(c5, "PROPOSTAS",   f"{kpis['qtd_propostas']:,.0f}",   "")
kpi_card(c6, "APROVADAS",   f"{kpis['qtd_aprovacao']:,.0f}",   "")
kpi_card(c7, "PAGOS",       f"{kpis['qtd_pagos']:,.0f}",       "")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-title">📈 Taxas de Conversão – Sobre a Base</div>', unsafe_allow_html=True)

t1, t2, t3, t4, t5, t6, t7 = st.columns(7)
kpi_card(t1, "% ACIONADO",   f"{kpis['pct_acionado']:.1f}%",   "clientes discados")
kpi_card(t2, "% ALÔ",        f"{kpis['pct_alo_base']:.1f}%",   "clientes com alô")
kpi_card(t3, "% CPC",        f"{kpis['pct_cpc_base']:.2f}%",   "sobre base")
kpi_card(t4, "% CPC NOVO",   f"{kpis['pct_cpc_novo']:.2f}%",   "sobre base")
kpi_card(t5, "% PROPOSTA",   f"{kpis['pct_proposta']:.2f}%",   "sobre base")
kpi_card(t6, "% APROVADO",   f"{kpis['pct_aprovado']:.2f}%",   "sobre base")
kpi_card(t7, "% PAGOS",      f"{kpis['pct_pagos']:.2f}%",      "sobre base")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-title">💰 Visão Contábil – Valores</div>', unsafe_allow_html=True)

v1, v2, v3 = st.columns(3)
kpi_card(v1, "CARTEIRA/BASE",   f"R$ {kpis['val_carteira']:,.2f}",   "")
kpi_card(v2, "$ DISCAGENS",     f"R$ {kpis['val_discagens']:,.2f}",  f"{kpis['pct_cont_acion']:.1f}% da carteira")
kpi_card(v3, "$ ALÔ",           f"R$ {kpis['val_alo']:,.2f}",        f"{kpis['pct_cont_alo']:.1f}% da carteira")

v4, v5, v6 = st.columns(3)
kpi_card(v4, "$ PROPOSTA",      f"R$ {kpis['val_propostas']:,.2f}",  f"{kpis['pct_cont_prop']:.2f}% da carteira")
kpi_card(v5, "$ APROVADO",      f"R$ {kpis['val_aprovacao']:,.2f}",  f"{kpis['pct_cont_aprov']:.2f}% da carteira")
kpi_card(v6, "CASH NOVO",       f"R$ {kpis['val_cash_novo']:,.2f}",  f"Contábil: R$ {kpis['val_contabil']:,.2f}")

st.markdown("---")

g1, g2 = st.columns([5, 5])

with g1:
    st.markdown("##### 🔻 Funil de Conversão")

    if visao_funil == "# Quantidade":
        etapas_funil = ["Clientes", "Acionado", "Alô", "CPC", "CPC Novo", "Proposta", "Pagos"]
        valores_funil = [
            kpis["qtd_clientes"], kpis["qtd_cli_disc"], kpis["qtd_cli_alo"],
            kpis["qtd_cpc"], kpis["qtd_cpc_novo"], kpis["qtd_propostas"], kpis["qtd_pagos"],
        ]
    else:
        etapas_funil = ["Carteira", "$ Discagens", "$ Alô", "$ CPC", "$ CPC Novo", "$ Proposta", "Cash Novo"]
        valores_funil = [
            kpis["val_carteira"], kpis["val_discagens"], kpis["val_alo"],
            kpis["val_cpc"], kpis["val_cpc_novo"], kpis["val_propostas"], kpis["val_cash_novo"],
        ]

    fig_funil = go.Figure(go.Funnel(
        y=etapas_funil,
        x=valores_funil,
        textinfo="value+percent initial",
        marker=dict(color=["#EC0000","#d40000","#b00000","#900000","#700000","#500000","#2a0000"]),
        textfont=dict(color="white"),
        connector=dict(line=dict(color="#333", width=2)),
    ))
    fig_funil.update_layout(
        paper_bgcolor="#1c1f2e", plot_bgcolor="#1c1f2e",
        font=dict(color="#e0e0e0"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=420,
    )
    st.plotly_chart(fig_funil, use_container_width=True)
 
with g2:
    st.markdown("##### 🗺️ Distribuição por Macro Região")
 
    if "MACRO" in df_filtrado.columns:
        col_pizza = "CLIENTE" if visao_funil == "# Quantidade" else "CONTÁBIL"
        pizza = df_filtrado.groupby("MACRO", as_index=False)[col_pizza].sum()
 
        fig_pizza = px.pie(
            pizza,
            values=col_pizza,
            names="MACRO",
            hole=0.42,
            color_discrete_sequence=["#EC0000","#c00000","#ff5555","#800000","#ff9999"],
        )
        fig_pizza.update_traces(textposition="outside", textinfo="percent+label")
        fig_pizza.update_layout(
            paper_bgcolor="#1c1f2e",
            font=dict(color="#e0e0e0"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=420,
            showlegend=True,
            legend=dict(orientation="h", y=-0.1),
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
    else:
        st.info("Coluna MACRO não encontrada na base.")
 
g3, g4 = st.columns([5, 5])
 
with g3:
    st.markdown("##### 📊 Propostas, Aprovações e Pagos por Segmento")
 
    if "SEGMENTO" in df_filtrado.columns:
        bar_seg = df_filtrado.groupby("SEGMENTO", as_index=False).agg({
            "QTD PROPOSTAS": "sum",
            "QTD APROVAÇÃO": "sum",
            "PAGOS":         "sum",
        })
 
        bar_melted = bar_seg.melt(
            id_vars="SEGMENTO",
            value_vars=["QTD PROPOSTAS", "QTD APROVAÇÃO", "PAGOS"],
            var_name="Etapa",
            value_name="Quantidade",
        )
 
        fig_bar = px.bar(
            bar_melted,
            x="SEGMENTO", y="Quantidade", color="Etapa",
            barmode="group",
            text="Quantidade",
            color_discrete_sequence=["#EC0000","#c00000","#800000"],
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            paper_bgcolor="#1c1f2e", plot_bgcolor="#1c1f2e",
            font=dict(color="#e0e0e0"),
            legend=dict(orientation="h", y=1.08),
            margin=dict(l=10, r=10, t=30, b=10),
            height=380,
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Coluna SEGMENTO não encontrada.")
 
with g4:
    st.markdown("##### 📅 Evolução por Dia Útil")
 
    if "DIA UTIL" in df_filtrado.columns and dia_selecionado is None:
        if visao_funil == "# Quantidade":
            evol = df_filtrado.groupby("DIA UTIL", as_index=False).agg({
                "QTD PROPOSTAS": "sum",
                "QTD APROVAÇÃO": "sum",
                "PAGOS":         "sum",
            })
            cols_evol = ["QTD PROPOSTAS", "QTD APROVAÇÃO", "PAGOS"]
            titulo_y = "Quantidade"
        else:
            evol = df_filtrado.groupby("DIA UTIL", as_index=False).agg({
                "$ PROPOSTA MOVIMENTADAS": "sum",
                "$ APROVAÇÃO":            "sum",
                "CASH NOVO":              "sum",
            })
            cols_evol = ["$ PROPOSTA MOVIMENTADAS", "$ APROVAÇÃO", "CASH NOVO"]
            titulo_y = "Valor (R$)"
 
        evol_melted = evol.melt(
            id_vars="DIA UTIL",
            value_vars=cols_evol,
            var_name="Métrica",
            value_name=titulo_y,
        )
 
        fig_evol = px.line(
            evol_melted,
            x="DIA UTIL", y=titulo_y, color="Métrica",
            markers=True,
            color_discrete_sequence=["#EC0000","#ffaa00","#44cc88"],
        )
        fig_evol.update_layout(
            paper_bgcolor="#1c1f2e", plot_bgcolor="#1c1f2e",
            font=dict(color="#e0e0e0"),
            legend=dict(orientation="h", y=1.08),
            xaxis=dict(dtick=1, title="Dia Útil"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=380,
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("Selecione 'Acumulado' no filtro de Dia Útil para ver a evolução diária.")
 
st.markdown("---")
 
st.markdown('<div class="section-title">📋 Detalhamento por Macro e Segmento</div>', unsafe_allow_html=True)
 
tab_qtd, tab_cont = st.tabs(["📊 Visão Quantidade (#)", "💰 Visão Contábil (R$)"])
 
colunas_group = [c for c in ["MACRO", "SEGMENTO"] if c in df_filtrado.columns]
 
if colunas_group:
    with tab_qtd:
        cols_qtd = {k: "sum" for k in [
            "CLIENTE","QTD DISCAGENS","QTD CLIENTES DISCADOS",
            "QTD ALÔ","QTD CLIENTES ALO","QTD CPC","QTD CPC NOVO",
            "QTD PROPOSTAS","QTD APROVAÇÃO","PAGOS",
        ] if k in df_filtrado.columns}
 
        grp_qtd = df_filtrado.groupby(colunas_group, as_index=False).agg(cols_qtd)
 
        if "QTD CLIENTES DISCADOS" in grp_qtd and "CLIENTE" in grp_qtd:
            grp_qtd["% ACIONADO"] = (grp_qtd["QTD CLIENTES DISCADOS"] / grp_qtd["CLIENTE"] * 100).round(2)
        if "QTD CLIENTES ALO" in grp_qtd and "CLIENTE" in grp_qtd:
            grp_qtd["% ALÔ"]      = (grp_qtd["QTD CLIENTES ALO"]      / grp_qtd["CLIENTE"] * 100).round(2)
        if "PAGOS" in grp_qtd and "CLIENTE" in grp_qtd:
            grp_qtd["% PAGOS"]    = (grp_qtd["PAGOS"]                 / grp_qtd["CLIENTE"] * 100).round(4)
 
        st.dataframe(grp_qtd, use_container_width=True, hide_index=True)
 
    with tab_cont:
        cols_val = {k: "sum" for k in [
            "CARTEIRA/BASE","$ DISCAGENS","$ ALÔ","$ CPC","$ CPC NOVO",
            "$ PROPOSTA MOVIMENTADAS","$ APROVAÇÃO","CASH NOVO","CONTÁBIL",
        ] if k in df_filtrado.columns}
 
        grp_val = df_filtrado.groupby(colunas_group, as_index=False).agg(cols_val)
 
        grp_display = grp_val.copy()
        for c in cols_val.keys():
            if c in grp_display.columns:
                grp_display[c] = grp_display[c].apply(lambda x: f"R$ {x:,.2f}")
 
        st.dataframe(grp_display, use_container_width=True, hide_index=True)
 
st.markdown("---")
 
st.markdown('<div class="section-title">🔍 Base Completa Filtrada</div>', unsafe_allow_html=True)
with st.expander(f"Clique para expandir ({len(df_filtrado):,} linhas)"):
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
 
st.markdown(f"""
<div style="text-align:center; color:#555; font-size:11px; margin-top:30px; padding:10px 0;">
    Planejamento Call Center Santander &nbsp;|&nbsp;
    BASE_CONSOLIDADA_FUNIL_ACIONAMENTOS_ABRIL &nbsp;|&nbsp;
    Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>
""", unsafe_allow_html=True)