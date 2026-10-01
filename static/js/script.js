/**
 * SNEAKER SQUAD - E-COMMERCE SCRIPT (script.js)
 * Modern Vanilla JavaScript for Cart, Live Search, Dynamic Sorting,
 * Active Nav Detection, Mobile Drawer, and Toast Notifications.
 * Formatted with Indian Rupee (₹) currency.
 */

// Global State
let cart = JSON.parse(localStorage.getItem('sneaker_squad_cart')) || [];

document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initActiveNavLink();
  initMobileMenu();
  initCart();
  initLiveSearch();
  initCategoryFilters();
  initProductSorting();
  initWishlist();
  initNewsletter();
  initUrlParamsFilter();
});

/* ==========================================================================
   0. STOREFRONT THEME TOGGLE (Light / Dark Mode with Persistence)
   ========================================================================== */
function initThemeToggle() {
  const toggleBtn = document.getElementById('theme-toggle-btn');
  const themeIcon = document.getElementById('theme-icon');
  const savedTheme = localStorage.getItem('sneaker_store_theme');

  if (savedTheme === 'light') {
    document.documentElement.classList.add('light-theme');
    document.body.classList.add('light-theme');
    if (themeIcon) {
      themeIcon.classList.remove('fa-moon');
      themeIcon.classList.add('fa-sun');
    }
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const isLight = document.body.classList.toggle('light-theme');
      document.documentElement.classList.toggle('light-theme', isLight);

      if (isLight) {
        localStorage.setItem('sneaker_store_theme', 'light');
        if (themeIcon) {
          themeIcon.classList.remove('fa-moon');
          themeIcon.classList.add('fa-sun');
        }
      } else {
        localStorage.setItem('sneaker_store_theme', 'dark');
        if (themeIcon) {
          themeIcon.classList.remove('fa-sun');
          themeIcon.classList.add('fa-moon');
        }
      }
    });
  }
}


/* ==========================================================================
   1. ACTIVE NAVIGATION LINK DETECTION
   ========================================================================== */
function initActiveNavLink() {
  const currentPath = window.location.pathname;
  const pageName = currentPath.substring(currentPath.lastIndexOf('/') + 1) || 'index.html';
  
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href === pageName || (pageName === '' && href === 'index.html')) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

/* ==========================================================================
   2. MOBILE HAMBURGER MENU & DRAWER
   ========================================================================== */
function initMobileMenu() {
  const mobileToggle = document.getElementById('mobile-menu-toggle') || document.querySelector('.mobile-toggle');
  const navMenu = document.getElementById('nav-menu') || document.querySelector('.nav-menu');
  const overlay = document.getElementById('mobile-menu-overlay');
  const closeBtn = document.getElementById('drawer-close-btn');

  function openDrawer() {
    const m = document.getElementById('nav-menu') || document.querySelector('.nav-menu');
    const o = document.getElementById('mobile-menu-overlay');
    if (m) m.classList.add('open');
    if (o) o.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    const m = document.getElementById('nav-menu') || document.querySelector('.nav-menu');
    const o = document.getElementById('mobile-menu-overlay');
    if (m) m.classList.remove('open');
    if (o) o.classList.remove('open');
    document.body.style.overflow = '';
  }

  // Global document click delegation for 100% reliable trigger on all mobile browsers
  document.addEventListener('click', (e) => {
    const toggle = e.target.closest('#mobile-menu-toggle, .mobile-toggle');
    if (toggle) {
      e.preventDefault();
      e.stopPropagation();
      const m = document.getElementById('nav-menu') || document.querySelector('.nav-menu');
      if (m && m.classList.contains('open')) {
        closeDrawer();
      } else {
        openDrawer();
      }
      return;
    }

    const close = e.target.closest('#drawer-close-btn, .drawer-close-btn');
    if (close) {
      e.preventDefault();
      e.stopPropagation();
      closeDrawer();
      return;
    }

    const ov = e.target.closest('#mobile-menu-overlay, .mobile-menu-overlay');
    if (ov) {
      closeDrawer();
      return;
    }

    const navLink = e.target.closest('#nav-menu .nav-link, .mobile-drawer-panel .nav-link, .nav-menu .nav-link');
    if (navLink) {
      closeDrawer();
    }
  });
}

/* ==========================================================================
   3. CART FUNCTIONALITY (ADD TO CART, DRAWER, QUANTITY, LOCALSTORAGE)
   ========================================================================== */
