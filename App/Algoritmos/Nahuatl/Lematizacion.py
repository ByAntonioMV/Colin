import csv
import sys
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────────────
# 1.  STOPWORDS DEL NÁHUATL
#     (partículas, pronombres, conjunciones,
#      preposiciones, adverbios no-lematizables)
# ──────────────────────────────────────────────
STOPWORDS_NAHUATL: set[str] = {
    # pronombres personales
    "nej", "tejwan", "yej", "yejwan", "namejwan", "amejwan",
    "nejwa", "tejwa", "yejwa", "tejwatzin",
    # pronombres / deícticos
    "in", "inin", "inon", "on", "ne",
    # conjunciones / conectores
    "wan", "iwan", "inwan", "noijki", "noso", "sino", "pero", "para",
    "porke", "ke", "komo", "maski", "asta", "desde", "entre", "mientras",
    "ya", "ok", "sa", "tla", "ma", "nian", "yon", "yen",
    # partículas aspectuales / modales
    "ax", "amo", "ayamo", "ayakmo", "nel", "wel", "weli",
    "moneki", "kox", "nion", "semi", "mach",
    # adverbios de lugar / posposiciones
    "ompa", "nepa", "kan", "kanaj", "ipan", "itech",
    "ijtik", "ixko", "iyakapan", "inawak", "inmixpan",
    "wejka", "niman", "achtoj", "satepan", "axan", "keman",
    "tlan", "ika", "nik", "ken", "yin",
    # adverbios de tiempo
    "ijkón", "ijkuakón", "ijkuak", "tonses", "yonik", "nochipa",
    "kenik", "yekan",
    # cuantificadores / determinantes
    "nochi", "nochtin", "miek", "miekej", "oksé", "ome", "eyi", "nawi",
    "chikome", "oksekimej", "sekimej", "oksemi", "akin", "akinmej",
    "akaj", "amakaj", "cada", "kada",
    # preposiciones / posposiciones
    "por", "de", "se", "no",
    # abreviaturas de libros bíblicos (corpus específico)
    "lc", "mt", "mr", "jn", "ik", "ke",
    # partículas discursivas
    "tej", "kej", "ok",
    # préstamos del español que funcionan como partículas/nombres propios
    "hola", "gracias", "favor",
    # nombres propios frecuentes en el corpus (Biblia)
    "pablo", "moisés", "dios", "jesucristo", "señor", "toseñor",
    "santo", "espíritu", "herodes", "pilato", "galilea", "judea",
    "simón", "bernabé",
    # otros
    "yonmej", "yeskia", "yetos", "yeto", "onkaj", "omen",
    "oyáj", "opéj", "witz",
}

