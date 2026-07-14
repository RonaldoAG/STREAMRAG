# Guía de Despliegue en la Nube: Plataforma SaaS de Ingeniería Hídrica

Esta guía detalla los pasos de infraestructura, configuración de variables de entorno y seguridad necesarios para publicar tu plataforma y permitir que otros ingenieros y usuarios accedan de forma remota.

---

## 1. Preparación de Repositorios en GitHub

Para un flujo de trabajo CI/CD (Integración y Despliegue Continuos), te recomendamos dividir tu código en dos repositorios de GitHub independientes:

1.  **Repositorio del Backend:** Aloja la carpeta `app/` y el archivo `requirements.txt`.
2.  **Repositorio del Frontend:** Aloja la estructura de tu proyecto React (o el archivo HTML/JS optimizado).

### Generar `requirements.txt` para el Backend
Para que el servidor en la nube sepa qué librerías de Python instalar, crea un archivo `requirements.txt` en la raíz del backend con el siguiente contenido:

```text
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
numpy>=1.22.0
scipy>=1.10.0
pandas>=2.0.0
```

---

## 2. Despliegue del Backend (FastAPI) en Render.com

Render es una de las plataformas más sencillas y accesibles para alojar aplicaciones FastAPI en Python.

### Pasos para el Despliegue:
1.  Inicia sesión en [Render.com](https://render.com/) (puedes ingresar usando tu cuenta de GitHub).
2.  Haz clic en **New +** y selecciona **Web Service**.
3.  Conecta tu repositorio de GitHub del backend.
4.  Configura los parámetros del Web Service:
    *   **Name:** `streamrag-backend` (o el nombre que prefieras).
    *   **Region:** Selecciona la más cercana a tus usuarios (ej. *Oregon* o *Ohio* para América).
    *   **Branch:** `main` (o tu rama de producción).
    *   **Runtime:** `Python 3`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
    *   **Plan:** Selecciona el plan gratuito (*Free*) o el plan básico (*Starter*) para evitar que la API entre en reposo tras periodos de inactividad.
    *   **Environment Variables:** Agrega la variable `PYTHON_VERSION` con el valor `3.12.3` en la pestaña Environment de Render (esencial para usar paquetes compilados y evitar fallos de compilación con SciPy/NumPy).
5.  Haz clic en **Create Web Service**.

Una vez completado el despliegue, Render te asignará una URL pública segura como:
`https://streamrag-backend.onrender.com`

---

## 3. Despliegue del Frontend (React) en Vercel

Vercel es la plataforma líder para desplegar aplicaciones frontales interactivas construidas con React o Vite.

### Pasos para el Despliegue:
1.  Antes de subir a GitHub, modifica tus archivos de React (`Dashboard.jsx`, `FrecuenciaModulo.jsx`, `HietogramaModulo.jsx`) para que la variable `API_BASE_URL` apunte a la URL de Render:
    ```javascript
    const API_BASE_URL = "https://streamrag-backend.onrender.com/api/v1";
    ```
2.  Inicia sesión en [Vercel.com](https://vercel.com/) con tu cuenta de GitHub.
3.  Haz clic en **Add New** > **Project**.
4.  Importa tu repositorio de GitHub del frontend.
5.  En la configuración del proyecto:
    *   **Framework Preset:** Selecciona `Vite` o `Create React App` (según cómo hayas inicializado el frontend).
    *   **Build and Output Settings:** Déjalos por defecto (`npm run build`).
6.  Haz clic en **Deploy**.

Vercel compilará tu aplicación y te dará una URL pública gratuita como:
`https://streamrag-frontend.vercel.app`

---

## 4. Configuraciones Críticas de Seguridad (CORS)

Una vez que tengas la URL de tu frontend de Vercel, debes **restringir el backend** para que solo acepte peticiones de tu dominio.

Modifica tu archivo `app/main.py` de la siguiente manera:

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as hidrologia_router

app = FastAPI(title="SaaS Hidrología - API Engine", version="1.0.0")

# Lista de orígenes de confianza (Asegura tu API frente a robos de cómputo)
origins = [
    "https://streamrag-frontend.vercel.app",  # Tu dominio en Vercel
    "http://localhost:3000",                    # Entorno de desarrollo local de React
    "http://localhost:5173",                    # Entorno de desarrollo local de Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Sube los cambios a tu repositorio de backend en GitHub; Render los detectará y redesplegará la aplicación automáticamente de forma segura.

---

## 5. (Alternativa Rápida) Publicar como una única página en GitHub Pages
Si solo deseas compartir una demo interactiva rápida sin configurar un pipeline de React:
1.  Cambia el nombre del archivo `visualizar_dashboard.html` a `index.html`.
2.  Cambia `API_BASE_URL` dentro del script a tu URL del backend de Render.
3.  Sube `index.html` a un repositorio público en GitHub.
4.  Entra en **Settings** > **Pages** en tu repositorio, selecciona la rama `main` y guarda.
5.  En pocos minutos, tu dashboard estará publicado gratis en:
    `https://tu-usuario-github.github.io/tu-repositorio/`
