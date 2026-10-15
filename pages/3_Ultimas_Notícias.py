import urllib.parse
import feedparser
import streamlit as st

st.set_page_config(page_title="Últimas Notícias | BrokerSimples", layout="wide")

# Estilização padrão do app
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

# ---------------------------------------------------------
# BARRA LATERAL (PAINEL ATIVO NETA PÁGINA)
# ---------------------------------------------------------
st.sidebar.title("💬 Histórico de Prompts")
st.sidebar.markdown("---")

if "historico" in st.session_state and st.session_state.historico:
    st.sidebar.markdown("**Conversas Anteriores:**")
    for i, msg in enumerate(st.session_state.historico):
        if msg["role"] == "user":
            resumo = msg["content"] if isinstance(msg["content"], str) else "[Imagem Enviada]"
            st.sidebar.button(f"📌 {resumo[:22]}...", key=f"hist_news_{i}")
else:
    st.sidebar.caption("Nenhum histórico recente.")

st.sidebar.markdown("---")
st.sidebar.subheader("📰 Mercado & Ativos")
st.sidebar.info("💡 Acesse a página 'app' para usar o chat inteligente do BrokerSimples!")

# ---------------------------------------------------------
# CONTEÚDO DA PÁGINA
# ---------------------------------------------------------
st.title("📰 Notícias do Mercado em Tempo Real")

@st.cache_data(ttl=900)
def buscar_noticias_google_news(termo_busca):
    try:
        termo_encoded = urllib.parse.quote(f"{termo_busca} quando:1d")
        rss_url = f"https://news.google.com/rss/search?q={termo_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        feed = feedparser.parse(rss_url)
        noticias = []
        for entry in feed.entries[:15]:
            noticias.append({
                'title': entry.get('title', 'Sem título'),
                'link': entry.get('link', '#'),
                'source': entry.get('source', {}).get('title', 'Google News'),
                'published': entry.get('published', '')
            })
        return noticias
    except Exception:
        return []

def exibir_noticias(termo_ativo):
    noticias = buscar_noticias_google_news(termo_ativo)
    if noticias:
        st.write(f"Exibindo as **{len(noticias)} notícias mais recentes de hoje**:")
        for item in noticias:
            st.subheader(f"[{item['title']}]({item['link']})")
            data_pub = f" | {item['published']}" if item['published'] else ""
            st.caption(f"Fonte: {item['source']}{data_pub}")
            st.divider()
    else:
        st.info("Nenhuma notícia encontrada no momento.")

acoes_b3 = sorted(["ABEV3", "B3SA3", "BBAS3", "BBDC4", "ITUB4", "PETR4", "VALE3", "WEGE3"])
fiis = sorted(["HGLG11", "KNRI11", "MXRF11", "XPML11"])
renda_fixa_macro = ["Dólar", "Ibovespa", "Taxa Selic", "Inflação IPCA"]
cripto = ["Bitcoin", "Ethereum", "Solana"]
internacional = ["S&P 500", "Nasdaq", "Apple", "Nvidia"]

tab_acoes, tab_fiis, tab_rf, tab_cripto, tab_inter = st.tabs([
    "📈 Ações B3", "🏢 Fundos Imobiliários", "💵 Renda Fixa / Macro", "🪙 Criptomoedas", "🌐 Internacional"
])

with tab_acoes:
    ativo = st.selectbox("Selecione a Ação:", acoes_b3, key="acoes")
    exibir_noticias(f"{ativo} ação B3")

with tab_fiis:
    ativo = st.selectbox("Selecione o FII:", fiis, key="fiis")
    exibir_noticias(f"{ativo} fundo imobiliario")

with tab_rf:
    ativo = st.selectbox("Selecione o Indicador:", renda_fixa_macro, key="rf")
    exibir_noticias(ativo)

with tab_cripto:
    ativo = st.selectbox("Selecione a Criptomoeda:", cripto, key="cripto")
    exibir_noticias(ativo)

with tab_inter:
    ativo = st.selectbox("Selecione o Ativo Internacional:", internacional, key="inter")
    exibir_noticias(ativo)
