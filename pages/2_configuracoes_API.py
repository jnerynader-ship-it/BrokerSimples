import streamlit as st

st.set_page_config(page_title="Configurações API | BrokerSimples", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.95)), 
                    url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1920&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(30, 41, 59, 0.95) !important;
    }
    div[data-testid="stMetricValue"], .stTextInput > div > div {
        background-color: rgba(30, 41, 59, 0.85) !important;
        color: #f8fafc !important;
        border-radius: 8px;
        backdrop-filter: blur(4px);
    }
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

# BARRA LATERAL COM LOGO
st.sidebar.image("logo.png", width=90)
st.sidebar.title("💬 Histórico de Prompts")
st.sidebar.markdown("---")

if "historico" in st.session_state and st.session_state.historico:
    st.sidebar.markdown("**Conversas Anteriores:**")
    for i, msg in enumerate(st.session_state.historico):
        if msg["role"] == "user":
            resumo = msg["content"] if isinstance(msg["content"], str) else "[Imagem Enviada]"
            st.sidebar.button(f"📌 {resumo[:22]}...", key=f"hist_cfg_{i}")
else:
    st.sidebar.caption("Nenhum histórico recente.")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Mercado & Ativos")
st.sidebar.markdown("Navegação Rápida:")
aba_lateral = st.sidebar.radio(
    "Ir para:",
    ["Chat Principal", "Últimas Notícias", "Recomendações de Compra"],
    key="nav_sidebar_cfg"
)

if aba_lateral != "Chat Principal":
    st.info(f"💡 Você selecionou **{aba_lateral}**. Para visualizar esta secção inteira, aceda à página principal (**app**).")

# CONTEÚDO
st.title("⚙️ Configurações da Plataforma")
st.caption("Gerencie credenciais de acesso às APIs e parâmetros do sistema.")

st.markdown("---")

with st.form("form_config_api"):
    st.subheader("🔑 Credenciais de Acesso")
    st.text_input("Chave da API OpenAI (sk-proj-...)", type="password", key="input_openai")
    st.text_input("Chave de Conexão Corretora / MetaTrader API", type="password", key="input_broker")
    
    st.selectbox(
        "Modo de Operação Padrão da IA",
        ["Conservador", "Moderado", "Agressivo"],
        key="select_modo_ia"
    )
    
    if st.form_submit_button("Guardar Configurações"):
        st.success("Configurações atualizadas com sucesso!")

st.markdown("---")
st.info("ℹ️ Certifique-se de manter as suas chaves de API em segurança e nunca as partilhe publicamente.")
