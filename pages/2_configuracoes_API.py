import streamlit as st

st.set_page_config(page_title="Configurações - BrokerSimples", page_icon="⚙️", layout="wide")

st.header("⚙️ Configurações da Plataforma")
st.markdown("Gerencie as credenciais de acesso às APIs de mercado e parâmetros da Inteligência Artificial.")

with st.form("form_config"):
    st.text_input("Chave da API OpenAI (sk-proj-...)", type="password")
    st.text_input("Chave de Conexão MetaTrader / Broker API", type="password")

    modo_operacao = st.selectbox("Modo de Operação da IA", ["Conservador", "Moderado", "Agressivo (Day Trader)"])

    salvar = st.form_submit_button("Guardar Configurações")
    if salvar:
        st.success("Configurações atualizadas com sucesso!")