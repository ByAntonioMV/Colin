import { obtenerDatosDesdeAPI } from '../../Public/Js/AdministrarCorpusFunciones.js';

// Variables globales para las instancias de ECharts
let posDonutChart = null;
let verbsBarChart = null;
let posBarRotationChart = null;

/**
 * Función que dispara la carga inicial cuando el DOM está listo
 */
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const hashCorpus = urlParams.get('hash');

    if (hashCorpus) {
        console.log("Iniciando carga de estadísticas para:", hashCorpus);
        inicializarEstadisticas(hashCorpus);
    } else {
        console.warn("No se encontró el parámetro 'hash' en la URL. Las gráficas no se cargarán.");
    }
});

/**
 * Función principal para cargar datos y renderizar con ECharts
 */
export async function inicializarEstadisticas(hashCorpus) {
    if (!hashCorpus || hashCorpus === "undefined") return;

    try {
        const data = await obtenerDatosDesdeAPI(hashCorpus);

        if (data) {
            
            actualizarKPIs(data.kpis);

            renderDonutPOS(data.pos);
            renderBarVerbos(data.top_verbos);
            renderBarRotationPOS(data.pos);

            const statsPanel = document.getElementById('stats');
            if (statsPanel) {
                const resizeObserver = new ResizeObserver(() => {
                    // Forzamos a ECharts a recalcular su tamaño
                    if (posDonutChart) posDonutChart.resize();
                    if (verbsBarChart) verbsBarChart.resize();
                    if (posBarRotationChart) posBarRotationChart.resize();
                });

                // Empezamos a observar el panel
                resizeObserver.observe(statsPanel);
            }

            // Mantenemos también el del window por si el usuario redimensiona el navegador
            window.addEventListener('resize', () => {
                if (posDonutChart) posDonutChart.resize();
                if (verbsBarChart) verbsBarChart.resize();
                if (posBarRotationChart) posBarRotationChart.resize();
            });

        } else {
            console.error("No se recibieron datos de la API para el hash proporcionado.");
        }
    } catch (error) {
        console.error("Error crítico al inicializar estadísticas:", error);
    }
}

// --- FUNCIONES DE RENDERIZADO (Se mantienen igual, solo añadimos validación de existencia) ---

function actualizarKPIs(kpis) {
    const cards = document.querySelectorAll('#stats .kpi-value');
    if (cards.length >= 4 && kpis) {
        cards[0].innerText = kpis["Total Tokens"]?.toLocaleString() || "0";
        cards[1].innerText = kpis["Total Tipos (Palabras unicas)"]?.toLocaleString() || "0";
        cards[2].innerText = kpis["Total Lemas Unicos"]?.toLocaleString() || "0";
        cards[3].innerHTML = `${kpis["Longitud Promedio de Palabra"] || 0} <small>letras</small>`;
    }
}

function renderDonutPOS(posData) {
    const chartDom = document.getElementById('posDonutChart');
    if (!chartDom || !posData) return;

    if (posDonutChart) echarts.dispose(chartDom);
    posDonutChart = echarts.init(chartDom);

    const option = {
        color: ['#8B2E16', '#2D5A3D', '#D9A05B', '#1A0F0A', '#3b5998', '#A8DADC'],
        tooltip: { trigger: 'item' },
        legend: { bottom: '0%', left: 'center', textStyle: { fontSize: 10 } },
        series: [{
            name: 'Categoría',
            type: 'pie',
            radius: ['40%', '70%'],
            itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
            label: { show: false },
            data: posData.labels.map((l, i) => ({ name: l, value: posData.values[i] }))
        }]
    };
    posDonutChart.setOption(option);
}

function renderBarVerbos(verbData) {
    const chartDom = document.getElementById('verbsBarChart');
    if (!chartDom || !verbData) return;

    if (verbsBarChart) echarts.dispose(chartDom);
    verbsBarChart = echarts.init(chartDom);

    const option = {
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value' },
        yAxis: { type: 'category', data: verbData.labels, inverse: true },
        series: [{
            name: 'Frecuencia',
            type: 'bar',
            data: verbData.values,
            itemStyle: { color: '#8B2E16', borderRadius: [0, 5, 5, 0] }
        }]
    };
    verbsBarChart.setOption(option);
}

function renderBarRotationPOS(posData) {
    const chartDom = document.getElementById('posBarRotationChart');
    if (!chartDom || !posData) return;

    if (posBarRotationChart) echarts.dispose(chartDom);
    posBarRotationChart = echarts.init(chartDom);

    const option = {
        tooltip: { trigger: 'axis' },
        grid: { bottom: '20%', left: '5%', right: '5%' },
        xAxis: {
            type: 'category',
            data: posData.labels,
            axisLabel: { rotate: 45, interval: 0 }
        },
        yAxis: { type: 'value' },
        series: [{
            name: 'Frecuencia',
            type: 'bar',
            data: posData.values,
            itemStyle: { color: '#2D5A3D', borderRadius: [5, 5, 0, 0] }
        }]
    };
    posBarRotationChart.setOption(option);
}