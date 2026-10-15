import streamlit as st
import yfinance as yf

st.title("📰 Notícias em Tempo Real")

# Selecionar o ativo para ver notícias
ticker_simbolo = st.selectbox("Escolha o ativo para ver as notícias:", ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "^BVSP"])

# Buscar informações do ativo
ticker = yf.Ticker(ticker_simbolo)
noticias = ticker.news

if noticias:
    for item in noticias[:5]:  # Mostra as 5 notícias mais recentes
        # O yfinance reorganizou a estrutura de notícias recentemente
        titulo = item.get('title') or item.get('content', {}).get('title', 'Sem título')
        link = item.get('link') or item.get('content', {}).get('canonicalUrl', {}).get('url', '#')
        fonte = item.get('publisher') or item.get('content', {}).get('provider', {}).get('displayName',
                                                                                         'Fonte desconhecida')

        st.subheader(f"[{titulo}]({link})")
        st.caption(f"Fonte: {fonte}")
        st.divider()
else:
    st.info("Nenhuma notícia encontrada para este ativo no momento.")