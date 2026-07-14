# STREAMRAG - Plataforma SaaS de Ingeniería Hídrica

STREAMRAG es una plataforma SaaS en la nube diseñada para la modelación y el análisis hidrológico extremo en tiempo real directamente desde el navegador.

## 🚀 Arquitectura General
El proyecto está estructurado como un **Monorrepositorio** desacoplado:
*   **Backend (Python/FastAPI):** Procesa los cálculos científicos pesados utilizando NumPy, SciPy y Pandas.
*   **Frontend (React.js/Vite/TailwindCSS):** Interfaz interactiva de alto rendimiento que visualiza curvas estadísticas CDF y hietogramas de tormentas de diseño con Plotly.js.

---

## 🛠️ Requisitos
*   **Python 3.9+**
*   **Node.js 18+** y **npm** (para desarrollo local y compilación del frontend)

---

## 📂 Estructura del Proyecto
```
/SaaS (GitHub Repo Root)
├── .gitignore                    # Evita el seguimiento de respaldos locales (_backup/)
├── README.md                     # Este documento
├── backend/                      # Componente Backend (API FastAPI)
│   ├── app/
│   │   ├── main.py               # Servidor FastAPI
│   │   ├── config.py             # Carga centralizada de variables con pydantic-settings
│   │   ├── schemas.py            # Esquemas de entrada y salida (Pydantic)
│   │   ├── api/
│   │   │   └── endpoints.py      # Endpoints POST del sistema
│   │   └── core/
│   │       ├── analisis_frecuencias.py # Motor del Hito 1
│   │       └── hietogramas.py          # Motor del Hito 2
│   ├── requirements.txt          # Dependencias exactas de Python
│   ├── .env.example              # Guía de variables locales
│   └── test_*.py                 # Scripts de verificación
└── frontend/                     # Componente Frontend (React + Vite)
    ├── package.json              # Dependencias de npm
    ├── vite.config.js            # Configuración de compilación de Vite
    ├── tailwind.config.js        # Estilos de Tailwind CSS
    ├── index.html                # HTML base de entrada
    ├── .env.example              # Guía de variables del frontend
    └── src/
        ├── main.jsx              # Montaje de React
        ├── App.jsx               # Enrutador principal
        ├── config.js             # Centralización de VITE_API_URL
        └── components/           # Componentes de la interfaz
            ├── Dashboard.jsx
            ├── FrecuenciaModulo.jsx
            └── HietogramaModulo.jsx
```

---

## 💻 Instalación y Ejecución Local

### 1. Levantar el Backend (FastAPI)
1.  Navega al directorio del backend:
    ```bash
    cd backend
    ```
2.  Crea un entorno virtual e instálalo:
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En Linux/macOS:
    source venv/bin/activate
    ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Crea tu archivo `.env` basado en `.env.example`:
    ```bash
    cp .env.example .env
    ```
5.  Inicia el servidor en modo desarrollo:
    ```bash
    python -m uvicorn app.main:app --reload --port 8000
    ```
    *   **Documentación Interactiva (Swagger):** Abre [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Levantar el Frontend (React + Vite)
1.  Abre otra terminal y navega al directorio del frontend:
    ```bash
    cd frontend
    ```
2.  Instala los paquetes:
    ```bash
    npm install
    ```
3.  Crea tu archivo `.env` basado en `.env.example`:
    ```bash
    cp .env.example .env
    ```
4.  Inicia la aplicación:
    ```bash
    npm run dev
    ```
    *   **Acceso local:** Abre [http://localhost:5173](http://localhost:5173).

---

## ⚙️ Variables de Entorno

### Backend (`/backend/.env`)
*   `ENV`: `"development"` en local o `"production"` en Render.
*   `HOST`: Dirección local (`127.0.0.1`).
*   `PORT`: Puerto del servidor (`8000`).
*   `FRONTEND_URL`: URL del cliente en Vercel para validación CORS en producción.

### Frontend (`/frontend/.env`)
*   `VITE_API_URL`: URL base de la API (ej. `http://localhost:8000/api/v1` en local o `https://tu-backend.onrender.com/api/v1` en producción).

---

## ☁️ Procedimiento de Despliegue en Producción

### Paso 1: Subir el Monorrepositorio a GitHub
1.  Inicializa Git en la raíz del proyecto `/SaaS`:
    ```bash
    git init
    git add .
    git commit -m "feat: base architecture for production"
    ```
2.  Crea un repositorio en GitHub y asócialo para subir tu rama principal:
    ```bash
    git remote add origin https://github.com/tu-usuario/tu-repositorio.git
    git branch -M main
    git push -u origin main
    ```

### Paso 2: Desplegar el Backend en Render.com
1.  Crea un nuevo **Web Service** en Render y vincula tu repositorio de GitHub.
2.  Configura los siguientes campos específicos del monorrepositorio:
    *   **Root Directory:** `backend` *(¡Muy importante!)*
    *   **Runtime:** `Python 3`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3.  En la pestaña **Environment**, agrega las variables de entorno de producción:
    *   `PYTHON_VERSION` = `3.12.3` *(¡Muy importante para usar paquetes compilados en Render y evitar fallos con SciPy!)*
    *   `ENV` = `production`
    *   `FRONTEND_URL` = `https://tu-frontend.vercel.app` (URL de Vercel una vez creada).
4.  Presiona **Deploy**. Render te proporcionará tu URL del backend (ej. `https://tu-backend.onrender.com`).

### Paso 3: Desplegar el Frontend en Vercel.com
1.  Crea un nuevo proyecto en Vercel y vincula tu repositorio de GitHub.
2.  Configura los siguientes campos específicos del monorrepositorio:
    *   **Root Directory:** `frontend` *(Vercel detectará Vite automáticamente)*.
3.  En la sección **Environment Variables**, agrega la URL de producción de tu API:
    *   `VITE_API_URL` = `https://tu-backend.onrender.com/api/v1` (URL asignada por Render).
4.  Presiona **Deploy**. Vercel compilará tu aplicación y te asignará la URL pública para tus usuarios.