function openCartDrawer() {
  const cartDrawer = document.getElementById('cart-drawer');
  const cartOverlay = document.getElementById('cart-drawer-overlay');
  renderCartItems();
  updateCartBadge();
  if (cartDrawer) {
    cartDrawer.classList.add('open');
    cartDrawer.classList.add('active');
  }
  if (cartOverlay) {
    cartOverlay.classList.add('open');
    cartOverlay.classList.add('active');
  }
}

function closeCartDrawer() {
  const cartDrawer = document.getElementById('cart-drawer');
  const cartOverlay = document.getElementById('cart-drawer-overlay');
  if (cartDrawer) {
    cartDrawer.classList.remove('open');
    cartDrawer.classList.remove('active');
  }
  if (cartOverlay) {
    cartOverlay.classList.remove('open');
    cartOverlay.classList.remove('active');
  }
}

window.openCartDrawer = openCartDrawer;
window.closeCartDrawer = closeCartDrawer;

function initCart() {
  updateCartBadge();
  renderCartItems();

  // Delegated Global Click Listener for Cart Trigger
  document.addEventListener('click', (e) => {
    const cartTrigger = e.target.closest('#cart-btn, .cart-btn, [aria-label="Shopping Bag"], .open-cart-trigger');
    if (cartTrigger) {
      e.preventDefault();
      e.stopPropagation();
      openCartDrawer();
      return;
    }

    const closeBtn = e.target.closest('#cart-close-btn, .cart-close-btn');
    if (closeBtn) {
      e.preventDefault();
      closeCartDrawer();
      return;
    }

    const overlay = e.target.closest('#cart-drawer-overlay');
    if (overlay) {
      closeCartDrawer();
      return;
    }
  });

  // Bind Add to Cart Buttons
  document.querySelectorAll('.btn-add-cart').forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const card = this.closest('.product-card');
      if (!card) return;

      const id = card.getAttribute('data-id') || Math.random().toString(36).substr(2, 9);
      const title = card.querySelector('.product-title')?.innerText || 'Sneaker';
      const priceAttr = card.getAttribute('data-price');
      const price = priceAttr ? parseFloat(priceAttr) : (parseFloat(card.querySelector('.current-price')?.innerText.replace(/[^0-9.]/g, '')) || 0);
      const image = card.querySelector('.product-image-box img')?.src || '';

      addToCart({ id, title, price, image });
      showToast(`Added <strong>${title}</strong> to your bag!`, 'fa-bag-shopping');
    });
  });

  // Checkout modal and triggers
  initCheckoutModal();
}

let activeDiscountPercent = 0;

