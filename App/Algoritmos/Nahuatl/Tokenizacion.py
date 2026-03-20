import pandas as pd
from nltk.tokenize import word_tokenize
import re
from collections import Counter, defaultdict
import os
import glob
from langdetect import detect, DetectorFactory
# Para resultados consistentes en detección de idioma
DetectorFactory.seed = 0

class IndigenousLanguageTokenizer:
    """
    Tokenizador universal para lenguas indígenas
    Detecta automáticamente características lingüísticas
    """
    
    # Caracteres especiales por familia lingüística
    LANGUAGE_PATTERNS = {
        'nahuatl': {
            'chars': r'[a-zāēīōūáéíóúñ]',
            'digraphs': ['tl', 'tz', 'ch', 'kw'],
            'common_1letter': {'a', 'o', 'i', 'y', 'u', 'e'},
            'common_2letter': {'in', 'ic', 'ca', 'mo', 'no', 'ti', 'ni', 'le'}
        },
        'maya': {
            'chars': r'[a-záéíóúäëïöüñ]',
            'digraphs': ['tz', 'ch', 'pp', 'th', 'kh'],
            'common_1letter': {'a', 'u', 'i'},
            'common_2letter': {'le', 'ka', 'ti', 'na'}
        },
        'mixteco': {
            'chars': r'[a-záéíóúãẽĩõũñ]',
            'digraphs': ['nd', 'nt', 'ch', 'ng'],
            'common_1letter': {'a', 'i', 'u'},
            'common_2letter': {'sa', 'nu', 'ta'}
        },
        'zapoteco': {
            'chars': r'[a-záéíóúñ]',
            'digraphs': ['dx', 'xh', 'ch', 'll'],
            'common_1letter': {'a', 'e', 'i', 'o', 'u'},
            'common_2letter': {'la', 'ne', 'ca'}
        },
        'quechua': {
            'chars': r'[a-záéíóúñčĉšž]',
            'digraphs': ['ch', 'sh', 'll', 'qu'],
            'common_1letter': {'a', 'i', 'u'},
            'common_2letter': {'ka', 'pi', 'ta', 'man'}
        },
        'guarani': {
            'chars': r'[a-záéíóúãẽĩõũñÿ]',
            'digraphs': ['ch', 'mb', 'nd', 'ng', 'nt', 'rr'],
            'common_1letter': {'a', 'e', 'i', 'o', 'u'},
            'common_2letter': {'pe', 'ha', 're', 'ta'}
        }
    }
    
    def __init__(self, language=None, auto_detect=True):
        """
        Inicializa tokenizador para lenguas indígenas
        
        Args:
            language: Código del idioma ('nahuatl', 'maya', 'mixteco', etc.)
            auto_detect: Detectar automáticamente del texto
        """
        self.language = language
        self.auto_detect = auto_detect
        self.detected_language = None
        
        # Patrones por defecto (universales)
        self.valid_chars = re.compile(r'[a-záéíóúãẽĩõũñäëïöüÿčĉšž]', re.IGNORECASE)
        self.punctuation = re.compile(r'[.,;:"!?()\[\]{}«»¡¿…—\-]')
        
        # CORRECCIÓN: Usar Counter en lugar de defaultdict para word_stats
        self.word_stats = Counter()  # ¡Cambiado!
        self.char_frequency = Counter()
        
        # Para aprendizaje de palabras cortas
        self.short_words = set()
        self.digraphs = []
        
    def detect_language(self, text_sample):
        """
        Detecta el idioma basado en muestra de texto
        """
        if not text_sample or len(text_sample) < 50:
            return None
            
        try:
            # Detectar idioma (usa langdetect)
            lang_code = detect(text_sample[:500])
            
            # Mapeo de códigos ISO a lenguas indígenas
            lang_mapping = {
                'nah': 'nahuatl',
                'yua': 'maya',
                'qu': 'quechua',
                'gn': 'guarani'
            }
            
            return lang_mapping.get(lang_code, None)
            
        except:
            # Si falla la detección, intentar por patrón de caracteres
            return self.detect_by_patterns(text_sample)
    
    def detect_by_patterns(self, text):
        """
        Detecta idioma por patrones de caracteres
        """
        text_lower = text.lower()
        
        scores = {}
        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            score = 0
            # Verificar caracteres especiales
            special_chars = re.findall(patterns['chars'], text_lower)
            score += len(special_chars) * 2
            
            # Verificar dígrafos comunes
            for digraph in patterns['digraphs']:
                if digraph in text_lower:
                    score += 5
                    self.digraphs.append(digraph)
            
            scores[lang] = score
        
        if scores and max(scores.values()) > 10:
            return max(scores, key=scores.get)
        return None
    
    def learn_from_text(self, text):
        """
        Aprende características del texto para mejorar tokenización
        """
        words = text.lower().split()
        
        for word in words:
            clean_word = re.sub(self.punctuation, '', word)
            if clean_word:
                self.word_stats[clean_word] += 1  # Counter funciona perfecto
                
                # Aprender palabras cortas comunes
                if 1 <= len(clean_word) <= 2:
                    self.short_words.add(clean_word)
                
                # Frecuencia de caracteres
                self.char_frequency.update(clean_word)
    
    def get_language_profile(self):
        """
        Genera perfil lingüístico basado en el texto procesado
        """
        # Identificar caracteres especiales frecuentes
        special_chars = []
        for char, freq in self.char_frequency.most_common():
            if not char.isascii() or char in 'áéíóúãẽĩõũñäëïöü':
                special_chars.append(f"{char} ({freq})")
        
        # Identificar dígrafos comunes - CORREGIDO
        # Obtener palabras más comunes como lista
        top_words = [word for word, count in self.word_stats.most_common(100)]
        text = ' '.join(top_words)
        
        found_digraphs = []
        common_digraphs = ['tl', 'tz', 'ch', 'sh', 'll', 'qu', 'mb', 'nd', 'nt', 'rr']
        for digraph in common_digraphs:
            if digraph in text:
                found_digraphs.append(digraph)
        
        return {
            'caracteres_especiales': special_chars[:10],
            'digrafos_detectados': found_digraphs,
            'palabras_cortas_comunes': list(self.short_words)[:20],
            'total_palabras_aprendidas': len(self.word_stats)
        }
    
    def tokenize(self, text, learning_mode=True):
        """
        Tokeniza texto de cualquier lengua indígena
        
        Args:
            text: Texto a tokenizar
            learning_mode: Si debe aprender del texto
        """
        if not isinstance(text, str):
            return []
        
        # Modo aprendizaje
        if learning_mode:
            self.learn_from_text(text)
        
        # Limpiar texto
        text = text.lower()
        
        # Preservar guiones para palabras compuestas
        text = re.sub(r'[.,;:"!?()\[\]{}«»¡¿…—]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Tokenizar con NLTK
        tokens = word_tokenize(text.strip())
        
        valid_tokens = []
        for token in tokens:
            token = token.strip()
            
            # Palabras con guiones (compuestas)
            if '-' in token:
                parts = token.split('-')
                if all(p.isalpha() and len(p) >= 1 for p in parts):
                    valid_tokens.append(token)
                continue
            
            # Palabras normales
            if token.isalpha():
                # Mantener TODAS las palabras de 1-2 letras
                if len(token) <= 2:
                    valid_tokens.append(token)
                else:
                    # Palabras largas: verificar caracteres válidos
                    if all(self.valid_chars.match(c) or not c.isascii() 
                          for c in token):
                        valid_tokens.append(token)
        
        return valid_tokens
    
    def get_multilingual_stats(self, tokens):
        """
        Estadísticas multilingüe
        """
        unique_tokens = set(tokens)
        return {
            'total': len(tokens),
            'unique': len(unique_tokens),
            'short_words_1_2': len([t for t in unique_tokens if len(t) <= 2]),
            'long_words': len([t for t in unique_tokens if len(t) > 8]),
            'compounds': len([t for t in unique_tokens if '-' in t]),
            'avg_length': sum(len(t) for t in tokens) / len(tokens) if tokens else 0
        }


def load_multiple_files(file_input):
    """
    Carga múltiples archivos CSV/TSV
    
    Args:
        file_input: Puede ser:
                   - String con patrón (ej: "*.csv")
                   - Lista de nombres de archivo (ej: ["a.csv", "b.csv"])
    
    Returns:
        DataFrame combinado con todos los textos
    """
    archivos = []
    
    # Determinar si es patrón o lista
    if isinstance(file_input, str):
        # Es un patrón (ej: "*.csv")
        archivos = glob.glob(file_input)
    elif isinstance(file_input, list):
        # Es una lista de archivos
        archivos = file_input
    else:
        print(f"❌ Tipo de entrada no válido: {type(file_input)}")
        return None
    
    if not archivos:
        print(f"❌ No se encontraron archivos: {file_input}")
        return None
    
    print(f"📁 Archivos encontrados: {len(archivos)}")
    for archivo in archivos:
        print(f"   • {archivo}")
    
    # Lista para almacenar todos los DataFrames
    dataframes = []
    total_lineas = 0
    archivos_cargados = 0
    
    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"\n⚠️  Archivo no encontrado: {archivo}")
            continue
            
        print(f"\n📂 Cargando {archivo}...")
        try:
            # Intentar como CSV normal primero
            df = pd.read_csv(archivo, encoding='utf-8')
            if len(df.columns) > 1:
                # Si hay múltiples columnas, tomar la primera
                df = df.iloc[:, [0]].copy()
            df.columns = ['text']
            print(f"   ✅ Cargado como CSV: {len(df)} líneas")
            dataframes.append(df)
            total_lineas += len(df)
            archivos_cargados += 1
            
        except Exception as e:
            try:
                # Intentar como TSV si falla el CSV normal
                df = pd.read_csv(archivo, sep='\t', encoding='utf-8', 
                                 header=None, names=['text'])
                print(f"   ✅ Cargado como TSV: {len(df)} líneas")
                dataframes.append(df)
                total_lineas += len(df)
                archivos_cargados += 1
                
            except Exception as e2:
                print(f"   ❌ Error cargando {archivo}: CSV ({e}) / TSV ({e2})")
                continue
    
    if not dataframes:
        print("❌ No se pudo cargar ningún archivo")
        return None
    
    # Combinar todos los DataFrames
    df_combinado = pd.concat(dataframes, ignore_index=True)
    print(f"\n📊 TOTAL: {len(df_combinado)} líneas combinadas de {archivos_cargados} archivos")
    
    return df_combinado

