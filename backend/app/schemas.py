from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class AnalisisFrecuenciaRequest(BaseModel):
    """
    Modelo de entrada para la solicitud de análisis de frecuencia.
    """
    datos: List[float] = Field(
        ..., 
        description="Lista de precipitaciones máximas anuales en milímetros (mm). Debe contener al menos 5 registros.",
        min_items=5,
        examples=[[45.2, 58.7, 72.1, 39.8, 62.4, 88.0, 51.3, 44.5, 68.9, 59.2]]
    )
    metodo_gumbel: Optional[str] = Field(
        "momentos", 
        description="Método de estimación de parámetros para Gumbel. Opciones: 'momentos' o 'mle' (máxima verosimilitud).",
        examples=["momentos", "mle"]
    )
    periodos_retorno: Optional[List[float]] = Field(
        [2, 5, 10, 25, 50, 100, 500], 
        description="Lista de periodos de retorno (T) en años para calcular eventos de diseño."
    )

    @field_validator("datos")
    def validar_datos_precipitacion(cls, v):
        if len(v) < 5:
            raise ValueError("Se requieren al menos 5 datos de precipitación.")
        if any(x <= 0 for x in v):
            raise ValueError("Todos los valores de precipitación deben ser estrictamente positivos (mayores a cero).")
        return v

    @field_validator("metodo_gumbel")
    def validar_metodo_gumbel(cls, v):
        if v.lower() not in ["momentos", "mle"]:
            raise ValueError("El método Gumbel debe ser 'momentos' o 'mle'.")
        return v.lower()


class ResumenResult(BaseModel):
    num_observaciones: int = Field(..., description="Número de años de registros analizados.")
    media: float = Field(..., description="Media aritmética de la muestra (mm).")
    desviacion_estandar: float = Field(..., description="Desviación estándar muestral (mm).")
    distribucion_recomendada: str = Field(..., description="Distribución recomendada basada en el menor estadístico K-S.")
    metodo_gumbel: str = Field(..., description="Método utilizado para ajustar Gumbel.")


class GumbelParameters(BaseModel):
    mu: float = Field(..., description="Parámetro de ubicación (loc) de Gumbel.")
    beta: float = Field(..., description="Parámetro de escala (scale) de Gumbel.")
    ks_statistic: float = Field(..., description="Estadístico de prueba D de Kolmogorov-Smirnov.")
    ks_p_value: float = Field(..., description="p-valor de la prueba Kolmogorov-Smirnov.")
    metodo: str = Field(..., description="Método de ajuste empleado.")


class LogPearson3Parameters(BaseModel):
    skew_log: float = Field(..., description="Coeficiente de asimetría corregido por sesgo de los logaritmos.")
    mean_log: float = Field(..., description="Media de los logaritmos.")
    std_log: float = Field(..., description="Desviación estándar de los logaritmos.")
    ks_statistic: float = Field(..., description="Estadístico de prueba D de Kolmogorov-Smirnov en espacio logarítmico.")
    ks_p_value: float = Field(..., description="p-valor de la prueba Kolmogorov-Smirnov.")


class EventoDiseno(BaseModel):
    periodo_retorno: float = Field(..., description="Periodo de retorno T en años.")
    gumbel: float = Field(..., description="Precipitación de diseño estimada por Gumbel (mm).")
    log_pearson3: float = Field(..., description="Precipitación de diseño estimada por Log-Pearson III (mm).")


class PuntoEmpirico(BaseModel):
    valor: float = Field(..., description="Valor de precipitación histórico observado (mm).")
    cdf_empirica: float = Field(..., description="Probabilidad acumulada empírica F(x) calculada con Weibull.")
    periodo_retorno_empirico: float = Field(..., description="Periodo de retorno empírico estimado (años).")


class CurvaDistribucion(BaseModel):
    cdf: List[float] = Field(..., description="Valores continuos de la función de distribución acumulada (CDF) teórica.")
    pdf: List[float] = Field(..., description="Valores continuos de la función de densidad de probabilidad (PDF) teórica.")


