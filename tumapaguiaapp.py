"""
MAPA GUÍA DE TU DESTINO - Versión Premium Design
Diseño moderno con paleta dorado, azul navy y blanco

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

load_dotenv()

# ============================================================================
# CONFIGURACIÓN Y ESTILOS PREMIUM
# ============================================================================

st.set_page_config(
    page_title="Mapa Guía de tu Destino",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Premium con paleta Dorado, Navy y Blanco
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
    
    /* Contenedor principal */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Títulos dorados */
    h1, h2, h3 {
        color: #D4AF37 !important;
        font-family: 'Georgia', serif;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 1rem !important;
    }
    
    /* Texto general */
    p, li, label, .stMarkdown {
        color: #FAF9F6 !important;
    }
    
    /* Sidebar elegante */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A1128 0%, #1C2541 100%);
        border-right: 2px solid #D4AF37;
    }
    
    [data-testid="stSidebar"] h1 {
        color: #D4AF37 !important;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid #D4AF37;
    }
    
    /* Botones premium con efecto hover */
    .stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
        color: #0A1128;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #F4E4C1 0%, #D4AF37 100%);
        box-shadow: 0 6px 25px rgba(212, 175, 55, 0.5);
        transform: translateY(-2px);
    }
    
    /* Cards con efecto cristal */
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
    
    /* Inputs elegantes */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(26, 37, 65, 0.6);
        border: 2px solid rgba(212, 175, 55, 0.3);
        border-radius: 15px;
        color: #FAF9F6;
        padding: 1rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #D4AF37;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
    }
    
    /* Tarjetas de precios */
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
        transform: scale(1.05);
        box-shadow: 0 15px 60px rgba(212, 175, 55, 0.3);
    }
    
    .price-amount {
        font-size: 3rem;
        font-weight: bold;
        color: #D4AF37;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
    }
    
    /* Badges y etiquetas */
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
    
    /* Íconos con brillo */
    .icon-glow {
        filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.6));
    }
    
    /* Tabs personalizados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: rgba(26, 37, 65, 0.6);
        padding: 1rem;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: 2px solid rgba(212, 175, 55, 0.3);
        border-radius: 10px;
        color: #FAF9F6;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #D4AF37;
        background: rgba(212, 175, 55, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D4AF37 0%, #C19A2E 100%);
        color: #0A1128;
        border-color: #D4AF37;
    }
    
    /* Alertas y notificaciones */
    .stAlert {
        background: rgba(26, 37, 65, 0.8);
        border-left: 4px solid #D4AF37;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    /* Métricas elegantes */
    [data-testid="stMetricValue"] {
        color: #D4AF37 !important;
        font-size: 2.5rem !important;
        font-weight: bold !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(26, 37, 65, 0.6);
        border: 2px dashed rgba(212, 175, 55, 0.5);
        border-radius: 15px;
        padding: 2rem;
    }
    
    /* Radio buttons */
    .stRadio > label {
        background: rgba(26, 37, 65, 0.6);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(212, 175, 55, 0.3);
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .stRadio > label:hover {
        border-color: #D4AF37;
        background: rgba(212, 175, 55, 0.1);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(26, 37, 65, 0.8);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 10px;
        color: #D4AF37 !important;
    }
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 10px;
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
    
    /* Animación de entrada */
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
    
    /* Separador dorado */
    .gold-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #D4AF37 50%, transparent 100%);
        margin: 2rem 0;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Configuración de precios
PRECIOS = {
    'consulta_basica': 0,
    'consulta_premium': 15000,
    'suscripcion_mensual': 20000
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
                  referencia_pago TEXT,
                  analisis_automatico TEXT,
                  interpretacion_personal TEXT,
                  FOREIGN KEY (usuario_id) REFERENCES usuarios (id))''')
    
    conn.commit()
    return conn

# ============================================================================
# CONOCIMIENTO BASE
# ============================================================================

CICLOS_VITALES = {
    1: {'nombre': 'Nuevos Inicios', 'emoji': '🌟', 'energia': 'Liderazgo y creación', 
        'recomendaciones': 'Inicia proyectos nuevos, toma la iniciativa, sé valiente'},
    2: {'nombre': 'Cooperación', 'emoji': '🤝', 'energia': 'Asociaciones y diplomacia',
        'recomendaciones': 'Trabaja en equipo, cultiva relaciones, sé paciente'},
    3: {'nombre': 'Expresión Creativa', 'emoji': '🎨', 'energia': 'Creatividad y comunicación',
        'recomendaciones': 'Exprésate libremente, socializa, crea sin límites'},
    4: {'nombre': 'Construcción', 'emoji': '🏗️', 'energia': 'Disciplina y trabajo',
        'recomendaciones': 'Construye bases sólidas, sé constante, persevera'},
    5: {'nombre': 'Cambio y Libertad', 'emoji': '🦋', 'energia': 'Aventura y expansión',
        'recomendaciones': 'Acepta cambios, experimenta, viaja y explora'},
    6: {'nombre': 'Responsabilidad', 'emoji': '🏡', 'energia': 'Familia y servicio',
        'recomendaciones': 'Cuida a los tuyos, mejora tu hogar, sirve con amor'},
    7: {'nombre': 'Introspección', 'emoji': '🧘', 'energia': 'Espiritualidad y análisis',
        'recomendaciones': 'Medita, estudia, conócete profundamente'},
    8: {'nombre': 'Poder y Logros', 'emoji': '👑', 'energia': 'Éxito y reconocimiento',
        'recomendaciones': 'Busca el éxito, gestiona finanzas, lidera con poder'},
    9: {'nombre': 'Culminación', 'emoji': '🌅', 'energia': 'Cierre y sabiduría',
        'recomendaciones': 'Cierra ciclos, perdona, comparte tu sabiduría'}
}

# ============================================================================
# FUNCIONES DE PAGO
# ============================================================================

def mostrar_opciones_pago(monto, tipo_consulta):
    """Muestra las opciones de pago con diseño premium"""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>✨ Elige tu Método de Pago ✨</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card" style="text-align: center;">
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
        <div class="info-card" style="text-align: center;">
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
        <div class="info-card" style="text-align: center;">
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
                """)
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    if st.button("← Volver a métodos de pago", key="back_mp"):
        if 'metodo_pago' in st.session_state:
            del st.session_state.metodo_pago
        st.rerun()
    
    return None

