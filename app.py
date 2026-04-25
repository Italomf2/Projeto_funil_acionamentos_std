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

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("""
    <div style="text-align:center; margin-top:15%;">
        <h1 style="color:#EC0000;">📞 Funil de Acionamentos</h1>
        <h3 style="color:#e0e0e0;">Santander</h3>
        <p style="color:#888;">Sistema seguro – requer autenticação</p>
    </div>""", unsafe_allow_html=True)
    with st.form("login"):
        senha = st.text_input("🔒 Digite a senha de acesso:", type="password")
        if st.form_submit_button("Acessar Dashboard", use_container_width=True):
            if senha == "VIANA@2026":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
    st.stop()

st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #161925; }
    .titulo-principal {
        font-size: 45px; font-weight: 800; color: #EC0000;
        letter-spacing: 1px; border-bottom: 2px solid #EC0000;
        padding-bottom: 8px; margin-bottom: 20px;
    }
    .section-title {
        font-size:28px; font-weight: 700; color: #EC0000;
        margin: 18px 0 10px 0; border-left: 4px solid #EC0000;
        padding-left: 20px;
    }
    .badge-comparar {
        background: #2a1f1f; border: 1px solid #EC0000; border-radius: 6px;
        padding: 6px 14px; font-size: 13px; color: #ffaaaa;
        margin-bottom: 16px; display: inline-block;
    }
    .kpi-card {
        flex: 1 1 auto; width: 100%; min-width: 100px;
        background: #1c1f2e; border-left: 4px solid #EC0000;
        border-radius: 10px; padding: 10px 20px; margin-bottom: 10px;
        height: auto; min-height: 85px; display: flex;
        flex-direction: column; justify-content: center; text-align: center;
    }
    .kpi-label { font-size: 11px; color: #888; text-transform: uppercase;
                 letter-spacing: 1px; font-weight: 700; }
    .kpi-value { font-size: 25px; font-weight: 800; color: #fff; line-height: 1.2; }
    .kpi-sub   { font-size: 11px; color: #aaa; margin-top: 3px; font-weight: 600; }
    .kpi-delta {
        background: #12141f; border: 1px solid #2a2d3e;
        border-radius: 10px; padding: 10px 8px; margin-bottom: 10px;
        min-height: 80px; text-align: center;
    }
    .delta-label { font-size: 9px; color: #666; text-transform: uppercase;
                   letter-spacing: 1px; margin-bottom: 3px; font-weight: 800; }
    .delta-up    { font-size: 17px; font-weight: 800; color: #22c55e; }
    .delta-down  { font-size: 17px; font-weight: 900; color: #ef4444; }
    .delta-flat  { font-size: 17px; font-weight: 800; color: #888; }
    .delta-sub   { font-size: 10px; color: #666; margin-top: 2px; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1c1f2e; border-radius: 8px; }
    .stTabs [data-baseweb="tab"]      { color: #aaa; }
    .stTabs [aria-selected="true"]    { color: #EC0000 !important;
                                        border-bottom: 2px solid #EC0000; }
</style>
""", unsafe_allow_html=True)

def fmt_qtd(v):
    try:
        return f"{int(float(v)):,}".replace(",", ".")
    except:
        return str(v)

def fmt_pct(v):
    try:
        return f"{float(v):.2f}".replace(".", ",") + "%"
    except:
        return str(v)

def fmt_val(v):
    try:
        n = float(v)
        s = f"{n:,.2f}"
        inteiro, dec = s.split(".")
        inteiro = inteiro.replace(",", ".")
        return f"R$ {inteiro},{dec}"
    except:
        return str(v)

CHAVES_PCT = {"pAcion", "pAlo", "pCpc", "pCpcN", "pProp", "pAprov", "pPagos",
              "pCartAcion", "pCartAlo", "pCartCpc", "pCartProp", "pCartAprov", "pCartCash"}

def fmt_kpi(chave, val):
    if chave == "cash":
        return fmt_val(val)
    elif chave in CHAVES_PCT:
        return fmt_pct(val)
    else:
        return fmt_qtd(val)

URL_ARQUIVO = "https://docs.google.com/spreadsheets/d/1P5KCkDHbheZsaNvcJgewOGjXfrasuuib/export?format=xlsx"
NOME_SHEET  = "BD"

@st.cache_data(show_spinner="⏳ Carregando dados...", ttl=600)
def carregar_dados(url: str) -> pd.DataFrame:
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name=NOME_SHEET, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df_raw = carregar_dados(URL_ARQUIVO)
except Exception as e:
    st.error(f"Erro ao carregar o arquivo. Verifique se o link está público.\n\nDetalhe: {e}")
    st.stop()

df = df_raw.copy()

if "MÊS" in df.columns:
    def formatar_mes(val):
        try:
            dt = pd.to_datetime(val)
            meses_pt = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",
                        7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}
            return f"{meses_pt[dt.month]}/{str(dt.year)[2:]}"
        except:
            return str(val).strip()
    df["MÊS"] = df["MÊS"].apply(formatar_mes)

if "DIA UTIL" in df.columns:
    df["DIA UTIL"] = pd.to_numeric(df["DIA UTIL"], errors="coerce").fillna(0).astype(int)

COLUNAS_NUM = [
    "CLIENTE","CARTEIRA/BASE",
    "QTD DISCAGENS","QTD CLIENTES DISCADOS","$ DISCAGENS",
    "QTD ALÔ","QTD CLIENTES ALO","$ ALÔ",
    "QTD CPC","$ CPC","QTD CPC NOVO","$ CPC NOVO",
    "QTD PROPOSTAS","$ PROPOSTA MOVIMENTADAS",
    "QTD APROVAÇÃO","$ APROVAÇÃO",
    "PAGOS","CASH NOVO","CONTÁBIL",
]

def parse_numero_br(valor):
    s = str(valor).strip().replace("R$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return pd.to_numeric(s, errors="coerce")

for col in COLUNAS_NUM:
    if col in df.columns:
        df[col] = df[col].apply(parse_numero_br).fillna(0)

st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/b/b8/Banco_Santander_Logotipo.svg",
    width=160,
)
st.sidebar.markdown("---")
st.sidebar.markdown("## Filtros")

macros_disp = sorted(df["MACRO"].dropna().unique()) if "MACRO" in df.columns else []
macro_filtro = st.sidebar.multiselect("🗺️ Macro Região", macros_disp, default=macros_disp)
if not macro_filtro:
    macro_filtro = macros_disp

segs_disp = sorted(df["SEGMENTO"].dropna().unique()) if "SEGMENTO" in df.columns else []
seg_filtro = st.sidebar.multiselect("👥 Segmento", segs_disp, default=segs_disp)
if not seg_filtro:
    seg_filtro = segs_disp

st.sidebar.markdown("---")
visao_funil = st.sidebar.radio("📊 Visão do Funil", ["# Quantidade", "R$ Contábil"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Dia Útil")

dus_disp = sorted(df["DIA UTIL"].dropna().unique().tolist()) if "DIA UTIL" in df.columns else []
modo_dia = st.sidebar.radio(
    "Modo de visualização",
    ["📅 Selecionar Dia Útil", "⚖️ Comparar dois dias"],
)

dia_selecionado = max(dus_disp) if dus_disp else None
dia_a = dia_b = None
modo_comp = False

if modo_dia == "📅 Selecionar Dia Útil":
    dia_selecionado = st.sidebar.selectbox("Dia Útil", dus_disp, index=len(dus_disp)-1)
elif modo_dia == "⚖️ Comparar dois dias":
    modo_comp = True
    dia_selecionado = None
    slider_vals = st.sidebar.select_slider(
        "Selecione os dois dias (A → B)",
        options=dus_disp,
        value=(dus_disp[max(0, len(dus_disp)-2)], dus_disp[-1]),
    )
    dia_a, dia_b = slider_vals[0], slider_vals[1]

meses_disp = sorted(df["MÊS"].dropna().unique().tolist()) if "MÊS" in df.columns else []

if len(meses_disp) > 0:
    st.sidebar.markdown("### 📆 Mês")
    if modo_dia == "⚖️ Comparar dois dias":
        col_ma, col_mb = st.sidebar.columns(2)
        mes_a = col_ma.selectbox("Mês A", meses_disp, index=0, key="mes_a")
        mes_b = col_mb.selectbox("Mês B", meses_disp, index=len(meses_disp)-1, key="mes_b")
        mes_filtro = meses_disp
    else:
        mes_filtro = st.sidebar.multiselect(
            "Selecione o(s) mês(es)", options=meses_disp, default=meses_disp)
        if not mes_filtro:
            mes_filtro = meses_disp
        mes_a = mes_b = None
else:
    mes_filtro = []
    mes_a = mes_b = None

st.sidebar.markdown("---")
st.sidebar.caption("Os dados são atualizados diariamente pelo fluxo de consolidação.")

def filtrar(dataframe, dia=None):
    d = dataframe.copy()
    if "MÊS"     in d.columns: d = d[d["MÊS"].isin(mes_filtro)]
    if "MACRO"    in d.columns: d = d[d["MACRO"].isin(macro_filtro)]
    if "SEGMENTO" in d.columns: d = d[d["SEGMENTO"].isin(seg_filtro)]
    if dia is not None and "DIA UTIL" in d.columns:
        d = d[d["DIA UTIL"] == dia]
    return d

def calcular_kpis(dataframe):
    def s(col):  return dataframe[col].sum() if col in dataframe.columns else 0
    def si(col): return int(s(col))
    def p(n, d): return (n / d * 100) if d > 0 else 0

    cli=si("CLIENTE"); disc=si("QTD DISCAGENS"); cDisc=si("QTD CLIENTES DISCADOS")
    alo=si("QTD ALÔ"); cAlo=si("QTD CLIENTES ALO"); cpc=si("QTD CPC")
    cpcN=si("QTD CPC NOVO"); prop=si("QTD PROPOSTAS")
    aprov=si("QTD APROVAÇÃO"); pagos=si("PAGOS")
    cart=s("CARTEIRA/BASE"); vDisc=s("$ DISCAGENS"); vAlo=s("$ ALÔ")
    vCpc=s("$ CPC"); vCpcN=s("$ CPC NOVO"); vProp=s("$ PROPOSTA MOVIMENTADAS")
    vAprov=s("$ APROVAÇÃO"); cash=s("CASH NOVO"); cont=s("CONTÁBIL")

    return dict(
        cli=cli, disc=disc, cDisc=cDisc, alo=alo, cAlo=cAlo,
        cpc=cpc, cpcN=cpcN, prop=prop, aprov=aprov, pagos=pagos,
        cart=cart, vDisc=vDisc, vAlo=vAlo, vCpc=vCpc, vCpcN=vCpcN,
        vProp=vProp, vAprov=vAprov, cash=cash, cont=cont,
        pAcion=p(cDisc,cli), pAlo=p(cAlo,cli), pCpc=p(cpc,cli),
        pCpcN=p(cpcN,cli),   pProp=p(prop,cli), pAprov=p(aprov,cli),
        pPagos=p(pagos,cli),
        pCartAcion=p(vDisc,cart), pCartAlo=p(vAlo,cart),
        pCartCpc=p(vCpc,cart),    pCartProp=p(vProp,cart),
        pCartAprov=p(vAprov,cart),pCartCash=p(cash,cart),
    )

def kpi_card(col, label, valor_formatado, sub=""):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{valor_formatado}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

def delta_card(col, label, val_a, val_b, fmt_tipo="int", bom_subir=True):
    diff  = val_b - val_a
    pct_d = (diff / val_a * 100) if val_a != 0 else 0

    if fmt_tipo == "int":
        sinal = "+" if diff >= 0 else "-"
        diff_str = sinal + fmt_qtd(abs(diff))
    elif fmt_tipo == "pct":
        diff_str = ("+" if diff >= 0 else "") + f"{diff:.2f}".replace(".", ",") + "pp"
    elif fmt_tipo == "moeda":
        sinal = "+" if diff >= 0 else "-"
        diff_str = sinal + " " + fmt_val(abs(diff))
    else:
        diff_str = ("+" if diff >= 0 else "-") + fmt_qtd(abs(diff))

    pct_str = "(" + ("+" if pct_d >= 0 else "") + f"{pct_d:.1f}".replace(".", ",") + "%)"

    melhora = (diff > 0 and bom_subir) or (diff < 0 and not bom_subir)
    if   diff == 0: css, seta = "delta-flat", "="
    elif melhora:   css, seta = "delta-up",   "▲"
    else:           css, seta = "delta-down", "▼"

    col.markdown(f"""
    <div class="kpi-delta">
        <div class="delta-label">{label}</div>
        <div class="{css}">{seta} {diff_str}</div>
        <div class="delta-sub">{pct_str}</div>
    </div>""", unsafe_allow_html=True)

if modo_comp:
    if mes_a and mes_b and len(meses_disp) > 0:
        df_dA = filtrar(df[df["MÊS"] == mes_a], dia_a)
        df_dB = filtrar(df[df["MÊS"] == mes_b], dia_b)
    else:
        df_dA = filtrar(df, dia_a)
        df_dB = filtrar(df, dia_b)
    df_f = filtrar(df, dia_b)
elif dia_selecionado is not None:
    df_f = filtrar(df, dia_selecionado)
else:
    df_f = filtrar(df, max(dus_disp))

df_todos = filtrar(df)
kp = calcular_kpis(df_f)

if   modo_comp:       subtit = f"Comparando DU {dia_a}  ×  DU {dia_b}"
elif dia_selecionado: subtit = f"Dia Útil {dia_selecionado}"
else:                 subtit = "Acumulado – Todos os Dias Úteis"

st.markdown(f"""
<div class="titulo-principal">
    FUNIL DE ACIONAMENTOS – SANTANDER
    <br>{subtit}
</div>""", unsafe_allow_html=True)


if modo_comp:
    kA = calcular_kpis(df_dA)
    kB = calcular_kpis(df_dB)

    st.markdown(
        f'<div class="badge-comparar">⚖️ Comparando DU {dia_a} → DU {dia_b} &nbsp;|&nbsp; '
        f'▲ Verde = melhora &nbsp;|&nbsp; ▼ Vermelho = piora</div>',
        unsafe_allow_html=True,
    )

    col_a, col_mid, col_b = st.columns([5, 3, 5])

    INDICADORES = [
        ("CLIENTES",   "cli",    "int",   True),
        ("DISCAGENS",  "disc",   "int",   True),
        ("ALÔ",        "alo",    "int",   True),
        ("CPC",        "cpc",    "int",   True),
        ("PROPOSTAS",  "prop",   "int",   True),
        ("APROVADAS",  "aprov",  "int",   True),
        ("PAGOS",      "pagos",  "int",   True),
        ("CASH NOVO",  "cash",   "moeda", True),
        ("% ACIONADO", "pAcion", "pct",   True),
        ("% ALÔ",      "pAlo",   "pct",   True),
        ("% CPC",      "pCpc",   "pct",   True),
        ("% PROPOSTA", "pProp",  "pct",   True),
    ]

    with col_a:
        st.markdown(f'<div class="section-title">Dia Útil {dia_a}</div>', unsafe_allow_html=True)
        for label, chave, _, _ in INDICADORES:
            sub = "sobre base" if chave.startswith("p") else ""
            kpi_card(col_a, label, fmt_kpi(chave, kA[chave]), sub)

    with col_mid:
        st.markdown(
            '<div class="section-title" style="text-align:center; padding-left:0;">COMPARATIVO</div>',
            unsafe_allow_html=True)
        for label, chave, fmt_tipo, bom in INDICADORES:
            delta_card(col_mid, label, kA[chave], kB[chave], fmt_tipo, bom)

    with col_b:
        st.markdown(f'<div class="section-title">Dia Útil {dia_b}</div>', unsafe_allow_html=True)
        for label, chave, _, _ in INDICADORES:
            sub = "sobre base" if chave.startswith("p") else ""
            kpi_card(col_b, label, fmt_kpi(chave, kB[chave]), sub)

    st.markdown("---")

    st.markdown('<div class="section-title">📊 Comparativo por Etapa</div>', unsafe_allow_html=True)
    if visao_funil == "# Quantidade":
        etapas = ["Discagens","Alô","CPC","CPC Novo","Propostas","Aprovadas","Pagos"]
        vA = [kA[k] for k in ["disc","alo","cpc","cpcN","prop","aprov","pagos"]]
        vB = [kB[k] for k in ["disc","alo","cpc","cpcN","prop","aprov","pagos"]]
        fmt_bar = fmt_qtd
    else:
        etapas = ["$ Disc.","$ Alô","$ CPC","$ CPC Novo","$ Proposta","$ Aprovado","Cash Novo"]
        vA = [kA[k] for k in ["vDisc","vAlo","vCpc","vCpcN","vProp","vAprov","cash"]]
        vB = [kB[k] for k in ["vDisc","vAlo","vCpc","vCpcN","vProp","vAprov","cash"]]
        fmt_bar = fmt_val

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name=f"DU {dia_a}", x=etapas, y=vA,
                              marker_color="#EC0000",
                              text=[fmt_bar(v) for v in vA], textposition="outside"))
    fig_comp.add_trace(go.Bar(name=f"DU {dia_b}", x=etapas, y=vB,
                              marker_color="#ff9999",
                              text=[fmt_bar(v) for v in vB], textposition="outside"))
    fig_comp.update_layout(
        barmode="group", paper_bgcolor="#1c1f2e", plot_bgcolor="#1c1f2e",
        font=dict(color="#e0e0e0"), height=380,
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=10, r=10, t=30, b=80),
    )
    if visao_funil == "R$ Contábil":
        fig_comp.update_traces(textangle=-90, textposition="outside", textfont=dict(size=13))
    else:
        fig_comp.update_traces(textfont=dict(size=14))
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown('<div class="section-title">📈 Variação Diária por Dia Útil</div>', unsafe_allow_html=True)

    df_evolucao = filtrar(df).copy()

    if visao_funil == "# Quantidade":
        metricas_delta = {
            "Discagens": "QTD DISCAGENS",
            "Alô":       "QTD ALÔ",
            "CPC":       "QTD CPC",
            "CPC Novo":  "QTD CPC NOVO",
            "Propostas": "QTD PROPOSTAS",
            "Pagos":     "PAGOS",
        }
    else:
        metricas_delta = {
            "$ Proposta": "$ PROPOSTA MOVIMENTADAS",
            "$ Aprovado": "$ APROVAÇÃO",
            "Cash Novo":  "CASH NOVO",
        }

    evol = (
        df_evolucao.groupby("DIA UTIL", as_index=False)[list(metricas_delta.values())]
        .sum().sort_values("DIA UTIL")
    )

    tabs_delta = st.tabs(list(metricas_delta.keys()))

    for tab, (nome, col) in zip(tabs_delta, metricas_delta.items()):
        with tab:
            if col not in evol.columns:
                st.info(f"Coluna {col} não encontrada.")
                continue

            vals = evol[col].tolist()
            dus  = evol["DIA UTIL"].tolist()

            deltas = [None] + [
                (vals[j] - vals[j-1]) / vals[j-1] * 100 if vals[j-1] != 0 else 0
                for j in range(1, len(vals))
            ]

            if visao_funil == "# Quantidade":
                vals_str = [fmt_qtd(v) for v in vals]
            else:
                vals_str = [fmt_val(v) for v in vals]

            fig_d = go.Figure()
            fig_d.add_trace(go.Scatter(
                x=dus, y=vals,
                fill="tozeroy", fillcolor="rgba(236,0,0,0.08)",
                line=dict(color="#EC0000", width=2.5),
                mode="lines", showlegend=False, hoverinfo="skip",
            ))

            for j in range(len(dus)):
                d = deltas[j]
                cor = "#aaa" if d is None else ("#22c55e" if d >= 0 else "#ef4444")
                seta = "" if d is None else ("▲" if d >= 0 else "▼")
                delta_txt = "—" if d is None else (
                    f"{seta} {abs(d):.1f}".replace(".", ",") + "%"
                )

                fig_d.add_trace(go.Scatter(
                    x=[dus[j]], y=[vals[j]],
                    mode="markers+text",
                    marker=dict(size=12, color=cor, line=dict(width=2, color="#1c1f2e")),
                    text=[vals_str[j]],
                    textposition="top center",
                    textfont=dict(size=12, color="#e0e0e0"),
                    showlegend=False,
                    hovertemplate=f"<b>DU {dus[j]}</b><br>{nome}: {vals_str[j]}<br>Δ {delta_txt}<extra></extra>",
                ))

                if d is not None:
                    fig_d.add_annotation(
                        x=dus[j], y=vals[j],
                        text=f"<b>{delta_txt}</b>",
                        showarrow=False, yshift=-22,
                        font=dict(size=12, color=cor),
                    )

            fig_d.update_layout(
                paper_bgcolor="#1c1f2e", plot_bgcolor="#1c1f2e",
                font=dict(color="#e0e0e0"), height=360,
                margin=dict(l=10, r=10, t=30, b=10),
                yaxis=dict(showgrid=True, gridcolor="#2a2d3e", showticklabels=False),
                xaxis=dict(title="Dia Útil", dtick=1, showgrid=False),
                showlegend=False,
            )
            st.plotly_chart(fig_d, use_container_width=True)
    st.stop()

st.markdown('<div class="section-title">Visão Quantidade – Funil de Acionamento</div>', unsafe_allow_html=True)
c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
kpi_card(c1, "CLIENTES",  fmt_qtd(kp['cli']),  "Base total")
kpi_card(c2, "DISCAGENS", fmt_qtd(kp['disc']), fmt_qtd(kp['cDisc']) + " únicos")
kpi_card(c3, "ALÔ",       fmt_qtd(kp['alo']),  fmt_qtd(kp['cAlo']) + " únicos")
kpi_card(c4, "CPC",       fmt_qtd(kp['cpc']),  "Novo: " + fmt_qtd(kp['cpcN']))
kpi_card(c5, "PROPOSTAS", fmt_qtd(kp['prop']))
kpi_card(c6, "APROVADAS", fmt_qtd(kp['aprov']))
kpi_card(c7, "PAGOS",     fmt_qtd(kp['pagos']))

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Taxas de Conversão – Sobre a Base</div>', unsafe_allow_html=True)
t1,t2,t3,t4,t5,t6,t7 = st.columns(7)
kpi_card(t1, "% ACIONADO", fmt_pct(kp['pAcion']), "clientes discados")
kpi_card(t2, "% ALÔ",      fmt_pct(kp['pAlo']),   "clientes c/ alô")
kpi_card(t3, "% CPC",      fmt_pct(kp['pCpc']),   "sobre base")
kpi_card(t4, "% CPC NOVO", fmt_pct(kp['pCpcN']),  "sobre base")
kpi_card(t5, "% PROPOSTA", fmt_pct(kp['pProp']),  "sobre base")
kpi_card(t6, "% APROVADO", fmt_pct(kp['pAprov']), "sobre base")
kpi_card(t7, "% PAGOS",    fmt_pct(kp['pPagos']), "sobre base")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Visão Contábil – Valores</div>', unsafe_allow_html=True)
v1,v2,v3 = st.columns(3)
kpi_card(v1, "CARTEIRA/BASE", fmt_val(kp['cart']))
kpi_card(v2, "$ DISCAGENS",  fmt_val(kp['vDisc']), fmt_pct(kp['pCartAcion']) + " da carteira")
kpi_card(v3, "$ ALÔ",        fmt_val(kp['vAlo']),  fmt_pct(kp['pCartAlo'])   + " da carteira")
v4,v5,v6 = st.columns(3)
kpi_card(v4, "$ PROPOSTA",  fmt_val(kp['vProp']),  fmt_pct(kp['pCartProp'])  + " da carteira")
kpi_card(v5, "$ APROVADO",  fmt_val(kp['vAprov']), fmt_pct(kp['pCartAprov']) + " da carteira")
kpi_card(v6, "CASH NOVO",   fmt_val(kp['cash']),   "Contábil: " + fmt_val(kp['cont']))

st.markdown("---")

g1, g2 = st.columns(2)
with g1:
    st.markdown("##### 🔻 Funil de Conversão")
    if visao_funil == "# Quantidade":
        ey = ["Clientes","Acionado","Alô","CPC","CPC Novo","Proposta","Pagos"]
        ev = [kp['cli'],kp['cDisc'],kp['cAlo'],kp['cpc'],kp['cpcN'],kp['prop'],kp['pagos']]
        fmt_funil = fmt_qtd
    else:
        ey = ["Carteira","$ Disc.","$ Alô","$ CPC","$ CPC Novo","$ Proposta","Cash Novo"]
        ev = [kp['cart'],kp['vDisc'],kp['vAlo'],kp['vCpc'],kp['vCpcN'],kp['vProp'],kp['cash']]
        fmt_funil = fmt_val

    primeiro = ev[0] if ev[0] > 0 else 1
    textos_funil = [
        fmt_funil(v) + "<br><br>" + f"{v/primeiro*100:.2f}".replace(".", ",") + "%"
        for v in ev
    ]
    fig_f = go.Figure(go.Funnel(
        y=ey, x=ev,
        text=textos_funil, textinfo="text", texttemplate="%{text}",
        marker=dict(color=["#EC0000","#d40000","#b00000","#900000","#700000","#500000","#2a0000"]),
        textfont=dict(color="white", size=13),
    ))
    fig_f.update_layout(paper_bgcolor="#1c1f2e", plot_bgcolor="#1c1f2e",
                        font=dict(color="#e0e0e0"), height=420,
                        margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig_f, use_container_width=True)

with g2:
    st.markdown("##### 🗺️ Distribuição por Macro Região")
    if "MACRO" in df_f.columns:
        col_p = "CLIENTE" if visao_funil == "# Quantidade" else "CONTÁBIL"
        pizza = df_f.groupby("MACRO", as_index=False)[col_p].sum()
        fig_p = px.pie(pizza, values=col_p, names="MACRO", hole=0.42,
                       color_discrete_sequence=["#EC0000","#c00000","#ff5555","#800000"])
        fig_p.update_traces(textposition="outside", textinfo="percent+label")
        fig_p.update_layout(paper_bgcolor="#1c1f2e", font=dict(color="#e0e0e0"),
                            margin=dict(l=10,r=10,t=10,b=10), height=420,
                            legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_p, use_container_width=True)

g3, g4 = st.columns(2)
with g3:
    st.markdown("##### 📊 Propostas, Aprovações e Pagos por Segmento")
    if "SEGMENTO" in df_f.columns:
        if visao_funil == "# Quantidade":
            seg_agg = df_f.groupby("SEGMENTO", as_index=False).agg(
                {"QTD PROPOSTAS":"sum","QTD APROVAÇÃO":"sum","PAGOS":"sum"})
            seg_melt = seg_agg.melt("SEGMENTO", var_name="Etapa", value_name="Valor")
            txt_seg = seg_melt["Valor"].apply(fmt_qtd)
        else:
            seg_agg = df_f.groupby("SEGMENTO", as_index=False).agg(
                {"$ PROPOSTA MOVIMENTADAS":"sum","$ APROVAÇÃO":"sum","CASH NOVO":"sum"})
            seg_melt = seg_agg.melt("SEGMENTO", var_name="Etapa", value_name="Valor")
            txt_seg = seg_melt["Valor"].apply(fmt_val)
        fig_b = px.bar(
            seg_melt, x="SEGMENTO", y="Valor", color="Etapa",
            barmode="group", text=txt_seg,
            color_discrete_sequence=["#EC0000","#c00000","#800000"],
        )
        fig_b.update_traces(textposition="outside")
        fig_b.update_layout(paper_bgcolor="#1c1f2e", plot_bgcolor="#1c1f2e",
                            font=dict(color="#e0e0e0"), height=380,
                            legend=dict(orientation="h", y=1.08),
                            margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig_b, use_container_width=True)

with g4:
    st.markdown("##### 📅 Evolução por Dia Útil")
    if "DIA UTIL" in df_todos.columns:
        if visao_funil == "# Quantidade":
            ev_agg = df_todos.groupby("DIA UTIL", as_index=False).agg(
                {"QTD PROPOSTAS":"sum","QTD APROVAÇÃO":"sum","PAGOS":"sum"})
            ey_l = "Quantidade"
        else:
            ev_agg = df_todos.groupby("DIA UTIL", as_index=False).agg(
                {"$ PROPOSTA MOVIMENTADAS":"sum","$ APROVAÇÃO":"sum","CASH NOVO":"sum"})
            ey_l = "Valor (R$)"
        fig_ev = px.line(
            ev_agg.melt("DIA UTIL", var_name="Métrica", value_name=ey_l),
            x="DIA UTIL", y=ey_l, color="Métrica", markers=True,
            color_discrete_sequence=["#EC0000","#ffaa00","#44cc88"],
        )
        fig_ev.update_layout(paper_bgcolor="#1c1f2e", plot_bgcolor="#1c1f2e",
                             font=dict(color="#e0e0e0"), height=380,
                             legend=dict(orientation="h", y=1.08),
                             xaxis=dict(dtick=1),
                             margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig_ev, use_container_width=True)
    else:
        st.info("Selecione 'Acumulado' para ver a evolução diária.")

st.markdown("---")

st.markdown('<div class="section-title">📋 Detalhamento por Macro e Segmento</div>', unsafe_allow_html=True)
tab_q, tab_r = st.tabs(["📊 Quantidade (#)", "💰 Contábil (R$)"])
grp_cols = [c for c in ["MACRO","SEGMENTO"] if c in df_f.columns]

if grp_cols:
    with tab_q:
        cols_q = {k:"sum" for k in ["CLIENTE","QTD DISCAGENS","QTD CLIENTES DISCADOS",
                  "QTD ALÔ","QTD CLIENTES ALO","QTD CPC","QTD CPC NOVO",
                  "QTD PROPOSTAS","QTD APROVAÇÃO","PAGOS"] if k in df_f.columns}
        grp_q = df_f.groupby(grp_cols, as_index=False).agg(cols_q)
        if "QTD CLIENTES DISCADOS" in grp_q.columns and "CLIENTE" in grp_q.columns:
            grp_q["% ACIONADO"] = (grp_q["QTD CLIENTES DISCADOS"] / grp_q["CLIENTE"] * 100)
        if "PAGOS" in grp_q.columns and "CLIENTE" in grp_q.columns:
            grp_q["% PAGOS"] = (grp_q["PAGOS"] / grp_q["CLIENTE"] * 100)
        disp_q = grp_q.copy()
        for c in cols_q:
            if c in disp_q.columns:
                disp_q[c] = disp_q[c].apply(fmt_qtd)
        for c in ["% ACIONADO", "% PAGOS"]:
            if c in disp_q.columns:
                disp_q[c] = grp_q[c].apply(fmt_pct)
        st.dataframe(disp_q, use_container_width=True, hide_index=True)

    with tab_r:
        cols_r = {k:"sum" for k in ["CARTEIRA/BASE","$ DISCAGENS","$ ALÔ","$ CPC",
                  "$ CPC NOVO","$ PROPOSTA MOVIMENTADAS","$ APROVAÇÃO","CASH NOVO","CONTÁBIL"]
                  if k in df_f.columns}
        grp_r = df_f.groupby(grp_cols, as_index=False).agg(cols_r)
        disp_r = grp_r.copy()
        for c in cols_r:
            if c in disp_r.columns:
                disp_r[c] = disp_r[c].apply(fmt_val)
        st.dataframe(disp_r, use_container_width=True, hide_index=True)

st.markdown("---")
with st.expander(f"🔍 Base Completa Filtrada ({fmt_qtd(len(df_f))} linhas)"):
    df_exib = df_f.copy()
    for c in ["CARTEIRA/BASE","$ DISCAGENS","$ ALÔ","$ CPC","$ CPC NOVO",
              "$ PROPOSTA MOVIMENTADAS","$ APROVAÇÃO","CASH NOVO","CONTÁBIL"]:
        if c in df_exib.columns:
            df_exib[c] = df_exib[c].apply(fmt_val)
    for c in ["CLIENTE","QTD DISCAGENS","QTD CLIENTES DISCADOS","QTD ALÔ",
              "QTD CLIENTES ALO","QTD CPC","QTD CPC NOVO","QTD PROPOSTAS",
              "QTD APROVAÇÃO","PAGOS"]:
        if c in df_exib.columns:
            df_exib[c] = df_exib[c].apply(fmt_qtd)
    st.dataframe(df_exib, use_container_width=True, hide_index=True)

st.markdown(f"""
<div style="text-align:center; color:#555; font-size:11px; margin-top:20px; padding:10px 0;">
    Planejamento Viana Peixoto Call Center Santander &nbsp;|&nbsp;
    BASE_CONSOLIDADA_FUNIL_ACIONAMENTOS &nbsp;|&nbsp;
    Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}
</div>""", unsafe_allow_html=True)