# ==============================================================================
# GEMELO DIGITAL FINANCIERO: MODELO ECONOMÉTRICO DE DIFERENCIACIÓN Y SEGMENTACIÓN
# Ruta local: F:\Santiago_IA\Gemelo_Digital_TC\modelo_econometrico_diferenciacion.py
# ==============================================================================

import os
import pandas as pd
import numpy as np

def estimar_modelo_diferenciacion_demanda():
    data_path = r"F:\Santiago_IA\Gemelo_Digital_TC\data\base_datos_caso_gemelo_digital.csv"
    
    if not os.path.exists(data_path):
        print(f"Error: No se encontró la base de datos en {data_path}")
        return

    print("[1/3] Cargando microdatos de la Superintendencia Financiera...")
    df = pd.read_csv(data_path)
    
    col_entidad = next((c for c in ['nombreentidad', 'nombre_entidad', 'entidad'] if c in df.columns), None)
    col_tarjetas = next((c for c in ['total_tarjetas_credito', 'total_tarjetas', 'tarjetas_activas'] if c in df.columns), None)
    
    # Agregación por entidad
    mercado = df.groupby(col_entidad)[col_tarjetas].mean().reset_index()
    mercado.columns = ['Entidad', 'Plásticos_Promedio']
    
    # Total mercado
    total_plasticos = mercado['Plásticos_Promedio'].sum()
    mercado['Cuota_Mercado_Actual'] = mercado['Plásticos_Promedio'] / total_plasticos

    print("[2/3] Parametrizando Vectores de Diferenciación y Segmentación...")
    
    # Asignación de Índice de Diferenciación Intangible (Z) y Especialización (X)
    # Basado en la teoría de Porter (1976) y Smith (1956)
    def asignar_atributos_estrategicos(nombre):
        nombre_upper = str(nombre).upper()
        if 'AGRARIO' in nombre_upper:
            return {'Tipo': 'Segmentada Especializada (Agro)', 'Inelasticidad_Cruzada': 0.85, 'Diferenciacion_Intangible': 0.3}
        elif 'CAJA SOCIAL' in nombre_upper:
            return {'Tipo': 'Gremial / Comunitario', 'Inelasticidad_Cruzada': 0.70, 'Diferenciacion_Intangible': 0.6}
        elif 'DAVIVIENDA' in nombre_upper or 'BANCOLOMBIA' in nombre_upper:
            return {'Tipo': 'Multisegmento / Franquicias Top', 'Inelasticidad_Cruzada': 0.90, 'Diferenciacion_Intangible': 0.95}
        elif 'BOGOTA' in nombre_upper or 'BBVA' in nombre_upper:
            return {'Tipo': 'Estilo de Vida / Corporativo', 'Inelasticidad_Cruzada': 0.75, 'Diferenciacion_Intangible': 0.80}
        else:
            return {'Tipo': 'Estándar / Masivo', 'Inelasticidad_Cruzada': 0.40, 'Diferenciacion_Intangible': 0.20}

    atributos = mercado['Entidad'].apply(asignar_atributos_estrategicos).apply(pd.Series)
    mercado = pd.concat([mercado, atributos], axis=1)

    # 3. Simulador Econométrico de Respuesta de Demanda (MNL)
    # Ante un shock simulado de incremento de +1.5% en la Cuota de Manejo / Tasa propia
    delta_precio_propio = 0.015
    
    # La sensibilidad de pérdida de clientes depende de la Inelasticidad Cruzada lograda por la entidad
    mercado['Sensibilidad_Precio'] = (1.0 - mercado['Inelasticidad_Cruzada']) * 2.5
    mercado['Factor_Impacto_Demanda'] = np.exp(-mercado['Sensibilidad_Precio'] * delta_precio_propio)
    
    # Proyección de la nueva cuota de mercado post-shock
    cuota_ajustada = mercado['Cuota_Mercado_Actual'] * mercado['Factor_Impacto_Demanda']
    mercado['Cuota_Mercado_Proyectada'] = cuota_ajustada / cuota_ajustada.sum()
    mercado['Variacion_Absoluta_Cuota'] = (mercado['Cuota_Mercado_Proyectada'] - mercado['Cuota_Mercado_Actual']) * 100

    print("\n====================================================================================================")
    print("      EVALUACIÓN ECONOMÉTRICA DE DIFERENCIACIÓN Y RETENCIÓN DE DEMANDA (GEMELO DIGITAL)            ")
    print("====================================================================================================")
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    mercado_print = mercado[['Entidad', 'Tipo', 'Inelasticidad_Cruzada', 'Diferenciacion_Intangible', 'Cuota_Mercado_Actual', 'Cuota_Mercado_Proyectada', 'Variacion_Absoluta_Cuota']].copy()
    mercado_print['Cuota_Mercado_Actual'] = mercado_print['Cuota_Mercado_Actual'].apply(lambda x: f"{x*100:.2f}%")
    mercado_print['Cuota_Mercado_Proyectada'] = mercado_print['Cuota_Mercado_Proyectada'].apply(lambda x: f"{x*100:.2f}%")
    mercado_print['Variacion_Absoluta_Cuota'] = mercado_print['Variacion_Absoluta_Cuota'].apply(lambda x: f"{x:+.3f}%")
    
    print(mercado_print.head(12))

    out_dir = r"F:\Santiago_IA\Gemelo_Digital_TC\outputs"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "modelo_diferenciacion_econometrico.csv")
    mercado.to_csv(out_file, index=False, encoding='utf-8-sig')
    print(f"\n[3/3] [OK] Resultados del Modelo Econométrico exportados a:\n -> {out_file}")

if __name__ == "__main__":
    estimar_modelo_diferenciacion_demanda()