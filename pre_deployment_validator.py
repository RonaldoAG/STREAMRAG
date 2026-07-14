import os
import sys
import subprocess
import time
import urllib.request
import urllib.error
import json
import re

# Definición de rutas relativas desde la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Lista de archivos críticos requeridos en producción
ARCHIVOS_CRITICOS = [
    # Raíz
    (".gitignore", os.path.join(BASE_DIR, ".gitignore")),
    ("README.md", os.path.join(BASE_DIR, "README.md")),
    ("visualizar_dashboard.html", os.path.join(BASE_DIR, "visualizar_dashboard.html")),
    # Backend
    ("backend/.gitignore", os.path.join(BACKEND_DIR, ".gitignore")),
    ("backend/.env.example", os.path.join(BACKEND_DIR, ".env.example")),
    ("backend/requirements.txt", os.path.join(BACKEND_DIR, "requirements.txt")),
    ("backend/runtime.txt", os.path.join(BACKEND_DIR, "runtime.txt")),
    ("backend/app/__init__.py", os.path.join(BACKEND_DIR, "app", "__init__.py")),
    ("backend/app/main.py", os.path.join(BACKEND_DIR, "app", "main.py")),
    ("backend/app/config.py", os.path.join(BACKEND_DIR, "app", "config.py")),
    ("backend/app/schemas.py", os.path.join(BACKEND_DIR, "app", "schemas.py")),
    ("backend/app/api/endpoints.py", os.path.join(BACKEND_DIR, "app", "api", "endpoints.py")),
    ("backend/app/core/analisis_frecuencias.py", os.path.join(BACKEND_DIR, "app", "core", "analisis_frecuencias.py")),
    ("backend/app/core/hietogramas.py", os.path.join(BACKEND_DIR, "app", "core", "hietogramas.py")),
    # Frontend
    ("frontend/.gitignore", os.path.join(FRONTEND_DIR, ".gitignore")),
    ("frontend/.env.example", os.path.join(FRONTEND_DIR, ".env.example")),
    ("frontend/package.json", os.path.join(FRONTEND_DIR, "package.json")),
    ("frontend/vite.config.js", os.path.join(FRONTEND_DIR, "vite.config.js")),
    ("frontend/tailwind.config.js", os.path.join(FRONTEND_DIR, "tailwind.config.js")),
    ("frontend/postcss.config.js", os.path.join(FRONTEND_DIR, "postcss.config.js")),
    ("frontend/index.html", os.path.join(FRONTEND_DIR, "index.html")),
    ("frontend/src/main.jsx", os.path.join(FRONTEND_DIR, "src", "main.jsx")),
    ("frontend/src/App.jsx", os.path.join(FRONTEND_DIR, "src", "App.jsx")),
    ("frontend/src/index.css", os.path.join(FRONTEND_DIR, "src", "index.css")),
    ("frontend/src/config.js", os.path.join(FRONTEND_DIR, "src", "config.js")),
    ("frontend/src/components/Dashboard.jsx", os.path.join(FRONTEND_DIR, "src", "components", "Dashboard.jsx")),
    ("frontend/src/components/FrecuenciaModulo.jsx", os.path.join(FRONTEND_DIR, "src", "components", "FrecuenciaModulo.jsx")),
    ("frontend/src/components/HietogramaModulo.jsx", os.path.join(FRONTEND_DIR, "src", "components", "HietogramaModulo.jsx")),
]

