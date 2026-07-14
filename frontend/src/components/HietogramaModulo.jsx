import React, { useState } from 'react';
import Plot from 'react-plotly.js';

export default function HietogramaModulo({ apiBaseUrl }) {
  // Coeficientes IDF por defecto (demostración)
  const [k, setK] = useState(1250.4);
  const [m, setM] = useState(0.28);
  const [C, setC] = useState(15.0);
  const [eta, setEta] = useState(0.72);
  
  // Parámetros de tormenta por defecto (demostración)
  const [T, setT] = useState(10.0);
  const [tD, setTD] = useState(120);
  const [dt, setDt] = useState(10);
  const [r, setR] = useState(0.35); // Asimetría por defecto 0.35 (pico adelantado)

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Validaciones en el cliente
    if (tD <= 0 || dt <= 0) {
      setError("La duración de la tormenta y el paso de tiempo deben ser mayores a cero.");
      setLoading(false);
      return;
    }
    if (tD % dt !== 0) {
      setError(`La duración total de la tormenta (${tD} min) debe ser un múltiplo exacto del paso de tiempo (${dt} min).`);
      setLoading(false);
      return;
    }

    try {
      // Petición POST a la API de Hietogramas
      const response = await fetch(`${apiBaseUrl}/hidrologia/hietograma-diseno`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          k: parseFloat(k),
          m: parseFloat(m),
          C: parseFloat(C),
          eta: parseFloat(eta),
          T: parseFloat(T),
          t_d: parseInt(tD),
          dt: parseInt(dt),
          r: parseFloat(r)
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Error al calcular el hietograma.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "No se pudo conectar con el motor de cálculo en el servidor.");
    } finally {
      setLoading(false);
    }
  };

  // Configurar los datos para el gráfico combinado de Plotly
  const getChartData = () => {
    if (!result) return [];

    const intervalos = result.intervalos;
    const xLabels = intervalos.map(i => `${i.tiempo_inicio}-${i.tiempo_fin}`);
    const yIncremental = intervalos.map(i => i.precipitacion_incremental);
    const yAcumulada = intervalos.map(i => i.precipitacion_acumulada);

    return [
      {
        x: xLabels,
        y: yIncremental,
        type: 'bar',
        name: 'Incremental (mm)',
        marker: { color: '#3b82f6', opacity: 0.7 },
        yaxis: 'y',
        hovertemplate: 'Intervalo: %{x} min<br>Incremental: %{y:.2f} mm<extra></extra>'
      },
      {
        x: xLabels,
        y: yAcumulada,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Acumulada (mm)',
        line: { color: '#ef4444', width: 2.5 },
        marker: { color: '#ef4444', size: 5 },
        yaxis: 'y2',
        hovertemplate: 'Intervalo: %{x} min<br>Acumulada: %{y:.2f} mm<extra></extra>'
      }
    ];
  };

  const chartLayout = {
    title: {
      text: 'Hietograma de Diseño - Método del Bloque Alterno',
      font: { family: 'Inter, sans-serif', size: 16, color: '#1e293b', weight: 'bold' }
    },
    xaxis: {
      title: 'Intervalos de Duración (minutos)',
      gridcolor: '#f1f5f9',
      tickangle: -45
    },
    yaxis: {
      title: 'Precipitación Incremental (mm)',
      titlefont: { color: '#3b82f6' },
      tickfont: { color: '#3b82f6' },
      gridcolor: '#f1f5f9',
      zerolinecolor: '#cbd5e1'
    },
    yaxis2: {
      title: 'Precipitación Acumulada (mm)',
      titlefont: { color: '#ef4444' },
      tickfont: { color: '#ef4444' },
      overlaying: 'y',
      side: 'right',
      zeroline: false,
      gridcolor: 'rgba(0,0,0,0)'
    },
    legend: {
      orientation: 'h',
      y: -0.3,
      x: 0.5,
      xanchor: 'center'
    },
    margin: { l: 50, r: 50, t: 50, b: 90 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    autosize: true,
    hovermode: 'closest'
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Panel Lateral de Parámetros */}
      <div className="bg-slate-900 text-slate-100 p-6 rounded-2xl shadow-xl border border-slate-800 space-y-6">
        <form onSubmit={handleGenerate} className="space-y-5">
          <div>
            <h3 className="text-lg font-bold text-white mb-1">Parámetros IDF y Tormenta</h3>
            <p className="text-xs text-slate-400">Define los coeficientes de la curva de lluvia y los parámetros de diseño pluvial.</p>
          </div>

          {/* Coeficientes IDF de Sherman */}
          <div className="border-t border-slate-800 pt-4 space-y-3">
            <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-wider block">
              1. Coeficientes Curva IDF (Sherman)
            </span>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-[10px] font-semibold text-slate-400 uppercase">Coeficiente k</label>
                <input
                  type="number" step="any" value={k} onChange={(e) => setK(e.target.value)}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-semibold text-slate-400 uppercase">Exponente m</label>
                <input
                  type="number" step="any" value={m} onChange={(e) => setM(e.target.value)}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-semibold text-slate-400 uppercase">Constante C (min)</label>
                <input
                  type="number" step="any" value={C} onChange={(e) => setC(e.target.value)}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-semibold text-slate-400 uppercase">Exponente eta (η)</label>
                <input
                  type="number" step="any" value={eta} onChange={(e) => setEta(e.target.value)}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
                />
              </div>
            </div>
          </div>

          {/* Variables de diseño de la tormenta */}
          <div className="border-t border-slate-800 pt-4 space-y-3">
            <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-wider block">
              2. Parámetros de la Tormenta
            </span>
            <div className="grid grid-cols-3 gap-2">
              <div className="space-y-1">
                <label className="text-[10px] font-semibold text-slate-400 uppercase block">Retorno T (años)</label>
                <input
                  type="number" step="any" value={T} onChange={(e) => setT(e.target.value)}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-center"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-semibold text-slate-400 uppercase block">Duración td (min)</label>
                <input
                  type="number" value={tD} onChange={(e) => setTD(e.target.value)}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-center"
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-semibold text-slate-400 uppercase block">Paso dt (min)</label>
                <input
                  type="number" value={dt} onChange={(e) => setDt(e.target.value)}
                  className="w-full bg-slate-950/60 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-center"
                />
              </div>
            </div>
          </div>

          {/* Slider para el Factor de Asimetría r */}
          <div className="border-t border-slate-800 pt-4 space-y-2">
            <div className="flex justify-between items-center text-xs font-semibold text-slate-300">
              <span className="uppercase tracking-wider">Factor de Asimetría (r)</span>
              <span className="text-indigo-400 font-mono text-sm">{parseFloat(r).toFixed(2)}</span>
            </div>
            <input
              type="range" min="0.1" max="0.9" step="0.05" value={r} onChange={(e) => setR(e.target.value)}
              className="w-full h-1.5 bg-slate-850 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>0.1 (Pico temprano)</span>
              <span>0.5 (Simétrico)</span>
              <span>0.9 (Pico tardío)</span>
            </div>
          </div>

          {/* Botón de Generar */}
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
                Generando Tormenta...
              </span>
            ) : (
              'Generar Tormenta'
            )}
          </button>
        </form>

        {/* Mensaje de Error */}
        {error && (
          <div className="mt-4 p-4 bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded-xl text-xs flex gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 shrink-0 text-rose-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div>
              <span className="font-bold block mb-0.5">Error en Parámetros</span>
              {error}
            </div>
          </div>
        )}
      </div>

      {/* Área de Visualización y Gráfico / Tabla */}
      <div className="lg:col-span-2 space-y-6">
        {!result && !loading && (
          <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center shadow-sm flex flex-col items-center justify-center h-full min-h-[450px]">
            <div className="text-slate-300 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </div>
            <h4 className="text-slate-700 font-bold text-lg">Esperando Configuración de Lluvia</h4>
            <p className="text-sm text-slate-400 max-w-sm mt-1">
              Ajusta los sliders y presiona "Generar Tormenta" para trazar el hietograma por el Método del Bloque Alterno.
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
            <h4 className="text-slate-700 font-semibold">Corriendo Ecuaciones IDF</h4>
            <p className="text-xs text-slate-400 mt-1">Generando hietograma incremental e integrando alturas de precipitación acumulada...</p>
          </div>
        )}

        {result && !loading && (
          <>
            {/* Gráfico Combinado Plotly de Doble Eje Y */}
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <Plot
                data={getChartData()}
                layout={chartLayout}
                useResizeHandler={true}
                style={{ width: '100%', height: '420px' }}
                config={{ responsive: true, displayModeBar: false }}
              />
            </div>

            {/* Metadatos Generados */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm text-center">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Lluvia Total</span>
                <span className="text-xl font-extrabold text-slate-800 block mt-1">
                  {result.metadatos.precipitacion_total_mm.toFixed(2)} mm
                </span>
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm text-center">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Intensidad Pico</span>
                <span className="text-xl font-extrabold text-indigo-600 block mt-1">
                  {result.metadatos.intensidad_pico_mm_h.toFixed(2)} mm/h
                </span>
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm text-center">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">N° Bloques</span>
                <span className="text-xl font-extrabold text-slate-800 block mt-1">
                  {result.metadatos.num_bloques}
                </span>
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm text-center">
                <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Posición del Pico</span>
                <span className="text-xl font-extrabold text-slate-800 block mt-1">
                  {Math.floor(result.metadatos.factor_asimetria_r * 100)}%
                </span>
              </div>
            </div>

            {/* Tabla Detallada de Intervalos */}
            <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100">
                <h4 className="text-slate-800 font-bold text-sm">Bloques Temporales del Hietograma</h4>
                <p className="text-xs text-slate-400 mt-0.5">Precipitaciones acumuladas, incrementales e intensidades de diseño por bloque.</p>
              </div>
              <div className="overflow-y-auto max-h-[350px]">
                <table className="w-full border-collapse text-left text-sm text-slate-500">
                  <thead className="bg-slate-50 text-xs text-slate-700 uppercase font-semibold sticky top-0 shadow-sm">
                    <tr>
                      <th scope="col" className="px-6 py-3">Bloque (min)</th>
                      <th scope="col" className="px-6 py-3">Incremental (mm)</th>
                      <th scope="col" className="px-6 py-3">Acumulada (mm)</th>
                      <th scope="col" className="px-6 py-3 text-right">Intensidad (mm/h)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {result.intervalos.map((item, idx) => {
                      const esPico = item.intensidad === result.metadatos.intensidad_pico_mm_h;
                      return (
                        <tr key={idx} className={`hover:bg-slate-50/50 transition-colors ${esPico ? 'bg-indigo-50/20 hover:bg-indigo-50/30' : ''}`}>
                          <td className={`px-6 py-3 font-medium ${esPico ? 'font-bold text-indigo-700' : 'text-slate-900'}`}>
                            {item.tiempo_inicio} - {item.tiempo_fin}
                            {esPico && <span className="ml-2 inline-flex px-1.5 py-0.5 rounded text-[9px] font-bold bg-indigo-100 text-indigo-800 border border-indigo-200">Pico</span>}
                          </td>
                          <td className={`px-6 py-3 ${esPico ? 'font-semibold text-slate-900' : ''}`}>{item.precipitacion_incremental.toFixed(3)}</td>
                          <td className="px-6 py-3">{item.precipitacion_acumulada.toFixed(3)}</td>
                          <td className="px-6 py-3 text-right font-mono text-xs">{item.intensidad.toFixed(2)}</td>
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
