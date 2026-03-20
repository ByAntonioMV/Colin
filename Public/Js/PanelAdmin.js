// 1. Variables Globales (Fuera para que todas las funciones las vean)
let editMode = false;
let currentEditId = null;

document.addEventListener('DOMContentLoaded', () => {
    // Definimos los elementos del DOM primero
    const userForm = document.getElementById('userForm');
    const modal = document.getElementById('userModal');
    const openBtn = document.getElementById('openCreateModal');
    const closeBtn = document.getElementById('closeModal');
    const modalTitle = document.getElementById('modalTitle');
    const submitBtn = userForm ? userForm.querySelector('.form-submit') : null;

    // 2. Navegación del Sidebar
    const navBtns = document.querySelectorAll('.admin-nav-btn');
    const panes = document.querySelectorAll('.admin-pane');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-target');
            navBtns.forEach(b => b.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });

    // 3. Control del Modal (Abrir para Nuevo Usuario)
    if (openBtn) {
        openBtn.onclick = () => {
            resetModal(userForm, modalTitle, submitBtn); // Limpiamos antes de abrir
            modal.classList.add('is-open');
        };
    }

    if (closeBtn) {
        closeBtn.onclick = () => {
            modal.classList.remove('is-open');
        };
    }

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.classList.remove('is-open');
        }
    };

    // 4. Envío del Formulario (Crear o Editar)
    if (userForm) {
        userForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const token = localStorage.getItem('access_token');

            const userData = {
                nombre: document.getElementById('userName').value,
                apellido: document.getElementById('userLastName').value,
                correo: document.getElementById('userEmail').value,
                password: document.getElementById('userPass').value,
                telefono: document.getElementById('userPhone').value,
                institucion: document.getElementById('userInst').value,
                rol: document.getElementById('userRol').value
            };

            const url = editMode ? `/api/usuarios/actualizar/${currentEditId}` : '/api/usuarios/crear';
            const method = editMode ? 'PUT' : 'POST';

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(userData)
                });

                if (response.ok) {
                    alert(editMode ? 'Usuario actualizado' : 'Usuario creado');
                    modal.classList.remove('is-open');
                    userForm.reset();
                    cargarUsuarios();
                } else {
                    const res = await response.json();
                    alert("❌ Error: " + (res.detail || "No se pudo procesar"));
                }
            } catch (error) {
                alert("Error de conexión");
            }
        });
    }

    // Cargar la tabla al iniciar
    cargarUsuarios();
});

// --- FUNCIONES GLOBALES (Fuera del DOMContentLoaded para que el HTML las vea) ---

async function cargarUsuarios() {
    const tableBody = document.getElementById('userTableBody');
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch('/api/usuarios/listar', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error('Error al obtener usuarios');

        const usuarios = await response.json();
        tableBody.innerHTML = '';

        usuarios.forEach(user => {
            const row = document.createElement('tr');
            const rolesBadges = user.roles.map(rol => `<span class="badge">${rol}</span>`).join(' ');

            row.innerHTML = `
                <td>${user.nombre}</td>
                <td>${user.apellido}</td>
                <td>${user.correo}</td>
                <td>••••••••</td>
                <td>${user.telefono || 'N/A'}</td>
                <td>${user.institucion || 'N/A'}</td>
                <td>${rolesBadges}</td>
                <td>
                    <div class="action-btns">
                        <button class="btn-edit" onclick="editarUsuario('${user.id}')">✏️</button>
                        <button class="btn-delete" onclick="eliminarUsuario('${user.id}')">🗑️</button>
                    </div>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error:', error);
    }
}

async function editarUsuario(id) {
    const token = localStorage.getItem('access_token');
    const modal = document.getElementById('userModal');
    const modalTitle = document.getElementById('modalTitle');
    const submitBtn = document.querySelector('.form-submit');

    try {
        const response = await fetch(`/api/usuarios/listar`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const usuarios = await response.json();
        const user = usuarios.find(u => u.id === id);

        if (user) {
            document.getElementById('userName').value = user.nombre;
            document.getElementById('userLastName').value = user.apellido;
            document.getElementById('userEmail').value = user.correo;
            document.getElementById('userPhone').value = user.telefono || '';
            document.getElementById('userInst').value = user.institucion || '';
            document.getElementById('userRol').value = user.roles[0];
            document.getElementById('userPass').value = '••••••••';

            editMode = true;
            currentEditId = id;
            modalTitle.textContent = "Editar Usuario";
            submitBtn.textContent = "Actualizar Cambios";
            modal.classList.add('is-open');
        }
    } catch (error) {
        console.error("Error al cargar datos", error);
    }
}

async function eliminarUsuario(idUsuario) {
    if (!confirm("¿Borrar este usuario?")) return;
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`/api/usuarios/eliminar/${idUsuario}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            alert("Usuario eliminado");
            cargarUsuarios();
        }
    } catch (error) {
        alert("Error al eliminar");
    }
}

function resetModal(form, title, btn) {
    if (form) form.reset();
    editMode = false;
    currentEditId = null;
    if (title) title.textContent = "Nuevo Usuario";
    if (btn) btn.textContent = "Guardar Usuario";
}