class CurvasTeoricas(BaseModel):
    x: List[float] = Field(..., description="Valores de precipitación (mm) generados secuencialmente para el eje X del gráfico.")
    gumbel: CurvaDistribucion = Field(..., description="Curva continua teórica de Gumbel.")
    log_pearson3: CurvaDistribucion = Field(..., description="Curva continua teórica de Log-Pearson Tipo III.")


class AnalisisFrecuenciaResponse(BaseModel):
    """
    Modelo de respuesta estructurado para la API.
    Consumible de forma directa por Plotly.js en el frontend.
    """
    resumen: ResumenResult
    gumbel: GumbelParameters
    log_pearson3: LogPearson3Parameters
    eventos_diseno: List[EventoDiseno]
    puntos_empiricos: List[PuntoEmpirico]
    curvas_teoricas: CurvasTeoricas


class HietogramaRequest(BaseModel):
    """
    Modelo de entrada para la generación de hietogramas de diseño mediante curvas IDF.
    """
    k: float = Field(..., gt=0, description="Coeficiente de escala k de la curva IDF.", examples=[1250.4])
    m: float = Field(..., gt=0, description="Exponente m de periodo de retorno de la curva IDF.", examples=[0.28])
    C: float = Field(..., ge=0, description="Constante de duración C (minutos) de la curva IDF.", examples=[15.0])
    eta: float = Field(..., gt=0, description="Exponente de duración eta de la curva IDF.", examples=[0.72])
    T: float = Field(..., gt=0, description="Periodo de retorno T en años.", examples=[10.0])
    t_d: int = Field(..., gt=0, description="Duración total de la tormenta en minutos.", examples=[120])
    dt: int = Field(..., gt=0, description="Paso de tiempo o discretización (minutos).", examples=[10])
    r: Optional[float] = Field(0.5, gt=0, lt=1, description="Factor de asimetría de la tormenta r (0 < r < 1). Ubicación del pico.", examples=[0.35])

    @field_validator("t_d")
    def validar_multiplo_paso(cls, t_d, info):
        # Para validar dt, necesitamos extraerlo del diccionario de valores
        dt = info.data.get("dt")
        if dt is not None and t_d % dt != 0:
            raise ValueError("La duración total de la tormenta (t_d) debe ser un múltiplo exacto del paso de tiempo (dt).")
        return t_d


class HietogramaIntervalo(BaseModel):
    tiempo_inicio: int = Field(..., description="Inicio del intervalo de tiempo (minutos).")
    tiempo_fin: int = Field(..., description="Fin del intervalo de tiempo (minutos).")
    precipitacion_incremental: float = Field(..., description="Precipitación caída en el intervalo (mm).")
    precipitacion_acumulada: float = Field(..., description="Precipitación acumulada total hasta el intervalo (mm).")
    intensidad: float = Field(..., description="Intensidad equivalente de lluvia para el intervalo (mm/h).")


class HietogramaMetadatos(BaseModel):
    duracion_total_minutos: int = Field(..., description="Duración total de la tormenta simulada (minutos).")
    paso_tiempo_minutos: int = Field(..., description="Paso de tiempo de discretización (minutos).")
    num_bloques: int = Field(..., description="Número de bloques temporales generados.")
    periodo_retorno_anos: float = Field(..., description="Periodo de retorno considerado (años).")
    factor_asimetria_r: float = Field(..., description="Factor de asimetría del pico empleado.")
    precipitacion_total_mm: float = Field(..., description="Lluvia total de diseño acumulada (mm).")
    intensidad_pico_mm_h: float = Field(..., description="Intensidad máxima registrada en el hietograma (mm/h).")


class HietogramaResponse(BaseModel):
    """
    Modelo de respuesta estructurado para la API de hietogramas de diseño.
    """
    metadatos: HietogramaMetadatos
    intervalos: List[HietogramaIntervalo]

