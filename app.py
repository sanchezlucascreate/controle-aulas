import streamlit as st
import sqlite3
from datetime import date

# ---------------- CONFIGURAÇÃO ----------------
st.set_page_config(page_title="Controle de Aulas", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3, h4 {
    font-weight: 600;
}

div[data-testid="stMetric"] {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}

section[data-testid="stSidebar"] {
    background-color: #f7f7f9;
}

.stButton > button {
    border-radius: 10px;
    padding: 0.6em 1.2em;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ---------------- BANCO DE DADOS ----------------
import os

DB_PATH = os.path.join(os.getcwd(), "dados.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS creditos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quantidade INTEGER,
    data TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS aulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno TEXT,
    data TEXT
)
""")

# Créditos disponíveis (soma entradas e saídas)
cursor.execute("SELECT COALESCE(SUM(quantidade), 0) FROM creditos")
creditos_disponiveis = cursor.fetchone()[0]

# ---------------- INTERFACE ----------------
st.title("Controle de Aulas")

pagina = st.sidebar.radio(
    "Menu",
    ["Controle", "Histórico"]
)

# ================= TELA CONTROLE =================
if pagina == "Controle":

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Créditos disponíveis")
        st.metric("Aulas", creditos_disponiveis)

    with col2:
        st.subheader("Adicionar créditos")
        qtd = st.number_input("Quantidade de aulas", min_value=1, step=1)

        if st.button("Adicionar créditos"):
            cursor.execute(
                "INSERT INTO creditos (quantidade, data) VALUES (?, ?)",
                (qtd, str(date.today()))
            )
            conn.commit()
            st.rerun()

    st.divider()

    st.subheader("Registrar aula")
    aluno = st.selectbox("Quem treinou?", ["Lucas", "Nicola"])
    data_aula = st.date_input("Data da aula", value=date.today())

    if st.button("Registrar aula"):
        if creditos_disponiveis <= 0:
            st.error("Sem créditos disponíveis.")
        else:
            cursor.execute(
                "INSERT INTO aulas (aluno, data) VALUES (?, ?)",
                (aluno, str(data_aula))
            )
            cursor.execute(
                "INSERT INTO creditos (quantidade, data) VALUES (?, ?)",
                (-1, str(data_aula))
            )
            conn.commit()
            st.rerun()

# ================= TELA HISTÓRICO =================
if pagina == "Histórico":

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Créditos adicionados")

        cursor.execute(
            "SELECT quantidade, data FROM creditos WHERE quantidade > 0 ORDER BY data DESC"
        )
        creditos_hist = cursor.fetchall()

        if creditos_hist:
            dados_creditos = []
            for qtd, data_str in creditos_hist:
                dados_creditos.append({
                    "Data": date.fromisoformat(data_str).strftime("%d/%m/%Y"),
                    "Quantidade de aulas": qtd
                })
            st.dataframe(dados_creditos, use_container_width=True)
        else:
            st.info("Nenhum crédito adicionado.")

    with col2:
        st.subheader("Aulas realizadas")

        cursor.execute(
            "SELECT aluno, data FROM aulas ORDER BY data DESC"
        )
        aulas = cursor.fetchall()

        if aulas:
            dados_aulas = []
            for aluno, data_str in aulas:
                dados_aulas.append({
                    "Data": date.fromisoformat(data_str).strftime("%d/%m/%Y"),
                    "Aluno": aluno
                })
            st.dataframe(dados_aulas, use_container_width=True)
        else:
            st.info("Nenhuma aula registrada.")
