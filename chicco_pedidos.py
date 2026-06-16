import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
from PIL import Image
import io

st.set_page_config(page_title="Chicco | Portal Lojas", layout="wide", page_icon="🛍️")

# ====================== LOGIN ======================
USERS = {
    "lisboa": "lisboa123",
    "porto": "porto123",
    "coimbra": "coimbra123",
    "faro": "faro123",
    "braga": "braga123",
}

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.loja = None

    if not st.session_state.logged_in:
        st.title("🛍️ Chicco Portugal")
        st.subheader("Portal de Lojas")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("### Login")
            username = st.text_input("Nome da Loja (minúsculas)", placeholder="lisboa")
            password = st.text_input("Password", type="password")
            
            if st.button("Entrar", use_container_width=True):
                if username in USERS and USERS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.loja = username.capitalize()
                    st.rerun()
                else:
                    st.error("Credenciais incorretas")
        st.stop()

check_login()

loja = st.session_state.loja

# ====================== BASE DE DADOS ======================
def init_db():
    conn = sqlite3.connect('chicco.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, loja TEXT, data TEXT, itens TEXT, status TEXT DEFAULT 'Pendente')''')
    c.execute('''CREATE TABLE IF NOT EXISTS fotos (id INTEGER PRIMARY KEY, loja TEXT, data TEXT, foto BLOB, descricao TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS medidas (loja TEXT PRIMARY KEY, vidro TEXT, vinil TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ====================== MENU LATERAL ======================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Chicco_logo.svg/2560px-Chicco_logo.svg.png", width=150)  # Logo Chicco (podes substituir)
st.sidebar.title(f"👋 {loja}")
menu = st.sidebar.selectbox("Navegação", 
    ["🏠 Início", "📦 Novo Pedido", "📸 Fotos Montra", "📏 Medidas", "📊 Histórico"])

# ====================== PÁGINAS ======================
if menu == "🏠 Início":
    st.title(f"Bem-vindo, {loja}!")
    st.markdown("### Portal de Pedidos e Montras - Chicco Portugal")
    st.info("Utiliza o menu lateral para navegar.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pedidos Enviados", "12")
    with col2:
        st.metric("Fotos Enviadas", "8")
    with col3:
        st.metric("Medidas Registadas", "Sim")

elif menu == "📦 Novo Pedido":
    st.title("📦 Novo Pedido de Material")
    st.markdown(f"**Loja:** {loja}")

    col1, col2 = st.columns(2)
    with col1:
        vinil = st.number_input("Vinil (m²)", min_value=0, value=5)
        espátula = st.number_input("Espátula", min_value=0, value=2)
    with col2:
        poster = st.number_input("Poster", min_value=0, value=3)
        outros = st.text_input("Outros materiais", placeholder="Fita dupla face, cola, etc.")

    if st.button("Enviar Pedido", type="primary", use_container_width=True):
        itens = f"Vinil: {vinil}m² | Espátula: {espátula} | Poster: {poster} | Outros: {outros}"
        conn = sqlite3.connect('chicco.db')
        conn.execute("INSERT INTO pedidos (loja, data, itens) VALUES (?, ?, ?)", 
                    (loja, datetime.now().strftime("%Y-%m-%d %H:%M"), itens))
        conn.commit()
        conn.close()
        st.success("✅ Pedido enviado com sucesso!")

elif menu == "📸 Fotos Montra":
    st.title("📸 Enviar Foto da Montra")
    descricao = st.text_input("Descrição da Montra", placeholder="Montra Verão 2026 - Tema Praia")
    foto = st.file_uploader("Seleciona a foto", type=['jpg', 'png', 'jpeg'])
    
    if foto and st.button("Enviar Foto", type="primary"):
        img = Image.open(foto)
        img_byte = io.BytesIO()
        img.save(img_byte, format='JPEG')
        conn = sqlite3.connect('chicco.db')
        conn.execute("INSERT INTO fotos (loja, data, foto, descricao) VALUES (?, ?, ?, ?)",
                    (loja, datetime.now().strftime("%Y-%m-%d %H:%M"), img_byte.getvalue(), descricao))
        conn.commit()
        conn.close()
        st.success("Foto enviada!")
        st.image(img, use_column_width=True)

elif menu == "📏 Medidas":
    st.title("📏 Medidas da Loja")
    conn = sqlite3.connect('chicco.db')
    df = pd.read_sql_query("SELECT vidro, vinil FROM medidas WHERE loja=?", conn, params=(loja,))
    conn.close()
    
    if not df.empty:
        st.success("Medidas já registadas")
        st.write(df.iloc[0])
    
    vidro = st.text_area("Medidas de Vidro", height=120)
    vinil = st.text_area("Medidas de Vinil / Áreas", height=120)
    
    if st.button("Guardar Medidas", type="primary"):
        conn = sqlite3.connect('chicco.db')
        conn.execute("INSERT OR REPLACE INTO medidas (loja, vidro, vinil) VALUES (?, ?, ?)", (loja, vidro, vinil))
        conn.commit()
        conn.close()
        st.success("Medidas guardadas!")

elif menu == "📊 Histórico":
    st.title("📊 Histórico da Loja")
    conn = sqlite3.connect('chicco.db')
    pedidos = pd.read_sql_query("SELECT data, itens, status FROM pedidos WHERE loja=? ORDER BY data DESC", conn, params=(loja,))
    fotos = pd.read_sql_query("SELECT data, descricao FROM fotos WHERE loja=? ORDER BY data DESC", conn, params=(loja,))
    conn.close()
    
    st.subheader("Pedidos")
    st.dataframe(pedidos, use_container_width=True)
    
    st.subheader("Fotos Enviadas")
    st.dataframe(fotos, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("App Chicco Portugal\nVersão melhorada")
