document.addEventListener('DOMContentLoaded', () => {
    const navButtons = document.querySelectorAll('.dash-nav-btn');
    const contentPanes = document.querySelectorAll('.dash-pane');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-section');

            // 1. Quitar clase active de todos los botones
            navButtons.forEach(btn => btn.classList.remove('active'));
            
            // 2. Quitar clase active de todas las secciones de contenido
            contentPanes.forEach(pane => pane.classList.remove('active'));

            // 3. Añadir clase active al botón clickeado
            button.classList.add('active');

            // 4. Mostrar la sección correspondiente
            const targetPane = document.getElementById(targetId);
            if (targetPane) {
                targetPane.classList.add('active');
            }
        });
    });
});