from datetime import datetime, timedelta
import os
import urllib.parse
from openai import OpenAI
import streamlit as st
import yfinance as yf

# Configuração inicial do app
st.set_page_config(
    page_title="BrokerSimples | Assistente Financeiro Inteligente",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Logo nativa no topo esquerdo da barra lateral
if os.path.exists("logo.png"):
  st.logo("logo.png", icon_image="logo.png")

# Estilização visual
st.markdown(
    """
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

    div[data-testid="stMetricValue"], 
    .stChatMessage, 
    .stTextInput > div > div {
        background-color: rgba(30, 41, 59, 0.85) !important;
        color: #f8fafc !important;
        border-radius: 8px;
        backdrop-filter: blur(4px);
    }

    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #f8fafc !important;
    }

    .stButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    .stButton > button:hover {
        background-color: #1d4ed8 !important;
    }

    [data-testid="stChatInput"] {
        border: 1px solid #2563eb !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.25) !important;
        background-color: rgba(15, 23, 42, 0.9) !important;
    }

    [data-testid="stLogo"] {
        max-height: 80px !important;
        height: auto !important;
    }
    [data-testid="stLogo"] img {
        max-height: 80px !important;
        width: auto !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- 1. Indicadores de Mercado (KPIs) ---
st.markdown("### 📊 Visão Geral do Mercado")
col1, col2, col3, col4 = st.columns(4)

try:
  ibov_val = yf.Ticker("^BVSP").history(period="1d")["Close"].iloc[-1]
  dolar_val = yf.Ticker("BRL=X").history(period="1d")["Close"].iloc[-1]
  sp_val = yf.Ticker("^GSPC").history(period="1d")["Close"].iloc[-1]
  petr_val = yf.Ticker("PETR4.SA").history(period="1d")["Close"].iloc[-1]
except Exception:
  ibov_val, dolar_val, sp_val, petr_val = (204324.0, 5.08, 7745.0, 57.92)

with col1:
  st.metric(
      label="IBOVESPA",
      value=f"{ibov_val:,.2f} pts".replace(",", "."),
      delta="-1.0%",
  )
with col2:
  st.metric(label="DÓLAR (USD/BRL)", value=f"R$ {dolar_val:.2f}", delta="+0.3%")
with col3:
  st.metric(
      label="S&P 500",
      value=f"{sp_val:,.2f} pts".replace(",", "."),
      delta="+0.8%",
  )
with col4:
  st.metric(label="PETR4", value=f"R$ {petr_val:.2f}", delta="+1.8%")

st.markdown("---")

# Inicialização do Histórico e Estado de Conversa
if "historico" not in st.session_state:
  st.session_state.historico = []

if "selected_prompt" not in st.session_state:
  st.session_state.selected_prompt = ""

# --- BARRA LATERAL UNIFICADA ---
st.sidebar.title("💬 Histórico de Prompts")
st.sidebar.markdown("---")

if st.session_state.historico:
  st.sidebar.markdown("**Conversas Anteriores:**")
  for i, msg in enumerate(st.session_state.historico):
    if msg["role"] == "user":
      resumo = (
          msg["content"]
          if isinstance(msg["content"], str)
          else "[Imagem Enviada]"
      )
      if st.sidebar.button(f"📌 {resumo[:22]}...", key=f"hist_{i}"):
        st.session_state.selected_prompt = (
            resumo if isinstance(resumo, str) else ""
        )

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Mercado & Ativos")
aba_lateral = st.sidebar.radio(
    "Navegação Rápida:",
    ["Chat Principal", "Últimas Notícias", "Recomendações de Compra"],
)

# --- VERIFICAÇÃO DA CHAVE DE API (OPENAI) ---
try:
  api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
  api_key = ""

if not api_key:
  st.warning(
      "⚠️ Insira a sua chave da OpenAI no ficheiro `secrets.toml` para ativar o"
      " assistente."
  )
  client = None
else:
  client = OpenAI(api_key=api_key)


# --- FUNÇÃO DE CONSULTA REAL VIA YFINANCE ---
@st.cache_data(ttl=300)
def obter_dados_e_noticias_yfinance(ticker_code):
  # Formatação automática para ativos brasileiros se não contiver ponto
  symbol = ticker_code.strip().upper()
  if not symbol.endswith(".SA") and not "-" in symbol and len(symbol) <= 6:
    symbol_sa = f"{symbol}.SA"
  else:
    symbol_sa = symbol

  resultado = {"info": {}, "news": [], "symbol_usado": symbol_sa}

  try:
    ticker = yf.Ticker(symbol_sa)
    resultado["info"] = ticker.info

    # Busca de notícias nativa do yfinance
    raw_news = ticker.news
    if raw_news:
      for n in raw_news[:5]:
        title = n.get("title") or n.get("content", {}).get("title", "Notícia")
        link = n.get("link") or n.get("content", {}).get("clickThroughUrl", {}).get("url", "#")
        publisher = n.get("publisher") or n.get("content", {}).get("provider", {}).get("displayName", "Mercado")
        
        resultado["news"].append({
            "titulo": title,
            "link": link,
            "fonte": publisher
        })
  except Exception:
    pass

  return resultado


# --- CONTEÚDO PRINCIPAL ---
if aba_lateral == "Últimas Notícias":
  st.header("🔥 Radar de Notícias Financeiras em Tempo Real")
  st.caption("Acompanhe as últimas publicações do mercado global e nacional.")
  st.markdown("---")

  noticias_ibov = obter_dados_e_noticias_yfinance("^BVSP")["news"]
  if noticias_ibov:
    for idx, item in enumerate(noticias_ibov, 1):
      st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
      st.caption(f"Fonte: **{item['fonte']}**")
      st.divider()
  else:
    st.info("A carregar últimas notícias do mercado financeiro...")

elif aba_lateral == "Recomendações de Compra":
  st.header("📈 Busca Universal de Ativos & Notícias em Tempo Real")
  st.caption("Consulte QUALQUER ativo negociado na B3, EUA, FIIs, Cripto ou Índices globais.")
  st.markdown("---")

  col_input, col_info = st.columns([2, 1])
  with col_input:
    codigo_digita = st.text_input(
        "Digite o Ticker de QUALQUER ativo (Ex: PVBL11, PETR4, ITUB4, AAPL, BTC-USD):",
        value="PVBL11"
    )
  with col_info:
    st.caption("💡 Para ações do Brasil ou FIIs, o sistema adiciona o sufixo `.SA` automaticamente.")

  if codigo_digita:
    with st.spinner(f"A consultar dados e notícias em tempo real para {codigo_digita}..."):
      dados_ativo = obter_dados_e_noticias_yfinance(codigo_digita)
      info = dados_ativo["info"]
      news = dados_ativo["news"]
      ticker_usado = dados_ativo["symbol_usado"]

    st.markdown(f"## 🔎 Resultado da Pesquisa: **{ticker_usado}**")
    
    col_resumo, col_noticias = st.columns([2, 1])
    
    with col_resumo:
      nome_empresa = info.get("longName") or info.get("shortName") or ticker_usado
      setor = info.get("sector") or info.get("industry") or "Ativo Financeiro / Mercado de Capitais"
      descricao = info.get("longBusinessSummary") or "Ativo consultado via base global de dados financeiros."

      st.markdown(f"### **{nome_empresa}**")
      st.markdown(f"**🏷️ Setor/Classe:** {setor}")
      st.markdown(f"**📖 Resumo do Ativo:** {descricao[:500]}...")
      st.markdown(
          "**🏛️ Contexto Político-Econômico:** Impactado diretamente pelas taxas de juros (Selic/Fed Rates), "
          "indicadores de inflação, políticas fiscais e apetite por risco no mercado internacional."
      )

    with col_noticias:
      st.markdown("### 📰 Notícias Atualizadas em Tempo Real")
      if news:
        for n in news:
          st.markdown(f"📌 [{n['titulo']}]({n['link']})")
          st.caption(f"Fonte: **{n['fonte']}**")
          st.divider()
      else:
        st.warning(f"Sem notícias diretas encontradas no momento para {ticker_usado}. Tente outro ticker como PETR4, ITUB4 ou AAPL.")

else:
  st.title("🤖 BrokerSimples - Assistente Financeiro Inteligente")
  st.markdown("Faça perguntas sobre o mercado ou peça análises ao assistente.")

  for msg in st.session_state.historico:
    role = msg["role"]
    avatar = "👤" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
      if isinstance(msg["content"], list):
        for item in msg["content"]:
          if isinstance(item, str):
            st.write(item)
          elif hasattr(item, "name"):
            st.image(item, width=300)
      else:
        st.write(msg["content"])

  st.markdown("---")
  prompt_chat = st.chat_input("Digite sua dúvida (Ex: Como está a PETR4?)...")

  if st.session_state.selected_prompt:
    prompt_chat = st.session_state.selected_prompt
    st.session_state.selected_prompt = ""

  if prompt_chat:
    conteudo_mensagem = [prompt_chat]
    st.session_state.historico.append(
        {"role": "user", "content": conteudo_mensagem}
    )

    with st.chat_message("user", avatar="👤"):
      st.write(prompt_chat)

    with st.chat_message("assistant", avatar="🤖"):
      if not client:
        st.error("Chave da API OpenAI não configurada.")
      else:
        try:
          with st.spinner("A analisar dados e mercado..."):
            resposta = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é o BrokerSimples, um analista financeiro"
                            " amigável e especialista em mercado de capitais."
                        ),
                    },
                    {"role": "user", "content": prompt_chat},
                ],
            )
            texto_resposta = resposta.choices[0].message.content
            st.write(texto_resposta)
            st.session_state.historico.append(
                {"role": "assistant", "content": texto_resposta}
            )
        except Exception as e:
          st.error(f"Erro ao comunicar com a OpenAI: {e}")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #94a3b8; font-size: 12px; padding: 10px;'>
        <strong>Aviso Legal (Disclaimer):</strong> O BrokerSimples é uma ferramenta educacional. As informações não constituem recomendação direta de investimento.
    </div>
""",
    unsafe_allow_html=True,
)
