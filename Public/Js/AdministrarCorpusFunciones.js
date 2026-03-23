
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
          obtenerDatosDesdeAPI();
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
    // 🔑 CORREGIDO: usar la misma clave que en login
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