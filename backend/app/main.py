from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as hidrologia_router
from app.config import settings

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="SaaS Hidrología - API Engine",
    description=(
        "Servicios de cálculo numérico para ingeniería hídrica y ambiental en la nube. "
        "Permite estimar eventos extremos de lluvia y caudales mediante modelos estadísticos avanzados."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración dinámica y segura de CORS
origins = [
    "http://localhost:5173",      # Vite React desarrollo local por defecto
    "http://127.0.0.1:5173",
    "http://localhost:3000",      # React App de desarrollo alternativa
    "http://127.0.0.1:3000"
]

# Si estamos en producción y se especifica la URL de producción del Frontend
if settings.ENV == "production" and settings.FRONTEND_URL:
    # Agregar el dominio de producción a los orígenes autorizados
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de enrutadores de la API (versión 1)
app.include_router(
    hidrologia_router,
    prefix="/api/v1/hidrologia",
    tags=["Hidrología y Clima"]
)

@app.get("/", tags=["Estado"])
def read_root():
    """
    Ruta raíz para comprobar el estado de salud de la API.
    """
    return {
        "status": "online",
        "api_name": "SaaS Hidrología Engine",
        "version": "1.0.0",
        "env": settings.ENV,
        "documentacion": "/docs"
    }
