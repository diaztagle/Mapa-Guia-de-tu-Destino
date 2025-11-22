"""
MAPA GUÍA DE TU DESTINO - Versión Completa
Análisis quirológico profundo con IA, validación de imágenes
Tipografía Roboto, diseño compacto

INSTALACIÓN:
py -m pip install streamlit pandas opencv-python mediapipe pillow bcrypt python-dotenv scikit-image

Uso:
streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import sqlite3
import bcrypt
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Importaciones opcionales
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
# CONFIGURACIÓN
# ============================================================================

st.set_page_config(
    page_title="Mapa Guía de tu Destino",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Compacto con Roboto
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    * {
        font-family: 'Roboto', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0A1128 0%, #1C2541 50%, #2A3B5F 100%);
    }
    
    .main .block-container {
        padding: 1rem;
        max-width: 1200px;
    }
    
    h1 {
        color: #D4AF37 !important;
        font-size: 1.8rem !important;
        font-weight: 500 !important;
        text-align: center;
        margin: 0.5rem 0 !important;
    }
    
    h2 {
        color: #D4AF37 !important;
        font-size: 1.3rem !important;
        margin: 0.5rem 0 !important;
    }
    
    h3 {
        color: #D4AF37 !important;
        font-size: 1.1rem !important;
        margin: 0.3rem 0 !important;
    }
    
    p, li, label {
        color: #FAF9F6 !important;
        font-size: 0.85rem !important;
        line-height: 1.4 !important;
        margin: 0.2rem 0 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
        color: #0A1128 !important;
        border: none;
        border-radius: 8px;
        padding: 0.4rem 1rem;
        font-weight: 500;
        font-size: 0.8rem;
        min-height: 36px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #F4E4C1 0%, #D4AF37 100%);
        transform: translateY(-1px);
    }
    
    .info-card {
        background: rgba(26, 37, 65, 0.8);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .price-card {
        background: linear-gradient(135deg, rgba(26, 37, 65, 0.9) 0%, rgba(10, 17, 40, 0.9) 100%);
        border: 2px solid #D4AF37;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    .price-amount {
        font-size: 1.8rem;
        font-weight: 700;
        color: #D4AF37;
        margin: 0.5rem 0;
    }
    
    .badge {
        background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
        color: #0A1128;
        padding: 0.25rem 0.75rem;
        border-radius: 10px;
        font-weight: 500;
        font-size: 0.75rem;
        display: inline-block;
        margin: 0.2rem;
    }
    
    .gold-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #D4AF37 50%, transparent 100%);
        margin: 1rem 0;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        background: rgba(26, 37, 65, 0.6) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 8px !important;
        color: #FAF9F6 !important;
        padding: 0.5rem !important;
        font-size: 0.85rem !important;
    }
    
    [data-testid="stFileUploader"] {
        background: rgba(26, 37, 65, 0.6);
        border: 1px dashed rgba(212, 175, 55, 0.5);
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 0.8rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PRECIOS = {
    'consulta_basica': 0,
    'consulta_premium_min': 20000,
    'consulta_premium_max': 60000,
}

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
# VALIDACIÓN DE IMÁGENES
# ============================================================================

def validar_calidad_imagen(image):
    """Valida la calidad de la imagen para análisis"""
    try:
        img_array = np.array(image)
        
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        h, w = gray.shape
        
        validaciones = {
            'resolucion': False,
            'iluminacion': False,
            'nitidez': False,
            'contraste': False,
            'mano_detectada': False
        }
        
        errores = []
        advertencias = []
        
        # Resolución
        if w >= 800 and h >= 600:
            validaciones['resolucion'] = True
        else:
            errores.append(f"Resolución {w}x{h}. Mínimo: 800x600")
        
        # Iluminación
        brillo = np.mean(gray)
        if 60 < brillo < 200:
            validaciones['iluminacion'] = True
        elif brillo <= 60:
            errores.append("Imagen muy oscura")
        else:
            advertencias.append("Imagen muy clara")
        
        # Nitidez
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var > 100:
            validaciones['nitidez'] = True
        else:
            errores.append(f"Imagen borrosa (nitidez: {laplacian_var:.0f})")
        
        # Contraste
        contraste = gray.std()
        if contraste > 30:
            validaciones['contraste'] = True
        else:
            advertencias.append("Bajo contraste")
        
        # Detectar mano
        if VISION_AVAILABLE:
            with mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=1,
                min_detection_confidence=0.5
            ) as hands:
                results = hands.process(cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))
                if results.multi_hand_landmarks:
                    validaciones['mano_detectada'] = True
                else:
                    errores.append("No se detectó mano clara")
        else:
            validaciones['mano_detectada'] = True
        
        puntuacion = sum(validaciones.values()) / len(validaciones) * 100
        
        return {
            'valida': puntuacion >= 60,
            'puntuacion': puntuacion,
            'validaciones': validaciones,
            'errores': errores,
            'advertencias': advertencias,
            'brillo': brillo,
            'nitidez': laplacian_var if 'laplacian_var' in locals() else 0,
            'contraste': contraste
        }
        
    except Exception as e:
        return {
            'valida': False,
            'puntuacion': 0,
            'errores': [f"Error: {str(e)}"],
            'advertencias': []
        }

def mostrar_resultado_validacion(validacion, numero_foto):
    """Muestra resultado de validación"""
    puntuacion = validacion['puntuacion']
    
    if puntuacion >= 80:
        color = "#4CAF50"
        icono = "✅"
        mensaje = "Excelente"
    elif puntuacion >= 60:
        color = "#FFA500"
        icono = "⚠️"
        mensaje = "Aceptable"
    else:
        color = "#F44336"
        icono = "❌"
        mensaje = "No válida"
    
    st.markdown(f"""
    <div style="background: rgba(26, 37, 65, 0.8); border-left: 4px solid {color}; 
                padding: 0.5rem; border-radius: 8px; margin: 0.3rem 0;">
        <p style="margin: 0; font-weight: 500;">{icono} Foto {numero_foto}: {mensaje} ({puntuacion:.0f}%)</p>
    </div>
    """, unsafe_allow_html=True)
    
    if validacion['errores']:
        for error in validacion['errores']:
            st.error(f"❌ {error}", icon="🚫")
    
    if validacion['advertencias']:
        for adv in validacion['advertencias']:
            st.warning(f"⚠️ {adv}", icon="⚡")
    
    with st.expander("📊 Detalles técnicos"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Brillo", f"{validacion.get('brillo', 0):.0f}")
        with col2:
            st.metric("Nitidez", f"{validacion.get('nitidez', 0):.0f}")
        with col3:
            st.metric("Contraste", f"{validacion.get('contraste', 0):.0f}")

# ============================================================================
# ANÁLISIS QUIROLÓGICO
# ============================================================================

def analisis_quirologico_completo(images):
    """Análisis completo de imágenes de manos"""
    
    if not VISION_AVAILABLE:
        return analisis_basico_sin_mediapipe(images)
    
    analisis = {
        'forma_mano': None,
        'dedos': {},
        'montes': {},
        'lineas': {},
        'textura': {},
        'flexibilidad': None,
        'confianza': 0
    }
    
    mejor_imagen = None
    mejor_landmarks = None
    
    # Buscar mejor imagen
    for img in images:
        if img is None:
            continue
        
        try:
            img_array = np.array(img)
            
            with mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=1,
                min_detection_confidence=0.7
            ) as hands:
                results = hands.process(cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))
                
                if results.multi_hand_landmarks:
                    mejor_imagen = img_array
                    mejor_landmarks = results.multi_hand_landmarks[0]
                    break
        except:
            continue
    
    if mejor_landmarks is None:
        return analisis_basico_sin_mediapipe(images[0] if images else None)
    
    # Extraer landmarks
    h, w = mejor_imagen.shape[:2]
    landmarks = []
    for lm in mejor_landmarks.landmark:
        landmarks.append({
            'x': lm.x * w,
            'y': lm.y * h,
            'z': lm.z
        })
    
    # Análisis de forma
    analisis['forma_mano'] = analizar_forma_mano(landmarks, w, h)
    
    # Análisis de dedos
    analisis['dedos'] = analizar_dedos(landmarks)
    
    # Análisis de montes
    analisis['montes'] = analizar_montes(landmarks)
    
    # Análisis de líneas
    analisis['lineas'] = analizar_lineas(mejor_imagen, landmarks)
    
    # Flexibilidad
    analisis['flexibilidad'] = calcular_flexibilidad(landmarks)
    
    analisis['confianza'] = 0.85
    
    return analisis

def analizar_forma_mano(landmarks, w, h):
    """Determina forma de mano"""
    muneca = landmarks[0]
    base_medio = landmarks[9]
    punta_medio = landmarks[12]
    base_indice = landmarks[5]
    base_menique = landmarks[17]
    
    largo_palma = np.sqrt((base_medio['x'] - muneca['x'])**2 + 
                          (base_medio['y'] - muneca['y'])**2)
    largo_dedo = np.sqrt((punta_medio['x'] - base_medio['x'])**2 + 
                         (punta_medio['y'] - base_medio['y'])**2)
    ancho_palma = np.sqrt((base_menique['x'] - base_indice['x'])**2 + 
                          (base_menique['y'] - base_indice['y'])**2)
    
    ratio_dedo_palma = largo_dedo / largo_palma if largo_palma > 0 else 1
    ratio_ancho = ancho_palma / largo_palma if largo_palma > 0 else 1
    
    if ratio_dedo_palma < 0.85 and ratio_ancho > 0.80:
        forma = 'cuadrada'
        elemento = 'Tierra'
        desc = 'Práctica, metódica, confiable'
    elif ratio_dedo_palma > 1.15:
        forma = 'filosofica'
        elemento = 'Aire'
        desc = 'Analítica, pensadora, reflexiva'
    elif ratio_dedo_palma > 0.95:
        forma = 'espatulada'
        elemento = 'Fuego'
        desc = 'Activa, enérgica, emprendedora'
    else:
        forma = 'conica'
        elemento = 'Agua'
        desc = 'Artística, intuitiva, creativa'
    
    return {
        'tipo': forma,
        'elemento': elemento,
        'descripcion': desc,
        'ratio_dedo_palma': round(ratio_dedo_palma, 2)
    }

def analizar_dedos(landmarks):
    """Análisis de dedos"""
    dedos = {}
    
    dedos_info = [
        ('Pulgar', [1, 2, 3, 4], 'Voluntad y determinación'),
        ('Índice', [5, 6, 7, 8], 'Liderazgo y ambición'),
        ('Medio', [9, 10, 11, 12], 'Responsabilidad y equilibrio'),
        ('Anular', [13, 14, 15, 16], 'Creatividad y expresión'),
        ('Meñique', [17, 18, 19, 20], 'Comunicación y negocios')
    ]
    
    for nombre, indices, significado in dedos_info:
        largo = 0
        for i in range(len(indices)-1):
            p1 = landmarks[indices[i]]
            p2 = landmarks[indices[i+1]]
            largo += np.sqrt((p2['x'] - p1['x'])**2 + (p2['y'] - p1['y'])**2)
        
        clasificacion = 'largo' if largo > 100 else 'normal' if largo > 70 else 'corto'
        
        dedos[nombre.lower()] = {
            'nombre': nombre,
            'largo': round(largo, 1),
            'clasificacion': clasificacion,
            'significado': significado
        }
    
    return dedos

def analizar_montes(landmarks):
    """Análisis de montes"""
    montes = {}
    
    montes_info = [
        ('Venus', range(1, 5), 'Amor, pasión, vitalidad'),
        ('Júpiter', range(5, 9), 'Ambición, liderazgo'),
        ('Saturno', range(9, 13), 'Responsabilidad, sabiduría'),
        ('Apolo', range(13, 17), 'Creatividad, éxito'),
        ('Mercurio', range(17, 21), 'Comunicación, negocios')
    ]
    
    for nombre, indices, significado in montes_info:
        z_promedio = np.mean([landmarks[i]['z'] for i in indices])
        
        if z_promedio < -0.08:
            prominencia = 'muy_alto'
            interp = 'MUY DESARROLLADO'
        elif z_promedio < -0.04:
            prominencia = 'alto'
            interp = 'DESARROLLADO'
        elif z_promedio < 0.02:
            prominencia = 'medio'
            interp = 'EQUILIBRADO'
        else:
            prominencia = 'bajo'
            interp = 'POR DESARROLLAR'
        
        montes[nombre.lower()] = {
            'nombre': nombre,
            'prominencia': prominencia,
            'significado': significado,
            'interpretacion': interp
        }
    
    return montes

def analizar_lineas(img_array, landmarks):
    """Análisis básico de líneas"""
    return {
        'vida': {
            'nombre': 'Línea de la Vida',
            'significado': 'Vitalidad, salud, energía vital',
            'interpretacion': 'Indica tu fuerza vital y resistencia física'
        },
        'cabeza': {
            'nombre': 'Línea de la Cabeza',
            'significado': 'Intelecto, forma de pensar',
            'interpretacion': 'Revela tu estilo cognitivo y capacidad mental'
        },
        'corazon': {
            'nombre': 'Línea del Corazón',
            'significado': 'Emociones, amor, relaciones',
            'interpretacion': 'Muestra tu vida emocional y afectiva'
        }
    }

def calcular_flexibilidad(landmarks):
    """Calcula flexibilidad"""
    angulos = []
    
    for base in [5, 9, 13, 17]:
        try:
            p1 = landmarks[base]
            p2 = landmarks[base + 2]
            p3 = landmarks[base + 4] if base + 4 < len(landmarks) else landmarks[base + 3]
            
            v1 = np.array([p2['x'] - p1['x'], p2['y'] - p1['y']])
            v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y']])
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
            angle = np.arccos(np.clip(cos_angle, -1, 1))
            angulos.append(np.degrees(angle))
        except:
            continue
    
    if angulos:
        promedio = np.mean(angulos)
        
        if promedio > 175:
            return {'tipo': 'muy_flexible', 'interpretacion': 'Mente abierta, adaptable'}
        elif promedio > 165:
            return {'tipo': 'flexible', 'interpretacion': 'Equilibrio entre flexibilidad y estructura'}
        else:
            return {'tipo': 'rigida', 'interpretacion': 'Principios firmes, estructurado'}
    
    return {'tipo': 'normal', 'interpretacion': 'Flexibilidad equilibrada'}

def analisis_basico_sin_mediapipe(image):
    """Análisis cuando no hay MediaPipe"""
    return {
        'forma_mano': {
            'tipo': 'mixta',
            'elemento': 'Múltiple',
            'descripcion': 'Análisis básico. Se requiere mejor imagen para precisión.',
            'ratio_dedo_palma': 1.0
        },
        'dedos': {},
        'montes': {},
        'lineas': {},
        'flexibilidad': {'tipo': 'normal', 'interpretacion': 'No determinado'},
        'confianza': 0.3
    }

# ============================================================================
# CICLOS TEMPORALES
# ============================================================================

def calcular_ciclo_vital(fecha_nacimiento):
    """Calcula ciclo vital"""
    hoy = datetime.now()
    suma = fecha_nacimiento.day + fecha_nacimiento.month + hoy.year
    while suma > 9:
        suma = sum(int(d) for d in str(suma))
    return suma

def analizar_ciclos_temporales(fecha_nacimiento, pregunta=""):
    """Analiza ciclos para períodos específicos"""
    hoy = datetime.now()
    ciclo_actual = calcular_ciclo_vital(fecha_nacimiento)
    
    pregunta_lower = pregunta.lower()
    periodos = []
    
    # Detectar períodos mencionados
    if any(p in pregunta_lower for p in ['próximo', 'siguiente', '2025', '2026']):
        periodos.append({'año': hoy.year + 1, 'tipo': 'próximo'})
    
    if any(p in pregunta_lower for p in ['este año', str(hoy.year)]):
        periodos.append({'año': hoy.year, 'tipo': 'actual'})
    
    if 'próximos años' in pregunta_lower:
        for i in range(1, 4):
            periodos.append({'año': hoy.year + i, 'tipo': f'año_{i}'})
    
    # Default: año actual y próximo
    if not periodos:
        periodos = [
            {'año': hoy.year, 'tipo': 'actual'},
            {'año': hoy.year + 1, 'tipo': 'próximo'}
        ]
    
    analisis_periodos = []
    
    for periodo in periodos:
        suma = fecha_nacimiento.day + fecha_nacimiento.month + periodo['año']
        while suma > 9:
            suma = sum(int(d) for d in str(suma))
        
        ciclo_info = CICLOS_VITALES.get(suma, CICLOS_VITALES[1])
        
        analisis_periodos.append({
            'año': periodo['año'],
            'ciclo': suma,
            'nombre': ciclo_info['nombre'],
            'emoji': ciclo_info['emoji'],
            'energia': ciclo_info['energia'],
            'recomendaciones': ciclo_info['recomendaciones']
        })
    
    return {
        'ciclo_actual': ciclo_actual,
        'periodos': analisis_periodos
    }

# ============================================================================
# GENERACIÓN DE ANÁLISIS COMPLETO
# ============================================================================

def generar_analisis_completo(analisis_quiro, ciclos, pregunta):
    """Genera análisis completo HTML"""
    
    if not analisis_quiro or analisis_quiro['confianza'] < 0.4:
        return "<p>No se pudo realizar el análisis. Por favor, sube imágenes de mejor calidad.</p>"
    
    forma = analisis_quiro.get('forma_mano', {})
    dedos = analisis_quiro.get('dedos', {})
    montes = analisis_quiro.get('montes', {})
    lineas = analisis_quiro.get('lineas', {})
    flex = analisis_quiro.get('flexibilidad', {})
    
    html = f"""
