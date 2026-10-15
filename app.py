import urllib.parse
import feedparser
from openai import OpenAI
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="BrokerSimples | Assistente Financeiro Inteligente",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("### 📈 BrokerSimples - Assistente Financeiro Inteligente")

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

# Inicialização do Histórico
if "historico" not in st.session_state:
  st.session_state.historico = []

if "selected_prompt" not in st.session_state:
  st.session_state.selected_prompt = ""

# ---------------------------------------------------------
# BARRA LATERAL
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# VERIFICAÇÃO DA CHAVE DE API
# ---------------------------------------------------------
try:
  api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
  api_key = ""

if not api_key:
  st.warning(
      "⚠️ Insira a sua chave da OpenAI no ficheiro `secrets.toml` para ativar o"
      " assistente e a análise de imagens."
  )
  client = None
else:
  client = OpenAI(api_key=api_key)


# ---------------------------------------------------------
# FUNÇÃO DO RADAR DE NOTÍCIAS (EXPANDIDO PARA MAIS MATÉRIAS)
# ---------------------------------------------------------
@st.cache_data(ttl=1800)  # Atualiza a cada 30 minutos (1800s)
def carregar_radar_economico_global():
  topicos = [
      "economia global bancos centrais inflacao",
      "fed juros estados unidos mercado financeiro",
      "politica monetaria europa china investimentos",
      "crise geopolitica commodities petroleo ouro mercado b3",
  ]

  noticias = []
  links_vistos = set()

  for termo in topicos:
    try:
      termo_encoded = urllib.parse.quote(termo)
      url = f"https://news.google.com/rss/search?q={termo_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
      feed = feedparser.parse(url)

      # Pega mais matérias por tópico
      for entry in feed.entries[:8]:
        link = entry.get("link", "#")
        if link not in links_vistos:
          links_vistos.add(link)
          noticias.append({
              "titulo": entry.get("title", "Sem título"),
              "link": link,
              "fonte": entry.get("source", {}).get("title", "Google News"),
              "data": entry.get("published", ""),
          })
    except Exception:
      pass

  return noticias[:16]  # Retorna até 16 matérias ordenadas


# ---------------------------------------------------------
# CONTEÚDO PRINCIPAL DA APLICAÇÃO
# ---------------------------------------------------------
if aba_lateral == "Últimas Notícias":
  st.header("🔥 Radar de Notícias: O que está a Mover o Mercado Global & B3")
  st.caption(
      "Atualizado automaticamente a cada 30 minutos. Matérias mais recentes no"
      " topo."
  )
  st.markdown("---")

  noticias_ao_vivo = carregar_radar_economico_global()

  if noticias_ao_vivo:
    col1, col2 = st.columns(2)
    metade = len(noticias_ao_vivo) // 2

    with col1:
      st.subheader("🌐 Cenário Internacional & Bancos Centrais")
      for idx, item in enumerate(noticias_ao_vivo[:metade], 1):
        st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
        data_str = f" | {item['data']}" if item["data"] else ""
        st.caption(f"Fonte: {item['fonte']}{data_str}")
        st.divider()

    with col2:
      st.subheader("📊 Macroeconomia & Geopolítica Global")
      for idx, item in enumerate(noticias_ao_vivo[metade:], metade + 1):
        st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
        data_str = f" | {item['data']}" if item["data"] else ""
        st.caption(f"Fonte: {item['fonte']}{data_str}")
        st.divider()
  else:
    st.info(
        "A carregar notícias em tempo real... Por favor, aguarde alguns"
        " instantes."
    )

elif aba_lateral == "Recomendações de Compra":
  st.header("📈 Ações Recomendadas & Análise de Ativos")
  st.markdown(
      "Confira abaixo as principais ações recomendadas para o cenário atual,"
      " com tese de valorização, notícia motivadora, cotação aproximada e"
      " histórico de proventos:"
  )

  st.markdown("""
    | Nome da Empresa / Ativo | Risco | Tese de Investimento & Motivo | Notícia do Estímulo (Fonte) | Preço Aprox. | Últimos Dividendos |
    | :--- | :--- | :--- | :--- | :--- | :--- |
    | **Petrobras (PETR4)** | 🟡 Mod. | Produção recorde na camada pré-sal e forte geração de caixa com a cotação do Brent em alta. | Valor Econômico | R$ 56,00 | R$ 1,04 / ação |
    | **B3 S.A. (B3SA3)** | 🟢 Baixo / Mod. | Crescimento expressivo no volume financeiro diário e ampliação de contas ativas. | InfoMoney | R$ 18,50 | R$ 0,14 / ação |
    | **Itaú Unibanco (ITUB4)** | 🟢 Baixo | Margem financeira sólida e capacidade defensiva elevada em períodos de ajuste bancário. | InfoMoney | R$ 50,40 | R$ 0,31 / ação |
    | **Movida (MOVI3)** | 🔴 Alto | Crescimento expressivo no lucro líquido consolidado, superando projeções. | ADVFN | R$ 12,40 | R$ 0,10 / ação |
    | **NVIDIA (NVDA)** | 🟡 Mod. | Demanda aquecida por semicondutores e chips de inteligência artificial. | Wall Street Journal | US$ 132,00 | US$ 0,01 / ação |
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
        * **Porquê são seguras?** Operam como líderes consolidados com alta geração de caixa.
        * **Cenário Atual:** Garantem proteção patrimonial e rendimento em dividendos recorrentes.
        """)

  with col_arr:
    st.error("### ⚠️ Ações Mais Arriscadas (Alto Potencial de Valorização)")
    st.markdown("""
        * **Movida (MOVI3)**
        * **Porquê são arriscadas?** Alta alavancagem operacional e sensibilidade a ciclos econômicos.
        * **Cenário Atual:** Oferecem assimetria positiva expressiva para investidores arrojados.
        """)

  st.caption(
      "⚠️ *Aviso: As informações apresentadas possuem caráter exclusivamente"
      " educacional.*"
  )

else:
  st.title("🤖 BrokerSimples - Assistente Financeiro Inteligente")
  st.markdown(
      "Faça perguntas sobre o mercado, envie gráficos/prints para análise"
      " visual ou utilize a barra central."
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

  prompt_chat = st.chat_input(
      "Digite sua dúvida, ordem ou análise (Ex: Como está a PETR4?)..."
  )

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
                            " amigável e especialista em mercado de capitais,"
                            " criptomoedas e análise técnica de gráficos."
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
        <strong>Aviso Legal (Disclaimer):</strong> O BrokerSimples é uma ferramenta educacional e de análise baseada em Inteligência Artificial.
        As informações apresentadas não constituem recomendação direta de compra ou venda de ativos financeiros.
    </div>
    """,
    unsafe_allow_html=True,
)
