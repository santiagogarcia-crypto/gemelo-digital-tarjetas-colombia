# ==============================================================================
# GEMELO DIGITAL FINANCIERO: MODELO DE PERFILAMIENTO COMPORTAMENTAL (DEFINITIVO)
# Ruta local: F:\Santiago_IA\Gemelo_Digital_TC\perfilamiento_clientes.py
# ==============================================================================

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def perfilar_comportamiento_clientes():
    data_path = r"F:\Santiago_IA\Gemelo_Digital_TC\data\base_datos_caso_gemelo_digital.csv"
    
    if not os.path.exists(data_path):
        print(f"Error: No se encontró la base de datos en {data_path}")
        return
        
    print("[1/3] Cargando y procesando la base de datos...")
    df = pd.read_csv(data_path)
    
    # Identificación dinámica de columnas de forma tolerante
    col_entidad = next((c for c in ['nombreentidad', 'nombre_entidad', 'entidad'] if c in df.columns), None)
    col_tarjetas = next((c for c in ['total_tarjetas_credito', 'total_tarjetas', 'tarjetas_activas', 'numero_tarjetas'] if c in df.columns), None)
    col_saldo = next((c for c in ['valor_saldos', 'saldo_total', 'monto_transacciones', 'volumen_transacciones'] if c in df.columns), None)
    
    if not col_entidad:
        print("Error: No se encontró la columna de entidad en la base de datos.")
        return

    # Construcción limpia del DataFrame de perfiles
    if col_tarjetas and col_saldo:
        perfiles = df.groupby(col_entidad).agg({
            col_tarjetas: 'mean',
            col_saldo: 'sum'
        }).reset_index()
        perfiles.columns = ['Entidad', 'Promedio_Plásticos', 'Monto_Total_COP']
    elif col_tarjetas:
        perfiles = df.groupby(col_entidad)[col_tarjetas].mean().reset_index()
        perfiles.columns = ['Entidad', 'Promedio_Plásticos']
        perfiles['Monto_Total_COP'] = perfiles['Promedio_Plásticos'] * 650000
    else:
        perfiles = df.groupby(col_entidad).size().reset_index(name='Promedio_Plásticos')
        perfiles['Monto_Total_COP'] = perfiles['Promedio_Plásticos'] * 650000

    # Ticket promedio estimado por tarjeta ($COP)
    perfiles['Ticket_Promedio_COP'] = perfiles['Monto_Total_COP'] / np.maximum(perfiles['Promedio_Plásticos'], 1)
    
    # Estandarización y Clustering Comportamental (K-Means)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(perfiles[['Promedio_Plásticos', 'Ticket_Promedio_COP']])
    
    n_clusters = min(4, len(perfiles))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    perfiles['Cluster'] = kmeans.fit_predict(X_scaled)
    
    mapa_perfiles = {
        0: 'Perfil 1: Inercial / Masivo',
        1: 'Perfil 2: Transaccional Frecuente',
        2: 'Perfil 3: Financiado Alto Volatilidad',
        3: 'Perfil 4: Líder de Red / Escala'
    }
    perfiles['Nombre_Perfil'] = perfiles['Cluster'].map(mapa_perfiles)
    
    # Formateo de visualización en consola
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    perfiles_print = perfiles.copy()
    perfiles_print['Promedio_Plásticos'] = perfiles_print['Promedio_Plásticos'].apply(lambda x: f"{x:,.0f}")
    perfiles_print['Ticket_Promedio_COP'] = perfiles_print['Ticket_Promedio_COP'].apply(lambda x: f"${x:,.0f} COP")
    
    print("\n===================================================================================")
    print("        RESULTADOS DEL MODELO COMPORTAMENTAL (GEMELO DIGITAL FINANCIERO)           ")
    print("===================================================================================")
    print(perfiles_print[['Entidad', 'Nombre_Perfil', 'Promedio_Plásticos', 'Ticket_Promedio_COP']].head(12))
    
    # Exportar archivo CSV
    out_dir = r"F:\Santiago_IA\Gemelo_Digital_TC\outputs"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "perfiles_clientes_gemelo.csv")
    perfiles.to_csv(out_file, index=False, encoding='utf-8-sig')
    print(f"\n[3/3] [OK] Resultados guardados exitosamente en:\n -> {out_file}")

if __name__ == "__main__":
    perfilar_comportamiento_clientes()