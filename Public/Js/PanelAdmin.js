let editMode = false;
let currentEditId = null;

let roleEditMode = false;
let currentRoleEditId = null;

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements: Usuarios ---
    const userForm = document.getElementById('userForm');
    const userModal = document.getElementById('userModal');
    const openUserBtn = document.getElementById('openCreateModal');
    const closeUserBtn = document.getElementById('closeModal');
    const userModalTitle = document.getElementById('modalTitle');
    const submitUserBtn = userForm ? userForm.querySelector('.form-submit') : null;

    // --- DOM Elements: Roles ---
    const roleForm = document.getElementById('roleForm');
    const roleModal = document.getElementById('roleModal');
    const openRoleBtn = document.getElementById('openCreateRoleModal');
    const closeRoleBtn = document.getElementById('closeRoleModal');
    const roleModalTitle = document.getElementById('roleModalTitle');
    const submitRoleBtn = roleForm ? roleForm.querySelector('.form-submit') : null;

    // ==========================================
    // 2. NAVEGACIÓN DEL SIDEBAR
    // ==========================================
    const navBtns = document.querySelectorAll('.admin-nav-btn');
    const panes = document.querySelectorAll('.admin-pane');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-target');
            navBtns.forEach(b => b.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(target).classList.add('active');

            // Cargar datos dinámicamente según la pestaña activa
            if (target === 'users-section') cargarUsuarios();
            if (target === 'roles-section') cargarRoles();
        });
    });

    // ==========================================
    // 3. CONTROL DE MODALES (Abrir / Cerrar)
    // ==========================================
    // Modal Usuarios
    if (openUserBtn) openUserBtn.onclick = () => { resetModal(userForm, userModalTitle, submitUserBtn); userModal.classList.add('is-open'); };
    if (closeUserBtn) closeUserBtn.onclick = () => userModal.classList.remove('is-open');

    // Modal Roles
    if (openRoleBtn) openRoleBtn.onclick = () => { resetRoleModal(roleForm, roleModalTitle, submitRoleBtn); roleModal.classList.add('is-open'); };
    if (closeRoleBtn) closeRoleBtn.onclick = () => roleModal.classList.remove('is-open');

    // Cerrar al dar click fuera
    window.onclick = (event) => {
        if (event.target == userModal) userModal.classList.remove('is-open');
        if (event.target == roleModal) roleModal.classList.remove('is-open');
    };

    // ==========================================
    // 4. ENVÍO DE FORMULARIOS (Submits)
    // ==========================================
    // Submit Usuario
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
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify(userData)
                });
                if (response.ok) {
                    alert(editMode ? 'Usuario actualizado' : 'Usuario creado');
                    userModal.classList.remove('is-open');
                    cargarUsuarios();
                } else {
                    const res = await response.json();
                    alert("❌ Error: " + (res.detail || "No se pudo procesar"));
                }
            } catch (error) { alert("Error de conexión"); }
        });
    }

    // Submit Rol
    if (roleForm) {
        roleForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const token = localStorage.getItem('access_token');
            const roleData = {
                nombre: document.getElementById('roleName').value
            };

            const url = roleEditMode ? `/api/roles/actualizar/${currentRoleEditId}` : '/api/roles/crear';
            const method = roleEditMode ? 'PUT' : 'POST';

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify(roleData)
                });
                if (response.ok) {
                    alert(roleEditMode ? 'Rol actualizado' : 'Rol creado');
                    roleModal.classList.remove('is-open');
                    cargarRoles(); // Recargar la tabla de roles
                } else {
                    const res = await response.json();
                    alert("❌ Error: " + (res.detail || "No se pudo procesar"));
                }
            } catch (error) { alert("Error de conexión"); }
        });
    }

    // Iniciar cargando la vista activa
    cargarUsuarios();
});

// ==========================================
// FUNCIONES GLOBALES PARA USUARIOS
// ==========================================
async function cargarUsuarios() {
    const tableBody = document.getElementById('userTableBody');
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch('/api/usuarios/listar', { headers: { 'Authorization': `Bearer ${token}` } });
        if (!response.ok) throw new Error('Error al obtener usuarios');
        const usuarios = await response.json();
        tableBody.innerHTML = '';
        usuarios.forEach(user => {
            const rolesBadges = user.roles.map(rol => `<span class="badge">${rol}</span>`).join(' ');
            const row = document.createElement('tr');
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
    } catch (error) { console.error('Error:', error); }
}

async function editarUsuario(id) {
    const token = localStorage.getItem('access_token');
    const modal = document.getElementById('userModal');
    try {
        const response = await fetch(`/api/usuarios/listar`, { headers: { 'Authorization': `Bearer ${token}` } });
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

            editMode = true; currentEditId = id;
            document.getElementById('modalTitle').textContent = "Editar Usuario";
            document.querySelector('#userForm .form-submit').textContent = "Actualizar Cambios";
            modal.classList.add('is-open');
        }
    } catch (error) { console.error("Error al cargar datos", error); }
}

async function eliminarUsuario(idUsuario) {
    if (!confirm("¿Borrar este usuario?")) return;
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`/api/usuarios/eliminar/${idUsuario}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) { alert("Usuario eliminado"); cargarUsuarios(); }
    } catch (error) { alert("Error al eliminar"); }
}

function resetModal(form, title, btn) {
    if (form) form.reset();
    editMode = false; currentEditId = null;
    if (title) title.textContent = "Nuevo Usuario";
    if (btn) btn.textContent = "Guardar Usuario";
}

// ==========================================
// FUNCIONES GLOBALES PARA ROLES
// ==========================================
async function cargarRoles() {
    const tableBody = document.getElementById('roleTableBody');
    if (!tableBody) return; // Por si acaso no estás en la pestaña

    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch('/api/roles/listar', { headers: { 'Authorization': `Bearer ${token}` } });
        if (!response.ok) throw new Error('Error al obtener roles');
        const roles = await response.json();
        tableBody.innerHTML = '';
        roles.forEach(rol => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${rol.nombre}</strong></td>
                <td><span class="badge">Activo</span></td>
                <td>
                    <div class="action-btns">
                        <button class="btn-delete" onclick="eliminarRol('${rol.id}')">🗑️</button>
                    </div>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) { console.error('Error:', error); }
}

async function eliminarRol(idRol) {
    if (!confirm("¿Borrar este rol? Fallará si hay usuarios con este rol asignado.")) return;
    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`/api/roles/eliminar/${idRol}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            alert("Rol eliminado");
            cargarRoles();
        } else {
            const res = await response.json();
            alert("❌ Error: " + (res.detail || "No se pudo eliminar"));
        }
    } catch (error) { alert("Error al eliminar"); }
}

function resetRoleModal(form, title, btn) {
    if (form) form.reset();
    roleEditMode = false; currentRoleEditId = null;
    if (title) title.textContent = "Nuevo Rol";
    if (btn) btn.textContent = "Guardar Rol";
}