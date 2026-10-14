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
if "posts" not in st.session_state:
    st.session_state.posts = [{
        "usuario": "Carlos Agrónomo",
        "avatar": "🌾",
        "texto": "Excelente producción en la altillanura. El campo colombiano avanza con tecnología.",
    }]

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

    # Introducción y Título principal
    st.markdown("<p style='color:#a48735; font-weight:800; font-size:12px; letter-spacing:2px; text-transform:uppercase;'>Introducción</p><h2>Regiones</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.markdown("<h3>Región Caribe:</h3><h4>Banano:</h4><p> El banano se cultiva en zonas cálidas, especialmente en Magdalena y La Guajira. Necesita agua constante, suelo fértil y cuidados para crecer. Se consume fresco y también se vende a otros países.</p>", unsafe_allow_html=True)
    # Cultivos de referencia
    st.markdown("<p style='color:#a48735; font-weight:800; font-size:12px; letter-spacing:2px; text-transform:uppercase;'>Producción Agrícola</p><h2>Cultivos de referencia</h2>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        with st.container(border=True):
            st.image(
                "https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=600&q=80",
                use_container_width=True,
            )
            st.markdown("### Maíz")
            st.write("Cultivo de importancia alimentaria y productiva, adaptable a diferentes sistemas agrícolas.")
            st.markdown("---")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.caption("Suelo\nBien drenado")
                st.caption("Clima\nCálido")
            with sc2:
                st.caption("Agua\nModerada")
                st.caption("Uso\nAlimentación")

    with c2:
        with st.container(border=True):
            st.image(
                "https://mareterracoffee.com/wp-content/uploads/2022/11/Planta-de-cafe--e1767865783596.png",
                use_container_width=True,
            )
            st.markdown("### Café")
            st.write("Sistema productivo asociado a zonas con condiciones climáticas y altitudinales particulares.")
            st.markdown("---")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.caption("Suelo\nDrenado")
                st.caption("Clima\nTemplado")
            with sc2:
                st.caption("Agua\nDisponible")
                st.caption("Uso\nComercial")

    with c3:
        with st.container(border=True):
            st.image(
                "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSgrsv2ZUeqLtcPtGEyfsP0h9jNDsZtuHtKwbC_1TyQtQ&s",
                use_container_width=True,
            )
            st.markdown("### Plátano")
            st.write("Cultivo tropical que requiere disponibilidad de agua y condiciones adecuadas de temperatura.")
            st.markdown("---")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.caption("Suelo\nFértil")
                st.caption("Clima\nTropical")
            with sc2:
                st.caption("Agua\nAlta")
                st.caption("Uso\nAlimentación")

    with c4:
        with st.container(border=True):
            st.image(
                "https://grandsur.com/wp-content/uploads/2021/02/GrandSur-Our-Products-ASSS.jpg",
                use_container_width=True,
            )
            st.markdown("### Cacao")
            st.write("Sistema productivo tropical que requiere condiciones adecuadas de humedad, temperatura y suelo.")
            st.markdown("---")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.caption("Suelo\nProfundo")
                st.caption("Clima\nTropical")
            with sc2:
                st.caption("Agua\nDisponible")
                st.caption("Uso\nComercial")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- PANEL DE CONTROL Y FILTROS ---
    st.markdown("#### 🗺️ Seleccionar Territorio y Parámetros")
    col_t1, col_t2, col_t3 = st.columns(3)

    with col_t1:
        territorio_elegido = st.selectbox(
            "Departamento / Región", list(DATOS_TERRITORIOS.keys())
        )

    with col_t2:
        cultivo_filtro = st.selectbox(
            "Filtrar por Orientación",
            ["Todos los sistemas", "Tecnificado", "Tradicional", "Agroindustrial"],
        )

    with col_t3:
        metrica_filtro = st.selectbox(
            "Métrica de Enfoque",
            ["Humedad del Suelo", "Temperatura Promedio", "Área Cultivada"],
        )

    info_region = DATOS_TERRITORIOS[territorio_elegido]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### 📊 Datos en Tiempo Real: *{territorio_elegido}*")

    # --- TARJETAS KPI ---
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div style="color:#718077; font-size:13px;">Humedad Promedio</div>
                <div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region['humedad']}</div>
                <small style="color:#2e7d32;">{info_region['est_humedad']}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div style="color:#718077; font-size:13px;">Temperatura Suelo</div>
                <div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region['temp']}</div>
                <small style="color:#718077;">{info_region['est_temp']}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div style="color:#718077; font-size:13px;">Áreas Registradas</div>
                <div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region['hectareas']}</div>
                <small style="color:#c8a64e;">Sensores Activos</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with k4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div style="color:#718077; font-size:13px;">Productores Conectados</div>
                <div style="font-size:26px; font-weight:800; margin:5px 0; color:#10271c;">{info_region['productores']}</div>
                <small style="color:#2e7d32;">Comunidad SENA</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

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

    # --- SECCIÓN CONTACTO ---
    st.markdown(
        "<p style='color:#a48735; font-weight:800; font-size:12px; letter-spacing:2px; text-transform:uppercase;'>Campo Digital Colombia</p>",
        unsafe_allow_html=True,
    )
    st.markdown("## Conecta con el proyecto")
    st.write(
        "Espacio de contacto para conocer la propuesta y continuar desarrollando herramientas digitales para el sector rural."
    )
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
            st.write(
                "C.D.C. tiene como referencia territorial inicial Villavicencio y el departamento del Meta."
            )
            st.link_button(
                "Abrir en Google Maps",
                "https://www.google.com/maps/place/Villavicencio,+Meta",
            )

# ==========================================
# SECCIÓN 2: FORO Y RED SOCIAL AGRO
# ==========================================
elif menu == "💬 Foro y Red Social Agro":
    st.markdown("## 💬 Comunidad y Foro Agropecuario - C.D.C.")
    st.write(
        "Comparte experiencias, reporta datos de cosecha o interactúa con otros aprendices."
    )

    usuarios_registrados = obtener_usuarios_db()

    if st.session_state.sesion_activa is None:
        tab_l, tab_r = st.tabs(["Iniciar Sesión", "Registrarse"])

        with tab_l:
            email = st.text_input("Correo electrónico", key="l_mail")
            pwd = st.text_input("Contraseña", type="password", key="l_pwd")
            if st.button("Entrar", type="primary"):
                if (
                    email in usuarios_registrados
                    and usuarios_registrados[email]["password"] == pwd
                ):
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
                        st.success(
                            "¡Cuenta creada con éxito y guardada en la base de datos!"
                        )
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
                    st.session_state.posts.insert(
                        0,
                        {
                            "usuario": st.session_state.sesion_activa,
                            "avatar": "🧑‍🌾",
                            "texto": texto_foro,
                        },
                    )
                    st.success("¡Publicado!")
                    st.rerun()

        st.markdown("#### 📰 Muro de Publicaciones")
        for p in st.session_state.posts:
            with st.container(border=True):
                st.markdown(f"**{p['avatar']} {p['usuario']}**")
                st.write(p["texto"])
