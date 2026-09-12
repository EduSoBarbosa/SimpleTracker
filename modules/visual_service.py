"""
Camada de apresentação: CSS customizado e elementos visuais em HTML/CSS puro.
Tema: CYBER BRUTALISM (High Contrast Fix)
"""

import base64
import os
import streamlit as st

CSS = """
<style>
    /* Importando fontes com pegada industrial/cibernética */
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&family=Teko:wght@500;700&display=swap');

    /* 1. TYPOGRAPHY & GLOBAL TEXT COLORS */
    /* Removemos o seletor agressivo para não quebrar a fonte dos ícones */
    html, body, .stApp {
        background-color: #F4F4F4 !important;
        font-family: 'Space Mono', monospace !important;
    }

    .stApp p, .stApp span, .stApp label, .stApp div[data-testid="stMarkdownContainer"] {
        color: #000000 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Teko', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: #000000 !important;
    }

    /* 2. KILL ALL BORDER RADIUS */
    * {
        border-radius: 0px !important;
    }

    /* 3. BUTTONS */
    .stButton > button {
        background-color: #000000 !important;
        border: 2px solid #000000 !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
        transition: all 0.1s ease-in-out !important;
        box-shadow: 4px 4px 0px #000000 !important;
    }
    
    /* Garante que os sub-elementos do botão fiquem transparentes e brancos */
    .stButton > button * {
        background-color: transparent !important;
        color: #FFFFFF !important;
    }
    
    .stButton > button:hover {
        background-color: #CCFF00 !important; /* Neon Chartreuse */
        box-shadow: 4px 4px 0px #8A2BE2 !important; /* Neon Purple */
        transform: translate(-2px, -2px) !important;
    }
    
    /* No hover, tudo dentro do botão muda para preto */
    .stButton > button:hover * {
        color: #000000 !important; 
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background-color: #8A2BE2 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #CCFF00 !important;
        box-shadow: 4px 4px 0px #000000 !important;
    }

    /* 4. METRIC CARDS */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        padding: 15px !important;
        box-shadow: 5px 5px 0px #000000 !important;
    }
    
    div[data-testid="stMetricLabel"] * {
        text-transform: uppercase !important;
        font-weight: bold !important;
        color: #8A2BE2 !important;
    }

    div[data-testid="stMetricValue"] * {
        color: #000000 !important;
    }

    /* 5. CONTAINERS & EXPANDERS */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border: 2px solid #000000 !important;
        background-color: #FFFFFF !important;
        box-shadow: 5px 5px 0px #000000 !important;
        padding: 1rem !important;
    }

    .stExpander {
        border: 2px solid #000000 !important;
        background-color: #FFFFFF !important;
        box-shadow: 4px 4px 0px #8A2BE2 !important;
    }
    
    /* FIX: Força a proteção da fonte de ícones (Material Icons) nas setinhas do expander */
    .stExpander summary span:not(p span), 
    div[data-testid="stExpanderToggleIcon"] * {
        font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
    }
    
    /* Garante que o texto em si (ex: "Outra quantidade") mantenha a fonte hacker */
    .stExpander summary p {
        font-family: 'Space Mono', monospace !important;
    }

    /* 6. INPUTS */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border: 2px solid #000000 !important;
        background-color: #FFFFFF !important;
        color: #000000 !important; /* Texto digitado visível */
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #8A2BE2 !important;
        box-shadow: none !important;
        background-color: #F4F4F4 !important;
    }

    /* 7. TABS (Corrigido para visibilidade total) */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #000000 !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        border: 2px solid #000000 !important;
        border-bottom: none !important;
        background: #FFFFFF !important;
        margin-right: -2px !important; 
        padding-top: 5px !important;
        padding-bottom: 5px !important;
    }
    /* Força o texto das abas a ser preto */
    .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span {
        color: #000000 !important; 
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #CCFF00 !important;
        border-bottom: 4px solid #CCFF00 !important;
        margin-bottom: -2px !important;
    }
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* 8. PROFILE PICTURE */
    .foto-perfil-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
    }
    .foto-perfil {
        width: 160px;
        height: 160px;
        object-fit: cover;
        border: 3px solid #000000;
        box-shadow: 8px 8px 0px #8A2BE2;
        filter: grayscale(100%) contrast(150%);
    }
    .foto-perfil-placeholder {
        width: 160px;
        height: 160px;
        background: #000000;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 64px;
        font-family: 'Teko', sans-serif;
        color: #CCFF00;
        font-weight: bold;
        border: 3px solid #000000;
        box-shadow: 8px 8px 0px #8A2BE2;
    }
    
    /* 9. STREAK BADGE & MISC */
    .stApp span.streak-badge {
        font-family: 'Space Mono', monospace !important;
        background: #000000 !important;
        color: #CCFF00 !important; 
        padding: 4px 10px !important;
        border: 2px solid #000000 !important;
        text-transform: uppercase !important;
        font-size: 14px !important;
        font-weight: 900 !important;
    }
        
    /* 10. SIDEBAR HACK (Cyber Brutalism Menu) */
        [data-testid="stSidebar"] {
            background-color: #F4F4F4 !important;
            border-right: 3px solid #000000 !important;
        }
        
        /* Força todos os textos normais da sidebar para preto */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
            color: #000000 !important;
        }

        /* Remove arredondamento nativo dos links do menu */
        [data-testid="stSidebarNav"] a {
            border-radius: 0px !important;
            margin-bottom: 5px !important;
        }

        /* Efeito de Hover (Mouse em cima) = Roxo Neon */
        [data-testid="stSidebarNav"] a:hover {
            background-color: #8A2BE2 !important;
        }
        [data-testid="stSidebarNav"] a:hover span {
            color: #FFFFFF !important;
        }

        /* Página Ativa (Selecionada) = Verde Chartreuse com borda brutalista */
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: #CCFF00 !important;
            border: 2px solid #000000 !important;
            box-shadow: 3px 3px 0px #000000 !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] span {
            color: #000000 !important;
            font-weight: 900 !important;
            text-transform: uppercase !important;
        }
        
    /* 11. FILE UPLOADER FIX (Cyber Brutalist Dropzone) */
    [data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF !important;
        border: 2px dashed #000000 !important;
        border-radius: 0px !important;
    }
    
    /* Força ícones e textos internos da zona de upload para preto */
    [data-testid="stFileUploadDropzone"] * {
        color: #000000 !important;
        font-family: 'Space Mono', monospace;
    }
    
    /* Botão "Browse files" interno do uploader */
    [data-testid="stFileUploadDropzone"] button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stFileUploadDropzone"] button:hover {
        background-color: #CCFF00 !important;
        color: #000000 !important;
        box-shadow: 4px 4px 0px #8A2BE2 !important;
    }
    </style>
"""

