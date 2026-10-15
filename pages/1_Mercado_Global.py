import streamlit as st
import yfinance as yf

# Estilização visual para manter o mesmo padrão escuro do app principal
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
# BARRA LATERAL (WIDGETS REATIVADOS NA PÁGINA)
# ---------------------------------------------------------
st.sidebar.title("💬 Histórico de Prompts")
st.sidebar.markdown("---")

if "historico" in st.session_state and st.session_state.historico:
    st.sidebar.markdown("**Conversas Anteriores:**")
    for i, msg in enumerate(st.session_state.historico):
        if msg["role"] == "user":
            resumo = msg["content"] if isinstance(msg["content"], str) else "[Imagem Enviada]"
            st.sidebar.button(f"📌 {resumo[:22]}...", key=f"hist_global_{i}")
else:
    st.sidebar.caption("Nenhum histórico recente.")

st.sidebar.markdown("---")
st.sidebar.subheader("📰 Mercado & Ativos")
st.sidebar.info("💡 Dica: Acesse a página principal ('app') para navegar entre as abas do assistente!")

# ---------------------------------------------------------
# CONTEÚDO PRINCIPAL DO MERCADO GLOBAL
# ---------------------------------------------------------
st.title("🌍 Mercado Global e Ativos")

st.info("💡 **Como usar:** Escolha qualquer ativo logo abaixo para ver o comportamento do preço ao longo do tempo. O gráfico mostra se o valor subiu ou caiu de forma bem visual!")

TODOS_ATIVOS = {
    "^GSPC": "S&P 500 (As 500 Maiores Empresas dos EUA)",
    "^IXIC": "Nasdaq (Bolsa das Empresas de Tecnologia dos EUA)",
    "^DJI": "Dow Jones (Bolsa Tradicional de Nova York)",
    "^BVSP": "Ibovespa (O Principal Índice da Bolsa do Brasil)",
    "USDBRL=X": "Dólar Comercial (Cotação frente ao Real)",
    "BTC-USD": "Bitcoin (A Principal Criptomoeda do Mundo)",
    "ETH-USD": "Ethereum (Segunda Maior Criptomoeda)",
    "AAPL": "Apple (Fabricante do iPhone)",
    "MSFT": "Microsoft (Gigante de Softwares e Tecnologia)",
    "NVDA": "Nvidia (Líder em Placas de Vídeo e Inteligência Artificial)",
    "PETR4.SA": "Petrobras (Ações Preferenciais - Foco em Dividendos)",
    "VALE3.SA": "Vale (Mineração e Commodities)",
    "ITUB4.SA": "Itaú Unibanco (Maior Banco Privado do Brasil)",
    "MXRF11.SA": "Fundo Imobiliário MXRF11 (Papel / Papéis Imobiliários)",
    "HGLG11.SA": "Fundo Imobiliário HGLG11 (Galpões Logísticos)"
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

st.subheader("📊 Como estão os principais índices agora?")
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
            delta=f"{info['var']:+.2f}%"
        )

st.divider()

st.subheader("📈 Olhada Rápida no Gráfico de Preços")

col_sel1, col_sel2 = st.columns([2, 1])

with col_sel1:
    ativo_selecionado = st.selectbox(
        "Escolha o que deseja acompanhar:",
        options=list(TODOS_ATIVOS.keys()),
        format_func=lambda x: f"{x} — {TODOS_ATIVOS[x]}"
    )

with col_sel2:
    periodo_selecionado = st.selectbox(
        "Qual o período?",
        options=["1d", "5d", "1mo", "6mo", "1y"],
        index=2,
        format_func=lambda x: {
            "1d": "Hoje (1 Dia)",
            "5d": "Últimos 5 Dias",
            "1mo": "Último Mês",
            "6mo": "Últimos 6 Meses",
            "1y": "Último Ano"
        }[x]
    )

intervalo_map = {"1d": "5m", "5d": "15m", "1mo": "1d", "6mo": "1d", "1y": "1wk"}
intervalo = intervalo_map.get(periodo_selecionado, "1d")

df_grafico = carregar_historico_grafico(ativo_selecionado, periodo_selecionado, intervalo)

if df_grafico is not None and not df_grafico.empty:
    st.line_chart(df_grafico["Close"])
    st.caption("📌 *Dica:* Cada ponto no gráfico representa o preço de fechamento no período selecionado.")
else:
    st.warning("Não foi possível carregar o gráfico deste ativo no momento.")
