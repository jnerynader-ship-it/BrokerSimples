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
    page_title="BrokerSimples | Terminal Financeiro & Recomendação",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Logo nativa no topo da barra lateral
if os.path.exists("logo.png"):
  st.logo("logo.png", icon_image="logo.png")

# Estilização visual padrão
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.96)), 
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
st.markdown("### 📊 Visão Geral do Mercado Global e Nacional")
col1, col2, col3, col4 = st.columns(4)

try:
  ibov_val = yf.Ticker("^BVSP").history(period="1d")["Close"].iloc[-1]
  dolar_val = yf.Ticker("BRL=X").history(period="1d")["Close"].iloc[-1]
  sp_val = yf.Ticker("^GSPC").history(period="1d")["Close"].iloc[-1]
  petr_val = yf.Ticker("PETR4.SA").history(period="1d")["Close"].iloc[-1]
except Exception:
  ibov_val, dolar_val, sp_val, petr_val = (131200.0, 5.45, 5820.0, 36.80)

with col1:
  st.metric(
      label="IBOVESPA (Brasil)",
      value=f"{ibov_val:,.2f} pts".replace(",", "."),
      delta="+0.8%",
  )
with col2:
  st.metric(label="DÓLAR (USD/BRL)", value=f"R$ {dolar_val:.2f}", delta="-0.2%")
with col3:
  st.metric(
      label="S&P 500 (EUA)",
      value=f"{sp_val:,.2f} pts".replace(",", "."),
      delta="+0.5%",
  )
with col4:
  st.metric(label="PETR4 (Petróleo)", value=f"R$ {petr_val:.2f}", delta="+1.4%")

st.markdown("---")

# Estado de Sessão e Histórico
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
st.sidebar.subheader("📊 Navegação de Mercado")
aba_lateral = st.sidebar.radio(
    "Ir Para:",
    ["Chat Principal", "Últimas Notícias", "Recomendações Estratégicas"],
)

# Chave OpenAI
try:
  api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
  api_key = ""

client = OpenAI(api_key=api_key) if api_key else None


# --- FUNÇÃO DE BUSCA DE NOTÍCIAS REAL ---
@st.cache_data(ttl=600)
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
          "titulo": entry.get("title", "Notícia de Mercado"),
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
  st.caption("Acompanhe as últimas publicações do mercado global e nacional.")
  st.markdown("---")

  noticias_mercado = buscar_noticias_reais(
      "mercado financeiro bolsa ibovespa juros quando:1d"
  )
  if noticias_mercado:
    for idx, item in enumerate(noticias_mercado, 1):
      st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
      st.caption(f"Fonte: **{item['fonte']}** | 🕒 {item['data']}")
      st.divider()
  else:
    st.info("A carregar últimas notícias do mercado financeiro...")

