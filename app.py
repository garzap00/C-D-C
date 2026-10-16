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
            "La Guajira": ["maíz", "fríjol", "yuca", "melón"],
            "Magdalena": ["banano", "palma de aceite", "arroz", "mango"],
            "Sucre": ["yuca", "ñame", "maíz", "arroz"],
        }
    },
    "Pacífica": {
        "humedad": "80-95%",
        "est_humedad": "Una de las regiones más húmedas del mundo",
        "temp": "24-28°C",
        "est_temp": "Cálido húmedo constante",
        "precipitacion": "4.000-10.000 mm/año",
        "est_pre": "Lluvias casi todo el año, especialmente en Chocó",
        "altitud": "0-1.500 m.s.n.m.",
        "est_alt": "Desde costa hasta estribaciones de la cordillera",
        "imagen": "https://mejorconsalud.as.com/wp-content/uploads/2022/09/cana-azucar-1.jpg",
        "cultivos": [
            {"nombre": "🍌 Plátano", "desc": "Cultivo importante en Chocó"},
            {"nombre": "☕ Café", "desc": "Valle del Cauca, Cauca y Nariño"},
            {"nombre": "🍫 Cacao", "desc": "Presente en toda la región"},
            {"nombre": "🌱 Caña de Azúcar", "desc": "Principalmente en Valle del Cauca"},
            {"nombre": "🥑 Aguacate", "desc": "Valle del Cauca"},
            {"nombre": "🥔 Papa", "desc": "Cauca y Nariño"},
            {"nombre": "🌿 Yuca", "desc": "Chocó"},
            {"nombre": "🍇 Borojó", "desc": "Fruto característico del Chocó"},
        ],
        "departamentos": {
            "Chocó": ["plátano", "yuca", "arroz", "cacao", "borojó"],
            "Valle del Cauca": ["caña de azúcar", "café", "cacao", "aguacate"],
            "Cauca": ["café", "papa", "maíz", "caña panelera", "cacao"],
            "Nariño": ["papa", "café", "maíz", "cacao", "caña panelera"],
        }
    },
    "Andina": {
        "humedad": "60-80%",
        "est_humedad": "Varía según la altura",
        "temp": "14-24°C",
        "est_temp": "Clima templado a frío según la altitud",
        "precipitacion": "1.000-2.500 mm/año",
        "est_pre": "Dos temporadas de lluvia al año",
        "altitud": "1.000-3.000 m.s.n.m.",
        "est_alt": "Cordilleras y altiplanos",
        "imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSL7Scwv8-ge6UqAYNiD7HFANXA0cN6kMgEsKj_VAh5J2M9DFCD4nAz4RU&s=10",
        "cultivos": [
            {"nombre": "☕ Café", "desc": "Cultivo estrella de la región"},
            {"nombre": "🥑 Aguacate", "desc": "Muy importante en varios departamentos"},
            {"nombre": "🍌 Plátano / Banano", "desc": "Antioquia, Caldas, Quindío y Risaralda"},
            {"nombre": "🍫 Cacao", "desc": "Presente en casi toda la región"},
            {"nombre": "🥔 Papa", "desc": "Boyacá y Cundinamarca"},
            {"nombre": "🌾 Arroz", "desc": "Huila, Norte de Santander y Tolima"},
            {"nombre": "🍊 Cítricos", "desc": "Caldas, Quindío y Santander"},
            {"nombre": "🍍 Piña", "desc": "Santander"},
        ],
        "departamentos": {
            "Antioquia": ["café", "banano", "cacao", "aguacate", "caña panelera"],
            "Boyacá": ["papa", "cebolla", "zanahoria", "arveja", "maíz"],
            "Caldas": ["café", "plátano", "aguacate", "cítricos"],
            "Cundinamarca": ["papa", "fresa", "arveja", "tomate", "zanahoria"],
            "Huila": ["café", "arroz", "cacao", "maíz", "granadilla"],
            "Norte de Santander": ["café", "cacao", "arroz", "cebolla", "caña panelera"],
            "Quindío": ["café", "plátano", "aguacate", "cítricos"],
            "Risaralda": ["café", "plátano", "aguacate", "cacao"],
            "Santander": ["café", "cacao", "caña panelera", "piña", "cítricos"],
            "Tolima": ["arroz", "café", "maíz", "aguacate"],
        }
    },
    "Orinoquía": {
        "humedad": "70-85%",
        "est_humedad": "Alta en temporada de lluvias",
        "temp": "24-30°C",
        "est_temp": "Cálido con variación estacional marcada",
        "precipitacion": "1.500-3.000 mm/año",
        "est_pre": "Una sola temporada de lluvias intensa",
        "altitud": "100-500 m.s.n.m.",
        "est_alt": "Llanuras y sabanas",
        "imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT1lJDl20gjF7ynnz7DA7fbxoR5RPtxKHcJTC_5kKtAiA&s=10",
        "cultivos": [
            {"nombre": "🌾 Arroz", "desc": "Cultivo principal de la región"},
            {"nombre": "🌽 Maíz", "desc": "Presente en todos los departamentos"},
            {"nombre": "🌴 Palma de Aceite", "desc": "Casanare y Meta"},
            {"nombre": "🍌 Plátano", "desc": "Arauca"},
            {"nombre": "🌿 Yuca", "desc": "Arauca, Casanare y Vichada"},
            {"nombre": "🍫 Cacao", "desc": "Arauca y Meta"},
            {"nombre": "🌱 Soya", "desc": "Meta"},
            {"nombre": "🥜 Marañón", "desc": "Vichada"},
        ],
        "departamentos": {
            "Arauca": ["arroz", "plátano", "yuca", "maíz", "cacao"],
            "Casanare": ["arroz", "palma de aceite", "maíz", "yuca"],
            "Meta": ["arroz", "maíz", "soya", "cacao", "palma de aceite"],
            "Vichada": ["yuca", "maíz", "marañón"],
        }
    },
    "Amazónica": {
        "humedad": "80-90%",
        "est_humedad": "Alta y constante todo el año",
        "temp": "24-28°C",
        "est_temp": "Cálido húmedo ecuatorial",
        "precipitacion": "2.500-4.000 mm/año",
        "est_pre": "Lluvias frecuentes durante casi todo el año",
        "altitud": "100-400 m.s.n.m.",
        "est_alt": "Selva baja y planicies",
        "imagen": "https://colombia.co/sites/default/files/marca-pais/media/images/geografia-de-la-region-amazonica.webp",
        "cultivos": [
            {"nombre": "🌿 Yuca", "desc": "Base alimentaria de la Amazonia"},
            {"nombre": "🍌 Plátano", "desc": "Presente en varios departamentos"},
            {"nombre": "🍫 Cacao", "desc": "Caquetá, Guaviare y Putumayo"},
            {"nombre": "🍍 Piña", "desc": "Guainía, Guaviare y Vaupés"},
            {"nombre": "🌽 Maíz", "desc": "Caquetá y Guaviare"},
            {"nombre": "🍇 Copoazú / Arazá", "desc": "Frutos amazónicos (Amazonas)"},
            {"nombre": "🌴 Chontaduro", "desc": "Putumayo"},
            {"nombre": "🌳 Caucho", "desc": "Caquetá"},
        ],
        "departamentos": {
            "Amazonas": ["yuca", "plátano", "copoazú", "arazá", "cacao"],
            "Caquetá": ["cacao", "plátano", "yuca", "maíz", "caucho"],
            "Guainía": ["yuca", "piña", "ají", "frutas amazónicas"],
            "Guaviare": ["yuca", "cacao", "plátano", "piña", "maíz"],
            "Putumayo": ["cacao", "café", "plátano", "yuca", "chontaduro"],
            "Vaupés": ["yuca", "piña", "ají", "frutas amazónicas"],
        }
    },
    "Insular": {
        "humedad": "70-85%",
        "est_humedad": "Alta por influencia marina",
        "temp": "27-30°C",
        "est_temp": "Cálido tropical con brisa marina",
        "precipitacion": "1.000-1.800 mm/año",
        "est_pre": "Lluvias moderadas, influenciadas por el Caribe",
        "altitud": "0-100 m.s.n.m.",
        "est_alt": "Islas bajas de origen coralino",
        "imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSY2Hk6ANaJiH1AKcYKJoalUbnCrXKcEL-aYOGHG_5PIA&s=10",
        "cultivos": [
            {"nombre": "🥥 Coco", "desc": "Cultivo característico de las islas"},
            {"nombre": "🌿 Yuca", "desc": "Presente en las tres islas"},
            {"nombre": "🍠 Batata", "desc": "San Andrés, Providencia y Santa Catalina"},
            {"nombre": "🍌 Plátano", "desc": "Providencia"},
            {"nombre": "🍍 Frutas Tropicales", "desc": "Cultivos a pequeña escala"},
        ],
        "departamentos": {
            "San Andrés": ["coco", "yuca", "batata", "frutas tropicales"],
            "Providencia": ["coco", "yuca", "batata", "plátano", "frutas tropicales"],
            "Santa Catalina": ["yuca", "batata", "frutas locales"],
        }
    },
}

