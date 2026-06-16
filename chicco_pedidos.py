import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
from PIL import Image
import io

st.set_page_config(page_title="Chicco | Portal Lojas", layout="wide", page_icon="🛍️", initial_sidebar_state="expanded")

# LOGIN
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
            st.subheader("Portal das Lojas")
            st.markdown("### Entrar")
            username = st.text_input("Utilizador", placeholder="lisboa")
            password = st.text_input("Palavra-passe", type="password")
            if st.button("Entrar", use_container_width=True):
                if username in USERS and USERS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.loja = username.capitalize()
                    st.rerun()
                else:
                    st.error("Utilizador ou password incorretos")
        st.stop()

check_login()

loja = st.session_state.loja

# DB
def init_db():
    conn = sqlite3.connect('chicco.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pedidos 
                 (id INTEGER PRIMARY KEY, loja TEXT, data TEXT, itens TEXT, status TEXT DEFAULT 'Pendente')''')
    c.execute('''CREATE TABLE IF NOT EXISTS fotos 
                 (id INTEGER PRIMARY KEY, loja TEXT, data TEXT, foto BLOB, descricao TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS medidas 
                 (loja TEXT PRIMARY KEY, vidro TEXT, vinil TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Chicco_logo.svg/2560px-Chicco_logo.svg.png", width=180)
    st.title(f"{loja}")
    st.markdown("---")
    menu = st.radio("Menu", 
        ["🏠 Início", "📦 Fazer Pedido", "📸 Fotos da Montra", "📏 Medidas da Loja", "📊 Meus Registos"])

# Páginas
if menu == "🏠 Início":
    st.title(f"Bem-vindo à Chicco, {loja}!")
    st.markdown("### Portal de Suporte às Lojas")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pedidos este mês", "8", "↑2")
    with col2:
        st.metric("Fotos enviadas", "14")
    with col3:
        st.metric("Medidas atualizadas", "Sim")

    st.info("Utiliza o menu lateral para fazer pedidos, enviar fotos das montras ou atualizar medidas.")

elif menu == "📦 Fazer Pedido":
    st.title("📦 Fazer Pedido de Material")
    st.write(f"**Loja:** {loja} | Data: {datetime.now().strftime('%d/%m/%Y')}")

    col1, col2 = st.columns(2)
    with col1:
        vinil = st.number_input("Vinil (m²)", min_value=0, value=0)
        espátula = st.number_input("Espátula", min_value=0, value=0)
    with col2:
        poster = st.number_input("Poster A1/A0", min_value=0, value=0)
        outros = st.text_area("Outros materiais", height=100)

    if st.button("Enviar Pedido", type="primary", use_container_width=True):
        itens = f"Vinil: {vinil}m² | Espátula: {espátula} | Poster: {poster} | Outros: {outros}"
        conn = sqlite3.connect('chicco.db')
        conn.execute("INSERT INTO pedidos (loja, data, itens) VALUES (?, ?, ?)", 
                    (loja, datetime.now().strftime("%Y-%m-%d %H:%M"), itens))
        conn.commit()
        conn.close()
        st.success("Pedido enviado com sucesso! Obrigado.")

elif menu == "📸 Fotos da Montra":
    st.title("📸 Enviar Foto da Montra")
    descricao = st.text_input("Descrição / Campanha", "Montra Verão 2026")
    foto = st.file_uploader("Foto da montra", type=['jpg','png','jpeg'])
    
    if foto and st.button("Enviar Foto", type="primary"):
        img = Image.open(foto)
        img_byte = io.BytesIO()
        img.save(img_byte, format='JPEG')
        conn = sqlite3.connect('chicco.db')
        conn.execute("INSERT INTO fotos (loja, data, foto, descricao) VALUES (?, ?, ?, ?)",
                    (loja, datetime.now().strftime("%Y-%m-%d %H:%M"), img_byte.getvalue(), descricao))
        conn.commit()
        conn.close()
        st.success("Foto enviada com sucesso!")
        st.image(img, use_column_width=True)

elif menu == "📏 Medidas da Loja":
    st.title("📏 Medidas da Loja")
    conn = sqlite3.connect('chicco.db')
    df = pd.read_sql_query("SELECT vidro, vinil FROM medidas WHERE loja=?", conn, params=(loja,))
    conn.close()
    
    if not df.empty:
        st.subheader("Medidas Atuais")
        st.write(df.iloc[0])
    
    vidro = st.text_area("Medidas de Vidro", height=150)
    vinil = st.text_area("Medidas / Áreas para Vinil", height=150)
    
    if st.button("Guardar Medidas", type="primary"):
        conn = sqlite3.connect('chicco.db')
        conn.execute("INSERT OR REPLACE INTO medidas (loja, vidro, vinil) VALUES (?, ?, ?)", (loja, vidro, vinil))
        conn.commit()
        conn.close()
        st.success("Medidas guardadas com sucesso!")

elif menu == "📊 Meus Registos":
    st.title("📊 Meus Registos")
    conn = sqlite3.connect('chicco.db')
    pedidos = pd.read_sql_query("SELECT data, itens, status FROM pedidos WHERE loja=? ORDER BY data DESC LIMIT 10", conn, params=(loja,))
    fotos = pd.read_sql_query("SELECT data, descricao FROM fotos WHERE loja=? ORDER BY data DESC LIMIT 10", conn, params=(loja,))
    conn.close()
    
    st.subheader("Últimos Pedidos")
    st.dataframe(pedidos, use_container_width=True)
    
    st.subheader("Últimas Fotos Enviadas")
    st.dataframe(fotos, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("Chicco Portugal - Portal Interno")
