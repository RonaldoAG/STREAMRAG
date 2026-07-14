import numpy as np
from typing import List, Dict, Any

class HietogramaDiseno:
    """
    Clase para la generación de hietogramas de diseño (tormentas de diseño)
    utilizando el Método del Bloque Alterno a partir de curvas IDF.
    """

    def __init__(self, k: float, m: float, C: float, eta: float, T: float):
        """
        Inicializa los coeficientes de la curva IDF y el periodo de retorno.
        Ecuación IDF: I = (k * T^m) / (d + C)^eta
        
        :param k: Coeficiente de escala.
        :param m: Exponente de periodo de retorno.
        :param C: Constante de duración (minutos).
        :param eta: Exponente de duración.
        :param T: Periodo de retorno (años).
        """
        if k <= 0 or m <= 0 or C < 0 or eta <= 0 or T <= 0:
            raise ValueError("Todos los parámetros IDF y el periodo de retorno deben ser positivos.")
            
        self.k = k
        self.m = m
        self.C = C
        self.eta = eta
        self.T = T
        
        # Calcular el numerador constante A(T) = k * T^m
        self.A_T = k * (T ** m)

    def calcular_intensidad_idf(self, duracion_minutos: float) -> float:
        """
        Calcula la intensidad de precipitación para una duración dada usando la ecuación IDF.
        
        :param duracion_minutos: Duración en minutos.
        :return: Intensidad en mm/h.
        """
        if duracion_minutos <= 0:
            raise ValueError("La duración debe ser mayor a cero.")
        return self.A_T / ((duracion_minutos + self.C) ** self.eta)

    def generar_hietograma(self, t_d: int, dt: int, r: float = 0.5) -> Dict[str, Any]:
        """
        Genera el hietograma de diseño usando el Método del Bloque Alterno.
        
        :param t_d: Duración total de la tormenta (minutos).
        :param dt: Paso de tiempo o discretización (minutos).
        :param r: Factor de asimetría de la tormenta (0 < r < 1). Ubicación del pico.
        :return: Diccionario con la serie del hietograma y metadatos del cálculo.
        """
        # Validaciones de entrada
        if t_d <= 0 or dt <= 0:
            raise ValueError("La duración de la tormenta y el paso de tiempo deben ser positivos.")
        if t_d % dt != 0:
            raise ValueError("La duración de la tormenta (t_d) debe ser un múltiplo exacto del paso de tiempo (dt).")
        if not (0 < r < 1):
            raise ValueError("El factor de asimetría 'r' debe estar estrictamente entre 0 y 1 (excluyendo extremos).")

        N = int(t_d / dt)
        
        # 1. Calcular duraciones acumuladas t_i (minutos)
        duraciones = np.arange(dt, t_d + dt, dt, dtype=float)
        
        # 2. Calcular intensidades de lluvia acumuladas (mm/h)
        intensidades_acum = np.array([self.calcular_intensidad_idf(t) for t in duraciones])
        
        # 3. Calcular precipitación acumulada P_i (mm): P_i = I_i * (t_i / 60)
        precip_acum = intensidades_acum * (duraciones / 60.0)
        
        # 4. Calcular precipitación incremental dP_i (mm)
        precip_increm = np.zeros(N)
        precip_increm[0] = precip_acum[0]
        precip_increm[1:] = np.diff(precip_acum)
        
        # Limpieza física (evitar decrementos numéricos si existiesen por aproximación)
        precip_increm = np.clip(precip_increm, 0.0, None)
        
        # 5. Ordenar incrementos de mayor a menor
        sorted_increments = np.sort(precip_increm)[::-1]
        
        # 6. Algoritmo del Bloque Alterno con asimetría 'r'
        hyetograph = np.zeros(N)
        
        # Índice del pico del hietograma
        c = int(np.floor(r * N))
        c = max(0, min(N - 1, c)) # Garantizar que esté en rango
        
        # Colocar el bloque más grande en la posición del pico
        hyetograph[c] = sorted_increments[0]
        
        left = c - 1
        right = c + 1
        
        # Alternar la colocación de bloques alrededor del pico
        for idx in range(1, N):
            val = sorted_increments[idx]
            if idx % 2 == 1:
                # Intenta colocar a la derecha
                if right < N:
                    hyetograph[right] = val
                    right += 1
                else:
                    hyetograph[left] = val
                    left -= 1
            else:
                # Intenta colocar a la izquierda
                if left >= 0:
                    hyetograph[left] = val
                    left -= 1
                else:
                    hyetograph[right] = val
                    right += 1
                    
        # 7. Re-calcular curvas del hietograma generado
        # Altura acumulada final de la tormenta de diseño generada
        precip_acum_generada = np.cumsum(hyetograph)
        
        # Intensidades instantáneas en cada intervalo del hietograma (mm/h)
        intensidades_diseno = hyetograph / (dt / 60.0)
        
        # Estructurar resultados para retorno de API
        intervalos = []
        for i in range(N):
            t_inicio = i * dt
            t_fin = (i + 1) * dt
            intervalos.append({
                "tiempo_inicio": int(t_inicio),
                "tiempo_fin": int(t_fin),
                "precipitacion_incremental": float(hyetograph[i]),
                "precipitacion_acumulada": float(precip_acum_generada[i]),
                "intensidad": float(intensidades_diseno[i])
            })
            
        return {
            "metadatos": {
                "duracion_total_minutos": t_d,
                "paso_tiempo_minutos": dt,
                "num_bloques": N,
                "periodo_retorno_anos": self.T,
                "factor_asimetria_r": r,
                "precipitacion_total_mm": float(precip_acum_generada[-1]),
                "intensidad_pico_mm_h": float(np.max(intensidades_diseno))
            },
            "intervalos": intervalos
        }
