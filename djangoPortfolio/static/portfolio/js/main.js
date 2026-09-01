// System Boot Sequence (Top Progress Bar)
const bootLoader = document.getElementById('boot-loader-bar');
let bootProgress = 0;
const bootInterval = setInterval(() => {
    bootProgress += Math.random() * 30;
    if(bootProgress > 90) bootProgress = 90;
    if(bootLoader) bootLoader.style.width = `${bootProgress}%`;
}, 100);

window.addEventListener('load', () => {
    clearInterval(bootInterval);
    if(bootLoader) {
        bootLoader.style.width = '100%';
        setTimeout(() => {
            bootLoader.style.opacity = '0';
            setTimeout(() => bootLoader.remove(), 500);
        }, 500);
    }
});

// --- 1. Custom Cursor Logic ---
if (window.matchMedia('(pointer: fine)').matches) {
    const cursor = document.getElementById('cursor');
    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let cursorX = window.innerWidth / 2;
    let cursorY = window.innerHeight / 2;
    let isMoving = false;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        if (!isMoving) {
            isMoving = true;
            requestAnimationFrame(animateCursor);
        }
    }, { passive: true });

    function lerp(start, end, amt) {
        return (1 - amt) * start + amt * end;
    }

    function animateCursor() {
        cursorX = lerp(cursorX, mouseX, 0.4);
        cursorY = lerp(cursorY, mouseY, 0.4);
        if (cursor) {
            cursor.style.setProperty('--cx', `${cursorX}px`);
            cursor.style.setProperty('--cy', `${cursorY}px`);
        }

        if (Math.abs(mouseX - cursorX) > 0.1 || Math.abs(mouseY - cursorY) > 0.1) {
            requestAnimationFrame(animateCursor);
        } else {
            isMoving = false;
        }
    }

    document.querySelectorAll('.interactive-element').forEach(el => {
        el.addEventListener('mouseenter', () => cursor && cursor.classList.add('hover-state'));
        el.addEventListener('mouseleave', () => cursor && cursor.classList.remove('hover-state'));
    });
}


// --- 2. Magnetic Buttons ---
const magnets = document.querySelectorAll('.magnetic-wrap');
magnets.forEach(magnet => {
    const btn = magnet.querySelector('.btn-magnetic');
    if (!btn) return;
    magnet.addEventListener('mousemove', (e) => {
        const rect = magnet.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;

// Move button slightly towards mouse
        if (typeof gsap !== 'undefined') {
            gsap.to(btn, {
                x: x * 0.4,
                y: y * 0.4,
                duration: 0.5,
                ease: "power2.out"
            });
        }
    });
    magnet.addEventListener('mouseleave', () => {
        if (typeof gsap !== 'undefined') {
            gsap.to(btn, {
                x: 0,
                y: 0,
                duration: 0.7,
                ease: "elastic.out(1, 0.3)"
            });
        }
    });
});


// --- 4. Smooth Scrolling (Lenis) ---
if (typeof Lenis !== 'undefined' && !window.location.pathname.includes('/logging')) {
    const lenis = new Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // easeOutExpo
        direction: 'vertical',
        gestureDirection: 'vertical',
        smooth: true,
        mouseMultiplier: 1,
    });

    function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);
}

// --- 5. GSAP Scroll Animations ---
if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);

    // Generic fade up reveal
    gsap.utils.toArray('.gsap-reveal').forEach(elem => {
        gsap.fromTo(elem,
            { y: 50, opacity: 0 },
            {
                y: 0,
                opacity: 1,
                duration: 1,
                ease: "power3.out",
                scrollTrigger: {
                    trigger: elem,
                    start: "top 85%", // Triggers when element is 85% from top of viewport
                }
            }
        );
    });

    // Staggered reveals for tech stack
    gsap.utils.toArray('.gsap-stagger-container').forEach(container => {
        const items = container.querySelectorAll('.gsap-stagger-item');
        gsap.set(items, { y: 20, opacity: 0 }); // Pre-set to avoid forced reflows from computed style reads
        gsap.to(items, {
            y: 0,
            opacity: 1,
            duration: 0.6,
            stagger: 0.03, // Faster, cheaper CPU overhead
            ease: "power4.out",
            scrollTrigger: {
                trigger: container,
                start: "top 85%",
            }
        });
    });
}