# ──────────────────────────────────────────────
# 2.  LEXICÓN BASE (raíces conocidas → lema)
#     Cubre las raíces más frecuentes del corpus
# ──────────────────────────────────────────────
LEXICON: dict[str, tuple[str, str]] = {
    # (raíz) : (lema, categoría)
    # VERBOS (raíz sin afijos)
    "tlakat":   ("tlakati",  "verbo"),
    "chij":     ("chiwa",    "verbo"),
    "chiw":     ("chiwa",    "verbo"),
    "chiwa":    ("chiwa",    "verbo"),
    "kijta":    ("kijta",    "verbo"),
    "ilwi":     ("ilwia",    "verbo"),
    "ilwia":    ("ilwia",    "verbo"),
    "ita":      ("itta",     "verbo"),
    "itta":     ("itta",     "verbo"),
    "tak":      ("itta",     "verbo"),   # o-ki-tak
    "kak":      ("kaki",     "verbo"),
    "mati":     ("mati",     "verbo"),
    "mat":      ("mati",     "verbo"),
    "nemi":     ("nemi",     "verbo"),
    "nek":      ("neki",     "verbo"),
    "neki":     ("neki",     "verbo"),
    "pia":      ("kipia",    "verbo"),
    "piaj":     ("kipia",    "verbo"),
    "pej":      ("pehua",    "verbo"),
    "pehu":     ("pehua",    "verbo"),
    "tlajlan":  ("tlajtlani","verbo"),
    "tlajtla":  ("tlajtlani","verbo"),
    "tlajtlani":("tlajtlani","verbo"),
    "tlajto":   ("tlajtoa",  "verbo"),
    "tlajtoa":  ("tlajtoa",  "verbo"),
    "tlami":    ("tlami",    "verbo"),
    "miki":     ("miki",     "verbo"),
    "mik":      ("miki",     "verbo"),
    "wal":      ("wallauh",  "verbo"),
    "wala":     ("wallauh",  "verbo"),
    "walaj":    ("wallauh",  "verbo"),
    "yaw":      ("yauh",     "verbo"),
    "yeka":     ("yeka",     "verbo"),
    "kichij":   ("kichiwa",  "verbo"),
    "kichiwa":  ("kichiwa",  "verbo"),
    "mochij":   ("mochiwa",  "verbo"),
    "mochiw":   ("mochiwa",  "verbo"),
    "mochiwa":  ("mochiwa",  "verbo"),
    "neltoka":  ("neltoka",  "verbo"),
    "nelto":    ("neltoka",  "verbo"),
    "tlaxtlawi":("tlaxtlawi","verbo"),
    "palewi":   ("palewia",  "verbo"),
    "palew":    ("palewia",  "verbo"),
    "palewia":  ("palewia",  "verbo"),
    "makixtia": ("makixtia", "verbo"),
    "makixtij": ("makixtia", "verbo"),
    "tekipano":  ("tekipanoa","verbo"),
    "tekipanoa": ("tekipanoa","verbo"),
    "tlachij":  ("tlachiwa", "verbo"),
    "tlachiwa": ("tlachiwa", "verbo"),
    "namaka":   ("tlanamaka","verbo"),
    "tlanamaka":("tlanamaka","verbo"),
    "pano":     ("panoa",    "verbo"),
    "panoa":    ("panoa",    "verbo"),
    "kalakin":  ("kalaki",   "verbo"),
    "kalak":    ("kalaki",   "verbo"),
    "kalaki":   ("kalaki",   "verbo"),
    "tlajtolpanol":("tlajtolpanoltia","verbo"),
    "toka":     ("toka",     "verbo"),   # itoka → llamarse
    "ilwij":    ("ilwia",    "verbo"),   # o-ki-lwijkej
    "ilwijkej": ("ilwia",    "verbo"),
    "nankilij": ("nankilia", "verbo"),
    "maka":     ("maka",     "verbo"),   # dar
    "makak":    ("maka",     "verbo"),
    "tlalij":   ("tlalia",   "verbo"),   # poner
    "tlalia":   ("tlalia",   "verbo"),
    "nelt":     ("neltoka",  "verbo"),
    "tlaneltoka":("neltoka", "verbo"),
    "yolkuik":  ("moyolkuia","verbo"),   # resucitar
    "moyolkuia":("moyolkuia","verbo"),
    "momachtij":("momachtia","verbo"),   # aprender
    "momachtia":("momachtia","verbo"),
    "tlamachtij":("tlamachtia","verbo"), # enseñar
    "tlamachtia":("tlamachtia","verbo"),
    "temaki":   ("temakixtia","verbo"),  # salvar
    "temakixtij":("temakixtia","verbo"),
    "temakixtia":("temakixtia","verbo"),
    "tlanawtia":("tlanawatia","verbo"),  # mandar/ordenar
    "tlanawatia":("tlanawatia","verbo"),
    "tlanawatij":("tlanawatia","verbo"),
    "kijtos":   ("kijtohua",  "verbo"),  # decir
    "kijtoa":   ("kijtohua",  "verbo"),
    "kijtohua":  ("kijtohua", "verbo"),
    "kijtoj":   ("kijtohua",  "verbo"),
    "ilwis":    ("ilwia",     "verbo"),
    "ilwia":    ("ilwia",     "verbo"),
    "namechilwi":("ilwia",    "verbo"),
    # SUSTANTIVOS
    "tlakatl":   ("tlakatl",  "sustantivo"),
    "tlaka":     ("tlakatl",  "sustantivo"),
    "tlakaj":    ("tlakatl",  "sustantivo"),
    "siwatl":    ("siwatl",   "sustantivo"),
    "siwa":      ("siwatl",   "sustantivo"),
    "siwame":    ("siwatl",   "sustantivo"),
    "siwamej":   ("siwatl",   "sustantivo"),
    "tokni":     ("tokniihtl","sustantivo"),
    "tokniwan":  ("tokniihtl","sustantivo"),
    "tekitl":    ("tekitl",   "sustantivo"),
    "teki":      ("tekitl",   "sustantivo"),
    "atl":       ("atl",      "sustantivo"),
    "tlal":      ("tlalli",   "sustantivo"),
    "tlale":     ("tlalli",   "sustantivo"),
    "tlalli":    ("tlalli",   "sustantivo"),
    "kali":      ("kalli",    "sustantivo"),
    "kalle":     ("kalli",    "sustantivo"),
    "kalli":     ("kalli",    "sustantivo"),
    "kale":      ("kalli",    "sustantivo"),
    "tonale":    ("tonalli",  "sustantivo"),
    "tonalli":   ("tonalli",  "sustantivo"),
    "tonal":     ("tonalli",  "sustantivo"),
    "yolo":      ("yollotl",  "sustantivo"),
    "yollotl":   ("yollotl",  "sustantivo"),
    "tepetl":    ("tepetl",   "sustantivo"),
    "tepe":      ("tepetl",   "sustantivo"),
    "ilwikak":   ("ilwikaktli","sustantivo"),
    "tlaltikpak":("tlaltikpaktli","sustantivo"),
    "tlaltikpa": ("tlaltikpaktli","sustantivo"),
    "tlajkuilol":("tlajkuilolli","sustantivo"),
    "nemilistle":("nemilistli","sustantivo"),
    "nemilis":   ("nemilistli","sustantivo"),
    "tlajtol":   ("tlajtoli",  "sustantivo"),
    "tlajtole":  ("tlajtoli",  "sustantivo"),
    "tlajtolpanol":("tlajtolpanolli","sustantivo"),
    "ikone":     ("iconetl",  "sustantivo"),
    "ikonewan":  ("iconetl",  "sustantivo"),
    "ikoni":     ("iconetl",  "sustantivo"),
    "tlaxkal":   ("tlaxkalli","sustantivo"),
    "teopan":    ("teopantli","sustantivo"),
    "tiopan":    ("teopantli","sustantivo"),
    "tomin":     ("tomintli", "sustantivo"),
    "tlamantle": ("tlamantli","sustantivo"),
    "tlamantin": ("tlamantli","sustantivo"),
    "xiwitl":    ("xihuitl",  "sustantivo"),
    "xiwit":     ("xihuitl",  "sustantivo"),
    "tlitl":     ("tlitl",    "sustantivo"),
    "krus":      ("krus",     "sustantivo"),
    "tlalpa":    ("tlalpan",  "sustantivo"),
    "altepetl":  ("altepetl", "sustantivo"),
    "altepeme":  ("altepetl", "sustantivo"),
    "tlajkate":  ("tlajtlakotl","sustantivo"),
    "tlajtlakol":("tlajtlakotl","sustantivo"),
    "tlajtlakole":("tlajtlakotl","sustantivo"),
    "tlajtlakot":("tlajtlakotl","sustantivo"),
    "pakilistle":("pakilistli","sustantivo"),
    "pakilis":   ("pakilistli","sustantivo"),
    "mikilistle":("mikilistli","sustantivo"),
    "mikilis":   ("mikilistli","sustantivo"),
    "tlaneltokalistle":("tlaneltokalistli","sustantivo"),
    "tlaneltokalis":   ("tlaneltokalistli","sustantivo"),
    "yolsewilistle":("yolsewilistli","sustantivo"),
    "yolsewilis":   ("yolsewilistli","sustantivo"),
    "tlajyowilistle":("tlajyowilistli","sustantivo"),
    "tlajyowilis":   ("tlajyowilistli","sustantivo"),
    "nemilistle":("nemilistli","sustantivo"),
    "tlanextle": ("tlaneztli","sustantivo"),
    "tlanex":    ("tlaneztli","sustantivo"),
    "wejkawitl": ("wejkawitl","sustantivo"),
    "itlaj":     ("itlajhtli","sustantivo"),
    "tlakuale":  ("tlakualli","sustantivo"),
    "tlakual":   ("tlakualli","sustantivo"),
    "melajka":   ("melajkak", "adjetivo"),
    "pueblo":    ("pueblo",   "sustantivo"),
    "rey":       ("rey",      "sustantivo"),
    "poder":     ("poder",    "sustantivo"),
    "estado":    ("estado",   "sustantivo"),
    "tajtzin":   ("tajtli",   "sustantivo"),
    "tote":      ("totah",    "sustantivo"),
    "totaj":     ("totah",    "sustantivo"),
    "totajtzin": ("totah",    "sustantivo"),
    "papan":     ("tahtli",   "sustantivo"),
    "judio":     ("judiojtl", "sustantivo"),
    "judiojtin": ("judiojtl", "sustantivo"),
    "fariseo":   ("fariseotl","sustantivo"),
    "fariseos":  ("fariseotl","sustantivo"),
    "profeta":   ("profetatl","sustantivo"),
    "profetajtin":("profetatl","sustantivo"),
    "tlatitlaniltin":("tlatitlanilli","sustantivo"),
    "tlatitlanil":("tlatitlanilli","sustantivo"),
    "tlamachtile":("tlamachtilli","sustantivo"),
    "tlamachtijke":("tlamachtiani","sustantivo"),
    "tiopixke":  ("teopixqui","sustantivo"),
    "tiopixkej": ("teopixqui","sustantivo"),
    # ADJETIVOS
    "kualtin":   ("kualli",   "adjetivo"),
    "kualli":    ("kualli",   "adjetivo"),
    "kuale":     ("kualli",   "adjetivo"),
    "weyikan":   ("weyik",    "adjetivo"),
    "weyi":      ("weyik",    "adjetivo"),
    "weyik":     ("weyik",    "adjetivo"),
    "chikawak":  ("chikawak", "adjetivo"),
    "chipawa":   ("chipawak", "adjetivo"),
    "chipawak":  ("chipawak", "adjetivo"),
    "yankuik":   ("yankuik",  "adjetivo"),
    "melawak":   ("melawak",  "adjetivo"),
    "welis":     ("welis",    "adjetivo"),   # puede / es posible
    "weli":      ("welis",    "adjetivo"),
    "okachi":    ("okachi",   "adjetivo"),   # más, bastante
    # NUMERALES
    "se":        ("se",       "numeral"),
    "ome":       ("ome",      "numeral"),
    "eyi":       ("eyi",      "numeral"),
    "nawi":      ("nawi",     "numeral"),
    "makuil":    ("makuilli", "numeral"),
    "chikuase":  ("chikuasen","numeral"),
    "chikome":   ("chikome",  "numeral"),
    "chikuey":   ("chikueyi", "numeral"),
    "nahui":     ("nahui",    "numeral"),
    "matlak":    ("matlaktli","numeral"),
    "poal":      ("poalli",   "numeral"),
}