<div class="info-card">

## 🔮 ANÁLISIS QUIROLÓGICO Y CICLOS VITALES

### 📋 FORMA DE MANO

**Tipo:** {forma.get('tipo', 'N/A').upper()} - Elemento {forma.get('elemento', 'N/A')}

{forma.get('descripcion', '')}

Ratio Dedo/Palma: {forma.get('ratio_dedo_palma', 0)}

---

### 🖐️ DEDOS

"""
    
    for nombre, info in dedos.items():
        html += f"""
**{info['nombre']}** - {info['clasificacion'].upper()}
- {info['significado']}
- Largo: {info['largo']}px

"""
    
    html += """
---

### 🏔️ MONTES

"""
    
    for nombre, info in montes.items():
        html += f"""
**Monte de {info['nombre']}** - {info['prominencia'].upper()}
- {info['significado']}
- {info['interpretacion']}

"""
    
    html += """
---

### 📏 LÍNEAS PRINCIPALES

"""
    
    for nombre, info in lineas.items():
        html += f"""
**{info['nombre']}**
- {info['significado']}
- {info['interpretacion']}

"""
    
    html += f"""
---

### 🎨 FLEXIBILIDAD

{flex.get('tipo', 'normal').upper()}: {flex.get('interpretacion', '')}

---

