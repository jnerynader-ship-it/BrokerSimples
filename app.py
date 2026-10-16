from datetime import datetime, timedelta
import os
import urllib.parse
import urllib.request
import feedparser
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


# --- FUNÇÃO DE BUSCA DE NOTÍCIAS CORRIGIDA COM USER-AGENT ---
@st.cache_data(ttl=300)
def buscar_noticias_reais(termo_busca):
  noticias = []
  try:
    q_encoded = urllib.parse.quote(termo_busca)
    rss_url = f"https://news.google.com/rss/search?q={q_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    req = urllib.request.Request(
        rss_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            )
        },
    )
    xml_data = urllib.request.urlopen(req, timeout=10).read()
    feed = feedparser.parse(xml_data)

    for entry in feed.entries[:3]:
      noticias.append({
          "titulo": entry.get("title", "Notícia do Mercado"),
          "link": entry.get("link", "#"),
          "fonte": entry.get("source", {}).get("title", "Imprensa Financeira"),
          "data": entry.get("published", "Hoje"),
      })
  except Exception:
    pass
  return noticias


# --- CONTEÚDO PRINCIPAL ---
if aba_lateral == "Últimas Notícias":
  st.header("🔥 Radar de Notícias Financeiras em Tempo Real")
  st.caption(
      "Acompanhe as últimas publicações do mercado organizadas por período."
  )
  st.markdown("---")

  hoje_str = datetime.now().strftime("%d/%m/%Y")
  ontem_str = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")

  tab_hoje, tab_ontem, tab_recente = st.tabs([
      f"📅 Hoje ({hoje_str}) - Últimas Horas",
      f"📅 Ontem ({ontem_str})",
      "📜 Últimos 7 Dias",
  ])

  with tab_hoje:
    st.subheader(f"⚡ Acontecimentos de Hoje ({hoje_str})")
    noticias_hoje = buscar_noticias_reais("mercado financeiro bolsa quando:1d")
    if noticias_hoje:
      for idx, item in enumerate(noticias_hoje, 1):
        st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
        st.caption(f"Fonte: **{item['fonte']}** | 🕒 {item['data']}")
        st.divider()
    else:
      st.info("A buscar notícias de hoje...")

  with tab_ontem:
    st.subheader(f"📑 Principais Notícias de Ontem ({ontem_str})")
    noticias_ontem = buscar_noticias_reais("economia ibovespa quando:2d")
    if noticias_ontem:
      for idx, item in enumerate(noticias_ontem, 1):
        st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
        st.caption(f"Fonte: **{item['fonte']}** | 🕒 {item['data']}")
        st.divider()

  with tab_recente:
    st.subheader("📚 Resumo do Mercado na Semana")
    noticias_semana = buscar_noticias_reais("acoes mercado financeiro quando:7d")
    if noticias_semana:
      for idx, item in enumerate(noticias_semana, 1):
        st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
        st.caption(f"Fonte: **{item['fonte']}** | 🕒 {item['data']}")
        st.divider()

