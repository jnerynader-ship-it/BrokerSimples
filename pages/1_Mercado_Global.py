import streamlit as st
import yfinance as yf

st.title("🌍 Mercado Global e Ativos")

# Dicionário organizado com TODOS os ativos possíveis
TODOS_ATIVOS = {
    # --- ÍNDICES E MACRO GLOBAL ---
    "^GSPC": "S&P 500 (EUA)",
    "^IXIC": "Nasdaq (EUA)",
    "^DJI": "Dow Jones (EUA)",
    "^BVSP": "Ibovespa (Brasil)",
    "^FTSE": "FTSE 100 (Londres)",
    "^N225": "Nikkei 225 (Japão)",
    # --- MOEDAS E MACRO ---
    "USDBRL=X": "Dólar / Real",
    "EURBRL=X": "Euro / Real",
    "BRL=X": "Real / Dólar",
    "^TNX": "Treasury 10 Anos (EUA)",
    # --- CRIPTOMOEDAS ---
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana",
    "BNB-USD": "Binance Coin",
    "XRP-USD": "XRP",
    "ADA-USD": "Cardano",
    "DOGE-USD": "Dogecoin",
    "AVAX-USD": "Avalanche",
    "LINK-USD": "Chainlink",
    # --- INTERNACIONAIS (BIG TECHS & OUTRAS) ---
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "AMZN": "Amazon",
    "GOOGL": "Alphabet (Google)",
    "META": "Meta (Facebook)",
    "TSLA": "Tesla",
    "NFLX": "Netflix",
    # --- AÇÕES B3 (EXEMPLOS PRINCIPAIS) ---
    "PETR4.SA": "Petrobras PN",
    "PETR3.SA": "Petrobras ON",
    "VALE3.SA": "Vale",
    "ITUB4.SA": "Itaú Unibanco",
    "BBDC4.SA": "Bradesco",
    "BBAS3.SA": "Banco do Brasil",
    "ABEV3.SA": "Ambev",
    "WEGE3.SA": "Weg",
    "RENT3.SA": "Localiza",
    "MGLU3.SA": "Magazine Luiza",
    # --- FUNDOS IMOBILIÁRIOS (IFIX) ---
    "MXRF11.SA": "FII MXRF11",
    "HGLG11.SA": "FII HGLG11",
    "XPML11.SA": "FII XPML11",
    "KNCR11.SA": "FII KNCR11",
    "BTLG11.SA": "FII BTLG11",
    "VISC11.SA": "FII VISC11",
}

indices_resumo = ["^GSPC", "^IXIC", "^DJI", "^BVSP", "^FTSE", "^N225"]


# Cache de 1 hora para as métricas do topo
@st.cache_data(ttl=3600)
def carregar_resumo_mercado(tickers):
  dados = {}
  for ticker in tickers:
    try:
      ativo = yf.Ticker(ticker)
      hist = ativo.history(period="2d")
      if len(hist) >= 2:
        preco_atual = hist["Close"].iloc[-1]
        preco_anterior = hist["Close"].iloc[-2]
        variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100
        dados[ticker] = {"preco": preco_atual, "var": variacao}
      elif not hist.empty:
        preco_atual = hist["Close"].iloc[-1]
        dados[ticker] = {"preco": preco_atual, "var": 0.0}
    except Exception:
      pass
  return dados


# Cache de 1 hora para carregar os dados do gráfico
@st.cache_data(ttl=3600)
def carregar_historico_grafico(ticker_simbolo, periodo, intervalo):
  try:
    ativo = yf.Ticker(ticker_simbolo)
    df = ativo.history(period=periodo, interval=intervalo)
    return df
  except Exception:
    return None


st.subheader("📊 Resumo dos Principais Índices")

# Métricas do topo
resumo = carregar_resumo_mercado(indices_resumo)

col1, col2, col3 = st.columns(3)
colunas = [col1, col2, col3]

for idx, ticker in enumerate(indices_resumo):
  col = colunas[idx % 3]
  info = resumo.get(ticker)
  nome = TODOS_ATIVOS.get(ticker, ticker)
  if info:
    col.metric(
        label=f"{ticker} ({nome})",
        value=f"{info['preco']:,.2f}",
        delta=f"{info['var']:+.2f}%",
    )

st.divider()

# Seção do Gráfico Interativo com TODOS OS ATIVOS
st.subheader("📈 Gráfico de Desempenho em Tempo Real")

col_sel1, col_sel2 = st.columns([2, 1])

with col_sel1:
  ativo_selecionado = st.selectbox(
      "Selecione QUALQUER ativo do sistema:",
      options=list(TODOS_ATIVOS.keys()),
      format_func=lambda x: f"{x} - {TODOS_ATIVOS[x]}",
  )

with col_sel2:
  periodo_selecionado = st.selectbox(
      "Período:",
      options=["1d", "5d", "1mo", "6mo", "1y", "5y"],
      index=2,  # Padrão: 1 Mês
      format_func=lambda x: {
          "1d": "1 Dia",
          "5d": "5 Dias",
          "1mo": "1 Mês",
          "6mo": "6 Meses",
          "1
