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


# --- FUNÇÃO DE BUSCA DE NOTÍCIAS REAL ---
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
  st.header("📈 Universo Geral de Ativos & Busca em Tempo Real")
  st.caption(
      "Acesse a lista completa de ativos do mercado ou pesquise qualquer outro"
      " ativo diretamente."
  )
  st.markdown("---")

  # BUSCA UNIVERSAL PARA QUALQUER ATIVO
  st.subheader("🔍 Consultar Qualquer Ativo Existente")
  ativo_pesquisado = st.text_input(
      "Digite o ticker ou nome de QUALQUER ativo (Ex: SANB11, WEGE3, AAPL,"
      " HGLG11, BTC):"
  )

  if ativo_pesquisado:
    st.markdown(f"### 🔎 Resultado para: **{ativo_pesquisado.upper()}**")
    c1, c2 = st.columns([2, 1])
    with c1:
      st.markdown(
          f"**📖 Resumo do Ativo:** Ativo pesquisado no mercado para avaliação"
          f" de oportunidade e alocação de carteira."
      )
      st.markdown(
          f"**🏛️ Contexto Político-Econômico:** Impactado pelas flutuações"
          f" recentes da taxa Selic, inflação (IPCA), decisões fiscais do"
          f" governo e cenário macroeconômico global."
      )
    with c2:
      st.markdown("**📰 Notícia Atualizada ao Vivo:**")
      noticias_busca = buscar_noticias_reais(ativo_pesquisado)
      if noticias_busca:
        for n in noticias_busca:
          st.markdown(f"📌 [{n['titulo']}]({n['link']})")
          st.caption(f"Fonte: **{n['fonte']}** | {n['data']}")
      else:
        st.info("Buscando informações no Google News...")
    st.markdown("---")

  # BASE COMPLETA ORGANIZADA POR CLASSE DE ATIVOS
  CATEGORIAS_ATIVOS = {
      "📈 Ações B3 (Setor Financeiro)": [
          {
              "nome": "Itaú Unibanco (ITUB4)",
              "risco": "Conservador",
              "resumo": "Maior banco privado do país com forte lucratividade.",
              "politica": "Protegido por altas taxas de juros e margem de crédito.",
              "busca": "Itaú ITUB4",
          },
          {
              "nome": "Banco do Brasil (BBAS3)",
              "risco": "Conservador",
              "resumo": "Líder no setor agrícola e alta distribuição de dividendos.",
              "politica": "Incentivos estatais ao agronegócio impulsionam receitas.",
              "busca": "Banco do Brasil BBAS3",
          },
          {
              "nome": "Bradesco (BBDC4)",
              "risco": "Moderado",
              "resumo": "Segundo maior banco privado em reestruturação de carteira.",
              "politica": "Sensível à inadimplência e à recuperação do crédito.",
              "busca": "Bradesco BBDC4",
          },
          {
              "nome": "Santander Brasil (SANB11)",
              "risco": "Moderado",
              "resumo": "Forte presença no varejo bancário e financiamento.",
              "politica": "Sensível a decisões do Banco Central sobre a Selic.",
              "busca": "Santander SANB11",
          },
          {
              "nome": "BTG Pactual (BPAC11)",
              "risco": "Moderado",
              "resumo": "Maior banco de investimentos da América Latina.",
              "politica": "Beneficia-se do volume de fusões e emissões na bolsa.",
              "busca": "BTG Pactual BPAC11",
          },
      ],
      "⚡ Ações B3 (Energia e Saneamento)": [
          {
              "nome": "Taesa (TAEE11)",
              "risco": "Conservador",
              "resumo": "Transmissora de energia com contratos de longo prazo.",
              "politica": "Receita indexada à inflação, imune a crises passageiras.",
              "busca": "Taesa TAEE11",
          },
          {
              "nome": "Eletrobras (ELET3)",
              "risco": "Conservador",
              "resumo": "Líder em geração e transmissão privatizada.",
              "politica": "Mudanças regulatórias no setor elétrico afetam cotações.",
              "busca": "Eletrobras ELET3",
          },
          {
              "nome": "CPFL Energia (CPFE3)",
              "risco": "Conservador",
              "resumo": "Distribuidora e geradora com altos dividendos.",
              "politica": "Estabilidade de consumo em todas as fases da economia.",
              "busca": "CPFL Energia CPFE3",
          },
          {
              "nome": "Sabesp (SBSP3)",
              "risco": "Moderado",
              "resumo": "Companhia de saneamento do estado de SP.",
              "politica": "Privatização e novos marcos regulatórios de saneamento.",
              "busca": "Sabesp SBSP3",
          },
      ],
      "🛢️ Ações B3 (Commodities e Indústria)": [
          {
              "nome": "Petrobras (PETR4)",
              "risco": "Moderado",
              "resumo": "Líder em exploração de petróleo no Pré-Sal.",
              "politica": "Influenciada por políticas de preços e cotação do Brent.",
              "busca": "Petrobras PETR4",
          },
          {
              "nome": "Vale (VALE3)",
              "risco": "Moderado",
              "resumo": "Exportadora global de minério de ferro.",
              "politica": "Depende da demanda da China e do Dólar.",
              "busca": "Vale VALE3",
          },
          {
              "nome": "Gerdau (GGBR4)",
              "risco": "Moderado",
              "resumo": "Siderúrgica com presença forte no Brasil e EUA.",
              "politica": "Impactada por investimentos em infraestrutura global.",
              "busca": "Gerdau GGBR4",
          },
          {
              "nome": "WEG (WEGE3)",
              "risco": "Moderado",
              "resumo": "Fabricante global de motores e energia renovável.",
              "politica": "Beneficiada pela transição energética e Dólar alto.",
              "busca": "WEG WEGE3",
          },
          {
              "nome": "Suzano (SUZB3)",
              "risco": "Moderado",
              "resumo": "Maior produtora mundial de celulose de eucalipto.",
              "politica": "Faturamento em Dólar protege contra inflação interna.",
              "busca": "Suzano SUZB3",
          },
      ],
      "🛍️ Ações B3 (Varejo e Consumo)": [
          {
              "nome": "Ambev (ABEV3)",
              "risco": "Conservador",
              "resumo": "Líder no mercado de bebidas e cervejas na América Latina.",
              "politica": "Consumo resiliente com forte geração de caixa.",
              "busca": "Ambev ABEV3",
          },
          {
              "nome": "Lojas Renner (LREN3)",
              "risco": "Moderado",
              "resumo": "Rede de vestuário e moda com forte presença física/digital.",
              "politica": "Sensível ao poder de compra e crédito ao consumidor.",
              "busca": "Lojas Renner LREN3",
          },
          {
              "nome": "Magazine Luiza (MGLU3)",
              "risco": "Arriscado",
              "resumo": "Varejista de eletrodomésticos e e-commerce.",
              "politica": "Reage fortemente a reduções na taxa Selic.",
              "busca": "Magazine Luiza MGLU3",
          },
          {
              "nome": "Casas Bahia (BHIA3)",
              "risco": "Arriscado",
              "resumo": "Tradicional rede de varejo em reestruturação.",
              "politica": "Depende de renegociação de dívidas e juros baixos.",
              "busca": "Casas Bahia BHIA3",
          },
      ],
      "🏢 Fundos Imobiliários (FIIs - Todas as Classes)": [
          {
              "nome": "HGLG11 - CSHG Logística",
              "risco": "Conservador",
              "resumo": "Galpões logísticos alugados para grandes empresas.",
              "politica": "Contratos atípicos de longo prazo protegem renda.",
              "busca": "Fundo HGLG11",
          },
          {
              "nome": "MXRF11 - Maxi Renda",
              "risco": "Conservador",
              "resumo": "Fundo de dívida imobiliária (CRIs).",
              "politica": "Rendimentos corrigidos pela inflação e CDI.",
              "busca": "MXRF11",
          },
          {
              "nome": "KNRI11 - Kinea Renda",
              "risco": "Conservador",
              "resumo": "Fundo híbrido de escritórios e galpões.",
              "politica": "Alta qualidade de imóveis nas capitais.",
              "busca": "Fundo KNRI11",
          },
          {
              "nome": "XPML11 - XP Malls",
              "risco": "Moderado",
              "resumo": "Participação nos principais shoppings do país.",
              "politica": "Beneficia-se das vendas no varejo e fluxo de pessoas.",
              "busca": "Fundo XPML11",
          },
          {
              "nome": "BTLG11 - BTG Logística",
              "risco": "Moderado",
              "resumo": "Galpões estratégicos nas proximidades de SP.",
              "politica": "Alta demanda por entregas rápidas do e-commerce.",
              "busca": "Fundo BTLG11",
          },
      ],
      "🌐 BDRs, Criptos & Mercado Internacional": [
          {
              "nome": "Apple (AAPL34)",
              "risco": "Moderado",
              "resumo": "Tecnologia global, iPhones e serviços.",
              "politica": "Proteção patrimonial em moeda forte (Dólar).",
              "busca": "Apple BDR AAPL34",
          },
          {
              "nome": "Microsoft (MSFT34)",
              "risco": "Moderado",
              "resumo": "Líder em softwares, nuvem e Inteligência Artificial.",
              "politica": "Pioneira na transformação digital corporativa.",
              "busca": "Microsoft BDR MSFT34",
          },
          {
              "nome": "Nvidia (NVDC34)",
              "risco": "Arriscado",
              "resumo": "Fabricante de processadores para IA.",
              "politica": "Demanda gigante por tecnologia de ponta.",
              "busca": "Nvidia BDR NVDC34",
          },
          {
              "nome": "Bitcoin (BTC)",
              "risco": "Arriscado",
              "resumo": "Principal moeda digital descentralizada.",
              "politica": "Reserva de valor imune à emissão de governos.",
              "busca": "Bitcoin criptomoeda",
          },
          {
              "nome": "Ethereum (ETH)",
              "risco": "Arriscado",
              "resumo": "Rede para contratos inteligentes e finanças digitais.",
              "politica": "Desenvolvimento tecnológico e adoção global.",
              "busca": "Ethereum criptomoeda",
          },
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
              st.markdown(f"**📖 Resumo do Ativo:** {item['resumo']}")
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
          st.markdown(f"**📖 Resumo do Ativo:** {item['resumo']}")
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
