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

    function tzPath(path) {
        var parts = window.location.pathname.split('/').filter(Boolean);
        var first = parts[0] || '';
        var roots = { shop: 1, about: 1, contact: 1, home: 1 };
        if (first && !roots[first] && first.length <= 10) {
            return '/' + first + path;
        }
        return path;
    }

    function odooJsonRpc(url, params) {
        return fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: params,
                id: Date.now(),
            }),
        })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.error) throw new Error(data.error.message || 'Request failed');
                return data.result;
            });
    }

    function updateCartBadge(count) {
        document.querySelectorAll('.tz-cart-count').forEach(function (el) {
            el.textContent = count;
        });
    }

    function initCartQty() {
        var cartList = document.querySelector('.tz-cart-list');
        if (!cartList) return;

        cartList.addEventListener('click', function (ev) {
            var btn = ev.target.closest('.tz-qty-cart .tz-qty-btn[data-action]');
            if (!btn || btn.disabled) return;

            ev.preventDefault();
            var wrap = btn.closest('.tz-qty-cart');
            var item = btn.closest('.tz-cart-item');
            if (!wrap || !item) return;

            var productId = parseInt(wrap.dataset.productId, 10);
            var action = btn.dataset.action;
            var qtyEl = wrap.querySelector('.tz-qty-val');
            var subtotalEl = item.querySelector('.tz-line-subtotal');

            btn.disabled = true;
            wrap.classList.add('is-busy');

            odooJsonRpc(tzPath('/shop/cart/update_qty'), { product_id: productId, action: action })
                .then(function (result) {
                    updateCartBadge(result.count);

                    if (result.empty) {
                        window.location.reload();
                        return;
                    }

                    var totalEl = document.getElementById('tzCartTotal');
                    if (totalEl) totalEl.textContent = result.total_formatted;

                    if (result.line) {
                        if (result.line.removed) {
                            item.style.transition = 'opacity 0.25s, transform 0.25s';
                            item.style.opacity = '0';
                            item.style.transform = 'scale(0.96)';
                            setTimeout(function () { item.remove(); }, 250);
                        } else {
                            if (qtyEl) qtyEl.textContent = result.line.qty;
                            if (subtotalEl) subtotalEl.textContent = result.line.subtotal_formatted;
                        }
                    }
                })
                .catch(function () {
                    window.location.href = action === 'dec'
                        ? tzPath('/shop/cart/dec/' + productId)
                        : tzPath('/shop/cart/inc/' + productId);
                })
                .finally(function () {
                    btn.disabled = false;
                    wrap.classList.remove('is-busy');
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
        initCartQty();
        initAddToCart();
    });
})();
