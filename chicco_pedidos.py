import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
from PIL import Image
import io

st.set_page_config(page_title="Chicco Pedidos", layout="wide")

# ====================== LOGIN ======================
USERS = {
    "lisboa": "lisboa123",
    "porto": "porto123",
    "coimbra": "coimbra123",
    "faro": "faro123",
    "braga": "braga123",
    # Adiciona mais lojas aqui: "nome_loja": "password"
}

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.loja = None

    if not st.session_state.logged_in:
        st.title("🔐 Login Chicco")
        st.write("Usa o nome da loja em minúsculas (ex: lisboa)")
        username = st.text_input("Nome da Loja", key="user")
        password = st.text_input("Password", type="password", key="pass")
        
        if st.button("Entrar"):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.loja = username.capitalize() + " - Chicco"
                st.rerun()
            else:
                st.error("Credenciais erradas. Tenta novamente.")
        st.stop()

check_login()

loja = st.session_state.loja

# ====================== BASE DE DADOS ======================
def init_db():
    conn = sqlite3.connect('chicco.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY, loja TEXT, data TEXT, itens TEXT, status TEXT DEFAULT 'Pendente'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS fotos (
        id INTEGER PRIMARY KEY, loja TEXT, data TEXT, foto BLOB, descricao TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS medidas (
        loja TEXT PRIMARY KEY, vidro TEXT, vinil TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# ====================== MENU ======================
st.sidebar.title(f"👋 Bem-vindo, {loja}")
menu = st.sidebar.selectbox("Menu", ["📦 Fazer Pedido", "📸 Enviar Foto Montra", "📏 Medidas", "📊 Meus Pedidos e Fotos"])

if menu == "📦 Fazer Pedido":
    st.title("📦 Novo Pedido de Material")
    st.write(f"**Loja:** {loja}")
    
    col1, col2 = st.columns(2)
    with col1:
        vinil = st.number_input("Vinil (m²)", min_value=0, value=0)
        espátula = st.number_input("Espátula", min_value=0, value=0)
    with col2:
        poster = st.number_input("Poster", min_value=0, value=0)
        outros = st.text_input("Outros materiais (ex: cola, fita, etc.)")
    
    if st.button("🚀 Enviar Pedido"):
        itens = f"Vinil: {vinil}m² | Espátula: {espátula} | Poster: {poster} | Outros: {outros}"
        data = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        conn = sqlite3.connect('chicco.db')
        conn.execute("INSERT INTO pedidos (loja, data, itens) VALUES (?, ?, ?)", (loja, data, itens))
        conn.commit()
        conn.close()
        
        st.success("✅ Pedido enviado com sucesso! A tua chefe vai receber.")

elif menu == "📸 Enviar Foto Montra":
    st.title("📸 Foto da Montra")
    st.write("Tira foto da montra depois de montada e envia aqui.")
    descricao = st.text_input("Descrição (ex: Montra Primavera 2026, Campanha Verão, etc.)")
    foto = st.file_uploader("Escolhe a foto da montra", type=['jpg', 'png', 'jpeg'])
    
    if foto and st.button("📤 Enviar Foto"):
        img = Image.open(foto)
        img_byte = io.BytesIO()
        img.save(img_byte, format='JPEG')
        
        conn = sqlite3.connect('chicco.db')
        conn.execute("INSERT INTO fotos (loja, data, foto, descricao) VALUES (?, ?, ?, ?)",
                    (loja, datetime.now().strftime("%Y-%m-%d %H:%M"), img_byte.getvalue(), descricao))
        conn.commit()
        conn.close()
        
        st.success("Foto guardada com sucesso!")
        st.image(img, caption=descricao, use_column_width=True)

elif menu == "📏 Medidas":
    st.title("📏 Medidas da Loja")
    st.write("Guarda aqui as medidas dos vidros e áreas de vinil para referência futura.")
    
    conn = sqlite3.connect('chicco.db')
    df = pd.read_sql_query("SELECT vidro, vinil FROM medidas WHERE loja=?", conn, params=(loja,))
    conn.close()
    
    if not df.empty:
        st.info("Medidas atuais guardadas:")
        st.write(df.iloc[0])
    
    vidro = st.text_area("Medidas de Vidro (ex: Vitrine principal: 2.5m x 3m, Lateral: 1.8m x 2m)", height=100)
    vinil = st.text_area("Medidas / Áreas para Vinil", height=100)
    
    if st.button("💾 Guardar Medidas"):
        conn = sqlite3.connect('chicco.db')
        conn.execute("INSERT OR REPLACE INTO medidas (loja, vidro, vinil) VALUES (?, ?, ?)", (loja, vidro, vinil))
        conn.commit()
        conn.close()
        st.success("Medidas guardadas com sucesso!")

elif menu == "📊 Meus Pedidos e Fotos":
    st.title("📊 Histórico da Loja")
    conn = sqlite3.connect('chicco.db')
    
    st.subheader("📦 Meus Pedidos")
    pedidos = pd.read_sql_query("SELECT data, itens, status FROM pedidos WHERE loja=? ORDER BY data DESC", conn, params=(loja,))
    if not pedidos.empty:
        st.dataframe(pedidos, use_container_width=True)
    else:
        st.info("Ainda não tens pedidos registados.")
    
    st.subheader("📸 Fotos Enviadas")
    fotos = pd.read_sql_query("SELECT data, descricao FROM fotos WHERE loja=? ORDER BY data DESC", conn, params=(loja,))
    if not fotos.empty:
        st.dataframe(fotos, use_container_width=True)
    else:
        st.info("Ainda não enviaste fotos.")
    
    conn.close()

st.sidebar.markdown("---")
st.sidebar.info("App desenvolvida para as lojas Chicco Portugal.\n\nPara uso interno.\n\nDúvidas? Fala com o teu gestor.")