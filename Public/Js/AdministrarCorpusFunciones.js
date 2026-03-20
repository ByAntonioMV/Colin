
document.addEventListener('DOMContentLoaded', function () {
  // ===== NAVEGACIÓN DEL DASHBOARD =====
  const navButtons = document.querySelectorAll('.dash-nav-btn');
  const panels = document.querySelectorAll('.dash-panel');

  navButtons.forEach(button => {
    button.addEventListener('click', function () {
      const target = this.getAttribute('data-target');

      // Remover clase active de todos los botones
      navButtons.forEach(btn => btn.classList.remove('active'));
      // Agregar active al botón clickeado
      this.classList.add('active');

      // Ocultar todos los paneles
      panels.forEach(panel => {
        panel.classList.remove('active');
        panel.classList.add('fade-in');
      });

      // Mostrar el panel seleccionado
      const targetPanel = document.getElementById(target);
      if (targetPanel) {
        targetPanel.classList.add('active');
        // Forzar reflow para activar la animación
        void targetPanel.offsetWidth;
        targetPanel.classList.add('is-visible');
        if (target === 'stats') {
          cargarDatosGraficas();
        }
      }
    });
  });

  // ===== ÁREA DE CARGA (DRAG AND DROP) =====
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-upload');

  // Prevenir comportamiento por defecto del navegador
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  // Resaltar zona de carga cuando se arrastra
  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
  });

  function highlight(e) {
    dropZone.classList.add('drag-over');
  }

  function unhighlight(e) {
    dropZone.classList.remove('drag-over');
  }

  // Manejar archivos soltados
  dropZone.addEventListener('drop', handleDrop, false);
  fileInput.addEventListener('change', handleFiles, false);

  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles({ target: { files } });
  }

  function handleFiles(e) {
    const files = e.target.files;
    const validFormats = ['text/plain', 'text/csv'];
    let validFiles = [];

    for (let file of files) {
      // Validar por tipo MIME
      if (validFormats.includes(file.type)) {
        validFiles.push({
          name: file.name,
          size: formatFileSize(file.size),
          type: file.type === 'text/plain' ? 'TXT' : 'CSV'
        });
      } else {
        console.warn(`Archivo rechazado: ${file.name} (formato no soportado)`);
      }
    }

    if (validFiles.length > 0) {
      showUploadSuccess(validFiles);
    } else {
      showUploadError('No se encontraron archivos válidos. Solo se permiten .txt y .csv');
    }
  }

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }

  function showUploadSuccess(files) {
    // Crear mensaje de éxito
    const message = document.createElement('div');
    message.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background-color: var(--oaxaca-forest);
      color: var(--oaxaca-cream);
      padding: 16px 24px;
      border-radius: 8px;
      box-shadow: 0 4px 16px rgba(45, 90, 61, 0.3);
      z-index: 1000;
      animation: slideIn 0.3s ease;
      font-size: 14px;
      font-weight: 600;
      max-width: 400px;
    `;

    let filesList = files.map(f => `${f.name} (${f.size})`).join(', ');
    message.textContent = `✓ ${files.length} archivo(s) cargado(s): ${filesList}`;
    document.body.appendChild(message);

    // Remover mensaje después de 4 segundos
    setTimeout(() => {
      message.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => message.remove(), 300);
    }, 4000);
  }

  function showUploadError(errorMsg) {
    const message = document.createElement('div');
    message.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background-color: var(--oaxaca-red);
      color: var(--oaxaca-cream);
      padding: 16px 24px;
      border-radius: 8px;
      box-shadow: 0 4px 16px rgba(139, 46, 22, 0.3);
      z-index: 1000;
      animation: slideIn 0.3s ease;
      font-size: 14px;
      font-weight: 600;
      max-width: 400px;
    `;

    message.textContent = `✕ Error: ${errorMsg}`;
    document.body.appendChild(message);

    setTimeout(() => {
      message.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => message.remove(), 300);
    }, 4000);
  }

  // ===== OBSERVADOR DE INTERSECCIÓN PARA ANIMACIONES =====
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  panels.forEach(panel => {
    observer.observe(panel);
  });

  // ===== ESTILOS DE ANIMACIÓN =====
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(400px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }

    @keyframes slideOut {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(400px);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);

  // ===== EVENTO PARA EL BOTÓN DE SELECCIONAR ARCHIVOS =====
  const uploadBtn = document.querySelector('.upload-btn');
  if (uploadBtn) {
    uploadBtn.addEventListener('click', function (e) {
      e.preventDefault();
      fileInput.click();
    });
  }

  console.log('[Dashboard] Inicializado correctamente');
});

// Variables globales para las instancias de ECharts
let posChart, verbsChart, posRotationChart;

