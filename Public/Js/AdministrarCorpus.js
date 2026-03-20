document.addEventListener('DOMContentLoaded', () => {

  const parametrosURL = new URLSearchParams(window.location.search);
  const idCorpus = parametrosURL.get('id');
  const hashCorpus = parametrosURL.get('hash');
  const nombreCorpus = parametrosURL.get('nombre');

  if (!idCorpus || !hashCorpus) {
    alert("No se encontró el corpus. Regresando...");
    window.location.href = '/PanelCorpus';
    return;
  }

  console.log(`Listo para subir archivos a HDFS en la carpeta: /${hashCorpus}`);
  document.getElementById('tituloCorpus').textContent = `Panel de Administración: ${nombreCorpus}`;
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-upload');

  // 1. Cuando se seleccionan archivos con el botón
  fileInput.addEventListener('change', (e) => {
    const archivos = e.target.files;
    if (archivos.length > 0) {
      enviarArchivosAlBackend(archivos, hashCorpus);
    }
  });

  // 2. Efectos visuales para el Drag & Drop (Arrastrar y soltar)
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault(); // Necesario para permitir el "drop"
    dropZone.style.border = "2px dashed #007bff"; // Cambia color para indicar que puede soltar
    dropZone.style.backgroundColor = "rgba(0, 123, 255, 0.05)";
  });

  dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.style.border = ""; // Restaura el diseño original
    dropZone.style.backgroundColor = "";
  });

  // 3. Cuando se sueltan los archivos en la zona
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.border = "";
    dropZone.style.backgroundColor = "";

    const archivos = e.dataTransfer.files;
    if (archivos.length > 0) {
      enviarArchivosAlBackend(archivos, hashCorpus);
    }
  });


});

async function enviarArchivosAlBackend(archivos, hash) {
  // Creamos el "paquete" de datos
  const formData = new FormData();

  // Le metemos el Hash (la carpeta destino)
  formData.append('hash_carpeta', hash);

  // Le metemos todos los archivos seleccionados
  for (let i = 0; i < archivos.length; i++) {
    formData.append('archivos', archivos[i]);
  }

  const token = localStorage.getItem('access_token');

  try {
    // Opcional: Aquí podrías mostrar un "Cargando..." en tu HTML
    console.log(`Subiendo y procesando ${archivos.length} archivo(s)...`);

    const response = await fetch('/api/corpus/subir-archivos', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    if (response.ok) {
      const data = await response.json();

      // 1. Mensaje de éxito y limpieza del input
      document.getElementById('file-upload').value = "";

      // =========================================================
      // 2. AQUÍ ENTRA TU NUEVO CÓDIGO PARA MOSTRAR ESTADÍSTICAS
      // =========================================================
      if (data.status === 'success' && data.estadisticas) {
        // Mostrar el panel oculto
        const panelResultados = document.getElementById('nlp-results-panel');
        if (panelResultados) panelResultados.style.display = 'block';

        // Llenar las tarjetas de métricas
        document.getElementById('res-lineas').innerText = data.estadisticas.lineas_totales.toLocaleString();
        document.getElementById('res-tokens').innerText = data.estadisticas.total_tokens.toLocaleString();

        // Llenar la lista de categorías (Verbos, Sustantivos, etc)
        const posList = document.getElementById('res-pos-list');
        if (posList) {
          posList.innerHTML = ''; // Limpiar lista previa

          const distribucion = data.estadisticas.distribucion_pos;
          for (const [categoria, cantidad] of Object.entries(distribucion)) {
            const li = document.createElement('li');
            li.innerHTML = `<span class="pos-name">${categoria}</span> <span class="pos-count">${cantidad.toLocaleString()}</span>`;
            posList.appendChild(li);
          }
        }
      }
      // =========================================================

      // Aquí en el futuro llamaremos a una función para recargar la tabla de archivos
    } else {
      const error = await response.json();
      alert("Error al subir: " + (error.detail || "Error desconocido"));
    }
  } catch (error) {
    console.error("Error de conexión:", error);
    alert("Ocurrió un error al intentar comunicarse con el servidor.");
  }
}