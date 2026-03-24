import streamlit as st
import pandas as pd
from PIL import Image
from fpdf import FPDF
import io
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS AVANZADOS (CSS)
st.set_page_config(page_title="Calculadora ROI Impulxer", layout="wide")

brand_color = "#996600"

st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    .main-title {{ font-size: 2.2rem; font-weight: bold; margin-bottom: 1rem; }}
    @media (max-width: 768px) {{
        .main-title {{ font-size: 1.5rem !important; }}
        .stImage img {{ width: 150px !important; }}
        div[data-testid="stMetricValue"] {{ font-size: 1.4rem !important; }}
    }}
    .stProgress > div > div > div > div {{ background-color: {brand_color}; }}
    button[data-testid="stMarkdownContainer"] p {{ font-size: 1.1rem; }}
    button[aria-selected="true"] {{ border-bottom-color: {brand_color} !important; }}
    button[data-testid="stBaseButton-tab"]:hover {{ color: {brand_color} !important; }}
    div[data-testid="stMetricValue"] {{ color: {brand_color}; }}
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #ffffff; color: #555555; text-align: center;
        padding: 15px; font-size: 0.8rem; border-top: 1px solid #e0e0e0; z-index: 1000;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. SECCIÓN SUPERIOR: LOGO
try:
    logo_path = 'Logo Academia-black (1).png'
    image = Image.open(logo_path)
    st.image(image, width=220)
except FileNotFoundError:
    logo_path = None
    st.warning("Logo no encontrado en GitHub.")

st.markdown('<p class="main-title">📊 Simulador de Rentabilidad de Aparatología</p>', unsafe_allow_html=True)
st.markdown("---")

# 3. BARRA LATERAL (ENTRADAS)
with st.sidebar:
    st.header("🖊️ Identificación del Equipo")
    nombre_aparato = st.text_input("Nombre del Aparato", value="Ej: Láser Diodo")
    marca_aparato = st.text_input("Marca / Modelo", value="Ej: Impulxer Pro")
    st.markdown("---")
    st.header("📋 Datos de la Inversión")
    inv_sin_iva = st.number_input("Inversión Equipo (sin IVA)", value=15000.0, step=500.0)
    iva_pct = st.slider("IVA %", 0, 21, 21)
    costes_adic = st.number_input("Formación y otros costes", value=300.0)
    intereses = st.number_input("Intereses financiación", value=2000.0)
    st.header("⏱️ Capacidad de Trabajo")
    anos_amort = st.slider("Años de amortización", 1, 10, 5)
    semanas_ano = st.slider("Semanas laborales/año", 1, 52, 48)
    sesiones_sem_max = st.number_input("Capacidad máx. (sesiones/sem)", value=30)
    minutos_sesion = st.number_input("Minutos por sesión", value=60)
    st.header("💰 Estrategia de Precios")
    precio_sesion = st.number_input("Precio de venta sesión (€)", value=60.0)
    sesiones_reales_mes = st.slider("Sesiones reales al mes", 1, 100, 6)

# 4. CÁLCULOS MAESTROS
inv_total_iva = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
coste_mensual = (inv_total_iva / anos_amort) / 12
total_ses_teoricas = anos_amort * semanas_ano * sesiones_sem_max
coste_unitario_sesion = inv_total_iva / total_ses_teoricas if total_ses_teoricas > 0 else 0
beneficio_sesion = precio_sesion - coste_unitario_sesion
margen_pct = (beneficio_sesion / precio_sesion) * 100 if precio_sesion > 0 else 0
punto_equilibrio_mes = coste_mensual / precio_sesion if precio_sesion > 0 else 0
beneficio_mensual_real = (sesiones_reales_mes * precio_sesion) - coste_mensual

# 5. DASHBOARD PRINCIPAL
st.subheader(f"Análisis para: {nombre_aparato} ({marca_aparato})")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Inversión Total", f"{inv_total_iva:,.2f} €")
col2.metric("Coste Mensual Fijo", f"{coste_mensual:,.2f} €")
col3.metric("Beneficio Mensual", f"{beneficio_mensual_real:,.2f} €")
col4.metric("¿Es Rentable?", "✅ SÍ" if beneficio_mensual_real > 0 else "❌ NO")

st.markdown("---")

tab1, tab2 = st.tabs(["🔍 Análisis Detallado", "📈 Escenarios de Crecimiento"])
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Costes Unitarios")
        st.write(f"**Coste por sesión:** {coste_unitario_sesion:.2f} €")
        st.write(f"**Sesiones necesarias al mes:** {punto_equilibrio_mes:.2f}")
    with c2:
        st.subheader("Margen de Beneficio")
        st.write(f"**Margen Bruto:** {margen_pct:.2f}%")
        st.progress(min(max(margen_pct/100, 0.0), 1.0))

with tab2:
    st.subheader("Comparativa de Volumen")
    escenarios = [5, 10, 20, 30, 40, 50]
    data_escenarios = []
    for s in escenarios:
        ben = (s * precio_sesion) - coste_mensual
        data_escenarios.append([s, f"{s*precio_sesion:,.2f} €", f"{ben:,.2f} €", "Sí" if ben > 0 else "No"])
    st.table(pd.DataFrame(data_escenarios, columns=["Sesiones/Mes", "Ingresos", "Beneficio Neto", "Rentable"]))

# 6. GENERACIÓN DE PDF
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Logo
    if logo_path:
        pdf.image(logo_path, x=10, y=8, w=40)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "", ln=1) # Espacio
    pdf.cell(0, 10, "INFORME DE RENTABILIDAD", ln=1, align="C")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align="R")
    pdf.ln(5)
    
    # Datos Equipo
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " DATOS DEL EQUIPO", ln=1, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f" Aparato: {nombre_aparato}", ln=1)
    pdf.cell(0, 8, f" Marca/Modelo: {marca_aparato}", ln=1)
    pdf.ln(5)
    
    # Resultados
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " RESUMEN FINANCIERO MENSUAL", ln=1, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f" Inversion Total: {inv_total_iva:,.2f} EUR", ln=1)
    pdf.cell(0, 8, f" Coste Fijo Mensual: {coste_mensual:,.2f} EUR", ln=1)
    pdf.cell(0, 8, f" Beneficio Neto (con {sesiones_reales_mes} sesiones): {beneficio_mensual_real:,.2f} EUR", ln=1)
    pdf.ln(10)
    
    # Disclaimer
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5, "Disclaimer: Este informe es una simulacion orientativa basada en los datos introducidos por el usuario. Impulxer Academy SL no se hace responsable de discrepancias con la realidad. Propiedad de Impulxer Academy SL - 2026")
    
    return pdf.output()

st.markdown("---")
st.subheader("📥 Generar Informe Profesional")
if st.button("🚀 Preparar PDF"):
    pdf_bytes = create_pdf()
    st.download_button(
        label="💾 Descargar PDF Oficial",
        data=pdf_bytes,
        file_name=f"ROI_{nombre_aparato.replace(' ','_')}.pdf",
        mime="application/pdf"
    )

# 7. FOOTER
st.markdown(f"""<div class="footer">Este simulador es orientativo. Impulxer Academy no se hace responsable de discrepancias con la realidad.<br><strong>Propiedad de Impulxer Academy SL - 2026</strong></div>""", unsafe_allow_html=True)