# ==============================================================================
# NUEVA FUNCIÓN PARA EL PIPELINE (ENTRYPOINT)
# ==============================================================================
def ejecutar_tokenizacion(archivo_entrada, directorio_salida="/tmp"):
    """
    Función principal para ser llamada desde CorpusService.py en el pipeline.
    
    Args:
        archivo_entrada (str o list): Ruta del archivo a procesar o lista de rutas.
        directorio_salida (str): Directorio donde se guardará el CSV resultante.
        
    Returns:
        str: Ruta completa del archivo CSV generado.
    """
    from datetime import datetime
    import os
    
    print(f"\n--- INICIANDO TOKENIZACIÓN EN PIPELINE ---")
    
    # Asegurar que el directorio de salida existe
    os.makedirs(directorio_salida, exist_ok=True)
    
    # 1. Cargar los datos usando la función existente
    # Si recibe un string, lo convertimos a lista para mantener la compatibilidad
    file_input = [archivo_entrada] if isinstance(archivo_entrada, str) else archivo_entrada
    df = load_multiple_files(file_input)
    
    if df is None or len(df) == 0:
        raise ValueError(f"No se pudieron cargar datos desde: {archivo_entrada}")
        
    # 2. Inicializar tokenizador
    tokenizer = IndigenousLanguageTokenizer(auto_detect=True)
    
    # 3. Detectar idioma
    print("🔍 Detectando idioma...")
    sample = ' '.join(df['text'].head(100).astype(str).tolist())
    detected_lang = tokenizer.detect_language(sample)
    
    if detected_lang and detected_lang in tokenizer.LANGUAGE_PATTERNS:
        pattern = tokenizer.LANGUAGE_PATTERNS[detected_lang]
        tokenizer.valid_chars = re.compile(pattern['chars'], re.IGNORECASE)
    
    # 4. Tokenizar
    print("🔄 Tokenizando...")
    all_tokens = []
    
    for text in df['text']:
        if pd.notna(text):
            tokens = tokenizer.tokenize(str(text), learning_mode=True)
            all_tokens.extend(tokens)
            
    if not all_tokens:
        raise ValueError("No se encontraron tokens válidos en el documento")
        
    # 5. Analizar y preparar resultados
    word_counts = Counter(all_tokens)
    
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"tokenizacion_{fecha}.csv"
    output_path = os.path.join(directorio_salida, output_filename)
    
    resultados = []
    for palabra, freq in word_counts.most_common():
        resultados.append({
            'palabra': palabra,
            'frecuencia': freq,
            'longitud': len(palabra),
            'tipo': 'corta' if len(palabra) <= 2 else 'compuesta' if '-' in palabra else 'normal'
        })
    
    # 6. Guardar CSV
    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ Tokenización completada. Archivo generado: {output_path}")
    
    return output_path

