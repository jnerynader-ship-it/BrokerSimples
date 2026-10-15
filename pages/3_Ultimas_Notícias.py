import streamlit as st
import yfinance as yf

st.title("📰 Notícias do Mercado em Tempo Real")


# Função com cache de 1 hora e tratamento robusto de erros para o yfinance
@st.cache_data(ttl=3600)
def carregar_noticias_com_cache(ticker_simbolo):
  try:
    t = yf.Ticker(ticker_simbolo)
    noticias = t.news
    return noticias if noticias else []
  except Exception:
    return []


# Função auxiliar para exibir as notícias na tela
def exibir_noticias(ticker_simbolo):
  noticias = carregar_noticias_com_cache(ticker_simbolo)

  if noticias:
    for item in noticias[:5]:  # Exibe as 5 notícias mais recentes
      # Tratamento flexível para diferentes formatos que o yfinance retorna
      content = item.get("content", {})
      titulo = (
          item.get("title")
          or content.get("title")
          or item.get("headline")
          or "Sem título"
      )
      
      link_obj = item.get("link") or content.get("canonicalUrl") or content.get("clickThroughUrl")
      if isinstance(link_obj, dict):
        link = link_obj.get("url", "#")
      else:
        link = link_obj if link_obj else "#"

      publisher = item.get("publisher") or content.get("provider")
      if isinstance(publisher, dict):
        fonte = publisher.get("displayName", "Fonte desconhecida")
      else:
        fonte = publisher if publisher else "Fonte desconhecida"

      st.subheader(f"[{titulo}]({link})")
      st.caption(f"Fonte: {fonte}")
      st.divider()
  else:
    # Tenta buscar um ativo macro global equivalente ou avisa o utilizador
    st.info(
        f"A API do Yahoo Finance não retornou notícias recentes para **{ticker_simbolo}**. Tente selecionar outro ativo (como PETR3, VALE3 ou BTC-USD) enquanto o mercado atualiza."
    )


# TODAS AS AÇÕES DO IBOVESPA
acoes_b3 = sorted([
    "ABEV3",
    "ALOS3",
    "ALPA4",
    "ARZZ3",
    "ASAI3",
    "AZUL4",
    "B3SA3",
    "BBAS3",
    "BBDC3",
    "BBDC4",
    "BBSE3",
    "BEEF3",
    "BPAC11",
    "BRAP4",
    "BRFS3",
    "BRKM5",
    "CASH3",
    "CCRO3",
    "CIEL3",
    "CMIG4",
    "CMIN3",
    "COGN3",
    "CPFE3",
    "CPLE6",
    "CRFB3",
    "CSAN3",
    "CSNA3",
    "CVCB3",
    "CYRE3",
    "DXCO3",
    "EGIE3",
    "ELET3",
    "ELET6",
    "EMBR3",
    "ENEV3",
    "ENGI11",
    "EQTL3",
    "EZTC3",
    "FLRY3",
    "GGBR4",
    "GOAU4",
    "HAPV3",
    "HYPE3",
    "IGTI11",
    "IRBR3",
    "ITSA4",
    "ITUB4",
    "JBSS3",
    "KLBN11",
    "LREN3",
    "LWSA3",
    "MGLU3",
    "MRFG3",
    "MRVE3",
    "MULT3",
    "NTCO3",
    "PCAR3",
    "PETR3",
    "PETR4",
    "PETZ3",
    "PRIO3",
    "RADL3",
    "RAIL3",
    "RAIZ4",
    "RDOR3",
    "RECV3",
    "RENT3",
    "SANB11",
    "SASP3",
    "SLCE3",
    "SMTO3",
    "SOMA3",
    "SUZB3",
    "TAEE11",
    "TOTS3",
    "UGPA3",
    "USIM5",
    "VALE3",
    "VAMO3",
    "VBBR3",
    "VIVT3",
    "WEGE3",
    "YDUQ3",
])

# TODOS OS FUNDOS IMOBILIÁRIOS DO IFIX
fiis = sorted([
    "ALZR11",
    "ARRI11",
    "BCFF11",
    "BCIA11",
    "BCRI11",
    "BMLC11",
    "BNFS11",
    "BPFF11",
    "BRCR11",
    "BRPP11",
    "BTAL11",
    "BTCI11",
    "BTL111",
    "BTLG11",
    "CPFF11",
    "CPIA11",
    "CPTS11",
    "CVBI11",
    "CXCO11",
    "DERA11",
    "GGRC11",
    "GTWR11",
    "HCTR11",
    "HGBS11",
    "HGLG11",
    "HGPO11",
    "HGRE11",
    "HGRU11",
    "HLOG11",
    "HSLG11",
    "HSML11",
    "HTMX11",
    "IRDM11",
    "JSRE11",
    "KFOF11",
    "KNCR11",
    "KNHY11",
    "KNIP11",
    "KNRI11",
    "KNSC11",
    "LIPO11",
    "MALL11",
    "MCCI11",
    "MFII11",
    "MGFF11",
    "MXRF11",
    "OUJP11",
    "PORD11",
    "PVBI11",
    "QAGR11",
    "RBCO11",
    "RBFF11",
    "RBRF11",
    "RBRP11",
    "RBRR11",
    "RECR11",
    "RECT11",
    "RPRB11",
    "RZAK11",
    "RZTR11",
    "SARE11",
    "SDIL11",
    "SNCI11",
    "SNFF11",
    "SPTW11",
    "TGAR11",
    "TORD11",
    "TRBL11",
    "URPR11",
    "VCJR11",
    "VGIA11",
    "VGIR11",
    "VILG11",
    "VINO11",
    "VISC11",
    "VJFD11",
    "VRTA11",
    "VSLH11",
    "VTLT11",
    "VVPR11",
    "XPCI11",
    "XPIN11",
    "XPLG11",
    "XPML11",
    "XPSF11",
])

renda_fixa_macro = ["USDBRL=X", "BRL=X", "EURBRL=X", "^BVSP", "^TNX"]

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

# Abas do Streamlit
tab_acoes, tab_fiis, tab_rf, tab_cripto, tab_inter = st.tabs([
    "📈 Ações B3",
    "🏢 Fundos Imobiliários",
    "💵 Renda Fixa / Macro",
    "🪙 Criptomoedas",
    "🌐 Internacional",
])

with tab_acoes:
  ativo = st.selectbox("Selecione a Ação:", acoes_b3, key="acoes")
  exibir_noticias(ativo + ".SA")

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
