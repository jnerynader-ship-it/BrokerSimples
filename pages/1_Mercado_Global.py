import streamlit as st
import yfinance as yf

st.title("🌍 Mercado Global")

# Lista dos principais índices
indices_globais = {
    "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq",
    "^DJI": "Dow Jones",
    "^FTSE": "FTSE 100",
    "^N225": "Nikkei 225",
}


# Cache de 1 hora para buscar cotações atuais
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


# Cache de 1 hora para os dados do gráfico
@st.cache_data(ttl=3600)
def carregar_historico_grafico(ticker_simbolo, periodo, intervalo):
  try:
    ativo = yf.Ticker(ticker_simbolo)
    df = ativo.history(period=periodo, interval=intervalo)
    return df
  except Exception:
    return None


st.subheader("📊 Principais Índices do Mundo")

# Exibição dos cards de topo (métricas)
resumo = carregar_resumo_mercado(list(indices_globais.keys()))

col1, col2, col3 = st.columns(3)
colunas = [col1, col2, col3]

for idx, (ticker, nome) in enumerate(indices_globais.items()):
  col = colunas[idx % 3]
  info = resumo.get(ticker)
  if info:
    col.metric(
        label=f"{ticker} ({nome})",
        value=f"{info['preco']:,.2f}",
        delta=f"{info['var']:+.2f}%",
    )

st.divider()

# Seção do Gráfico Interativo no lugar das notícias
st.subheader("📈 Gráfico de Desempenho em Tempo Real")

col_sel1, col_sel2 = st.columns([2, 1])

with col_sel1:
  ativo_selecionado = st.selectbox(
      "Selecione o Índice/Ativo para visualizar:",
      options=list(indices_globais.keys()),
      format_func=lambda x: f"{x} - {indices_globais[x]}",
  )

with col_sel2:
  periodo_selecionado = st.selectbox(
      "Período:",
      options=["1d", "5d", "1mo", "6mo", "1y", "5y"],
      index=2,
      format_func=lambda x: {
          "1d": "1 Dia",
          "5d": "5 Dias",
          "1mo": "1 Mês",
          "6mo": "6 Meses",
          "1y": "1 Ano",
          "5y": "5 Anos",
      }[x],
  )

intervalo_map = {
    "1d": "5m",
    "5d": "15m",
    "1mo": "1d",
    "6mo": "1d",
    "1y": "1wk",
    "5y": "1mo",
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
