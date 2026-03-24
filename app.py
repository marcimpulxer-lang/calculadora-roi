import streamlit as st
import pandas as pd
from PIL import Image
import io

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS DE MARCA AVANZADOS
st.set_page_config(page_title="Calculadora ROI Impulxer", layout="wide")

brand_color = "#996600"

st.markdown(f"""
    <style>
    /* Fondo general */
    .main {{ background-color: #f8f9fa; }}
    
    /* --- FUENTES Y TÍTULOS --- */
    .main-title {{
        font-size: 2.2rem;
        font-weight: bold;
        color: #333333;
        margin-bottom: 1rem;
    }}
    
    @media (max-width: 768px) {{
        .main-title {{ font-size: 1.5rem !important; }}
        .stImage img {{ width: 140px !important; }}
    }}

    /* --- CORRECCIÓN DE COLORES (SIDEBAR Y SLIDERS) --- */
    /* El círculo y la línea del Slider */
    div[data-baseweb="slider"] > div > div {{
        background-color: {brand_color} !important;
    }}
    /* Los números que aparecen al mover el slider */
    div[data-testid="stThumbValue"] {{
        background-color: {brand_color} !important;
        color: white !important;
    }}
    /* Bordes de los inputs (cuadros de texto/número) al hacer clic */
    div[data-baseweb="input"] > div:focus-within {{
        border-color: {brand_color} !important;
    }}

    /* --- CORRECCIÓN DE PESTAÑAS (TABS) --- */
    /* Línea inferior de la pestaña activa */
    button[aria-selected="true"] {{
        border-bottom-color: {brand_color} !important;
        color: {brand_color} !important;
    }}
    /* Texto de la pestaña al pasar el ratón (hover) */
    button[data-testid="stBaseButton-tab"]:hover p {{
        color: {brand_color} !important;
    }}
    /* Color del texto de la pestaña seleccionada */
    button[aria-selected="true"] p {{
        color: {brand_color} !important;
    }}

    /* --- MÉTRICAS Y BARRAS --- */
    div[data-testid="stMetricValue"] {{ color: {brand_color}; }}
    .stProgress > div > div > div > div {{
        background-color: {brand_color} !important;
    }}

    /* --- FOOTER --- */
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #555555;
        text-align: center;
        padding: 10px;
        font-size: 0.75rem;
        border-top: 1px solid #e0e0e0;
        z-index: 1000;
    }}
    /* Espacio extra al final para que el footer no tape el contenido */
    .content-spacer {{ height: 80px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. LOGO Y TÍTULO
try:
    image = Image.open('Logo Academia-black (1).png')
    st.image(image, width=200)
except FileNotFoundError:
    st.info("Sube el logo a GitHub para visualizarlo.")

st.markdown('<p class="main-title">📊 Simulador de Rentabilidad de Aparatología</p>', unsafe_allow_html=True)

# 3. SIDEBAR
with st.sidebar:
    st.header("🖊️ Identificación")
    nombre_aparato = st.text_input("Nombre del Aparato", value="Láser Diodo")
    marca_aparato = st.text_input("Marca / Modelo", value="Impulxer Pro")
    st.markdown("---")
    st.header("📋 Inversión")
    inv_sin_iva = st.number_input("Inversión (sin IVA)", value=15000.0)
    iva_pct = st.slider("IVA %", 0, 21, 21)
    costes_adic = st.number_input("Formación/Otros", value=300.0)
    intereses = st.number_input("Intereses", value=2000.0)
    st.header("⏱️ Capacidad")
    anos_amort = st.slider("Años amortización", 1, 10, 5)
    semanas_ano = st.slider("Semanas/año", 1, 52, 48)
    sesiones_sem_max = st.number_input("Capacidad máx (ses/sem)", value=30)
    st.header("💰 Venta")
    precio_sesion = st.number_input("Precio sesión (€)", value=60.0)
    sesiones_reales_mes = st.slider("Sesiones reales/mes", 1, 100, 6)

# 4. CÁLCULOS
inv_total_iva = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
coste_mensual = (inv_total_iva / anos_amort) / 12
total_ses_teoricas = anos_amort * semanas_ano * sesiones_sem_max
coste_u_sesion = inv_total_iva / total_ses_teoricas if total_ses_teoricas > 0 else 0
beneficio_sesion = precio_sesion - coste_u_sesion
margen_pct = (beneficio_sesion / precio_sesion) * 100 if precio_sesion > 0 else 0
beneficio_mensual = (sesiones_reales_mes * precio_sesion) - coste_mensual

# 5. DASHBOARD
st.subheader(f"Equipo: {nombre_aparato} | {marca_aparato}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Inversión Total", f"{inv_total_iva:,.0f} €")
c2.metric("Coste Fijo Mes", f"{coste_mensual:,.2f} €")
c3.metric("Beneficio Mes", f"{beneficio_mensual:,.2f} €")
c4.metric("Rentable", "✅ SÍ" if beneficio_mensual > 0 else "❌ NO")

t1, t2 = st.tabs(["🔍 Análisis", "📈 Escenarios"])
with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"**Coste/Sesión:** {coste_u_sesion:.2f} €")
        st.write(f"**Punto de equilibrio:** {coste_mensual/precio_sesion:.2f} ses/mes")
    with col_b:
        st.write(f"**Margen Bruto:** {margen_pct:.1f}%")
        st.progress(min(max(margen_pct/100, 0.0), 1.0))

with t2:
    esc = [5, 10, 20, 30, 50]
    df = pd.DataFrame([[s, f"{s*precio_sesion:,.0f} €", f"{(s*precio_sesion)-coste_mensual:,.0f} €"] for s in esc], 
                      columns=["Ses/Mes", "Ingresos", "Neto"])
    st.table(df)

# 6. DESCARGA Y FOOTER
st.markdown("---")
if st.download_button("💾 Descargar Informe (TXT)", f"ROI {nombre_aparato}\nInv: {inv_total_iva}€\nBen: {beneficio_mensual}€", f"ROI_{nombre_aparato}.txt"):
    st.success("¡Informe generado!")

st.markdown('<div class="content-spacer"></div>', unsafe_allow_html=True)
st.markdown(f"""<div class="footer">Este simulador es orientativo. Impulxer Academy no se hace responsable de discrepancias. <b>Propiedad de Impulxer Academy SL - 2026</b></div>""", unsafe_allow_html=True)
