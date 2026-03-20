document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modalCorpus');
    const btnOpen = document.getElementById('btnNuevoCorpus');
    const btnClose = document.getElementById('closeModalCorpus');
    const form = document.getElementById('formCorpus');

    // Abrir modal
    btnOpen.addEventListener('click', () => {
        modal.classList.add('is-open');
    });

    // Cerrar modal
    btnClose.addEventListener('click', () => {
        modal.classList.remove('is-open');
    });

    // Enviar Formulario
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Recolectar los datos
        const nuevoCorpus = {
            nombre: document.getElementById('corpusNombre').value,
            tipo: document.getElementById('corpusTipo').value,
            lengua: document.getElementById('corpusLengua').value,
            variante: document.getElementById('corpusVariante').value,
            estado: document.getElementById('corpusEstado').value,
            municipio: document.getElementById('corpusMunicipio').value
        };

        // 2. Obtener el token con el nombre correcto que usa tu sistema
        const token = localStorage.getItem('access_token');

        try {
            // 3. Hacer la petición al backend (Usamos la ruta relativa como en tu otro JS)
            const response = await fetch('/api/corpus/crear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(nuevoCorpus)
            });

            if (response.ok) {
                // Todo salió perfecto (Status 200)
                alert('Corpus creado con éxito');
                cargarCorpus()
                modal.classList.remove('is-open');
                form.reset();

                // Si ya tienes tu función para recargar la tabla de corpus, la llamas aquí:
                // cargarCorpus(); 
            } else {
                // El servidor devolvió un error
                const res = await response.json();
                alert("❌ Error: " + (res.detail || "No se pudo procesar"));
            }

        } catch (error) {
            console.error("Error en la petición:", error);
            alert("Error de conexión con el servidor.");
        }
    });
    cargarCorpus();
});

// ==========================================
// OBTENER Y PINTAR LA TABLA DE CORPUS
// ==========================================
async function cargarCorpus() {
    const tableBody = document.getElementById('corpusTableBody');
    const token = localStorage.getItem('access_token');

    try {
        // 1. Mostrar estado de carga (opcional pero recomendado)
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center">Cargando corpus...</td></tr>';

        // 2. Hacer la petición al backend
        const response = await fetch('/api/corpus/listar', {
            method: 'GET',
            headers: { 
                'Authorization': `Bearer ${token}` 
            }
        });

        if (!response.ok) throw new Error('Error al obtener la lista de corpus');

        const listaCorpus = await response.json();
        
        // 3. Limpiar la tabla
        tableBody.innerHTML = '';

        // 4. Si no hay datos, mostramos un mensaje
        if (listaCorpus.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center">No hay corpus registrados aún.</td></tr>';
            return;
        }

        // 5. Recorrer los datos e inyectarlos en el HTML
        listaCorpus.forEach(corpus => {
            const row = document.createElement('tr');

            row.innerHTML = `
                <td class="font-bold">${corpus.nombre}</td>
                <td><span class="tag-type">${corpus.tipo}</span></td>
                <td>${corpus.lengua}</td>
                <td>${corpus.variante}</td>
                <td>${corpus.estado}</td>
                <td>${corpus.municipio}</td>
                <td class="text-center action-btns">
                    <button class="btn-manage" onclick="administrarCorpus('${corpus.id}', '${corpus.hash}', '${corpus.nombre}')">Administrar →</button>
                </td>
            `;
            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error('Error:', error);
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center text-red">Error al cargar los datos. Verifica tu conexión.</td></tr>';
    }
}

// ==========================================
// ELIMINAR UN CORPUS (HDFS y MySQL)
// ==========================================
async function eliminarCorpus(idCorpus) {
    if (!confirm("¿Estás seguro de que deseas eliminar este corpus? Esto borrará la carpeta en Hadoop y los datos de la base de datos.")) return;
    
    const token = localStorage.getItem('access_token');
    
    try {
        const response = await fetch(`/api/corpus/eliminar/${idCorpus}`, {
            method: 'DELETE',
            headers: { 
                'Authorization': `Bearer ${token}` 
            }
        });
        
        if (response.ok) {
            alert("✅ Corpus eliminado correctamente");
            cargarCorpus(); // Recargamos la tabla para que desaparezca
        } else {
            const res = await response.json();
            alert("❌ Error al eliminar: " + (res.detail || "Error desconocido"));
        }
    } catch (error) {
        alert("Error de conexión al intentar eliminar");
        console.error(error);
    }
}

// ==========================================
// FUNCIÓN PLACEHOLDER PARA ADMINISTRAR
// ==========================================
function administrarCorpus(idCorpus, hashCorpus, nombreCorpus) {
    // Codificamos el nombre por si tiene espacios o acentos
    const nombreSeguro = encodeURIComponent(nombreCorpus);
    // Lo mandamos a la nueva página con los datos pegados en la URL
    window.location.href = `/AdministrarCorpus?id=${idCorpus}&hash=${hashCorpus}&nombre=${nombreSeguro}`;
}