# ──────────────────────────────────────────────
# 3.  REGLAS MORFOLÓGICAS (simulan el FST)
# ──────────────────────────────────────────────

SUBJECT_PREFIXES = [
    "nik", "nij", "ni", "tik", "tij", "ti", "ki",  "k", "kin", "kim", "an",
    "xi", "xik", "xij", "ma",
]
OBJECT_PREFIXES = ["nech", "mitz", "tech", "amech", "ki", "kin", "kim", "c", "quin"]
REFLEXIVE_PREFIXES = ["mo", "no", "to", "amo"]
COMPLETIVE_PREFIXES = ["o"]
VERBAL_SUFFIXES = [
    "ltiskej", "tiskej", "ltiske", "tiske", "ltisyaj", "tisyaj", "wiskej",  "wiske",
    "skej", "ske", "ltis", "tis", "wis", "jkej", "ke", "kej", "j", "ya", "yaj",
    "tiwitz", "titek", "tiw", "ko", "tok", "toke", "j", "ltia", "tia", "lhia", "lia", "s",
]
NOMINAL_SUFFIXES = ["jtin", "tzitzintin", "tzintin", "tintin", "mej", "tin", "me", "wan", "tli", "tl", "li", "le", "tzin"]
POSSESSIVE_PREFIXES = ["no", "to", "mo", "amo", "i", "in"]


