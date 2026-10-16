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


# --- FUNÇÃO DE BUSCA DE NOTÍCIAS MAIS ATUAIS (CACHE DE 15 MIN) ---
@st.cache_data(ttl=900)
def buscar_noticias_especificas(termo):
  q_encoded = urllib.parse.quote(f"{termo} mercado financeiro quando:1d")
  url = f"https://news.google.com/rss/search?q={q_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
  feed = feedparser.parse(url)
  noticias = []
  for entry in feed.entries[:3]:
    noticias.append({
        "titulo": entry.get("title", "Notícia em tempo real"),
        "link": entry.get("link", "#"),
        "fonte": entry.get("source", {}).get("title", "Imprensa Financeira"),
        "data": entry.get("published", "Hoje"),
    })
  return noticias


@st.cache_data(ttl=900)
def buscar_noticias_por_filtro(filtro_tempo="when:1d"):
  queries = [
      f"ibovespa dolar eleições quando:1d",
      f"economia inflacao selic quando:1d",
      f"acoes empresas bolsa quando:1d",
  ]
  noticias = []
  links_vistos = set()
  for q in queries:
    try:
      q_encoded = urllib.parse.quote(q)
      url = f"https://news.google.com/rss/search?q={q_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
      feed = feedparser.parse(url)
      for entry in feed.entries[:8]:
        link = entry.get("link", "#")
        if link not in links_vistos:
          links_vistos.add(link)
          noticias.append({
              "titulo": entry.get("title", "Sem título"),
              "link": link,
              "fonte": entry.get("source", {}).get("title", "Veículo"),
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
      st.info("A buscar notícias de hoje...")

  with tab_ontem:
    st.subheader(f"📑 Principais Notícias de Ontem ({ontem_str})")
    noticias_ontem = buscar_noticias_por_filtro("when:2d")
    if noticias_ontem:
      for idx, item in enumerate(noticias_ontem[:10], 1):
        st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
        st.caption(f"Fonte: **{item['fonte']}** | 🕒 {item['data']}")
        st.divider()

  with tab_recente:
    st.subheader("📚 Resumo do Mercado na Semana")
    noticias_semana = buscar_noticias_por_filtro("when:7d")
    if noticias_semana:
      for idx, item in enumerate(noticias_semana[:15], 1):
        st.markdown(f"**{idx}. [{item['titulo']}]({item['link']})**")
        st.caption(f"Fonte: **{item['fonte']}** | 🕒 {item['data']}")
        st.divider()

elif aba_lateral == "Recomendações de Compra":
  st.header("📈 Catálogo de Ativos Recomendados & Contexto Político")
  st.caption(
      "Guia simplificado para todos os perfis de investidor, com notícias"
      " atualizadas a cada 15 minutos."
  )
  st.markdown("---")

  col_top1, col_top2 = st.columns([3, 1])
  with col_top1:
    st.info(
        "💡 **Como funciona:** Escolha a aba do seu perfil de risco para ver"
        " uma lista diversificada de ativos (Ações, FIIs, Renda Fixa e BDRs)."
        " Clique em qualquer ativo para ver a notícia mais recente que valida"
        " essa recomendação!"
    )
  with col_top2:
    if st.button("🔄 Atualizar Notícias Agora"):
      st.cache_data.clear()
      st.rerun()

  BANCO_COMPLETO_ATIVOS = {
      "conservador": [
          {
              "nome": "Itaú Unibanco (ITUB4)",
              "tipo": "Ação / Setor Bancário",
              "para_leigos": (
                  "É o maior banco privado do país. Ganha dinheiro cobrando"
                  " tarifas e emprestando para milhões de pessoas e empresas"
                  " com baixo risco de calote."
              ),
              "contexto_politico": (
                  "Em momentos de disputa eleitoral ou inflação alta, o Itaú é"
                  " um 'porto seguro', pois consegue repassar juros e manter"
                  " lucros bilionários."
              ),
              "busca": "Itaú ITUB4",
          },
          {
              "nome": "Banco do Brasil (BBAS3)",
              "tipo": "Ação / Estatal e Agronegócio",
              "para_leigos": (
                  "O banco mais antigo do Brasil e líder absoluto em empréstimos"
                  " para o agronegócio (fazendeiros e produtores)."
              ),
              "contexto_politico": (
                  "Mesmo em trocas de governo, o agronegócio é o setor que mais"
                  " traz dólares para o Brasil. Paga dividendos gordos e está"
                  " muito barato na bolsa."
              ),
              "busca": "Banco do Brasil BBAS3",
          },
          {
              "nome": "Taesa (TAEE11)",
              "tipo": "Ação / Energia Elétrica",
              "para_leigos": (
                  "Dona de milhares de quilômetros de torres de transmissão de"
                  " energia. Ganha dinheiro apenas por deixar a tomada do país"
                  " ligada."
              ),
              "contexto_politico": (
                  "As tarifas de energia são corrigidas pela inflação por"
                  " contratos de governo de 30 anos. Imune a crises políticas"
                  " passageiras."
              ),
              "busca": "Taesa TAEE11",
          },
          {
              "nome": "HGLG11 - CSHG Logística",
              "tipo": "Fundo Imobiliário (FII de Tijolo)",
              "para_leigos": (
                  "Fundo que compra galpões gigantescos de entregas e os aluga"
                  " para empresas como Mercado Livre e Magalu. O aluguel vira"
                  " pinga-pinga diário na sua conta."
              ),
              "contexto_politico": (
                  "O comércio online e a necessidade de estoques perto de"
                  " grandes cidades protegem os galpões de variações na economia"
                  " do governo."
              ),
              "busca": "Fundo HGLG11",
          },
          {
              "nome": "MXRF11 - Maxi Renda",
              "tipo": "Fundo Imobiliário (FII de Papel)",
              "para_leigos": (
                  "Em vez de tijolo, este fundo financia obras de construção e"
                  " recebe juros mensalmente. Custa em torno de R$ 10,00 por"
                  " cota."
              ),
              "contexto_politico": (
                  "Como a taxa de juros (Selic) e a inflação continuam altas,"
                  " este fundo paga retornos mensais isentos de Imposto de"
                  " Renda."
              ),
              "busca": "MXRF11",
          },
          {
              "nome": "Tesouro Selic / IPCA+",
              "tipo": "Renda Fixa Pública (Governo)",
              "para_leigos": (
                  "Emprestar dinheiro diretamente para o Governo Federal. É o"
                  " investimento mais seguro de todo o Brasil."
              ),
              "contexto_politico": (
                  "Diante de volatilidade em pesquisas eleitorais, o Tesouro"
                  " Direto garante rentabilidade travada acima da inflação sem"
                  " risco de bolsa."
              ),
              "busca": "Tesouro Direto Selic IPCA",
          },
      ],
      "moderado": [
          {
              "nome": "Petrobras (PETR4)",
              "tipo": "Ação / Petróleo e Energia",
              "para_leigos": (
                  "Maior empresa de combustível do Brasil. Extrai petróleo do"
                  " fundo do mar (Pré-Sal) a um custo baixíssimo."
              ),
              "contexto_politico": (
                  "Sofre grande impacto com discursos políticos sobre o preço da"
                  " gasolina e dividendos. Se o petróleo subir no exterior,"
                  " vira uma maquina de lucros."
              ),
              "busca": "Petrobras PETR4",
          },
          {
              "nome": "Vale (VALE3)",
              "tipo": "Ação / Mineração e Commodities",
              "para_leigos": (
                  "Uma das maiores produtoras de minério de ferro do planeta."
                  " Vende montanhas de ferro para a China construir prédios."
              ),
              "contexto_politico": (
                  "Muito ligada à economia chinesa e ao Dólar. Quando o dólar"
                  " sobe no Brasil, a Vale fatura mais porque vende em moeda"
                  " americana."
              ),
              "busca": "Vale VALE3",
          },
          {
              "nome": "WEG (WEGE3)",
              "tipo": "Ação / Indústria e Tecnologia",
              "para_leigos": (
                  "Fabricante de motores elétricos e equipamentos para energia"
                  " solar. Apelidada de 'Fábrica de Bilionários'."
              ),
              "contexto_politico": (
                  "Empresa global com presença nos EUA e Europa. Protege contra"
                  " crises brasileiras porque a maior parte dos seus clientes"
                  " está fora do país."
              ),
              "busca": "WEG WEGE3",
          },
          {
              "nome": "XPML11 - XP Malls",
              "tipo": "Fundo Imobiliário (FII de Shoppings)",
              "para_leigos": (
                  "Virar 'dono' de pedaços de grandes shoppings no Brasil."
                  " Ganha dinheiro com os aluguéis das lojas e com o estacionamento."
              ),
              "contexto_politico": (
                  "A queda das taxas de juros no médio prazo reaquece as compras"
                  " de fim de ano e aumenta a circulação de pessoas nos"
                  " shoppings."
              ),
              "busca": "Fundo XPML11",
          },
          {
              "nome": "Apple (AAPL34 - BDR)",
              "tipo": "BDR Internacional / Tecnologia",
              "para_leigos": (
                  "Permite investir na dona do iPhone diretamente pela Bolsa do"
                  " Brasil, pagando em Reais."
              ),
              "contexto_politico": (
                  "Protege o patrimônio em caso de desvalorização do Real frente"
                  " ao Dólar, além de acompanhar o avanço global da"
                  " Inteligência Artificial."
              ),
              "busca": "Apple BDR AAPL34",
          },
      ],
      "arriscado": [
          {
              "nome": "Magazine Luiza (MGLU3)",
              "tipo": "Ação / Varejo Digital",
              "para_leigos": (
                  "Gigante de venda de geladeiras, celulares e compras pelo"
                  " aplicativo."
              ),
              "contexto_politico": (
                  "Altamente dependente da Selic. Se os juros caírem ou o"
                  " governo liberar crédito para as famílias, a ação pode"
                  " disparar, mas oscila muito."
              ),
              "busca": "Magazine Luiza MGLU3",
          },
          {
              "nome": "Movida (MOVI3)",
              "tipo": "Ação / Aluguel de Carros",
              "para_leigos": (
                  "Aluga frotas de carros para motoristas de app e empresas,"
                  " além de vender os seminovos."
              ),
              "contexto_politico": (
                  "Como compra muitos carros financiado, precisa de juros"
                  " baixos. Se a economia crescer após as eleições, é uma das"
                  " que mais sobem."
              ),
              "busca": "Movida MOVI3",
          },
          {
              "nome": "CVC Brasil (CVCB3)",
              "tipo": "Ação / Turismo e Viagens",
              "para_leigos": (
                  "Agência de viagens que vende pacotes de turismo e passagens"
                  " aéreas."
              ),
              "contexto_politico": (
                  "Sensível ao Dólar e ao poder de compra das famílias. Se a"
                  " inflação der trégua e as passagens caírem, a empresa tende"
                  " a se recuperar."
              ),
              "busca": "CVC Brasil CVCB3",
          },
          {
              "nome": "Azul Linhas Aéreas (AZUL4)",
              "tipo": "Ação / Aviação Comercial",
              "para_leigos": (
                  "Empresa de aviação responsável por voos regionais e"
                  " internacionais."
              ),
              "contexto_politico": (
                  "Sofre muito com o preço do combustível de aviação (atrelado"
                  " ao petróleo) e com a cotação do Dólar. Risco alto, mas"
                  " grande potencial em reestruturações."
              ),
              "busca": "Azul Linhas Aéreas AZUL4",
          },
      ],
  }

  tab_c, tab_m, tab_a = st.tabs([
      "🛡️ Bloco Conservador (Segurança & Renda)",
      "⚖️ Bloco Moderado (Crescimento & Equilíbrio)",
      "🚀 Bloco Arriscado (Potencial & Volatilidade)",
  ])

  def exibir_lista_interativa(lista_ativos, emoji):
    for item in lista_ativos:
      with st.expander(f"{emoji} {item['nome']} — [{item['tipo']}]"):
        c1, c2 = st.columns([2, 1])

        with c1:
          st.markdown(f"**💡 Explication para Leigos:** {item['para_leigos']}")
          st.markdown(
              f"**🏛️ Contexto Político-Econômico:** {item['contexto_politico']}"
          )

        with c2:
          st.markdown("**📰 Notícia Mais Recente (Google News):**")
          noticias = buscar_noticias_especificas(item["busca"])
          if noticias:
            for n in noticias:
              st.markdown(f"📌 [{n['titulo']}]({n['link']})")
              st.caption(f"Fonte: **{n['fonte']}** | {n['data']}")
          else:
            st.caption("A buscar atualizações da imprensa...")

  with tab_c:
    st.success(
        "### 🛡️ Para quem busca estabilidade, dividendos e baixo risco"
    )
    exibir_lista_interativa(BANCO_COMPLETO_ATIVOS["conservador"], "🟢")

  with tab_m:
    st.warning(
        "### ⚖️ Para quem quer multiplicar patrimônio e aceita variações"
    )
    exibir_lista_interativa(BANCO_COMPLETO_ATIVOS["moderado"], "🟡")

  with tab_a:
    st.error(
        "### 🚀 Para investidores audaciosos buscando altas valorizações"
    )
    exibir_lista_interativa(BANCO_COMPLETO_ATIVOS["arriscado"], "🔴")

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
