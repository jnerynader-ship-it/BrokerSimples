import streamlit as st
import yfinance as yf

st.title("🌍 Mercado Global e Ativos")

TODOS_ATIVOS = {
    "^GSPC": "S&P 500 (EUA)",
    "^IXIC": "Nasdaq (EUA)",
    "^DJI": "Dow Jones (EUA)",
    "^BVSP": "Ibovespa (Brasil)",
    "USDBRL=X": "Dólar / Real",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "PETR4.SA": "Petrobras PN",
    "VALE3.SA": "Vale",
    "ITUB4.SA": "Itaú Unibanco",
    "MXRF11.SA": "FII MXRF11",
    "HGLG11.SA": "FII HGLG11",
}

indices_resumo = ["^GSPC", "^IXIC", "^DJI", "^BVSP"]


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


@st.cache_data(ttl=3600)
def carregar_historico_grafico(ticker_simbolo, periodo, intervalo):
  try:
    ativo = yf.Ticker(ticker_simbolo)
    df = ativo.history(period=periodo, interval=intervalo)
    return df
  except Exception:
    return None


st.subheader("📊 Resumo dos Principais Índices")
resumo = carregar_resumo_mercado(indices_resumo)

col1, col2, col3, col4 = st.columns(4)
colunas = [col1, col2, col3, col4]

for idx, ticker in enumerate(indices_resumo):
  col = colunas[idx % 4]
  info = resumo.get(ticker)
  if info:
    col.metric(
        label=f"{ticker}",
        value=f"{info['preco']:,.2f}",
        delta=f"{info['var']:+.2f}%",
    )

st.divider()

st.subheader("📈 Gráfico de Desempenho em Tempo Real")

col_sel1, col_sel2 = st.columns([2, 1])

with col_sel1:
  ativo_selecionado = st.selectbox(
      "Selecione o ativo:",
      options=list(TODOS_ATIVOS.keys()),
      format_func=lambda x: f"{x} - {TODOS_ATIVOS[x]}",
  )

with col_sel2:
  periodo_selecionado = st.selectbox(
      "Período:",
      options=["1d", "5d", "1mo", "6mo", "1y"],
      index=2,
      format_func=lambda x: {
          "1d": "1 Dia",
          "5d": "5 Dias",
          "1mo": "1 Mês",
          "6mo": "6 Meses",
          "1y": "1 Ano",
      }[x],
  )

intervalo_map = {
    "1d": "5m",
    "5d": "15m",
    "1mo": "1d",
    "6mo": "1d",
    "1y": "1wk",
}
intervalo = intervalo_map.get(periodo_selecionado, "1d")

df_grafico = carregar_historico_grafico(
    ativo_selecionado, periodo_selecionado, intervalo
)

if df_grafico is not None and not df_grafico.empty:
  st.line_chart(df_grafico["Close"])
else:
  st.warning(
      "Não foi possível carregar os dados do gráfico para este ativo no"
      " momento."
  )