# ──────────────────────────────────────────────
# 4.  INTENTO DE USAR HFST
# ──────────────────────────────────────────────
def _build_hfst_transducer():
    try:
        import hfst  # type: ignore
        lexc_content = """
Multichar_Symbols
+Verb +Noun +Adj +Comp +Imp
o- ni- ti- ki- kin- an- mo- no-
-s -ya -j -ke -kej -tia -lia -tok

LEXICON Root
VerbPrefix ;
NounPrefix ;
NounRoot  ;

LEXICON VerbPrefix
ni:ni VerbRoot "Subject 1sg" ;
ti:ti VerbRoot "Subject 2sg/1pl" ;
ki:ki VerbRoot "Subject 3sg obj" ;
an:an VerbRoot "Subject 2pl" ;
VerbRoot ;

LEXICON VerbRoot
chiwa:chiwa VerbSuffix "+Verb":0 ;
mati:mati   VerbSuffix "+Verb":0 ;
nemi:nemi   VerbSuffix "+Verb":0 ;
neki:neki   VerbSuffix "+Verb":0 ;
itta:itta   VerbSuffix "+Verb":0 ;
ilwia:ilwia VerbSuffix "+Verb":0 ;
yauh:ya     VerbSuffix "+Verb":0 ;
kalaki:kala VerbSuffix "+Verb":0 ;
kaki:kak    VerbSuffix "+Verb":0 ;
tlajtoa:tlajto VerbSuffix "+Verb":0 ;
mochiwa:mochiw VerbSuffix "+Verb":0 ;

LEXICON VerbSuffix
s:s # ;
ya:ya # ;
j:j # ;
ke:ke # ;
kej:kej # ;
0:0 # ;

LEXICON NounPrefix
no:no NounRoot ;
to:to NounRoot ;
mo:mo NounRoot ;
i:i  NounRoot ;
NounRoot ;

LEXICON NounRoot
tlakatl:tlaka NounSuffix "+Noun":0 ;
siwatl:siwa   NounSuffix "+Noun":0 ;
tekitl:teki   NounSuffix "+Noun":0 ;
atl:atl       NounSuffix "+Noun":0 ;
tlalli:tlal   NounSuffix "+Noun":0 ;
kalli:kal     NounSuffix "+Noun":0 ;
tonalli:tonal NounSuffix "+Noun":0 ;
tepetl:tepe   NounSuffix "+Noun":0 ;

LEXICON NounSuffix
tl:tl # ;
tli:tli # ;
li:li # ;
le:le # ;
mej:mej # ;
tin:tin # ;
me:me # ;
0:0 # ;

END
"""
        tmp_path = "/tmp/_nahuatl_lexc.lexc"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(lexc_content)

        transducer = hfst.compile_lexc_file(tmp_path)
        transducer.invert()
        transducer.minimize()
        return transducer
    except (ImportError, Exception):
        return None

