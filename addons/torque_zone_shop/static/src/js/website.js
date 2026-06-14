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
        var roots = { shop: 1, about: 1, contact: 1, home: 1, web: 1 };
        if (first && !roots[first] && first.length <= 10) {
            return '/' + first + path;
        }
        var lang = document.documentElement.getAttribute('lang') || '';
        if (lang.indexOf('en') === 0 && path.indexOf('/en/') !== 0) {
            return '/en' + path;
        }
        return path;
    }

    function odooJsonRpc(url, params) {
        params = params || {};
        if (window.odoo && window.odoo.csrf_token) {
            params.csrf_token = window.odoo.csrf_token;
        }
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
            .then(function (res) {
                if (!res.ok) throw new Error('HTTP ' + res.status);
                return res.json();
            })
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

    function showEmptyCart() {
        var checkout = document.querySelector('.tz-checkout');
        var empty = document.getElementById('tzCartEmpty');
        if (checkout) checkout.remove();
        if (empty) {
            empty.style.display = 'block';
            empty.classList.add('is-visible');
            return;
        }
        var block = document.querySelector('.tz-block.tz-wrap');
        if (!block) return;
        block.innerHTML =
            '<div class="tz-empty tz-fade is-visible" id="tzCartEmpty">' +
            '<span>🛒</span><h3>Your cart is empty</h3>' +
            '<p>Browse our shop and add tools to get started.</p>' +
            '<a href="' + tzPath('/shop') + '" class="tz-btn tz-btn-fill">Browse Shop</a></div>';
    }

    function removeCartItem(item) {
        item.style.transition = 'opacity 0.25s, transform 0.25s';
        item.style.opacity = '0';
        item.style.transform = 'scale(0.96)';
        setTimeout(function () { item.remove(); }, 250);
    }

    function applyCartResult(result, item, qtyEl, subtotalEl) {
        updateCartBadge(result.count);

        var totalEl = document.getElementById('tzCartTotal');
        if (totalEl) totalEl.textContent = result.total_formatted;

        if (result.empty) {
            setTimeout(showEmptyCart, 280);
            return;
        }

        if (result.line && result.line.removed) {
            removeCartItem(item);
            var list = document.querySelector('.tz-cart-list');
            if (list && !list.querySelector('.tz-cart-item')) {
                setTimeout(showEmptyCart, 280);
            }
            return;
        }

        if (result.line) {
            if (qtyEl) qtyEl.textContent = result.line.qty;
            if (subtotalEl) subtotalEl.textContent = result.line.subtotal_formatted;
        }
    }

    function initCartActions() {
        var cartList = document.querySelector('.tz-cart-list');
        if (!cartList) return;

        cartList.addEventListener('click', function (ev) {
            var removeBtn = ev.target.closest('.tz-remove[data-product-id]');
            if (removeBtn) {
                ev.preventDefault();
                var item = removeBtn.closest('.tz-cart-item');
                var productId = parseInt(removeBtn.dataset.productId, 10);
                removeBtn.disabled = true;
                odooJsonRpc(tzPath('/shop/cart/remove_item'), { product_id: productId })
                    .then(function (result) {
                        applyCartResult(result, item, null, null);
                    })
                    .catch(function () {
                        window.location.href = tzPath('/shop/cart/remove/' + productId);
                    });
                return;
            }

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
                    applyCartResult(result, item, qtyEl, subtotalEl);
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
        document.querySelectorAll('form[action*="/shop/cart/add"]').forEach(function (form) {
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
        initCartActions();
        initAddToCart();
    });
})();
