document.addEventListener('DOMContentLoaded', () => {
    const navButtons = document.querySelectorAll('.dash-nav-btn');
    const contentPanes = document.querySelectorAll('.dash-pane');
    const langSelect = document.getElementById("langSelect");

    const chartDom = document.getElementById('wordCloud');
    console.log("wordCloud al inicio:", chartDom.offsetWidth, chartDom.offsetHeight);
    let wordsPendientes = null;

    // ==========================
    // NAVEGACIÓN 
    // ==========================
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-section');

            navButtons.forEach(btn => btn.classList.remove('active'));
            contentPanes.forEach(pane => pane.classList.remove('active'));

            button.classList.add('active');

            const targetPane = document.getElementById(targetId);
            if (targetPane) {
                targetPane.classList.add('active');
            }

            // ✅ Si hay datos pendientes y navegamos al panel de la nube, renderizar
            if (wordsPendientes) {
                setTimeout(() => {
                    dibujarNube(wordsPendientes);
                    wordsPendientes = null;
                }, 50);
            }
        });
    });

    // ==========================
    // CARGAR CORPUS EN SELECT
    // ==========================
    cargarCorpus();

    async function cargarCorpus() {
        try {
            const res = await fetch("/api/corpus/listar/usuario");
            const data = await res.json();

            console.log("Respuesta backend:", data);
            langSelect.innerHTML = "";

            if (!Array.isArray(data) || data.length === 0) {
                langSelect.innerHTML = `<option>No hay corpus</option>`;
                return;
            }

            data.forEach(corpus => {
                const option = document.createElement("option");
                option.value = corpus.id;
                option.textContent = corpus.nombre;
                option.dataset.hash = corpus.hash;
                langSelect.appendChild(option);
            });

            const primerHash = data[0].hash;
            cargarNube(primerHash);

        } catch (error) {
            console.error("Error cargando corpus:", error);
        }
    }

    // ==========================
    // OBTENER NUBE DESDE BACKEND
    // ==========================
    async function cargarNube(hash) {
        try {
            const res = await fetch(`/api/datos-hadoop/nube/usuario/${hash}`);

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Error al obtener nube");
            }

            const data = await res.json();
            console.log("DATA NUBE:", data);

            const lista = data.data || [];

            if (lista.length === 0) {
                console.warn("Nube vacía:", data);
                return;
            }

            const chartDom = document.getElementById('wordCloud');

            // ✅ Si el contenedor tiene dimensiones, dibujar directo
            if (chartDom.offsetWidth > 0 && chartDom.offsetHeight > 0) {
                dibujarNube(lista);
            } else {
                // ✅ Si está oculto, guardar para cuando el panel sea visible
                console.log("Panel oculto, guardando datos para después...");
                wordsPendientes = lista;
            }

        } catch (error) {
            console.error("Error nube:", error);
        }
    }

    // ==========================
    // DIBUJAR WORDCLOUD
    // ==========================
    function dibujarNube(words) {
        const chartDom = document.getElementById('wordCloud');

        if (!chartDom) {
            console.error("No existe #wordCloud");
            return;
        }

        const existente = echarts.getInstanceByDom(chartDom);
        if (existente) existente.dispose();

        const myChart = echarts.init(chartDom);

        const colors = ['#534AB7', '#1D9E75', '#D85A30', '#185FA5',
            '#639922', '#993C1D', '#378ADD', '#7F77DD'];

        myChart.setOption({
            series: [{
                type: 'wordCloud',
                left: 'center',
                top: 'center',
                width: '100%',
                height: '100%',
                gridSize: 8,
                sizeRange: [14, 56],
                rotationRange: [-45, 45],
                rotationStep: 45,
                drawOutOfBound: false,
                textStyle: {
                    fontFamily: 'sans-serif',
                    fontWeight: 'bold',
                    color: () => colors[Math.floor(Math.random() * colors.length)]
                },
                emphasis: {
                    textStyle: {
                        shadowBlur: 8,
                        shadowColor: 'rgba(0,0,0,0.15)'
                    }
                },
                data: words
            }]
        });

        window.addEventListener('resize', () => myChart.resize());
    }

    // ==========================
    // EVENTO SELECT
    // ==========================
    langSelect.addEventListener("change", (e) => {
        const selectedOption = e.target.selectedOptions[0];
        const hash = selectedOption.dataset.hash;
        console.log("Hash seleccionado:", hash);
        cargarNube(hash);
    });

});