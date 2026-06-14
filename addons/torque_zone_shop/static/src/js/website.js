(function () {
    'use strict';

    function initHeader() {
        var header = document.getElementById('tzHeader');
        var burger = document.getElementById('tzBurger');
        var nav = document.getElementById('tzNav');
        if (!header) return;

        window.addEventListener('scroll', function () {
            header.classList.toggle('is-scrolled', window.scrollY > 16);
        }, { passive: true });

        if (burger && nav) {
            burger.addEventListener('click', function () {
                nav.classList.toggle('is-open');
                burger.classList.toggle('is-open');
            });
            nav.querySelectorAll('.tz-nav-link').forEach(function (link) {
                link.addEventListener('click', function () {
                    nav.classList.remove('is-open');
                    burger.classList.remove('is-open');
                });
            });
        }
    }

    function initFadeIn() {
        if (!window.IntersectionObserver) {
            document.querySelectorAll('.tz-fade').forEach(function (el) {
                el.classList.add('is-visible');
            });
            return;
        }
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

        document.querySelectorAll('.tz-fade').forEach(function (el) {
            observer.observe(el);
        });
    }

    function initQtySteppers() {
        document.querySelectorAll('[data-qty-stepper]').forEach(function (wrap) {
            var input = wrap.querySelector('.tz-qty-input');
            var valueEl = wrap.querySelector('.tz-qty-val');
            var minus = wrap.querySelector('.tz-qty-minus');
            var plus = wrap.querySelector('.tz-qty-plus');
            if (!input || !valueEl) return;

            function setQty(n) {
                n = Math.max(1, n);
                input.value = n;
                valueEl.textContent = n;
            }

            if (minus) minus.addEventListener('click', function () {
                setQty(parseInt(input.value, 10) - 1);
            });
            if (plus) plus.addEventListener('click', function () {
                setQty(parseInt(input.value, 10) + 1);
            });
        });
    }

    function initAddToCart() {
        document.querySelectorAll('form[action="/shop/cart/add"]').forEach(function (form) {
            form.addEventListener('submit', function () {
                var btn = form.querySelector('button[type="submit"]');
                if (btn && !btn.disabled) {
                    btn.disabled = true;
                    btn.classList.add('is-loading');
                    btn.textContent = 'Adding…';
                }
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initHeader();
        initFadeIn();
        initQtySteppers();
        initAddToCart();
    });
})();