function initCheckoutModal() {
  const checkoutBtn = document.getElementById('btn-checkout');
  const modalOverlay = document.getElementById('checkout-modal-overlay');
  const modalClose = document.getElementById('checkout-modal-close');
  const form = document.getElementById('expressCheckoutForm');
  const cartDrawer = document.getElementById('cart-drawer');
  const cartOverlay = document.getElementById('cart-drawer-overlay');
  const applyCouponBtn = document.getElementById('btn_apply_coupon');
  const couponInput = document.getElementById('chk_coupon');
  const couponMsg = document.getElementById('coupon-msg');
  const errAlert = document.getElementById('checkout-error-alert');

  // Order Success Modal elements
  const successModal = document.getElementById('order-success-modal');
  const successModalClose = document.getElementById('success-modal-close');

  if (checkoutBtn && modalOverlay) {
    checkoutBtn.addEventListener('click', () => {
      if (!cart || cart.length === 0) {
        showToast('Your bag is empty! Add kicks to proceed.', 'fa-triangle-exclamation');
        return;
      }
      // Close cart drawer & open modal
      if (cartDrawer && cartOverlay) {
        cartDrawer.classList.remove('open');
        cartOverlay.classList.remove('open');
      }
      activeDiscountPercent = 0;
      updateCheckoutSummary();
      modalOverlay.style.display = 'flex';
    });
  }

  if (modalClose && modalOverlay) {
    modalClose.addEventListener('click', () => {
      modalOverlay.style.display = 'none';
    });
  }

  if (successModalClose && successModal) {
    successModalClose.addEventListener('click', () => {
      successModal.style.display = 'none';
    });
  }

  if (applyCouponBtn && couponInput) {
    applyCouponBtn.addEventListener('click', () => {
      const code = couponInput.value.trim().toUpperCase();
      if (code === 'SQUAD20') {
        activeDiscountPercent = 20;
        couponMsg.style.display = 'block';
        couponMsg.style.color = '#4ade80';
        couponMsg.innerHTML = '<i class="fa-solid fa-circle-check"></i> Code <strong>SQUAD20</strong> applied! 20% discount unlocked.';
        updateCheckoutSummary();
      } else if (code === '') {
        activeDiscountPercent = 0;
        couponMsg.style.display = 'none';
        updateCheckoutSummary();
      } else {
        couponMsg.style.display = 'block';
        couponMsg.style.color = '#f87171';
        couponMsg.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Invalid promo code. Try <strong>SQUAD20</strong>';
      }
    });
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errAlert.style.display = 'none';

      const submitBtn = document.getElementById('chk_submit_btn');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Placing Order...';

      let subtotal = cart.reduce((sum, item) => sum + (item.price * (item.qty || item.quantity || 1)), 0);
      let discount = subtotal * (activeDiscountPercent / 100);
      let shipping = (subtotal - discount) >= 2999 ? 0 : (subtotal > 0 ? 150 : 0);
      let grandTotal = (subtotal - discount) + shipping;

      const selectedPayment = document.querySelector('input[name="chk_payment"]:checked')?.value || 'RAZORPAY';

      const orderPayload = {
        full_name: document.getElementById('chk_name').value.trim(),
        phone: document.getElementById('chk_phone').value.trim(),
        email: document.getElementById('chk_email').value.trim(),
        address: document.getElementById('chk_address').value.trim(),
        city: document.getElementById('chk_city').value.trim(),
        postal_code: document.getElementById('chk_pincode').value.trim(),
        payment_method: selectedPayment,
        total_amount: grandTotal,
        items: cart.map(it => ({
          id: it.id,
          name: it.title || it.name,
          price: it.price,
          quantity: it.qty || it.quantity || 1,
          size: it.size || '',
          color: it.color || ''
        }))
      };

      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      }

      function handleOrderSuccess(data) {
        // Clear cart
        cart = [];
        saveCart();
        updateCartBadge();
        renderCartItems();

        // Hide checkout modal
        modalOverlay.style.display = 'none';
        form.reset();

        // Show confirmation modal
        const formattedOrderId = data.order_id || 'SQUAD-ORDER';
        const orderIdEl = document.getElementById('success-order-id');
        if (orderIdEl) orderIdEl.innerText = `#${formattedOrderId}`;

        const invoiceBtn = document.getElementById('success-invoice-btn');
        if (invoiceBtn) {
          invoiceBtn.href = data.invoice_url || `/accounts/order/${formattedOrderId}/invoice/`;
        }

        const estEl = document.getElementById('success-est-delivery');
        if (estEl && data.estimated_delivery) {
          estEl.innerText = `${data.estimated_delivery} (${data.courier || 'Blue Dart'})`;
        }

        if (successModal) successModal.style.display = 'flex';
        showToast(`Order #${formattedOrderId} placed! 🚀`, 'fa-circle-check');
      }

      try {
        // Option 1: ONLINE PAYMENT VIA RAZORPAY (UPI, QR, CARDS, NETBANKING)
        if (selectedPayment === 'RAZORPAY' || selectedPayment === 'UPI') {
          submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Initializing Payment Gateway...';
          
          const createRes = await fetch('/api/payment/create-order/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(orderPayload)
          });

          const createData = await createRes.json();
          if (!createRes.ok || !createData.success) {
            throw new Error(createData.message || 'Failed to initialize payment gateway.');
          }

          // Check if Razorpay JS SDK loaded
          if (typeof Razorpay !== 'undefined' && createData.key_id && !createData.key_id.startsWith('rzp_test_squadsneakers')) {
            const rzpOptions = {
              key: createData.key_id,
              amount: createData.amount,
              currency: createData.currency || 'INR',
              name: 'SNEAKERS SQUADS',
              description: `Order #${createData.order_id} - Verified Deadstock Kicks`,
              image: '/static/img/shoe-1.jpg',
              order_id: createData.razorpay_order_id,
              handler: async function (paymentResponse) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Verifying Payment Signature...';
                
                try {
                  const verifyRes = await fetch('/api/payment/verify/', {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                      order_id: createData.order_id,
                      razorpay_order_id: paymentResponse.razorpay_order_id,
                      razorpay_payment_id: paymentResponse.razorpay_payment_id,
                      razorpay_signature: paymentResponse.razorpay_signature
                    })
                  });
                  const verifyData = await verifyRes.json();
                  if (verifyRes.ok && verifyData.success) {
                    handleOrderSuccess(verifyData);
                  } else {
                    errAlert.style.display = 'block';
                    errAlert.innerText = verifyData.message || 'Payment signature verification failed.';
                  }
                } catch (vErr) {
                  errAlert.style.display = 'block';
                  errAlert.innerText = 'Error while verifying transaction with server.';
                } finally {
                  submitBtn.disabled = false;
                  submitBtn.innerHTML = '<i class="fa-solid fa-lock"></i> Proceed to Pay Securely';
                }
              },
              prefill: {
                name: createData.customer_name,
                email: createData.customer_email,
                contact: createData.customer_phone
              },
              theme: {
                color: '#ff5a1f'
              },
              modal: {
                ondismiss: function () {
                  submitBtn.disabled = false;
                  submitBtn.innerHTML = '<i class="fa-solid fa-lock"></i> Proceed to Pay Securely';
                  showToast('Payment window was closed. Try again when ready.', 'fa-circle-info');
                }
              }
            };

            const rzp = new Razorpay(rzpOptions);
            rzp.on('payment.failed', function (resp) {
              errAlert.style.display = 'block';
              errAlert.innerText = `Payment Failed: ${resp.error.description || 'Transaction declined'}`;
              submitBtn.disabled = false;
              submitBtn.innerHTML = '<i class="fa-solid fa-lock"></i> Proceed to Pay Securely';
            });
            rzp.open();
          } else {
            // Test Mode Instant Simulator (Seamlessly verifies and confirms without real bank charge)
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Test Payment (UPI / QR)...';
            
            const verifyRes = await fetch('/api/payment/verify/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
              },
              body: JSON.stringify({
                order_id: createData.order_id,
                razorpay_order_id: createData.razorpay_order_id,
                razorpay_payment_id: `pay_test_${Math.random().toString(36).substring(2, 11)}`,
                razorpay_signature: 'test_signature_valid'
              })
            });

            const verifyData = await verifyRes.json();
            if (verifyRes.ok && verifyData.success) {
              handleOrderSuccess(verifyData);
            } else {
              throw new Error(verifyData.message || 'Payment confirmation failed.');
            }
          }
        } else {
          // Option 2: CASH ON DELIVERY (COD)
          const response = await fetch('/api/checkout/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(orderPayload)
          });

          const data = await response.json();
          if (response.ok && (data.status === 'success' || data.success)) {
            handleOrderSuccess(data);
          } else {
            errAlert.style.display = 'block';
            errAlert.innerText = data.message || 'Failed to place order. Please check details.';
          }
        }
      } catch (err) {
        errAlert.style.display = 'block';
        errAlert.innerText = err.message || 'Network error while connecting to server. Please try again.';
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fa-solid fa-lock"></i> Proceed to Pay Securely';
      }
    });
  }
}


