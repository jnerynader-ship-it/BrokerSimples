import streamlit as st
import yfinance as yf

st.title("📰 Notícias do Mercado em Tempo Real")


# Função auxiliar para carregar e exibir as notícias de um ativo
def exibir_noticias(ticker_simbolo):
    ticker = yf.Ticker(ticker_simbolo)
    noticias = ticker.news

    if noticias:
        for item in noticias[:5]:  # Exibe as 5 notícias mais recentes
            titulo = item.get('title') or item.get('content', {}).get('title', 'Sem título')
            link = item.get('link') or item.get('content', {}).get('canonicalUrl', {}).get('url', '#')
            fonte = item.get('publisher') or item.get('content', {}).get('provider', {}).get('displayName',
                                                                                             'Fonte desconhecida')

            st.subheader(f"[{titulo}]({link})")
            st.caption(f"Fonte: {fonte}")
            st.divider()
    else:
        st.info("Nenhuma notícia recente encontrada para este ativo no momento.")


# Listas de ativos por categoria
acoes_b3 = [
    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA",
    "WEGE3.SA", "RENT3.SA", "MGLU3.SA", "BBAS3.SA", "JBSS3.SA",
    "LREN3.SA", "SUZB3.SA", "GGBR4.SA", "CSNA3.SA", "EQTL3.SA"
]

fiis = [
    "HGLG11.SA", "KNCR11.SA", "MXRF11.SA", "XPML11.SA", "BCSC11.SA",
    "VISC11.SA", "TGAR11.SA", "IRDM11.SA", "CPTS11.SA", "XPIN11.SA"
]

renda_fixa_macro = [
    "^BVSP", "BRL=X", "USDBRL=X", "EURBRL=X", "^TNX"
]

cripto = [
    "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD",
    "ADA-USD", "DOGE-USD", "AVAX-USD", "LINK-USD"
]

internacional = [
    "^GSPC", "^IXIC", "^DJI", "AAPL", "MSFT", "NVDA",
    "AMZN", "GOOGL", "META", "TSLA", "NFLX"
]

# Criação das abas no Streamlit
tab_acoes, tab_fiis, tab_rf, tab_cripto, tab_inter = st.tabs([
    "📈 Ações B3",
    "🏢 Fundos Imobiliários",
    "💵 Renda Fixa / Macro",
    "🪙 Criptomoedas",
    "🌐 Internacional"
])

with tab_acoes:
    ativo = st.selectbox("Selecione a Ação:", acoes_b3, key="acoes")
    exibir_noticias(ativo)

with tab_fiis:
    ativo = st.selectbox("Selecione o FII:", fiis, key="fiis")
    exibir_noticias(ativo)

with tab_rf:
    ativo = st.selectbox("Selecione o Índice/Moeda:", renda_fixa_macro, key="rf")
    exibir_noticias(ativo)

with tab_cripto:
    ativo = st.selectbox("Selecione a Criptomoeda:", cripto, key="cripto")
    exibir_noticias(ativo)

with tab_inter:
    ativo = st.selectbox("Selecione o Ativo Internacional:", internacional, key="inter")
    exibir_noticias(ativo)