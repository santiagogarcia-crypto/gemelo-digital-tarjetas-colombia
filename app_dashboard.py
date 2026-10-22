# ==============================================================================
# GEMELO DIGITAL FINANCIERO: DASHBOARD INTEGRAL MULTIMODELO (STREAMLIT)
# Mercado de Tarjetas de Crédito en Colombia (SFC)
# ==============================================================================

import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Configuración inicial de la página (Primera instrucción de Streamlit)
st.set_page_config(
    page_title="Gemelo Digital Financiero - Tarjetas de Crédito Colombia",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definición de rutas relativas dinámicas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "outputs")

# Importación segura del motor de reportes con diagnóstico de error
PDF_ERROR = None
try:
    from advanced_pdf_report_generator import FDTReportEngine
    PDF_DISPONIBLE = True
except Exception as e:
    PDF_DISPONIBLE = False
    PDF_ERROR = str(e)

# Encabezado principal
st.title("🏛️ Gemelo Digital Financiero: Mercado de Tarjetas de Crédito en Colombia")
st.markdown("**Metodología:** Martínez Carazo (2006) | **Insumo:** Datos Abiertos SFC (Dataset `h2jg-r3zg`) | **Período:** 2021–2026")
st.markdown("---")

# ==============================================================================
# BARRA LATERAL (SIDEBAR): NAVEGACIÓN Y PARÁMETROS DE SIMULACIÓN
# ==============================================================================
menu = st.sidebar.radio(
    "Seleccione la Capa de Análisis:",
    [
        "1. Serie Temporal e Ingesta SFC",
        "2. Constelación Financiera (Red Multilado)",
        "3. Segmentación Comportamental (K-Means)",
        "4. Modelo Econométrico de Diferenciación"
    ],
    key="nav_menu_radio_v3"
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Parámetros de Simulación (ML & PDF)")

# Slider de Shock de Precio sincronizado con Python y el Generador de PDF
shock_precio_pct = st.sidebar.slider(
    "Porcentaje Shock de Precio (%):",
    min_value=-15.0,
    max_value=15.0,
    value=0.0,
    step=1.0,
    format="%.1f%%",
    key="shock_slider_global"
) / 100.0  # Convierte porcentaje a decimal (ej: 5.0% -> 0.05)


# ==============================================================================
# CAPA 1: SERIE TEMPORAL E INGESTA SFC + POWER BI EMBEDDED
# ==============================================================================
if menu == "1. Serie Temporal e Ingesta SFC":
    st.header("📈 Evolución Temporal del Mercado de Tarjetas de Crédito")
    st.write("Exploración dinámica del volumen de plásticos e indicadores históricos de la SFC (Exclusivo Tarjetas de Crédito).")
    
    # --------------------------------------------------------------------------
    # CONEXIÓN INTEGRADA CON TU DASHBOARD DE POWER BI
    # --------------------------------------------------------------------------
    with st.expander("📊 Ver Tablero Ejecutivo de Sensibilidad (Power BI Embedded)", expanded=False):
        # URL de acceso a tu informe de Power BI
        POWER_BI_DIRECT_URL = "https://app.powerbi.com/groups/me/reports/d81204f7-8faa-443f-987d-6f637e8e9c99/7a892de421e47bbb6094?experience=power-bi"
        
        # URL formateada para iframe incrustado (Power BI Service View)
        POWER_BI_IFRAME_URL = "https://app.powerbi.com/reportEmbed?reportId=d81204f7-8faa-443f-987d-6f637e8e9c99&autoAuth=true"
        
        st.info("💡 Puedes interactuar con el panel directamente o abrirlo en pantalla completa con tu cuenta de Power BI.")
        st.link_button("🔗 Abrir Dashboard Directamente en Power BI", POWER_BI_DIRECT_URL, type="secondary")
        
        # Renderizado dentro del marco de Streamlit
        st.components.v1.iframe(POWER_BI_IFRAME_URL, height=600, scrolling=True)
    # --------------------------------------------------------------------------

    archivos_data = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')] if os.path.exists(DATA_DIR) else []
    
    if archivos_data:
        csv_base = os.path.join(DATA_DIR, archivos_data[0])
        try:
            df = pd.read_csv(csv_base)
            if df.empty:
                st.error(f"El archivo `{archivos_data[0]}` está vacío.")
            else:
                # --------------------------------------------------------------
                # FILTRADO EXCLUSIVO: EXCLUSIÓN PERMANENTE DE TARJETA DÉBITO
                # --------------------------------------------------------------
                if 'nombre_uca' in df.columns:
                    df = df[df['nombre_uca'] != 'TARJETA DEBITO']
                if 'cod_uca' in df.columns:
                    df = df[df['cod_uca'] != 6]
                if 'subcuenta' in df.columns:
                    df = df[~df['subcuenta'].astype(str).str.contains('DEBITO|Débito', case=False, na=False)]
                # --------------------------------------------------------------

                col_fecha = 'fechacorte' if 'fechacorte' in df.columns else ('fecha' if 'fecha' in df.columns else df.columns[0])
                col_entidad = 'nombreentidad' if 'nombreentidad' in df.columns else ('nombre_entidad' if 'nombre_entidad' in df.columns else df.columns[1])
                col_tarjetas = 'total_tarjetas_credito' if 'total_tarjetas_credito' in df.columns else ('total_tarjetas' if 'total_tarjetas' in df.columns else df.columns[2])
                
                df[col_fecha] = pd.to_datetime(df[col_fecha])
                
                # APLICACIÓN DEL SHOCK DE PRECIO EN TIEMPO REAL SOBRE PYTHON
                df[col_tarjetas] = df[col_tarjetas] * (1 + shock_precio_pct)

                entidades_disponibles = list(df[col_entidad].dropna().unique())
                entidades_default = entidades_disponibles[:5] if len(entidades_disponibles) >= 5 else entidades_disponibles
                
                entidades_seleccionadas = st.multiselect(
                    "Seleccione Entidades a Comparar:", 
                    options=entidades_disponibles, 
                    default=entidades_default,
                    key="multi_entidades_capa1_v3"
                )
                
                if entidades_seleccionadas:
                    df_filtered = df[df[col_entidad].isin(entidades_seleccionadas)]
                    
                    titulo_grafico = f"Volumen Histórico con Shock Simulado ({shock_precio_pct*100:+.1f}%)"
                    fig = px.line(df_filtered, x=col_fecha, y=col_tarjetas, color=col_entidad, title=titulo_grafico)
                    st.plotly_chart(fig, width='stretch', key="fig_linea_capa1_v3")
                    
                    with st.expander("🔍 Ver Tabla de Datos Filtrados y Simulados (SFC)"):
                        st.dataframe(df_filtered.sort_values(by=col_fecha, ascending=False))
        except Exception as e:
            st.error(f"Error al leer la fuente de datos CSV: {e}")
    else:
        st.error(f"No se encontró ningún archivo CSV en `{DATA_DIR}`.")

# ==============================================================================
# CAPA 2: CONSTELACIÓN FINANCIERA (RED MULTILADO)
# ==============================================================================
elif menu == "2. Constelación Financiera (Red Multilado)":
    st.header("🕸️ Estructura Económica de la Constelación Multilado")
    csv_const = os.path.join(OUT_DIR, "matriz_constelacion_financiera.csv")
    if os.path.exists(csv_const):
        try:
            df_c = pd.read_csv(csv_const)
            
            # Recálculo simulado por efecto del shock
            vol_simulado = df_c['volumen_transado_mensual'].sum() * (1 + shock_precio_pct)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Volumen Transado Simulado", f"${vol_simulado:,.0f} COP", delta=f"{shock_precio_pct*100:+.1f}%")
            col2.metric("Comisión Comercio (MDR)", f"${df_c['ingreso_mdr_comercio'].sum():,.0f} COP")
            col3.metric("Margen Operativo Neto", f"${df_c['margen_neto_operativo'].sum():,.0f} COP")
            
            col_entidad_c = 'nombreentidad' if 'nombreentidad' in df_c.columns else 'Entidad'
            fig_bar = px.bar(
                df_c.sort_values(by='volumen_transado_mensual', ascending=False).head(10),
                x=col_entidad_c, y=['ingreso_intereses', 'ingreso_mdr_comercio', 'ingreso_cuota_manejo'],
                title="Desglose de Fuentes de Ingreso", barmode='stack'
            )
            st.plotly_chart(fig_bar, width='stretch', key="fig_barras_capa2_v3")
        except Exception as e:
            st.error(f"Error al cargar la matriz de constelación: {e}")
    else:
        st.warning(f"No se encontró `{csv_const}`.")

# ==============================================================================
# CAPA 3: SEGMENTACIÓN COMPORTAMENTAL (K-MEANS)
# ==============================================================================
elif menu == "3. Segmentación Comportamental (K-Means)":
    st.header("🎯 Perfiles Tipológicos del Consumidor")
    csv_perf = os.path.join(OUT_DIR, "perfiles_clientes_gemelo.csv")
    if os.path.exists(csv_perf):
        try:
            df_p = pd.read_csv(csv_perf)
            fig_scatter = px.scatter(
                df_p, x='Promedio_Plásticos', y='Ticket_Promedio_COP', color='Nombre_Perfil',
                hover_name='Entidad', size='Promedio_Plásticos', title="Mapa Comportamental K-Means"
            )
            st.plotly_chart(fig_scatter, width='stretch', key="fig_scatter_capa3_v3")
        except Exception as e:
            st.error(f"Error al cargar perfiles: {e}")
    else:
        st.warning(f"No se encontró `{csv_perf}`.")

# ==============================================================================
# CAPA 4: MODELO ECONOMÉTRICO DE DIFERENCIACIÓN
# ==============================================================================
elif menu == "4. Modelo Econométrico de Diferenciación":
    st.header("⚖️ Respuesta de Demanda e Inelasticidad Cruzada")
    csv_econ = os.path.join(OUT_DIR, "modelo_diferenciacion_econometrico.csv")
    if os.path.exists(csv_econ):
        try:
            df_e = pd.read_csv(csv_econ)
            fig_diff = px.bar(
                df_e.sort_values(by='Variacion_Absoluta_Cuota', ascending=False).head(12),
                x='Entidad', y='Variacion_Absoluta_Cuota', color='Tipo', title=f"Sensibilidad ante Shock de Precio ({shock_precio_pct*100:+.1f}%)"
            )
            st.plotly_chart(fig_diff, width='stretch', key="fig_barras_capa4_v3")
        except Exception as e:
            st.error(f"Error al cargar modelo econométrico: {e}")
    else:
        st.warning(f"No se encontró `{csv_econ}`.")

# ==============================================================================
# BARRA LATERAL: SECCIÓN DEL GENERADOR DE REPORTES PDF
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.header("📄 Generador de Reporte PDF")

if PDF_DISPONIBLE:
    engine = FDTReportEngine(data_dir=DATA_DIR, outputs_dir=OUT_DIR)

    nombre_estudiante = st.sidebar.text_input("Nombre del Estudiante:", "Santiago García Carvajal", key="pdf_nom_v3")
    curso_estudiante = st.sidebar.text_input("Asignatura:", "Gerencia de Servicios Financieros", key="pdf_cur_v3")

    entidades_opts = ["Perspectiva Consolidada"]
    if not engine.df_const.empty and "nombreentidad" in engine.df_const.columns:
        entidades_opts.extend(list(engine.df_const["nombreentidad"].unique()))
    
    entidad_target = st.sidebar.selectbox("Entidad Objeto de Estudio:", entidades_opts, key="pdf_ent_v3")
    target_arg = None if entidad_target == "Perspectiva Consolidada" else entidad_target

    modulos_seleccionados = st.sidebar.multiselect(
        "Módulos en el PDF:",
        ["Serie Temporal SFC", "Constelación Financiera (Red Multilado)", "Segmentación Comportamental (K-Means)", "Modelo Econométrico de Diferenciación"],
        default=["Serie Temporal SFC", "Constelación Financiera (Red Multilado)", "Modelo Econométrico de Diferenciación"],
        key="pdf_mod_v3"
    )

    if st.sidebar.button("🎓 Generar PDF Personalizado", type="primary", key="pdf_btn_gen_v3"):
        student_info = {"nombre": nombre_estudiante, "curso": curso_estudiante}
        
        # DICCIONARIO ACTUALIZADO CON EL SHOCK SIMULADO Y ENVIADO AL PDF
        strategic_decisions = {
            "mk_externo": f"Ajuste por shock simulado de {shock_precio_pct*100:+.1f}%.",
            "mk_interno": "Optimización del margen neto operativo.",
            "mk_interactivo": "Alta disponibilidad en punto de pago.",
            "rub_ingesta": f"Análisis de series de tiempo SFC (Shock: {shock_precio_pct*100:+.1f}%).",
            "rub_multilado": "Estructuración de red de 6 enlaces.",
            "rub_kmeans": "Perfiles transaccionales identificados.",
            "rub_econ": "Modelo de inelasticidad cruzada."
        }

        pdf_buffer = engine.generate_pdf(
            filename="Reporte_Evaluacion_FDT.pdf",
            student_info=student_info,
            modules_selected=modulos_seleccionados,
            strategic_decisions=strategic_decisions,
            target_entity=target_arg
        )

        st.sidebar.success("¡PDF generado!")
        st.sidebar.download_button(
            label="⬇️ Descargar PDF de Evaluación",
            data=pdf_buffer,
            file_name=f"Reporte_FDT_{nombre_estudiante.replace(' ', '_')}.pdf",
            mime="application/pdf",
            key="pdf_btn_dl_v3"
        )
else:
    st.sidebar.error(f"Error de inicialización PDF: {PDF_ERROR}")
