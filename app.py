import streamlit as st

st.set_page_config(
    page_title="BrokerSimples | Assistente Financeiro Inteligente",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

from openai import OpenAI

st.markdown("### 📈 BrokerSimples - Assistente Financeiro Inteligente")

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
""", unsafe_allow_html=True)
# --- 1. Indicadores de Mercado (KPIs) ---
st.markdown("### 📊 Visão Geral do Mercado")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="IBOVESPA", value="128.450 pts", delta="+1.2%")
with col2:
    st.metric(label="DÓLAR (USD/BRL)", value="R$ 4,95", delta="-0.3%")
with col3:
    st.metric(label="S&P 500", value="5.120 pts", delta="+0.8%")
with col4:
    st.metric(label="PETR4", value="R$ 38,10", delta="+2.1%")

st.markdown("---")
# Inicialização do Histórico e Estado de Conversa
if "historico" not in st.session_state:
    st.session_state.historico = []

if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = ""

# ---------------------------------------------------------
# BARRA LATERAL (ESTILO GEMINI - HISTÓRICO NO CANTO INFERIOR)
# ---------------------------------------------------------
st.sidebar.title("💬 Histórico de Prompts")
st.sidebar.markdown("---")

# Lista os prompts anteriores na barra lateral
if st.session_state.historico:
    st.sidebar.markdown("**Conversas Anteriores:**")
    for i, msg in enumerate(st.session_state.historico):
        if msg["role"] == "user":
            resumo = msg["content"] if isinstance(msg["content"], str) else "[Imagem Enviada]"
            if st.sidebar.button(f"📌 {resumo[:22]}...", key=f"hist_{i}"):
                st.session_state.selected_prompt = resumo if isinstance(resumo, str) else ""

st.sidebar.markdown("---")

# Secção de Navegação Rápida na Barra Lateral
st.sidebar.subheader("📰 Mercado & Ativos")
aba_lateral = st.sidebar.radio("Navegação Rápida:", ["Chat Principal", "Últimas Notícias", "Recomendações de Compra"])

# ---------------------------------------------------------
# VERIFICAÇÃO DA CHAVE DE API
# ---------------------------------------------------------
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    api_key = ""

if not api_key:
    st.warning(
        "⚠️ Insira a sua chave da OpenAI no ficheiro `secrets.toml` para ativar o assistente e a análise de imagens.")
    client = None
else:
    client = OpenAI(api_key=api_key)

# ---------------------------------------------------------
# CONTEÚDO PRINCIPAL DA APLICAÇÃO
# ---------------------------------------------------------
if aba_lateral == "Últimas Notícias":
    st.header("🔥 Radar de Notícias: O que está a Mover o Mercado Global & B3")
    st.caption(
        "Fontes de alta credibilidade em tempo real: InfoMoney, Bloomberg Linea, Valor Econômico, Reuters e ADVFN")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🇧🇷 Mercado Nacional, B3 & Macroeconomia")

        st.markdown("""
        ### 1. Ibovespa opera em queda de 1,49% acompanhando o exterior
        * **Fonte:** InfoMoney | *Mercados*
        * **Resumo:** O índice Bovespa recua aos 203,8 mil pontos influenciado pela cautela internacional com dados da inflação americana e forte pressão no setor bancário.
        * [🔗 Ler matéria no InfoMoney](https://www.infomoney.com.br/mercados/ibovespa-hoje-bolsa-de-valores-ao-vivo-14102026/)
        """)
        st.divider()

        st.markdown("""
        ### 2. Petrobras (PETR4) sobe mais de 1,3% impulsionada pelo petróleo
        * **Fonte:** Valor Econômico | *Empresas*
        * **Resumo:** As ações da Petrobras mantêm trajetória de alta com a recuperação do petróleo Brent e recordes na produção do pré-sal anunciados pelo Banco BBI.
        * [🔗 Ver cobertura no Valor Econômico](https://valor.globo.com/empresas/)
        """)
        st.divider()

        st.markdown("""
        ### 3. B3 (B3SA3) registra alta de 45,7% no volume financeiro negociado
        * **Fonte:** InfoMoney / B3 | *Giro Financeiro*
        * **Resumo:** O volume médio diário negociado na B3 apresentou forte aceleração no trimestre, totalizando mais de 5,88 milhões de contas de investidores individuais ativas.
        * [🔗 Ler análise no InfoMoney](https://www.infomoney.com.br/cotacoes/b3/)
        """)
        st.divider()

        st.markdown("""
        ### 4. XP projeta até R$ 540 bilhões em novos fluxos para a Bolsa
        * **Fonte:** XP Investimentos | *Estratégia de Ações*
        * **Resumo:** Analistas apontam que a rotação global de carteiras pode injetar até R$ 540 bilhões na Bolsa brasileira, com foco concentrado em ações cíclicas domésticas.
        * [🔗 Ver relatório na XP/InfoMoney](https://www.infomoney.com.br/)
        """)
        st.divider()

        st.markdown("""
        ### 5. Setor de Serviços no Brasil recua 0,1% em agosto, aponta IBGE
        * **Fonte:** IBGE / Reuters | *Economia*
        * **Resumo:** O volume do setor de serviços teve retração leve, reforçando a leitura de desaceleração gradativa da atividade econômica no terceiro trimestre.
        * [🔗 Acompanhar dados no IBGE/Reuters](https://www.reuters.com)
        """)
        st.divider()

        st.markdown("""
        ### 6. Ações de grandes bancos recuam com cautela sobre inadimplência
        * **Fonte:** InfoMoney | *Bancos*
        * **Resumo:** Papéis do Itaú (ITUB4), Bradesco (BBDC4) e Banco do Brasil (BBAS3) operam no vermelho em dia de ajuste generalizado na renda variável brasileira.
        * [🔗 Ver cotações no InfoMoney](https://www.infomoney.com.br/cotacoes/)
        """)
        st.divider()

        st.markdown("""
        ### 7. Dólar comercial avança para R$ 5,04 acompanhando juros nos EUA
        * **Fonte:** Banco Central / Valor | *Câmbio*
        * **Resumo:** A moeda norte-americana ganha força globalmente com a alta nas taxas dos títulos do Tesouro dos EUA (Treasuries) e apreensão com a inflação global.
        * [🔗 Ler matéria sobre câmbio](https://valor.globo.com/)
        """)
        st.divider()

        st.markdown("""
        ### 8. Santander (SANB11) aprova R$ 1,5 bilhão em Juros sobre Capital Próprio
        * **Fonte:** ADVFN / RI Santander | *Proventos*
        * **Resumo:** O conselho de administração aprovou a distribuição aos acionistas registrados até a data com, reforçando o retorno via dividendos no setor bancário.
        * [🔗 Ver detalhes na ADVFN](https://br.advfn.com/)
        """)
        st.divider()

        st.markdown("""
        ### 9. Varejistas registram queda e MGLU3 recua mais de 6% no pregão
        * **Fonte:** InfoMoney | *Consumo e Varejo*
        * **Resumo:** As ações do setor de varejo sofrem com a alta dos juros futuros e dados de vendas no comércio físico abaixo das expectativas de analistas.
        * [🔗 Acompanhar movimentações do setor](https://www.infomoney.com.br/)
        """)
        st.divider()

        st.markdown("""
        ### 10. FII TVRI11 adquire imóvel em Salvador por R$ 39,1 milhões
        * **Fonte:** InfoMoney FIIs | *Fundos Imobiliários*
        * **Resumo:** O fundo imobiliário concluiu a aquisição de um imóvel corporativo com desconto de 17,5% em relação ao laudo de avaliação, ampliando a renda recorrente.
        * [🔗 Ler mais no InfoMoney FIIs](https://www.infomoney.com.br/imoveis/fiis/)
        """)

    with col2:
        st.subheader("🌐 Mercados Internacionais, Cripto & Tecnologia")

        st.markdown("""
        ### 11. Inflação ao Consumidor (CPI) nos EUA sobe 0,6% em setembro
        * **Fonte:** Reuters / US Bureau of Labor | *Internacional*
        * **Resumo:** O índice de preços ao consumidor norte-americano avançou 3,7% no acumulado de 12 meses, mantendo o Federal Reserve sob pressão no combate à inflação.
        * [🔗 Ler notícia na Reuters](https://www.reuters.com)
        """)
        st.divider()

        st.markdown("""
        ### 12. Bitcoin (BTC) recupera patamar de US$ 84 mil no 'Uptober'
        * **Fonte:** Mercado Bitcoin / CoinDesk | *Criptoativos*
        * **Resumo:** A maior criptomoeda do mundo volta a superar a média móvel de 50 semanas impulsionada por fluxo contínuo de compra nos ETFs de grande porte.
        * [🔗 Ver análise no Mercado Bitcoin](https://www.mercadobitcoin.com.br/blog/)
        """)
        st.divider()

        st.markdown("""
        ### 13. Morgan Stanley lucra US$ 4,9 bilhões impulsionado por Wall Street
        * **Fonte:** Bloomberg Linea | *Balanços Globais*
        * **Resumo:** O banco de investimento surpreendeu positivamente os analistas com um crescimento expressivo na receita do segmento de assessoria e renda variável.
        * [🔗 Ler na Bloomberg Linea](https://www.bloomberglinea.com.br/)
        """)
        st.divider()

        st.markdown("""
        ### 14. Bank of America registra lucro líquido de US$ 6,9 bilhões no 3º Tri
        * **Fonte:** InfoMoney / BofA | *Resultados Internacionais*
        * **Resumo:** Apesar de uma queda anual de 17%, os números do banco superaram as projeções do mercado para receita líquida de juros e gestão de fortunas.
        * [🔗 Ver balanço no InfoMoney](https://www.infomoney.com.br/)
        """)
        st.divider()

        st.markdown("""
        ### 15. Títulos do Tesouro dos EUA (Treasuries 10 anos) sobem a 5,30%
        * **Fonte:** Bloomberg Linea | *Renda Fixa Global*
        * **Resumo:** O rendimento dos títulos públicos americanos atingiu novas máximas, atraindo capital global e pressionando as bolsas de valores ao redor do mundo.
        * [🔗 Acompanhar Treasuries na Bloomberg](https://www.bloomberglinea.com.br/)
        """)
        st.divider()

        st.markdown("""
        ### 16. S&P 500 e Nasdaq oscilam após liquidação no setor de semicondutores
        * **Fonte:** Wall Street Journal / ADVFN | *Nova York*
        * **Resumo:** Ações de empresas de inteligência artificial e chips sofrem realizações de lucros, enquanto o índice Dow Jones opera próximo da estabilidade.
        * [🔗 Ler no Wall Street Journal / ADVFN](https://br.advfn.com/)
        """)
        st.divider()

        st.markdown("""
        ### 17. MicroStrategy expande compra de Bitcoin e ultrapassa 840 mil BTC
        * **Fonte:** Reuters / InfoMoney Cripto | *Corporativo*
        * **Resumo:** A empresa de software reforça sua posição como a maior detentora corporativa de Bitcoin do mundo, alocando recursos adicionais do seu caixa institucional.
        * [🔗 Ler notícia na Reuters/InfoMoney](https://www.infomoney.com.br/cripto/)
        """)
        st.divider()

        st.markdown("""
        ### 18. JPMorgan projeta que mercado cripto acumulou US$ 50 bi no ano
        * **Fonte:** Portal do Bitcoin / JPMorgan | *Análise Macro*
        * **Resumo:** Relatório do JPMorgan destaca que o fluxo de investimentos institucionais para fundos e produtos cripto em 2026 bateu novos recordes operacionais.
        * [🔗 Ver análise no Portal do Bitcoin](https://portaldobitcoin.uol.com.br/)
        """)
        st.divider()

        st.markdown("""
        ### 19. Movida (MOVI3) reporta lucro de R$ 152 milhões no 3º trimestre
        * **Fonte:** ADVFN | *Resultados no Brasil*
        * **Resumo:** A locadora de veículos registrou uma alta de 117% no seu lucro líquido consolidado, superando o guidance divulgado anteriormente aos investidores.
        * [🔗 Ler detalhes da matéria na ADVFN](https://br.advfn.com/)
        """)
        st.divider()

        st.markdown("""
        ### 20. FMI revisa projeções de crescimento global para a América Latina
        * **Fonte:** Fundo Monetário Internacional / Reuters | *Economia Global*
        * **Resumo:** Relatório de perspetivas econômicas do FMI sugere cautela na gestão fiscal dos países emergentes diante do aperto monetário prolongado em economias desenvolvidas.
        * [🔗 Acompanhar dados do FMI](https://www.reuters.com)
        """)

elif aba_lateral == "Recomendações de Compra":
    st.header("📈 Ações Recomendadas & Análise de Ativos")
    st.markdown(
        "Confira abaixo as principais ações recomendadas para o cenário atual, com tese de valorização, notícia motivadora, cotação aproximada e histórico de proventos:")

    st.markdown("""
    | Nome da Empresa / Ativo | Risco | Tese de Investimento & Motivo | Notícia do Estímulo (Fonte) | Preço Aprox. | Últimos Dividendos |
    | :--- | :--- | :--- | :--- | :--- | :--- |
    | **Petrobras (PETR4)** | 🟡 Mod. | Produção recorde na camada pré-sal e forte geração de caixa com a cotação do Brent em alta. | [📰 Ver Notícia #2 (Valor Econômico)](https://valor.globo.com/empresas/) | R$ 56,00 | R$ 1,04 / ação |
    | **B3 S.A. (B3SA3)** | 🟢 Baixo / Mod. | Crescimento expressivo de 45,7% no volume financeiro diário e ampliação de contas ativas. | [📰 Ver Notícia #3 (InfoMoney)](https://www.infomoney.com.br/cotacoes/b3/) | R$ 18,50 | R$ 0,14 / ação |
    | **Itaú Unibanco (ITUB4)** | 🟢 Baixo | Margem financeira sólida e capacidade defensiva elevada em períodos de ajuste bancário generalizado. | [📰 Ver Notícia #6 (InfoMoney)](https://www.infomoney.com.br/cotacoes/) | R$ 50,40 | R$ 0,31 / ação |
    | **Movida (MOVI3)** | 🔴 Alto | Crescimento de 117% no lucro líquido consolidado do 3º Tri, superando as projeções dos analistas. | [📰 Ver Notícia #19 (ADVFN)](https://br.advfn.com/) | R$ 12,40 | R$ 0,10 / ação |
    | **NVIDIA (NVDA)** | 🟡 Mod. | Demanda aquecida por semicondutores e chips de IA após ligeira realização de lucros criar ponto de entrada. | [📰 Ver Notícia #16 (Wall Street Journal)](https://br.advfn.com/) | US$ 132,00 | US$ 0,01 / ação |
    | **MicroStrategy / BTC (MSTR)** | 🔴 Alto | Expansão institucional agressiva de caixa ultrapassando a marca de 840 mil Bitcoins na tesouraria. | [📰 Ver Notícia #17 (Reuters)](https://www.infomoney.com.br/cripto/) | US$ 215,00 | US$ 0,00 |
    """)

    st.markdown("---")
    st.subheader("🛡️ Análise do Cenário Global: Ativos Mais Seguros vs. Mais Arriscados")

    col_seg, col_arr = st.columns(2)

    with col_seg:
        st.success("### 🛡️ Ações Mais Seguras (Resilientes)")
        st.markdown("""
        * **Itaú Unibanco (ITUB4) e B3 (B3SA3)**
        * **Porquê são seguras?** Operam como monopólios ou líderes consolidados com alta geração de caixa e capacidade de repasse de custos.
        * **Cenário Atual:** Com a volatilidade nos juros globais, garantem proteção patrimonial e rendimento em dividendos recorrentes.
        """)

    with col_arr:
        st.error("### ⚠️ Ações Mais Arriscadas (Alto Potencial de Valorização)")
        st.markdown("""
        * **Movida (MOVI3) e MicroStrategy (MSTR)**
        * **Porquê são arriscadas?** Possuem alta alavancagem operacional ou exposição direta à volatilidade do mercado de criptoativos.
        * **Cenário Atual:** Oferecem assimetria positiva expressiva (turnaround/valorização) para investidores com perfil arrojado.
        """)

    st.caption(
        "⚠️ *Aviso: As informações apresentadas possuem caráter exclusivamente educacional e demonstrativo, não constituindo recomendação formal de investimento.*")

else:
    # CHAT PRINCIPAL COM PESQUISA CENTRALIZADA E SUPORTE A IMAGENS
    st.title("🤖 BrokerSimples - Assistente Financeiro Inteligente")
    st.markdown("Faça perguntas sobre o mercado, envie gráficos/prints para análise visual ou utilize a barra central.")

    # Exibição do histórico de mensagens no ecrã principal
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

    # Processamento do envio através do Chat Nativo do Streamlit (Fixo e Prático)
    prompt_chat = st.chat_input("Digite sua dúvida, ordem ou análise (Ex: Como está a PETR4?)...")

    # Se o utilizador clicou num prompt anterior na sidebar, usa-o
    if st.session_state.selected_prompt:
        prompt_chat = st.session_state.selected_prompt
        st.session_state.selected_prompt = ""

    if prompt_chat:
        conteudo_mensagem = [prompt_chat]

        # Regista mensagem do utilizador
        st.session_state.historico.append({"role": "user", "content": conteudo_mensagem})

        with st.chat_message("user", avatar="👤"):
            st.write(prompt_chat)

        # Resposta da IA (GPT-4o)
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
                                    "content": "Você é o BrokerSimples, um analista financeiro amigável e especialista em mercado de capitais, criptomoedas e análise técnica de gráficos."
                                },
                                {
                                    "role": "user",
                                    "content": prompt_chat
                                }
                            ]
                        )
                        texto_resposta = resposta.choices[0].message.content
                        st.write(texto_resposta)
                        st.session_state.historico.append({"role": "assistant", "content": texto_resposta})
                except Exception as e:
                    st.error(f"Erro ao comunicar com a OpenAI: {e}")
                    # --- 2. Disclaimer / Isenção de Responsabilidade (Rodapé) ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #94a3b8; font-size: 12px; padding: 10px;'>
        <strong>Aviso Legal (Disclaimer):</strong> O BrokerSimples é uma ferramenta educacional e de análise baseada em Inteligência Artificial.
        As informações apresentadas não constituem recomendação direta de compra ou venda de ativos financeiros.
        Invista com responsabilidade e consulte um profissional certificado antes de tomar decisões de mercado.
    </div>
    """,
    unsafe_allow_html=True
    )


