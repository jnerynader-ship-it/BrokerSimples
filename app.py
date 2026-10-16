elif aba_lateral == "Recomendações de Compra":
  st.header("📈 Recomendações Estratégicas de Ativos & Cenário Global")
  st.caption(
      "🔄 Sistema de recomendação inteligente atualizado automaticamente a"
      " cada 30 minutos com base no mercado nacional e internacional."
  )
  st.markdown("---")

  # Botão para forçar a atualização imediata da recomendação
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

  # --- FUNÇÃO CACHEADA DE 30 MINUTOS PARA RECOMENDAÇÕES ---
  @st.cache_data(ttl=1800)
  def obter_dados_recomendacoes():
    # Retorna a estrutura organizada dos 3 blocos de risco
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
                    " privado do país, dispondo de elevado colchão de capital"
                    " e forte resiliência contra volatilidades macroeconômicas."
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

  # --- RENDERIZAÇÃO DOS 3 BLOCOS ---

  # 1. BLOCO CONSERVADOR
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

  # 2. BLOCO MODERADO
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

  # 3. BLOCO ARRISCADO
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