### 🌙 CICLOS VITALES

"""
    
    for periodo in ciclos['periodos']:
        html += f"""
**{periodo['emoji']} AÑO {periodo['año']} - Ciclo {periodo['ciclo']}: {periodo['nombre']}**

Energía: {periodo['energia']}

Recomendaciones: {periodo['recomendaciones']}

"""
    
    if pregunta:
        html += f"""
---

### 💭 RESPUESTA A TU CONSULTA

**Tu pregunta:** "{pregunta}"

Basándome en tu mano {forma.get('tipo', '')}, que revela una personalidad {forma.get('descripcion', '').lower()}, 
y considerando el ciclo {ciclos['ciclo_actual']} en el que te encuentras, te recomiendo:

{CICLOS_VITALES[ciclos['ciclo_actual']]['recomendaciones']}

Tu forma de mano indica fortalezas en {forma.get('descripcion', '').lower()}.
"""
    
    html += """

---

### ⭐ CONCLUSIÓN

Este análisis muestra tendencias y potenciales. Tu libre albedrío y acciones conscientes 
son los verdaderos creadores de tu destino.

</div>

<p style="text-align: center; color: #F4E4C1; font-style: italic; font-size: 0.8rem;">
⚠️ Análisis orientativo. No sustituye consejo profesional.
</p>
"""
    
    return html

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
# INTERFAZ PRINCIPAL
# ============================================================================

def main():
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = init_db()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # SIDEBAR
    with st.sidebar:
        st.markdown('<div style="text-align: center;"><h2>🔮 Mapa Guía</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        if not st.session_state.logged_in:
            pagina = st.radio("Ir a:", ["Inicio", "Ingresar"], label_visibility="collapsed")
        else:
            st.markdown('<div class="badge">👤 Usuario</div>', unsafe_allow_html=True)
            pagina = st.radio("Ir a:", [
                "Inicio",
                "Consulta Gratis",
                "Consulta Premium",
                "Cerrar Sesión"
            ], label_visibility="collapsed")
            
            if pagina == "Cerrar Sesión":
                st.session_state.logged_in = False
                st.rerun()
        
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
        <p style="text-align: center;"><span class="badge">Básico: GRATIS</span></p>
        <p style="text-align: center;"><span class="badge">Premium: $20k-$60k</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    # PÁGINAS
    if pagina == "Inicio":
        st.markdown('<h1>🔮 Mapa Guía de tu Destino</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 0.9rem;">Quirología y Ciclos Vitales con IA Avanzada</p>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="price-card">
            <h3>🆓 Análisis Gratis</h3>
            <div class="price-amount">GRATIS</div>
            <p style="font-size: 0.8rem;">• Análisis de fotos<br>• Ciclo vital<br>• Interpretación básica</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="price-card">
            <h3>⭐ Premium</h3>
            <div class="price-amount">$20k-$60k</div>
            <p style="font-size: 0.8rem;">• Análisis profundo<br>• Ciclos temporales<br>• Respuesta personalizada</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
        <h3>✨ Características</h3>
        <ul style="font-size: 0.85rem;">
        <li>Validación automática de calidad de imágenes</li>
        <li>Análisis con IA y MediaPipe</li>
        <li>Interpretación de forma, dedos, montes y líneas</li>
        <li>Ciclos vitales personalizados</li>
        <li>Respuestas contextualizadas a tu pregunta</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    elif pagina == "Ingresar":
        st.markdown('<h1>🔐 Acceso</h1>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            email = st.text_input("📧 Email")
            password = st.text_input("🔒 Contraseña", type="password")
            
            if st.button("Iniciar Sesión", use_container_width=True):
                st.session_state.logged_in = True
                st.success("✅ Sesión iniciada")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif pagina == "Consulta Gratis":
        st.markdown('<h1>🆓 Consulta Gratis con Análisis de Fotos</h1>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        
        fecha_nac = st.date_input(
            "📅 Fecha de nacimiento",
            min_value=datetime(1920, 1, 1),
            max_value=datetime.now()
        )
        
        st.markdown("### 📸 Sube fotos de tus manos (1-4 imágenes)")
        st.info("💡 **Consejos:** Luz natural, fondo claro, mano centrada, sin joyas")
        
        col1, col2 = st.columns(2)
        with col1:
            foto1 = st.file_uploader("🖐️ Palma derecha", type=['jpg', 'png'], key="f1")
        with col2:
            foto2 = st.file_uploader("🖐️ Palma izquierda", type=['jpg', 'png'], key="f2")
        
        col3, col4 = st.columns(2)
        with col3:
            foto3 = st.file_uploader("📷 Dorso (opcional)", type=['jpg', 'png'], key="f3")
        with col4:
            foto4 = st.file_uploader("📷 Lateral (opcional)", type=['jpg', 'png'], key="f4")
        
        if st.button("🔮 Analizar Manos", use_container_width=True):
            fotos = [foto1, foto2, foto3, foto4]
            fotos_validas = [f for f in fotos if f is not None]
            
            if not fotos_validas:
                st.error("⚠️ Debes subir al menos una foto")
            else:
                with st.spinner("✨ Validando calidad de imágenes..."):
                    imagenes_procesadas = []
                    todas_validas = True
                    
                    for idx, foto in enumerate(fotos_validas, 1):
                        img = Image.open(foto)
                        validacion = validar_calidad_imagen(img)
                        
                        mostrar_resultado_validacion(validacion, idx)
                        
                        if validacion['valida']:
                            imagenes_procesadas.append(img)
                        else:
                            todas_validas = False
                    
                    if todas_validas and imagenes_procesadas:
                        st.success(f"✅ {len(imagenes_procesadas)} imagen(es) válida(s)")
                        
                        with st.spinner("🔮 Analizando quirología..."):
                            analisis_quiro = analisis_quirologico_completo(imagenes_procesadas)
                            ciclos = analizar_ciclos_temporales(fecha_nac)
                            resultado = generar_analisis_completo(analisis_quiro, ciclos, "")
                            
                            st.markdown(resultado, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ Por favor mejora la calidad de las imágenes según las recomendaciones")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif pagina == "Consulta Premium":
        st.markdown('<h1>⭐ Consulta Premium Personalizada</h1>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        
        with st.form("consulta_premium"):
            pregunta = st.text_area(
                "💭 Tu consulta específica",
                placeholder="Ejemplo: ¿Cómo será mi carrera profesional en los próximos 2 años?",
                height=100
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
                    "💰 Donación (COP)",
                    min_value=PRECIOS['consulta_premium_min'],
                    max_value=PRECIOS['consulta_premium_max'],
                    value=30000,
                    step=5000
                )
            
            st.markdown("### 📸 Fotos de tus manos (1-4 imágenes)")
            
            col1, col2 = st.columns(2)
            with col1:
                foto1 = st.file_uploader("🖐️ Palma derecha", type=['jpg', 'png'], key="p1")
            with col2:
                foto2 = st.file_uploader("🖐️ Palma izquierda", type=['jpg', 'png'], key="p2")
            
            col3, col4 = st.columns(2)
            with col3:
                foto3 = st.file_uploader("📷 Dorso", type=['jpg', 'png'], key="p3")
            with col4:
                foto4 = st.file_uploader("📷 Lateral", type=['jpg', 'png'], key="p4")
            
            submitted = st.form_submit_button("✨ Enviar Consulta", use_container_width=True)
            
            if submitted and pregunta and foto1:
                fotos = [foto1, foto2, foto3, foto4]
                fotos_validas = [f for f in fotos if f is not None]
                
                with st.spinner("🔮 Procesando análisis profundo..."):
                    imagenes_procesadas = []
                    
                    for foto in fotos_validas:
                        img = Image.open(foto)
                        validacion = validar_calidad_imagen(img)
                        if validacion['valida']:
                            imagenes_procesadas.append(img)
                    
                    if imagenes_procesadas:
                        analisis_quiro = analisis_quirologico_completo(imagenes_procesadas)
                        ciclos = analizar_ciclos_temporales(fecha_nac, pregunta)
                        resultado = generar_analisis_completo(analisis_quiro, ciclos, pregunta)
                        
                        st.success("✅ ¡Análisis Premium completado!")
                        st.markdown(resultado, unsafe_allow_html=True)
                        
                        st.info(f"💰 Donación: ${monto:,} COP - Gracias por tu apoyo a esta labor social")
                        st.balloons()
                    else:
                        st.error("❌ No se pudieron procesar las imágenes. Por favor, sube fotos de mejor calidad.")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
