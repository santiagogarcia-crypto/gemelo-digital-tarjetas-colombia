# ==============================================================================
# GEMELO DIGITAL FINANCIERO: DASHBOARD INTEGRAL MULTIMODELO (STREAMLIT)
# Ruta local: F:\Santiago_IA\Gemelo_Digital_TC\app_dashboard.py
# ==============================================================================

import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Gemelo Digital Financiero - Tarjetas de Crédito Colombia",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = r"F:\Santiago_IA\Gemelo_Digital_TC"
OUT_DIR = os.path.join(BASE_DIR, "outputs")

st.title("🏛️ Gemelo Digital Financiero: Mercado de Tarjetas de Crédito en Colombia")
st.markdown("**Metodología:** Martínez Carazo (2006) | **Insumo:** Datos Abiertos SFC (Dataset `h2jg-r3zg`) | **Período:** 2021–2026")

# Menú lateral para navegar entre capas del Gemelo Digital
menu = st.sidebar.radio(
    "Seleccione la Capa de Análisis:",
    [
        "1. Serie Temporal e Ingesta SFC",
        "2. Constelación Financiera (Red Multilado)",
        "3. Segmentación Comportamental (K-Means)",
        "4. Modelo Econométrico de Diferenciación"
    ]
)

# ------------------------------------------------------------------------------
# CAPA 1: SERIE TEMPORAL
# ------------------------------------------------------------------------------
if menu == "1. Serie Temporal e Ingesta SFC":
    st.header("📈 Evolución Temporal del Mercado de Tarjetas de Crédito")
    csv_base = os.path.join(BASE_DIR, "data", "base_datos_caso_gemelo_digital.csv")
    
    if os.path.exists(csv_base):
        df = pd.read_csv(csv_base)
        col_fecha = 'fechacorte' if 'fechacorte' in df.columns else 'fecha'
        col_entidad = 'nombreentidad' if 'nombreentidad' in df.columns else 'nombre_entidad'
        col_tarjetas = 'total_tarjetas_credito' if 'total_tarjetas_credito' in df.columns else 'total_tarjetas'
        
        df[col_fecha] = pd.to_datetime(df[col_fecha])
        
        # Filtro multiselect
        entidades = st.multiselect("Seleccione Entidades a Comparar:", df[col_entidad].unique(), default=df[col_entidad].unique()[:5])
        df_filtered = df[df[col_entidad].isin(entidades)]
        
        fig = px.line(
            df_filtered, 
            x=col_fecha, 
            y=col_tarjetas, 
            color=col_entidad,
            title="Volumen Histórico de Plásticos Activos por Entidad",
            labels={col_fecha: "Fecha de Corte", col_tarjetas: "Total Tarjetas de Crédito"}
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.error("No se encontró la base de datos principal en `/data/base_datos_caso_gemelo_digital.csv`.")

# ------------------------------------------------------------------------------
# CAPA 2: CONSTELACIÓN FINANCIERA
# ------------------------------------------------------------------------------
elif menu == "2. Constelación Financiera (Red Multilado)":
    st.header("🕸️ Estructura Económica de la Constelación (Emisor - Adquirente - Comercio)")
    csv_const = os.path.join(OUT_DIR, "matriz_constelacion_financiera.csv")
    
    if os.path.exists(csv_const):
        df_c = pd.read_csv(csv_const)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Volumen Transado Total", f"${df_c['volumen_transado_mensual'].sum():,.0f} COP")
        col2.metric("Ingreso por Comisión Comercio (MDR)", f"${df_c['ingreso_mdr_comercio'].sum():,.0f} COP")
        col3.metric("Margen Operativo Neto de la Red", f"${df_c['margen_neto_operativo'].sum():,.0f} COP")
        
        fig_bar = px.bar(
            df_c.sort_values(by='volumen_transado_mensual', ascending=False).head(10),
            x='nombreentidad' if 'nombreentidad' in df_c.columns else 'Entidad',
            y=['ingreso_intereses', 'ingreso_mdr_comercio', 'ingreso_cuota_manejo'],
            title="Composición de Ingresos de la Constelación por Entidad (Top 10)",
            labels={'value': 'Pesos COP', 'variable': 'Fuente de Ingreso'},
            barmode='stack'
        )
        st.plotly_chart(fig_bar, width="stretch")
        st.dataframe(df_c)
    else:
        st.warning("Ejecute `python simulacion_constelacion.py` para generar esta capa.")

# ------------------------------------------------------------------------------
# CAPA 3: SEGMENTACIÓN COMPORTAMENTAL
# ------------------------------------------------------------------------------
elif menu == "3. Segmentación Comportamental (K-Means)":
    st.header("🎯 Perfiles Tipológicos del Consumidor (Sistema Recíproco Tríadico)")
    csv_perf = os.path.join(OUT_DIR, "perfiles_clientes_gemelo.csv")
    
    if os.path.exists(csv_perf):
        df_p = pd.read_csv(csv_perf)
        
        fig_scatter = px.scatter(
            df_p,
            x='Promedio_Plásticos',
            y='Ticket_Promedio_COP',
            color='Nombre_Perfil',
            hover_name='Entidad',
            size='Promedio_Plásticos',
            title="Mapa Comportamental de Clústeres (Monto vs. Escala de Plásticos)",
            labels={'Promedio_Plásticos': 'Volumen de Plásticos', 'Ticket_Promedio_COP': 'Ticket Promedio ($COP)'}
        )
        st.plotly_chart(fig_scatter, width="stretch")
        st.dataframe(df_p[['Entidad', 'Nombre_Perfil', 'Promedio_Plásticos', 'Ticket_Promedio_COP']])
    else:
        st.warning("Ejecute `python perfilamiento_clientes.py` para generar esta capa.")

# ------------------------------------------------------------------------------
# CAPA 4: MODELO ECONOMÉTRICO
# ------------------------------------------------------------------------------
elif menu == "4. Modelo Econométrico de Diferenciación":
    st.header("⚖️ Respuesta de Demanda e Inelasticidad Cruzada (Porter / Smith)")
    csv_econ = os.path.join(OUT_DIR, "modelo_diferenciacion_econometrico.csv")
    
    if os.path.exists(csv_econ):
        df_e = pd.read_csv(csv_econ)
        
        fig_diff = px.bar(
            df_e.sort_values(by='Variacion_Absoluta_Cuota', ascending=False).head(12),
            x='Entidad',
            y='Variacion_Absoluta_Cuota',
            color='Tipo',
            title="Sensibilidad de Cuota de Mercado ante Shock de Precio (+1.5% Cuota de Manejo)",
            labels={'Variacion_Absoluta_Cuota': 'Variación Absoluta en Cuota (%)', 'Tipo': 'Estrategia de Mercado'}
        )
        st.plotly_chart(fig_diff, width="stretch")
        st.dataframe(df_e[['Entidad', 'Tipo', 'Inelasticidad_Cruzada', 'Diferenciacion_Intangible', 'Cuota_Mercado_Actual', 'Cuota_Mercado_Proyectada', 'Variacion_Absoluta_Cuota']])
    else:
        st.warning("Ejecute `python modelo_econometrico_diferenciacion.py` para generar esta capa.")