# ==============================================================================

def main():
    # CONFIGURACIÓN - Elige UNA de estas opciones:
    
    # Opción 1: Patrón para múltiples archivos (todos los CSV)
    # FILE_INPUT = "*.csv"
    
    # Opción 2: Patrón específico (todos los que empiezan con nhy)
    # FILE_INPUT = "nhy*.csv"
    
    # Opción 3: Lista específica de archivos
    FILE_INPUT = [
        "nhy01.csv",
        "nhy02.csv"
    ]
    
    print("🌎 TOKENIZADOR UNIVERSAL PARA LENGUAS INDÍGENAS - MÚLTIPLES ARCHIVOS")
    print("="*70)
    
    # Cargar múltiples archivos
    df = load_multiple_files(FILE_INPUT)
    
    if df is None or len(df) == 0:
        print("❌ No hay datos para procesar")
        return
    
    # Inicializar tokenizador
    tokenizer = IndigenousLanguageTokenizer(auto_detect=True)
    
    # Primera fase: Detección de idioma
    print("\n🔍 Detectando idioma...")
    sample = ' '.join(df['text'].head(100).astype(str).tolist())
    detected_lang = tokenizer.detect_language(sample)
    
    if detected_lang:
        print(f"✅ Idioma detectado: {detected_lang.upper()}")
        if detected_lang in tokenizer.LANGUAGE_PATTERNS:
            pattern = tokenizer.LANGUAGE_PATTERNS[detected_lang]
            tokenizer.valid_chars = re.compile(pattern['chars'], re.IGNORECASE)
    else:
        print("ℹ️ Usando modo universal (detección automática de patrones)")
    
    # Segunda fase: Tokenización con aprendizaje
    print("\n🔄 Tokenizando y aprendiendo...")
    all_tokens = []
    
    total_filas = len(df)
    for i, text in enumerate(df['text']):
        if pd.notna(text):
            tokens = tokenizer.tokenize(str(text), learning_mode=True)
            all_tokens.extend(tokens)
        
        # Mostrar progreso
        if (i + 1) % 100 == 0 or (i + 1) % max(1, total_filas // 10) == 0:
            pct = (i + 1) / total_filas * 100
            print(f"   Procesados {i+1}/{total_filas} ({pct:.1f}%) - Tokens: {len(all_tokens):,}")
    
    if not all_tokens:
        print("❌ No se encontraron tokens válidos")
        return
    
    # Tercera fase: Análisis
    word_counts = Counter(all_tokens)
    stats = tokenizer.get_multilingual_stats(all_tokens)
    language_profile = tokenizer.get_language_profile()
    
    # Resultados
    print("\n" + "="*70)
    print("📊 ANÁLISIS MULTILINGÜE DE LENGUA INDÍGENA - MÚLTIPLES ARCHIVOS")
    print("="*70)
    
    # Calcular número de archivos procesados
    if isinstance(FILE_INPUT, list):
        num_archivos = len([f for f in FILE_INPUT if os.path.exists(f)])
    else:
        num_archivos = len(glob.glob(FILE_INPUT))
    
    print(f"📁 Archivos procesados:     {num_archivos}")
    print(f"📄 Documentos totales:      {len(df):,}")
    print(f"📝 Total tokens:            {stats['total']:,}")
    print(f"📚 Vocabulario único:       {stats['unique']:,}")
    print(f"📊 Diversidad léxica:       {(stats['unique']/stats['total'])*100:.2f}%")
    print(f"📏 Longitud promedio:       {stats['avg_length']:.2f} caracteres")
    print(f"🔤 Palabras 1-2 letras:     {stats['short_words_1_2']:,}")
    print(f"📐 Palabras >8 letras:      {stats['long_words']:,}")
    print(f"➖ Palabras compuestas:     {stats['compounds']:,}")
    print("="*70)
    
    # Perfil lingüístico
    print("\n🔬 PERFIL LINGÜÍSTICO DETECTADO:")
    print("-" * 50)
    if language_profile['caracteres_especiales']:
        print("Caracteres especiales:")
        for c in language_profile['caracteres_especiales'][:5]:
            print(f"   • {c}")
    else:
        print("   • Sin caracteres especiales detectados")
    
    if language_profile['digrafos_detectados']:
        print("\nDígrafos detectados:")
        for d in language_profile['digrafos_detectados'][:5]:
            print(f"   • {d}")
    else:
        print("\n• Sin dígrafos especiales detectados")
    
    if language_profile['palabras_cortas_comunes']:
        print("\nPalabras cortas comunes:")
        palabras_cortas = sorted(language_profile['palabras_cortas_comunes'])[:10]
        print(f"   • {', '.join(palabras_cortas)}")
    
    # Top palabras
    print("\n📈 TOP 20 PALABRAS MÁS FRECUENTES:")
    print("-" * 50)
    for palabra, freq in word_counts.most_common(20):
        tipo = "🔹" if len(palabra) <= 2 else "➖" if '-' in palabra else "📄"
        print(f"   {tipo} {palabra:<20} {freq:>8,}")
    
    # Guardar resultados
    from datetime import datetime
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"tokenizacion_{fecha}.csv"
    
    resultados = []
    for palabra, freq in word_counts.most_common():
        resultados.append({
            'palabra': palabra,
            'frecuencia': freq,
            'longitud': len(palabra),
            'tipo': 'corta' if len(palabra) <= 2 else 'compuesta' if '-' in palabra else 'normal'
        })
    
    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 Resultados guardados en: {output_file}")
    
    # Resumen ejecutivo
    print("\n" + "="*70)
    print("📋 RESUMEN EJECUTIVO MULTILINGÜE - MÚLTIPLES ARCHIVOS")
    print("="*70)
    print(f"✅ Análisis completado para {detected_lang.upper() if detected_lang else 'lengua indígena'}")
    print(f"📁 Archivos procesados: {num_archivos}")
    print(f"📄 Documentos totales: {len(df):,}")
    print(f"📊 Vocabulario total: {stats['unique']:,} palabras únicas")
    print(f"🎯 Diversidad léxica global: {(stats['unique']/stats['total'])*100:.1f}%")
    print(f"\n💡 Características lingüísticas detectadas:")
    print(f"   • {stats['short_words_1_2']:,} partículas de 1-2 letras")
    print(f"   • {stats['long_words']:,} palabras largas (>8 letras)")
    print(f"   • {stats['compounds']:,} palabras compuestas")
    print("="*70)


if __name__ == "__main__":
    main()