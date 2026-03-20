/* ===================================================
   LENGUAS VIVAS DE OAXACA - JAVASCRIPT PURO
   Sin frameworks, sin dependencias
   =================================================== */

document.addEventListener('DOMContentLoaded', function () {

  // ===== SMOOTH SCROLL =====
  var navAnchors = document.querySelectorAll('a[href^="#"]');
  for (var i = 0; i < navAnchors.length; i++) {
    navAnchors[i].addEventListener('click', function (e) {
      e.preventDefault();
      var targetId = this.getAttribute('href');
      var target = document.querySelector(targetId);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
      // Cerrar menu movil si esta abierto
      var mobileMenu = document.getElementById('mobile-menu');
      var hamburger = document.getElementById('hamburger');
      if (mobileMenu && mobileMenu.classList.contains('is-open')) {
        mobileMenu.classList.remove('is-open');
        hamburger.classList.remove('is-active');
      }
    });
  }

  // ===== NAV SHADOW ON SCROLL =====
  var nav = document.getElementById('main-nav');
  window.addEventListener('scroll', function () {
    if (!nav) return;
    if (window.scrollY > 50) {
      nav.style.boxShadow = '0 4px 20px rgba(44,24,16,0.15)';
    } else {
      nav.style.boxShadow = 'none';
    }
  });

  // ===== ACTIVE SECTION HIGHLIGHT =====
  var sections = document.querySelectorAll('section[id]');
  var navLinks = document.querySelectorAll('.nav-link');

  function highlightActiveSection() {
    var scrollY = window.scrollY + window.innerHeight / 2;
    for (var i = sections.length - 1; i >= 0; i--) {
      var section = sections[i];
      if (section.offsetTop <= scrollY) {
        for (var j = 0; j < navLinks.length; j++) {
          navLinks[j].classList.remove('active-link');
          if (navLinks[j].getAttribute('href') === '#' + section.id) {
            navLinks[j].classList.add('active-link');
          }
        }
        break;
      }
    }
  }

  window.addEventListener('scroll', highlightActiveSection);
  highlightActiveSection();

  // ===== HAMBURGER MENU TOGGLE =====
  var hamburger = document.getElementById('hamburger');
  var mobileMenu = document.getElementById('mobile-menu');

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', function () {
      hamburger.classList.toggle('is-active');
      mobileMenu.classList.toggle('is-open');
    });
  }

  // ===== LOGIN MODAL =====
  var loginBtn = document.getElementById('login-btn');
  var loginBtnMobile = document.getElementById('login-btn-mobile');
  var loginModal = document.getElementById('login-modal');
  var closeModal = document.getElementById('close-modal');

  function openModal() {
    if (loginModal) {
      loginModal.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    }
  }

  function hideModal() {
    if (loginModal) {
      loginModal.classList.remove('is-open');
      document.body.style.overflow = '';
    }
  }

  if (loginBtn) loginBtn.addEventListener('click', openModal);
  if (loginBtnMobile) loginBtnMobile.addEventListener('click', openModal);
  if (closeModal) closeModal.addEventListener('click', hideModal);

  if (loginModal) {
    loginModal.addEventListener('click', function (e) {
      if (e.target === loginModal) hideModal();
    });
  }

  // Cerrar modal con Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') hideModal();
  });

  // ===== ANIMATE STAT COUNTERS =====
  var statNumbers = document.querySelectorAll('.stat-number');
  var statsAnimated = [];

  function animateCount(el, index) {
    if (statsAnimated[index]) return;
    statsAnimated[index] = true;

    var target = parseInt(el.getAttribute('data-target') || '0', 10);
    var current = 0;
    var increment = Math.ceil(target / 60);
    var timer = setInterval(function () {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = current.toLocaleString('es-MX');
    }, 30);
  }

  // ===== FADE-IN ON SCROLL (IntersectionObserver) =====
  if ('IntersectionObserver' in window) {

    // Fade-in elements
    var fadeEls = document.querySelectorAll('.fade-in');
    var fadeObserver = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) {
          entries[i].target.classList.add('is-visible');
        }
      }
    }, { threshold: 0.1 });

    for (var i = 0; i < fadeEls.length; i++) {
      fadeObserver.observe(fadeEls[i]);
    }

    // Stat counters
    var statsObserver = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) {
          var idx = Array.prototype.indexOf.call(statNumbers, entries[i].target);
          animateCount(entries[i].target, idx);
          statsObserver.unobserve(entries[i].target);
        }
      }
    }, { threshold: 0.5 });

    for (var i = 0; i < statNumbers.length; i++) {
      statsAnimated.push(false);
      statsObserver.observe(statNumbers[i]);
    }

    // Animate bar fills when visible
    var barFills = document.querySelectorAll('.bar-fill');
    var barsObserver = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) {
          var el = entries[i].target;
          el.style.width = el.getAttribute('data-width');
          barsObserver.unobserve(el);
        }
      }
    }, { threshold: 0.3 });

    for (var i = 0; i < barFills.length; i++) {
      barsObserver.observe(barFills[i]);
    }

  } else {
    // Fallback: mostrar todo sin animacion
    var fadeEls = document.querySelectorAll('.fade-in');
    for (var i = 0; i < fadeEls.length; i++) {
      fadeEls[i].classList.add('is-visible');
    }
    for (var i = 0; i < statNumbers.length; i++) {
      var target = statNumbers[i].getAttribute('data-target') || '0';
      statNumbers[i].textContent = parseInt(target, 10).toLocaleString('es-MX');
    }
    var barFills = document.querySelectorAll('.bar-fill');
    for (var i = 0; i < barFills.length; i++) {
      barFills[i].style.width = barFills[i].getAttribute('data-width');
    }
  }

  // ===== TAB SWITCHING (VISUALIZACION) =====
  var tabBtns = document.querySelectorAll('.tab-btn');
  var tabPanels = document.querySelectorAll('.tab-panel');

  for (var i = 0; i < tabBtns.length; i++) {
    tabBtns[i].addEventListener('click', function () {
      // Quitar activo de todos
      for (var j = 0; j < tabBtns.length; j++) {
        tabBtns[j].classList.remove('tab-active');
      }
      for (var j = 0; j < tabPanels.length; j++) {
        tabPanels[j].classList.remove('is-active');
      }
      // Activar el seleccionado
      this.classList.add('tab-active');
      var targetPanel = document.getElementById(this.getAttribute('data-tab'));
      if (targetPanel) {
        targetPanel.classList.add('is-active');
      }
    });
  }

  // ===== CONTACT FORM =====
  var contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var successMsg = document.getElementById('form-success');
      if (successMsg) {
        successMsg.classList.add('is-visible');
        setTimeout(function () {
          successMsg.classList.remove('is-visible');
        }, 4000);
      }
      contactForm.reset();
    });
  }

  // ===== LOGIN FORM (prevenir recarga) =====
  const loginForm = document.getElementById('login-form');

  if (loginForm) {
    // Cambiamos a 'async function' para poder usar await
    loginForm.addEventListener('submit', async function (e) {
      e.preventDefault();

      // 1. Obtener los valores que ingresó el usuario
      const email = document.getElementById('login-email').value;
      const password = document.getElementById('login-password').value;

      // 2. Formatear los datos como exige OAuth2 (NO como JSON)
      const formData = new URLSearchParams();
      formData.append('username', email); // FastAPI buscará 'username'
      formData.append('password', password);

      try {
        // 3. Enviar la petición al backend
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: formData.toString()
        });

        // Leer la respuesta del servidor
        const data = await response.json();

        if (response.ok) {
          // 4. Guardar el token
          localStorage.setItem('access_token', data.access_token);

          // --- NUEVO: Lógica de Redirección por Rol ---
          try {
            const payloadBase64 = data.access_token.split('.')[1];
            const payload = JSON.parse(atob(payloadBase64));

            console.log("Datos del usuario:", payload);

            const roles = payload.roles || [];

            if (roles.includes('Administrador')) {
              window.location.href = '/PanelAdmin';
            } else if (roles.includes('Especialista')) {
              window.location.href = '/PanelCorpus';
            } else {
              // Un rol por defecto o una página de inicio básica
              window.location.href = '/';
            }
          } catch (decodeError) {
            console.error("Error al leer el token:", decodeError);
            // Si algo falla al decodificar, mandamos a una ruta segura por defecto
            window.location.href = '/';
          }

        } else {
          alert('Error: ' + (data.detail || 'Credenciales incorrectas'));
        }
      } catch (error) {
        console.error('Error en la petición:', error);
        alert('Error de conexión con el servidor.');
      }
    });
  }

});