console.log(
    "%c🟢 SYSTEM ONLINE: Josué Leiva\n%c\nLooking under the hood? I like your style. \nI'm a Telematics Engineering student specializing in backend architecture, distributed systems, and real-time telemetry. \n\nLet's build something scalable. \n👉 GitHub: https://github.com/josue-fourier\n👉 LinkedIn: https://linkedin.com/in/josuenicolas",
    "color: #10b981; font-size: 24px; font-weight: 900; font-family: 'Archivo Black', sans-serif; text-shadow: 0 0 10px rgba(16,185,129,0.5);",
    "color: #a6adbb; font-size: 14px; font-family: monospace; line-height: 1.5;"
);

// Ambient Scroll Progress
window.addEventListener('scroll', () => {
    const scrollProgress = document.getElementById("scroll-progress");
    if (scrollProgress) {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        scrollProgress.style.width = scrolled + "%";
    }
});

// --- 7. Frontend Project Filtering ---
const filterBtns = document.querySelectorAll('.tech-filter-btn');
const projectCards = document.querySelectorAll('.project-card');
let activeFilter = null;

if (filterBtns.length > 0 && projectCards.length > 0) {
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tech = btn.getAttribute('data-tech');

            if (activeFilter === tech) {
                // Clear filter
                activeFilter = null;
                filterBtns.forEach(b => {
                    b.classList.remove('border-brand-primary', 'text-brand-primary', 'bg-white', 'shadow-md');
                    b.classList.add('border-slate-200', 'text-slate-700', 'bg-white/80');
                });
                projectCards.forEach(card => {
                    card.style.display = 'block';
                    requestAnimationFrame(() => card.classList.remove('filter-hidden'));
                });
                if (typeof ScrollTrigger !== 'undefined') setTimeout(() => ScrollTrigger.refresh(), 450);
            } else {
                // Apply filter
                activeFilter = tech;
                filterBtns.forEach(b => {
                    if (b === btn) {
                        b.classList.remove('border-slate-200', 'text-slate-700', 'bg-white/80');
                        b.classList.add('border-brand-primary', 'text-brand-primary', 'bg-white', 'shadow-md');
                    } else {
                        b.classList.remove('border-brand-primary', 'text-brand-primary', 'bg-white', 'shadow-md');
                        b.classList.add('border-slate-200', 'text-slate-700', 'bg-white/80');
                    }
                });

                projectCards.forEach(card => {
                    const cardTechs = card.getAttribute('data-techs');
                    if ((`,` + cardTechs).includes(`,${tech},`)) {
                        card.style.display = 'block';
                        requestAnimationFrame(() => card.classList.remove('filter-hidden'));
                    } else {
                        card.classList.add('filter-hidden');
                        setTimeout(() => {
                            if (activeFilter === tech) card.style.display = 'none';
                        }, 400); // Wait for CSS transition
                    }
                });
                if (typeof ScrollTrigger !== 'undefined') setTimeout(() => ScrollTrigger.refresh(), 450);
            }
        });
    });
}

// --- 8. Theme Switcher Persistence ---
const themeController = document.querySelector('.theme-controller');
const htmlTag = document.documentElement;

// Load saved theme
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    htmlTag.setAttribute('data-theme', savedTheme);
    if (themeController) {
        themeController.checked = (savedTheme === 'dracula');
    }
}

// Listen for changes
if (themeController) {
    themeController.addEventListener('change', (e) => {
        const newTheme = e.target.checked ? 'dracula' : 'lofi';
        htmlTag.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}
