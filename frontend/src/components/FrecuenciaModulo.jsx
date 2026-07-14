import React, { useState } from 'react';
import Plot from 'react-plotly.js';

// Datos de demostración listos para que el usuario pruebe de inmediato
const DEFAULT_DATOS = "54.2, 68.5, 47.9, 88.3, 61.0, 72.4, 50.1, 95.6, 42.8, 59.3, 78.1, 65.2, 53.0, 49.7, 83.4, 102.1, 57.6, 66.8, 44.9, 75.0, 60.3, 51.5, 91.2, 70.8, 58.7";

export default function FrecuenciaModulo({ apiBaseUrl }) {
  const [datosStr, setDatosStr] = useState(DEFAULT_DATOS);
  const [metodoGumbel, setMetodoGumbel] = useState('momentos');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleExecute = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // 1. Parsear y limpiar datos del textarea
    const datosArray = datosStr
      .split(',')
      .map(v => parseFloat(v.trim()))
      .filter(v => !isNaN(v));

    // 2. Validaciones básicas en el cliente para evitar peticiones inútiles
    if (datosArray.length < 5) {
      setError("Se requieren al menos 5 datos numéricos válidos separados por comas.");
      setLoading(false);
      return;
    }
    if (datosArray.some(v => v <= 0)) {
      setError("Todos los valores de precipitación deben ser mayores a cero.");
      setLoading(false);
      return;
    }

    try {
      // 3. Petición POST asíncrona a la API
      const response = await fetch(`${apiBaseUrl}/hidrologia/analisis-frecuencia`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          datos: datosArray,
          metodo_gumbel: metodoGumbel,
          periodos_retorno: [2, 5, 10, 25, 50, 100, 500]
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Error en el cálculo del servidor.");
      }

      // 4. Guardar resultados
      setResult(data);
    } catch (err) {
      setError(err.message || "No se pudo conectar con el motor de cálculo en el servidor.");
    } finally {
      setLoading(false);
    }
  };

  // Configuración del gráfico interactivo de Plotly
  const getChartData = () => {
    if (!result) return [];

    const xTeorico = result.curvas_teoricas.x;
    const gumbelCdf = result.curvas_teoricas.gumbel.cdf;
    const lp3Cdf = result.curvas_teoricas.log_pearson3.cdf;

    const xEmpirico = result.puntos_empiricos.map(p => p.valor);
    const yEmpirico = result.puntos_empiricos.map(p => p.cdf_empirica);

    return [
      {
        x: xEmpirico,
        y: yEmpirico,
        mode: 'markers',
        type: 'scatter',
        name: 'Datos Históricos (Weibull)',
        marker: { color: '#0f172a', size: 8, line: { color: '#ffffff', width: 1 } },
        hovertemplate: 'Precipitación: %{x:.2f} mm<br>Prob. Acumulada: %{y:.3%}<extra></extra>'
      },
      {
        x: xTeorico,
        y: gumbelCdf,
        mode: 'lines',
        type: 'scatter',
        name: 'Curva Gumbel Teórica',
        line: { color: '#2563eb', width: 2.5 },
        hovertemplate: 'Gumbel: %{x:.2f} mm<br>F(x): %{y:.3%}<extra></extra>'
      },
      {
        x: xTeorico,
        y: lp3Cdf,
        mode: 'lines',
        type: 'scatter',
        name: 'Curva Log-Pearson III',
        line: { color: '#10b981', width: 2.5, dash: 'dash' },
        hovertemplate: 'LP3: %{x:.2f} mm<br>F(x): %{y:.3%}<extra></extra>'
      }
    ];
  };

  const chartLayout = {
    title: {
      text: 'Función de Distribución Acumulada (CDF)',
      font: { family: 'Inter, sans-serif', size: 16, color: '#1e293b', weight: 'bold' }
    },
    xaxis: {
      title: 'Precipitación Máxima Anual (mm)',
      gridcolor: '#f1f5f9',
      zerolinecolor: '#cbd5e1'
    },
    yaxis: {
      title: 'Probabilidad de no excedencia F(x)',
      gridcolor: '#f1f5f9',
      zerolinecolor: '#cbd5e1',
      range: [0, 1.05]
    },
    legend: {
      orientation: 'h',
      y: -0.2,
      x: 0.5,
      xanchor: 'center'
    },
    margin: { l: 60, r: 20, t: 50, b: 60 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    autosize: true,
    hovermode: 'closest'
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Panel Lateral de Entrada de Datos */}
      <div className="bg-slate-900 text-slate-100 p-6 rounded-2xl shadow-xl flex flex-col justify-between border border-slate-800">
        <form onSubmit={handleExecute} className="space-y-6">
          <div>
            <h3 className="text-lg font-bold text-white mb-1">Configuración del Ajuste</h3>
            <p className="text-xs text-slate-400">Ingresa tus registros de lluvias anuales e inicia el ajuste estadístico.</p>
          </div>

          {/* Textarea de datos */}
          <div className="space-y-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
              Precipitaciones Máximas Anuales (mm)
            </label>
            <textarea
              value={datosStr}
              onChange={(e) => setDatosStr(e.target.value)}
              className="w-full h-40 bg-slate-950/60 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-mono transition-all"
              placeholder="Ej. 45.2, 58.7, 72.1..."
            />
            <span className="text-[10px] text-slate-500 block">
              Separa los valores anuales estrictamente por comas.
            </span>
          </div>

          {/* Selector de Método Gumbel */}
          <div className="space-y-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
              Método de Ajuste (Gumbel)
            </label>
            <select
              value={metodoGumbel}
              onChange={(e) => setMetodoGumbel(e.target.value)}
              className="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            >
              <option value="momentos">Método de Momentos (Mom)</option>
              <option value="mle">Máxima Verosimilitud (MLE)</option>
            </select>
          </div>

          {/* Botón de Ejecutar */}
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3.5 rounded-xl font-semibold text-sm transition-all duration-200 shadow-md ${
              loading
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-500 text-white hover:shadow-indigo-600/20 active:scale-95'
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5 text-indigo-400" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Procesando Ajuste...
              </span>
            ) : (
              'Ejecutar Análisis'
            )}
          </button>
        </form>

        {/* Mensaje de Error */}
        {error && (
          <div className="mt-6 p-4 bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded-xl text-xs flex gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 shrink-0 text-rose-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div>
              <span className="font-bold block mb-0.5">Error en los datos</span>
              {error}
            </div>
          </div>
        )}
      </div>

      {/* Panel de Visualización y Resultados */}
      <div className="lg:col-span-2 space-y-6">
        {!result && !loading && (
          <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center shadow-sm flex flex-col items-center justify-center h-full min-h-[450px]">
            <div className="text-slate-300 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h4 className="text-slate-700 font-bold text-lg">Esperando Entrada de Datos</h4>
            <p className="text-sm text-slate-400 max-w-sm mt-1">
              Modifica la serie anual en el panel izquierdo y haz clic en "Ejecutar Análisis" para graficar y calibrar las curvas.
            </p>
          </div>
        )}

        {loading && (
          <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center shadow-sm flex flex-col items-center justify-center h-full min-h-[450px]">
            <div className="flex gap-1.5 justify-center items-center mb-4">
              <div className="w-3 h-3 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-3 h-3 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-3 h-3 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
            </div>
            <h4 className="text-slate-700 font-semibold">Ejecutando Modelos en la Nube</h4>
            <p className="text-xs text-slate-400 mt-1">Resolviendo parámetros estadísticas y bondad de ajuste K-S...</p>
          </div>
        )}

        {result && !loading && (
          <>
            {/* Gráfico CDF de Plotly */}
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <Plot
                data={getChartData()}
                layout={chartLayout}
                useResizeHandler={true}
                style={{ width: '100%', height: '420px' }}
                config={{ responsive: true, displayModeBar: false }}
              />
            </div>

            {/* Tarjeta de Distribución Recomendada */}
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
              <div className="md:col-span-2">
                <span className="text-[10px] text-indigo-600 font-bold uppercase tracking-wider block mb-1">
                  Evaluación de Ajuste (K-S)
                </span>
                <h4 className="text-slate-800 font-bold text-lg flex items-center gap-2">
                  Modelo Sugerido: <span className="text-indigo-600">{result.resumen.distribucion_recomendada}</span>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                    Mejor Ajuste
                  </span>
                </h4>
                <p className="text-xs text-slate-500 mt-1">
                  El sistema determinó de forma automatizada que {result.resumen.distribucion_recomendada} minimiza el estadístico de distancia de Kolmogorov-Smirnov.
                </p>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex flex-col justify-center">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                  Estadístico KS (D)
                </span>
                <span className="text-2xl font-extrabold text-slate-800 mt-0.5">
                  {result.resumen.distribucion_recomendada === 'Gumbel' 
                    ? result.gumbel.ks_statistic.toFixed(4)
                    : result.log_pearson3.ks_statistic.toFixed(4)}
                </span>
                <span className="text-[10px] text-slate-500 font-medium">
                  p-valor: {result.resumen.distribucion_recomendada === 'Gumbel' 
                    ? result.gumbel.ks_p_value.toFixed(4)
                    : result.log_pearson3.ks_p_value.toFixed(4)}
                </span>
              </div>
            </div>

            {/* Tabla Comparativa de Eventos de Diseño XT */}
            <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100">
                <h4 className="text-slate-800 font-bold text-sm">Precipitaciones de Diseño Comparativas (mm)</h4>
                <p className="text-xs text-slate-400 mt-0.5">Eventos extremos estimadas para distintos Periodos de Retorno (T).</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-left text-sm text-slate-500">
                  <thead className="bg-slate-50 text-xs text-slate-700 uppercase font-semibold">
                    <tr>
                      <th scope="col" className="px-6 py-3">Periodo de Retorno T (años)</th>
                      <th scope="col" className="px-6 py-3">Distribución Gumbel (mm)</th>
                      <th scope="col" className="px-6 py-3">Log-Pearson Tipo III (mm)</th>
                      <th scope="col" className="px-6 py-3 text-right">Variación (%)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {result.eventos_diseno.map((ev) => {
                      const diferencia = Math.abs(ev.gumbel - ev.log_pearson3);
                      const promedio = (ev.gumbel + ev.log_pearson3) / 2.0;
                      const varPorcentaje = (diferencia / promedio) * 100;
                      
                      return (
                        <tr key={ev.periodo_retorno} className="hover:bg-slate-50/50 transition-colors">
                          <td className="px-6 py-3.5 font-bold text-slate-900">{ev.periodo_retorno}</td>
                          <td className="px-6 py-3.5 font-medium">{ev.gumbel.toFixed(2)}</td>
                          <td className="px-6 py-3.5 font-medium">{ev.log_pearson3.toFixed(2)}</td>
                          <td className="px-6 py-3.5 text-right font-mono text-xs text-slate-400">
                            {varPorcentaje.toFixed(2)}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