# Inicializar estados de sesión
if "sesion_activa" not in st.session_state:
    st.session_state.sesion_activa = None

# Contenedor para el logo y el título alineados horizontalmente
col_logo, col_titulo = st.columns([0.07, 0.93])
with col_logo:
    st.image(
        "https://raw.githubusercontent.com/garzap00/C-D-C/refs/heads/main/logo.jpeg",
        width=45,
    )
with col_titulo:
    st.markdown(
        "<h2 style='margin: 0; padding-top: 2px; color: #8fc148;'>C.D.C. | Campo Digital Colombia</h2>",
        unsafe_allow_html=True,
    )

# Menú de navegación horizontal debajo del título
menu = st.radio(
    "Navegación",
    ["Inicio & Dashboard", "💬 Foro y Red Social Agro"],
    horizontal=True,
    label_visibility="collapsed",
)
st.divider()

# SECCIÓN 1: INICIO & DASHBOARD
if menu == "Inicio & Dashboard":
    st.markdown(
        """
        <div class="hero">
            <span style="border: 1px solid rgba(255,255,255,.3); padding: 5px 12px; border-radius: 20px; font-size: 11px; text-transform: uppercase;">
                SENA • Proyecto Agropecuario
            </span>
            <h1 style="font-size: 38px; margin-top: 15px;">
                Sembramos Conocimiento y 
                <span style="color:#d1b052;">
                    Sembramos Futuro
                </span>
            </h1>
            <p style="font-size: 15px; color: #dce6df; max-width: 700px;">
                Tecnología e Información Agrícola al Alcance de Quienes Hacen Crecer el Campo Colombiano
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
    <style>
    .problem-solution {
        background: #f7f7ef;
        color: #183b2d;
        padding: 35px 30px;
        border-radius: 18px;
        margin-top: 25px;
        font-family: sans-serif;
    }
    .section-title {
        display: inline-block;
        background: #174b35;
        color: white;
        padding: 10px 22px;
        border-radius: 12px;
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 18px;
    }
    .section-title span {
        color: #f3c84b;
    }
    .section-text {
        font-size: 16px;
        line-height: 1.8;
        text-align: justify;
    }
    .info-card {
        background: #e8efdc;
        border-radius: 14px;
        padding: 16px 10px;
        text-align: center;
        min-height: 125px;
        margin-top: 10px;
        color: #214a35;
        border: 1px solid #dce7d1;
    }
    .info-card .symbol {
        font-size: 30px;
        margin-bottom: 8px;
    }
    .info-card p {
        font-size: 13px;
        line-height: 1.5;
        margin: 0;
    }
    .final-message {
        background: #f9e8a9;
        color: #214a35;
        padding: 20px;
        border-radius: 18px;
        line-height: 1.8;
        margin-top: 20px;
        border-left: 5px solid #d9b744;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="problem-solution">', unsafe_allow_html=True)

    # COLUMNA PROBLEMA
    col_problema, col_solucion = st.columns([1, 1.05], gap="large")
    with col_problema:
        st.markdown("""
        <div class="section-title">
            El <span>problema</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="section-text">
            Muchas personas del campo quieren cultivar sus propios
            alimentos, mejorar sus cosechas o comenzar un negocio
            agrícola, pero no saben por dónde empezar. Algunas
            desconocen qué cultivos se adaptan a su región, qué tipo
            de suelo necesitan, en qué época deben sembrar o cómo
            cuidar sus plantas.
            <br><br>
            Otras tienen dificultades para encontrar información
            confiable sobre cómo vender sus productos o resolver
            los problemas que aparecen durante el cultivo.
            <br><br>
            Esta falta de información puede provocar pérdidas de
            tiempo, dinero y cosechas. Además, en algunas zonas
            rurales es difícil acceder a internet o encontrar
            orientación adaptada al territorio.
        </div>
        """, unsafe_allow_html=True)

        tarjetas = [
            ("🌱", "No saben qué cultivos se adaptan a su región."),
            ("🌾", "Desconocen el tipo de suelo que necesitan."),
            ("📅", "No conocen la época adecuada para sembrar."),
            ("🐛", "Tienen problemas con sus cultivos y plagas."),
        ]
        tarjetas_cols = st.columns(2)
        for i, (icono, texto) in enumerate(tarjetas):
            with tarjetas_cols[i % 2]:
                st.markdown(f"""
                <div class="info-card">
                    <div class="symbol">{icono}</div>
                    <p>{texto}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("""
        <div class="section-text" style="margin-top:20px;">
            La falta de información puede dificultar el crecimiento
            de los proyectos agrícolas y afectar los ingresos de
            las familias campesinas.
        </div>
        """, unsafe_allow_html=True)

    # COLUMNA SOLUCIÓN
    with col_solucion:
        st.markdown("""
        <div class="section-title">
            La <span>solución</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="section-text">
            <b>C.D.C. (Campo Digital Colombia)</b> busca reducir
            estas dificultades mediante una página que reúne
            información útil para las personas del campo.
            <br><br>
            Permite aprender sobre los cultivos desde cero, conocer
            qué productos se pueden sembrar en diferentes regiones
            de Colombia y consultar recomendaciones para su cuidado.
            <br><br>
            También cuenta con un foro donde las personas pueden
            compartir sus dudas, responder preguntas de otros
            agricultores y buscar orientación sobre cultivos,
            ventas y otras actividades agrícolas.
        </div>
        """, unsafe_allow_html=True)
        st.image(
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRBZUj4GcnsYbycJV5Ed1urj89TPf2IAAuus6f8rqLVBA&s=10",
            use_container_width=True
        )
        st.markdown("""
        <div class="final-message">
            <b>🌱 Sembramos conocimiento, cosechamos futuro.</b>
            <br><br>
            Queremos que la falta de conocimientos o de orientación
            no sea un obstáculo para quienes desean trabajar la
            tierra, aprovechar mejor sus recursos y encontrar
            nuevas oportunidades en la agricultura.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h2>Regiones</h2><p style='color:#a48735; font-weight:800; font-size:12px; letter-spacing:2px; text-transform:uppercase;'>lo más sembrado</p>", unsafe_allow_html=True)

    # REGION CARIBE
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("<h3>Región Caribe</h3>", unsafe_allow_html=True)
            sc1, sc2 = st.columns(2)
            with sc1:
                st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQhHsBjVPxM9dPvIsgMiDSywqJIBIfxF7LWUYZZD-QUEg&s=10", use_container_width=True)
                st.markdown("<h4>Banano:</h4><p>El banano se cultiva en zonas cálidas, especialmente en Magdalena y La Guajira.</p>", unsafe_allow_html=True)
            with sc2:
                st.image("https://blog.mentta.com/wp-content/uploads/2024/06/pexels-daniel-dan-47825192-7543155-scaled.jpg", use_container_width=True)
                st.markdown("<h4>Yuca:</h4><p>Se cultiva en Bolívar, Córdoba, Sucre y Atlántico.</p>", unsafe_allow_html=True)

    # REGION PACIFICA
    with c2:
        with st.container(border=True):
            st.markdown("<h3>Región Pacífica</h3>", unsafe_allow_html=True)
            sc1, sc2 = st.columns(2)
            with sc1:
                st.image("https://mejorconsalud.as.com/wp-content/uploads/2022/09/cana-azucar-1.jpg", use_container_width=True)
                st.markdown("<h4>Caña de azúcar:</h4><p>Se cultiva principalmente en el Valle del Cauca.</p>", unsafe_allow_html=True)
            with sc2:
                st.image("https://dulcesdiabeticos.com/wp-content/uploads/2019/12/platano-y-diabetes-puede-un-diabetico-comer-platanos_opt.png", use_container_width=True)
                st.markdown("<h4>Plátano:</h4><p>Cultivado en zonas cálidas y húmedas como el Chocó.</p>", unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    # REGION ANDINA
    with s1:
        with st.container(border=True):
            st.markdown("<h3>Región Andina</h3>", unsafe_allow_html=True)
            ss1, ss2 = st.columns(2)
            with ss1:
                st.image("https://apasionadosporelcafe.com/wp-content/uploads/2021/11/shutterstock_559059673-1.jpg", use_container_width=True)
                st.markdown("<h4>Café:</h4><p>Tradicional de Antioquia, Huila, Caldas, Quindío y Risaralda.</p>", unsafe_allow_html=True)
            with ss2:
                st.image("https://cdn.portalfruticola.com/2020/09/91882f55-potatoes-2543686_1920.jpg", use_container_width=True)
                st.markdown("<h4>Papa:</h4><p>Principal en zonas frías de Boyacá, Cundinamarca y Nariño.</p>", unsafe_allow_html=True)

    # REGION ORINOQUIA
    with s2:
        with st.container(border=True):
            st.markdown("<h3>Región Orinoquía</h3>", unsafe_allow_html=True)
            ss1, ss2 = st.columns(2)
            with ss1:
                st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQyVJsiV9lFmNi3lJf4Bd4u5K6rsPKWWBkuHN-tk3sYAo0AtzQaUIVOSfE5&s=10", use_container_width=True)
                st.markdown("<h4>Arroz:</h4><p>Cultivado masivamente en Meta y Casanare.</p>", unsafe_allow_html=True)
            with ss2:
                st.image("https://www.microfertisa.com.co/wp-content/uploads/2021/04/Imagen-2-cultivo-palma-de-aceite-Microfertisa.jpg", use_container_width=True)
                st.markdown("<h4>Palma de Aceite:</h4><p>Desarrollada en las altillanuras del Meta.</p>", unsafe_allow_html=True)

    v1, v2 = st.columns(2)
    # REGION AMAZONIA
    with v1:
        with st.container(border=True):
            st.markdown("<h3>Región Amazonía</h3>", unsafe_allow_html=True)
            vs1, vs2 = st.columns(2)
            with vs1:
                st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRopDO0LRj2yZQLwBAibyEyJwTCgrPkPOq8joBMAYGKLBeD-asSOrw7e3h2&s=10", use_container_width=True)
                st.markdown("<h4>Cacao:</h4><p>Se cultiva en Caquetá y Putumayo.</p>", unsafe_allow_html=True)
            with vs2:
                st.image("https://radionacional-v3.s3.amazonaws.com/s3fs-public/node/article/field_image/Produccion%20de%20chontaduro.jpeg", use_container_width=True)
                st.markdown("<h4>Chontaduro:</h4><p>Fruto tropical de las comunidades amazónicas.</p>", unsafe_allow_html=True)

    # REGION INSULAR
    with v2:
        with st.container(border=True):
            st.markdown("<h3>Región Insular</h3>", unsafe_allow_html=True)
            vs1, vs2 = st.columns(2)
            with vs1:
                st.image("https://agrotendencia.tv/wp-content/uploads/2020/07/agrotendencia-agropedia-cultivo-de-coco-7.jpg", use_container_width=True)
                st.markdown("<h4>Coco:</h4><p>Propio de San Andrés y Providencia.</p>", unsafe_allow_html=True)
            with vs2:
                st.image("https://www.cocinadominicana.com/wp-content/uploads/2022/05/batata-mercado-dinamarca-DSC2578-2.jpg", use_container_width=True)
                st.markdown("<h4>Batata:</h4><p>Tubérculo adaptado a suelos tropicales sueltos.</p>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ========== SELECCIÓN DE REGIÓN + FOTO ABAJO ==========
    st.markdown("#### 🗺️ Seleccionar Región")
    territorio_elegido = st.selectbox("Región", list(DATOS_TERRITORIOS.keys()))
    info_region = DATOS_TERRITORIOS[territorio_elegido]

    # Foto debajo del selector
# Foto debajo del selector (controlando el ALTO)
    st.markdown(
       f"""
        <div style="text-align: center; margin: 15px 0;">
            <img src="{info_region['imagen']}" 
             style="max-height: 280px; width: auto; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />
            <p style="color: #555; font-size: 14px; margin-top: 8px; font-weight: 500;">
            Región {territorio_elegido}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### 📊 Datos Promedio de: *{territorio_elegido}*")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div style="color:#718077; font-size:13px;">Humedad del suelo</div><div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region["humedad"]}</div><small style="color:#2e7d32;">{info_region["est_humedad"]}</small></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div style="color:#718077; font-size:13px;">Temperatura </div><div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region["temp"]}</div><small style="color:#718077;">{info_region["est_temp"]}</small></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div style="color:#718077; font-size:13px;">Precipitación</div><div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region["precipitacion"]}</div><small style="color:#c8a64e;">{info_region["est_pre"]}</small></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card"><div style="color:#718077; font-size:13px;">Altitud</div><div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region["altitud"]}</div><small style="color:#2e7d32;">{info_region["est_alt"]}</small></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### 🌾 Cultivos Característicos en *{territorio_elegido.split(' ')[0]}*")

    # Mostrar cultivos en filas de 4 columnas
    cultivos = info_region["cultivos"]
    for i in range(0, len(cultivos), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(cultivos):
                cultivo = cultivos[i + j]
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"##### {cultivo['nombre']}")
                        st.write(cultivo["desc"])
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='color:#a48735; font-weight:800; font-size:12px; letter-spacing:2px; text-transform:uppercase;'>Campo Digital Colombia</p>", unsafe_allow_html=True)
    st.markdown("## Nuestro proyecto")
    st.write("Espacio de contacto para conocer la propuesta y continuar desarrollando herramientas digitales para el sector rural,y los directivos de la institucion y creadores de la pagina ")
    st.markdown("<br>", unsafe_allow_html=True)

    cc1, cc2, cc3 = st.columns(3)
    with cc2:
        with st.container(border=True):
            st.markdown("### Correo electrónico")
            st.write("campodigitalcolombia2@gmail.com")
            if st.button("Enviar correo"):
                st.info("Correo de contacto: campodigitalcolombia2@gmail.com")
    with cc1:
        with st.container(border=True):
            st.markdown("### Directivos de la institucion")
            st.write("rector-Gilberto Useche Gutiérrez")
            st.write("Cordinadoro-Carlos Andrés ramíres")
            st.write("Cordinadora-")
    with cc3:
        with st.container(border=True):
            st.markdown("### Creadores de C.D.C")
            st.write("-Gabriel Arturo Garzón Penagos")
            st.write("-Samuel Matias Gómez Carrillo")
            st.write("-Josse Luis Quimbayo Amaya ")
            st.write("-Sebastian David Mendez Ariza")
            st.write("-Sáhara Sofía Roberto Venegas")
# ==========================================
# SECCIÓN 2: FORO Y RED SOCIAL AGRO
# ==========================================
elif menu == "💬 Foro y Red Social Agro":
    st.markdown("## 💬 Comunidad y Foro Agropecuario - C.D.C.")
    st.write("Comparte experiencias, reporta datos de cosecha o interactúa con otros aprendices.")

    usuarios_registrados = obtener_usuarios_db()

    if st.session_state.sesion_activa is None:
        tab_l, tab_r = st.tabs(["Iniciar Sesión", "Registrarse"])
        with tab_l:
            email = st.text_input("Correo electrónico", key="l_mail")
            pwd = st.text_input("Contraseña", type="password", key="l_pwd")
            if st.button("Entrar", type="primary"):
                if email in usuarios_registrados and usuarios_registrados[email]["password"] == pwd:
                    st.session_state.sesion_activa = usuarios_registrados[email]["nombre"]
                    st.success("¡Bienvenido!")
                    st.rerun()
                else:
                    st.error("Datos incorrectos. (Usa: admin@sena.edu.co / 123)")
        with tab_r:
            r_nom = st.text_input("Nombre completo", key="r_nom")
            r_mail = st.text_input("Correo", key="r_mail")
            r_pwd = st.text_input("Contraseña", type="password", key="r_pwd")
            if st.button("Crear cuenta"):
                if not r_mail or not r_pwd or not r_nom:
                    st.error("Por favor completa todos los campos.")
                elif r_mail in usuarios_registrados:
                    st.error("El correo ya se encuentra registrado.")
                else:
                    exito = registrar_usuario_db(r_mail, r_pwd, r_nom)
                    if exito:
                        st.session_state.sesion_activa = r_nom
                        st.success("¡Cuenta creada con éxito y guardada en la base de datos!")
                        st.rerun()
                    else:
                        st.error("Hubo un error al registrarse en la base de datos.")
    else:
        col_u1, col_u2 = st.columns([3, 1])
        with col_u1:
            st.info(f"Conectado como: **{st.session_state.sesion_activa}**")
        with col_u2:
            if st.button("Cerrar Sesión"):
                st.session_state.sesion_activa = None
                st.rerun()

        with st.form("nuevo_post"):
            texto_foro = st.text_area("¿Qué deseas compartir sobre el campo hoy?")
            if st.form_submit_button("Publicar en la red"):
                if texto_foro.strip():
                    crear_post_db(st.session_state.sesion_activa, texto_foro)
                    st.success("¡Publicado en el foro!")
                    st.rerun()

        st.markdown("#### 📰 Muro de Publicaciones")
        posts_actuales = obtener_posts_db()
        for p in posts_actuales:
            post_id = p.get("id")
            with st.container(border=True):
                st.markdown(f"**👤 {p.get('usuario')}**")
                st.write(p.get("texto"))

                # Cargar respuestas/comentarios del post actual
                comentarios = obtener_comentarios_db(post_id) if post_id else []
                num_comentarios = len(comentarios)

                with st.expander(f"💬 Respuestas ({num_comentarios})"):
                    # Mostrar comentarios existentes
                    for c in comentarios:
                        st.markdown(f"↳ **{c.get('usuario')}**: {c.get('texto')}")

                    # Formulario para agregar una nueva respuesta
                    with st.form(f"form_resp_{post_id}"):
                        txt_respuesta = st.text_input("Escribe tu respuesta:", key=f"input_{post_id}")
                        if st.form_submit_button("Responder"):
                            if txt_respuesta.strip():
                                crear_comentario_db(post_id, st.session_state.sesion_activa, txt_respuesta)
                                st.success("¡Respuesta enviada!")
                                st.rerun()
