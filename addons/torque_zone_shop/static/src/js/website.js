(function () {
    'use strict';

    function initNav() {
        var nav = document.getElementById('tzwNav');
        var toggle = document.getElementById('tzwNavToggle');
        var menu = document.getElementById('tzwMenu');
        if (!nav) return;

        window.addEventListener('scroll', function () {
            nav.classList.toggle('tzw-scrolled', window.scrollY > 20);
        }, { passive: true });

        if (toggle && menu) {
            toggle.addEventListener('click', function () {
                menu.classList.toggle('tzw-open');
                toggle.classList.toggle('tzw-open');
            });
            menu.querySelectorAll('.tzw-menu-link').forEach(function (link) {
                link.addEventListener('click', function () {
                    menu.classList.remove('tzw-open');
                    toggle.classList.remove('tzw-open');
                });
            });
        }
    }

    function initAnimateIn() {
        if (!window.IntersectionObserver) return;
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('tzw-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.06, rootMargin: '0px 0px -30px 0px' });

        document.querySelectorAll('.tzw-animate-in, .tzw-reveal').forEach(function (el) {
            observer.observe(el);
        });
    }

    function initQtySteppers() {
        document.querySelectorAll('.tzw-qty-stepper:not(.tzw-qty-stepper-cart)').forEach(function (wrap) {
            var input = wrap.querySelector('.tzw-qty-input');
            var valueEl = wrap.querySelector('.tzw-qty-value');
            var minus = wrap.querySelector('.tzw-qty-minus');
            var plus = wrap.querySelector('.tzw-qty-plus');
            if (!input || !valueEl) return;

            function setQty(n) {
                n = Math.max(1, n);
                input.value = n;
                valueEl.textContent = n;
            }

            if (minus) minus.addEventListener('click', function () { setQty(parseInt(input.value, 10) - 1); });
            if (plus) plus.addEventListener('click', function () { setQty(parseInt(input.value, 10) + 1); });
        });
    }

    function initAddToCart() {
        document.querySelectorAll('form[action="/shop/cart/add"]').forEach(function (form) {
            form.addEventListener('submit', function () {
                var btn = form.querySelector('button[type="submit"]');
                if (btn && !btn.disabled) {
                    btn.disabled = true;
                    btn.classList.add('tzw-loading');
                    var label = btn.textContent;
                    btn.dataset.label = label;
                    btn.textContent = 'Adding…';
                }
            });
        });
    }

    function initPageEnter() {
        var main = document.querySelector('.tzw-main');
        if (main) main.classList.add('tzw-page-enter');
    }

    document.addEventListener('DOMContentLoaded', function () {
        initNav();
        initAnimateIn();
        initQtySteppers();
        initAddToCart();
        initPageEnter();
    });
})();
