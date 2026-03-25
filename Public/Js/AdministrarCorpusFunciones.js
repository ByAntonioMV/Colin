
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
          setTimeout(async () => {
            try {
              const data = await obtenerDatosDesdeAPI();

              if (data) {
              }
            } catch (error) {
              console.error("Error al cargar las estadísticas:", error);
            }
          }, 50);
        }
        if (target === 'stats-special') {
          try {
            const urlParams = new URLSearchParams(window.location.search);
            const hashCorpus = urlParams.get('hash');

            // Llamamos a la función que creamos en el paso anterior
            // (Asegúrate de haber importado esta función al inicio de tu archivo)
            inicializarTablaEspecifica(hashCorpus);

          } catch (error) {
            console.error("Error al cargar la tabla específica:", error);
          }
        }
        if (target === 'viz') {
          try {
            const urlParams = new URLSearchParams(window.location.search);
            const hashCorpus = urlParams.get('hash');

            inicializarNubePalabras(hashCorpus);

            // Forzamos un resize por si ECharts no detectó bien el tamaño
            setTimeout(() => { if (wordCloudChart) wordCloudChart.resize(); }, 150);

          } catch (error) {
            console.error("Error al cargar la nube:", error);
          }
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

export async function obtenerDatosDesdeAPI(hashCorpus) {
  if (!hashCorpus || hashCorpus === "undefined") {
    const urlParams = new URLSearchParams(window.location.search);
    hashCorpus = urlParams.get('hash');
  }

  if (!hashCorpus) {
    console.error("El hash proporcionado no es válido y no se encontró en la URL.");
    return null;
  }

  try {
    const token = localStorage.getItem("access_token");

    console.log("Token enviado:", token);

    if (!token) {
      console.error("No hay token. Usuario no autenticado.");
      return null;
    }

    const response = await fetch(`/api/datos-hadoop/graficas/${hashCorpus}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status} en la ruta /api/datos-hadoop/graficas/${hashCorpus}`);
    }

    const result = await response.json();
    return (result.status === 'success') ? result.data : null;

  } catch (error) {
    console.error("Error en la petición:", error);
    return null;
  }
}

/**
 * Pide los datos específicos para la tabla al backend
 */
export async function obtenerDatosTablaDesdeAPI(hashCorpus, limite = 1000) {
  if (!hashCorpus || hashCorpus === "undefined") {
    const urlParams = new URLSearchParams(window.location.search);
    hashCorpus = urlParams.get('hash');
  }

  if (!hashCorpus) return null;

  try {
    const token = localStorage.getItem("access_token");

    // Llamamos al nuevo endpoint que creamos en Python
    const response = await fetch(`/api/datos-hadoop/tabla/${hashCorpus}?limite=${limite}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Error HTTP: ${response.status} al obtener la tabla`);
    }

    const result = await response.json();
    return (result.status === 'success') ? result.data : null;

  } catch (error) {
    console.error("Error en la petición de la tabla:", error);
    return null;
  }
}

/**
 * Recibe los datos y construye las filas de la tabla dinámicamente
 */
export function renderizarTablaEspecifica(datos) {
  // Apuntamos al cuerpo de la tabla
  const tbody = document.querySelector('#detailedStatsTable tbody');
  if (!tbody) return;

  // 1. Limpiamos las filas de ejemplo que pusiste en el HTML
  tbody.innerHTML = '';

  // 2. Validamos si hay datos
  if (!datos || datos.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 20px; color: #888;">
                    No se encontraron datos detallados para este corpus.
                </td>
            </tr>
        `;
    return;
  }

  // 3. Recorremos el JSON y creamos una fila por cada elemento
  datos.forEach(fila => {
    const tr = document.createElement('tr');

    // Formateamos la frecuencia para que tenga comas (ej. 1,234)
    const frecuenciaFormateada = fila.frecuencia ? fila.frecuencia.toLocaleString() : '0';

    // Manejamos posibles valores vacíos en la morfología para que no diga "undefined"
    const morfologia = fila.morfologia || '-';
    const pos = fila.pos || 'Desconocido';

    tr.innerHTML = `
            <td><strong>${fila.token}</strong></td>
            <td>${fila.lema}</td>
            <td><span class="pos-badge">${pos}</span></td>
            <td>${morfologia}</td>
            <td>${frecuenciaFormateada}</td>
        `;

    tbody.appendChild(tr);
  });
}

/**
 * Función principal para orquestar la carga de la tabla
 */
export async function inicializarTablaEspecifica(hashCorpus) {
  // Opcional: Puedes mostrar un mensaje de "Cargando..." aquí
  const tbody = document.querySelector('#detailedStatsTable tbody');
  if (tbody) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Cargando datos desde Hadoop...</td></tr>';
  }

  const datos = await obtenerDatosTablaDesdeAPI(hashCorpus, 200); // Traemos el top 200
  renderizarTablaEspecifica(datos);
}

let wordCloudChart = null;

export async function inicializarNubePalabras(hashCorpus) {
  if (!hashCorpus) return;

  try {
    const token = localStorage.getItem("access_token");

    // Llamamos al nuevo endpoint
    const response = await fetch(`/api/datos-hadoop/nube/${hashCorpus}?limite=150`, {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!response.ok) throw new Error("Error al cargar la nube");
    const result = await response.json();

    if (result.status === 'success' && result.data) {
      renderizarNube(result.data);
    }
  } catch (error) {
    console.error("Error renderizando nube:", error);
  }
}

/**
 * Dibuja la nube usando ECharts
 */
function renderizarNube(datosNube) {
  const chartDom = document.getElementById('wordCloudChart');
  if (!chartDom || !datosNube) return;

  if (wordCloudChart) echarts.dispose(chartDom);
  wordCloudChart = echarts.init(chartDom);

  const option = {
    tooltip: { show: true },
    series: [{
      type: 'wordCloud',
      shape: 'circle', // Puedes cambiarlo a 'cardioid', 'diamond', 'triangle-forward'
      keepAspect: false,
      left: 'center',
      top: 'center',
      width: '90%',
      height: '90%',
      right: null,
      bottom: null,
      sizeRange: [12, 60], // Tamaño mínimo y máximo de las letras
      rotationRange: [-45, 45], // Ángulos de rotación de las palabras
      rotationStep: 45,
      gridSize: 8,
      drawOutOfBound: false,
      layoutAnimation: true,
      textStyle: {
        fontFamily: 'sans-serif',
        fontWeight: 'bold',
        // Color aleatorio para cada palabra basado en tu paleta
        color: function () {
          const colors = ['#8B2E16', '#2D5A3D', '#D9A05B', '#1A0F0A', '#3b5998'];
          return colors[Math.floor(Math.random() * colors.length)];
        }
      },
      emphasis: { focus: 'self', textStyle: { textShadowBlur: 10, textShadowColor: '#333' } },
      data: datosNube
    }]
  };

  wordCloudChart.setOption(option);
}