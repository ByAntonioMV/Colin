from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import uvicorn
import os

from App.API.Routes.RouteViews import router as views_router
from App.API.Routes.AutenticacionRoute import router as auth_router
from App.API.Routes.UsuarioRoutes import router as usuarios
from App.API.Routes.CorpusRoute import router as corpus

app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def no_cache_static_files(request: Request, call_next):
    # Dejamos que FastAPI procese la petición normalmente
    response = await call_next(request)
    
    # Si detectamos que el navegador está pidiendo algo de la carpeta "/Public"
    # le inyectamos los encabezados anti-caché.
    if request.url.path.startswith("/Public"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
    return response
# Archivos estáticos 
app.mount("/Public", StaticFiles(directory="Public"), name="public")

app.include_router(views_router)
app.include_router(auth_router)
app.include_router(usuarios)
app.include_router(corpus)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)