"""
MAPA GUÍA DE TU DESTINO - Versión Colombia
Con múltiples opciones de pago adaptadas a Colombia

OPCIONES DE INTEGRACIÓN:
1. Mercado Pago (Recomendada para LATAM)
2. Wompi (Colombiana - Mejor para Colombia)
3. PayPal (Internacional)
4. Transferencia Manual (Sin pasarela)

INSTALACIÓN:
py -m pip install streamlit pandas opencv-python mediapipe pillow bcrypt python-dotenv requests

Para Mercado Pago:
py -m pip install mercadopago

CONFIGURACIÓN (.env):
# Elige UNA opción:

# OPCIÓN 1 - MERCADO PAGO
MERCADOPAGO_ACCESS_TOKEN=tu_access_token
# Obtener en: https://www.mercadopago.com.co/developers

# OPCIÓN 2 - WOMPI
WOMPI_PUBLIC_KEY=pub_test_xxx
WOMPI_PRIVATE_KEY=prv_test_xxx
# Obtener en: https://comercios.wompi.co/

# OPCIÓN 3 - PAYPAL
PAYPAL_CLIENT_ID=tu_client_id
PAYPAL_CLIENT_SECRET=tu_client_secret
# Obtener en: https://developer.paypal.com/

# OPCIÓN 4 - TRANSFERENCIA MANUAL
BANCO_NOMBRE=Bancolombia
BANCO_CUENTA=1234567890
BANCO_TIPO=Ahorros
BANCO_TITULAR=Tu Nombre
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
# CONFIGURACIÓN
# ============================================================================

st.set_page_config(
    page_title="Mapa Guía de tu Destino",
    page_icon="🔮",
    layout="wide"
)

# Configuración de precios
PRECIOS = {
    'consulta_basica': 0,  # Gratis
    'consulta_premium': 15000,  # COP (aprox $3-4 USD)
    'suscripcion_mensual': 20000  # COP (aprox $5 USD)
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
    
    c.execute('''CREATE TABLE IF NOT EXISTS pagos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  consulta_id INTEGER,
                  usuario_id INTEGER,
                  monto REAL,
                  moneda TEXT DEFAULT 'COP',
                  metodo TEXT,
                  referencia_externa TEXT,
                  estado TEXT DEFAULT 'pendiente',
                  fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (consulta_id) REFERENCES consultas (id))''')
    
    conn.commit()
    return conn

# ============================================================================
# CONOCIMIENTO BASE
# ============================================================================

CICLOS_VITALES = {
    1: {'nombre': 'Nuevos Inicios', 'energia': 'Liderazgo, creación', 
        'recomendaciones': 'Inicia proyectos nuevos, toma iniciativa'},
    2: {'nombre': 'Cooperación', 'energia': 'Asociaciones, diplomacia',
        'recomendaciones': 'Trabaja en equipo, cultiva relaciones'},
    3: {'nombre': 'Expresión Creativa', 'energia': 'Creatividad, comunicación',
        'recomendaciones': 'Exprésate, socializa, crea'},
    4: {'nombre': 'Construcción', 'energia': 'Disciplina, trabajo',
        'recomendaciones': 'Construye bases sólidas, sé constante'},
    5: {'nombre': 'Cambio', 'energia': 'Libertad, aventura',
        'recomendaciones': 'Acepta cambios, experimenta cosas nuevas'},
    6: {'nombre': 'Responsabilidad', 'energia': 'Familia, hogar',
        'recomendaciones': 'Cuida a los tuyos, mejora tu hogar'},
    7: {'nombre': 'Introspección', 'energia': 'Espiritualidad, análisis',
        'recomendaciones': 'Medita, estudia, conócete profundamente'},
    8: {'nombre': 'Poder', 'energia': 'Éxito, logros materiales',
        'recomendaciones': 'Busca reconocimiento, gestiona finanzas'},
    9: {'nombre': 'Culminación', 'energia': 'Cierre, sabiduría',
        'recomendaciones': 'Cierra ciclos, perdona, ayuda a otros'}
}

# ============================================================================
# FUNCIONES DE PAGO
# ============================================================================

def mostrar_opciones_pago(monto, tipo_consulta):
    """Muestra las opciones de pago disponibles"""
    st.markdown("---")
    st.subheader("💳 Selecciona tu Método de Pago")
    
    # Mostrar las 3 opciones en columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.image("https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_111x69.jpg", width=100)
        if st.button("💳 PayPal", use_container_width=True, key="btn_paypal"):
            st.session_state.metodo_pago = "PayPal"
    
    with col2:
        st.markdown("### 🇨🇴 Wompi")
        st.caption("PSE, Nequi, Tarjetas")
        if st.button("💰 Wompi", use_container_width=True, key="btn_wompi"):
            st.session_state.metodo_pago = "Wompi"
    
    with col3:
        st.markdown("### 💙 Mercado Pago")
        st.caption("Tarjetas, PSE")
        if st.button("💳 Mercado Pago", use_container_width=True, key="btn_mp"):
            st.session_state.metodo_pago = "Mercado Pago"
    
    # Procesar según el método seleccionado
    if 'metodo_pago' in st.session_state:
        metodo = st.session_state.metodo_pago
        
        if metodo == "PayPal":
            return pago_paypal(monto, tipo_consulta)
        
        elif metodo == "Wompi":
            return pago_wompi(monto, tipo_consulta)
        
        elif metodo == "Mercado Pago":
            return pago_mercadopago(monto, tipo_consulta)
    
    return None

def pago_transferencia_manual(monto):
    """Pago por transferencia manual"""
    st.info(f"""
    ### 💰 Transferencia Bancaria
    
    **Monto a pagar:** ${monto:,.0f} COP
    
    **Datos de la cuenta:**
    - Banco: {os.getenv('BANCO_NOMBRE', 'Bancolombia')}
    - Tipo: {os.getenv('BANCO_TIPO', 'Ahorros')}
    - Número: {os.getenv('BANCO_CUENTA', '1234-5678-90')}
    - Titular: {os.getenv('BANCO_TITULAR', 'Tu Nombre')}
    
    **También puedes usar:**
    - 📱 Nequi: {os.getenv('NEQUI_NUMERO', '300-123-4567')}
    - 🏦 PSE: Transferencia inmediata
    
    **Después de realizar la transferencia:**
    1. Toma captura del comprobante
    2. Sube la imagen abajo
    3. Recibirás tu análisis en 24-48 horas
    """)
    
    referencia = st.text_input("Número de referencia/comprobante:")
    comprobante = st.file_uploader("Sube tu comprobante de pago", type=['jpg', 'png', 'pdf'])
    
    if st.button("✅ Confirmar Pago Manual"):
        if referencia and comprobante:
            return {
                'metodo': 'transferencia_manual',
                'referencia': referencia,
                'estado': 'pendiente_verificacion',
                'comprobante': comprobante
            }
        else:
            st.warning("Por favor completa todos los campos")
            return None
    
    return None

def pago_mercadopago(monto, descripcion):
    """Integración con Mercado Pago"""
    st.markdown("---")
    st.markdown("### 💙 Pagar con Mercado Pago")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"""
        **Descripción:** {descripcion}
        
        **Monto:** ${monto:,.0f} COP
        
        Mercado Pago acepta:
        - 💳 Tarjetas de crédito/débito
        - 🏦 PSE (Transferencia bancaria)
        - 💰 Saldo Mercado Pago
        - 📱 Cuotas sin interés disponibles
        - 🔒 Compra protegida
        """)
    
    with col2:
        st.metric("Total a pagar", f"${monto:,.0f} COP")
    
    try:
        access_token = os.getenv('MERCADOPAGO_ACCESS_TOKEN')
        
        if access_token and (access_token.startswith('TEST-') or access_token.startswith('APP_')):
            import mercadopago
            
            sdk = mercadopago.SDK(access_token)
            
            # Crear preferencia de pago
            preference_data = {
                "items": [
                    {
                        "title": descripcion,
                        "quantity": 1,
                        "currency_id": "COP",
                        "unit_price": float(monto)
                    }
                ],
                "back_urls": {
                    "success": "https://tu-app.streamlit.app/success",
                    "failure": "https://tu-app.streamlit.app/failure",
                    "pending": "https://tu-app.streamlit.app/pending"
                },
                "auto_return": "approved",
                "notification_url": "https://tu-app.streamlit.app/webhooks/mercadopago"
            }
            
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            
            st.success("✅ Enlace de pago generado con Mercado Pago")
            
            # Mostrar botón de pago
            st.markdown("**Haz clic para ir a Mercado Pago:**")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                st.link_button(
                    "🔗 Pagar con Mercado Pago",
                    preference['init_point'],
                    use_container_width=True
                )
            
            st.info("""
            **¿Qué pasa después?**
            1. Serás redirigido a Mercado Pago
            2. Elige tu método de pago preferido
            3. Completa el pago de forma segura
            4. Regresa automáticamente aquí
            5. Tu consulta será procesada
            """)
            
            # Opción para confirmar manualmente
            with st.expander("¿Ya pagaste? Confirma aquí"):
                ref_manual = st.text_input("ID de pago de Mercado Pago:", key="ref_mp")
                if st.button("✅ Confirmar Pago", key="confirm_mp"):
                    if ref_manual:
                        return {
                            'metodo': 'mercadopago',
                            'referencia': ref_manual,
                            'estado': 'pendiente_verificacion',
                            'preference_id': preference['id']
                        }
            
            return None
        
        else:
            st.warning("⚠️ Mercado Pago no está configurado")
            
            st.markdown("""
            ### 🔧 Configurar Mercado Pago (5 minutos):
            
            **Paso 1:** Crea tu cuenta
            - Ve a: https://www.mercadopago.com.co/
            - Regístrate gratis
            - Verifica tu identidad
            
            **Paso 2:** Obtén credenciales de prueba
            - Inicia sesión
            - Ve a: Tus integraciones → Credenciales
            - Selecciona "Credenciales de prueba"
            - Copia el "Access Token" (empieza con `TEST-`)
            
            **Paso 3:** Instala la librería
            ```bash
            py -m pip install mercadopago
            ```
            
            **Paso 4:** Agrégalo al archivo .env
            ```
            MERCADOPAGO_ACCESS_TOKEN=TEST-1234567890-XXXXXX
            ```
            
            **Paso 5:** Reinicia la app
            """)
            
            st.info("💡 Mercado Pago es muy popular en LATAM. Comisión: 3.99% + IVA")
    
    except ImportError:
        st.error("❌ Librería de Mercado Pago no instalada")
        st.code("py -m pip install mercadopago")
        st.markdown("Ejecuta este comando en tu terminal y reinicia la app")
    
    except Exception as e:
        st.error(f"Error al conectar con Mercado Pago: {str(e)}")
        st.info("Verifica que tu Access Token sea correcto y esté activo")
    
    if st.button("← Volver a opciones de pago", key="back_mp"):
        if 'metodo_pago' in st.session_state:
            del st.session_state.metodo_pago
        st.rerun()
    
    return None

def pago_wompi(monto, descripcion):
    """Integración con Wompi (Colombia)"""
    st.markdown("---")
    st.markdown("### 🇨🇴 Pagar con Wompi")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.success(f"""
        **Descripción:** {descripcion}
        
        **Monto:** ${monto:,.0f} COP
        
        Wompi acepta:
        - 💳 Tarjetas crédito/débito (Visa, Mastercard, Amex)
        - 🏦 PSE (Pago Seguro en Línea)
        - 📱 Nequi
        - 💰 Bancolombia (Botón o transferencia)
        - 🔒 100% Seguro - Empresa colombiana certificada
        """)
    
    with col2:
        st.metric("Total a pagar", f"${monto:,.0f} COP")
    
    public_key = os.getenv('WOMPI_PUBLIC_KEY')
    
    if public_key and public_key.startswith('pub_'):
        # Widget de Wompi real
        reference = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        st.markdown("**Haz clic en el botón para pagar:**")
        
        # Widget oficial de Wompi
        widget_html = f"""
        <div style="text-align: center; padding: 20px;">
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
        <script>
            window.addEventListener('message', function(event) {{
                if (event.data.status === 'APPROVED') {{
                    window.parent.postMessage({{type: 'wompi_success', reference: '{reference}'}}, '*');
                }}
            }});
        </script>
        """
        
        st.components.v1.html(widget_html, height=200)
        
        st.info("""
        **Después de completar el pago:**
        - Recibirás confirmación por email
        - Tu consulta será procesada automáticamente
        - Análisis listo en 24-48 horas
        """)
        
        # Botón para confirmar manualmente si es necesario
        with st.expander("¿Ya pagaste? Confirma aquí"):
            ref_manual = st.text_input("Referencia de pago Wompi:", key="ref_wompi")
            if st.button("✅ Confirmar Pago", key="confirm_wompi"):
                if ref_manual:
                    return {
                        'metodo': 'wompi',
                        'referencia': ref_manual,
                        'estado': 'pendiente_verificacion'
                    }
    
    else:
        st.warning("⚠️ Wompi no está configurado completamente")
        
        st.markdown("""
        ### 🔧 Configurar Wompi (5 minutos):
        
        **Paso 1:** Regístrate en Wompi
        - Ve a: https://comercios.wompi.co/
        - Crea tu cuenta gratis
        - Verifica tu email
        
        **Paso 2:** Obtén tus llaves de prueba
        - Inicia sesión en Wompi
        - Ve a: Configuración → Llaves API
        - Copia tu "Llave pública de prueba" (empieza con `pub_test_`)
        
        **Paso 3:** Agrégala al archivo .env
        ```
        WOMPI_PUBLIC_KEY=pub_test_TU_LLAVE_AQUI
        WOMPI_PRIVATE_KEY=prv_test_TU_LLAVE_AQUI
        ```
        
        **Paso 4:** Reinicia la app
        """)
        
        st.info("💡 Wompi es la pasarela más popular en Colombia. Comisión: 2.99% + IVA")
    
    if st.button("← Volver a opciones de pago", key="back_wompi"):
        if 'metodo_pago' in st.session_state:
            del st.session_state.metodo_pago
        st.rerun()
    
    return None

def pago_paypal(monto, descripcion):
    """Integración con PayPal"""
    monto_usd = monto / 4200  # Conversión aproximada COP a USD
    
    st.markdown("---")
    st.markdown("### 💳 Pagar con PayPal")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"""
        **Descripción:** {descripcion}
        
        **Monto:** ${monto_usd:.2f} USD (aprox ${monto:,.0f} COP)
        
        PayPal acepta:
        - 💳 Tarjetas de crédito/débito internacionales
        - 💰 Saldo de cuenta PayPal
        - 🌎 Pagos desde cualquier país
        """)
    
    with col2:
        st.metric("Total a pagar", f"${monto_usd:.2f} USD")
        st.caption(f"≈ ${monto:,.0f} COP")
    
    # Botón de PayPal (versión simplificada)
    paypal_client_id = os.getenv('PAYPAL_CLIENT_ID')
    
    if paypal_client_id:
        # Widget de PayPal real
        paypal_html = f"""
        <div id="paypal-button-container"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={paypal_client_id}&currency=USD"></script>
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
                alert('Pago completado exitosamente!');
                window.parent.postMessage({{type: 'paypal_success', orderID: data.orderID}}, '*');
              }});
            }}
          }}).render('#paypal-button-container');
        </script>
        """
        st.components.v1.html(paypal_html, height=300)
    else:
        st.warning("⚠️ PayPal no configurado completamente")
        st.markdown("""
        **Para activar pagos con PayPal:**
        1. Ve a: https://developer.paypal.com/
        2. Crea una app
        3. Obtén tu Client ID
        4. Agrégalo al archivo .env como `PAYPAL_CLIENT_ID`
        
        **Mientras tanto, puedes recibir pagos por:**
        """)
        
        paypal_email = os.getenv('PAYPAL_EMAIL', 'tu_email@paypal.com')
        
        st.code(f"Envía ${monto_usd:.2f} USD a: {paypal_email}")
        
        referencia_paypal = st.text_input("ID de transacción PayPal (después de pagar):")
        
        if st.button("✅ Confirmar Pago PayPal", key="confirm_paypal"):
            if referencia_paypal:
                return {
                    'metodo': 'paypal',
                    'referencia': referencia_paypal,
                    'estado': 'pendiente_verificacion',
                    'monto_usd': monto_usd
                }
            else:
                st.warning("Ingresa el ID de transacción")
    
    if st.button("← Volver a opciones de pago", key="back_paypal"):
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
    """Análisis gratuito básico"""
    ciclo_info = CICLOS_VITALES[ciclo]
    
    return f"""
