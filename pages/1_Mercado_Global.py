import streamlit as st
import yfinance as yf

st.title("🌍 Mercado Global em Tempo Real")


# Cache de 1 hora (3600 segundos) para não sobrecarregar a API
@st.cache_data(ttl=3600)
def carregar_dados_mercado_global(tickers):
  dados = {}
  for ticker in tickers:
    try:
      ativo = yf.Ticker(ticker)
      # Obtém as informações principais do ativo
      dados[ticker] = ativo.history(period="1d")
    except Exception:
      dados[ticker] = None
  return dados


# Cache de 1 hora para as notícias internacionais
@st.cache_data(ttl=3600)
def carregar_noticias_globais(ticker_simbolo):
  try:
    t = yf.Ticker(ticker_simbolo)
    return t.news if t.news else []
  except Exception:
    return []


# Exemplo de lista de índices e ativos globais
indices_globais = [
    "^GSPC",  # S&P 500
    "^IXIC",  # Nasdaq
    "^DJI",  # Dow Jones
    "^FTSE",  # FTSE 100 (Londres)
    "^N225",  # Nikkei 225 (Japão)
]

st.subheader("📊 Principais Índices do Mundo")

# Carrega os dados com cache de 1 hora
dados_indices = carregar_dados_mercado_global(indices_globais)

col1, col2, col3 = st.columns(3)
colunas = [col1, col2, col3]

for idx, ticker in enumerate(indices_globais):
  col = colunas[idx % 3]
  df = dados_indices.get(ticker)

  if df is not None and not df.empty:
    preco_atual = df["Close"].iloc[-1]
    preco_abertura = df["Open"].iloc[-1]
    variacao = ((preco_atual - preco_abertura) / preco_abertura) * 100

    col.metric(
        label=ticker,
        value=f"{preco_atual:,.2f}",
        delta=f"{variacao:+.2f}%",
    )

st.divider()
st.subheader("📰 Notícias Internacionais")

ativo_noticia = st.selectbox(
    "Selecione o Mercado/Ativo para ver notícias:",
    ["^GSPC", "^IXIC", "AAPL", "MSFT", "NVDA", "TSLA"],
)

noticias = carregar_noticias_globais(ativo_noticia)

if noticias:
  for item in noticias[:5]:
    content = item.get("content", {})
    titulo = (
        item.get("title")
        or content.get("title")
        or item.get("headline")
        or "Sem título"
    )

    link_obj = (
        item.get("link")
        or content.get("canonicalUrl")
        or content.get("clickThroughUrl")
    )
    link = link_obj.get("url", "#") if isinstance(link_obj, dict) else (link_obj or "#")

    publisher = item.get("publisher") or content.get("provider")
    fonte = (
        publisher.get("displayName", "Fonte desconhecida")
        if isinstance(publisher, dict)
        else (publisher or "Fonte desconhecida")
    )

    st.subheader(f"[{titulo}]({link})")
    st.caption(f"Fonte: {fonte}")
    st.divider()
else:
  st.info("Nenhuma notícia encontrada para este ativo no momento.")
