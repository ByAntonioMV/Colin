import pandas as pd
import os
import time

def ejecutar_estadisticas(archivo_tokens: str, archivo_lemas: str, directorio_salida: str = "/tmp") -> str:
    """
    Función principal para ser llamada desde CorpusService.py en el pipeline.
    Recibe los CSVs de tokenización y lematización, y retorna la ruta del CSV de estadísticas.
    """
    print(f"\n--- INICIANDO GENERACIÓN DE ESTADÍSTICAS EN PIPELINE ---")
    
    # Asegurar que el directorio de salida existe
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Generar nombre dinámico con timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    archivo_salida = os.path.join(directorio_salida, f"estadisticas_{timestamp}.csv")
    
    print("Cargando archivos para estadísticas...")
    # Cargar los datos
    df_tokens = pd.read_csv(archivo_tokens)
    df_lemas = pd.read_csv(archivo_lemas)
    
    # --- 1. CÁLCULOS GENERALES ---
    total_tokens = int(df_tokens['frecuencia'].sum())
    total_lemas_unicos = int(df_lemas['lema'].nunique())
    total_tipos_unicos = int(df_tokens['palabra'].nunique())
    
    ttr_palabras = total_tipos_unicos / total_tokens if total_tokens > 0 else 0
    ttr_lemas = total_lemas_unicos / total_tokens if total_tokens > 0 else 0
    
    # --- 2. FRECUENCIAS ESPECÍFICAS ---
    top_10_lemas = df_lemas.groupby('lema')['frecuencia'].sum().nlargest(10).reset_index()
    
    verbos = df_lemas[df_lemas['categoria'] == 'verbo']
    if not verbos.empty:
        top_10_verbos = verbos.groupby('lema')['frecuencia'].sum().nlargest(10).reset_index()
    else:
        top_10_verbos = pd.DataFrame(columns=['lema', 'frecuencia'])
    
    distribucion_pos = df_lemas.groupby('categoria')['frecuencia'].sum().sort_values(ascending=False).reset_index()
    
    # --- 3. SEGMENTACIÓN MORFOLÓGICA ---
    distribucion_longitud = df_tokens.groupby('longitud')['frecuencia'].sum().reset_index()
    longitud_promedio = (df_tokens['longitud'] * df_tokens['frecuencia']).sum() / total_tokens if total_tokens > 0 else 0
    
    # --- 4. EXPORTAR TODO A UN ÚNICO CSV ---
    print(f"Generando el archivo de salida: {archivo_salida}...")
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("=== ESTADISTICAS GENERALES ===\n")
        f.write("Metrica,Valor\n")
        f.write(f"Total Tokens,{total_tokens}\n")
        f.write(f"Total Tipos (Palabras unicas),{total_tipos_unicos}\n")
        f.write(f"Total Lemas Unicos,{total_lemas_unicos}\n")
        f.write(f"TTR (Palabras/Tokens),{ttr_palabras:.6f}\n")
        f.write(f"TTR (Lemas/Tokens),{ttr_lemas:.6f}\n")
        f.write(f"Longitud Promedio de Palabra,{longitud_promedio:.2f}\n")
        f.write("\n")
        
        f.write("=== TOP 10 LEMAS MAS FRECUENTES ===\n")
        f.write("Lema,Frecuencia\n")
        for _, row in top_10_lemas.iterrows():
            f.write(f"{row['lema']},{int(row['frecuencia'])}\n")
        f.write("\n")
        
        f.write("=== TOP 10 VERBOS MAS FRECUENTES ===\n")
        f.write("Verbo (Lema),Frecuencia\n")
        for _, row in top_10_verbos.iterrows():
            f.write(f"{row['lema']},{int(row['frecuencia'])}\n")
        f.write("\n")
        
        f.write("=== FRECUENCIAS POR CATEGORIA GRAMATICAL (POS) ===\n")
        f.write("Categoria,Frecuencia\n")
        for _, row in distribucion_pos.iterrows():
            f.write(f"{row['categoria']},{int(row['frecuencia'])}\n")
        f.write("\n")
        
        f.write("=== APROXIMACION MORFOLOGICA (Tokens por Longitud) ===\n")
        f.write("Longitud_de_Palabra,Cantidad_de_Tokens\n")
        for _, row in distribucion_longitud.iterrows():
            f.write(f"{int(row['longitud'])},{int(row['frecuencia'])}\n")

    print(f"✅ Estadísticas completadas. Archivo generado: {archivo_salida}")
    return archivo_salida

# Mantengo tu bloque original por si quieres hacer pruebas locales
if __name__ == "__main__":
    archivo_tokenizacion = 'tokenizacion_20260312_115554.csv'
    archivo_lematizacion = 'lemas_nahuatl.csv'
    archivo_resultado = 'estadistica.csv'
    
    if os.path.exists(archivo_tokenizacion) and os.path.exists(archivo_lematizacion):
        ejecutar_estadisticas(archivo_tokenizacion, archivo_lematizacion, ".")
    else:
        print("Error: No se encontraron los archivos de entrada locales.")