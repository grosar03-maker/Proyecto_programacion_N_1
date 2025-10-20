// =========================================================================
// ARCHIVO: script.js
// CUMPLE CON TODOS LOS REQUISITOS (CON VALIDACIÓN DETALLADA Y RANKING DINÁMICO)
// =========================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM completamente cargado. Inicializando scripts.");

    const noticiasContainer = document.getElementById('noticias-container');
    if (noticiasContainer) {
        cargarNoticias(noticiasContainer, 'obtener_noticias.php');
    }

    const form = document.getElementById('formulario');
    if (form) {
        form.addEventListener('submit', function(ev) {
            manejarEnvioFormulario(ev, this);
        });
    }

    const rankingContainer = document.getElementById('ranking-dinamico');
    if (rankingContainer) {
        inicializarRankingDinamico();
    }

    inicializarEfectosVisuales();
});

// ========================================================
// FUNCIÓN 1: Cargar noticias usando FETCH
// ========================================================
function cargarNoticias(container, url) {
    console.log(`Iniciando fetch de noticias desde: ${url}`);
    
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`Error HTTP! estado: ${response.status}`);
            return response.json();
        })
        .then(noticias => {
            console.log("Noticias recibidas de la BD:", noticias);
            if (noticias.length === 0) {
                container.innerHTML = '<p>No hay noticias para mostrar en este momento.</p>';
                return;
            }
            
            container.innerHTML = ''; // Limpiar el contenedor

            noticias.forEach(noticia => {
                const card = document.createElement('article');
                card.className = 'card reveal';
                card.setAttribute('aria-labelledby', `title-${noticia.id}`);
                card.innerHTML = `
                    <figure>
                        <img src="${noticia.url_imagen}" alt="${noticia.alt_imagen}" loading="lazy">
                        <figcaption>Foto: Unsplash</figcaption>
                    </figure>
                    <div class="card-body">
                        <h3 id="title-${noticia.id}">${noticia.titulo}</h3>
                        <p>${noticia.descripcion}</p>
                        <p class="meta">Fuente: ${noticia.fuente} — ${noticia.fecha_publicacion}</p>
                        <a class="btn" target="_blank" rel="noopener" href="${noticia.url_noticia}">Leer en ${noticia.fuente}</a>
                    </div>
                `;
                container.appendChild(card);
            });
            
            document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
        })
        .catch(error => {
            console.error('Error al cargar las noticias:', error);
            container.innerHTML = '<p>Hubo un error al cargar las noticias. Revisa la consola para más detalles.</p>';
        });
}