function updateCheckoutSummary() {
  const subtotalEl = document.getElementById('chk_summary_subtotal');
  const discountRow = document.getElementById('chk_discount_row');
  const discountEl = document.getElementById('chk_summary_discount');
  const shippingEl = document.getElementById('chk_summary_shipping');
  const totalEl = document.getElementById('chk_summary_total');

  let subtotal = cart.reduce((sum, item) => sum + (item.price * (item.qty || item.quantity || 1)), 0);
  let discount = subtotal * (activeDiscountPercent / 100);
  let shipping = (subtotal - discount) >= 2999 ? 0 : (subtotal > 0 ? 150 : 0);
  let grandTotal = (subtotal - discount) + shipping;

  if (subtotalEl) subtotalEl.innerText = `₹${subtotal.toLocaleString('en-IN')}`;
  if (discountRow && discountEl) {
    if (activeDiscountPercent > 0) {
      discountRow.style.display = 'flex';
      discountEl.innerText = `-₹${discount.toLocaleString('en-IN')}`;
    } else {
      discountRow.style.display = 'none';
    }
  }
  if (shippingEl) {
    shippingEl.innerText = shipping === 0 ? 'FREE' : `₹${shipping}`;
    shippingEl.style.color = shipping === 0 ? '#4ade80' : '#fff';
  }
  if (totalEl) totalEl.innerText = `₹${grandTotal.toLocaleString('en-IN')}`;
}