elif aba_lateral == "Recomendações Estratégicas":
  st.header(
      "🏛️ Matriz de Recomendação de Ativos: Conexão Político-Econômica"
  )
  st.caption(
      "Teses de investimento ligando diretamente o cenário de Juros (Selic/Fed"
      " Rates), Eleições, Inflação e Geopolítica aos ativos Nacionais e"
      " Internacionais."
  )
  st.markdown("---")

  # BANCO DE DADOS ESTRATÉGICO DE RECOMENDAÇÕES (NACIONAL E INTERNACIONAL)
  MATRIZ_RECOMENDACOES = {
      "Nacionais (Brasil - B3 / Renda Fixa)": [
          {
              "ativo": "Itaú Unibanco (ITUB4)",
              "categoria": "Ação B3 — Financeiro",
              "risco": "Conservador",
              "tese": (
                  "Maior banco privado do país. Apresenta o melhor ROE do setor"
                  " com inadimplência controlada."
              ),
              "contexto": (
                  "Com a Selic em níveis elevados para conter a inflação, o"
                  " Itaú consegue repassar custos de crédito com margem"
                  " financeira sólida, sendo o porto seguro do mercado contra"
                  " ruídos fiscais."
              ),
              "busca_news": "Itaú ITUB4 banco juros",
          },
          {
              "ativo": "Banco do Brasil (BBAS3)",
              "categoria": "Ação B3 — Estatal / Agro",
              "risco": "Conservador",
              "tese": (
                  "Negociado com forte desconto frente ao valor patrimonial e"
                  " pagador de dividendos robustos."
              ),
              "contexto": (
                  "Líder no financiamento ao Agronegócio (setor fundamental"
                  " para a balança comercial e exportação). É diretamente"
                  " impactado pelos subsídios e programas governamentais do"
                  " Plano Safra."
              ),
              "busca_news": "Banco do Brasil BBAS3 dividendos",
          },
          {
              "ativo": "Taesa (TAEE11) / CPFL (CPFE3)",
              "categoria": "Ações B3 — Elétricas / Concessões",
              "risco": "Conservador",
              "tese": (
                  "Receita previsível corrigida por índices de inflação"
                  " (IPCA/IGP-M)."
              ),
              "contexto": (
                  "Atuam em setor regulado por contratos estatais de 30 anos."
                  " Blindam o patrimônio em momentos de volatilidade política e"
                  " eleições locais."
              ),
              "busca_news": "Taesa TAEE11 energia dividendo",
          },
          {
              "ativo": "Petrobras (PETR4)",
              "categoria": "Ação B3 — Petróleo / Commodities",
              "risco": "Moderado",
              "tese": (
                  "Geração de caixa extraordinária com baixíssimo custo de"
                  " extração no Pré-Sal."
              ),
              "contexto": (
                  "Totalmente exposta ao cenário político nacional (política de"
                  " dividendos e controle de combustíveis) e geopolítico"
                  " internacional (conflitos no Oriente Médio que elevam o"
                  " barril de petróleo Brent)."
              ),
              "busca_news": "Petrobras PETR4 petróleo dividendos",
          },
          {
              "ativo": "Vale (VALE3)",
              "categoria": "Ação B3 — Mineração",
              "risco": "Moderado",
              "tese": (
                  "Líder global na exportação de minério de ferro de alta"
                  " pureza."
              ),
              "contexto": (
                  "Sensível à política de estímulos econômicos do governo"
                  " chinês para o setor imobiliário e à cotação do Dólar."
                  " Protege o portfólio nacional contra desvalorizações do Real."
              ),
              "busca_news": "Vale VALE3 minério China",
          },
          {
              "ativo": "HGLG11 / MXRF11",
              "categoria": "Fundos Imobiliários (Logística e Papel)",
              "risco": "Conservador",
              "tese": (
                  "Geração de renda passiva mensal isenta de Imposto de Renda"
                  " para pessoa física."
              ),
              "contexto": (
                  "FIIs de Papel (CRIs) capturam juros e inflação elevados;"
                  " FIIs Logísticos beneficiam-se da expansão estrutural do"
                  " e-commerce no varejo nacional."
              ),
              "busca_news": "Fundo imobiliario HGLG11 MXRF11",
          },
          {
              "ativo": "Magazine Luiza (MGLU3) / Movida (MOVI3)",
              "categoria": "Ações B3 — Varejo e Consumo Ciclico",
              "risco": "Arriscado",
              "tese": (
                  "Ativos de alto beta com grande potencial de valorização em"
                  " momentos de inflexão dos juros."
              ),
              "contexto": (
                  "Sofrem em períodos de Selic alta devido ao custo da dívida."
                  " São os primeiros ativos a disparar quando o mercado passa a"
                  " precificar novos cortes nas taxas de juros."
              ),
              "busca_news": "Magazine Luiza MGLU3 juros Selic",
          },
          {
              "ativo": "Tesouro IPCA+ / Tesouro Selic",
              "categoria": "Renda Fixa Pública",
              "risco": "Conservador",
              "tese": (
                  "Garantia soberana do Governo Federal com retorno real acima"
                  " da inflação."
              ),
              "contexto": (
                  "Reflete o risco fiscal do país. Permite travar taxas reais"
                  " históricas altas em períodos de incerteza política e"
                  " orçamentária."
              ),
              "busca_news": "Tesouro Direto IPCA Selic governo",
          },
      ],
      "Internacionais (EUA / BDRs / Cripto / Global)": [
          {
              "ativo": "Microsoft (MSFT34 / MSFT)",
              "categoria": "BDR Internacional — Big Tech / Nuvem / IA",
              "risco": "Moderado",
              "tese": (
                  "Dona da estrutura Azure e parceira estratégica da OpenAI na"
                  " revolução da Inteligência Artificial."
              ),
              "contexto": (
                  "Captura o crescimento da produtividade corporativa mundial."
                  " Beneficia-se do afrouxamento monetário do Federal Reserve"
                  " (Fed) nos EUA e protege contra o risco-Brasil."
              ),
              "busca_news": "Microsoft MSFT inteligencia artificial",
          },
          {
              "ativo": "Apple (AAPL34 / AAPL)",
              "categoria": "BDR Internacional — Tecnologia / Consumo",
              "risco": "Moderado",
              "tese": (
                  "Ecossistema de hardware e serviços com altíssima fidelidade"
                  " de clientes e geração de caixa."
              ),
              "contexto": (
                  "Ativo com perfil defensivo no mercado global. Atua como"
                  " proteção cambial para o investidor brasileiro em momentos"
                  " de desvalorização do Real."
              ),
              "busca_news": "Apple AAPL acoes mercado",
          },
          {
              "ativo": "Nvidia (NVDC34 / NVDA)",
              "risco": "Arriscado",
              "categoria": "BDR Internacional — Semiconductores / IA",
              "tese": (
                  "Monopólio prático no fornecimento de processadores (GPUs)"
                  " para treinamento de redes neurais."
              ),
              "contexto": (
                  "No centro das disputas geopolíticas e de sanções comerciais"
                  " de tecnologia entre Estados Unidos e China."
              ),
              "busca_news": "Nvidia NVDA chips inteligencia artificial",
          },
          {
              "ativo": "Coca-Cola (COCA34 / KO)",
              "categoria": "BDR Internacional — Consumo Não-Cíclico",
              "risco": "Conservador",
              "tese": (
                  "Presença global com poder de precificação contra a inflação"
                  " mundial."
              ),
              "contexto": (
                  "Invariável perante crises políticas ou geoeconômicas"
                  " locais. Mantém pagamentos de dividendos crescentes há mais"
                  " de 50 anos."
              ),
              "busca_news": "Coca-Cola KO dividendos mercado",
          },
          {
              "ativo": "Bitcoin (BTC-USD / BTC)",
              "categoria": "Ativo Digital — Criptomoeda",
              "risco": "Arriscado",
              "tese": (
                  "Reserva de valor digital escassa e descentralizada com limite"
                  " de 21 milhões de moedas."
              ),
              "contexto": (
                  "Adoção por grandes fundos institucionais globais (ETFs da"
                  " BlackRock) e usado como hedge contra a impressão desenfreada"
                  " de moedas estatais e inflação global."
              ),
              "busca_news": "Bitcoin criptomoeda ETF mercado",
          },
          {
              "ativo": "Ethereum (ETH-USD / ETH)",
              "categoria": "Ativo Digital — Plataforma / DeFi",
              "risco": "Arriscado",
              "tese": (
                  "Infraestrutura de contratos inteligentes para a tokenização"
                  " de ativos reais (RWA) e finanças globais."
              ),
              "contexto": (
                  "Diretamente regulada por decisões da SEC (EUA) e com alto"
                  " potencial em ciclos de afrouxamento de liquidez global."
              ),
              "busca_news": "Ethereum cripto SEC mercado",
          },
      ],
  }

  tab_nac, tab_inter = st.tabs([
      "🇧🇷 Ativos Nacionais (Brasil)",
      "🌐 Ativos Internacionais (EUA, Global & Cripto)",
  ])

  def renderizar_matriz(lista_ativos):
    for item in lista_ativos:
      cor_tag = (
          "🟢"
          if item["risco"] == "Conservador"
          else ("🟡" if item["risco"] == "Moderado" else "🔴")
      )
      with st.expander(
          f"{cor_tag} {item['ativo']} — [{item['categoria']}] — Perfil"
          f" {item['risco']}"
      ):
        c1, c2 = st.columns([2, 1])

        with c1:
          st.markdown(f"**📖 Tese do Ativo:** {item['tese']}")
          st.markdown(
              f"**🏛️ Impacto do Cenário Político-Econômico:** {item['contexto']}"
          )

        with c2:
          st.markdown("**📰 Notícias do Ativo em Tempo Real:**")
          news = buscar_noticias_reais(item["busca_news"])
          if news:
            for n in news:
              st.markdown(f"📌 [{n['titulo']}]({n['link']})")
              st.caption(f"Fonte: **{n['fonte']}** | {n['data']}")
          else:
            st.info("A consultar últimas publicações de mercado...")

  with tab_nac:
    st.info(
        "💡 **Mercado Doméstico:** Ativos selecionados conforme o ciclo da"
        " Selic, inflação (IPCA), agronegócio e política fiscal interna."
    )
    renderizar_matriz(MATRIZ_RECOMENDACOES["Nacionais (Brasil - B3 / Renda Fixa)"])

  with tab_inter:
    st.info(
        "💡 **Mercado Global:** Ativos expostos ao Dólar, decisões do Fed"
        " (EUA), Big Techs e tecnologia descentralizada para diversificação"
        " geográfica."
    )
    renderizar_matriz(
        MATRIZ_RECOMENDACOES["Internacionais (EUA / BDRs / Cripto / Global)"]
    )

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
