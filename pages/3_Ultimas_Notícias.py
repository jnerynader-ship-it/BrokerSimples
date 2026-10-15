import os
import urllib.parse
import feedparser
import streamlit as st

st.set_page_config(
    page_title="Últimas Notícias | BrokerSimples",
    page_icon="📰",
    layout="wide",
)

# Logo nativa no topo esquerdo da barra lateral
if os.path.exists("logo.png"):
  st.logo("logo.png", icon_image="logo.png")

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# BARRA LATERAL
st.sidebar.title("💬 Histórico de Prompts")
st.sidebar.markdown("---")

if "historico" in st.session_state and st.session_state.historico:
  st.sidebar.markdown("**Conversas Anteriores:**")
  for i, msg in enumerate(st.session_state.historico):
    if msg["role"] == "user":
      resumo = (
          msg["content"] if isinstance(msg["content"], str) else "[Imagem Enviada]"
      )
      st.sidebar.button(f"📌 {resumo[:22]}...", key=f"hist_news_{i}")
else:
  st.sidebar.caption("Nenhum histórico recente.")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Mercado & Ativos")
aba_lateral = st.sidebar.radio(
    "Navegação Rápida:",
    ["Chat Principal", "Últimas Notícias", "Recomendações de Compra"],
    key="nav_sidebar_news",
)

if aba_lateral != "Chat Principal":
  st.info(
      f"💡 Você selecionou **{aba_lateral}**. Para visualizar esta secção"
      " inteira, aceda à página principal (**app**)."
  )


@st.cache_data(ttl=900)
def buscar_noticias_ativo(termo_busca):
  noticias = []
  links_vistos = set()
  queries = [f"{termo_busca} quando:1d", f"{termo_busca}"]

  for q in queries:
    if len(noticias) >= 10:
      break
    try:
      q_encoded = urllib.parse.quote(q)
      rss_url = f"https://news.google.com/rss/search?q={q_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
      feed = feedparser.parse(rss_url)

      for entry in feed.entries[:12]:
        link = entry.get("link", "#")
        if link not in links_vistos:
          links_vistos.add(link)
          noticias.append({
              "title": entry.get("title", "Sem título"),
              "link": link,
              "source": entry.get("source", {}).get(
                  "title", "Portal de Notícias"
              ),
              "published": entry.get("published", ""),
          })
    except Exception:
      pass
  return noticias[:15]


def exibir_noticias_do_ativo(termo_ativo, chave_unica):
  col_header, col_btn = st.columns([4, 1])
  with col_header:
    st.write(
        f"🔍 Notícias mais recentes desenvolvidas sobre **{termo_ativo}**:"
    )
  with col_btn:
    if st.button("🔄 Atualizar Agora", key=f"btn_refresh_{chave_unica}"):
      st.cache_data.clear()
      st.rerun()

  with st.spinner("Busca em tempo real nas fontes de imprensa..."):
    noticias = buscar_noticias_ativo(termo_ativo)

  if noticias:
    for idx, item in enumerate(noticias, 1):
      st.markdown(f"### {idx}. [{item['title']}]({item['link']})")
      data_pub = f" | 🕒 *{item['published']}*" if item['published'] else ""
      st.caption(f"Fonte: **{item['source']}**{data_pub}")
      st.divider()
  else:
    st.warning(f"Nenhuma notícia encontrada no momento para **{termo_ativo}**.")


st.title("📰 Notícias por Ativo em Tempo Real")
st.caption(
    "Notícias atualizadas a cada 15 minutos para cada ação, FII, cripto ou"
    " indicador selecionado."
)

ACOES_B3 = {
    "ITUB4": "Itaú ITUB4",
    "PETR4": "Petrobras PETR4",
    "VALE3": "Vale VALE3",
    "BBDC4": "Bradesco BBDC4",
    "BBAS3": "Banco do Brasil BBAS3",
    "B3SA3": "B3 B3SA3",
    "ABEV3": "Ambev ABEV3",
    "WEGE3": "Weg WEGE3",
    "MGLU3": "Magazine Luiza MGLU3",
    "RENT3": "Localiza RENT3",
}
FIIS = {
    "MXRF11": "Fundo Imobiliario MXRF11",
    "HGLG11": "Fundo Imobiliario HGLG11",
    "XPML11": "Fundo Imobiliario XPML11",
    "KNRI11": "Fundo Imobiliario KNRI11",
    "BTLG11": "Fundo Imobiliario BTLG11",
}
RENDA_FIXA = {
    "Dólar": "Dólar comercial câmbio",
    "Ibovespa": "Ibovespa bolsa de valores",
    "Taxa Selic": "Taxa Selic Banco Central",
    "Inflação IPCA": "Inflação IPCA IBGE",
}
CRIPTO = {
    "Bitcoin": "Bitcoin Criptomoeda",
    "Ethereum": "Ethereum Criptomoeda",
    "Solana": "Solana Criptomoeda",
}
INTERNACIONAL = {
    "S&P 500": "S&P 500 índice EUA",
    "Nasdaq": "Nasdaq tecnologia",
    "Apple": "Apple Ações NVDA AAPL",
    "Nvidia": "Nvidia inteligência artificial",
}

tab_acoes, tab_fiis, tab_rf, tab_cripto, tab_inter = st.tabs([
    "📈 Ações B3",
    "🏢 Fundos Imobiliários",
    "💵 Renda Fixa / Macro",
    "🪙 Criptomoedas",
    "🌐 Internacional",
])

with tab_acoes:
  codigo_acao = st.selectbox(
      "Selecione a Ação:", list(ACOES_B3.keys()), key="sel_acao"
  )
  exibir_noticias_do_ativo(
      ACOES_B3[codigo_acao], chave_unica=f"acao_{codigo_acao}"
  )

with tab_fiis:
  codigo_fii = st.selectbox(
      "Selecione o FII:", list(FIIS.keys()), key="sel_fii"
  )
  exibir_noticias_do_ativo(FIIS[codigo_fii], chave_unica=f"fii_{codigo_fii}")

with tab_rf:
  nome_rf = st.selectbox(
      "Selecione o Indicador:", list(RENDA_FIXA.keys()), key="sel_rf"
  )
  exibir_noticias_do_ativo(RENDA_FIXA[nome_rf], chave_unica=f"rf_{nome_rf}")

with tab_cripto:
  nome_cripto = st.selectbox(
      "Selecione a Criptomoeda:", list(CRIPTO.keys()), key="sel_cripto"
  )
  exibir_noticias_do_ativo(
      CRIPTO[nome_cripto], chave_unica=f"cripto_{nome_cripto}"
  )

with tab_inter:
  nome_inter = st.selectbox(
      "Selecione o Ativo Internacional:",
      list(INTERNACIONAL.keys()),
      key="sel_inter",
  )
  exibir_noticias_do_ativo(
      INTERNACIONAL[nome_inter], chave_unica=f"inter_{nome_inter}"
  )
