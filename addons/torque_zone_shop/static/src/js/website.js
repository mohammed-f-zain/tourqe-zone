(function () {
    'use strict';

    function initNav() {
        var nav = document.getElementById('tzwNav');
        var toggle = document.getElementById('tzwNavToggle');
        var menu = document.getElementById('tzwMenu');
        if (!nav) return;

        window.addEventListener('scroll', function () {
            nav.classList.toggle('tzw-scrolled', window.scrollY > 40);
        }, { passive: true });

        if (toggle && menu) {
            toggle.addEventListener('click', function () {
                menu.classList.toggle('tzw-open');
            });
            menu.querySelectorAll('.tzw-menu-link').forEach(function (link) {
                link.addEventListener('click', function () {
                    menu.classList.remove('tzw-open');
                });
            });
        }
    }

    function initReveal() {
        if (!window.IntersectionObserver) {
            document.querySelectorAll('.tzw-reveal').forEach(function (el) {
                el.style.opacity = '1';
            });
            return;
        }
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

        document.querySelectorAll('.tzw-reveal').forEach(function (el) {
            el.style.animationPlayState = 'paused';
            observer.observe(el);
        });
    }

    function initForms() {
        document.querySelectorAll('form[action="/shop/cart/add"]').forEach(function (form) {
            form.addEventListener('submit', function () {
                var btn = form.querySelector('button[type="submit"]');
                if (btn) {
                    btn.disabled = true;
                    btn.textContent = 'Adding…';
                }
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initNav();
        initReveal();
        initForms();
    });
})();
