# ==============================================================================
# FASE 3 Y 4: ANÁLISIS ESTADÍSTICO DESCRIPTIVO DEL GEMELO DIGITAL FINANCIERO
# Metodología: Martínez Carazo (2006) / Shaw (1999)
# Ruta local: F:\Santiago_IA\Gemelo_Digital_TC
# ==============================================================================

import os
import pandas as pd
import numpy as np

def generar_analisis_descriptivo():
    base_dir = r"F:\Santiago_IA\Gemelo_Digital_TC"
    data_path = os.path.join(base_dir, "data", "base_datos_caso_gemelo_digital.csv")
    outputs_dir = os.path.join(base_dir, "outputs")
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"No se encontró la base de datos en: {data_path}")
        
    print("[1/3] Cargando base de datos del Gemelo Digital...")
    df = pd.DataFrame(pd.read_csv(data_path))
    
    # 1. Resumen General del Sistema Financiero
    total_registros = len(df)
    total_tarjetas_recientes = df[df['fechacorte'] == df['fechacorte'].max()]['total_tarjetas_credito'].sum()
    entidades_unicas = df['nombreentidad'].nunique()
    
    print("\n========================================================")
    print("      RESUMEN EJECUTIVO - GEMELO DIGITAL FINANCIERO     ")
    print("========================================================")
    print(f"• Período analizado: {df['anio'].min()} - {df['anio'].max()}")
    print(f"• Volumen total de observaciones: {total_registros:,} registros")
    print(f"• Entidades financieras monitoreadas: {entidades_unicas} instituciones")
    print(f"• Parque total de tarjetas (Último corte): {total_tarjetas_recientes:,.0f} plásticos")
    print("========================================================\n")
    
    # 2. Concentración de Mercado por Entidad (Top 10)
    print("[2/3] Calculando participación de mercado (Market Share)...")
    ultimo_corte = df['fechacorte'].max()
    df_ultimo = df[df['fechacorte'] == ultimo_corte].copy()
    
    market_share = df_ultimo.groupby('nombreentidad')['total_tarjetas_credito'].sum().reset_index()
    market_share['participacion_pct'] = (market_share['total_tarjetas_credito'] / total_tarjetas_recientes) * 100
    market_share = market_share.sort_values(by='total_tarjetas_credito', ascending=False)
    
    # Índice de Herfindahl-Hirschman (HHI) para evaluar la concentración del mercado
    hhi = (market_share['participacion_pct'] ** 2).sum()
    
    # 3. Distribución por Tipo de Cliente (Persona Natural vs. Jurídica)
    total_natural = df_ultimo['persona_natural'].sum()
    total_juridica = df_ultimo['persona_juridica'].sum()
    pct_natural = (total_natural / total_tarjetas_recientes) * 100 if total_tarjetas_recientes > 0 else 0
    pct_juridica = (total_juridica / total_tarjetas_recientes) * 100 if total_tarjetas_recientes > 0 else 0
    
    # 4. Exportar Reporte Estadístico
    reporte_path = os.path.join(outputs_dir, "reporte_estratificacion_mercado.csv")
    market_share.to_csv(reporte_path, index=False, encoding='utf-8-sig')
    
    print("[3/3] Guardando reporte estadístico consolidado...")
    print(f" -> Guardado en: {reporte_path}\n")
    
    print("========================================================")
    print("               HALLAZGOS CLAVE DEL MERCADO              ")
    print("========================================================")
    print(f"1. ÍNDICE DE CONCENTRACIÓN (HHI): {hhi:.2f} puntos")
    if hhi < 1500:
        print("   Interpretación: Mercado competitivo y no concentrado.")
    elif 1500 <= hhi <= 2500:
        print("   Interpretación: Mercado moderadamente concentrado.")
    else:
        print("   Interpretación: Mercado altamente concentrado.")
        
    print(f"\n2. SEGMENTACIÓN DE CLIENTES:")
    print(f"   • Personas Naturales: {pct_natural:.2f}% ({total_natural:,.0f} tarjetas)")
    print(f"   • Personas Jurídicas: {pct_juridica:.2f}% ({total_juridica:,.0f} tarjetas)")
    
    print(f"\n3. TOP 5 ENTIDADES LÍDERES EN TARJETAS:")
    for idx, row in market_share.head(5).iterrows():
        print(f"   • {row['nombreentidad']}: {row['participacion_pct']:.2f}% del mercado ({row['total_tarjetas_credito']:,.0f} tarjetas)")
    print("========================================================")

if __name__ == "__main__":
    generar_analisis_descriptivo()