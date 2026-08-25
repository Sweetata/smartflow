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

def nivel_capacidade(meta):
    if meta < 4:
        return "Iniciante"
    elif meta < 8:
        return "Regular"
    else:
        return "Ágil"

comparacao["status"] = comparacao["achievement_pct"].apply(classificar)
comparacao["nivel"] = comparacao["reference_capacity_kits_min"].apply(nivel_capacidade)

mesas = st.sidebar.multiselect("Filtrar por mesa", options=comparacao["table_id"].unique(), default=comparacao["table_id"].unique())
busca = st.sidebar.text_input("Buscar funcionário")

comparacao_filtrada = comparacao[comparacao["table_id"].isin(mesas)]
if busca:
    comparacao_filtrada = comparacao_filtrada[comparacao_filtrada["employee_name"].str.contains(busca, case=False, na=False)]

if comparacao_filtrada.empty:
    st.warning("Nenhum funcionário encontrado com esse filtro.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Produção total", int(df["quantity_produced"].sum()))
col2.metric("Ritmo médio", round(df["actual_rate_kits_min"].mean(), 2))
col3.metric("Funcionários analisados", len(comparacao_filtrada))

qtd_alerta = len(comparacao_filtrada[comparacao_filtrada["status"] != "NORMAL"])
if qtd_alerta > 0:
    col4.metric("Em atenção/alto", qtd_alerta, delta="requer atenção", delta_color="inverse")
else:
    col4.metric("Em atenção/alto", qtd_alerta, delta="tudo normal", delta_color="normal")

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
st.subheader("Nível de capacidade da equipe")
nivel_contagem = comparacao_filtrada["nivel"].value_counts().reindex(["Iniciante", "Regular", "Ágil"]).fillna(0)
fig3, ax3 = plt.subplots()
ax3.bar(nivel_contagem.index, nivel_contagem.values, color=["#f0997b", "#85b7eb", "#5dcaa5"])
ax3.set_ylabel("Funcionários")
st.pyplot(fig3)

st.divider()
st.subheader("Detalhamento por funcionário")
tabela = comparacao_filtrada[["employee_id", "employee_name", "table_id", "actual_rate_kits_min", "reference_capacity_kits_min", "achievement_pct", "nivel", "status"]]
st.dataframe(tabela)

csv = tabela.to_csv(index=False).encode("utf-8")
st.download_button("Baixar dados filtrados (CSV)", data=csv, file_name="smartflow_dados.csv", mime="text/csv")

st.divider()
st.markdown("[GitHub](https://github.com/Sweetata) · [LinkedIn](https://www.linkedin.com/in/talita-alves-da-silva)")
