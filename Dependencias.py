import os
import subprocess
import venv

# Lista de dependencias sin versiones (instalará las más recientes)
DEPENDENCIAS = [
    "annotated-doc",
    "annotated-types",
    "anyio",
    "bcrypt",
    "certifi",
    "charset-normalizer",
    "click",
    "docopt",
    "fastapi",
    "greenlet",
    "h11",
    "hdfs",
    "idna",
    "joblib",
    "langdetect",
    "nltk",
    "numpy",
    "pandas",
    "passlib",
    "pydantic",
    "pydantic-core",
    "PyJWT",
    "PyMySQL",
    "python-dateutil",
    "python-multipart",
    "regex",
    "requests",
    "six",
    "SQLAlchemy",
    "starlette",
    "tqdm",
    "typing-extensions",
    "typing-inspection",
    "urllib3",
    "uvicorn"
]

def configurar_entorno():
    directorio_venv = ".venv"

    print(f"[*] Creando el entorno virtual en '{directorio_venv}'...")
    venv.create(directorio_venv, with_pip=True)

    if os.name == 'nt': 
        pip_ejecutable = os.path.join(directorio_venv, "Scripts", "pip.exe")
    else:  
        pip_ejecutable = os.path.join(directorio_venv, "bin", "pip")

    print("[*] Actualizando pip...")
    subprocess.run([pip_ejecutable, "install", "--upgrade", "pip"], check=True)

    print("[*] Instalando dependencias en sus versiones más recientes...")
    comando_instalacion = [pip_ejecutable, "install"] + DEPENDENCIAS
    subprocess.run(comando_instalacion, check=True)

    print("\n¡Listo! Entorno virtual creado y dependencias actualizadas con éxito.")
    
    if os.name == 'nt':
        print(f"-> Para activar tu entorno usa: .\\{directorio_venv}\\Scripts\\activate")
    else:
        print(f"-> Para activar tu entorno usa: source {directorio_venv}/bin/activate")

if __name__ == "__main__":
    configurar_entorno()