import streamlit as st

st.set_page_config(page_title="Educação e Aprendizado | BrokerSimples", layout="wide")

# Estilização visual padrão
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
# BARRA LATERAL (ESTRUTURA COMPLETA)
# ---------------------------------------------------------
st.sidebar.title("💬 Histórico de Prompts")
st.sidebar.markdown("---")

if "historico" in st.session_state and st.session_state.historico:
    st.sidebar.markdown("**Conversas Anteriores:**")
    for i, msg in enumerate(st.session_state.historico):
        if msg["role"] == "user":
            resumo = msg["content"] if isinstance(msg["content"], str) else "[Imagem Enviada]"
            st.sidebar.button(f"📌 {resumo[:22]}...", key=f"hist_edu_{i}")
else:
    st.sidebar.caption("Nenhum histórico recente.")

st.sidebar.markdown("---")
st.sidebar.subheader("📚 Educação & Aprendizado")
st.sidebar.info("💡 Dica: Utilize esta secção para estudar conceitos fundamentais de investimentos e gestão de portfólio!")

# ---------------------------------------------------------
# CONTEÚDO DA PÁGINA DE EDUCAÇÃO E APRENDIZADO
# ---------------------------------------------------------
st.title("🎓 Central de Educação e Aprendizado Financeiro")
st.caption("Aprenda os pilares do mercado de capitais, análise fundamentalista, valuation e gestão de risco.")

st.markdown("---")

tab_fundamentos, tab_analise, tab_psicologia, tab_glossario = st.tabs([
    "📖 Fundamentos de Investimento", 
    "📊 Análise de Ações & FIIs", 
    "🧠 Psicologia do Mercado", 
    "📚 Glossário Financeiro"
])

with tab_fundamentos:
    st.header("💡 Os Pilares do Investidor de Sucesso")
    st.markdown("""
    Investir não é especular; é alocar capital em ativos geradores de valor a longo prazo. Conheça os conceitos essenciais:
    
    * **1. Juros Compostos:** O tempo no mercado é mais importante do que tentar acertar o momento exato (*timing*). O reinvestimento de dividendos acelera exponencialmente o património.
    * **2. Diversificação Inteligente:** Não coloque todos os ovos no mesmo cesto. Divida entre renda fixa (proteção), ações sólidas (crescimento/dividendos) e ativos internacionais (proteção cambial).
    * **3. Margem de Segurança:** Comprar um ativo por um valor abaixo do seu justo valor intrínseco protege o capital contra volatilidades imprevistas.
    """)

with tab_analise:
    st.header("📈 Como Analisar uma Empresa ou FII")
    st.markdown("""
    Para avaliar se uma ação ou Fundo Imobiliário vale a pena, analise os seguintes indicadores fundamentalistas:
    
    * **P/L (Preço sobre Lucro):** Indica quanto os investidores estão pagando por cada real de lucro da empresa.
    * **ROE (Return on Equity):** Mede a eficiência da empresa em gerar lucro com o dinheiro dos acionistas (quanto maior e consistente, melhor).
    * **Dividend Yield (DY):** O retorno percentual pago em dividendos em relação ao preço atual da cota ou ação.
    * **P/VP (Preço sobre Valor Patrimonial nos FIIs):** Mostra se o fundo está sendo negociado com ágio (>1) ou desconto (<1) em relação aos seus imóveis.
    """)

with tab_psicologia:
    st.header("🧠 Psicologia Econômica e Comportamental")
    st.markdown("""
    O maior inimigo do investidor costuma ser o espelho. Os vieses mais comuns que prejudicam a rentabilidade são:
    
    * **Efeito Manada:** Comprar um ativo só porque "todo mundo está falando sobre ele" na alta, e vender em pânico na baixa.
    * **Aversão à Perda:** A dor de perder dinheiro é psicologicamente duas vezes mais forte do que a alegria de ganha-lo, o que leva investidores a segurarem ativos ruins por muito tempo.
    * **Visão de Curto Prazo:** Confundir volatilidade diária com perda de fundamentos da empresa.
    """)

with tab_glossario:
    st.header("📚 Glossário Rápido do Mercado")
    st.markdown("""
    * **Bear Market:** Mercado em tendência de queda prolongada (pessimismo).
    * **Bull Market:** Mercado em alta sostenida (otimismo).
    * **Circuit Breaker:** Mecanismo de segurança da B3 que paralisa os negócios temporariamente em caso de quedas drásticas no Ibovespa.
    * **IPO (Initial Public Offering):** Abertura de capital de uma empresa na bolsa de valores.
    """)