elif aba_lateral == "Recomendações de Compra":
  st.header("📈 Universo Completo de Ativos & Análise Político-Econômica")
  st.caption(
      "Explore todas as classes de ativos existentes no mercado nacional e"
      " internacional, explicadas para leigos e validadas por notícias em"
      " tempo real."
  )
  st.markdown("---")

  # BANCO UNIVERSAL DE ATIVOS POR CATEGORIA
  CATEGORIAS_ATIVOS = {
      "📈 Ações B3 (Empresas Brasileiras)": [
          {
              "nome": "Itaú Unibanco (ITUB4)",
              "risco": "Conservador",
              "leigos": (
                  "Maior banco privado do país. Lucra alto cobrando tarifas e"
                  " emprestando com baixo risco."
              ),
              "politica": (
                  "Em cenários de juros altos ou incerteza política, os bancos"
                  " mantêm lucros bilionários repassando taxas."
              ),
              "busca": "Itaú ITUB4",
          },
          {
              "nome": "Banco do Brasil (BBAS3)",
              "risco": "Conservador",
              "leigos": (
                  "Banco estatal líder no crédito para o agronegócio"
                  " brasileiro."
              ),
              "politica": (
                  "Incentivos do governo ao agronegócio (Plano Safra)"
                  " impulsionam seus resultados e dividendos."
              ),
              "busca": "Banco do Brasil BBAS3",
          },
          {
              "nome": "Petrobras (PETR4)",
              "risco": "Moderado",
              "leigos": (
                  "Líder na extração de petróleo no Pré-Sal com baixíssimo custo"
                  " de produção."
              ),
              "politica": (
                  "Sensível a discursos sobre preços de combustíveis e conflitos"
                  " no Oriente Médio que elevam o petróleo."
              ),
              "busca": "Petrobras PETR4",
          },
          {
              "nome": "Vale (VALE3)",
              "risco": "Moderado",
              "leigos": (
                  "Uma das maiores exportadoras mundiais de minério de ferro."
              ),
              "politica": (
                  "Depende diretamente do crescimento da China e da cotação do"
                  " Dólar no mercado internacional."
              ),
              "busca": "Vale VALE3",
          },
          {
              "nome": "Magazine Luiza (MGLU3)",
              "risco": "Arriscado",
              "leigos": "Gigante do varejo de eletrodomésticos e e-commerce.",
              "politica": (
                  "Altamente dependente da taxa Selic. Juros baixos e facilidade"
                  " de crédito reaquecem suas vendas."
              ),
              "busca": "Magazine Luiza MGLU3",
          },
      ],
      "🏢 Fundos Imobiliários (FIIs - Tijolo e Papel)": [
          {
              "nome": "HGLG11 - CSHG Logística",
              "risco": "Conservador",
              "leigos": (
                  "Dono de galpões gigantes alugados para empresas de e-commerce"
                  " como Mercado Livre."
              ),
              "politica": (
                  "Imune a crises políticas por ter contratos de aluguel de"
                  " longo prazo com garantias sólidas."
              ),
              "busca": "Fundo HGLG11",
          },
          {
              "nome": "MXRF11 - Maxi Renda",
              "risco": "Conservador",
              "leigos": (
                  "Empresta dinheiro para obras do setor imobiliário e paga"
                  " rendimentos todo mês."
              ),
              "politica": (
                  "Protege o patrimônio porque seus rendimentos corrigem"
                  " automaticamente com a inflação (IPCA)."
              ),
              "busca": "MXRF11",
          },
          {
              "nome": "XPML11 - XP Malls",
              "risco": "Moderado",
              "leigos": (
                  "Dono de participações nos maiores shopping centers das"
                  " capitais."
              ),
              "politica": (
                  "Beneficia-se da recuperação do consumo das famílias e da"
                  " queda da inflação de alimentos/bens."
              ),
              "busca": "Fundo XPML11",
          },
      ],
      "🌐 BDRs & Ações Internacionais (EUA e Global)": [
          {
              "nome": "Apple (AAPL34)",
              "risco": "Moderado",
              "leigos": (
                  "Fabricante do iPhone e computadores Mac com ecossistema de"
                  " serviços global."
              ),
              "politica": (
                  "Proteção cambial: ao investir na Apple, você protege seu"
                  " dinheiro contra a desvalorização do Real."
              ),
              "busca": "Apple BDR AAPL34",
          },
          {
              "nome": "Nvidia (NVDC34)",
              "risco": "Arriscado",
              "leigos": (
                  "Líder absoluta na fabricação de chips e placas para"
                  " Inteligência Artificial."
              ),
              "politica": (
                  "Submetida a disputas tecnológicas entre EUA e China. Alto"
                  " potencial de valorização futura."
              ),
              "busca": "Nvidia BDR NVDC34",
          },
      ],
      "🪙 Criptomoedas (Ativos Digitais)": [
          {
              "nome": "Bitcoin (BTC)",
              "risco": "Arriscado",
              "leigos": (
                  "A primeira e mais valiosa moeda digital descentralizada do"
                  " mundo."
              ),
              "politica": (
                  "Usado mundialmente como reserva de valor alternativa ao"
                  " dinheiro emitido por governos com inflação."
              ),
              "busca": "Bitcoin criptomoeda",
          },
          {
              "nome": "Ethereum (ETH)",
              "risco": "Arriscado",
              "leigos": (
                  "Plataforma digital onde são construídos contratos"
                  " inteligentes e finanças descentralizadas."
              ),
              "politica": (
                  "Impactado por regulamentações de órgãos financeiros dos EUA"
                  " (SEC) e da União Europeia."
              ),
              "busca": "Ethereum criptomoeda",
          },
      ],
      "💵 Renda Fixa & Títulos Públicos": [
          {
              "nome": "Tesouro Selic / IPCA+",
              "risco": "Conservador",
              "leigos": (
                  "Emprestar dinheiro diretamente para o Governo Federal do"
                  " Brasil."
              ),
              "politica": (
                  "Opção mais segura do país. Garante rendimento acima da"
                  " inflação independente de quem ganhe as eleições."
              ),
              "busca": "Tesouro Direto Selic IPCA",
          }
      ],
  }

  tab_perfil, tab_cat = st.tabs(
      ["🎯 Filtrar por Perfil de Risco", "📂 Ver por Categoria de Ativo"]
  )

  with tab_perfil:
    perfil_escolhido = st.radio(
        "Selecione o seu perfil de investidor:",
        ["🟢 Conservador", "🟡 Moderado", "🔴 Arriscado"],
        horizontal=True,
    )

    mapa_risco = {
        "🟢 Conservador": "Conservador",
        "🟡 Moderado": "Moderado",
        "🔴 Arriscado": "Arriscado",
    }
    risco_alvo = mapa_risco[perfil_escolhido]

    for cat_nome, lista in CATEGORIAS_ATIVOS.items():
      filtrados = [item for item in lista if item["risco"] == risco_alvo]
      if filtrados:
        st.subheader(f"{cat_nome}")
        for item in filtrados:
          with st.expander(f"{item['nome']} — Perfil {item['risco']}"):
            c1, c2 = st.columns([2, 1])
            with c1:
              st.markdown(f"**📖 Para Leigos:** {item['leigos']}")
              st.markdown(
                  f"**🏛️ Contexto Político-Econômico:** {item['politica']}"
              )
            with c2:
              st.markdown("**📰 Notícia Atualizada ao Vivo:**")
              noticias = buscar_noticias_reais(item["busca"])
              if noticias:
                for n in noticias:
                  st.markdown(f"📌 [{n['titulo']}]({n['link']})")
                  st.caption(f"Fonte: **{n['fonte']}** | {n['data']}")
              else:
                st.info("A consultar Google News...")
        st.divider()

  with tab_cat:
    cat_selecionada = st.selectbox(
        "Escolha a classe de ativo:", list(CATEGORIAS_ATIVOS.keys())
    )
    for item in CATEGORIAS_ATIVOS[cat_selecionada]:
      with st.expander(f"{item['nome']} — Perfil {item['risco']}"):
        c1, c2 = st.columns([2, 1])
        with c1:
          st.markdown(f"**📖 Para Leigos:** {item['leigos']}")
          st.markdown(
              f"**🏛️ Contexto Político-Econômico:** {item['politica']}"
          )
        with c2:
          st.markdown("**📰 Notícia Atualizada ao Vivo:**")
          noticias = buscar_noticias_reais(item["busca"])
          if noticias:
            for n in noticias:
              st.markdown(f"📌 [{n['titulo']}]({n['link']})")
              st.caption(f"Fonte: **{n['fonte']}** | {n['data']}")
          else:
            st.info("A consultar Google News...")

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