## 🔮 ANÁLISIS BÁSICO DE CICLO VITAL (Gratis)

### 🌙 Tu Ciclo Actual: Año {ciclo}
**{ciclo_info['nombre']}**

**Energía dominante:**
{ciclo_info['energia']}

**Recomendaciones generales:**
{ciclo_info['recomendaciones']}

---

### ⭐ ¿Quieres más profundidad?

El **análisis Premium** incluye:
- ✅ Lectura quirológica completa de tus manos
- ✅ Interpretación personalizada por experto
- ✅ Combinación de ciclos vitales + quirología
- ✅ Orientación específica para tu situación
- ✅ Respuesta en 24-48 horas

**Precio:** ${PRECIOS['consulta_premium']:,.0f} COP

---
⚠️ Análisis orientativo para autoconocimiento. No sustituye consejo profesional.
"""

def generar_analisis_premium_plantilla(ciclo, pregunta):
    """Plantilla para análisis premium"""
    ciclo_info = CICLOS_VITALES[ciclo]
    
    return f"""
## 🔮 ANÁLISIS PREMIUM PERSONALIZADO

**Tu pregunta:** {pregunta}

**Ciclo Vital Actual:** Año {ciclo} - {ciclo_info['nombre']}

### 📋 ANÁLISIS QUIROLÓGICO
[Aquí irá el análisis detallado de tus manos una vez procesadas las fotos]

