"""
MAPA GUÍA DE TU DESTINO - Versión Premium Design Mejorada
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
import cv2
import mediapipe as mp
import sqlite3
import bcrypt
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURACIÓN Y ESTILOS PREMIUM RESPONSIVE
# ============================================================================

st.set_page_config(
    page_title="Mapa Guía de tu Destino",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Premium Mejorado - Responsive y Simétrico
CUSTOM_CSS = """
<style>
    /* Paleta de colores */
    :root {
        --navy: #0A1128;
        --navy-light: #1C2541;
        --gold: #D4AF37;
        --gold-light: #F4E4C1;
        --white: #FFFFFF;
        --cream: #FAF9F6;
    }
    
    /* Fondo principal con gradiente */
    .stApp {
        background: linear-gradient(135deg, #0A1128 0%, #1C2541 50%, #2A3B5F 100%);
    }
    
    /* Contenedor principal responsive */
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
    
    /* Títulos dorados con jerarquía clara */
    h1, h2, h3, h4 {
        color: #D4AF37 !important;
        font-family: 'Georgia', serif;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    h1 {
        font-size: clamp(2rem, 5vw, 3.5rem) !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 1rem !important;
        line-height: 1.2 !important;
    }
    
    h2 {
        font-size: clamp(1.5rem, 4vw, 2.5rem) !important;
        margin: 1.5rem 0 1rem 0 !important;
    }
    
    h3 {
        font-size: clamp(1.2rem, 3vw, 1.8rem) !important;
    }
    
    /* Texto general legible */
    p, li, label, .stMarkdown {
        color: #FAF9F6 !important;
        font-size: clamp(0.9rem, 2vw, 1.1rem);
        line-height: 1.6;
    }
    
    /* Sidebar elegante y responsive */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A1128 0%, #1C2541 100%);
        border-right: 2px solid #D4AF37;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: #D4AF37 !important;
        text-align: center;
        padding: 1rem 0;
    }
    
    /* Botones premium SIMÉTRICOS con hover */
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
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Cards UNIFORMES con efecto cristal */
    .info-card {
        background: rgba(26, 37, 65, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .info-card:hover {
        border-color: rgba(212, 175, 55, 0.6);
        box-shadow: 0 12px 48px rgba(212, 175, 55, 0.2);
        transform: translateY(-5px);
    }
    
    @media (max-width: 768px) {
        .info-card {
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
    }
    
    /* Inputs elegantes uniformes */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        background: rgba(26, 37, 65, 0.6) !important;
        border: 2px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 15px !important;
        color: #FAF9F6 !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stDateInput > div > div > input:focus {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3) !important;
        background: rgba(26, 37, 65, 0.9) !important;
    }
    
    /* Labels consistentes */
    label {
        color: #F4E4C1 !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Tarjetas de precios SIMÉTRICAS */
    .price-card {
        background: linear-gradient(135deg, rgba(26, 37, 65, 0.9) 0%, rgba(10, 17, 40, 0.9) 100%);
        border: 2px solid #D4AF37;
        border-radius: 25px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
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
    
    /* Badges uniformes */
    .badge {
        background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
        color: #0A1128;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
        font-size: clamp(0.8rem, 2vw, 1rem);
    }
    
    /* Tabs modernos y consistentes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(26, 37, 65, 0.6);
        padding: 1rem;
        border-radius: 15px;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: 2px solid rgba(212, 175, 55, 0.3);
        border-radius: 10px;
        color: #FAF9F6;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        min-width: 150px;
        text-align: center;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #D4AF37;
        background: rgba(212, 175, 55, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
        color: #0A1128 !important;
        border-color: #D4AF37;
        font-weight: 600;
    }
    
    /* Radio buttons mejorados */
    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .stRadio > div > label {
        background: rgba(26, 37, 65, 0.6);
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid rgba(212, 175, 55, 0.3);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stRadio > div > label:hover {
        border-color: #D4AF37;
        background: rgba(212, 175, 55, 0.1);
        transform: translateX(5px);
    }
    
    /* File uploader consistente */
    [data-testid="stFileUploader"] {
        background: rgba(26, 37, 65, 0.6);
        border: 2px dashed rgba(212, 175, 55, 0.5);
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #D4AF37;
        background: rgba(212, 175, 55, 0.1);
    }
    
    /* Alertas estilizadas */
    .stAlert {
        background: rgba(26, 37, 65, 0.8) !important;
        border-left: 4px solid #D4AF37 !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px);
    }
    
    /* Success, info, warning colores */
    [data-baseweb="notification"] {
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    /* Expander consistente */
    .streamlit-expanderHeader {
        background: rgba(26, 37, 65, 0.8);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 10px;
        color: #D4AF37 !important;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #D4AF37;
        background: rgba(212, 175, 55, 0.1);
    }
    
    /* Scrollbar dorado */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0A1128;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #D4AF37 0%, #C19A2E 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #F4E4C1;
    }
    
    /* Animaciones suaves */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Separador dorado elegante */
    .gold-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #D4AF37 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    /* Grid responsive para columnas */
    .stColumn {
        padding: 0 0.5rem;
    }
    
    @media (max-width: 768px) {
        .stColumn {
            padding: 0.5rem 0;
        }
    }
    
    /* Imágenes responsive */
    img {
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Spinner personalizado */
    .stSpinner > div {
        border-top-color: #D4AF37 !important;
    }
    
    /* Link buttons consistentes */
    .stLinkButton > a {
        background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
        color: #0A1128 !important;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        text-decoration: none;
        font-weight: 600;
        display: inline-block;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    }
    
    .stLinkButton > a:hover {
        background: linear-gradient(135deg, #F4E4C1 0%, #D4AF37 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(212, 175, 55, 0.5);
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Configuración de precios
PRECIOS = {
    'consulta_basica': 0,
    'consulta_premium_min': 20000,
    'consulta_premium_max': 60000,
    'suscripcion_mensual': 80000
}

# ============================================================================
# MEDIAPIPE INICIALIZACIÓN
# ============================================================================

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

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
                  es_premium INTEGER DEFAULT 0,
                  fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS consultas
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  usuario_id INTEGER,
                  fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  pregunta TEXT NOT NULL,
                  fecha_nacimiento DATE,
                  tipo_consulta TEXT DEFAULT 'basica',
                  estado_pago TEXT DEFAULT 'pendiente',
                  metodo_pago TEXT,
                  monto_donacion REAL,
                  referencia_pago TEXT,
                  analisis_automatico TEXT,
                  interpretacion_personal TEXT,
                  FOREIGN KEY (usuario_id) REFERENCES usuarios (id))''')
    
    conn.commit()
    return conn

# ============================================================================
# CONOCIMIENTO BASE AMPLIADO
# ============================================================================

CICLOS_VITALES = {
    1: {
        'nombre': 'Nuevos Inicios',
        'emoji': '🌟',
        'energia': 'Liderazgo, independencia, iniciativa y valentía',
        'recomendaciones': 'Es tu momento de iniciar proyectos nuevos, tomar la iniciativa sin esperar a otros, ser valiente en tus decisiones y confiar en tu capacidad de liderazgo',
        'desafios': 'Evita la arrogancia, el egoísmo y la impaciencia',
        'oportunidades': 'Emprendimiento, liderazgo, nuevos comienzos profesionales',
        'areas_clave': 'Carrera, proyectos personales, auto-afirmación'
    },
    2: {
        'nombre': 'Cooperación',
        'emoji': '🤝',
        'energia': 'Asociaciones, diplomacia, paciencia y sensibilidad',
        'recomendaciones': 'Trabaja en equipo, cultiva relaciones significativas, sé paciente con los procesos y practica la escucha activa',
        'desafios': 'No te pierdas en complacer a otros, mantén tus límites',
        'oportunidades': 'Sociedades, matrimonio, colaboraciones exitosas',
        'areas_clave': 'Relaciones, partnerships, trabajo en equipo'
    },
    3: {
        'nombre': 'Expresión Creativa',
        'emoji': '🎨',
        'energia': 'Creatividad, comunicación, alegría y expansión social',
        'recomendaciones': 'Exprésate libremente sin miedo al juicio, socializa activamente, crea sin límites y disfruta el momento presente',
        'desafios': 'Evita dispersarte en muchas direcciones, mantén el enfoque',
        'oportunidades': 'Arte, escritura, oratoria, redes sociales, marketing',
        'areas_clave': 'Creatividad, comunicación, vida social'
    },
    4: {
        'nombre': 'Construcción',
        'emoji': '🏗️',
        'energia': 'Disciplina, trabajo duro, estructura y bases sólidas',
        'recomendaciones': 'Construye cimientos firmes para tu futuro, sé disciplinado y constante, persevera aunque sea difícil',
        'desafios': 'No te vuelvas rígido o workaholic, busca balance',
        'oportunidades': 'Compra de vivienda, inversiones, consolidación financiera',
        'areas_clave': 'Finanzas, hogar, estabilidad, trabajo constante'
    },
    5: {
        'nombre': 'Cambio y Libertad',
        'emoji': '🦋',
        'energia': 'Aventura, cambio, expansión y experiencias nuevas',
        'recomendaciones': 'Acepta los cambios con entusiasmo, experimenta cosas nuevas, viaja si puedes y expande tus horizontes',
        'desafios': 'No caigas en la imprudencia o en huir de responsabilidades',
        'oportunidades': 'Viajes, cambio de carrera, mudanzas, nuevas experiencias',
        'areas_clave': 'Libertad, aventura, cambios positivos'
    },
    6: {
        'nombre': 'Responsabilidad',
        'emoji': '🏡',
        'energia': 'Hogar, familia, servicio y amor incondicional',
        'recomendaciones': 'Cuida a tu familia y seres queridos, mejora tu hogar, sirve a otros con amor genuino',
        'desafios': 'No te sacrifiques en exceso, cuida también de ti mismo',
        'oportunidades': 'Matrimonio, hijos, mejoras en el hogar, cuidado familiar',
        'areas_clave': 'Familia, hogar, relaciones cercanas, servicio'
    },
    7: {
        'nombre': 'Introspección',
        'emoji': '🧘',
        'energia': 'Espiritualidad, análisis profundo, soledad productiva',
        'recomendaciones': 'Medita regularmente, estudia temas que te apasionen, conócete profundamente en soledad',
        'desafios': 'No te aísles completamente ni caigas en escapismo',
        'oportunidades': 'Estudios avanzados, espiritualidad, investigación, terapia',
        'areas_clave': 'Espiritualidad, autoconocimiento, estudio, introspección'
    },
    8: {
        'nombre': 'Poder y Logros',
        'emoji': '👑',
        'energia': 'Éxito material, poder, reconocimiento y abundancia',
        'recomendaciones': 'Busca el éxito con determinación, gestiona bien tus finanzas, lidera con integridad',
        'desafios': 'No te vuelvas materialista ni abuses del poder',
        'oportunidades': 'Ascensos, negocios exitosos, reconocimiento público',
        'areas_clave': 'Carrera, finanzas, negocios, reconocimiento'
    },
    9: {
        'nombre': 'Culminación',
        'emoji': '🌅',
        'energia': 'Cierre de ciclos, sabiduría, humanitarismo y perdón',
        'recomendaciones': 'Cierra ciclos pendientes, perdona y libera, comparte tu sabiduría, ayuda a la humanidad',
        'desafios': 'No te aferres al pasado, suelta con amor',
        'oportunidades': 'Ayuda humanitaria, enseñanza, legado, culminación de proyectos',
        'areas_clave': 'Cierre de etapas, servicio humanitario, sabiduría'
    }
}

FORMAS_MANO_DETALLADO = {
    'cuadrada': {
        'elemento': 'Tierra',
        'personalidad': 'Práctica, metódica, confiable, realista y trabajadora',
        'fortalezas': 'Organización, constancia, lealtad, sentido común',
        'debilidades': 'Rigidez, terquedad, dificultad para adaptarse',
        'profesiones': 'Ingeniería, contabilidad, administración, construcción, agricultura',
        'amor': 'Leal y estable, busca relaciones duraderas y seguridad',
        'dinero': 'Conservador con el dinero, buen ahorrador'
    },
    'conica': {
        'elemento': 'Agua',
        'personalidad': 'Artística, intuitiva, emocional, creativa y sensible',
        'fortalezas': 'Creatividad, empatía, intuición, expresión artística',
        'debilidades': 'Hipersensibilidad, cambios de humor, indecisión',
        'profesiones': 'Arte, música, diseño, terapias, escritura creativa',
        'amor': 'Romántico e idealista, busca conexión emocional profunda',
        'dinero': 'Generoso pero puede ser poco práctico'
    },
    'filosofica': {
        'elemento': 'Aire',
        'personalidad': 'Analítica, pensadora, estudiosa, reflexiva e intelectual',
        'fortalezas': 'Inteligencia, análisis, investigación, sabiduría',
        'debilidades': 'Sobre-análisis, distanciamiento emocional, crítica excesiva',
        'profesiones': 'Filosofía, investigación, enseñanza, escritura, ciencias',
        'amor': 'Intelectual, necesita estimulación mental en pareja',
        'dinero': 'Planificador estratégico, invierte en educación'
    },
    'espatulada': {
        'elemento': 'Fuego',
        'personalidad': 'Activa, enérgica, emprendedora, dinámica e inquieta',
        'fortalezas': 'Energía, entusiasmo, valentía, capacidad de acción',
        'debilidades': 'Impulsividad, impaciencia, agresividad',
        'profesiones': 'Deportes, ventas, emprendimiento, liderazgo, militares',
        'amor': 'Apasionado y directo, busca emoción y aventura',
        'dinero': 'Arriesgado, puede ganar y perder grandes sumas'
    }
}

# ============================================================================
# ANÁLISIS MEJORADO CON IA
# ============================================================================

def analizar_mano_ia_mejorado(image):
    """Análisis mejorado de mano con MediaPipe y procesamiento avanzado"""
    try:
        img_array = np.array(image)
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        h, w = img_array.shape[:2]
        
        # Detección con MediaPipe
        with mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        ) as hands:
            results = hands.process(cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB))
            
            if not results.multi_hand_landmarks:
                # Análisis básico si MediaPipe falla
                return analizar_forma_basica(img_array)
            
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = []
            
            for landmark in hand_landmarks.landmark:
                landmarks.append({
                    'x': landmark.x * w,
                    'y': landmark.y * h,
                    'z': landmark.z
                })
            
            # Análisis avanzado de proporciones
            analisis = {
                'forma': determinar_forma_mano(landmarks, w, h),
                'dedos': analizar_dedos(landmarks),
                'montes': analizar_montes_detallado(landmarks),
                'palma': analizar_palma(landmarks, w, h),
                'flexibilidad': estimar_flexibilidad(landmarks),
                'confianza': 0.85  # Confianza alta con MediaPipe
            }
            
            return analisis
            
    except Exception as e:
        # Fallback a análisis básico
        return analizar_forma_basica(np.array(image))

def determinar_forma_mano(landmarks, width, height):
    """Determina forma de mano con precisión mejorada"""
    muneca = landmarks[0]
    base_medio = landmarks[9]
    punta_medio = landmarks[12]
    base_indice = landmarks[5]
    base_menique = landmarks[17]
    
    # Calcular proporciones
    largo_palma = np.sqrt((base_medio['x'] - muneca['x'])**2 + 
                          (base_medio['y'] - muneca['y'])**2)
    largo_dedo = np.sqrt((punta_medio['x'] - base_medio['x'])**2 + 
                         (punta_medio['y'] - base_medio['y'])**2)
    ancho_palma = np.sqrt((base_menique['x'] - base_indice['x'])**2 + 
                          (base_menique['y'] - base_indice['y'])**2)
    
    ratio_dedo_palma = largo_dedo / largo_palma if largo_palma > 0 else 1
    ratio_ancho = ancho_palma / largo_palma if largo_palma > 0 else 1
    
    # Clasificación mejorada
    if ratio_dedo_palma < 0.85 and ratio_ancho > 0.80:
        return 'cuadrada'
    elif ratio_dedo_palma > 1.15:
        return 'filosofica'
    elif ratio_dedo_palma > 0.95 and landmarks[12]['x'] > landmarks[9]['x']:
        return 'espatulada'
    else:
        return 'conica'

def analizar_dedos(landmarks):
    """Análisis detallado de cada dedo"""
    dedos_info = {
        'pulgar': analizar_dedo_individual(landmarks, [1, 2, 3, 4]),
        'indice': analizar_dedo_individual(landmarks, [5, 6, 7, 8]),
        'medio': analizar_dedo_individual(landmarks, [9, 10, 11, 12]),
        'anular': analizar_dedo_individual(landmarks, [13, 14, 15, 16]),
        'menique': analizar_dedo_individual(landmarks, [17, 18, 19, 20])
    }
    return dedos_info

def analizar_dedo_individual(landmarks, indices):
    """Analiza un dedo específico"""
    largo = 0
    for i in range(len(indices)-1):
        p1 = landmarks[indices[i]]
        p2 = landmarks[indices[i+1]]
        largo += np.sqrt((p2['x'] - p1['x'])**2 + (p2['y'] - p1['y'])**2)
    
    return {
        'largo_relativo': 'largo' if largo > 100 else 'normal' if largo > 70 else 'corto',
        'interpretacion': interpretar_largo_dedo(indices[0], largo)
    }

def interpretar_largo_dedo(base_index, largo):
    """Interpreta el significado del largo de cada dedo"""
    interpretaciones = {
        1: "Voluntad y determinación",  # Pulgar
        5: "Liderazgo y ambición",      # Índice
        9: "Responsabilidad y equilibrio", # Medio
        13: "Creatividad y expresión",  # Anular
        17: "Comunicación y negocios"   # Meñique
    }
    
    cualidad = interpretaciones.get(base_index, "Característica personal")
    if largo > 100:
        return f"{cualidad} muy desarrollada"
    elif largo > 70:
        return f"{cualidad} equilibrada"
    else:
        return f"{cualidad} por desarrollar"

def analizar_montes_detallado(landmarks):
    """Análisis profundo de los montes de la mano"""
    montes = {}
    
    # Venus (base del pulgar)
    venus_z = np.mean([landmarks[i]['z'] for i in range(1, 5)])
    montes['venus'] = {
        'prominencia': 'alto' if venus_z < -0.08 else 'medio' if venus_z < -0.03 else 'bajo',
        'significado': 'Amor, pasión, vitalidad física',
        'interpretacion': interpretar_monte_venus(venus_z)
    }
    
    # Júpiter (base del índice)
    jupiter_z = np.mean([landmarks[i]['z'] for i in range(5, 9)])
    montes['jupiter'] = {
        'prominencia': 'alto' if jupiter_z < -0.08 else 'medio' if jupiter_z < -0.03 else 'bajo',
        'significado': 'Ambición, liderazgo, autoridad',
        'interpretacion': interpretar_monte_jupiter(jupiter_z)
    }
    
    # Saturno (base del medio)
    saturno_z = np.mean([landmarks[i]['z'] for i in range(9, 13)])
    montes['saturno'] = {
        'prominencia': 'alto' if saturno_z < -0.08 else 'medio' if saturno_z < -0.03 else 'bajo',
        'significado': 'Responsabilidad, sabiduría, seriedad',
        'interpretacion': interpretar_monte_saturno(saturno_z)
    }
    
    # Apolo (base del anular)
    apolo_z = np.mean([landmarks[i]['z'] for i in range(13, 17)])
    montes['apolo'] = {
        'prominencia': 'alto' if apolo_z < -0.08 else 'medio' if apolo_z < -0.03 else 'bajo',
        'significado': 'Creatividad, arte, éxito',
        'interpretacion': interpretar_monte_apolo(apolo_z)
    }
    
    # Mercurio (base del meñique)
    mercurio_z = np.mean([landmarks[i]['z'] for i in range(17, 21)])
    montes['mercurio'] = {
        'prominencia': 'alto' if mercurio_z < -0.08 else 'medio' if mercurio_z < -0.03 else 'bajo',
        'significado': 'Comunicación, negocios, astucia',
        'interpretacion': interpretar_monte_mercurio(mercurio_z)
    }
    
    return montes

def interpretar_monte_venus(z):
    if z < -0.08:
        return "Persona muy apasionada, cálida y sociable. Gran capacidad de amar."
    elif z < -0.03:
        return "Equilibrio entre pasión y razón. Afectividad sana."
    else:
        return "Naturaleza más reservada emocionalmente. Desarrollar calidez."

def interpretar_monte_jupiter(z):
    if z < -0.08:
        return "Líder natural con gran ambición. Alta confianza en sí mismo."
    elif z < -0.03:
        return "Ambición equilibrada. Capacidad de liderazgo moderada."
    else:
        return "Naturaleza más humilde. Desarrollar autoconfianza."

def interpretar_monte_saturno(z):
    if z < -0.08:
        return "Muy responsable y serio. Tendencia a la introspección profunda."
    elif z < -0.03:
        return "Responsabilidad equilibrada. Seriedad apropiada."
    else:
        return "Naturaleza más despreocupada. Cultivar disciplina."

def interpretar_monte_apolo(z):
    if z < -0.08:
        return "Gran talento artístico. Potencial para el éxito y reconocimiento."
    elif z < -0.03:
        return "Creatividad presente. Apreciación por el arte."
    else:
        return "Creatividad latente. Desarrollar expresión artística."

def interpretar_monte_mercurio(z):
    if z < -0.08:
        return "Excelente comunicador. Talento natural para negocios."
    elif z < -0.03:
        return "Buenas habilidades de comunicación. Sentido comercial."
    else:
        return "Comunicación por desarrollar. Cultivar expresión verbal."

def analizar_palma(landmarks, width, height):
    """Analiza características generales de la palma"""
    muneca = landmarks[0]
    base_medio = landmarks[9]
    
    area_palma = calcular_area_aproximada(landmarks, [0, 5, 9, 13, 17])
    
    return {
        'tamano': 'grande' if area_palma > 15000 else 'mediano' if area_palma > 10000 else 'pequeño',
        'textura': 'Análisis visual requerido',
        'color': 'Análisis visual requerido'
    }

def calcular_area_aproximada(landmarks, indices):
    """Calcula área aproximada de la palma"""
    puntos = [(landmarks[i]['x'], landmarks[i]['y']) for i in indices]
    # Fórmula del área del polígono (Shoelace)
    area = 0
    for i in range(len(puntos)):
        j = (i + 1) % len(puntos)
        area += puntos[i][0] * puntos[j][1]
        area -= puntos[j][0] * puntos[i][1]
    return abs(area) / 2

def estimar_flexibilidad(landmarks):
    """Estima flexibilidad de la mano basado en ángulos"""
    # Análisis de ángulos entre falanges
    angulos = []
    for base in [5, 9, 13, 17]:
        angulo = calcular_angulo_dedo(landmarks, base)
        angulos.append(angulo)
    
    promedio_angulo = np.mean(angulos)
    
    if promedio_angulo > 170:
        return "Muy flexible - Adaptable, mente abierta"
    elif promedio_angulo > 160:
        return "Flexibilidad normal - Equilibrado"
    else:
        return "Rígida - Estructurado, principios firmes"

def calcular_angulo_dedo(landmarks, base_idx):
    """Calcula ángulo de un dedo"""
    try:
        p1 = landmarks[base_idx]
        p2 = landmarks[base_idx + 2]
        p3 = landmarks[base_idx + 4] if base_idx + 4 < len(landmarks) else landmarks[base_idx + 3]
        
        v1 = np.array([p2['x'] - p1['x'], p2['y'] - p1['y']])
        v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y']])
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
        angle = np.arccos(np.clip(cos_angle, -1, 1))
        return np.degrees(angle)
    except:
        return 165  # Valor por defecto

def analizar_forma_basica(img_array):
    """Análisis básico cuando MediaPipe no funciona"""
    h, w = img_array.shape[:2]
    ratio = h / w if w > 0 else 1
    
    if ratio < 1.2:
        forma = 'cuadrada'
    elif ratio > 1.5:
        forma = 'filosofica'
    elif ratio > 1.3:
        forma = 'espatulada'
    else:
        forma = 'conica'
    
    return {
        'forma': forma,
        'dedos': {'general': 'Análisis detallado requiere mejor imagen'},
        'montes': {'general': 'Análisis detallado requiere mejor imagen'},
        'palma': {'tamano': 'mediano'},
        'flexibilidad': 'Normal',
        'confianza': 0.6
    }

def calcular_ciclo_vital(fecha_nacimiento):
    """Calcula año personal según numerología"""
    hoy = datetime.now()
    suma = fecha_nacimiento.day + fecha_nacimiento.month + hoy.year
    while suma > 9:
        suma = sum(int(d) for d in str(suma))
    return suma

def generar_analisis_completo(forma_mano, analisis_mano, ciclo, pregunta=""):
    """Genera análisis completo integrando quirología y ciclos"""
    forma_info = FORMAS_MANO_DETALLADO[forma_mano]
    ciclo_info = CICLOS_VITALES[ciclo]
    
    analisis = f"""
<div class="info-card animate-in">

## 🔮 ANÁLISIS QUIROLÓGICO Y DE CICLOS VITALES COMPLETO

### 📋 PERFIL QUIROLÓGICO

**Forma de Mano:** {forma_mano.upper()} - Elemento {forma_info['elemento']}

**Características de Personalidad:**
{forma_info['personalidad']}

**Fortalezas Naturales:**
{forma_info['fortalezas']}

**Áreas de Desarrollo:**
{forma_info['debilidades']}

**Campos Profesionales Favorables:**
{forma_info['profesiones']}

**En el Amor:**
{forma_info['amor']}

**Relación con el Dinero:**
{forma_info['dinero']}

---

### 🌙 CICLO VITAL ACTUAL - AÑO {ciclo}
**{ciclo_info['emoji']} {ciclo_info['nombre']} {ciclo_info['emoji']}**

**Energía Dominante del Año:**
{ciclo_info['energia']}

**Recomendaciones Específicas:**
{ciclo_info['recomendaciones']}

**Desafíos a Evitar:**
{ciclo_info['desafios']}

**Oportunidades del Año:**
{ciclo_info['oportunidades']}

**Áreas Clave de Enfoque:**
{ciclo_info['areas_clave']}

---

### 🎯 SÍNTESIS PERSONALIZADA

"""
    
    # Síntesis inteligente basada en combinaciones
    if forma_mano == 'cuadrada' and ciclo == 4:
        analisis += """
**Alineación Perfecta:** Tu naturaleza práctica y metódica se alinea perfectamente con este año de construcción. 
Es tu momento dorado para establecer bases sólidas que durarán años. Tu disciplina natural te llevará al éxito.
"""
    elif forma_mano == 'conica' and ciclo in [3, 5, 6]:
        analisis += """
**Momento Creativo:** Tu sensibilidad artística florece especialmente en este ciclo. Es tiempo de expresar 
tu creatividad sin límites y conectar emocionalmente con otros. Tu intuición está en su punto máximo.
"""
    elif forma_mano == 'filosofica' and ciclo in [7, 8]:
        analisis += """
**Profundización Intelectual:** Tu mente analítica encuentra su mejor expresión en este período. 
Es momento de estudiar, investigar y compartir tu conocimiento. La sabiduría que adquieras ahora 
marcará tu futuro profesional.
"""
    elif forma_mano == 'espatulada' and ciclo in [1, 5, 8]:
        analisis += """
**Energía en Acción:** Tu naturaleza dinámica y emprendedora está perfectamente sincronizada con este ciclo. 
Es tu momento para actuar con valentía, tomar riesgos calculados y liderar proyectos ambiciosos.
"""
    else:
        analisis += f"""
**Integración Única:** Tu perfil {forma_mano} ({forma_info['elemento']}) en un año {ciclo} crea 
una combinación única. Usa tu {forma_info['fortalezas'].split(',')[0]} para navegar las energías 
de {ciclo_info['nombre'].lower()}. El equilibrio entre tu naturaleza y el ciclo actual es clave para tu éxito.
"""
    
    # Si hay pregunta específica
    if pregunta:
        analisis += f"""

---

### 💭 RESPUESTA A TU CONSULTA

**Tu pregunta:** "{pregunta}"

**Orientación basada en tu perfil:**

Considerando tu naturaleza {forma_mano} y el ciclo {ciclo} en el que te encuentras, aquí está mi orientación:

{generar_respuesta_especifica(forma_mano, ciclo, pregunta)}
"""
    
    analisis += """

---

### ⚡ MONTES Y CARACTERÍSTICAS ADICIONALES

"""
    
    # Agregar análisis de montes si existe
    if 'montes' in analisis_mano and isinstance(analisis_mano['montes'], dict):
        for monte, info in analisis_mano['montes'].items():
            if isinstance(info, dict):
                analisis += f"""
**Monte de {monte.capitalize()}:** {info.get('prominencia', 'medio').upper()}
- {info.get('significado', '')}
- {info.get('interpretacion', '')}
"""
    
    analisis += """

---

### 🌟 RECOMENDACIONES FINALES

**Para este período:**
1. Mantén alineación entre tu naturaleza y las energías del ciclo
2. Aprovecha tus fortalezas naturales especialmente ahora
3. Trabaja conscientemente en tus áreas de desarrollo
4. Confía en tu intuición y en el timing perfecto del universo

**Recuerda:** Tu carta quirológica muestra potenciales, pero TÚ eres quien decide cómo manifestarlos. 
Este análisis es una brújula, no un destino fijo. Tu libre albedrío y esfuerzo consciente son 
los verdaderos creadores de tu realidad.

</div>

<p style="text-align: center; color: #F4E4C1; font-style: italic; margin-top: 2rem;">
⚠️ Este análisis es una herramienta de autoconocimiento y orientación personal. 
No sustituye consejo médico, psicológico, legal o financiero profesional.
</p>
"""
    
    return analisis

def generar_respuesta_especifica(forma_mano, ciclo, pregunta):
    """Genera respuesta específica a la pregunta del usuario"""
    pregunta_lower = pregunta.lower()
    forma_info = FORMAS_MANO_DETALLADO[forma_mano]
    ciclo_info = CICLOS_VITALES[ciclo]
    
    respuesta = ""
    
    # Detectar tema de la consulta
    if any(palabra in pregunta_lower for palabra in ['trabajo', 'carrera', 'profesional', 'empleo', 'negocio']):
        respuesta += f"""
**Orientación Profesional:**

Tu mano {forma_mano} ({forma_info['elemento']}) te inclina naturalmente hacia: {forma_info['profesiones']}.

En este año {ciclo}, la energía favorece: {ciclo_info['areas_clave']}.

**Recomendación específica:** {ciclo_info['recomendaciones']} 
Esto se alinea perfectamente con tus fortalezas de {forma_info['fortalezas']}.
"""
    
    elif any(palabra in pregunta_lower for palabra in ['amor', 'pareja', 'relación', 'matrimonio', 'sentimental']):
        respuesta += f"""
**Orientación en el Amor:**

Tu perfil {forma_mano} en relaciones: {forma_info['amor']}.

Este año {ciclo} trae energía de: {ciclo_info['energia']}.

**Recomendación específica:** {ciclo_info['recomendaciones']}
Mantén presente que {forma_info['debilidades']} para crear relaciones más armoniosas.
"""
    
    elif any(palabra in pregunta_lower for palabra in ['dinero', 'económico', 'financiero', 'inversión', 'ahorro']):
        respuesta += f"""
**Orientación Financiera:**

Tu relación natural con el dinero: {forma_info['dinero']}.

El ciclo {ciclo} favorece: {ciclo_info['oportunidades']}.

**Recomendación específica:** {ciclo_info['recomendaciones']}
Aprovecha tu naturaleza {forma_info['personalidad'].split(',')[0]} para tomar decisiones financieras.
"""
    
    elif any(palabra in pregunta_lower for palabra in ['cambio', 'decisión', 'camino', 'elección']):
        respuesta += f"""
**Orientación para Decisiones:**

Tu forma de decidir (perfil {forma_mano}): {forma_info['personalidad']}.

La energía del año {ciclo}: {ciclo_info['energia']}.

**Recomendación específica:** {ciclo_info['recomendaciones']}
Confía en tus fortalezas: {forma_info['fortalezas']}, pero ten cuidado con {forma_info['debilidades']}.
"""
    
    else:
        respuesta += f"""
**Orientación General:**

Basándome en tu perfil quirológico {forma_mano} y el ciclo {ciclo} actual:

Tu naturaleza {forma_info['personalidad']} se encuentra en un momento donde {ciclo_info['energia']}.

**Recomendación:** {ciclo_info['recomendaciones']}

Las oportunidades que se presentan: {ciclo_info['oportunidades']}.

Mantén consciencia de: {ciclo_info['desafios']}.
"""
    
    return respuesta

def generar_analisis_basico(ciclo):
    """Análisis gratuito básico con diseño premium"""
    ciclo_info = CICLOS_VITALES[ciclo]
    
    return f"""
<div class="info-card animate-in">
<h2 style="text-align: center;">{ciclo_info['emoji']} Año {ciclo}: {ciclo_info['nombre']} {ciclo_info['emoji']}</h2>

### ✨ Energía Dominante del Año
<p style="font-size: 1.2rem; color: #F4E4C1;">{ciclo_info['energia']}</p>

### 🎯 Recomendaciones para este Ciclo
<p style="font-size: 1.1rem;">{ciclo_info['recomendaciones']}</p>

### ⚡ Áreas de Enfoque
<p style="font-size: 1.1rem;">{ciclo_info['areas_clave']}</p>

<div class="gold-divider"></div>

### ⭐ ¿Quieres profundizar más?

<div class="price-card" style="margin: 2rem 0;">
<h3>Análisis Premium Personalizado</h3>
<p style="color: #F4E4C1;">Con donación consciente de $20.000 - $60.000 COP</p>
<p>Incluye:</p>
<ul style="text-align: left;">
<li>✅ Lectura quirológica completa de tus manos</li>
<li>✅ Análisis de forma, dedos, montes y líneas</li>
<li>✅ Interpretación experta personalizada</li>
<li>✅ Combinación ciclos vitales + quirología</li>
<li>✅ Orientación específica para tu situación</li>
<li>✅ Respuesta detallada en 24-48 horas</li>
</ul>
</div>
</div>

<p style="text-align: center; color: #F4E4C1; font-style: italic; margin-top: 2rem;">
⚠️ Este análisis es orientativo para autoconocimiento. No sustituye consejo profesional.
</p>
"""

# ============================================================================
# FUNCIONES DE PAGO (Continúa igual...)
# ============================================================================

def mostrar_opciones_pago(monto, tipo_consulta):
    """Muestra las opciones de pago con diseño premium"""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>✨ Elige tu Método de Pago ✨</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card" style="text-align: center; min-height: 300px;">
            <h3>💙 Mercado Pago</h3>
            <p>La más popular en LATAM</p>
            <ul style="text-align: left; list-style: none; padding: 0;">
                <li>✓ Tarjetas crédito/débito</li>
                <li>✓ PSE transferencias</li>
                <li>✓ Cuotas sin interés</li>
                <li>✓ Compra protegida</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💙 Pagar con Mercado Pago", key="btn_mp", use_container_width=True):
            st.session_state.metodo_pago = "Mercado Pago"
    
    with col2:
        st.markdown("""
        <div class="info-card" style="text-align: center; min-height: 300px;">
            <h3>🇨🇴 Wompi</h3>
            <p>100% Colombiana</p>
            <ul style="text-align: left; list-style: none; padding: 0;">
                <li>✓ PSE inmediato</li>
                <li>✓ Nequi</li>
                <li>✓ Bancolombia</li>
                <li>✓ Comisión más baja</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🇨🇴 Pagar con Wompi", key="btn_wompi", use_container_width=True):
            st.session_state.metodo_pago = "Wompi"
    
    with col3:
        st.markdown("""
        <div class="info-card" style="text-align: center; min-height: 300px;">
            <h3>💳 PayPal</h3>
            <p>Internacional y seguro</p>
            <ul style="text-align: left; list-style: none; padding: 0;">
                <li>✓ Tarjetas mundiales</li>
                <li>✓ Saldo PayPal</li>
                <li>✓ Protección comprador</li>
                <li>✓ Confianza global</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💳 Pagar con PayPal", key="btn_paypal", use_container_width=True):
            st.session_state.metodo_pago = "PayPal"
    
    if 'metodo_pago' in st.session_state:
        metodo = st.session_state.metodo_pago
        
        if metodo == "PayPal":
            return pago_paypal(monto, tipo_consulta)
        elif metodo == "Wompi":
            return pago_wompi(monto, tipo_consulta)
        elif metodo == "Mercado Pago":
            return pago_mercadopago(monto, tipo_consulta)
    
    return None

def pago_mercadopago(monto, descripcion):
    """Integración Mercado Pago con diseño premium"""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="info-card">
            <h2>💙 Mercado Pago</h2>
            <p><strong>Servicio:</strong> {descripcion}</p>
            <p><strong>Métodos disponibles:</strong></p>
            <ul>
                <li>💳 Tarjetas de crédito y débito</li>
                <li>🏦 PSE (Transferencia bancaria inmediata)</li>
                <li>💰 Saldo Mercado Pago</li>
                <li>📱 Hasta 12 cuotas sin interés</li>
                <li>🔒 Compra 100% protegida</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="price-card">
            <p style="color: #F4E4C1; margin: 0;">Total a pagar</p>
            <div class="price-amount">${monto:,.0f}</div>
            <p style="color: #F4E4C1; margin: 0;">COP</p>
        </div>
        """, unsafe_allow_html=True)
    
    try:
        access_token = os.getenv('MERCADOPAGO_ACCESS_TOKEN')
        
        if access_token and (access_token.startswith('TEST-') or access_token.startswith('APP_')):
            import mercadopago
            
            sdk = mercadopago.SDK(access_token)
            
            preference_data = {
                "items": [{
                    "title": descripcion,
                    "quantity": 1,
                    "currency_id": "COP",
                    "unit_price": float(monto)
                }],
                "back_urls": {
                    "success": "https://tu-app.streamlit.app/success",
                    "failure": "https://tu-app.streamlit.app/failure"
                },
                "auto_return": "approved"
            }
            
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            
            st.success("✅ Enlace de pago generado exitosamente")
            
            col_btn = st.columns([1, 2, 1])
            with col_btn[1]:
                st.link_button(
                    "🔗 Continuar a Mercado Pago",
                    preference['init_point'],
                    use_container_width=True
                )
            
            st.info("""
            **📋 Proceso de pago:**
            1. Click en el botón de arriba
            2. Elige tu método de pago favorito
            3. Completa el pago de forma segura
            4. Regresa automáticamente aquí
            5. Tu análisis estará listo en 24-48 horas
            """)
            
        else:
            st.warning("⚙️ Mercado Pago requiere configuración")
            with st.expander("📖 Ver instrucciones de configuración"):
                st.markdown("""
                ### Configurar Mercado Pago (5 minutos):
                
                **1.** Crea cuenta en: https://www.mercadopago.com.co/
                **2.** Ve a: Tus integraciones → Credenciales
                **3.** Copia el Access Token de prueba (TEST-)
                **4.** Instala librería: `py -m pip install mercadopago`
                **5.** Agrégalo al archivo .env:
                ```
                MERCADOPAGO_ACCESS_TOKEN=TEST-tu-token-aqui
                ```