_HFST_TRANSDUCER = _build_hfst_transducer()

def analyze_with_hfst(word: str) -> Optional[tuple[str, str]]:
    if _HFST_TRANSDUCER is None:
        return None
    try:
        results = _HFST_TRANSDUCER.lookup(word)
        if results:
            best = results[0][0]
            cat = "verbo" if "+Verb" in best else "sustantivo" if "+Noun" in best else "desconocido"
            lema = best.replace("+Verb", "").replace("+Noun", "").replace("+Adj", "").strip(":")
            if lema:
                return lema, cat
    except Exception:
        pass
    return None

# ──────────────────────────────────────────────
# 5.  ANALIZADOR MORFOLÓGICO POR REGLAS (fallback)
# ──────────────────────────────────────────────

def _strip_prefix(word: str, prefixes: list[str]) -> tuple[str, str]:
    for p in sorted(prefixes, key=len, reverse=True):
        if word.startswith(p) and len(word) - len(p) >= 3:
            return word[len(p):], p
    return word, ""

def _strip_suffix(word: str, suffixes: list[str]) -> tuple[str, str]:
    for s in sorted(suffixes, key=len, reverse=True):
        if word.endswith(s) and len(word) - len(s) >= 3:
            return word[: -len(s)], s
    return word, ""

def rule_based_lemmatize(word: str) -> tuple[str, str, bool]:
    w = word.lower().strip()
    if w in STOPWORDS_NAHUATL:
        return w, "stopword", True
    if w in LEXICON:
        lema, cat = LEXICON[w]
        return lema, cat, False

    stem = w
    if stem.startswith("o") and len(stem) > 4:
        stem = stem[1:]

    stem, subj = _strip_prefix(stem, SUBJECT_PREFIXES)
    stem, refl = _strip_prefix(stem, REFLEXIVE_PREFIXES)
    stem, obj = _strip_prefix(stem, OBJECT_PREFIXES)

    if stem in LEXICON:
        lema, cat = LEXICON[stem]
        return lema, cat, False

    verb_stem = stem
    for _ in range(3):
        new_stem, suf = _strip_suffix(verb_stem, VERBAL_SUFFIXES)
        if suf:
            verb_stem = new_stem
        else:
            break

    if verb_stem in LEXICON:
        lema, cat = LEXICON[verb_stem]
        return lema, cat, False

    if subj:
        if verb_stem.endswith("tia") or verb_stem.endswith("lia"):
            verb_stem = verb_stem[:-3]
        if verb_stem in LEXICON:
            lema, cat = LEXICON[verb_stem]
            return lema, cat, False
        return verb_stem, "verbo", False

    noun_stem = w
    noun_stem, poss = _strip_prefix(noun_stem, POSSESSIVE_PREFIXES)

    for _ in range(2):
        new_stem, suf = _strip_suffix(noun_stem, NOMINAL_SUFFIXES)
        if suf:
            noun_stem = new_stem
        else:
            break

    if noun_stem in LEXICON:
        lema, cat = LEXICON[noun_stem]
        return lema, cat, False

    if len(w) <= 2:
        return w, "stopword", True

    return noun_stem if noun_stem else w, "desconocido", False