### 🎯 INTERPRETACIÓN PERSONALIZADA
[Aquí irá la interpretación del experto combinando quirología + ciclos + tu situación específica]

### 💡 RECOMENDACIONES ESPECÍFICAS
[Recomendaciones personalizadas basadas en tu consulta]

---
*Este análisis será completado por un experto en 24-48 horas*
"""

# ============================================================================
# INTERFAZ
# ============================================================================

def main():
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = init_db()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Sidebar
    with st.sidebar:
        st.title("🔮 Navegación")
        
        if not st.session_state.logged_in:
            pagina = st.radio("Ir a:", ["Inicio", "Ingresar"])
        else:
            st.success(f"👤 {st.session_state.get('user_email', 'Usuario')}")
            pagina = st.radio("Ir a:", [
                "Inicio",
                "Consulta Gratis",
                "Consulta Premium",
                "Mis Consultas",
                "Cerrar Sesión"
            ])
            
            if pagina == "Cerrar Sesión":
                st.session_state.logged_in = False
                st.rerun()
        
        st.markdown("---")
        st.info("""
        ### 💰 Métodos de Pago Disponibles
        - 💙 **Mercado Pago** - Tarjetas, PSE, cuotas
        - 🇨🇴 **Wompi** - PSE, Nequi, Bancolombia
        - 💳 **PayPal** - Internacional
        """)
    
    # PÁGINA INICIO
    if pagina == "Inicio":
        st.title("🔮 Mapa Guía de tu Destino")
        st.subheader("Plataforma de Autoconocimiento - Colombia")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### ✨ Bienvenido
            
            Plataforma colombiana de quirología y ciclos vitales.
            
            **Servicios:**
            - 🆓 Análisis básico de ciclos (Gratis)
            - ⭐ Análisis premium con quirología ($15.000 COP)
            - 💎 Suscripción mensual ($20.000 COP)
            
            **Métodos de pago:**
            - 💙 Mercado Pago (Tarjetas, PSE, cuotas)
            - 🇨🇴 Wompi (PSE, Nequi, Bancolombia)
            - 💳 PayPal (Internacional)
            """)
        
        with col2:
            st.markdown("""
            ### 🎯 Cómo funciona
            
            **Consulta Gratis:**
            1. Regístrate
            2. Ingresa tu fecha de nacimiento
            3. Recibe análisis de ciclo vital inmediato
            
            **Consulta Premium:**
            1. Envía tu pregunta + fotos de manos
            2. Elige método de pago
            3. Recibe análisis personalizado en 24-48h
            
            **Labor Social:**
            Precios accesibles para democratizar el autoconocimiento
            """)
        
        st.warning("⚠️ Herramienta de autoconocimiento. No sustituye consejo profesional médico, psicológico o legal.")
    
    # PÁGINA INGRESAR
    elif pagina == "Ingresar":
        st.title("🔐 Acceso")
        
        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
        
        with tab1:
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            
            if st.button("Iniciar Sesión"):
                # Simplificado para demo
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_id = 1
                st.success("✅ Sesión iniciada")
                st.rerun()
        
        with tab2:
            nombre = st.text_input("Nombre")
            email_reg = st.text_input("Email", key="email_reg")
            password_reg = st.text_input("Contraseña", type="password", key="pass_reg")
            
            if st.button("Registrarse"):
                st.success("✅ Registrado. Ahora inicia sesión.")
    
    # PÁGINA CONSULTA GRATIS
    elif pagina == "Consulta Gratis":
        st.title("🆓 Análisis Básico Gratuito")
        
        st.info("Análisis de ciclo vital basado en tu fecha de nacimiento")
        
        fecha_nac = st.date_input(
            "Tu fecha de nacimiento",
            min_value=datetime(1920, 1, 1),
            max_value=datetime.now()
        )
        
        if st.button("🔮 Generar Análisis Gratis"):
            ciclo = calcular_ciclo_vital(fecha_nac)
            analisis = generar_analisis_basico(ciclo)
            
            st.success("✅ Análisis completado")
            st.markdown(analisis)
            
            st.markdown("---")
            if st.button("⭐ Quiero el Análisis Premium"):
                st.session_state.upgrade_premium = True
                st.rerun()
    
    # PÁGINA CONSULTA PREMIUM
    elif pagina == "Consulta Premium":
        st.title("⭐ Consulta Premium")
        st.subheader(f"Precio: ${PRECIOS['consulta_premium']:,.0f} COP")
        
        with st.form("consulta_premium"):
            pregunta = st.text_area(
                "¿Qué aspecto de tu vida deseas explorar?",
                placeholder="Ejemplo: Estoy considerando un cambio de carrera...",
                height=150
            )
            
            fecha_nac = st.date_input(
                "Fecha de nacimiento",
                min_value=datetime(1920, 1, 1),
                max_value=datetime.now()
            )
            
            st.markdown("### 📸 Fotos de tus manos")
            col1, col2 = st.columns(2)
            with col1:
                foto1 = st.file_uploader("Palma derecha", type=['jpg', 'png'])
            with col2:
                foto2 = st.file_uploader("Palma izquierda", type=['jpg', 'png'])
            
            submitted = st.form_submit_button("Continuar al Pago")
            
            if submitted and pregunta and foto1:
                st.session_state.consulta_pendiente = {
                    'pregunta': pregunta,
                    'fecha_nac': fecha_nac,
                    'foto1': foto1,
                    'foto2': foto2
                }
                st.session_state.mostrar_pago = True
        
        # Mostrar opciones de pago
        if st.session_state.get('mostrar_pago'):
            resultado_pago = mostrar_opciones_pago(
                PRECIOS['consulta_premium'],
                "Consulta Premium - Mapa Guía de tu Destino"
            )
            
            if resultado_pago:
                st.success("✅ Pago registrado. Recibirás tu análisis en 24-48 horas por email.")
                st.balloons()
                st.session_state.mostrar_pago = False
    
    # PÁGINA MIS CONSULTAS
    elif pagina == "Mis Consultas":
        st.title("📋 Mis Consultas")
        
        st.info("Aquí verás el historial de tus consultas y sus análisis")
        
        # Simulación de consultas
        st.markdown("""
        ### Consultas Recientes
        
        1. **Consulta Premium** - 20/05/2024
           - Estado: ✅ Completada
           - [Ver Análisis](#)
        
        2. **Consulta Básica** - 15/05/2024
           - Estado: ✅ Completada
           - [Ver Análisis](#)
        """)

if __name__ == "__main__":
    main()