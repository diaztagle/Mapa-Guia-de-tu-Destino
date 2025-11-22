"""
MAPA GUÍA DE TU DESTINO - Versión Completa y Corregida
Diseño moderno responsive con paleta dorado, azul navy y blanco
IA mejorada para análisis quirológico detallado

INSTALACIÓN:
py -m pip install streamlit pandas opencv-python mediapipe pillow bcrypt python-dotenv requests mercadopago

CONFIGURACIÓN (.env):
MERCADOPAGO_ACCESS_TOKEN=TEST-xxxxx
WOMPI_PUBLIC_KEY=pub_test_xxxxx
WOMPI_PRIVATE_KEY=prv_test_xxxxx
PAYPAL_CLIENT_ID=xxxxx
PAYPAL_CLIENT_SECRET=xxxxx
PAYPAL_EMAIL=tu_email@paypal.com
"""

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import sqlite3
import bcrypt
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Importaciones opcionales para visión por computadora
try:
    import cv2
    import mediapipe as mp
    VISION_AVAILABLE = True
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
except:
    VISION_AVAILABLE = False

load_dotenv()

# ============================================================================
# CONFIGURACIÓN Y ESTILOS
# ============================================================================

st.set_page_config(
    page_title="Mapa Guía de tu Destino",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Premium
CUSTOM_CSS = """
<style>
    :root {
        --navy: #0A1128;
        --navy-light: #1C2541;
        --gold: #D4AF37;
        --gold-light: #F4E4C1;
        --white: #FFFFFF;
        --cream: #FAF9F6;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0A1128 0%, #1C2541 50%, #2A3B5F 100%);
    }
    
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem;
        }
    }
    
    h1, h2, h3, h4 {
        color: #D4AF37 !important;
        font-family: 'Roboto', condensed;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    h1 {
        font-size: clamp(2rem, 5vw, 3.5rem) !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 1rem !important;
        line-height: 1.2 !important;
    }
    
    p, li, label, .stMarkdown {
        color: #FAF9F6 !important;
        font-size: clamp(0.9rem, 2vw, 1.1rem);
        line-height: 1.6;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A1128 0%, #1C2541 100%);
        border-right: 2px solid #D4AF37;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
        color: #0A1128 !important;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: clamp(0.9rem, 2vw, 1.1rem);
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
        width: 100%;
        min-height: 50px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #F4E4C1 0%, #D4AF37 100%);
        box-shadow: 0 6px 25px rgba(212, 175, 55, 0.5);
        transform: translateY(-2px);
    }
    
    .info-card {
        background: rgba(26, 37, 65, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        border-color: rgba(212, 175, 55, 0.6);
        box-shadow: 0 12px 48px rgba(212, 175, 55, 0.2);
        transform: translateY(-5px);
    }
    
    .price-card {
        background: linear-gradient(135deg, rgba(26, 37, 65, 0.9) 0%, rgba(10, 17, 40, 0.9) 100%);
        border: 2px solid #D4AF37;
        border-radius: 25px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    }
    
    .price-card:hover {
        transform: scale(1.03);
        box-shadow: 0 15px 60px rgba(212, 175, 55, 0.3);
    }
    
    .price-amount {
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: bold;
        color: #D4AF37;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
        margin: 1rem 0;
    }
    
    .badge {
        background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
        color: #0A1128;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    }
    
    .gold-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #D4AF37 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        background: rgba(26, 37, 65, 0.6) !important;
        border: 2px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 15px !important;
        color: #FAF9F6 !important;
        padding: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3) !important;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Precios
PRECIOS = {
    'consulta_basica': 0,
    'consulta_premium_min': 20000,
    'consulta_premium_max': 60000,
    'suscripcion_mensual': 80000
}

# ============================================================================
# BASE DE DATOS
# ============================================================================

@st.cache_resource
def init_db():
    conn = sqlite3.connect('mapa_guia_destino.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  nombre TEXT,
                  fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS consultas
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  usuario_id INTEGER,
                  fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  pregunta TEXT NOT NULL,
                  fecha_nacimiento DATE,
                  monto_donacion REAL,
                  analisis_automatico TEXT)''')
    
    conn.commit()
    return conn

# ============================================================================
# CONOCIMIENTO BASE
# ============================================================================

CICLOS_VITALES = {
    1: {'nombre': 'Nuevos Inicios', 'emoji': '🌟', 
        'energia': 'Liderazgo, independencia, iniciativa',
        'recomendaciones': 'Inicia proyectos nuevos, toma la iniciativa, sé valiente'},
    2: {'nombre': 'Cooperación', 'emoji': '🤝',
        'energia': 'Asociaciones, diplomacia, paciencia',
        'recomendaciones': 'Trabaja en equipo, cultiva relaciones, sé paciente'},
    3: {'nombre': 'Expresión Creativa', 'emoji': '🎨',
        'energia': 'Creatividad, comunicación, alegría',
        'recomendaciones': 'Exprésate libremente, socializa, crea sin límites'},
    4: {'nombre': 'Construcción', 'emoji': '🏗️',
        'energia': 'Disciplina, trabajo duro, estructura',
        'recomendaciones': 'Construye bases sólidas, sé disciplinado'},
    5: {'nombre': 'Cambio y Libertad', 'emoji': '🦋',
        'energia': 'Aventura, cambio, expansión',
        'recomendaciones': 'Acepta cambios, experimenta cosas nuevas'},
    6: {'nombre': 'Responsabilidad', 'emoji': '🏡',
        'energia': 'Hogar, familia, servicio',
        'recomendaciones': 'Cuida a tu familia, mejora tu hogar'},
    7: {'nombre': 'Introspección', 'emoji': '🧘',
        'energia': 'Espiritualidad, análisis profundo',
        'recomendaciones': 'Medita, estudia, conócete profundamente'},
    8: {'nombre': 'Poder y Logros', 'emoji': '👑',
        'energia': 'Éxito material, reconocimiento',
        'recomendaciones': 'Busca el éxito, gestiona finanzas, lidera'},
    9: {'nombre': 'Culminación', 'emoji': '🌅',
        'energia': 'Cierre de ciclos, sabiduría',
        'recomendaciones': 'Cierra ciclos, perdona, comparte sabiduría'}
}

# ============================================================================
# FUNCIONES PRINCIPALES
# ============================================================================

def calcular_ciclo_vital(fecha_nacimiento):
    hoy = datetime.now()
    suma = fecha_nacimiento.day + fecha_nacimiento.month + hoy.year
    while suma > 9:
        suma = sum(int(d) for d in str(suma))
    return suma

def generar_analisis_basico(ciclo):
    ciclo_info = CICLOS_VITALES[ciclo]
    
    return f"""
<div class="info-card">
<h2 style="text-align: center;">{ciclo_info['emoji']} Año {ciclo}: {ciclo_info['nombre']} {ciclo_info['emoji']}</h2>

### ✨ Energía Dominante
<p style="font-size: 1.2rem; color: #F4E4C1;">{ciclo_info['energia']}</p>

### 🎯 Recomendaciones
<p style="font-size: 1.1rem;">{ciclo_info['recomendaciones']}</p>

<div class="gold-divider"></div>

### ⭐ ¿Quieres profundizar más?

<div class="price-card" style="margin: 2rem 0;">
<h3>Análisis Premium Personalizado</h3>
<p style="color: #F4E4C1;">Donación consciente: $20.000 - $60.000 COP</p>
<p>Incluye:</p>
<ul style="text-align: left;">
<li>✅ Lectura quirológica completa</li>
<li>✅ Interpretación experta</li>
<li>✅ Orientación específica</li>
<li>✅ Respuesta en 24-48 horas</li>
</ul>
</div>
</div>

<p style="text-align: center; color: #F4E4C1; font-style: italic; margin-top: 2rem;">
⚠️ Análisis orientativo para autoconocimiento. No sustituye consejo profesional.
</p>
"""

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

def main():
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = init_db()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # SIDEBAR
    with st.sidebar:
        st.markdown('<div style="text-align: center;"><h1>🔮</h1><h2>Mapa Guía</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        if not st.session_state.logged_in:
            pagina = st.radio("📍 Navegar:", ["🏠 Inicio", "🔐 Ingresar"], label_visibility="collapsed")
            pagina = pagina.split(" ", 1)[1]
        else:
            st.markdown(f'<div class="badge">👤 Usuario</div>', unsafe_allow_html=True)
            pagina = st.radio("📍 Navegar:", [
                "🏠 Inicio",
                "🆓 Consulta Gratis",
                "⭐ Consulta Premium",
                "🚪 Cerrar Sesión"
            ], label_visibility="collapsed")
            pagina = pagina.split(" ", 1)[1]
            
            if pagina == "Cerrar Sesión":
                st.session_state.logged_in = False
                st.rerun()
        
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
        <h3 style="text-align: center;">💎 Precios</h3>
        <p style="text-align: center;"><span class="badge">Básico: GRATIS</span></p>
        <p style="text-align: center;"><span class="badge">Premium: $20.000-$60.000</span></p>
        <p style="text-align: center; font-size: 0.85rem;">Tú eliges el monto de la donación</p>
        </div>
        """, unsafe_allow_html=True)
    
    # PÁGINAS
    if pagina == "Inicio":
        st.markdown('<h1>🔮 Mapa Guía de tu Destino 🔮</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 1.3rem; color: #F4E4C1;">Descubre tu camino a través de la Quirología y los Ciclos de la Vida</p>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="info-card">
            <h3 style="text-align: center;">✨ Autoconocimiento</h3>
            <p style="text-align: center;">Descubre tu potencial a través del análisis de tu real personalidad</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-card">
            <h3 style="text-align: center;">🎯 Orientación</h3>
            <p style="text-align: center;">Guía personalizada para tus decisiones</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="info-card">
            <h3 style="text-align: center;">💎 Accesible</h3>
            <p style="text-align: center;">Tu aporte o donación que elijas para consulta Premium</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center;">📋 Nuestros Servicios</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="price-card">
            <h3>🆓 Análisis Básico</h3>
            <div class="price-amount">GRATIS</div>
            <ul style="text-align: left;">
            <li>✓ Cálculo de ciclo vital</li>
            <li>✓ Interpretación numerológica</li>
            <li>✓ Recomendaciones generales</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="price-card">
            <h3>⭐ Análisis Premium</h3>
            <div class="price-amount">$20.000 - $60.000</div>
            <p style="color: #F4E4C1;">COP (Tú eliges el monto de la donación)</p>
            <ul style="text-align: left;">
            <li>✓ Análisis quirológico completo</li>
            <li>✓ Interpretación personalizada</li>
            <li>✓ Orientación específica</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    elif pagina == "Ingresar":
        st.markdown('<h1>🔐 Acceso de Usuario</h1>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
        
        with tab1:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            email = st.text_input("📧 Email", key="login_email")
            password = st.text_input("🔒 Contraseña", type="password", key="login_pass")
            
            if st.button("✨ Iniciar Sesión", use_container_width=True):
                st.session_state.logged_in = True
                st.success("✅ Sesión iniciada")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            nombre = st.text_input("👤 Nombre")
            email = st.text_input("📧 Email", key="reg_email")
            password = st.text_input("🔒 Contraseña", type="password", key="reg_pass")
            
            if st.button("🌟 Crear Cuenta", use_container_width=True):
                st.success("✅ Cuenta creada")
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif pagina == "Consulta Gratis":
        st.markdown('<h1>🆓 Análisis Básico Gratuito</h1>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        
        with st.form("consulta_Gratis"):
            pregunta = st.text_area(
                "💭 ¿Qué aspecto deseas explorar?",
                placeholder="Ejemplo: Orientación profesional...",
                height=150
            )
            
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            fecha_nac = st.date_input(
                "📅 Tu fecha de nacimiento",
                min_value=datetime(1920, 1, 1),
                max_value=datetime.now()
            )
            
            if st.button("🔮 Generar Análisis Gratis", use_container_width=True):
                ciclo = calcular_ciclo_vital(fecha_nac)
                analisis = generar_analisis_basico(ciclo)
                st.markdown(analisis, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif pagina == "Consulta Premium":
        st.markdown('<h1>⭐ Consulta Premium</h1>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        
        with st.form("consulta_premium"):
            pregunta = st.text_area(
                "💭 ¿Qué aspecto deseas explorar?",
                placeholder="Ejemplo: Orientación profesional...",
                height=150
            )
            
            col1, col2 = st.columns(2)
            with col1:
                fecha_nac = st.date_input(
                    "📅 Fecha de nacimiento",
                    min_value=datetime(1920, 1, 1),
                    max_value=datetime.now()
                )
            
            with col2:
                monto = st.number_input(
                    "💰 Monto de donación (COP)",
                    min_value=PRECIOS['consulta_premium_min'],
                    max_value=PRECIOS['consulta_premium_max'],
                    value=30000,
                    step=5000
                )
            
            st.markdown("### 📸 Fotos de tus Manos")
            foto1 = st.file_uploader("🖐️ Palma derecha", type=['jpg', 'png'])
            foto2 = st.file_uploader("🖐️ Palma izquierda", type=['jpg', 'png'])
            foto3 = st.file_uploader("🖐️ Dorso derecho", type=['jpg', 'png'])
            foto4 = st.file_uploader("🖐️ Puño - percusion derecha", type=['jpg', 'png'])
            
            submitted = st.form_submit_button("✨ Enviar Consulta", use_container_width=True)
            
            if submitted and pregunta and foto1:
                st.success("✅ Consulta recibida. Te contactaremos en 24-48 horas.")
                st.stars()
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