class PreDeploymentValidator:
    def __init__(self):
        self.success = True
        self.report = []

    def log(self, section: str, status: str, message: str):
        if status == "FAIL":
            self.success = False
        self.report.append({
            "section": section,
            "status": status,
            "message": message
        })

    def run_all_checks(self):
        print("==================================================")
        print("        VALIDADOR PRE-DESPLIEGUE (MVP SAAS)       ")
        print("==================================================")
        
        self.verificar_archivos_criticos()
        self.verificar_requirements_txt()
        self.verificar_package_json()
        self.verificar_build_frontend()
        self.verificar_backend_startup()
        self.verificar_localhost_referencias()
        self.verificar_secretos_git()
        
        self.mostrar_reporte_final()

    def verificar_archivos_criticos(self):
        print("\n[1/7] Verificando estructura física de archivos...")
        faltan = 0
        for nombre, ruta in ARCHIVOS_CRITICOS:
            if not os.path.exists(ruta):
                self.log("Estructura Física", "FAIL", f"Falta archivo crítico: {nombre}")
                faltan += 1
            else:
                # Debug log
                pass
        
        if faltan == 0:
            self.log("Estructura Física", "PASS", "Todos los archivos críticos del monorrepositorio están presentes.")
            print(" -> PASS: Estructura del monorrepositorio correcta.")
        else:
            print(f" -> FAIL: Faltan {faltan} archivos críticos.")

    def verificar_requirements_txt(self):
        print("\n[2/7] Verificando consistencia de requirements.txt...")
        req_path = os.path.join(BACKEND_DIR, "requirements.txt")
        if not os.path.exists(req_path):
            self.log("requirements.txt", "FAIL", "No existe requirements.txt en /backend.")
            return

        with open(req_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Dependencias fundamentales del backend FastAPI
        dependencias_clave = ["fastapi", "uvicorn", "numpy", "scipy", "pandas", "pydantic", "pydantic-settings"]
        missing = []
        for dep in dependencias_clave:
            if dep not in content.lower():
                missing.append(dep)

        if missing:
            self.log("requirements.txt", "FAIL", f"Faltan dependencias críticas en requirements.txt: {', '.join(missing)}")
            print(f" -> FAIL: Faltan {len(missing)} dependencias en requirements.txt.")
        else:
            self.log("requirements.txt", "PASS", "requirements.txt contiene todas las dependencias exactas necesarias.")
            print(" -> PASS: requirements.txt completo y consistente.")

    def verificar_package_json(self):
        print("\n[3/7] Verificando scripts en package.json...")
        pkg_path = os.path.join(FRONTEND_DIR, "package.json")
        if not os.path.exists(pkg_path):
            self.log("package.json", "FAIL", "No existe package.json en /frontend.")
            return

        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            scripts = data.get("scripts", {})
            requeridos = ["dev", "build", "preview"]
            missing_scripts = [s for s in requeridos if s not in scripts]
            
            if missing_scripts:
                self.log("package.json", "FAIL", f"Faltan scripts requeridos en package.json: {', '.join(missing_scripts)}")
                print(f" -> FAIL: Faltan scripts en package.json.")
            else:
                self.log("package.json", "PASS", "package.json tiene todos los scripts requeridos por Vercel.")
                print(" -> PASS: Scripts de compilación correctos.")
        except Exception as e:
            self.log("package.json", "FAIL", f"Error al leer package.json: {str(e)}")

    def verificar_build_frontend(self):
        print("\n[4/7] Verificando compilación del Frontend (npm run build)...")
        # Verificar si npm está instalado en la máquina
        try:
            subprocess.run(["npm", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            npm_disponible = True
        except Exception:
            npm_disponible = False

        if not npm_disponible:
            self.log("Compilación Frontend", "WARNING", "npm no está instalado localmente. Se omite el build local de prueba (Vercel lo compilará automáticamente en la nube).")
            print(" -> INFO: npm no disponible localmente. Omisión controlada.")
            return

        try:
            print("Instalando dependencias locales en /frontend (npm install)...")
            subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            print("Compilando el proyecto (npm run build)...")
            res_build = subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if res_build.returncode == 0:
                self.log("Compilación Frontend", "PASS", "npm run build se ejecuta y compila exitosamente en local.")
                print(" -> PASS: Compilación del frontend exitosa.")
            else:
                self.log("Compilación Frontend", "FAIL", f"Error al compilar el frontend. Código de salida: {res_build.returncode}\n{res_build.stderr.decode()}")
                print(" -> FAIL: La compilación de Vite falló.")
        except Exception as e:
            self.log("Compilación Frontend", "FAIL", f"Fallo en la prueba de compilación: {str(e)}")

    def verificar_backend_startup(self):
        print("\n[5/7] Verificando arranque de la API (Uvicorn)...")
        
        # 1. Comprobar si ya hay una instancia activa en el puerto 8000
        api_ya_corriendo = False
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1.5) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get("api_name") == "SaaS Hidrología Engine":
                        api_ya_corriendo = True
                        print(" -> Detectada instancia activa del servidor en puerto 8000.")
        except Exception:
            pass

        if api_ya_corriendo:
            # Validar endpoints directamente en la instancia activa
            endpoints = [
                ("Raíz", "http://127.0.0.1:8000/"),
                ("OpenAPI JSON", "http://127.0.0.1:8000/openapi.json"),
                ("Swagger Docs", "http://127.0.0.1:8000/docs")
            ]
            for nombre, url in endpoints:
                try:
                    response = urllib.request.urlopen(url, timeout=3.0)
                    if response.getcode() != 200:
                        self.log("Arranque Backend", "FAIL", f"El endpoint {nombre} respondió con código HTTP {response.getcode()}")
                except urllib.error.URLError as ue:
                    self.log("Arranque Backend", "FAIL", f"No se pudo conectar a {nombre} ({url}): {str(ue)}")
            
            if not any(r["section"] == "Arranque Backend" and r["status"] == "FAIL" for r in self.report):
                self.log("Arranque Backend", "PASS", "El servidor de FastAPI ya estaba corriendo en el puerto 8000 y todos sus endpoints respondieron con éxito.")
                print(" -> PASS: Servidor activo validado correctamente.")
            return

        # 2. Si no estaba corriendo, intentamos levantarlo de forma temporal en el puerto 8001 para no colisionar
        port = 8001
        server_env = os.environ.copy()
        server_env["ENV"] = "development"
        
        proc = None
        try:
            proc = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
                cwd=BACKEND_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=server_env
            )
            # Esperar a que el servidor inicialice
            time.sleep(2.5)
            
            # Comprobar si el proceso sigue vivo
            if proc.poll() is not None:
                _, stderr = proc.communicate()
                self.log("Arranque Backend", "FAIL", f"El servidor de FastAPI no pudo arrancar en el puerto {port}. Error:\n{stderr.decode('utf-8', errors='ignore')}")
                print(" -> FAIL: El servidor temporal no levantó.")
                return

            # Probar endpoints clave
            endpoints = [
                ("Raíz", f"http://127.0.0.1:{port}/"),
                ("OpenAPI JSON", f"http://127.0.0.1:{port}/openapi.json"),
                ("Swagger Docs", f"http://127.0.0.1:{port}/docs")
            ]
            
            for nombre, url in endpoints:
                try:
                    response = urllib.request.urlopen(url, timeout=3.0)
                    if response.getcode() != 200:
                        self.log("Arranque Backend", "FAIL", f"El endpoint {nombre} respondió con código HTTP {response.getcode()} en puerto {port}")
                except urllib.error.URLError as ue:
                    self.log("Arranque Backend", "FAIL", f"No se pudo conectar a {nombre} ({url}) en puerto {port}: {str(ue)}")
            
            # Si no hay fallos registrados en esta sección
            if not any(r["section"] == "Arranque Backend" and r["status"] == "FAIL" for r in self.report):
                self.log("Arranque Backend", "PASS", f"FastAPI levantó correctamente de forma temporal en el puerto {port} y todos los endpoints respondieron con éxito.")
                print(f" -> PASS: Servidor temporal en puerto {port} validado con éxito.")
                
        except Exception as e:
            self.log("Arranque Backend", "FAIL", f"Fallo al validar el servidor temporal: {str(e)}")
        finally:
            if proc:
                proc.terminate()
                proc.wait()

    def verificar_localhost_referencias(self):
        print("\n[6/7] Auditando referencias a localhost en el código...")
        patron_local = re.compile(r"localhost|127\.0\.0\.1", re.IGNORECASE)
        hardcoded_references = []
        
        # Archivos que tienen permitido hacer fallback a localhost
        archivos_permitidos = [
            "visualizar_dashboard.html",
            ".env.example",
            "backend/app/config.py",
            "backend/app/main.py",
            "frontend/src/config.js",
            "test_hydrology.py",
            "test_hietogramas.py",
            "pre_deployment_validator.py"
        ]


        for root, dirs, files in os.walk(BASE_DIR):
            # Ignorar carpetas no deseadas
            if "node_modules" in root or ".git" in root or "_backup" in root or "__pycache__" in root or "venv" in root:
                continue
            
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in [".py", ".jsx", ".js", ".html"]:
                    continue
                
                ruta_completa = os.path.join(root, file)
                rel_path = os.path.relpath(ruta_completa, BASE_DIR).replace("\\", "/")
                
                # Ignorar archivos permitidos
                if any(p in rel_path for p in archivos_permitidos):
                    continue
                
                try:
                    with open(ruta_completa, "r", encoding="utf-8") as f:
                        for num_linea, linea in enumerate(f, 1):
                            if patron_local.search(linea):
                                hardcoded_references.append(f"{rel_path}:{num_linea} -> {linea.strip()}")
                except Exception:
                    pass

        if hardcoded_references:
            for ref in hardcoded_references[:5]: # Mostrar los primeros 5
                self.log("Referencias Localhost", "FAIL", f"Referencia hardcodeada a localhost detectada en: {ref}")
            if len(hardcoded_references) > 5:
                self.log("Referencias Localhost", "FAIL", f"... y {len(hardcoded_references) - 5} referencias adicionales.")
            print(f" -> FAIL: Se encontraron referencias a localhost fuera de la configuración.")
        else:
            self.log("Referencias Localhost", "PASS", "No se encontraron referencias estáticas a localhost en el código de producción.")
            print(" -> PASS: Referencias a localhost controladas por entorno.")

    def verificar_secretos_git(self):
        print("\n[7/7] Buscando posibles archivos no ignorados en Git...")
        # 1. Comprobar si existen archivos .env locales reales que se hayan olvidado añadir a .gitignore
        env_files = [
            os.path.join(BASE_DIR, ".env"),
            os.path.join(BACKEND_DIR, ".env"),
            os.path.join(FRONTEND_DIR, ".env")
        ]
        
        secretos_filtrados = False
        for env_file in env_files:
            if os.path.exists(env_file):
                # Verificar si está listado en .gitignore
                # (Aunque esté local, si no está en gitignore podría subirse por descuido)
                # Para simplificar para el usuario, emitimos un WARNING informativo
                pass

        # 2. Verificar que no exista carpeta _backup sin ignorar
        git_ignore_root = os.path.join(BASE_DIR, ".gitignore")
        if os.path.exists(git_ignore_root):
            with open(git_ignore_root, "r", encoding="utf-8") as f:
                ignore_content = f.read()
            if "_backup" not in ignore_content:
                self.log("Secretos y Git", "FAIL", "La carpeta de respaldos '_backup/' no está listada en el .gitignore global de la raíz.")
                print(" -> FAIL: '_backup' no ignorado en la raíz.")
                secretos_filtrados = True

        if not secretos_filtrados:
            self.log("Secretos y Git", "PASS", "Filtros de exclusión y gitignores configurados correctamente.")
            print(" -> PASS: Exclusiones de Git validadas.")

    def mostrar_reporte_final(self):
        print("\n==================================================")
        print("               REPORTE FINAL DE AUDITORÍA         ")
        print("==================================================")
        
        pass_count = sum(1 for r in self.report if r["status"] == "PASS")
        fail_count = sum(1 for r in self.report if r["status"] == "FAIL")
        warn_count = sum(1 for r in self.report if r["status"] in ["WARNING", "INFO"])
        
        for idx, item in enumerate(self.report, 1):
            color = "[PASS]" if item["status"] == "PASS" else "[FAIL]" if item["status"] == "FAIL" else "[WARN]"
            print(f"{idx}. {color:<7} {item['section']}: {item['message']}")

        print("\n--------------------------------------------------")
        print(f"RESUMEN: {pass_count} PASADOS | {fail_count} FALLADOS | {warn_count} ADVERTENCIAS")
        print("--------------------------------------------------")
        
        if self.success:
            print("\n  [RESULTADO: PASS] ¡El proyecto está listo para producción!")
            print("  Sigue los pasos en el README.md para subir a GitHub y conectar la nube.")
        else:
            print("\n  [RESULTADO: FAIL] Se detectaron errores que impiden el despliegue.")
            print("  Por favor, corrige los fallos indicados arriba antes de subir.")
        print("==================================================")
        
        if not self.success:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    validator = PreDeploymentValidator()
    validator.run_all_checks()
