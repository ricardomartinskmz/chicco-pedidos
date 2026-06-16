import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
from PIL import Image
import io

st.set_page_config(page_title="Chicco - Artsana Portugal", layout="wide", page_icon="🛍️")

# ====================== LOGIN ======================
USERS = {
    "lisboa": "lisboa123", "porto": "porto123", "coimbra": "coimbra123",
    "faro": "faro123", "braga": "braga123"
}

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.loja = None

    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.title("🛍️ Chicco")
            st.subheader("Artsana Portugal")
            username = st.text_input("Utilizador", placeholder="lisboa")
            password = st.text_input("Password", type="password")
            if st.button("Entrar", use_container_width=True):
                if username in USERS and USERS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.loja = username.capitalize()
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")
        st.stop()

check_login()

loja = st.session_state.loja

# ====================== MENU LATERAL ======================
st.sidebar.title("Artsana Portugal")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Chicco_logo.svg/2560px-Chicco_logo.svg.png", width=180)
menu = st.sidebar.radio("Menu", 
    ["Início", "Lojas", "Pedidos de Material", "Estado de Pedidos de Material", "Medidas Lojas"])

# ====================== DB ======================
def init_db():
    conn = sqlite3.connect('chicco.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pedidos 
                 (id INTEGER PRIMARY KEY, loja TEXT, data TEXT, material TEXT, quantidade TEXT, status TEXT DEFAULT 'Pendente')''')
    c.execute('''CREATE TABLE IF NOT EXISTS fotos 
                 (id INTEGER PRIMARY KEY, loja TEXT, data TEXT, foto BLOB, descricao TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS medidas 
                 (loja TEXT PRIMARY KEY, medidas_texto TEXT)''')
    conn.commit()
    conn.close()

init_db()

if menu == "Início":
    st.title(f"Bem-vindo, {loja}!")
    st.markdown("### Portal Chicco - Artsana Portugal")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("Lojas", use_container_width=True)
    with col2:
        st.button("Pedidos de Material", use_container_width=True)
    with col3:
        st.button("Estado de Pedidos", use_container_width=True)
    with col4:
        st.button("Medidas Lojas", use_container_width=True)

elif menu == "Pedidos de Material":
    st.title("Formulário de Pedido de Material")
    st.write(f"**Loja:** {loja}")
    
    material = st.text_area("Material em falta *", height=100, placeholder="Vinil, Espátula, Poster, etc.")
    quantidade = st.text_area("Quantidades *", height=100)
    anexos = st.file_uploader("Anexos (opcional)", type=['jpg','png','pdf'])
    
    if st.button("Enviar", type="primary", use_container_width=True):
        conn = sqlite3.connect('chicco.db')
        conn.execute("INSERT INTO pedidos (loja, data, material, quantidade) VALUES (?, ?, ?, ?)", 
                    (loja, datetime.now().strftime("%Y-%m-%d %H:%M"), material, quantidade))
        conn.commit()
        conn.close()
        st.success("Pedido enviado com sucesso!")

elif menu == "Estado de Pedidos de Material":
    st.title("Estado de Pedidos de Material")
    conn = sqlite3.connect('chicco.db')
    df = pd.read_sql_query("SELECT data, material, quantidade, status FROM pedidos WHERE loja=? ORDER BY data DESC", conn, params=(loja,))
    conn.close()
    st.dataframe(df, use_container_width=True)

elif menu == "Medidas Lojas":
    st.title("Medidas Lojas")
    st.write("Medidas de Montras (em centímetros)")
    
    conn = sqlite3.connect('chicco.db')
    df = pd.read_sql_query("SELECT * FROM medidas WHERE loja=?", conn, params=(loja,))
    conn.close()
    
    if df.empty:
        st.info("Ainda não tem medidas registadas.")
    else:
        st.dataframe(df, use_container_width=True)
    
    # Formulário simples para medidas
    medidas = st.text_area("Insira as medidas (ex: Vidro principal: 250x300 cm)")
    if st.button("Guardar Medidas"):
        conn = sqlite3.connect('chicco.db')
        conn.execute("INSERT OR REPLACE INTO medidas (loja, medidas_texto) VALUES (?, ?)", (loja, medidas))
        conn.commit()
        conn.close()
        st.success("Medidas guardadas!")

elif menu == "Lojas":
    st.title("Lojas")
    st.write("Em breve...")

st.sidebar.caption("Made with Streamlit • Artsana Portugal")