function addToCart(product) {
  if (typeof product === 'string') {
    const pData = (typeof PRODUCTS_DATA !== 'undefined' && PRODUCTS_DATA[product]) ? PRODUCTS_DATA[product] : null;
    if (pData) {
      product = {
        id: pData.id,
        name: pData.name,
        price: pData.price,
        image: pData.mainImage,
        size: pData.sizes ? pData.sizes[0] : 'UK 8'
      };
    } else {
      product = { id: product, name: 'Sneaker Squad Kicks', price: 9999, image: '', size: 'UK 8' };
    }
  }

  const existingItem = cart.find(item => item.id === product.id && (!product.size || item.size === product.size));
  if (existingItem) {
    existingItem.qty += 1;
  } else {
    cart.push({ ...product, qty: 1 });
  }

  saveCart();
  updateCartBadge();
  renderCartItems();
  animateCartBadge();
  if (typeof showToast === 'function') {
    showToast(`${product.name} added to Bag! ⚡`, 'fa-cart-plus');
  }
}

function updateQuantity(id, delta) {
  const item = cart.find(item => item.id === id);
  if (!item) return;

  item.qty += delta;
  if (item.qty <= 0) {
    cart = cart.filter(i => i.id !== id);
  }

  saveCart();
  updateCartBadge();
  renderCartItems();
}

function removeFromCart(id) {
  cart = cart.filter(item => item.id !== id);
  saveCart();
  updateCartBadge();
  renderCartItems();
  showToast('Item removed from bag', 'fa-trash-can');
}

function saveCart() {
  localStorage.setItem('sneaker_squad_cart', JSON.stringify(cart));
}

function updateCartBadge() {
  cart = JSON.parse(localStorage.getItem('sneaker_squad_cart')) || [];
  const totalCount = cart.reduce((sum, item) => sum + (item.qty || item.quantity || 1), 0);
  const badges = document.querySelectorAll('.cart-badge');
  badges.forEach(badge => {
    badge.innerText = totalCount;
  });
}

function animateCartBadge() {
  const badges = document.querySelectorAll('.cart-badge');
  badges.forEach(badge => {
    badge.classList.add('bump');
    setTimeout(() => {
      badge.classList.remove('bump');
    }, 250);
  });
}