def injetar_css():
    st.markdown(CSS, unsafe_allow_html=True)

def imagem_para_base64(caminho):
    with open(caminho, "rb") as f:
        return base64.b64encode(f.read()).decode()

def renderizar_foto_perfil(caminho_foto, nome_usuario):
    st.markdown("<p style='font-size: 12px; margin-bottom: 0px; font-weight: bold;'>// NODE: USER_PROFILE</p>", unsafe_allow_html=True)
    
    if os.path.exists(caminho_foto):
        b64 = imagem_para_base64(caminho_foto)
        st.markdown(
            f"""
            <div class="foto-perfil-container">
                <img src="data:image/png;base64,{b64}" class="foto-perfil">
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        inicial = nome_usuario.strip()[0].upper() if nome_usuario.strip() else "?"
        st.markdown(
            f"""
            <div class="foto-perfil-container">
                <div class="foto-perfil-placeholder">{inicial}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("RECONFIG.IMG"):
        upload = st.file_uploader("UPLOAD NEW DATA", type=["png", "jpg", "jpeg"], key="upload_foto")
        if upload is not None:
            os.makedirs(os.path.dirname(caminho_foto), exist_ok=True)
            with open(caminho_foto, "wb") as f:
                f.write(upload.getbuffer())
            st.success("DATA OVERWRITTEN")
            st.rerun()