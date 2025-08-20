/* >>>>>>>>>   PAGINA DE INICIO   <<<<<<<<< */


// FUNCIONALIDAD DE FILTROS DE EVENTOS
// ==============================
document.addEventListener('DOMContentLoaded', function() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const eventCards = document.querySelectorAll('.event-card');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remover clase active de todos los botones
            filterBtns.forEach(b => b.classList.remove('active'));
            // Agregar clase active al botón clickeado
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            
            eventCards.forEach(card => {
                if (filter === 'all' || card.classList.contains(filter)) {
                    card.classList.remove('hidden');
                    // Animación de entrada
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                } else {
                    card.classList.add('hidden');
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                }
            });
        });
    });
    
    // Animación inicial de las tarjetas
    eventCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// ==============================
// SMOOTH SCROLLING PARA ENLACES INTERNOS
// ==============================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==============================
// TOGGLE MENÚ MÓVIL
// ==============================
const mobileMenuBtn = document.getElementById('mobile-menu-btn');
const mobileMenu = document.getElementById('mobile-menu');

if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('active');
    });

    // Cerrar menú móvil al hacer clic en un enlace
    document.querySelectorAll('#mobile-menu a').forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
        });
    });
}

// ==============================
// CAMBIO DE FONDO EN LA NAVBAR AL HACER SCROLL
// ==============================
window.addEventListener('scroll', () => {
    const nav = document.querySelector('nav');
    if (!nav) return;

    if (window.scrollY > 100) {
        nav.classList.add('bg-white/98');
        nav.classList.remove('bg-white/95');
    } else {
        nav.classList.add('bg-white/95');
        nav.classList.remove('bg-white/98');
    }
});

// ==============================
// ANIMACIÓN DE CONTADORES
// ==============================
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    const timer = setInterval(() => {
        start += increment;
        element.textContent = Math.floor(start);
        
        if (start >= target) {
            element.textContent = target;
            clearInterval(timer);
        }
    }, 16);
}

// ==============================
// OBSERVADOR PARA ACTIVAR ANIMACIÓN DE CONTADORES CUANDO SON VISIBLES
// ==============================
const observerOptions = {
    threshold: 0.5,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const counter = entry.target;
            const target = parseInt(counter.getAttribute('data-target'));
            animateCounter(counter, target);
            observer.unobserve(counter);
        }
    });
}, observerOptions);

// Observar todos los elementos con clase .counter
document.querySelectorAll('.counter').forEach(counter => {
    observer.observe(counter);
});

// ==============================
// EFECTO PARALLAX PARA LA SECCIÓN HERO
// ==============================
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroSection = document.getElementById('inicio');
    const rate = scrolled * -0.5;
    
    if (heroSection) {
        heroSection.style.transform = `translateY(${rate}px)`;
    }
});

// ==============================
// ANIMACIÓN DE CARGA (AL CARGAR LA PÁGINA)
// ==============================
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});

// ==============================


/* >>>>>> FIN DE LOS .JS PARA LA PAGINA INICIAL ( ABAJO OTROS .JS DE OTROS MODULOS)<<<<<<< */