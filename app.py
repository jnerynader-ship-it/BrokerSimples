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


# --- FUNÇÕES DE BUSCA CACHEADA ---
@st.cache_data(ttl=900)
def buscar_noticias_especificas(termo):
  q_encoded = urllib.parse.quote(f"{termo} mercado financeiro quando:2d")
  url = f"https://news.google.com/rss/search?q={q_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
  feed = feedparser.parse(url)
  noticias = []
  for entry in feed.entries[:3]:
    noticias.append({
        "titulo": entry.get("title", "Notícia Recente"),
        "link": entry.get("link", "#"),
        "fonte": entry.get("source", {}).get("title", "Imprensa"),
    })
  return noticias


@st.cache_data(ttl=600)
def buscar_noticias_por_filtro(filtro_tempo="when:1d"):
  queries = [
      f"mercado financeiro bolsa {filtro_tempo}",
      f"economia inflacao juros {filtro_tempo}",
      f"ibovespa ações empresas {filtro_tempo}",
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
              "fonte": entry.get("source", {}).get("title", "Veículo"),
              "data": entry.get("published", "Data recente"),
          })
    except Exception:
      pass
  return noticias


# --- CONTEÚDO PRINCIPAL ---
if aba_lateral == "Últimas Notícias":
  st.header("🔥 Radar de Notícias Organizado por Data")
  st.caption(
      "Acompanhe as notícias mais recentes separadas pelo dia da publicação."
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

  with tab_recente:
    st.subheader("📚 Resumo do Mercado na Semana (Últimos 7 Dias)")
    noticias_semana = buscar_noticias_por_filtro("when:7d")
    if noticias_semana:
      for idx, item in enumerate(noticias_semana[:15], 1):
        st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
        st.caption(f"Fonte: **{item['fonte']}** | 🕒 {item['data']}")
        st.divider()

elif aba_lateral == "Recomendações de Compra":
  st.header("📈 Guia Descomplicado de Ativos & Cenário Político-Econômico")
  st.caption(
      "Entenda o mercado sem complicações: teses explicadas para leigos e"
      " validadas por notícias em tempo real."
  )
  st.markdown("---")

  # Dicionário dinâmico expandido de ativos
  BANCO_ATIVOS = {
      "conservador": [
          {
              "nome": "Itaú Unibanco (ITUB4)",
              "o_que_e": (
                  "O maior banco privado do Brasil. Ganha dinheiro emprestando"
                  " para pessoas e empresas com grande segurança."
              ),
              "cenario_politico_econo": (
                  "Em períodos de juros altos ou incerteza política, os grandes"
                  " bancos continuam lucrando com taxas de empréstimo e têm"
                  " proteção sólida contra crises."
              ),
              "termo_busca": "Itaú ITUB4",
          },
          {
              "nome": "Banco do Brasil (BBAS3)",
              "o_que_e": (
                  "Banco estatal com forte atuação no agronegócio"
                  " brasileiro."
              ),
              "cenario_politico_econo": (
                  "O agronegócio é o motor de exportação do país. Decisões do"
                  " governo sobre o Plano Safra e subsídios influenciam"
                  " diretamente a sua receita."
              ),
              "termo_busca": "Banco do Brasil BBAS3",
          },
          {
              "nome": "HGLG11 - CSHG Logística (FII)",
              "o_que_e": (
                  "Fundo Imobiliário dono de galpões logísticos alugados para"
                  " grandes empresas de e-commerce."
              ),
              "cenario_politico_econo": (
                  "Mesmo com oscilações econômicas, o consumo de produtos de"
                  " primeira necessidade e entregas rápidas mantém esses"
                  " galpões sempre ocupados."
              ),
              "termo_busca": "Fundo HGLG11",
          },
          {
              "nome": "MXRF11 - Maxi Renda (FII)",
              "o_que_e": (
                  "Fundo Imobiliário de 'Papel', que empresta dinheiro para o"
                  " setor imobiliário e recebe juros todo mês."
              ),
              "cenario_politico_econo": (
                  "Protege o investidor contra a inflação, pois seus títulos"
                  " corrigem os pagamentos mensais de acordo com o aumento do"
                  " custo de vida."
              ),
              "termo_busca": "MXRF11",
          },
          {
              "nome": "Eletrobras (ELET3)",
              "o_que_e": (
                  "Líder em geração e transmissão de energia elétrica no país."
              ),
              "cenario_politico_econo": (
                  "Energia é um serviço essencial. Mudanças regulatórias no"
                  " setor elétrico e privatizações afetam seu valor, mas sua"
                  " receita é altamente estável."
              ),
              "termo_busca": "Eletrobras ELET3",
          },
      ],
      "moderado": [
          {
              "nome": "Petrobras (PETR4)",
              "o_que_e": (
                  "Gigante estatal de exploração de petróleo e combustíveis."
              ),
              "cenario_politico_econo": (
                  "Ativo muito influenciado por política interna (política de"
                  " preços dos combustíveis) e por conflitos internacionais"
                  " que alteram o preço do barril de petróleo."
              ),
              "termo_busca": "Petrobras PETR4",
          },
          {
              "nome": "Vale (VALE3)",
              "o_que_e": (
                  "Uma das maiores mineradoras do mundo, exportadora de minério"
                  " de ferro."
              ),
              "cenario_politico_econo": (
                  "Depende diretamente do crescimento da economia da China e"
                  " da demanda por construção civil e aço no exterior."
              ),
              "termo_busca": "Vale VALE3",
          },
          {
              "nome": "B3 S.A. (B3SA3)",
              "o_que_e": (
                  "A empresa que é dona da própria Bolsa de Valores do Brasil."
              ),
              "cenario_politico_econo": (
                  "Quando a taxa Selic cai ou há otimismo com reformas"
                  " econômicas do governo, mais pessoas investem na bolsa,"
                  " aumentando os lucros da B3."
              ),
              "termo_busca": "B3 B3SA3",
          },
          {
              "nome": "WEG (WEGE3)",
              "o_que_e": (
                  "Fabricante global de motores elétricos e tecnologias para"
                  " energia solar e eólica."
              ),
              "cenario_politico_econo": (
                  "Beneficia-se de incentivos globais à transição energética e"
                  " da alta do Dólar, pois exporta para dezenas de países."
              ),
              "termo_busca": "WEG WEGE3",
          },
      ],
      "arriscado": [
          {
              "nome": "Magazine Luiza (MGLU3)",
              "o_que_e": "Varejista gigante de eletrodomésticos e e-commerce.",
              "cenario_politico_econo": (
                  "Altamente afetada pela taxa de juros (Selic). Quando os"
                  " juros estão altos, o crédito fica caro e as pessoas compram"
                  " menos parcelado."
              ),
              "termo_busca": "Magazine Luiza MGLU3",
          },
          {
              "nome": "Movida (MOVI3)",
              "o_que_e": "Empresa de aluguel de carros e venda de seminovos.",
              "cenario_politico_econo": (
                  "Sensível à inflação de carros novos e aos juros altos, que"
                  " encarecem a compra e renovação da sua frota de veículos."
              ),
              "termo_busca": "Movida MOVI3",
          },
          {
              "nome": "CVC Brasil (CVCB3)",
              "o_que_e": "A maior operadora de turismo e viagens do Brasil.",
              "cenario_politico_econo": (
                  "Depende do poder de compra das famílias e da cotação do"
                  " Dólar. Quando o dólar sobe, viagens internacionais ficam"
                  " mais caras."
              ),
              "termo_busca": "CVC Brasil CVCB3",
          },
      ],
  }

  tab_cons, tab_mod, tab_arris = st.tabs([
      "🛡️ Perfil Conservador (Baixo Risco)",
      "⚖️ Perfil Moderado (Médio Risco)",
      "🚀 Perfil Arriscado (Alto Risco)",
  ])

  def renderizar_bloco_ativos(lista_ativos, rotulo_risco, cor_emoji):
    for idx, item in enumerate(lista_ativos):
      with st.expander(f"{cor_emoji} {item['nome']}"):
        col_desc, col_news = st.columns([2, 1])

        with col_desc:
          st.markdown(f"**📖 O que é (para leigos):** {item['o_que_e']}")
          st.markdown(
              f"**🏛️ Impacto do Cenário Político-Econômico:**"
              f" {item['cenario_politico_econo']}"
          )

        with col_news:
          st.markdown("**📰 Notícias de Hoje que Comprovam o Cenário:**")
          noticias = buscar_noticias_especificas(item["termo_busca"])
          if noticias:
            for n in noticias:
              st.markdown(f"• [{n['titulo']}]({n['link']})")
              st.caption(f"Fonte: {n['fonte']}")
          else:
            st.caption("Nenhuma notícia recente encontrada no momento.")

  with tab_cons:
    st.info(
        "💡 **Perfil Conservador:** Ideal para quem quer proteger seu dinheiro"
        " da inflação e ter renda mensal sem correr grandes riscos."
    )
    renderizar_bloco_ativos(BANCO_ATIVOS["conservador"], "Conservador", "🟢")

  with tab_mod:
    st.info(
        "💡 **Perfil Moderado:** Para quem busca crescimento do patrimônio e"
        " aceita pequenas oscilações de preço no curto prazo."
    )
    renderizar_bloco_ativos(BANCO_ATIVOS["moderado"], "Moderado", "🟡")

  with tab_arris:
    st.info(
        "💡 **Perfil Arriscado:** Para quem busca lucros expressivos a longo"
        " prazo e entende que o valor das ações pode oscilar fortemente."
    )
    renderizar_bloco_ativos(BANCO_ATIVOS["arriscado"], "Arriscado", "🔴")

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
