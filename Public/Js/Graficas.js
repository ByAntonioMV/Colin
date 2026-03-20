// Variables globales para guardar las instancias de las gráficas
let posChart = null;
let verbsChart = null;
let lengthChart = null;

// Función principal para cargar y dibujar los datos
async function cargarDatosGraficas() {
    // 1. Obtener el hash de la carpeta actual desde la URL
    const parametrosURL = new URLSearchParams(window.location.search);
    const hashCorpus = parametrosURL.get('hash');

    if (!hashCorpus) {
        console.warn("No hay hash en la URL para cargar estadísticas.");
        return;
    }

    try {
        // 2. Hacer la petición a tu backend FastAPI
        const response = await fetch(`/api/corpus/graficas/${hashCorpus}`);
        const result = await response.json();

        if (result.status === 'success') {
            const data = result.data;

            // 3. ACTUALIZAR LAS TARJETAS KPI (Indicadores clave)
            const kpiValues = document.querySelectorAll('#stats .kpi-value');
            if (kpiValues.length >= 4) {
                kpiValues[0].innerText = data.kpis["Total Tokens"]?.toLocaleString() || "0";
                kpiValues[1].innerText = data.kpis["Total Tipos (Palabras unicas)"]?.toLocaleString() || "0";
                kpiValues[2].innerText = data.kpis["Total Lemas Unicos"]?.toLocaleString() || "0";

                const longitudPromedio = data.kpis["Longitud Promedio de Palabra"] || 0;
                kpiValues[3].innerHTML = `${longitudPromedio} <small>letras</small>`;
            }

            // 4. CONFIGURAR COLORES (Basado en tu paleta "Oaxaca")
            const oaxacaRed = '#8B2E16';
            const oaxacaForest = '#2D5A3D';
            const oaxacaGold = '#D9A05B';
            const oaxacaDark = '#1A0F0A';
            const oaxacaBlue = '#3b5998';
            const paletaPos = [oaxacaRed, oaxacaForest, oaxacaGold, oaxacaDark, oaxacaBlue, '#A8DADC'];

            // 5. DESTRUIR GRÁFICAS PREVIAS (Para evitar superposiciones)
            if (posChart) posChart.destroy();
            if (verbsChart) verbsChart.destroy();
            if (lengthChart) lengthChart.destroy();

            // 6. DIBUJAR GRÁFICA DE DONA: Distribución Gramatical
            const ctxPos = document.getElementById('posDonutChart').getContext('2d');
            posChart = new Chart(ctxPos, {
                type: 'doughnut',
                data: {
                    labels: data.pos.labels,
                    datasets: [{
                        data: data.pos.values,
                        backgroundColor: paletaPos,
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            });

            // 7. DIBUJAR GRÁFICA DE BARRAS HORIZONTALES: Top Verbos
            const ctxVerbs = document.getElementById('verbsBarChart').getContext('2d');
            verbsChart = new Chart(ctxVerbs, {
                type: 'bar',
                data: {
                    labels: data.top_verbos.labels,
                    datasets: [{
                        label: 'Frecuencia',
                        data: data.top_verbos.values,
                        backgroundColor: 'rgba(139, 46, 22, 0.8)', // Oaxaca Red con opacidad
                        borderColor: oaxacaRed,
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                },
                options: {
                    indexAxis: 'y', // ESTO HACE QUE SEA HORIZONTAL
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false } // Ocultamos la leyenda porque es redundante aquí
                    }
                }
            });

            // 8. DIBUJAR GRÁFICA DE ÁREA: Aproximación Morfológica
            const ctxLength = document.getElementById('lengthAreaChart').getContext('2d');
            lengthChart = new Chart(ctxLength, {
                type: 'line',
                data: {
                    labels: data.morfologia.labels,
                    datasets: [{
                        label: 'Cantidad de Tokens',
                        data: data.morfologia.values,
                        fill: true, // ESTO CONVIERTE LA LÍNEA EN ÁREA
                        backgroundColor: 'rgba(45, 90, 61, 0.2)', // Oaxaca Forest clarito
                        borderColor: oaxacaForest,
                        tension: 0.4, // Suaviza la curva (campana de Gauss)
                        pointRadius: 3,
                        pointBackgroundColor: oaxacaForest
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });

        }
    } catch (error) {
        console.error("Error cargando gráficas:", error);
    }
}