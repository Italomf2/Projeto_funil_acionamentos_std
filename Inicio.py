import streamlit as st
import base64
from pathlib import Path

st.set_page_config(
    page_title="Viana Peixoto – Painéis de Acionamento",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def logo_base64() -> str:
    logo_path = Path(__file__).parent / "assets" / "LOGO_VIANA_PEIXOTO.png"
    with open(logo_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = logo_base64()
logo_tag  = f'<img src="data:image/png;base64,{logo_b64}" style="height:180px; filter: brightness(1.5);" />'

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=Jost:wght@300;400;500&display=swap');
        .stApp {{ background-color: #1a1a1a; }}
        section[data-testid="stSidebar"] {{ display: none; }}
        #MainMenu, footer, header {{ visibility: hidden; }}
        .login-wrap {{
            display: flex; flex-direction: column; align-items: center;
            justify-content: center; padding-top: 80px; gap: 0;
        }}
        .login-sub {{
            font-family: 'Jost', sans-serif;
            font-size: 30px; font-weight: 300; letter-spacing: 5px;
            color: #C85C1A; text-transform: uppercase; text-align: center;
            margin-top: 16px; margin-bottom: 32px;
        }}
        .login-divider {{
            width: 36px; height: 1px; background: #C85C1A;
            margin: 0 auto 32px auto;
        }}
        .login-label {{
            font-family: 'Jost', sans-serif;
            font-size: 10px; letter-spacing: 3px; color: #666;
            text-transform: uppercase; text-align: center; margin-bottom: 32px;
        }}
        div[data-testid="stTextInput"] input {{
            background: transparent !important;
            border: none !important;
            border-bottom: 1px solid #333 !important;
            border-radius: 0 !important; color: #f0ede8 !important;
            font-family: 'Jost', sans-serif !important;
            font-size: 15px !important; letter-spacing: 2px;
            text-align: center; padding: 10px 0 !important;
            box-shadow: none !important;
        }}
        div[data-testid="stTextInput"] input:focus {{
            border-bottom: 1px solid #C85C1A !important;
        }}
        div[data-testid="stTextInput"] label {{ display: none !important; }}
        div[data-testid="stFormSubmitButton"] button {{
            background: transparent !important;
            border: 1px solid #C85C1A !important;
            color: #C85C1A !important;
            font-family: 'Jost', sans-serif !important;
            font-size: 10px !important; letter-spacing: 4px !important;
            text-transform: uppercase !important;
            padding: 12px 48px !important; border-radius: 0 !important;
            margin-top: 20px !important; transition: all 0.3s ease !important;
            width: 100% !important;
        }}
        div[data-testid="stFormSubmitButton"] button:hover {{
            background: #C85C1A !important; color: #1a1a1a !important;
        }}
    </style>
    <div class="login-wrap">
        {logo_tag}
        <div class="login-sub">PAINÉIS PLAN - FUNIL DE ACIONAMENTOS</div>
        <div class="login-divider"></div>
        <div class="login-label">FAÇA SEU LOGIN</div>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 1.2, 1])[1]
    with col:
        with st.form("login", clear_on_submit=True):
            senha = st.text_input("", type="password", placeholder="••••••••")
            ok = st.form_submit_button("Entrar", use_container_width=True)
            if ok:
                if senha == "VIANA@2026":
                    st.session_state.logado = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
    st.stop()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&family=Jost:wght@300;400;500;600&display=swap');

    .stApp { background-color: #1a1a1a; color: #f0ede8; }
    #MainMenu, footer, header { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none; }

    .vp-header {
        text-align: center;
        padding: 48px 0 36px 0;
        border-bottom: 1px solid #262626;
        margin-bottom: 52px;
    }
    .vp-tagline {
        font-family: 'Jost', sans-serif;
        font-size: 30px; letter-spacing: 5px; color: #C85C1A;
        text-transform: uppercase; margin-top: 14px;
    }
    .vp-section-title {
        font-family: 'Jost', sans-serif;
        font-size: 20px; letter-spacing: 5px; color: #C85C1A;
        text-transform: uppercase; text-align: center; margin-bottom: 36px;
        opacity: 0.7;
    }

    /* Cada coluna vira o card clicável via st.button */
    div[data-testid="stButton"] button {
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        font-size: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: 0 !important;
        min-height: 0 !important;
    }
    div[data-testid="stButton"] button:hover {
        background: #161616 !important;
        border-color: #EC0000 !important;
        border-top: 3px solid #EC0000 !important;
        color: #f0ede8 !important;
    }

    /* hover específico por banco usando nth-child */
    div[data-testid="stColumn"]:nth-child(1) div[data-testid="stButton"] button:hover {
        border-color: #EC0000 !important; border-top: 3px solid #EC0000 !important;
    }
    div[data-testid="stColumn"]:nth-child(2) div[data-testid="stButton"] button:hover {
        border-color: #F9C000 !important; border-top: 3px solid #F9C000 !important;
    }
    div[data-testid="stColumn"]:nth-child(3) div[data-testid="stButton"] button:hover {
        border-color: #CC0000 !important; border-top: 3px solid #CC0000 !important;
    }
    div[data-testid="stColumn"]:nth-child(4) div[data-testid="stButton"] button:hover {
        border-color: #C8A800 !important; border-top: 3px solid #C8A800 !important;
    }

    .rodape {
        text-align: center;
        font-family: 'Jost', sans-serif;
        font-size: 10px; letter-spacing: 3px; color: #C85C1A;
        text-transform: uppercase; margin-top: 80px; padding-bottom: 40px;
        opacity: 0.35;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="vp-header">
    {logo_tag}
    <div class="vp-tagline">Painéis de Acionamento</div>
</div>
<div class="vp-section-title">Selecione o banco</div>
""", unsafe_allow_html=True)

BANCOS = [
    {
        "nome": "Santander",
        "icon": "🔴",
        "desc": "Funil de Acionamentos",
        "tag": "● ATIVO",
        "accent": "#EC0000",
        "page": "pages/Santander.py",
        "ativo": True,
    },
    {
        "nome": "Banco do Brasil",
        "icon": "🔵",
        "desc": "Funil de Acionamentos",
        "tag": "Em breve",
        "accent": "#F9C000",
        "page": None,
        "ativo": False,
    },
    {
        "nome": "Bradesco",
        "icon": "🟠",
        "desc": "Funil de Acionamentos",
        "tag": "Em breve",
        "accent": "#CC0000",
        "page": None,
        "ativo": False,
    },
    {
        "nome": "Cooperforte",
        "icon": "🟡",
        "desc": "Funil de Acionamentos",
        "tag": "Em breve",
        "accent": "#C8A800",
        "page": None,
        "ativo": False,
    },
]


st.markdown("""
<style>
    div[data-testid="stButton"] button {
        position: relative !important;
        margin-top: -220px !important;  
        height: 220px !important;       
        width: 100% !important;
        opacity: 0 !important;          
        cursor: pointer !important;
        z-index: 10 !important;
    }
</style>
""", unsafe_allow_html=True)

cols = st.columns(4, gap="large")
for col, banco in zip(cols, BANCOS):
    with col:
        opacidade = "1" if banco["ativo"] else "0.45"
        cursor = "pointer" if banco["ativo"] else "default"
        st.markdown(f"""
        <div style="background:#111111; border:1px solid #242424; border-radius:2px;
                    padding:36px 28px 32px 28px; text-align:center; opacity:{opacidade};
                    transition:all 0.35s ease; cursor:{cursor};"
             onmouseover="this.style.borderColor='{banco['accent']}'; this.style.background='#161616'; this.style.borderTopWidth='3px';"
             onmouseout="this.style.borderColor='#242424'; this.style.background='#111111'; this.style.borderTopWidth='1px';">
            <div style="font-size:34px; margin-bottom:14px;">{banco['icon']}</div>
            <div style="font-family:'Cormorant Garamond',serif; font-size:22px; font-weight:600;
                        letter-spacing:2px; color:#f0ede8; margin-bottom:6px;">{banco['nome']}</div>
            <div style="font-family:'Jost',sans-serif; font-size:10px; letter-spacing:2px;
                        color:#4a4a4a; text-transform:uppercase;">{banco['desc']}</div>
            <div style="display:inline-block; font-family:'Jost',sans-serif; font-size:9px;
                        letter-spacing:2px; color:{banco['accent']}; border:1px solid {banco['accent']};
                        padding:3px 10px; margin-top:16px; text-transform:uppercase; opacity:0.7;">
                {banco['tag']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if banco["ativo"]:
            if st.button(" ", key=banco["nome"], use_container_width=True):
                st.switch_page(banco["page"])

st.markdown("""
<div class="rodape">
    Viana Peixoto Advogados Associados &nbsp;·&nbsp; Uso interno &nbsp;·&nbsp;
</div>
""", unsafe_allow_html=True)