// ========================================================
// FUNCIÓN 2: Manejar el envío del formulario (VERSIÓN CON VALIDACIÓN DETALLADA)
// ========================================================
function manejarEnvioFormulario(evento, formulario) {
    console.log("Interceptando envío de formulario...");
    evento.preventDefault();

    const submitButton = formulario.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = 'Enviando...';

    const nombre = formulario.querySelector('#nombre');
    const email = formulario.querySelector('#email');
    const mensaje = formulario.querySelector('#mensaje');
    const helpText = formulario.querySelector('#form-help');

    // === INICIO DE LA VALIDACIÓN DETALLADA ===
    // En lugar de una sola validación, revisamos cada campo y cada regla por separado
    // para dar un mensaje de error específico.

    // 1. Validar el campo Nombre
    if (nombre.value.trim() === '') {
        mostrarNotificacion(helpText, 'El campo Nombre es obligatorio.', 'error');
        submitButton.disabled = false;
        submitButton.textContent = 'Enviar';
        return;
    }
    if (nombre.value.length < 2) {
        mostrarNotificacion(helpText, 'El nombre debe tener al menos 2 caracteres.', 'error');
        submitButton.disabled = false;
        submitButton.textContent = 'Enviar';
        return;
    }
    const namePattern = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/;
    if (!namePattern.test(nombre.value)) {
        mostrarNotificacion(helpText, 'El nombre solo puede contener letras y espacios.', 'error');
        submitButton.disabled = false;
        submitButton.textContent = 'Enviar';
        return;
    }

    // 2. Validar el campo Correo
    if (email.value.trim() === '') {
        mostrarNotificacion(helpText, 'El campo Correo es obligatorio.', 'error');
        submitButton.disabled = false;
        submitButton.textContent = 'Enviar';
        return;
    }
    // Usamos checkValidity() aquí específicamente para el formato de email
    if (!email.checkValidity()) {
        mostrarNotificacion(helpText, 'Por favor, ingresa un formato de correo válido (ej: tu@correo.com).', 'error');
        submitButton.disabled = false;
        submitButton.textContent = 'Enviar';
        return;
    }

    // 3. Validar el campo Mensaje
    if (mensaje.value.trim() === '') {
        mostrarNotificacion(helpText, 'El campo Mensaje es obligatorio.', 'error');
        submitButton.disabled = false;
        submitButton.textContent = 'Enviar';
        return;
    }
    if (mensaje.value.length < 10) {
        mostrarNotificacion(helpText, 'El mensaje debe tener al menos 10 caracteres.', 'error');
        submitButton.disabled = false;
        submitButton.textContent = 'Enviar';
        return;
    }
    
    // Si todas las validaciones pasan, limpiamos el mensaje de ayuda antes de enviar.
    mostrarNotificacion(helpText, '', 'success');
    // === FIN DE LA VALIDACIÓN DETALLADA ===

    const formData = new FormData(formulario);
    fetch(formulario.action, {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(respuesta => {
        console.log("Respuesta del servidor (guardar_contacto.php):", respuesta);
        mostrarNotificacion(helpText, respuesta, 'success');
        formulario.reset();
    })
    .catch(error => {
        console.error('Error al enviar el formulario:', error);
        mostrarNotificacion(helpText, 'Error de conexión. No se pudo enviar el mensaje.', 'error');
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.textContent = 'Enviar';
    });
}

// ========================================================
// FUNCIÓN 3: Mostrar notificación al usuario
// ========================================================
function mostrarNotificacion(elemento, mensaje, tipo) {
    console.log(`Mostrando notificación: [${tipo}] ${mensaje}`);
    elemento.textContent = mensaje;
    elemento.style.color = tipo === 'success' ? '#a7f3d0' : '#ff8a8a';
}

// ========================================================
// FUNCIÓN 4: Inicializar la sección de Ranking Dinámico
// ========================================================
function inicializarRankingDinamico() {
    console.log("Inicializando funcionalidad de ranking dinámico.");
    const select = document.getElementById('innovacion-select');
    const detalleContainer = document.getElementById('innovacion-detalle');

    fetch('obtener_innovaciones.php')
        .then(response => {
            if (!response.ok) throw new Error(`Error HTTP! estado: ${response.status}`);
            return response.json();
        })
        .then(innovaciones => {
            console.log("Innovaciones recibidas de la BD:", innovaciones);
            if (innovaciones.length > 0) {
                select.innerHTML = '<option value="">-- Elige una opción --</option>';
                innovaciones.forEach(innovacion => {
                    const option = document.createElement('option');
                    option.value = innovacion.id;
                    option.textContent = innovacion.nombre;
                    select.appendChild(option);
                });
                select.addEventListener('change', function() {
                    mostrarDetalleInnovacion(this, innovaciones, detalleContainer);
                });
            } else {
                select.innerHTML = '<option value="">No hay innovaciones para mostrar</option>';
            }
        })
        .catch(error => {
            console.error('Error al cargar las innovaciones:', error);
            detalleContainer.innerHTML = '<p>Hubo un error al cargar los datos del ranking.</p>';
        });
}

// ========================================================
// FUNCIÓN 5: Mostrar detalles de la innovación seleccionada (VERSIÓN CON IMAGEN)
// ========================================================
function mostrarDetalleInnovacion(selectElement, innovaciones, container) {
    console.log("Mostrando detalle para la innovación seleccionada.");
    const idSeleccionado = selectElement.value;
    
    if (!idSeleccionado) {
        container.innerHTML = '';
        return;
    }

    const innovacionEncontrada = innovaciones.find(i => i.id == idSeleccionado);

    if (innovacionEncontrada) {
        container.innerHTML = `
            <figure class="innovacion-figure">
                <img src="${innovacionEncontrada.url_imagen}" alt="${innovacionEncontrada.alt_imagen}" loading="lazy">
                <figcaption>${innovacionEncontrada.nombre}</figcaption>
            </figure>
            <div>
                <h3>${innovacionEncontrada.nombre}</h3>
                <p class="meta"><strong>Categoría:</strong> ${innovacionEncontrada.categoria}</p>
                <p class="meta"><strong>Impacto Estimado:</strong> ${innovacionEncontrada.impacto}</p>
                <p>${innovacionEncontrada.descripcion}</p>
            </div>
        `;
    }
}

// ========================================================
// Funciones de efectos visuales (código original + observer)
// ========================================================
let observer;

function inicializarEfectosVisuales() {
    console.log("Inicializando efectos visuales (scroll, mouse glow, theme switch).");
    
    observer = new IntersectionObserver((entries) => {
        entries.forEach(e => {
            if (e.isIntersecting) e.target.classList.add('visible');
        });
    }, { threshold: .15 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

    document.addEventListener('pointermove', (e) => {
        document.documentElement.style.setProperty('--mx', e.clientX + 'px');
        document.documentElement.style.setProperty('--my', e.clientY + 'px');
    });

    const titulo = document.getElementById('titulo');
    if (titulo) {
        let dark = true;
        titulo.addEventListener('click', function() {
            dark = !dark;
            cambiarTema(this, dark);
        });
    }
}

function cambiarTema(elemento, esOscuro) {
    console.log(`Cambiando tema. Es oscuro: ${esOscuro}`);
    document.body.style.background = esOscuro
        ? 'radial-gradient(1200px 600px at 20% 10%, #0ff3, transparent), radial-gradient(800px 800px at 80% 0%, #f0f3, transparent), #0d1117'
        : 'linear-gradient(135deg,#0d1117 0%,#1f1144 60%,#2b0f3b 100%)';
}