function renderCartItems() {
  cart = JSON.parse(localStorage.getItem('sneaker_squad_cart')) || [];
  const cartContainer = document.getElementById('cart-drawer-body');
  const subtotalEl = document.getElementById('cart-subtotal');
  if (!cartContainer || !subtotalEl) return;

  if (cart.length === 0) {
    cartContainer.innerHTML = `
      <div class="cart-empty-state">
        <i class="fa-solid fa-shoe-prints" style="font-size: 2.8rem; color: #cbd5e1; margin-bottom: 12px; display: block;"></i>
        <p style="font-weight: 600;">Your bag is currently empty.</p>
        <small style="color: var(--text-muted); display: block; margin-top: 6px;">Add some fresh kicks to step up your rotation!</small>
      </div>
    `;
    subtotalEl.innerText = '₹0';
    return;
  }

  let subtotal = 0;
  cartContainer.innerHTML = cart.map(item => {
    const itemQty = item.qty || item.quantity || 1;
    const itemTotal = item.price * itemQty;
    subtotal += itemTotal;

    const colorBadge = item.color ? `<span class="cart-variant-badge color"><i class="fa-solid fa-palette"></i> ${item.color}</span>` : '';
    const sizeBadge = item.size ? `<span class="cart-variant-badge size">${item.size}</span>` : '';

    return `
      <div class="cart-item">
        <img src="${item.image}" alt="${item.title || item.name}" class="cart-item-img">
        <div class="cart-item-info">
          <div class="cart-item-title">${item.title || item.name}</div>
          <div class="cart-item-variants-row">
            ${colorBadge}
            ${sizeBadge}
          </div>
          <div class="cart-item-price">₹${item.price.toLocaleString('en-IN')}</div>
          <div class="cart-item-controls">
            <button class="qty-btn" onclick="updateQuantity('${item.id}', -1)">-</button>
            <span class="cart-item-qty">${itemQty}</span>
            <button class="qty-btn" onclick="updateQuantity('${item.id}', 1)">+</button>
            <button class="cart-item-remove" onclick="removeFromCart('${item.id}')" title="Remove item">
              <i class="fa-regular fa-trash-can"></i>
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');

  subtotalEl.innerText = `₹${subtotal.toLocaleString('en-IN')}`;
}

// Make helper functions globally accessible for inline onclicks
window.updateQuantity = updateQuantity;
window.removeFromCart = removeFromCart;

/* ==========================================================================
   4. REAL-TIME LIVE SEARCH FILTER & DROPDOWN
   ========================================================================== */
function initLiveSearch() {
  const searchInput = document.querySelector('.search-input');
  const searchDropdown = document.getElementById('search-dropdown');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    filterProductsByQuery(query);
    showSearchSuggestions(query, searchDropdown);
  });

  const searchForm = document.querySelector('.search-form');
  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const query = searchInput.value.toLowerCase().trim();
      const productCards = document.querySelectorAll('.product-grid .product-card');
      if (productCards.length === 0 && query) {
        window.location.href = `men.html?q=${encodeURIComponent(query)}`;
      } else {
        filterProductsByQuery(query);
      }
    });
  }

  // Close dropdown on click outside
  document.addEventListener('click', (e) => {
    if (searchDropdown && !searchDropdown.contains(e.target) && !searchInput.contains(e.target)) {
      searchDropdown.style.display = 'none';
    }
  });
}

function showSearchSuggestions(query, dropdown) {
  if (!dropdown) return;
  if (!query || query.length < 2) {
    dropdown.style.display = 'none';
    dropdown.innerHTML = '';
    return;
  }

  // Look up products in PRODUCTS_DATA (if available) or search existing cards
  let matches = [];
  if (typeof PRODUCTS_DATA !== 'undefined') {
    matches = Object.values(PRODUCTS_DATA).filter(p => 
      p.name.toLowerCase().includes(query) || 
      (p.brand && p.brand.toLowerCase().includes(query)) ||
      (p.category && p.category.toLowerCase().includes(query))
    ).slice(0, 6);
  }

  if (matches.length === 0) {
    dropdown.innerHTML = `<div style="padding: 14px; text-align: center; color: #94a3b8; font-size: 0.88rem;"><i class="fa-solid fa-magnifying-glass"></i> No sneakers found for "${query}"</div>`;
    dropdown.style.display = 'block';
    return;
  }

  dropdown.innerHTML = matches.map(p => `
    <a href="product-detail.html?id=${p.id}" style="display: flex; align-items: center; gap: 12px; padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.06); text-decoration: none; color: #fff; transition: background 0.2s ease;">
      <img src="${p.mainImage || (p.colors && p.colors[0] ? p.colors[0].mainImage : '')}" alt="${p.name}" style="width: 42px; height: 42px; object-fit: cover; border-radius: 8px; background: #0b0d13;">
      <div style="flex: 1;">
        <div style="font-weight: 700; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${p.name}</div>
        <div style="font-size: 0.78rem; color: #94a3b8;">${p.brand || 'Sneaker'} &bull; ${p.category || 'Footwear'}</div>
      </div>
      <div style="color: #ff5a1f; font-weight: 800; font-size: 0.92rem;">₹${Number(p.price).toLocaleString('en-IN')}</div>
    </a>
  `).join('') + `
    <div style="padding: 8px; text-align: center; background: #0b0d13; border-radius: 0 0 12px 12px;">
      <a href="men.html?q=${encodeURIComponent(query)}" style="font-size: 0.82rem; color: #ff5a1f; font-weight: 700; text-decoration: none;">View all results &rarr;</a>
    </div>
  `;
  dropdown.style.display = 'block';
}


// Filter & Search Global State
window.currentCategoryFilter = 'all';
window.currentSearchFilter = '';

function isCardMatchingCategory(card, filterValue) {
  if (!filterValue || filterValue === 'all') return true;

  const f = filterValue.toLowerCase().trim();
  const cardTag = (card.getAttribute('data-tag') || '').toLowerCase();
  const cardCat = (card.getAttribute('data-category') || '').toLowerCase();
  const title = (card.querySelector('.product-title')?.innerText || '').toLowerCase();
  const meta = (card.querySelector('.product-category-meta')?.innerText || '').toLowerCase();

  // 1. Semantic aliases for perfect filtering
  if (f === 'high-top' || f === 'high-tops' || f === 'hightop') {
    return cardTag.includes('high') || cardCat.includes('high') || meta.includes('high') || title.includes('high');
  }
  if (f === 'chunky') {
    return cardTag.includes('chunky') || cardCat.includes('chunky') || meta.includes('chunky') || title.includes('chunky');
  }
  if (f === 'platform') {
    return cardTag.includes('platform') || cardCat.includes('platform') || meta.includes('platform') || title.includes('platform');
  }
  if (f === 'running') {
    return cardTag.includes('run') || cardCat.includes('run') || meta.includes('run') || title.includes('run') || cardTag.includes('gym');
  }
  if (f === 'basketball') {
    return cardTag.includes('basketball') || cardCat.includes('basketball') || meta.includes('basketball') || cardTag.includes('court') || meta.includes('court');
  }
  if (f === 'retro') {
    return cardTag.includes('retro') || cardCat.includes('retro') || meta.includes('retro') || cardTag.includes('vintage') || meta.includes('vintage') || cardTag.includes('classic');
  }

  // 2. Token & Substring Matching
  const tagTokens = cardTag.split(/\s+/).filter(Boolean);
  return tagTokens.includes(f) ||
         cardTag.includes(f) ||
         cardCat.includes(f) ||
         title.includes(f) ||
         meta.includes(f);
}

function applyAllFilters() {
  const productCards = document.querySelectorAll('.product-grid .product-card');
  if (productCards.length === 0) return;

  const catFilter = (window.currentCategoryFilter || 'all').toLowerCase().trim();
  const searchFilter = (window.currentSearchFilter || '').toLowerCase().trim();

  let visibleCount = 0;

  productCards.forEach(card => {
    const cardTag = (card.getAttribute('data-tag') || '').toLowerCase();
    const cardCat = (card.getAttribute('data-category') || '').toLowerCase();
    const title = (card.querySelector('.product-title')?.innerText || '').toLowerCase();
    const meta = (card.querySelector('.product-category-meta')?.innerText || '').toLowerCase();

    // 1. Category Tag Matching
    const matchesCategory = isCardMatchingCategory(card, catFilter);

    // 2. Search Query Matching
    let matchesSearch = true;
    if (searchFilter.length > 0) {
      matchesSearch = title.includes(searchFilter) ||
                      meta.includes(searchFilter) ||
                      cardTag.includes(searchFilter) ||
                      cardCat.includes(searchFilter);
    }

    if (matchesCategory && matchesSearch) {
      card.style.display = 'flex';
      visibleCount++;
    } else {
      card.style.display = 'none';
    }
  });

  // Manage No Results State
  let noResults = document.getElementById('no-results');
  const productGrid = document.querySelector('.product-grid');
  if (!noResults && productGrid) {
    noResults = document.createElement('div');
    noResults.id = 'no-results';
    noResults.style.gridColumn = '1 / -1';
    noResults.style.textAlign = 'center';
    noResults.style.padding = '48px 20px';
    noResults.style.color = '#94a3b8';
    noResults.innerHTML = `
      <div style="font-size: 2.8rem; margin-bottom: 12px; color: #ff5a1f;"><i class="fa-solid fa-shoe-prints"></i></div>
      <h3 style="font-size: 1.35rem; font-weight: 800; color: #fff; margin-bottom: 8px;">No Matching Items Found</h3>
      <p style="font-size: 0.92rem; margin-bottom: 18px;">Try selecting another category filter or resetting your search.</p>
      <button type="button" class="btn btn-primary" onclick="resetAllProductFilters()" style="display: inline-flex; align-items: center; gap: 8px; margin: 0 auto; padding: 10px 22px;">
        <i class="fa-solid fa-rotate-left"></i> View All Items
      </button>
    `;
    productGrid.appendChild(noResults);
  }

  if (noResults) {
    noResults.style.display = visibleCount === 0 ? 'block' : 'none';
  }

  updateProductCount(visibleCount);
}

function filterProductsByQuery(query) {
  window.currentSearchFilter = query || '';
  applyAllFilters();
}

window.resetAllProductFilters = function() {
  window.currentCategoryFilter = 'all';
  window.currentSearchFilter = '';
  
  const filterButtons = document.querySelectorAll('.filter-btn');
  filterButtons.forEach(b => {
    if ((b.getAttribute('data-filter') || 'all').toLowerCase() === 'all') {
      b.classList.add('active');
    } else {
      b.classList.remove('active');
    }
  });

  const searchInput = document.querySelector('.search-input');
  if (searchInput) searchInput.value = '';

  applyAllFilters();
};

/* ==========================================================================
   5. CATEGORY FILTER PILLS
   ========================================================================== */
function initCategoryFilters() {
  const filterButtons = document.querySelectorAll('.filter-btn');
  if (filterButtons.length === 0) return;

  filterButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Clear search input when user switches categories to prevent blocking results
      const searchInput = document.querySelector('.search-input');
      if (searchInput) searchInput.value = '';
      window.currentSearchFilter = '';
      const searchDropdown = document.getElementById('search-dropdown');
      if (searchDropdown) searchDropdown.style.display = 'none';

      const filterValue = (btn.getAttribute('data-filter') || 'all').toLowerCase();
      window.currentCategoryFilter = filterValue;
      applyAllFilters();
    });
  });
}

/* ==========================================================================
   6. DYNAMIC SORTING (PRICE, RATING, NAME)
   ========================================================================== */
function initProductSorting() {
  const sortSelect = document.getElementById('sort-select');
  const productGrid = document.querySelector('.product-grid');

  if (!sortSelect || !productGrid) return;

  sortSelect.addEventListener('change', () => {
    const sortValue = sortSelect.value;
    const cards = Array.from(productGrid.querySelectorAll('.product-card'));

    cards.sort((a, b) => {
      const priceA = parseFloat(a.getAttribute('data-price')) || 0;
      const priceB = parseFloat(b.getAttribute('data-price')) || 0;
      const ratingA = parseFloat(a.getAttribute('data-rating')) || 0;
      const ratingB = parseFloat(b.getAttribute('data-rating')) || 0;
      const titleA = a.querySelector('.product-title')?.innerText.toLowerCase() || '';
      const titleB = b.querySelector('.product-title')?.innerText.toLowerCase() || '';

      switch (sortValue) {
        case 'price-low-high':
          return priceA - priceB;
        case 'price-high-low':
          return priceB - priceA;
        case 'rating-high':
          return ratingB - ratingA;
        case 'name-az':
          return titleA.localeCompare(titleB);
        default:
          return 0;
      }
    });

    // Re-append in sorted order (keeping no-results placeholder at the end)
    const noResults = document.getElementById('no-results');
    cards.forEach(card => productGrid.appendChild(card));
    if (noResults) {
      productGrid.appendChild(noResults);
    }
  });
}

function updateProductCount(count) {
  const countEl = document.getElementById('products-count-text');
  if (countEl) {
    const isAccessories = window.location.pathname.includes('accessories');
    const itemWord = isAccessories ? (count === 1 ? 'item' : 'items') : (count === 1 ? 'sneaker' : 'sneakers');
    countEl.innerText = `Showing ${count} ${itemWord}`;
  }
}

/* ==========================================================================
   7. WISHLIST SYNC (Managed by auth-drawer.js full-stack engine)
   ========================================================================== */
function initWishlist() {
  if (window.syncWishlistHeartsUI) {
    window.syncWishlistHeartsUI();
  }
}

/* ==========================================================================
   8. NEWSLETTER SUBSCRIPTION
   ========================================================================== */
function initNewsletter() {
  const form = document.querySelector('.newsletter-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = form.querySelector('.newsletter-input');
    if (input && input.value.trim() !== '') {
      showToast(`Subscribed successfully with ${input.value.trim()}! 🎁`, 'fa-paper-plane');
      input.value = '';
    }
  });
}

/* ==========================================================================
   9. TOAST NOTIFICATION UTILITY
   ========================================================================== */
function showToast(message, iconClass = 'fa-circle-check') {
  let toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `
    <i class="fa-solid ${iconClass}"></i>
    <span>${message}</span>
  `;

  toastContainer.appendChild(toast);

  // Trigger animation
  requestAnimationFrame(() => {
    toast.classList.add('show');
  });

  // Auto remove after 3.2s
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3200);
}

/* ==========================================================================
   10. URL PARAMETERS & DIRECT FILTER ENGINE
   ========================================================================== */

function initUrlParamsFilter() {
  const params = new URLSearchParams(window.location.search);
  const q = params.get('q') || params.get('search');
  const tag = params.get('tag') || params.get('filter') || params.get('cat') || params.get('category');

  if (q) {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) searchInput.value = q;
    window.currentSearchFilter = q;
  }

  if (tag) {
    const targetTag = tag.toLowerCase().trim();
    window.currentCategoryFilter = targetTag;
    const targetPill = document.querySelector(`.filter-btn[data-filter="${targetTag}"]`);
    if (targetPill) {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      targetPill.classList.add('active');
    }
  }

  applyAllFilters();
}