def pago_wompi(monto, descripcion):
    """Integración Wompi con diseño premium"""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="info-card">
            <h2>🇨🇴 Wompi Colombia</h2>
            <p><strong>Servicio:</strong> {descripcion}</p>
            <p><strong>Métodos disponibles:</strong></p>
            <ul>
                <li>🏦 PSE - Pago Seguro en Línea</li>
                <li>📱 Nequi</li>
                <li>💰 Bancolombia (Botón o transferencia)</li>
                <li>💳 Tarjetas Visa, Mastercard, Amex</li>
                <li>🇨🇴 Empresa 100% colombiana certificada</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="price-card">
            <p style="color: #F4E4C1; margin: 0;">Total a pagar</p>
            <div class="price-amount">${monto:,.0f}</div>
            <p style="color: #F4E4C1; margin: 0;">COP</p>
            <div class="badge" style="margin-top: 1rem;">Comisión 2.99%</div>
        </div>
        """, unsafe_allow_html=True)
    
    public_key = os.getenv('WOMPI_PUBLIC_KEY')
    
    if public_key and public_key.startswith('pub_'):
        reference = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        widget_html = f"""
        <div style="text-align: center; padding: 20px; background: rgba(212, 175, 55, 0.1); border-radius: 15px; border: 2px solid #D4AF37;">
            <form>
                <script
                  src="https://checkout.wompi.co/widget.js"
                  data-render="button"
                  data-public-key="{public_key}"
                  data-currency="COP"
                  data-amount-in-cents="{int(monto * 100)}"
                  data-reference="{reference}"
                >
                </script>
            </form>
        </div>
        """
        
        st.components.v1.html(widget_html, height=200)
        
        st.success("""
        **✅ Después de pagar:**
        - Confirmación instantánea por email
        - Análisis personalizado en 24-48 horas
        - Notificación cuando esté listo
        """)
        
    else:
        st.warning("⚙️ Wompi requiere configuración")
        with st.expander("📖 Ver instrucciones"):
            st.markdown("""
            ### Configurar Wompi (10 minutos):
            
            **1.** Regístrate: https://comercios.wompi.co/
            **2.** Verifica tu identidad
            **3.** Ve a: Configuración → Llaves API
            **4.** Copia las llaves de prueba
            **5.** Agrégalas al .env:
            ```
            WOMPI_PUBLIC_KEY=pub_test_xxxxx
            WOMPI_PRIVATE_KEY=prv_test_xxxxx
            ```
            """)
    
    if st.button("← Volver a métodos de pago", key="back_wompi"):
        if 'metodo_pago' in st.session_state:
            del st.session_state.metodo_pago
        st.rerun()
    
    return None

def pago_paypal(monto, descripcion):
    """Integración PayPal con diseño premium"""
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    
    monto_usd = monto / 4200
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="info-card">
            <h2>💳 PayPal Internacional</h2>
            <p><strong>Servicio:</strong> {descripcion}</p>
            <p><strong>Métodos disponibles:</strong></p>
            <ul>
                <li>💳 Tarjetas internacionales Visa, Mastercard</li>
                <li>💰 Saldo de cuenta PayPal</li>
                <li>🌎 Acepta pagos desde cualquier país</li>
                <li>🔒 Protección del comprador incluida</li>
                <li>✅ Confianza global - Millones de usuarios</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="price-card">
            <p style="color: #F4E4C1; margin: 0;">Total a pagar</p>
            <div class="price-amount">${monto_usd:.2f}</div>
            <p style="color: #F4E4C1; margin: 0;">USD</p>
            <p style="color: #D4AF37; font-size: 0.9rem; margin-top: 1rem;">≈ ${monto:,.0f} COP</p>
        </div>
        """, unsafe_allow_html=True)
    
    client_id = os.getenv('PAYPAL_CLIENT_ID')
    
    if client_id:
        paypal_html = f"""
        <div style="text-align: center; padding: 30px; background: rgba(212, 175, 55, 0.1); border-radius: 15px; border: 2px solid #D4AF37;">
            <div id="paypal-button-container"></div>
        </div>
        <script src="https://www.paypal.com/sdk/js?client-id={client_id}&currency=USD"></script>
        <script>
          paypal.Buttons({{
            createOrder: function(data, actions) {{
              return actions.order.create({{
                purchase_units: [{{
                  amount: {{
                    value: '{monto_usd:.2f}'
                  }},
                  description: '{descripcion}'
                }}]
              }});
            }},
            onApprove: function(data, actions) {{
              return actions.order.capture().then(function(details) {{
                alert('✅ Pago completado exitosamente!');
              }});
            }},
            style: {{
              color: 'gold',
              shape: 'pill',
              label: 'pay',
              height: 50
            }}
          }}).render('#paypal-button-container');
        </script>
        """
        st.components.v1.html(paypal_html, height=300)
        
    else:
        st.warning("⚙️ PayPal requiere configuración")
        with st.expander("📖 Ver instrucciones"):
            st.markdown("""
            ### Configurar PayPal (15 minutos):
            
            **1.** Crea cuenta developer: https://developer.paypal.com/
            **2.** Ve a: Dashboard → My Apps & Credentials
            **3.** Crea una App en Sandbox
            **4.** Copia el Client ID
            **5.** Agrégalo al .env:
            ```
            PAYPAL_CLIENT_ID=tu-client-id-aqui
            PAYPAL_EMAIL=tu-email@paypal.com
            ```
            """)
    
    if st.button("← Volver a métodos de pago", key="back_paypal"):
        if 'metodo_pago' in st.session_state:
            del st.session_state.metodo_pago
        st.rerun()
    
    return None

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
    """Análisis gratuito con diseño premium"""
    ciclo_info = CICLOS_VITALES[ciclo]
    
    return f"""
<div class="info-card animate-in">
<h2 style="text-align: center;">{ciclo_info['emoji']} Año {ciclo}: {ciclo_info['nombre']} {ciclo_info['emoji']}</h2>

### ✨ Energía Dominante
<p style="font-size: 1.2rem; color: #F4E4C1;">{ciclo_info['energia']}</p>

### 🎯 Recomendaciones para este Ciclo
<p style="font-size: 1.1rem;">{ciclo_info['recomendaciones']}</p>

<div class="gold-divider"></div>

### ⭐ ¿Quieres profundizar más?

<div class="price-card" style="margin: 2rem 0;">
<h3>Análisis Premium Personalizado</h3>
<p>Incluye:</p>
<ul style="text-align: left;">
<li>✅ Lectura quirológica completa de tus manos</li>
<li>✅ Interpretación experta personalizada</li>
<li>✅ Combinación ciclos vitales + quirología</li>
<li>✅ Orientación específica para tu situación</li>
<li>✅ Respuesta detallada en 24-48 horas</li>
</ul>
<div class="price-amount">${PRECIOS['consulta_premium']:,.0f} COP</div>
</div>
</div>

<p style="text-align: center; color: #F4E4C1; font-style: italic; margin-top: 2rem;">
⚠️ Este análisis es orientativo para autoconocimiento. No sustituye consejo profesional.
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
    
    # SIDEBAR PREMIUM
    with st.sidebar:
        st.markdown('<h1 style="text-align: center;">🔮</h1>', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; font-size: 1.5rem;">Mapa Guía</h2>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        if not st.session_state.logged_in:
            pagina = st.radio("📍 Navegar:", ["Inicio", "Ingresar"], label_visibility="collapsed")
        else:
            st.markdown(f'<div class="badge">👤 {st.session_state.get("user_email", "Usuario")}</div>', 
                       unsafe_allow_html=True)
            pagina = st.radio("📍 Navegar:", [
                "Inicio",
                "Consulta Gratis",
                "Consulta Premium",
                "Mis Consultas",
                "Cerrar Sesión"
            ], label_visibility="collapsed")
            
            if pagina == "Cerrar Sesión":
                st.session_state.logged_in = False
                st.rerun()
        
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # Tarjeta de precios en sidebar
        st.markdown("""
        <div class="info-card">
        <h3 style="text-align: center;">💎 Precios</h3>
        <p><span class="badge">Básico: GRATIS</span></p>
        <p><span class="badge">Premium: $20.000 - $600.000 - Tú eliges el monto de la donacion</span></p>
        <p><span class="badge">Suscripción: $80.000/mes</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
        <h4>💳 Pagos aceptados:</h4>
        <p>💙 Mercado Pago</p>
        <p>🇨🇴 Wompi</p>
        <p>💳 PayPal</p>
        </div>
        """, unsafe_allow_html=True)
    
    # PÁGINA INICIO
    if pagina == "Inicio":
        st.markdown('<h1 class="animate-in">🔮 Mapa Guía de tu Destino 🔮</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 1.3rem; color: #F4E4C1;">Descubre tu camino a través de la Quirología y los Ciclos Vitales</p>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # Hero section con 3 columnas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="info-card animate-in">
            <h3 style="text-align: center;">✨ Autoconocimiento</h3>
            <p style="text-align: center;">Descubre tu potencial a través del análisis de tus manos y ciclos de vida</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-card animate-in">
            <h3 style="text-align: center;">🎯 Orientación</h3>
            <p style="text-align: center;">Recibe guía personalizada para tomar mejores decisiones en tu camino</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="info-card animate-in">
            <h3 style="text-align: center;">💎 Accesible</h3>
            <p style="text-align: center;">Precios sociales para democratizar el conocimiento esotérico</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # Sección de servicios
        st.markdown('<h2 style="text-align: center;">📋 Nuestros Servicios</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="price-card">
            <h3>🆓 Análisis Básico</h3>
            <div class="price-amount">GRATIS</div>
            <p style="color: #F4E4C1; margin: 1rem 0;">Incluye:</p>
            <ul style="text-align: left; color: #FAF9F6;">
            <li>✓ Cálculo de ciclo vital actual</li>
            <li>✓ Interpretación numerológica</li>
            <li>✓ Recomendaciones generales</li>
            <li>✓ Energía del año personal</li>
            <li>✓ Resultado inmediato</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="price-card">
            <h3>⭐ Análisis Premium</h3>
            <div class="price-amount">${PRECIOS['consulta_premium']:,.0f}</div>
            <p style="color: #F4E4C1; margin: 0;">COP</p>
            <p style="color: #F4E4C1; margin: 1rem 0;">Incluye TODO lo básico más:</p>
            <ul style="text-align: left; color: #FAF9F6;">
            <li>✓ Análisis quirológico completo</li>
            <li>✓ Lectura de líneas y montes</li>
            <li>✓ Interpretación experta personalizada</li>
            <li>✓ Orientación específica a tu pregunta</li>
            <li>✓ Entrega en 24-48 horas</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # Cómo funciona
        st.markdown('<h2 style="text-align: center;">🌟 ¿Cómo Funciona?</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="info-card" style="text-align: center;">
            <h1 style="font-size: 3rem;">1️⃣</h1>
            <h4>Regístrate</h4>
            <p>Crea tu cuenta en segundos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-card" style="text-align: center;">
            <h1 style="font-size: 3rem;">2️⃣</h1>
            <h4>Elige</h4>
            <p>Básico gratis o Premium</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="info-card" style="text-align: center;">
            <h1 style="font-size: 3rem;">3️⃣</h1>
            <h4>Envía</h4>
            <p>Tu consulta y fotos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="info-card" style="text-align: center;">
            <h1 style="font-size: 3rem;">4️⃣</h1>
            <h4>Recibe</h4>
            <p>Tu análisis detallado</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        # Disclaimer
        st.markdown("""
        <div class="info-card" style="border-color: rgba(212, 175, 55, 0.5);">
        <p style="text-align: center; font-size: 0.95rem; color: #F4E4C1;">
        ⚠️ <strong>IMPORTANTE:</strong> Esta plataforma es una herramienta de autoconocimiento y orientación personal. 
        No sustituye consejo médico, psicológico, legal o financiero profesional. Los resultados deben interpretarse 
        como guías reflexivas para el crecimiento personal. Tu libre albedrío y esfuerzo son los verdaderos 
        creadores de tu destino.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    # PÁGINA INGRESAR
    elif pagina == "Ingresar":
        st.markdown('<h1 class="animate-in">🔐 Acceso de Usuario</h1>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
        
        with tab1:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("👤 Iniciar Sesión")
            email = st.text_input("📧 Email", key="login_email")
            password = st.text_input("🔒 Contraseña", type="password", key="login_pass")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("✨ Iniciar Sesión", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.user_id = 1
                    st.success("✅ Sesión iniciada exitosamente")
                    st.balloons()
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("✨ Crear Cuenta Nueva")
            nombre = st.text_input("👤 Nombre completo")
            email_reg = st.text_input("📧 Email", key="email_reg")
            password_reg = st.text_input("🔒 Contraseña", type="password", key="pass_reg")
            password_confirm = st.text_input("🔒 Confirmar contraseña", type="password")
            
            acepta = st.checkbox("✓ Acepto términos de servicio y política de privacidad")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🌟 Crear Cuenta", use_container_width=True):
                    if password_reg == password_confirm and acepta:
                        st.success("✅ Cuenta creada exitosamente")
                        st.balloons()
                    else:
                        st.error("Verifica los datos ingresados")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # PÁGINA CONSULTA GRATIS
    elif pagina == "Consulta Gratis":
        st.markdown('<h1 class="animate-in">🆓 Análisis Básico Gratuito</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #F4E4C1;">Descubre tu ciclo vital actual de forma inmediata</p>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("📅 Ingresa tu Fecha de Nacimiento")
            
            fecha_nac = st.date_input(
                "Selecciona tu fecha",
                min_value=datetime(1920, 1, 1),
                max_value=datetime.now(),
                label_visibility="collapsed"
            )
            
            if st.button("🔮 Generar mi Análisis Gratis", use_container_width=True):
                with st.spinner("✨ Calculando tu ciclo vital..."):
                    ciclo = calcular_ciclo_vital(fecha_nac)
                    analisis = generar_analisis_basico(ciclo)
                    
                    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
                    st.markdown(analisis, unsafe_allow_html=True)
                    
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                    with col_btn2:
                        if st.button("⭐ Quiero el Análisis Premium", use_container_width=True):
                            st.session_state.upgrade_premium = True
                            st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # PÁGINA CONSULTA PREMIUM
    elif pagina == "Consulta Premium":
        st.markdown('<h1 class="animate-in">⭐ Consulta Premium Personalizada</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align: center; font-size: 1.3rem;"><span class="badge">Precio: ${PRECIOS["consulta_premium"]:,.0f} COP</span></p>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        
        with st.form("consulta_premium"):
            st.subheader("💭 Tu Consulta")
            pregunta = st.text_area(
                "¿Qué aspecto de tu vida deseas explorar?",
                placeholder="Ejemplo: Estoy considerando un cambio de carrera y busco orientación sobre cuál camino tomar basado en mi potencial natural...",
                height=150
            )
            
            col1, col2 = st.columns(2)
            with col1:
                fecha_nac = st.date_input(
                    "📅 Fecha de nacimiento",
                    min_value=datetime(1920, 1, 1),
                    max_value=datetime.now()
                )
            
            st.markdown("### 📸 Fotos de tus Manos")
            st.info("💡 Toma fotos con buena iluminación, fondo claro, sin joyas")
            
            col1, col2 = st.columns(2)
            with col1:
                foto1 = st.file_uploader("🖐️ Palma derecha", type=['jpg', 'png', 'jpeg'])
                if foto1:
                    st.image(foto1, caption="Palma derecha", use_container_width=True)
            
            with col2:
                foto2 = st.file_uploader("🖐️ Palma izquierda", type=['jpg', 'png', 'jpeg'])
                if foto2:
                    st.image(foto2, caption="Palma izquierda", use_container_width=True)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submitted = st.form_submit_button("✨ Continuar al Pago", use_container_width=True)
            
            if submitted and pregunta and foto1:
                st.session_state.consulta_pendiente = {
                    'pregunta': pregunta,
                    'fecha_nac': fecha_nac,
                    'foto1': foto1,
                    'foto2': foto2
                }
                st.session_state.mostrar_pago = True
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mostrar opciones de pago
        if st.session_state.get('mostrar_pago'):
            resultado_pago = mostrar_opciones_pago(
                PRECIOS['consulta_premium'],
                "Consulta Premium - Mapa Guía de tu Destino"
            )
            
            if resultado_pago:
                st.success("✅ ¡Pago registrado exitosamente!")
                st.markdown("""
                <div class="info-card" style="text-align: center;">
                <h3>🎉 ¡Gracias por tu confianza!</h3>
                <p>Tu consulta ha sido recibida y será procesada por nuestro equipo de expertos.</p>
                <p><strong>📧 Recibirás tu análisis detallado en 24-48 horas por email</strong></p>
                <p>🔔 Te notificaremos cuando esté listo</p>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
                st.session_state.mostrar_pago = False
    
    # PÁGINA MIS CONSULTAS
    elif pagina == "Mis Consultas":
        st.markdown('<h1 class="animate-in">📋 Mis Consultas</h1>', unsafe_allow_html=True)
        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
        <h3>📊 Historial de Consultas</h3>
        
        <div style="margin: 1rem 0; padding: 1rem; background: rgba(212, 175, 55, 0.1); border-radius: 10px; border-left: 4px solid #D4AF37;">
        <h4>⭐ Consulta Premium - 20/11/2024</h4>
        <p><strong>Estado:</strong> <span class="badge">✅ Completada</span></p>
        <p><strong>Tema:</strong> Orientación profesional</p>
        <button style="background: #D4AF37; color: #0A1128; padding: 0.5rem 1rem; border: none; border-radius: 10px; cursor: pointer;">Ver Análisis Completo</button>
        </div>
        
        <div style="margin: 1rem 0; padding: 1rem; background: rgba(212, 175, 55, 0.1); border-radius: 10px; border-left: 4px solid #D4AF37;">
        <h4>🆓 Consulta Básica - 15/11/2024</h4>
        <p><strong>Estado:</strong> <span class="badge">✅ Completada</span></p>
        <p><strong>Ciclo:</strong> Año 5 - Cambio y Libertad</p>
        <button style="background: #D4AF37; color: #0A1128; padding: 0.5rem 1rem; border: none; border-radius: 10px; cursor: pointer;">Ver Resultado</button>
        </div>
        
        <div style="margin: 1rem 0; padding: 1rem; background: rgba(212, 175, 55, 0.1); border-radius: 10px; border-left: 4px solid #D4AF37;">
        <h4>⭐ Consulta Premium - 10/11/2024</h4>
        <p><strong>Estado:</strong> <span class="badge" style="background: #FFA500;">⏳ En proceso</span></p>
        <p><strong>Tema:</strong> Relaciones personales</p>
        <p style="color: #F4E4C1;"><em>Tu análisis estará listo en aproximadamente 18 horas</em></p>
        </div>
        
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
