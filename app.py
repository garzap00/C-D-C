import streamlit as st
from supabase import create_client

# Configuración inicial de la página
st.set_page_config(
    page_title="C.D.C. | Campo Digital Colombia",
    page_icon="https://raw.githubusercontent.com/garzap00/C-D-C/refs/heads/main/logo.jpeg",
    layout="wide",
)

# Conexión segura a Supabase usando los secretos de Streamlit
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Estilos CSS
st.markdown(
    """
    <style>
    .hero {
        background: linear-gradient(rgba(9,31,21,.70),rgba(9,31,21,.84)), url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=2000&q=85") center/cover;
        padding: 50px 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
    }
    .kpi-card {
        background-color: #f7f8f5;
        border: 1px solid #e0e5df;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- FUNCIONES DE USUARIOS CON SUPABASE ---
def obtener_usuarios_db():
    try:
        response = supabase.table("usuarios").select("*").execute()
        data = response.data
        usuarios_dict = {}
        for row in data:
            usuarios_dict[row["r_mail"]] = {
                "password": row["r_pwd"],
                "nombre": row["r_nom"],
            }
        if "admin@sena.edu.co" not in usuarios_dict:
            usuarios_dict["admin@sena.edu.co"] = {
                "password": "123",
                "nombre": "Aprendiz SENA",
            }
        return usuarios_dict
    except Exception:
        return {
            "admin@sena.edu.co": {"password": "123", "nombre": "Aprendiz SENA"}
        }

def registrar_usuario_db(email, password, nombre):
    try:
        response = (
            supabase.table("usuarios")
            .insert({"r_mail": email, "r_pwd": password, "r_nom": nombre})
            .execute()
        )
        return True
    except Exception as e:
        st.error(f"Detalle técnico del error: {e}")
        return False

# --- FUNCIONES DEL FORO CON SUPABASE ---
def obtener_posts_db():
    try:
        response = supabase.table("foro").select("*").order("id", desc=True).execute()
        if response.data:
            return response.data
        else:
            return [{
                "id": 1,
                "usuario": "Carlos Agrónomo",
                "texto": "Excelente producción en la altillanura. El campo colombiano avanza con tecnología.",
            }]
    except Exception:
        return [{
            "id": 1,
            "usuario": "Carlos Agrónomo",
            "texto": "Excelente producción en la altillanura. El campo colombiano avanza con tecnología.",
        }]

def crear_post_db(usuario, texto):
    try:
        supabase.table("foro").insert({
            "usuario": usuario,
            "texto": texto,
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error al publicar en la base de datos: {e}")
        return False

# --- FUNCIONES DE COMENTARIOS / RESPUESTAS ---
def obtener_comentarios_db(post_id):
    try:
        response = (
            supabase.table("comentarios")
            .select("*")
            .eq("post_id", post_id)
            .order("id", desc=False)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error al leer comentarios del post {post_id}: {e}")
        return []

def crear_comentario_db(post_id, usuario, texto):
    try:
        supabase.table("comentarios").insert({
            "post_id": post_id,
            "usuario": usuario,
            "texto": texto,
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar comentario: {e}")
        return False

# --- BASE DE DATOS DINÁMICA POR TERRITORIO ---
DATOS_TERRITORIOS = {
    "Caribe": {
        "humedad": "55-75%",
        "est_humedad": "Humedad variable, más baja en La Guajira",
        "temp": "27-32°C",
        "est_temp": "Clima cálido y seco en gran parte del año",
        "precipitacion": "500-1.500 mm/año",
        "est_pre": "Estación seca prolongada, lluvias concentradas",
        "altitud": "0-200 m.s.n.m.",
        "est_alt": "Llanura costera y valles bajos",
        "imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQh6-FtKHVjEt3Kg_DxAScZ6UcW8Xi2m_NHUojtT5aSHg&s=10",
        "cultivos": [
            {"nombre": "🌽 Maíz", "desc": "Cultivo presente en casi todo el Caribe"},
            {"nombre": "🌿 Yuca", "desc": "Base alimentaria de la región"},
            {"nombre": "🌴 Palma de Aceite", "desc": "Importante en Cesar y Magdalena"},
            {"nombre": "🍌 Banano", "desc": "Principalmente en Magdalena"},
            {"nombre": "🌾 Arroz", "desc": "Bolívar, Cesar, Córdoba y Sucre"},
            {"nombre": "🥭 Mango", "desc": "Atlántico y Magdalena"},
            {"nombre": "🥔 Ñame", "desc": "Bolívar, Córdoba y Sucre"},
            {"nombre": "🍫 Cacao", "desc": "Presente en Cesar"},
        ],
        "departamentos": {
            "Atlántico": ["yuca", "maíz", "mango", "guayaba"],
            "Bolívar": ["arroz", "yuca", "ñame", "maíz"],
            "Cesar": ["palma de aceite", "arroz", "maíz", "cacao"],
            "Córdoba": ["maíz", "arroz", "yuca", "ñame"],
