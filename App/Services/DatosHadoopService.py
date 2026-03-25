from hdfs import InsecureClient
import pandas as pd
import io

class DatosHadoopService:
    # Asegúrate de tener tus credenciales de Hadoop aquí
    HDFS_URL = "http://localhost:9870" 
    HDFS_USER = "hadoop"
    HDFS_BASE_PATH = "/"

    @staticmethod
    def _leer_y_combinar_csv(hash_carpeta: str, prefijo: str):
        """
        Función interna (helper) que busca, lee y unifica TODOS los archivos CSV 
        de Hadoop que comiencen con el prefijo indicado (ej. 'tokenizacion_').
        """
        try:
            client = InsecureClient(DatosHadoopService.HDFS_URL, user=DatosHadoopService.HDFS_USER)
            ruta_directorio = f"{DatosHadoopService.HDFS_BASE_PATH.rstrip('/')}/{hash_carpeta}"
            archivos = client.list(ruta_directorio)
        except Exception as e:
            print(f"Error al conectar con Hadoop o listar archivos: {e}")
            return pd.DataFrame() # Retorna tabla vacía en caso de error

        # Filtrar solo los archivos que nos interesan
        archivos_objetivo = [f for f in archivos if f.startswith(prefijo)]
        
        if not archivos_objetivo:
            return pd.DataFrame()
            
        df_list = []
        for archivo in archivos_objetivo:
            ruta_archivo = f"{ruta_directorio}/{archivo}"
            with client.read(ruta_archivo) as reader:
                contenido_csv = reader.read().decode('utf-8')
                df = pd.read_csv(io.StringIO(contenido_csv))
                df_list.append(df)
                
        # Unir todos los documentos en un solo DataFrame
        df_master = pd.concat(df_list, ignore_index=True)
        return df_master

    # =========================================================
    # 1. FUNCIÓN PARA OBTENER TODOS LOS TOKENS UNIFICADOS
    # =========================================================
    @staticmethod
    def obtener_todos_los_tokens(hash_carpeta: str):
        df_tokens = DatosHadoopService._leer_y_combinar_csv(hash_carpeta, 'tokenizacion_')
        
        if df_tokens.empty:
            return {"status": "error", "message": "No hay archivos de tokenización."}
        
        # Agrupar las palabras iguales de todos los archivos y sumar su frecuencia
        df_agrupado = df_tokens.groupby(['palabra', 'longitud', 'tipo'])['frecuencia'].sum().reset_index()
        # Ordenar de mayor a menor frecuencia
        df_agrupado = df_agrupado.sort_values(by='frecuencia', ascending=False)
        
        return {
            "status": "success", 
            "data": df_agrupado.to_dict(orient='records')
        }

    # =========================================================
    # 2. FUNCIÓN PARA OBTENER TODOS LOS LEMAS UNIFICADOS
    # =========================================================
    @staticmethod
    def obtener_todos_los_lemas(hash_carpeta: str, return_df=False):
        df_lemas = DatosHadoopService._leer_y_combinar_csv(hash_carpeta, 'lematizacion_')
        
        if df_lemas.empty:
            if return_df: return pd.DataFrame()
            return {"status": "error", "message": "No hay archivos de lematización."}
        
        # Agrupar lemas y sumar sus frecuencias históricas
        columnas_agrupacion = ['palabra', 'longitud', 'tipo', 'lema', 'categoria', 'es_stopword']
        df_agrupado = df_lemas.groupby(columnas_agrupacion)['frecuencia'].sum().reset_index()
        df_agrupado = df_agrupado.sort_values(by='frecuencia', ascending=False)
        
        # Si la llamamos desde la función de estadísticas, devolvemos el DataFrame para hacer cálculos
        if return_df:
            return df_agrupado
            
        return {
            "status": "success", 
            "data": df_agrupado.to_dict(orient='records')
        }

    # =========================================================
    # 3. FUNCIÓN PARA OBTENER ESTADÍSTICAS GLOBALES (GRÁFICAS)
    # =========================================================
    @staticmethod
    def obtener_datos_graficas(hash_carpeta: str):
        # Usamos la función de lemas para obtener toda la base de datos combinada
        df_master = DatosHadoopService.obtener_todos_los_lemas(hash_carpeta, return_df=True)
        
        if df_master.empty:
            return {"status": "error", "message": "Aún no hay datos procesados para este corpus."}
            
        # --- CÁLCULOS MATEMÁTICOS EXACTOS ---
        total_tokens = int(df_master['frecuencia'].sum())
        total_tipos = int(df_master['palabra'].nunique()) # nunique() cuenta palabras únicas reales
        total_lemas = int(df_master['lema'].nunique())
        
        longitud_promedio = 0
        if total_tokens > 0:
            longitud_promedio = round(float((df_master['longitud'] * df_master['frecuencia']).sum() / total_tokens), 2)
        
        # Agrupaciones para ECharts
        pos_grouped = df_master.groupby('categoria')['frecuencia'].sum().reset_index()
        
        verbos_df = df_master[df_master['categoria'] == 'verbo']
        if not verbos_df.empty:
            verbos_grouped = verbos_df.groupby('lema')['frecuencia'].sum().nlargest(10).reset_index()
        else:
            verbos_grouped = pd.DataFrame(columns=['lema', 'frecuencia'])
            
        morf_grouped = df_master.groupby('longitud')['frecuencia'].sum().reset_index().sort_values('longitud')
        
        datos_limpios = {
            "kpis": {
                "Total Tokens": total_tokens,
                "Total Tipos (Palabras unicas)": total_tipos,
                "Total Lemas Unicos": total_lemas,
                "Longitud Promedio de Palabra": longitud_promedio
            },
            "pos": {
                "labels": pos_grouped['categoria'].tolist(),
                "values": pos_grouped['frecuencia'].astype(int).tolist()
            },
            "top_verbos": {
                "labels": verbos_grouped['lema'].tolist(),
                "values": verbos_grouped['frecuencia'].astype(int).tolist()
            },
            "morfologia": {
                "labels": morf_grouped['longitud'].astype(str).tolist(),
                "values": morf_grouped['frecuencia'].astype(int).tolist()
            }
        }
        
        return {
            "status": "success", 
            "data": datos_limpios
        }
    
    # =========================================================
    # 4. FUNCIÓN PARA OBTENER DATOS DE LA TABLA ESPECÍFICA
    # =========================================================
    @staticmethod
    def obtener_datos_tabla(hash_carpeta: str, limite: int = 1000):
        # Traemos toda la base combinada en formato DataFrame
        df_master = DatosHadoopService.obtener_todos_los_lemas(hash_carpeta, return_df=True)
        
        if df_master.empty:
            return {"status": "error", "message": "No hay datos disponibles para la tabla."}
            
        # 1. Extraer solo las columnas que necesitamos para la tabla
        # Asumimos que la columna 'tipo' tiene la información morfológica
        df_tabla = df_master[['palabra', 'lema', 'categoria', 'tipo', 'frecuencia']].copy()
        
        # 2. Ordenar por frecuencia (los más altos primero) y aplicar el límite
        df_tabla = df_tabla.sort_values(by='frecuencia', ascending=False).head(limite)
        
        # 3. Renombrar las columnas para que el JSON sea idéntico a lo que espera el JS
        df_tabla.rename(columns={
            'palabra': 'token',
            'categoria': 'pos',
            'tipo': 'morfologia'
        }, inplace=True)
        
        # 4. Limpiar posibles valores nulos (NaN a string vacío)
        df_tabla.fillna('', inplace=True)
        
        return {
            "status": "success", 
            "data": df_tabla.to_dict(orient='records')
        }
    
    # =========================================================
    # 5. FUNCIÓN PARA LA NUBE DE PALABRAS
    # =========================================================
    @staticmethod
    def obtener_datos_nube(hash_carpeta: str, limite: int = 150):
        # Traemos la base de lemas
        df_master = DatosHadoopService.obtener_todos_los_lemas(hash_carpeta, return_df=True)
        
        if df_master.empty:
            return {"status": "error", "message": "No hay datos para la nube de palabras."}
            
        # Agrupamos por lema y sumamos frecuencias
        df_agrupado = df_master.groupby('lema')['frecuencia'].sum().reset_index()
        # Tomamos el top N
        df_agrupado = df_agrupado.sort_values(by='frecuencia', ascending=False).head(limite)
        
        # Renombramos para que ECharts lo entienda mágicamente (name y value)
        df_agrupado.rename(columns={'lema': 'name', 'frecuencia': 'value'}, inplace=True)
        
        return {
            "status": "success", 
            "data": df_agrupado.to_dict(orient='records')
        }