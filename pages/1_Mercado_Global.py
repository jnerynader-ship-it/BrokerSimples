import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Mercado Global - BrokerSimples", page_icon="📊", layout="wide")

st.header("📊 Monitor de Ativos e Cotações")
st.markdown("Acompanhe em tempo real os principais pares de moedas, índices e criptoativos.")

# Tabela simulada de ativos financeiros
dados_mercado = pd.DataFrame({
    "Ativo": ["EURUSD", "GBPUSD", "USDJPY", "PETR4", "VALE3", "BTCUSD"],
    "Tipo": ["Forex", "Forex", "Forex", "Ação BR", "Ação BR", "Criptomoeda"],
    "Último": [1.1123, 1.3170, 158.86, 36.50, 62.10, 64200.00],
    "Variação (%)": [+0.15, -0.42, +0.81, +1.25, -0.73, +3.40]
})
st.dataframe(dados_mercado, width='stretch')

st.subheader("Gráfico de Tendência (Simulação)")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=["EURUSD", "PETR4", "VALE3"]
)
st.line_chart(chart_data)