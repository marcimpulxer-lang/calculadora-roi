import streamlit as st

st.set_page_config(page_title="Simulador de Inversión App", layout="centered")

st.title("📊 Calculadora de ROI - Aparatología")
st.markdown("---")

# --- BARRA LATERAL (ENTRADAS) ---
st.sidebar.header("Configuración de la Inversión")
inv_sin_iva = st.sidebar.number_input("Inversión (sin IVA)", value=15000.0)
iva_pct = st.sidebar.slider("IVA %", 0, 21, 21)
costes_adic = st.sidebar.number_input("Costes Adicionales", value=300.0)
intereses = st.sidebar.number_input("Intereses Financiación", value=2000.0)

st.sidebar.header("Variables de Venta")
precio_sesion = st.sidebar.number_input("Precio medio por sesión", value=60.0)
sesiones_mes = st.sidebar.slider("Sesiones estimadas al mes", 1, 100, 6)

# --- CÁLCULOS (Lógica de tu Excel) ---
inv_total = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
amort_meses = 60 # 5 años como en tu Excel
coste_mensual_equipo = inv_total / amort_meses
coste_por_sesion = inv_total / (5 * 48 * 30) # Basado en tus celdas de capacidad

beneficio_mensual = (sesiones_mes * precio_sesion) - coste_mensual_equipo
es_rentable = "🟢 Sí" if beneficio_mensual > 0 else "🔴 No"

# --- RESULTADOS VISUALES ---
col1, col2, col3 = st.columns(3)
col1.metric("Inversión Total", f"{inv_total:,.2f} €")
col2.metric("Beneficio Mensual", f"{beneficio_mensual:,.2f} €")
col3.metric("¿Rentable?", es_rentable)

st.markdown("---")
st.subheader("Análisis de Amortización")
st.write(f"Para cubrir los **{coste_mensual_equipo:.2f} €** que cuesta el equipo al mes, necesitas realizar al menos **{coste_mensual_equipo / precio_sesion:.2f}** sesiones mensuales.")
