import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

arquivo = "gastos.csv"

# ⚙️ CONFIG
st.set_page_config(page_title="Controle de Gastos", layout="wide")

# 🎨 ESTILO
st.markdown("""
<style>
body {
    background-color: #0e0e0e;
}

/* Card saldo */
.card {
    background: linear-gradient(135deg, #1c1c1c, #000000);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 20px;
}

.titulo {
    font-size: 16px;
    color: #cccccc;
}

.valor {
    font-size: 40px;
    font-weight: bold;
    color: #00ff88;
}

/* Card gasto */
.gasto {
    background-color: #1a1a1a;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 8px;
    border-left: 5px solid #00ff88;
    color: #ffffff;
}

/* Texto secundário */
.data {
    font-size: 14px;
    color: #bbbbbb;
}
</style>
""", unsafe_allow_html=True)

st.title("Controle de Gastos - Para de gastar Siôô💰")

# 📊 FUNÇÃO
def carregar_dados():
    if os.path.exists(arquivo):
        try:
            df = pd.read_csv(arquivo)
            df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
            df = df.dropna(subset=["Data"])
            return df
        except:
            return pd.DataFrame(columns=["Valor", "Forma", "Categoria", "Descrição", "Data"])
    else:
        return pd.DataFrame(columns=["Valor", "Forma", "Categoria", "Descrição", "Data"])

df = carregar_dados()

# 💳 SALDO
total = df["Valor"].sum() if not df.empty else 0

st.markdown(f"""
<div class="card">
    <div class="titulo">Saldo atual</div>
    <div class="valor">R$ {total:.2f}</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# 📥 FORMULÁRIO
with st.form("form_gastos", clear_on_submit=True):

    st.subheader("➕ Novo gasto")

    col1, col2 = st.columns(2)

    with col1:
        valor = st.number_input("Valor", min_value=0.0)
        forma = st.selectbox("Forma", ["Selecione...", "Pix", "Débito", "Crédito", "Dinheiro"])

    with col2:
        categoria = st.selectbox("Categoria", ["Selecione...", "Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Outros"])
        descricao = st.text_input("Descrição")

    salvar = st.form_submit_button("Salvar")

    if salvar:
        if valor == 0 or forma == "Selecione..." or categoria == "Selecione..." or descricao.strip() == "":
            st.warning("Preencha todos os campos!")
        else:
            novo = pd.DataFrame(
                [[valor, forma, categoria, descricao, datetime.now()]],
                columns=["Valor", "Forma", "Categoria", "Descrição", "Data"]
            )

            try:
                df_total = pd.read_csv(arquivo)
                df_total = pd.concat([df_total, novo], ignore_index=True)
            except:
                df_total = novo

            df_total.to_csv(arquivo, index=False)

            st.success("Gasto registrado 💸")
            st.rerun()

st.divider()

# 📊 LAYOUT: ESQUERDA (LISTA) | DIREITA (GRÁFICO)
if not df.empty:

    col_esq, col_dir = st.columns([2,1])

    # 📋 ESQUERDA
    with col_esq:

        st.subheader("📋 Seus gastos")

        df = df.sort_values(by="Data", ascending=False)

        hoje = datetime.now().date()
        ontem = hoje - timedelta(days=1)

        datas_validas = df["Data"].dt.date.unique()

        for data_unica in datas_validas:

            gastos_dia = df[df["Data"].dt.date == data_unica]
            total_dia = gastos_dia["Valor"].sum()

            if data_unica == hoje:
                titulo = "Hoje"
            elif data_unica == ontem:
                titulo = "Ontem"
            else:
                titulo = data_unica.strftime("%d/%m/%Y")

            st.markdown(f"### 📅 {titulo} — 💰 R$ {total_dia:.2f}")

            for i, row in gastos_dia.iterrows():

                data_formatada = row["Data"].strftime("%d/%m/%Y")

                col1, col2 = st.columns([5,1])

                with col1:
                    st.markdown(f"""
                    <div class="gasto">
                        💸 <b>R$ {row['Valor']:.2f}</b> - {row['Descrição']} <br>
                        <span class="data">{row['Categoria']} | 📅 {data_formatada}</span>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if st.button("🗑️", key=f"del_{i}"):
                        df_total = pd.read_csv(arquivo)
                        df_total = df_total.drop(i)
                        df_total.to_csv(arquivo, index=False)
                        st.rerun()

            st.divider()

    # 🍕 DIREITA (GRÁFICO PEQUENO)
    with col_dir:

        st.subheader("📊 Gastos por Categoria")

        grafico = df.groupby("Categoria")["Valor"].sum()

        fig, ax = plt.subplots(figsize=(3,3))
        ax.pie(grafico.values, labels=grafico.index, autopct='%1.0f%%', textprops={'fontsize': 8, 'color': 'Black'})
        ax.set_facecolor("#0e0e0e")
        

        st.pyplot(fig)

else:
    st.info("Nenhum gasto ainda 😅")