import streamlit as st
import yfinance as yf

st.title("📰 Notícias do Mercado em Tempo Real")


# Função auxiliar para carregar e exibir as notícias de um ativo
def exibir_noticias(ticker_simbolo):
  # Adiciona automaticamente o .SA se for um ativo da B3/FII para o yfinance conseguir consultar
  # (Assume-se que tickers com 4 a 6 letras/números da B3 precisam do .SA para dados, exceto índices/cripto/internacional)
  ticker = yf.Ticker(ticker_simbolo)
  noticias = ticker.news

  if noticias:
    for item in noticias[:5]:  # Exibe as 5 notícias mais recentes
      titulo = (
          item.get("title")
          or item.get("content", {}).get("title", "Sem título")
      )
      link = (
          item.get("link")
          or item.get("content", {}).get("canonicalUrl", {}).get("url", "#")
      )
      fonte = (
          item.get("publisher")
          or item.get("content", {}).get("provider", {}).get(
              "displayName", "Fonte desconhecida"
          )
      )

      st.subheader(f"[{titulo}]({link})")
      st.caption(f"Fonte: {fonte}")
      st.divider()
  else:
    st.info("Nenhuma notícia recente encontrada para este ativo no momento.")


# Listas de ativos SEM o .SA no final
acoes_b3 = [
    "PETR4",
    "VALE3",
    "ITUB4",
    "BBDC4",
    "ABEV3",
    "WEGE3",
    "RENT3",
    "MGLU3",
    "BBAS3",
    "JBSS3",
    "LREN3",
    "SUZB3",
    "GGBR4",
    "CSNA3",
    "EQTL3",
]

fiis = ["HGLG11", "KNCR11", "MXRF11", "XPML11", "BCSC11"]

renda_fixa_macro = ["USDBRL=X", "BRL=X", "^BVSP"]

cripto = [
    "BTC-USD",
    "ETH-USD",
    "SOL-USD",
    "BNB-USD",
    "XRP-USD",
    "ADA-USD",
    "DOGE-USD",
    "AVAX-USD",
    "LINK-USD",
]

internacional = [
    "^GSPC",
    "^IXIC",
    "^DJI",
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
    "META",
    "TSLA",
    "NFLX",
]

# Criação das abas no Streamlit
tab_acoes, tab_fiis, tab_rf, tab_cripto, tab_inter = st.tabs([
    "📈 Ações B3",
    "🏢 Fundos Imobiliários",
    "💵 Renda Fixa / Macro",
    "🪙 Criptomoedas",
    "🌐 Internacional",
])

with tab_acoes:
  ativo = st.selectbox("Selecione a Ação:", acoes_b3, key="acoes")
  # Como a lista já não tem o .SA, se o yfinance precisar dele para ações brasileiras,
  # podemos concatenar o '.SA' apenas no envio para a função:
  exibir_noticias(ativo + ".SA" if not ativo.startswith("^") else ativo)

with tab_fiis:
  ativo = st.selectbox("Selecione o FII:", fiis, key="fiis")
  exibir_noticias(ativo + ".SA")

with tab_rf:
  ativo = st.selectbox(
      "Selecione o Índice/Moeda:", renda_fixa_macro, key="rf"
  )
  exibir_noticias(ativo)

with tab_cripto:
  ativo = st.selectbox("Selecione a Criptomoeda:", cripto, key="cripto")
  exibir_noticias(ativo)

with tab_inter:
  ativo = st.selectbox(
      "Selecione o Ativo Internacional:", internacional, key="inter"
  )
  exibir_noticias(ativo)