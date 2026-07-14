import json
import numpy as np
from app.core.hietogramas import HietogramaDiseno
from fastapi.testclient import TestClient

# Coeficientes IDF de prueba (típicos de una región andina/costera)
K_PRUEBA = 1250.4
M_PRUEBA = 0.28
C_PRUEBA = 15.0
ETA_PRUEBA = 0.72

# Parámetros de tormenta
T_RETORNO = 10.0      # Periodo de retorno de 10 años
T_DURACION = 120      # Duración total de 120 minutos (2 horas)
PASO_TIEMPO = 10      # Paso de 10 minutos (12 bloques)
ASIMETRIA = 0.35      # Pico en el primer tercio (35%)

def verificar_motor_hietogramas():
    print("=== 1. VERIFICACIÓN DEL MOTOR CIENTÍFICO (CORE) ===")
    
    motor = HietogramaDiseno(
        k=K_PRUEBA,
        m=M_PRUEBA,
        C=C_PRUEBA,
        eta=ETA_PRUEBA,
        T=T_RETORNO
    )
    
    # Generar hietograma
    resultado = motor.generar_hietograma(
        t_d=T_DURACION,
        dt=PASO_TIEMPO,
        r=ASIMETRIA
    )
    
    meta = resultado["metadatos"]
    intervalos = resultado["intervalos"]
    
    print(f"Periodo de Retorno: {meta['periodo_retorno_anos']} años")
    print(f"Duración de tormenta: {meta['duracion_total_minutos']} min ({meta['num_bloques']} bloques de {meta['paso_tiempo_minutos']} min)")
    print(f"Precipitación total acumulada: {meta['precipitacion_total_mm']:.4f} mm")
    print(f"Intensidad de pico en el hietograma: {meta['intensidad_pico_mm_h']:.4f} mm/h")
    print(f"Factor de asimetría utilizado: r = {meta['factor_asimetria_r']}")
    
    # Verificación de Conservación de Masa
    suma_incrementos = sum(item["precipitacion_incremental"] for item in intervalos)
    lluvia_total = meta["precipitacion_total_mm"]
    diferencia_masa = abs(suma_incrementos - lluvia_total)
    
    print("\n--- Verificaciones Físicas ---")
    if diferencia_masa < 1e-9:
        print(f"[OK] Conservación de Masa: Cumplida. Suma incrementos ({suma_incrementos:.4f} mm) = Lluvia total acumulada ({lluvia_total:.4f} mm)")
    else:
        print(f"[ERROR] Discrepancia de masa detectada: {diferencia_masa} mm")
        
    # Verificación de ubicación del pico
    bloques_incrementales = [item["precipitacion_incremental"] for item in intervalos]
    idx_pico_detectado = np.argmax(bloques_incrementales)
    idx_pico_esperado = int(np.floor(ASIMETRIA * (T_DURACION / PASO_TIEMPO)))
    
    if idx_pico_detectado == idx_pico_esperado:
        print(f"[OK] Posicionamiento del Pico: Cumplido. Pico máximo ubicado en el bloque {idx_pico_detectado} (Tiempo: {intervalos[idx_pico_detectado]['tiempo_inicio']}-{intervalos[idx_pico_detectado]['tiempo_fin']} min)")
    else:
        print(f"[ERROR] El pico máximo está en el bloque {idx_pico_detectado}, se esperaba en el bloque {idx_pico_esperado}")
        
    # Tabla del hietograma generado
    print("\n--- Hietograma de Diseño Generado ---")
    print(f"{'Tiempo (min)':<12} | {'Incremento (mm)':<16} | {'Acumulado (mm)':<16} | {'Intensidad (mm/h)':<18}")
    print("-" * 70)
    for item in intervalos:
        intervalo_txt = f"{item['tiempo_inicio']}-{item['tiempo_fin']}"
        print(f"{intervalo_txt:<12} | {item['precipitacion_incremental']:<16.4f} | {item['precipitacion_acumulada']:<16.4f} | {item['intensidad']:<18.4f}")
        
    # Guardar resultados
    with open("example_hyetograph.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    print("\n[OK] Resultados completos exportados a 'example_hyetograph.json' para el frontend.")


def verificar_api_hietogramas():
    print("\n=== 2. VERIFICACIÓN DEL ENDPOINT (FASTAPI TESTCLIENT) ===")
    from app.main import app
    
    client = TestClient(app)
    
    payload = {
        "k": K_PRUEBA,
        "m": M_PRUEBA,
        "C": C_PRUEBA,
        "eta": ETA_PRUEBA,
        "T": T_RETORNO,
        "t_d": T_DURACION,
        "dt": PASO_TIEMPO,
        "r": ASIMETRIA
    }
    
    print("Enviando petición POST a /api/v1/hidrologia/hietograma-diseno...")
    response = client.post("/api/v1/hidrologia/hietograma-diseno", json=payload)
    
    if response.status_code == 200:
        print("[OK] Conexión exitosa! Estado HTTP 200 OK.")
        data = response.json()
        print(f"Respuesta JSON validada por Pydantic.")
        print(f"Claves principales del JSON devuelto: {list(data.keys())}")
        print(f"Precipitación Total devuelta en metadatos: {data['metadatos']['precipitacion_total_mm']:.4f} mm")
    else:
        print(f"[ERROR] Error en la petición: Código {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    try:
        verificar_motor_hietogramas()
    except Exception as e:
        print("Error en las pruebas del motor:", e)
        
    try:
        verificar_api_hietogramas()
    except Exception as e:
        print("Error al verificar la API de hietogramas:", e)
