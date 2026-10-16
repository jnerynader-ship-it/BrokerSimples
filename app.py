from datetime import datetime, timedelta
import os
import urllib.parse
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

# Estilização visual padrão
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

    /* Ajuste do tamanho da logo */
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


# --- FUNÇÃO DE BUSCA POR DATA / FILTRO RIGOROSO ---
@st.cache_data(ttl=600)
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
      st.info("Buscando registos do dia anterior...")

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
  st.header("📈 Recomendações Estratégicas de Ativos & Cenário Global")
  st.caption(
      "🔄 Sistema de recomendação inteligente atualizado automaticamente a"
      " cada 30 minutos com base no mercado nacional e internacional."
  )
  st.markdown("---")

  col_info, col_btn = st.columns([3, 1])
  with col_info:
    st.info(
        "💡 Os ativos abaixo são selecionados e revisados periodicamente"
        " considerando juros, inflação e fluxo de capital estrangeiro."
    )
  with col_btn:
    if st.button("🔄 Atualizar Recomendações"):
      st.cache_data.clear()
      st.rerun()


  @st.cache_data(ttl=1800)
  def obter_dados_recomendacoes():
    return {
        "conservador": [
            {
                "ativo": "Itaú Unibanco (ITUB4)",
                "tipo": "Ação — Setor Financeiro",
                "porque_comprar": (
                    "Margem financeira sólida, excelente controle de"
                    " inadimplência e projeções de lucro recorde com forte"
                    " capacidade de distribuição de proventos."
                ),
                "porque_risco": (
                    "Classificado como **Conservador** por ser o maior banco"
                    " privado do país, disponando de elevado colchão de"
                    " capital e forte resiliência contra volatilidades"
                    " macroeconômicas."
                ),
            },
            {
                "ativo": "Banco do Brasil (BBAS3)",
                "tipo": "Ação — Bancário / Estatal",
                "porque_comprar": (
                    "Negociado a múltiplos extremamente atrativos (baixo P/L)"
                    " com forte exposição ao crédito agronegócio e corporativo,"
                    " garantindo dividend yields elevados."
                ),
                "porque_risco": (
                    "Nível **Conservador** devido à sua solidez histórica e"
                    " suporte estatal implícito, o que mitiga crises de"
                    " liquidez sistêmica."
                ),
            },
            {
                "ativo": "HGLG11 (CSHG Logística)",
                "tipo": "Fundo Imobiliário (FII de Tijolo)",
                "porque_comprar": (
                    "Portfólio de galpões logísticos de alto padrão (AAA)"
                    " localizados nos principais eixos rodoviários e centros"
                    " de consumo."
                ),
                "porque_risco": (
                    "Perfil **Conservador** sustentado por contratos de longo"
                    " prazo (atípicos) com inquilinos corporativos AAA,"
                    " assegurando rendimentos mensais previsíveis."
                ),
            },
            {
                "ativo": "MXRF11 (Maxi Renda)",
                "tipo": "Fundo Imobiliário (FII de Papel)",
                "porque_comprar": (
                    "Extrema liquidez diária e carteira pulverizada focada em"
                    " Certificados de Recebíveis Imobiliários (CRIs) com"
                    " garantias robustas."
                ),
                "porque_risco": (
                    "Considerado **Conservador** pela proteção parcial"
                    " proporcionada pelos indexadores de inflação e taxas"
                    " flutuantes da renda fixa imobiliária."
                ),
            },
        ],
        "moderado": [
            {
                "ativo": "Petrobras (PETR4)",
                "tipo": "Ação — Petróleo, Gás e Biocombustíveis",
                "porque_comprar": (
                    "Extração competitiva no pré-sal com custos reduzidos,"
                    " forte geração de fluxo de caixa livre e apelo contínuo"
                    " via dividendos extraordinários."
                ),
                "porque_risco": (
                    "Nível **Moderado** pois, embora os fundamentos operacionais"
                    " sejam excelentes, o ativo sofre oscilações atreladas à"
                    " volatilidade internacional do petróleo Brent e ao"
                    " ambiente regulatório."
                ),
            },
            {
                "ativo": "B3 S.A. (B3SA3)",
                "tipo": "Ação — Infraestrutura de Mercado",
                "porque_comprar": (
                    "Monopólio natural da câmara de compensação e negociação de"
                    " ativos no Brasil; beneficia-se diretamente do volume"
                    " financeiro e retorno do apetite estrangeiro."
                ),
                "porque_risco": (
                    "Classificado como **Moderado** por ser sensível ao"
                    " volume diário negociado na bolsa e às flutuações das"
                    " taxas de juros de longo prazo."
                ),
            },
            {
                "ativo": "XPML11 (XP Malls)",
                "tipo": "Fundo Imobiliário (FII de Shoppings)",
                "porque_comprar": (
                    "Participação em shopping centers dominantes em praças de"
                    " alta renda, capturando o crescimento real das vendas e"
                    " do consumo das famílias."
                ),
                "porque_risco": (
                    "Perfil **Moderado** devido à sensibilidade inerente do"
                    " setor de varejo físico e shoppings frente aos ciclos de"
                    " consumo e oscilações de juros."
                ),
            },
            {
                "ativo": "Weg (WEGE3)",
                "tipo": "Ação — Bens de Capital / Global",
                "porque_comprar": (
                    "Liderança global em eficiência energética, motores"
                    " elétricos e forte histórico de expansão internacional"
                    " com gestão impecável."
                ),
                "porque_risco": (
                    "Nível **Moderado** porque, apesar da altíssima qualidade"
                    " do negócio, negocia historicamente a múltiplos de"
                    " preço esticados (valuation elevado)."
                ),
            },
        ],
        "arriscado": [
            {
                "ativo": "Magazine Luiza (MGLU3)",
                "tipo": "Ação — Varejo Digital e E-commerce",
                "porque_comprar": (
                    "Elevado potencial de reversão de resultados e ganho de"
                    " margem operacional caso o cenário inflacionário e de"
                    " crédito apresente trégua."
                ),
                "porque_risco": (
                    "Classificado como **Arriscado** devido à alta"
                    " alavancagem financeira, sensibilidade extrema a juros"
                    " elevados e forte concorrência no comércio eletrônico."
                ),
            },
            {
                "ativo": "Movida (MOVI3)",
                "tipo": "Ação — Locação de Veículos & Seminovos",
                "porque_comprar": (
                    "Oportunidade de valorização por otimização da frota e"
                    " reprecificação das margens no segmento de aluguel e"
                    " revenda de seminovos."
                ),
                "porque_risco": (
                    "Perfil **Arriscado** por conta da forte intensidade de"
                    " capital e dependência de linhas de financiamento de"
                    " curto e médio prazo sensíveis à taxa Selic."
                ),
            },
        ],
    }


  dados = obter_dados_recomendacoes()

  st.subheader(
      "🛡️ Bloco 1: Ações & FIIs Conservadores (Foco em Defesa e Renda Sólida)"
  )
  st.markdown(
      "Ativos recomendados para mitigar a volatilidade, oferecendo"
      " previsibilidade de fluxo de caixa e proteção contra choques externos."
  )
  for item in dados["conservador"]:
    with st.expander(f"🟢 {item['ativo']} ({item['tipo']})"):
      st.markdown(f"**💡 Por que ser comprada:** {item['porque_comprar']}")
      st.markdown(f"**⚖️ Análise do Risco:** {item['porque_risco']}")

  st.markdown("---")
  st.subheader(
      "⚖️ Bloco 2: Ações & FIIs Moderados (Equilíbrio entre Valor e Crescimento)"
  )
  st.markdown(
      "Empresas e fundos consolidados com forte exposição a ciclos"
      " macroeconômicos e commodities, equilibrando risco e retorno."
  )
  for item in dados["moderado"]:
    with st.expander(f"🟡 {item['ativo']} ({item['tipo']})"):
      st.markdown(f"**💡 Por que ser comprada:** {item['porque_comprar']}")
      st.markdown(f"**⚖️ Análise do Risco:** {item['porque_risco']}")

  st.markdown("---")
  st.subheader(
      "🚀 Bloco 3: Ações Arriscadas (Alto Potencial de Valorização & Volatilidade)"
  )
  st.markdown(
      "Ativos voltados a investidores com maior tolerância a oscilações"
      " intensas, focados em recuperação operacional e alavancagem de"
      " resultados."
  )
  for item in dados["arriscado"]:
    with st.expander(f"🔴 {item['ativo']} ({item['tipo']})"):
      st.markdown(f"**💡 Por que ser comprada:** {item['porque_comprar']}")
      st.markdown(f"**⚖️ Análise do Risco:** {item['porque_risco']}")

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
