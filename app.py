import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="SmartFlow", layout="wide")

st.title("SmartFlow — Painel Operacional de Gestão de Equipe")
st.caption("Produtividade alta não deveria significar exaustão da equipe.")

df = pd.read_excel("smartflow.xlsx", sheet_name="production")
funcionarios = pd.read_excel("smartflow.xlsx", sheet_name="employees")

ritmo_por_func = df.groupby("employee_id")["actual_rate_kits_min"].mean().reset_index()
comparacao = ritmo_por_func.merge(funcionarios, on="employee_id")
comparacao["achievement_pct"] = comparacao["actual_rate_kits_min"] / comparacao["reference_capacity_kits_min"]

def classificar(pct):
    if pct > 1.15:
        return "ALTO"
    elif pct > 1.05:
        return "ATENÇÃO"
    else:
        return "NORMAL"

comparacao["status"] = comparacao["achievement_pct"].apply(classificar)

# filtro na barra lateral
mesas = st.sidebar.multiselect("Filtrar por mesa", options=comparacao["table_id"].unique(), default=comparacao["table_id"].unique())
comparacao_filtrada = comparacao[comparacao["table_id"].isin(mesas)]
if comparacao_filtrada.empty:
    st.warning("Selecione ao menos uma mesa no filtro para ver os dados.")
    st.stop()
# métricas no topo
col1, col2, col3, col4 = st.columns(4)
col1.metric("Produção total", int(df["quantity_produced"].sum()))
col2.metric("Ritmo médio", round(df["actual_rate_kits_min"].mean(), 2))
col3.metric("Funcionários analisados", len(comparacao_filtrada))
col4.metric("Em atenção/alto", len(comparacao_filtrada[comparacao_filtrada["status"] != "NORMAL"]))

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Produção por funcionário")
    producao = df[df["employee_id"].isin(comparacao_filtrada["employee_id"])].groupby("employee_id")["quantity_produced"].sum().sort_values(ascending=False)
    fig1, ax1 = plt.subplots()
    ax1.bar(producao.index, producao.values, color="steelblue")
    ax1.set_ylabel("Kits produzidos")
    st.pyplot(fig1)

with col_b:
    st.subheader("Distribuição de carga")
    contagem = comparacao_filtrada["status"].value_counts()
    cores = {"NORMAL": "seagreen", "ATENÇÃO": "goldenrod", "ALTO": "firebrick"}
    fig2, ax2 = plt.subplots()
    ax2.pie(contagem.values, labels=contagem.index, autopct="%1.0f%%", colors=[cores[s] for s in contagem.index])
    st.pyplot(fig2)

st.divider()
st.subheader("Detalhamento por funcionário")
st.dataframe(comparacao_filtrada[["employee_id", "employee_name", "table_id", "actual_rate_kits_min", "reference_capacity_kits_min", "achievement_pct", "status"]])
