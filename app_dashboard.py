# ==============================================================================
# GEMELO DIGITAL FINANCIERO: DASHBOARD INTEGRAL MULTIMODELO (STREAMLIT)
# Mercado de Tarjetas de Crédito en Colombia (SFC)
# ==============================================================================

import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(
    page_title="Gemelo Digital Financiero - Tarjetas de Crédito Colombia",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definición de rutas relativas dinámicas para compatibilidad con Streamlit Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "outputs")

# Encabezado principal del Dashboard
st.title("🏛️ Gemelo Digital Financiero: Mercado de Tarjetas de Crédito en Colombia")
st.markdown("**Metodología:** Martínez Carazo (2006) | **Insumo:** Datos Abiertos SFC (Dataset `h2jg-r3zg`) | **Período:** 2021–2026")
st.markdown("---")

# Menú de navegación en la barra lateral
menu = st.sidebar.radio(
    "Seleccione la Capa de Análisis:",
    [
        "1. Serie Temporal e Ingesta SFC",
        "2. Constelación Financiera (Red Multilado)",
        "3. Segmentación Comportamental (K-Means)",
        "4. Modelo Econométrico de Diferenciación"
    ]
)

# ==============================================================================
# CAPA 1: SERIE TEMPORAL E INGESTA SFC
# ==============================================================================
if menu == "1. Serie Temporal e Ingesta SFC":
    st.header("📈 Evolución Temporal del Mercado de Tarjetas de Crédito")
    st.write("Exploración dinámica del volumen de plásticos e indicadores históricos de la Superintendencia Financiera de Colombia.")
    
    # Detección dinámica del archivo CSV en la carpeta data/
    archivos_data = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')] if os.path.exists(DATA_DIR) else []
    
    if archivos_data:
        csv_base = os.path.join(DATA_DIR, archivos_data[0])
        df = pd.read_csv(csv_base)
        
        # Identificación flexible de columnas
        col_fecha = 'fechacorte' if 'fechacorte' in df.columns else ('fecha' if 'fecha' in df.columns else df.columns[0])
        col_entidad = 'nombreentidad' if 'nombreentidad' in df.columns else ('nombre_entidad' if 'nombre_entidad' in df.columns else df.columns[1])
        col_tarjetas = 'total_tarjetas_credito' if 'total_tarjetas_credito' in df.columns else ('total_tarjetas' if 'total_tarjetas' in df.columns else df.columns[2])
        
        df[col_fecha] = pd.to_datetime(df[col_fecha])
        
        # Filtro de entidades multiselect
        entidades_disponibles = list(df[col_entidad].dropna().unique())
        entidades_default = entidades_disponibles[:5] if len(entidades_disponibles) >= 5 else entidades_disponibles
        
        entidades_seleccionadas = st.multiselect(
            "Seleccione Entidades a Comparar:", 
            options=entidades_disponibles, 
            default=entidades_default
        )
        
        if entidades_seleccionadas:
            df_filtered = df[df[col_entidad].isin(entidades_seleccionadas)]
            
            fig = px.line(
                df_filtered, 
                x=col_fecha, 
                y=col_tarjetas, 
                color=col_entidad,
                title="Volumen Histórico de Plásticos Activos por Entidad",
                labels={col_fecha: "Fecha de Corte", col_tarjetas: "Total Tarjetas de Crédito", col_entidad: "Entidad Financiera"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("🔍 Ver Tabla de Datos Filtrados (SFC)"):
                st.dataframe(df_filtered.sort_values(by=col_fecha, ascending=False))
        else:
            st.info("Por favor, seleccione al menos una entidad en el filtro superior.")
    else:
        st.error(f"No se encontró ningún archivo CSV en el directorio de datos: `{DATA_DIR}`.")

# ==============================================================================
# CAPA 2: CONSTELACIÓN FINANCIERA (RED MULTILADO)
# ==============================================================================
elif menu == "2. Constelación Financiera (Red Multilado)":
    st.header("🕸️ Estructura Económica de la Constelación (Emisor - Adquirente - Comercio)")
    st.write("Análisis de la plataforma de múltiples lados: ingresos por tasas rotativas, comisión al comercio (MDR) y cuotas de manejo.")
    
    csv_const = os.path.join(OUT_DIR, "matriz_constelacion_financiera.csv")
    
    if os.path.exists(csv_const):
        df_c = pd.read_csv(csv_const)
        
        # Métricas agregadas
        col1, col2, col3 = st.columns(3)
        col1.metric("Volumen Transado Total", f"${df_c['volumen_transado_mensual'].sum():,.0f} COP")
        col2.metric("Ingreso por Comisión Comercio (MDR)", f"${df_c['ingreso_mdr_comercio'].sum():,.0f} COP")
        col3.metric("Margen Operativo Neto de la Red", f"${df_c['margen_neto_operativo'].sum():,.0f} COP")
        
        st.markdown("### Composición de Ingresos por Entidad")
        col_entidad_c = 'nombreentidad' if 'nombreentidad' in df_c.columns else 'Entidad'
        
        fig_bar = px.bar(
            df_c.sort_values(by='volumen_transado_mensual', ascending=False).head(10),
            x=col_entidad_c,
            y=['ingreso_intereses', 'ingreso_mdr_comercio', 'ingreso_cuota_manejo'],
            title="Desglose de Fuentes de Ingreso de la Constelación (Top 10 Entidades)",
            labels={'value': 'Pesos COP', 'variable': 'Fuente de Ingreso', col_entidad_c: 'Entidad'},
            barmode='stack'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        with st.expander("📄 Ver Matriz Financiera Completa de la Constelación"):
            st.dataframe(df_c)
    else:
        st.warning(f"No se encontró el archivo de la constelación en `{csv_const}`. Asegúrese de haber subido la carpeta `/outputs` a GitHub.")

# ==============================================================================
# CAPA 3: SEGMENTACIÓN COMPORTAMENTAL (K-MEANS)
# ==============================================================================
elif menu == "3. Segmentación Comportamental (K-Means)":
    st.header("🎯 Perfiles Tipológicos del Consumidor (Sistema Recíproco Tríadico)")
    st.write("Agrupamiento no supervisado K-Means / RFM sobre hábitos transaccionales y escala de plásticos.")
    
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
            title="Mapa Comportamental de Clústeres (Ticket Promedio vs. Escala de Plásticos)",
            labels={
                'Promedio_Plásticos': 'Volumen Promedio de Plásticos', 
                'Ticket_Promedio_COP': 'Ticket Promedio ($COP)',
                'Nombre_Perfil': 'Perfil Comportamental'
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        with st.expander("📊 Ver Detalle de Entidades por Clúster"):
            st.dataframe(df_p[['Entidad', 'Nombre_Perfil', 'Promedio_Plásticos', 'Ticket_Promedio_COP']])
    else:
        st.warning(f"No se encontró el archivo de perfiles en `{csv_perf}`. Asegúrese de haber subido la carpeta `/outputs` a GitHub.")

# ==============================================================================
# CAPA 4: MODELO ECONOMÉTRICO DE DIFERENCIACIÓN
# ==============================================================================
elif menu == "4. Modelo Econométrico de Diferenciación":
    st.header("⚖️ Respuesta de Demanda e Inelasticidad Cruzada (Porter / Smith)")
    st.write("Simulación econométrica de migración de cuota de mercado ante un shock de precio (+1.5% en cuota de manejo).")
    
    csv_econ = os.path.join(OUT_DIR, "modelo_diferenciacion_econometrico.csv")
    
    if os.path.exists(csv_econ):
        df_e = pd.read_csv(csv_econ)
        
        fig_diff = px.bar(
            df_e.sort_values(by='Variacion_Absoluta_Cuota', ascending=False).head(12),
            x='Entidad',
            y='Variacion_Absoluta_Cuota',
            color='Tipo',
            title="Sensibilidad de Cuota de Mercado ante Shock de Precio (+1.5% Cuota de Manejo)",
            labels={
                'Variacion_Absoluta_Cuota': 'Variación Absoluta en Cuota (%)', 
                'Tipo': 'Estrategia de Mercado',
                'Entidad': 'Entidad Financiera'
            }
        )
        st.plotly_chart(fig_diff, use_container_width=True)
        
        with st.expander("📈 Ver Indicadores Econométricos e Inelasticidad Cruzada"):
            col_mostrar = ['Entidad', 'Tipo', 'Inelasticidad_Cruzada', 'Diferenciacion_Intangible', 'Cuota_Mercado_Actual', 'Cuota_Mercado_Proyectada', 'Variacion_Absoluta_Cuota']
            cols_existentes = [c for c in col_mostrar if c in df_e.columns]
            st.dataframe(df_e[cols_existentes])
    else:
        st.warning(f"No se encontró el archivo econométrico en `{csv_econ}`. Asegúrese de haber subido la carpeta `/outputs` a GitHub.")
