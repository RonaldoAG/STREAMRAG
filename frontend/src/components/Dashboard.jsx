import React, { useState } from 'react';
import FrecuenciaModulo from './FrecuenciaModulo';
import HietogramaModulo from './HietogramaModulo';
import { API_BASE_URL } from '../config.js';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('frecuencias');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex flex-col md:flex-row h-screen bg-slate-50 overflow-hidden font-sans relative">
      {/* Backdrop de Oscurecimiento para Móviles */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-slate-950/60 z-40 md:hidden transition-opacity duration-300"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar de Navegación Lateral (Colapsable en Móviles) */}
      <aside className={`fixed inset-y-0 left-0 w-64 bg-slate-900 text-slate-100 flex flex-col justify-between border-r border-slate-800 shadow-xl z-50 transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0 ${
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div>
          {/* Logo y Encabezado de la Plataforma */}
          <div className="p-6 border-b border-slate-800 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="bg-indigo-500 p-2 rounded-lg text-white shadow-md">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <div>
                <h1 className="font-bold text-lg tracking-wide bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
                  STREAMRAG
                </h1>
                <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider">
                  SaaS Hidrología
                </p>
              </div>
            </div>
            {/* Botón de cerrar sidebar (Solo móvil) */}
            <button 
              className="md:hidden text-slate-400 hover:text-slate-100 p-1"
              onClick={() => setIsSidebarOpen(false)}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Menú de Navegación */}
          <nav className="p-4 space-y-2">
            <button
              onClick={() => {
                setActiveTab('frecuencias');
                setIsSidebarOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeTab === 'frecuencias'
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-100'
              }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              Análisis de Frecuencias
            </button>

            <button
              onClick={() => {
                setActiveTab('hietogramas');
                setIsSidebarOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeTab === 'hietogramas'
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-100'
              }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
              Hietograma de Diseño
            </button>
          </nav>
        </div>

        {/* Footer del Sidebar: Estado del Servidor */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span className="font-medium">API Base URL</span>
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Online
            </span>
          </div>
          <p className="text-[10px] text-slate-600 font-mono mt-1 overflow-x-auto whitespace-nowrap">
            {API_BASE_URL}
          </p>
        </div>
      </aside>

      {/* Contenedor del Contenido Principal */}
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Encabezado Superior de Contexto */}
        <header className="bg-white border-b border-slate-200 py-4 px-6 md:px-8 flex items-center justify-between shadow-sm z-10">
          <div className="flex items-center gap-3">
            {/* Botón de Hamburguesa para Móviles/Tablets */}
            <button 
              className="md:hidden text-slate-600 hover:text-slate-900 p-2 border border-slate-200 rounded-lg bg-slate-50 focus:outline-none"
              onClick={() => setIsSidebarOpen(true)}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <h2 className="text-base md:text-xl font-bold text-slate-800 leading-tight">
                {activeTab === 'frecuencias' ? 'Análisis de Frecuencias' : 'Hietograma de Diseño'}
              </h2>
              <p className="hidden sm:block text-[11px] md:text-xs text-slate-500 mt-0.5">
                {activeTab === 'frecuencias'
                  ? 'Ajuste de distribuciones estadísticas y periodos de retorno.'
                  : 'Generación de tormentas de diseño mediante curvas IDF y el método del bloque alterno.'}
              </p>
            </div>
          </div>
          <div className="text-[10px] md:text-xs text-slate-400 font-medium whitespace-nowrap">
            SaaS Engine v1.0.0
          </div>
        </header>

        {/* Componente del Módulo Activo */}
        <div className="flex-1 overflow-y-auto bg-slate-50 p-4 md:p-8">
          <div className="max-w-7xl mx-auto transition-opacity duration-300">
            {activeTab === 'frecuencias' ? (
              <FrecuenciaModulo apiBaseUrl={API_BASE_URL} />
            ) : (
              <HietogramaModulo apiBaseUrl={API_BASE_URL} />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

