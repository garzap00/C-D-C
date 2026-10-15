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
    "Meta (Altillanura)": {
        "humedad": "72%",
        "est_humedad": "Óptimo para arroz/palma",
        "temp": "28.5°C",
        "est_temp": "Clima cálido seco",
        "hectareas": "3,450 Ha",
        "productores": "520 Líderes",
        "cultivos": [
            {"nombre": "🍌 Plátano y Yuca", "desc": "Principal renglón de la altillanura"},
            {"nombre": "🌽 Maíz Tecnificado", "desc": "Siembra masiva con maquinaria"},
            {"nombre": "🌾 Arroz de Riego", "desc": "Altos rendimientos por hectárea"},
            {"nombre": "🌴 Palma de Aceite", "desc": "Cultivo agroindustrial dinámico"},
        ],
    },
    "Eje Cafetero": {
        "humedad": "64%",
        "est_humedad": "Ideal para zona montañosa",
        "temp": "19.2°C",
        "est_temp": "Clima templado húmedo",
        "hectareas": "2,890 Ha",
        "productores": "840 Líderes",
        "cultivos": [
            {"nombre": "☕ Café Especial", "desc": "Granos suaves de exportación"},
            {"nombre": "🥑 Aguacate Hass", "desc": "Crecimiento de producción"},
            {"nombre": "🍊 Cítricos Dulces", "desc": "Naranja y mandarina en ladera"},
            {"nombre": "🍌 Plátano Intercalado", "desc": "Sombra y sombrío tradicional"},
        ],
    },
    "Antioquia (Urabá/Centro)": {
        "humedad": "81%",
        "est_humedad": "Humedad alta constante",
        "temp": "27.0°C",
        "est_temp": "Cálido tropical",
        "hectareas": "4,120 Ha",
        "productores": "960 Líderes",
        "cultivos": [
            {"nombre": "🍌 Banano de Exportación", "desc": "Motor económico regional"},
            {"nombre": "🥑 Aguacate de Altura", "desc": "Oriente antioqueño"},
            {"nombre": "🥔 Papa Criolla", "desc": "Zonas frías de meseta"},
            {"nombre": "🥛 Ganadería Lechera", "desc": "Sistemas intensivos de leche"},
        ],
    },
    "Valle del Cauca": {
        "humedad": "60%",
        "est_humedad": "Riego controlado",
        "temp": "25.8°C",
        "est_temp": "Cálido moderado",
        "hectareas": "5,300 Ha",
        "productores": "610 Líderes",
        "cultivos": [
            {"nombre": "🌱 Caña de Azúcar", "desc": "Agroindustria del valle geográfico"},
            {"nombre": "🍇 Frutales y Uva", "desc": "Zonas de microclima especial"},
            {"nombre": "🍍 Piña Oro Miel", "desc": "Demanda nacional e internacional"},
            {"nombre": "🌽 Maíz y Soya", "desc": "Rotación de suelos eficiente"},
        ],
    },
    "Costa Caribe": {
        "humedad": "55%",
        "est_humedad": "Monitoreo por sequía",
        "temp": "31.2°C",
        "est_temp": "Cálido árido/semiárido",
        "hectareas": "3,100 Ha",
        "productores": "450 Líderes",
        "cultivos": [
            {"nombre": "🐮 Ganadería Doble Propósito", "desc": "Carne y leche adaptada"},
            {"nombre": "🌴 Palma y Ñame", "desc": "Seguridad e industria"},
            {"nombre": "🌽 Maíz Tradicional", "desc": "Cultivo de ciclo corto"},
            {"nombre": "🥭 Mango de Azúcar", "desc": "Producción frutícola costera"},
        ],
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
        color: #29465b;
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
            ("📶", "En algunas zonas es difícil acceder a internet.")
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
            "https://images.unsplash.com/photo-1595974482597-4f6c1cfc8d62?auto=format&fit=crop&w=800&q=80",
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
# CAMBIAR SELEC REGION PARA DATOS    
    st.markdown("#### 🗺️ Seleccionar Territorio y Parámetros")
    col_t1, col_t2, col_t3 = st.columns(3)

    with col_t1:
        territorio_elegido = st.selectbox("Departamento / Región", list(DATOS_TERRITORIOS.keys()))

    with col_t2:
        cultivo_filtro = st.selectbox("Filtrar por Orientación", ["Todos los sistemas", "Tecnificado", "Tradicional", "Agroindustrial"])

    with col_t3:
        metrica_filtro = st.selectbox("Métrica de Enfoque", ["Humedad del Suelo", "Temperatura Promedio", "Área Cultivada"])

    info_region = DATOS_TERRITORIOS[territorio_elegido]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### 📊 Datos en Tiempo Real: *{territorio_elegido}*")
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div style="color:#718077; font-size:13px;">Humedad Promedio</div><div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region["humedad"]}</div><small style="color:#2e7d32;">{info_region["est_humedad"]}</small></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div style="color:#718077; font-size:13px;">Temperatura Suelo</div><div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region["temp"]}</div><small style="color:#718077;">{info_region["est_temp"]}</small></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div style="color:#718077; font-size:13px;">Áreas Registradas</div><div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region["hectareas"]}</div><small style="color:#c8a64e;">Sensores Activos</small></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card"><div style="color:#718077; font-size:13px;">Productores Conectados</div><div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region["productores"]}</div><small style="color:#2e7d32;">Comunidad SENA</small></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### 🌾 Cultivos Característicos en *{territorio_elegido.split(' ')[0]}*")

    rc1, rc2, rc3, rc4 = st.columns(4)
    cols = [rc1, rc2, rc3, rc4]

    for index, cultivo in enumerate(info_region["cultivos"]):
        with cols[index]:
            with st.container(border=True):
                st.markdown(f"##### {cultivo['nombre']}")
                st.write(cultivo["desc"])

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("<p style='color:#a48735; font-weight:800; font-size:12px; letter-spacing:2px; text-transform:uppercase;'>Campo Digital Colombia</p>", unsafe_allow_html=True)
    st.markdown("## Conecta con el proyecto")
    st.write("Espacio de contacto para conocer la propuesta y continuar desarrollando herramientas digitales para el sector rural.")
    st.markdown("<br>", unsafe_allow_html=True)

    cc1, cc2 = st.columns(2)
    with cc1:
        with st.container(border=True):
            st.markdown("### Correo electrónico")
            st.write("campodigitalcolombia2@gmail.com")
            if st.button("Enviar correo"):
                st.info("Correo de contacto: campodigitalcolombia2@gmail.com")

    with cc2:
        with st.container(border=True):
            st.markdown("### Villavicencio, Meta")
            st.write("C.D.C. tiene como referencia territorial inicial Villavicencio y el departamento del Meta.")
            st.link_button("Abrir en Google Maps", "https://www.google.com/maps/place/Villavicencio,+Meta")

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