# ──────────────────────────────────────────────
# 6.  LEMATIZADOR PRINCIPAL
# ──────────────────────────────────────────────
def lemmatize(word: str) -> tuple[str, str, bool]:
    w = word.lower().strip()
    if w in STOPWORDS_NAHUATL:
        return w, "stopword", True
    hfst_result = analyze_with_hfst(w)
    if hfst_result:
        lema, cat = hfst_result
        return lema, cat, False
    return rule_based_lemmatize(w)

# ──────────────────────────────────────────────
# 7.  PROCESAMIENTO DEL CSV
# ──────────────────────────────────────────────
def process_csv(input_path: str, output_path: str) -> None:
    input_path  = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        # ¡CORRECCIÓN AQUÍ! Lanzamos excepción en lugar de sys.exit(1)
        raise FileNotFoundError(f"[ERROR] Archivo no encontrado: {input_path}")

    hfst_status = "ACTIVO" if _HFST_TRANSDUCER is not None else "NO DISPONIBLE (usando reglas)"
    print(f"[INFO] HFST: {hfst_status}")
    print(f"[INFO] Leyendo: {input_path}")

    rows_in:  list[dict] = []
    fieldnames_in: list[str] = []

    with open(input_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames_in = reader.fieldnames or []
        for row in reader:
            rows_in.append(row)

    print(f"[INFO] Palabras leídas: {len(rows_in)}")

    fieldnames_out = fieldnames_in + ["lema", "categoria", "es_stopword"]
    stats = {"verbo": 0, "sustantivo": 0, "adjetivo": 0, "numeral": 0, "stopword": 0, "desconocido": 0}
    rows_out: list[dict] = []
    
    for row in rows_in:
        palabra = row.get("palabra", "").strip()
        lema, cat, is_sw = lemmatize(palabra)
        stats[cat if cat in stats else "desconocido"] += 1
        rows_out.append({
            **row,
            "lema":        lema,
            "categoria":   cat,
            "es_stopword": "sí" if is_sw else "no",
        })

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_out)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"[INFO] Resultado guardado en: {output_path}")
    print(f"[INFO] Estadísticas de categorías:")
    for cat, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"         {cat:<15} {count:>6}")

# ==============================================================================
# 8. NUEVA FUNCIÓN PARA EL PIPELINE (ENTRYPOINT)
# ==============================================================================
def ejecutar_lematizacion(archivo_entrada_csv: str, directorio_salida: str = "/tmp") -> str:
    """
    Función principal para ser llamada desde CorpusService.py en el pipeline.
    Recibe el CSV de la tokenización y retorna la ruta del CSV final lematizado.
    """
    import os
    import time
    
    print(f"\n--- INICIANDO LEMATIZACIÓN EN PIPELINE ---")
    
    # Asegurar que el directorio de salida existe
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Generar nombre del archivo de salida con timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_filename = f"lematizacion_{timestamp}.csv"
    output_path = os.path.join(directorio_salida, output_filename)
    
    # Ejecutar el procesamiento llamando a tu función existente
    process_csv(archivo_entrada_csv, output_path)
    
    print(f"✅ Lematización completada. Archivo generado: {output_path}")
    return output_path

# ==============================================================================

if __name__ == "__main__":
    # Rutas por defecto (ajusta según necesidad)
    INPUT_CSV  = sys.argv[1] if len(sys.argv) > 1 else "tokenizacion_20260312_115554.csv"
    OUTPUT_CSV = sys.argv[2] if len(sys.argv) > 2 else "lemas_nahuatl.csv"

    try:
        process_csv(INPUT_CSV, OUTPUT_CSV)
    except Exception as e:
        print(e)