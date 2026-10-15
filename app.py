from datetime import datetime, timedelta
import urllib.parse
import feedparser
from openai import OpenAI
import streamlit as st
import yfinance as yf

# Configuração inicial
st.set_page_config(
    page_title="BrokerSimples | Assistente Financeiro Inteligente",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("### 📈 BrokerSimples - Assistente Financeiro Inteligente")

# Estilização do app
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
  ibov_val, dolar_val, sp_val, petr_val = (128450.0, 4.95, 5120.0, 38.10)

with col1:
  st.metric(
      label="IBOVESPA",
      value=f"{ibov_val:,.2f} pts".replace(",", "."),
      delta="+1.2%",
  )
with col2:
  st.metric(label="DÓLAR (USD/BRL)", value=f"R$ {dolar_val:.2f}", delta="-0.3%")
with col3:
  st.metric(
      label="S&P 500",
      value=f"{sp_val:,.2f} pts".replace(",", "."),
      delta="+0.8%",
  )
with col4:
  st.metric(label="PETR4", value=f"R$ {petr_val:.2f}", delta="+2.1%")

st.markdown("---")

# Inicialização do Histórico e Estado de Conversa
if "historico" not in st.session_state:
  st.session_state.historico = []

if "selected_prompt" not in st.session_state:
  st.session_state.selected_prompt = ""

# --- BARRA LATERAL ---
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
st.sidebar.subheader("📰 Mercado & Ativos")
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


# --- FUNÇÃO DE BUSCA POR DATA / FILTRO RIGOROSO ---
@st.cache_data(ttl=600)  # Atualiza a cada 10 minutos
def buscar_noticias_por_filtro(filtro_tempo="when:1d"):
  queries = [
      f"mercado financeiro bolsa {filtro_tempo}",
      f"economia inflacao juros {filtro_tempo}",
      f"ibovespa ações empresas {filtro_tempo}",
      f"fed banco central dolar {filtro_tempo}",
  ]

  noticias = []
  links_vistos = set()

  for q in queries:
    try:
      q_encoded = urllib.parse.quote(q)
      url = f"https://news.google.com/rss/search?q={q_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
      feed = feedparser.parse(url)

      for entry in feed.entries[:10]:
        link = entry.get("link", "#")
        if link not in links_vistos:
          links_vistos.add(link)
          noticias.append({
              "titulo": entry.get("title", "Sem título"),
              "link": link,
              "fonte": entry.get("source", {}).get("title", "Veículo de Notícias"),
              "data": entry.get("published", "Data recente"),
          })
    except Exception:
      pass

  return noticias


# --- CONTEÚDO PRINCIPAL ---
if aba_lateral == "Últimas Notícias":
  st.header("🔥 Radar de Notícias Organizado por Data")
  st.caption(
      "Acompanhe as notícias mais recentes separadas exatamente pelo dia da"
      " publicação."
  )
  st.markdown("---")

  # Datas dinâmicas para os nomes das abas
  hoje_str = datetime.now().strftime("%d/%m/%Y")
  ontem_str = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")

  tab_hoje, tab_ontem, tab_recente = st.tabs([
      f"📅 Hoje ({hoje_str}) - Tempo Real",
      f"📅 Ontem ({ontem_str})",
      "📜 Últimos 7 Dias",
  ])

  with tab_hoje:
    st.subheader(f"⚡ Acontecimentos de Hoje ({hoje_str})")
    noticias_hoje = buscar_noticias_por_filtro("when:12h")

    if noticias_hoje:
      col1, col2 = st.columns(2)
      metade = len(noticias_hoje) // 2

      with col1:
        for idx, item in enumerate(noticias_hoje[:metade], 1):
          st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
          st.caption(f"Fonte: **{item['fonte']}** | 🕒 {item['data']}")
          st.divider()

      with col2:
        for idx, item in enumerate(noticias_hoje[metade:], metade + 1):
          st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
          st.caption(f"Fonte: **{item['fonte']}** | 🕒 {item['data']}")
          st.divider()
    else:
      st.info("Buscando notícias publicadas hoje...")

  with tab_ontem:
    st.subheader(f"📑 Principais Notícias de Ontem ({ontem_str})")
    noticias_ontem = buscar_noticias_por_filtro("when:2d")

    if noticias_ontem:
      for idx, item in enumerate(noticias_ontem[:10], 1):
        st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
        st.caption(f"Fonte: **{item['fonte']}** | 🕒 {item['data']}")
        st.divider()
    else:
      st.info("Buscando registros do dia anterior...")

  with tab_recente:
    st.subheader("📚 Resumo do Mercado na Semana (Últimos 7 Dias)")
    noticias_semana = buscar_noticias_por_filtro("when:7d")

    if noticias_semana:
      for idx, item in enumerate(noticias_semana[:15], 1):
        st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
        st.caption(f"Fonte: **{item['fonte']}** | 🕒 {item['data']}")
        st.divider()
    else:
      st.info("Buscando histórico da semana...")

elif aba_lateral == "Recomendações de Compra":
  st.header("📈 Ações Recomendadas & Análise de Ativos")
  st.markdown(
      "Confira abaixo as principais ações recomendadas para o cenário atual:"
  )

  st.markdown("""
    | Nome da Empresa / Ativo | Risco | Tese de Investimento & Motivo | Notícia do Estímulo (Fonte) | Preço Aprox. | Últimos Dividendos |
    | :--- | :--- | :--- | :--- | :--- | :--- |
    | **Petrobras (PETR4)** | 🟡 Mod. | Produção recorde na camada pré-sal e forte geração de caixa. | Valor Econômico | R$ 56,00 | R$ 1,04 / ação |
    | **B3 S.A. (B3SA3)** | 🟢 Baixo / Mod. | Crescimento no volume financeiro diário e contas ativas. | InfoMoney | R$ 18,50 | R$ 0,14 / ação |
    | **Itaú Unibanco (ITUB4)** | 🟢 Baixo | Margem financeira sólida e capacidade defensiva elevada. | InfoMoney | R$ 50,40 | R$ 0,31 / ação |
    """)

  st.markdown("---")
  st.subheader(
      "🛡️ Análise do Cenário Global: Ativos Mais Seguros vs. Mais Arriscados"
  )

  col_seg, col_arr = st.columns(2)

  with col_seg:
    st.success("### 🛡️ Ações Mais Seguras (Resilientes)")
    st.markdown("""
        * **Itaú Unibanco (ITUB4) e B3 (B3SA3)**
        * Líderes consolidados com alta geração de caixa e dividendos recorrentes.
        """)

  with col_arr:
    st.error("### ⚠️ Ações Mais Arriscadas (Alto Potencial)")
    st.markdown("""
        * **Movida (MOVI3)**
        * Alta alavancagem e forte sensibilidade aos ciclos de juros.
        """)

else:
  st.title("🤖 BrokerSimples - Assistente Financeiro Inteligente")
  st.markdown(
      "Faça perguntas sobre o mercado ou peça análises ao assistente."
  )

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
