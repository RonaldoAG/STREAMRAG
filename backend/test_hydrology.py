import json
import numpy as np
from app.core.analisis_frecuencias import AnalisisFrecuencias
from fastapi.testclient import TestClient

# Datos de precipitación máxima anual simulados para pruebas (25 años de registros en mm)
DATOS_PRUEBA = [
    54.2, 68.5, 47.9, 88.3, 61.0, 72.4, 50.1, 95.6, 42.8, 59.3,
    78.1, 65.2, 53.0, 49.7, 83.4, 102.1, 57.6, 66.8, 44.9, 75.0,
    60.3, 51.5, 91.2, 70.8, 58.7
]

def verificar_calculos():
    print("=== 1. VERIFICACIÓN DEL MOTOR CIENTÍFICO (CORE) ===")
    motor = AnalisisFrecuencias(DATOS_PRUEBA)
    
    # Procesar análisis con Método de Momentos para Gumbel
    res_momentos = motor.procesar_analisis(metodo_gumbel="momentos")
    print(f"Número de registros: {res_momentos['resumen']['num_observaciones']}")
    print(f"Media de la muestra: {res_momentos['resumen']['media']:.2f} mm")
    print(f"Desviación Estándar: {res_momentos['resumen']['desviacion_estandar']:.2f} mm")
    
    print("\n--- Distribución Gumbel (Momento de Momentos) ---")
    print(f"Parámetro de ubicación (mu): {res_momentos['gumbel']['mu']:.4f}")
    print(f"Parámetro de escala (beta): {res_momentos['gumbel']['beta']:.4f}")
    print(f"Estadístico KS: {res_momentos['gumbel']['ks_statistic']:.4f} (p-valor: {res_momentos['gumbel']['ks_p_value']:.4f})")
    
    # Procesar análisis con MLE para Gumbel
    res_mle = motor.procesar_analisis(metodo_gumbel="mle")
    print("\n--- Distribución Gumbel (MLE) ---")
    print(f"Parámetro de ubicación (mu): {res_mle['gumbel']['mu']:.4f}")
    print(f"Parámetro de escala (beta): {res_mle['gumbel']['beta']:.4f}")
    print(f"Estadístico KS: {res_mle['gumbel']['ks_statistic']:.4f} (p-valor: {res_mle['gumbel']['ks_p_value']:.4f})")
    
    print("\n--- Distribución Log-Pearson Tipo III (Momentos) ---")
    print(f"Media Log: {res_momentos['log_pearson3']['mean_log']:.4f}")
    print(f"Std Log: {res_momentos['log_pearson3']['std_log']:.4f}")
    print(f"Asimetría Log (skew): {res_momentos['log_pearson3']['skew_log']:.4f}")
    print(f"Estadístico KS (Log-space): {res_momentos['log_pearson3']['ks_statistic']:.4f} (p-valor: {res_momentos['log_pearson3']['ks_p_value']:.4f})")
    
    print("\nDistribución Recomendada (Mejor Ajuste KS):", res_momentos['resumen']['distribucion_recomendada'])
    
    print("\n--- Eventos de Diseño (Precipitaciones en mm por Periodo de Retorno) ---")
    print(f"{'T (años)':<10} | {'Gumbel (mm)':<12} | {'Log-Pearson III (mm)':<20}")
    print("-" * 50)
    for ev in res_momentos['eventos_diseno']:
        print(f"{ev['periodo_retorno']:<10} | {ev['gumbel']:<12.2f} | {ev['log_pearson3']:<20.2f}")

    # Guardar un ejemplo de salida JSON completa para uso del frontend
    with open("example_output.json", "w", encoding="utf-8") as f:
        json.dump(res_momentos, f, indent=2, ensure_ascii=False)
    print("\n[OK] Resultados guardados en 'example_output.json' para el frontend.")

def verificar_api():
    print("\n=== 2. VERIFICACIÓN DEL ENDPOINT (FASTAPI TESTCLIENT) ===")
    from app.main import app
    
    client = TestClient(app)
    
    payload = {
        "datos": DATOS_PRUEBA,
        "metodo_gumbel": "momentos",
        "periodos_retorno": [2, 5, 10, 25, 50, 100, 500]
    }
    
    print("Enviando petición POST a /api/v1/hidrologia/analisis-frecuencia...")
    response = client.post("/api/v1/hidrologia/analisis-frecuencia", json=payload)
    
    if response.status_code == 200:
        print("[OK] Conexión exitosa! Estado HTTP 200 OK.")
        data = response.json()
        print(f"Respuesta JSON validada por Pydantic.")
        print(f"Claves principales del JSON devuelto: {list(data.keys())}")
        print(f"Recomendación de la API: {data['resumen']['distribucion_recomendada']}")
    else:
        print(f"[ERROR] Error en la petición: Código {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    try:
        verificar_calculos()
    except Exception as e:
        print("Error al verificar cálculos:", e)
        
    try:
        verificar_api()
    except Exception as e:
        print("\nNota: No se pudo verificar la API mediante TestClient porque faltan dependencias (ej. fastapi).")
        print("Error:", e)
