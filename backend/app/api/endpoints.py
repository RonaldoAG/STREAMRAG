from fastapi import APIRouter, HTTPException, status
from app.core.analisis_frecuencias import AnalisisFrecuencias
from app.core.hietogramas import HietogramaDiseno
from app.schemas import (
    AnalisisFrecuenciaRequest, 
    AnalisisFrecuenciaResponse,
    HietogramaRequest,
    HietogramaResponse
)

router = APIRouter()

@router.post(
    "/analisis-frecuencia", 
    response_model=AnalisisFrecuenciaResponse, 
    status_code=status.HTTP_200_OK,
    summary="Realiza un análisis de frecuencias hidrológicas",
    description="Procesa una serie de precipitaciones máximas anuales para ajustar distribuciones Gumbel y Log-Pearson III, estimando caudales o lluvias de diseño y ejecutando pruebas de bondad de ajuste K-S."
)
def realizar_analisis_frecuencia(payload: AnalisisFrecuenciaRequest):
    try:
        # Inicializar el motor de cálculo con los datos validados del payload
        motor = AnalisisFrecuencias(datos=payload.datos)
        
        # Procesar análisis completo con las opciones seleccionadas
        resultado = motor.procesar_analisis(
            periodos_retorno=payload.periodos_retorno,
            metodo_gumbel=payload.metodo_gumbel
        )
        
        return resultado
        
    except ValueError as ve:
        # Excepciones controladas de datos de entrada inválidos
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error de validación física: {str(ve)}"
        )
    except Exception as e:
        # Excepciones no controladas o fallos numéricos internos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Fallo crítico en el cálculo hidrológico: {str(e)}"
        )


@router.post(
    "/hietograma-diseno", 
    response_model=HietogramaResponse, 
    status_code=status.HTTP_200_OK,
    summary="Genera un hietograma de diseño por el método del bloque alterno",
    description="Calcula la precipitación incremental y acumulada a partir de coeficientes de curvas IDF, ordenándolos alternamente."
)
def generar_hietograma_diseno(payload: HietogramaRequest):
    try:
        # Inicializar motor de hietograma con los parámetros IDF
        motor = HietogramaDiseno(
            k=payload.k,
            m=payload.m,
            C=payload.C,
            eta=payload.eta,
            T=payload.T
        )
        
        # Generar el hietograma con discretización y factor de asimetría
        resultado = motor.generar_hietograma(
            t_d=payload.t_d,
            dt=payload.dt,
            r=payload.r
        )
        
        return resultado
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Error de validación física: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Fallo crítico en el cálculo del hietograma: {str(e)}"
        )

