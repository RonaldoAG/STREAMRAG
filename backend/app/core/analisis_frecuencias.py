import numpy as np
import pandas as pd
import scipy.stats as stats
from typing import List, Dict, Any, Tuple, Union

class AnalisisFrecuencias:
    """
    Clase para el Análisis de Frecuencias de Precipitaciones Máximas Anuales.
    Implementa el ajuste de distribuciones Gumbel (EVD I) y Log-Pearson Tipo III (LP3),
    cálculo de eventos de diseño para periodos de retorno y bondad de ajuste con Kolmogorov-Smirnov.
    """

    def __init__(self, datos: Union[List[float], np.ndarray, pd.Series]):
        """
        Inicializa el motor de cálculo con la serie de datos de precipitación máxima anual.
        
        :param datos: Serie temporal o lista de precipitaciones máximas anuales en mm.
        """
        # Convertir a array de numpy y limpiar valores nulos o no válidos
        self.datos = np.array(datos, dtype=float)
        self.datos = self.datos[~np.isnan(self.datos)]
        
        # Validaciones de integridad física de los datos
        if len(self.datos) < 5:
            raise ValueError("Se requieren al menos 5 años de datos para realizar un análisis de frecuencia confiable.")
        if np.any(self.datos <= 0):
            raise ValueError("Los datos de precipitación máxima anual deben ser estrictamente mayores a cero (valores positivos).")
            
        self.n = len(self.datos)
        
    def ajustar_gumbel(self, metodo: str = "momentos") -> Dict[str, Any]:
        """
        Ajusta los datos a una distribución Gumbel (EVD Tipo I).
        
        :param metodo: Método de ajuste, puede ser 'momentos' o 'mle'.
        :return: Diccionario con parámetros y métricas de ajuste.
        """
        metodo = metodo.lower()
        if metodo == "momentos":
            # Método de Momentos Clásico
            media = np.mean(self.datos)
            std_dev = np.std(self.datos, ddof=1)
            
            # Constante de Euler-Mascheroni
            euler_constant = 0.57721566490153286
            
            # beta = std_dev * sqrt(6) / pi
            beta = (std_dev * np.sqrt(6)) / np.pi
            # mu = media - euler * beta
            mu = media - (euler_constant * beta)
        elif metodo == "mle":
            # Ajuste por Máxima Verosimilitud usando scipy
            mu, beta = stats.gumbel_r.fit(self.datos)
        else:
            raise ValueError("Método de ajuste Gumbel no válido. Use 'momentos' o 'mle'.")
            
        # Prueba de bondad de ajuste Kolmogorov-Smirnov (K-S)
        ks_res = stats.kstest(self.datos, 'gumbel_r', args=(mu, beta))
        
        return {
            "mu": float(mu),
            "beta": float(beta),
            "ks_statistic": float(ks_res.statistic),
            "ks_p_value": float(ks_res.pvalue),
            "metodo": metodo
        }
        
    def ajustar_log_pearson3(self) -> Dict[str, Any]:
        """
        Ajusta los datos a una distribución Log-Pearson Tipo III (LP3).
        Aplica transformación logarítmica decimal (log10) y ajusta por momentos con sesgo.
        
        :return: Diccionario con parámetros y métricas de ajuste.
        """
        # Transformación logarítmica decimal (estándar en hidrología Bulletin 17B/17C)
        datos_log = np.log10(self.datos)
        
        # Parámetros por método de momentos en espacio logarítmico
        media_log = np.mean(datos_log)
        std_log = np.std(datos_log, ddof=1)
        
        # Coeficiente de asimetría corregido por sesgo de muestra
        skew_log = stats.skew(datos_log, bias=False)
        
        # Manejo de sesgo cercano a cero para evitar inestabilidad en pearson3
        if abs(skew_log) < 1e-6:
            skew_log = 1e-6
            
        # En scipy, la distribución pearson3 toma (skew, loc, scale)
        # donde loc es la media y scale la desviación estándar
        # Prueba K-S en el espacio logarítmico transformado
        ks_res = stats.kstest(datos_log, 'pearson3', args=(skew_log, media_log, std_log))
        
        return {
            "skew_log": float(skew_log),
            "mean_log": float(media_log),
            "std_log": float(std_log),
            "ks_statistic": float(ks_res.statistic),
            "ks_p_value": float(ks_res.pvalue)
        }
        
    def calcular_evento_diseno_gumbel(self, mu: float, beta: float, periodos_retorno: List[float]) -> Dict[float, float]:
        """
        Calcula la precipitación de diseño para periodos de retorno bajo la distribución Gumbel.
        
        :param mu: Parámetro de ubicación.
        :param beta: Parámetro de escala.
        :param periodos_retorno: Lista de periodos de retorno en años (T).
        :return: Diccionario con {T: precipitación_diseño}.
        """
        resultados = {}
        for T in periodos_retorno:
            # Probabilidad de no excedencia p = 1 - 1/T
            p = 1.0 - (1.0 / T)
            # Cuantil usando scipy
            x_t = stats.gumbel_r.ppf(p, loc=mu, scale=beta)
            resultados[T] = float(x_t)
        return resultados

    def calcular_evento_diseno_log_pearson3(self, skew_log: float, mean_log: float, std_log: float, periodos_retorno: List[float]) -> Dict[float, float]:
        """
        Calcula la precipitación de diseño para periodos de retorno bajo la distribución Log-Pearson III.
        
        :param skew_log: Coeficiente de asimetría en log-space.
        :param mean_log: Media en log-space.
        :param std_log: Desviación estándar en log-space.
        :param periodos_retorno: Lista de periodos de retorno en años (T).
        :return: Diccionario con {T: precipitación_diseño}.
        """
        resultados = {}
        for T in periodos_retorno:
            # Probabilidad de no excedencia p = 1 - 1/T
            p = 1.0 - (1.0 / T)
            # Cuantil en log-space usando scipy
            y_t = stats.pearson3.ppf(p, skew_log, loc=mean_log, scale=std_log)
            # Transformación inversa a espacio lineal
            x_t = 10 ** y_t
            resultados[T] = float(x_t)
        return resultados

    def obtener_puntos_empiricos(self) -> List[Dict[str, float]]:
        """
        Calcula los puntos empíricos utilizando la posición de graficación de Weibull,
        ideal para graficar datos históricos vs curvas teóricas.
        
        :return: Lista de diccionarios ordenados con los datos, probabilidad acumulada y periodo de retorno empírico.
        """
        datos_ordenados = np.sort(self.datos)
        puntos = []
        n = len(datos_ordenados)
        
        for idx, x in enumerate(datos_ordenados):
            # Rango 1-indexed (m)
            m = idx + 1
            # Probabilidad acumulada (CDF empírica) usando Weibull: F(x) = m / (n + 1)
            f_emp = m / (n + 1)
            # Probabilidad de excedencia p_exc = 1 - F(x) = (n + 1 - m) / (n + 1)
            p_exc = 1.0 - f_emp
            # Periodo de retorno empírico T = 1 / p_exc
            t_emp = 1.0 / p_exc if p_exc > 0 else float('inf')
            
            puntos.append({
                "valor": float(x),
                "cdf_empirica": float(f_emp),
                "periodo_retorno_empirico": float(t_emp)
            })
            
        return puntos

    def generar_curvas_teoricas(self, 
                                 params_gumbel: Dict[str, Any], 
                                 params_lp3: Dict[str, Any], 
                                 x_max_limit: float,
                                 n_points: int = 150) -> Dict[str, Any]:
        """
        Genera una secuencia de puntos continuos para trazar las curvas PDF y CDF teóricas.
        
        :param params_gumbel: Parámetros estimados de Gumbel.
        :param params_lp3: Parámetros estimados de LP3.
        :param x_max_limit: Valor máximo de x para graficar (usualmente el evento de T=500).
        :param n_points: Número de puntos a generar.
        :return: Diccionario con curvas teóricas de Gumbel y LP3.
        """
        # Definir rango dinámico para el eje X
        x_min = max(0.1, np.min(self.datos) * 0.5)
        x_max = x_max_limit * 1.15
        
        x_vals = np.linspace(x_min, x_max, n_points)
        
        # Curva Gumbel
        gumbel_cdf = stats.gumbel_r.cdf(x_vals, loc=params_gumbel["mu"], scale=params_gumbel["beta"])
        gumbel_pdf = stats.gumbel_r.pdf(x_vals, loc=params_gumbel["mu"], scale=params_gumbel["beta"])
        
        # Curva LP3
        # Para LP3 calculamos sobre el espacio logarítmico y luego ajustamos PDF por cambio de variables
        y_vals = np.log10(x_vals)
        lp3_cdf = stats.pearson3.cdf(y_vals, params_lp3["skew_log"], loc=params_lp3["mean_log"], scale=params_lp3["std_log"])
        
        # PDF en espacio lineal: f_X(x) = f_Y(log10(x)) / (x * ln(10))
        lp3_pdf_y = stats.pearson3.pdf(y_vals, params_lp3["skew_log"], loc=params_lp3["mean_log"], scale=params_lp3["std_log"])
        lp3_pdf = lp3_pdf_y / (x_vals * np.log(10.0))
        
        return {
            "x": x_vals.tolist(),
            "gumbel": {
                "cdf": gumbel_cdf.tolist(),
                "pdf": gumbel_pdf.tolist()
            },
            "log_pearson3": {
                "cdf": lp3_cdf.tolist(),
                "pdf": lp3_pdf.tolist()
            }
        }

    def procesar_analisis(self, 
                         periodos_retorno: List[float] = [2, 5, 10, 25, 50, 100, 500],
                         metodo_gumbel: str = "momentos") -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo de análisis de frecuencias: ajustes, eventos de diseño,
        prueba K-S, selección del mejor modelo y generación de curvas para gráficos.
        
        :param periodos_retorno: Periodos de retorno de interés.
        :param metodo_gumbel: 'momentos' o 'mle' para el ajuste de Gumbel.
        :return: Resultados estructurados para salida de la API.
        """
        # 1. Ajustar distribuciones
        gumbel_fit = self.ajustar_gumbel(metodo=metodo_gumbel)
        lp3_fit = self.ajustar_log_pearson3()
        
        # 2. Calcular eventos de diseño
        disenos_gumbel = self.calcular_evento_diseno_gumbel(
            gumbel_fit["mu"], gumbel_fit["beta"], periodos_retorno
        )
        disenos_lp3 = self.calcular_evento_diseno_log_pearson3(
            lp3_fit["skew_log"], lp3_fit["mean_log"], lp3_fit["std_log"], periodos_retorno
        )
        
        # 3. Determinar mejor ajuste por K-S (menor estadístico D)
        d_gumbel = gumbel_fit["ks_statistic"]
        d_lp3 = lp3_fit["ks_statistic"]
        
        distribucion_recomendada = "Log-Pearson Tipo III" if d_lp3 < d_gumbel else "Gumbel"
        
        # 4. Obtener puntos de graficación empíricos
        puntos_empiricos = self.obtener_puntos_empiricos()
        
        # 5. Generar curvas continuas teóricas
        # Usamos el diseño máximo como límite para que la curva muestre toda la extrapolación
        x_max_limit = max(max(disenos_gumbel.values()), max(disenos_lp3.values()))
        curvas_teoricas = self.generar_curvas_teoricas(gumbel_fit, lp3_fit, x_max_limit)
        
        # Estructurar eventos de diseño como lista de objetos para simplificar consumo en React
        eventos_diseno = []
        for T in periodos_retorno:
            eventos_diseno.append({
                "periodo_retorno": T,
                "gumbel": disenos_gumbel[T],
                "log_pearson3": disenos_lp3[T]
            })
            
        return {
            "resumen": {
                "num_observaciones": self.n,
                "media": float(np.mean(self.datos)),
                "desviacion_estandar": float(np.std(self.datos, ddof=1)),
                "distribucion_recomendada": distribucion_recomendada,
                "metodo_gumbel": metodo_gumbel
            },
            "gumbel": gumbel_fit,
            "log_pearson3": lp3_fit,
            "eventos_diseno": eventos_diseno,
            "puntos_empiricos": puntos_empiricos,
            "curvas_teoricas": curvas_teoricas
        }