async function cargarDatosGraficas() {
  const parametrosURL = new URLSearchParams(window.location.search);
  const hashCorpus = parametrosURL.get('hash');

  if (!hashCorpus) return;

  try {
    const response = await fetch(`/api/corpus/graficas/${hashCorpus}`);
    const result = await response.json();

    if (result.status === 'success') {
      const data = result.data;

      // 1. ACTUALIZAR KPIs
      const kpiValues = document.querySelectorAll('#stats .kpi-value');
      if (kpiValues.length >= 4) {
        kpiValues[0].innerText = data.kpis["Total Tokens"]?.toLocaleString() || "0";
        kpiValues[1].innerText = data.kpis["Total Tipos (Palabras unicas)"]?.toLocaleString() || "0";
        kpiValues[2].innerText = data.kpis["Total Lemas Unicos"]?.toLocaleString() || "0";
        kpiValues[3].innerHTML = `${data.kpis["Longitud Promedio de Palabra"] || 0} <small>letras</small>`;
      }

      // 2. COLORES OAXACA
      const oaxacaRed = '#8B2E16';
      const oaxacaForest = '#2D5A3D';
      const oaxacaGold = '#D9A05B';
      const oaxacaDark = '#1A0F0A';
      const oaxacaBlue = '#3b5998';
      const paletaPos = [oaxacaRed, oaxacaForest, oaxacaGold, oaxacaDark, oaxacaBlue, '#A8DADC'];

      // 3. LIMPIAR E INICIALIZAR CONTENEDORES (Una sola vez)
      if (posChart) posChart.dispose();
      if (verbsChart) verbsChart.dispose();
      if (posRotationChart) posRotationChart.dispose();

      posChart = echarts.init(document.getElementById('posDonutChart'));
      verbsChart = echarts.init(document.getElementById('verbsBarChart'));
      posRotationChart = echarts.init(document.getElementById('posBarRotationChart'));

      // =========================================================
      // GRÁFICA 1: Pie with Scrollable Legend
      // =========================================================
      const posData = data.pos.labels.map((label, index) => ({
        name: label,
        value: data.pos.values[index]
      }));

      posChart.setOption({
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b} : {c} ({d}%)'
        },
        legend: {
          type: 'scroll',
          orient: 'vertical',
          right: 10,
          top: 20,
          bottom: 20,
          data: data.pos.labels
        },
        color: paletaPos,
        series: [
          {
            name: 'Categoría (POS)',
            type: 'pie',
            radius: '55%',
            center: ['40%', '50%'],
            data: posData,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      });

      // =========================================================
      // GRÁFICA 2: Estilo "Rainfall and Evaporation" (Top Verbos)
      // =========================================================
      verbsChart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['Frecuencia'] },
        toolbox: {
          show: true,
          feature: {
            dataView: { show: true, readOnly: false, title: 'Datos' },
            magicType: { show: true, type: ['line', 'bar'], title: { line: 'Línea', bar: 'Barra' } },
            restore: { show: true, title: 'Restaurar' },
            saveAsImage: { show: true, title: 'Guardar' }
          }
        },
        calculable: true,
        xAxis: [
          {
            type: 'category',
            data: data.top_verbos.labels
          }
        ],
        yAxis: [
          {
            type: 'value'
          }
        ],
        series: [
          {
            name: 'Frecuencia',
            type: 'bar',
            data: data.top_verbos.values,
            itemStyle: { color: oaxacaRed },
            markPoint: {
              data: [
                { type: 'max', name: 'Máximo' },
                { type: 'min', name: 'Mínimo' }
              ]
            },
            markLine: {
              data: [{ type: 'average', name: 'Promedio' }]
            }
          }
        ]
      });

      // =========================================================
      // GRÁFICA 3: Bar Label Rotation (Frecuencias POS)
      // =========================================================
      const labelOption = {
        show: true,
        position: 'insideBottom',
        distance: 15,
        align: 'left',
        verticalAlign: 'middle',
        rotate: 90,
        formatter: '{c}',
        fontSize: 14,
        color: '#ffffff',
        rich: { name: {} }
      };

      posRotationChart.setOption({
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        legend: {
          data: ['Frecuencia']
        },
        toolbox: {
          show: true,
          orient: 'vertical',
          left: 'right',
          top: 'center',
          feature: {
            mark: { show: true },
            dataView: { show: true, readOnly: false, title: 'Datos' },
            magicType: { show: true, type: ['line', 'bar', 'stack'], title: { line: 'Línea', bar: 'Barra', stack: 'Apilar' } },
            restore: { show: true, title: 'Restaurar' },
            saveAsImage: { show: true, title: 'Guardar' }
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            axisTick: { show: false },
            data: data.pos.labels,
            axisLabel: {
              rotate: 45,
              fontSize: 13
            }
          }
        ],
        yAxis: [
          {
            type: 'value'
          }
        ],
        series: [
          {
            name: 'Frecuencia',
            type: 'bar',
            barGap: 0,
            label: labelOption,
            emphasis: { focus: 'series' },
            itemStyle: { color: oaxacaBlue },
            data: data.pos.values
          }
        ]
      });

    }
  } catch (error) {
    console.error("Error cargando gráficas ECharts:", error);
  }
}

// Redimensionar gráficos si cambia el tamaño de la ventana
window.addEventListener('resize', function () {
  if (posChart) posChart.resize();
  if (verbsChart) verbsChart.resize();
  if (posRotationChart) posRotationChart.resize();
});