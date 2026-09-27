/**
 * SNEAKER SQUAD - PERMANENT USER AUTH & DRAWER ENGINE (auth-drawer.js)
 * Persistent Login across sessions, AJAX Login/Register/Forgot,
 * Live Header User State, and Permanent MySQL Wishlist (❤️).
 */

(function() {
  let currentUser = JSON.parse(localStorage.getItem('sneaker_squad_user') || 'null');
  let currentWishlist = JSON.parse(localStorage.getItem('sneaker_squad_wishlist') || '[]');

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

  function setupAuthDrawer() {
    let drawer = document.getElementById('auth-drawer');
    if (!drawer) {
      const drawerHTML = `
        <div class="auth-drawer-overlay" id="auth-drawer-overlay"></div>
        <aside class="auth-drawer" id="auth-drawer" aria-label="Account Login and Signup">
          <div class="auth-drawer-header">
            <div class="auth-header-brand">
              <i class="fa-solid fa-shoe-prints" style="color: var(--primary);"></i>
              <span>SNEAKER</span> SQUAD
            </div>
            <button class="auth-close-btn" id="auth-close-btn" aria-label="Close Account Panel">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>

          <!-- Auth Tabs (Login / Sign Up) -->
          <div class="auth-tabs-row" id="auth-tabs-row">
            <button type="button" class="auth-tab-btn active" id="tab-login-btn">Log In</button>
            <button type="button" class="auth-tab-btn" id="tab-signup-btn">Create Account</button>
          </div>

          <div class="auth-drawer-body">
            
            <!-- Alert Message Box -->
            <div id="auth-alert-box" style="display:none; padding:12px 16px; border-radius:10px; font-size:0.88rem; font-weight:700; margin-bottom:16px;"></div>

            <!-- View 1: Log In Form -->
            <form class="auth-form-view active" id="form-login-view">
              <div class="auth-welcome-text">
                <h3>Welcome Back!</h3>
                <p>Log in to access your saved kicks, saved addresses, and live order tracking.</p>
              </div>

              <div class="auth-input-group">
                <label for="login-email">Email or Username</label>
                <div class="auth-input-wrapper">
                  <i class="fa-solid fa-envelope input-icon"></i>
                  <input type="text" id="login-email" class="auth-input-field" placeholder="name@domain.com / username" required autocomplete="username">
                </div>
              </div>

              <div class="auth-input-group">
                <label for="login-password">Password</label>
                <div class="auth-input-wrapper">
                  <i class="fa-solid fa-lock input-icon"></i>
                  <input type="password" id="login-password" class="auth-input-field" placeholder="Enter your secret password" required autocomplete="current-password">
                  <button type="button" class="toggle-password-btn" id="btn-toggle-login-pass">
                    <i class="fa-solid fa-eye" id="icon-login-pass"></i>
                  </button>
                </div>
              </div>

              <div class="auth-extra-row">
                <label class="auth-checkbox-label">
                  <input type="checkbox" id="login-remember" checked>
                  <span>Remember me</span>
                </label>
                <a href="#" class="auth-forgot-link" id="auth-forgot-btn">Forgot Password?</a>
              </div>

              <button type="submit" class="btn-auth-submit" id="btn-submit-login">
                <i class="fa-solid fa-arrow-right-to-bracket"></i> Sign In to Squad
              </button>
            </form>

            <!-- View 2: Sign Up Form -->
            <form class="auth-form-view" id="form-signup-view">
              <div class="auth-welcome-text">
                <h3>Join Sneaker Squad</h3>
                <p>Create an account for persistent wishlist & fast 1-click checkout!</p>
              </div>

              <div class="auth-input-group">
                <label for="signup-name">Full Name</label>
                <div class="auth-input-wrapper">
                  <i class="fa-solid fa-user input-icon"></i>
                  <input type="text" id="signup-name" class="auth-input-field" placeholder="Rahul Sharma" required>
                </div>
              </div>

              <div class="auth-input-group">
                <label for="signup-email">Email Address</label>
                <div class="auth-input-wrapper">
                  <i class="fa-solid fa-envelope input-icon"></i>
                  <input type="email" id="signup-email" class="auth-input-field" placeholder="rahul@example.com" required autocomplete="email">
                </div>
              </div>

              <div class="auth-input-group">
                <label for="signup-phone">Mobile Number</label>
                <div class="auth-input-wrapper">
                  <i class="fa-solid fa-phone input-icon"></i>
                  <input type="tel" id="signup-phone" class="auth-input-field" placeholder="9876543210">
                </div>
              </div>

              <div class="auth-input-group">
                <label for="signup-password">Create Password (Min. 6 characters)</label>
                <div class="auth-input-wrapper">
                  <i class="fa-solid fa-lock input-icon"></i>
                  <input type="password" id="signup-password" class="auth-input-field" placeholder="Create strong password" required minlength="6">
                  <button type="button" class="toggle-password-btn" id="btn-toggle-signup-pass">
                    <i class="fa-solid fa-eye" id="icon-signup-pass"></i>
                  </button>
                </div>
              </div>

              <button type="submit" class="btn-auth-submit" id="btn-submit-signup">
                <i class="fa-solid fa-user-plus"></i> Create Squad Account
              </button>
            </form>

            <!-- View 3: Forgot Password Form -->
            <form class="auth-form-view" id="form-forgot-view">
              <div class="auth-welcome-text">
                <h3>Reset Password</h3>
                <p>Enter your registered email to receive password reset instructions.</p>
              </div>

              <div class="auth-input-group">
                <label for="forgot-email">Registered Email</label>
                <div class="auth-input-wrapper">
                  <i class="fa-solid fa-envelope input-icon"></i>
                  <input type="email" id="forgot-email" class="auth-input-field" placeholder="name@domain.com" required>
                </div>
              </div>

              <button type="submit" class="btn-auth-submit">
                <i class="fa-solid fa-paper-plane"></i> Send Reset Link
              </button>

              <div style="text-align:center; margin-top:16px;">
                <a href="#" id="forgot-back-to-login" style="color:var(--primary); font-size:0.88rem; font-weight:700; text-decoration:none;">
                  <i class="fa-solid fa-arrow-left"></i> Back to Login
                </a>
              </div>
            </form>

            <!-- View 4: Logged-in Profile View -->
            <div class="auth-form-view" id="form-profile-view">
              <div class="auth-user-profile-box" style="text-align:center; padding: 15px 0;">
                <div style="position:relative; display:inline-block; margin-bottom:12px;">
                  <img src="https://ui-avatars.com/api/?name=Squad&background=ff5a1f&color=fff" id="profile-avatar-img" style="width:80px; height:80px; border-radius:50%; border:3px solid var(--primary); object-fit:cover; box-shadow:0 6px 20px rgba(255,90,31,0.3);">
                  <span style="position:absolute; bottom:2px; right:2px; background:#22c55e; width:14px; height:14px; border-radius:50%; border:2px solid #14171f;"></span>
                </div>
                <h4 class="auth-user-name" id="profile-user-name" style="font-size:1.25rem; font-weight:900; color:#fff; margin-bottom:3px;">Squad Member</h4>
                <p class="auth-user-email" id="profile-user-email" style="font-size:0.86rem; color:var(--text-muted); margin-bottom:18px;">member@sneakersquad.com</p>
                
                <div style="display: flex; flex-direction: column; gap: 9px; width: 100%;">
                  <a href="/dashboard.html#overview" class="btn btn-primary drawer-dash-link" style="width:100%; justify-content:flex-start; text-decoration:none; padding:12px 16px; font-weight:800; gap:12px; box-sizing:border-box;">
                    <i class="fa-solid fa-gauge-high" style="font-size:1.1rem; width:20px; text-align:center;"></i> My Dashboard Overview
                  </a>
                  <a href="/dashboard.html#orders" class="btn btn-secondary drawer-dash-link" style="width:100%; justify-content:flex-start; text-decoration:none; padding:12px 16px; gap:12px; box-sizing:border-box; color:#fff;">
                    <i class="fa-solid fa-box-open" style="color:var(--primary); font-size:1.1rem; width:20px; text-align:center;"></i> My Orders & Tracking
                  </a>
                  <a href="/dashboard.html#wishlist" class="btn btn-secondary drawer-dash-link" style="width:100%; justify-content:flex-start; text-decoration:none; padding:12px 16px; gap:12px; box-sizing:border-box; color:#fff;">
                    <i class="fa-solid fa-heart" style="color:#ec4899; font-size:1.1rem; width:20px; text-align:center;"></i> My Wishlist (<span id="drawer-wishlist-count">0</span>)
                  </a>
                  <a href="/dashboard.html#addresses" class="btn btn-secondary drawer-dash-link" style="width:100%; justify-content:flex-start; text-decoration:none; padding:12px 16px; gap:12px; box-sizing:border-box; color:#fff;">
                    <i class="fa-solid fa-map-location-dot" style="color:#38bdf8; font-size:1.1rem; width:20px; text-align:center;"></i> Saved Addresses
                  </a>
                  <a href="/dashboard.html#profile" class="btn btn-secondary drawer-dash-link" style="width:100%; justify-content:flex-start; text-decoration:none; padding:12px 16px; gap:12px; box-sizing:border-box; color:#fff;">
                    <i class="fa-solid fa-user-gear" style="color:#a855f7; font-size:1.1rem; width:20px; text-align:center;"></i> Profile & Security
                  </a>
                  <button type="button" class="btn btn-secondary" id="btn-user-logout" style="width:100%; justify-content:flex-start; padding:12px 16px; gap:12px; color:#ef4444; border-color:rgba(239,68,68,0.3); margin-top:6px; box-sizing:border-box; cursor:pointer;">
                    <i class="fa-solid fa-arrow-right-from-bracket" style="font-size:1.1rem; width:20px; text-align:center;"></i> Sign Out
                  </button>
                </div>
              </div>
            </div>

          </div>
        </aside>
      `;
      document.body.insertAdjacentHTML('beforeend', drawerHTML);
    }

    bindAuthEvents();
  }

  function showAlert(msg, isSuccess = false) {
    const alertBox = document.getElementById('auth-alert-box');
    if (!alertBox) return;
    alertBox.style.display = 'block';
    alertBox.style.background = isSuccess ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)';
    alertBox.style.border = isSuccess ? '1px solid #22c55e' : '1px solid #ef4444';
    alertBox.style.color = isSuccess ? '#22c55e' : '#fca5a5';
    alertBox.innerHTML = `${isSuccess ? '<i class="fa-solid fa-circle-check"></i>' : '<i class="fa-solid fa-triangle-exclamation"></i>'} ${msg}`;
  }

  function hideAlert() {
    const alertBox = document.getElementById('auth-alert-box');
    if (alertBox) alertBox.style.display = 'none';
  }

  function openDrawer(view = 'login') {
    setupAuthDrawer();
    const d = document.getElementById('auth-drawer');
    const o = document.getElementById('auth-drawer-overlay');
    hideAlert();

    if (currentUser) {
      showView('profile');
    } else {
      showView(view);
    }

    if (d) d.classList.add('open');
    if (o) o.classList.add('open');
  }

  function closeDrawer() {
    const d = document.getElementById('auth-drawer');
    const o = document.getElementById('auth-drawer-overlay');
    if (d) d.classList.remove('open');
    if (o) o.classList.remove('open');
  }

  function showView(viewName) {
    const tabsRow = document.getElementById('auth-tabs-row');
    const tabLogin = document.getElementById('tab-login-btn');
    const tabSignup = document.getElementById('tab-signup-btn');
    const formLogin = document.getElementById('form-login-view');
    const formSignup = document.getElementById('form-signup-view');
    const formForgot = document.getElementById('form-forgot-view');
    const formProfile = document.getElementById('form-profile-view');

    [formLogin, formSignup, formForgot, formProfile].forEach(f => f && f.classList.remove('active'));

    if (viewName === 'profile') {
      if (tabsRow) tabsRow.style.display = 'none';
      if (formProfile) formProfile.classList.add('active');
    } else {
      if (tabsRow) tabsRow.style.display = 'flex';
      if (viewName === 'login') {
        if (tabLogin) tabLogin.classList.add('active');
        if (tabSignup) tabSignup.classList.remove('active');
        if (formLogin) formLogin.classList.add('active');
      } else if (viewName === 'signup') {
        if (tabSignup) tabSignup.classList.add('active');
        if (tabLogin) tabLogin.classList.remove('active');
        if (formSignup) formSignup.classList.add('active');
      } else if (viewName === 'forgot') {
        if (tabsRow) tabsRow.style.display = 'none';
        if (formForgot) formForgot.classList.add('active');
      }
    }
  }

  function bindAuthEvents() {
    const closeBtn = document.getElementById('auth-close-btn');
    const overlay = document.getElementById('auth-drawer-overlay');
    if (closeBtn) closeBtn.onclick = closeDrawer;
    if (overlay) overlay.onclick = closeDrawer;

    // Tabs
    const tabLogin = document.getElementById('tab-login-btn');
    const tabSignup = document.getElementById('tab-signup-btn');
    if (tabLogin) tabLogin.onclick = () => showView('login');
    if (tabSignup) tabSignup.onclick = () => showView('signup');

    // Forgot password trigger
    const forgotBtn = document.getElementById('auth-forgot-btn');
    const forgotBack = document.getElementById('forgot-back-to-login');
    if (forgotBtn) forgotBtn.onclick = (e) => { e.preventDefault(); showView('forgot'); };
    if (forgotBack) forgotBack.onclick = (e) => { e.preventDefault(); showView('login'); };

    // Password Toggles
    const toggleLoginPass = document.getElementById('btn-toggle-login-pass');
    const inputLoginPass = document.getElementById('login-password');
    const iconLoginPass = document.getElementById('icon-login-pass');
    if (toggleLoginPass && inputLoginPass) {
      toggleLoginPass.onclick = () => {
        if (inputLoginPass.type === 'password') {
          inputLoginPass.type = 'text';
          iconLoginPass.className = 'fa-solid fa-eye-slash';
        } else {
          inputLoginPass.type = 'password';
          iconLoginPass.className = 'fa-solid fa-eye';
        }
      };
    }

    const toggleSignupPass = document.getElementById('btn-toggle-signup-pass');
    const inputSignupPass = document.getElementById('signup-password');
    const iconSignupPass = document.getElementById('icon-signup-pass');
    if (toggleSignupPass && inputSignupPass) {
      toggleSignupPass.onclick = () => {
        if (inputSignupPass.type === 'password') {
          inputSignupPass.type = 'text';
          iconSignupPass.className = 'fa-solid fa-eye-slash';
        } else {
          inputSignupPass.type = 'password';
          iconSignupPass.className = 'fa-solid fa-eye';
        }
      };
    }

    // Login Form Submit (AJAX)
    const formLogin = document.getElementById('form-login-view');
    if (formLogin) {
      formLogin.onsubmit = async (e) => {
        e.preventDefault();
        hideAlert();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
          const res = await fetch('/accounts/api/login/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ email, password })
          });
          const data = await res.json();
          if (data.success) {
            currentUser = data.user;
            currentWishlist = data.wishlist || [];
            localStorage.setItem('sneaker_squad_user', JSON.stringify(currentUser));
            localStorage.setItem('sneaker_squad_wishlist', JSON.stringify(currentWishlist));
            updateHeaderUserState();
            syncWishlistHeartsUI();
            showAlert(data.message, true);
            setTimeout(() => {
              closeDrawer();
            }, 800);
          } else {
            showAlert(data.message || 'Login failed.');
          }
        } catch (err) {
          showAlert('Network error. Please try again.');
        }
      };
    }

    // Sign Up Form Submit (AJAX)
    const formSignup = document.getElementById('form-signup-view');
    if (formSignup) {
      formSignup.onsubmit = async (e) => {
        e.preventDefault();
        hideAlert();
        const full_name = document.getElementById('signup-name').value;
        const email = document.getElementById('signup-email').value;
        const phone = document.getElementById('signup-phone').value;
        const password = document.getElementById('signup-password').value;

        try {
          const res = await fetch('/accounts/api/register/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ full_name, email, phone, password })
          });
          const data = await res.json();
          if (data.success) {
            currentUser = data.user;
            currentWishlist = data.wishlist || [];
            localStorage.setItem('sneaker_squad_user', JSON.stringify(currentUser));
            localStorage.setItem('sneaker_squad_wishlist', JSON.stringify(currentWishlist));
            updateHeaderUserState();
            syncWishlistHeartsUI();
            showAlert(data.message, true);
            setTimeout(() => {
              closeDrawer();
            }, 1000);
          } else {
            showAlert(data.message || 'Registration failed.');
          }
        } catch (err) {
          showAlert('Network error during registration.');
        }
      };
    }

    // Forgot Password Form Submit
    const formForgot = document.getElementById('form-forgot-view');
    if (formForgot) {
      formForgot.onsubmit = async (e) => {
        e.preventDefault();
        hideAlert();
        const email = document.getElementById('forgot-email').value;

        try {
          const res = await fetch('/accounts/api/forgot-password/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ email })
          });
          const data = await res.json();
          if (data.resetUrl) {
            showAlert(`${data.message}<div style="margin-top:10px; padding:10px; background:rgba(0,0,0,0.3); border-radius:8px; text-align:center;"><a href="${data.resetUrl}" style="color:#ff5a1f; font-weight:800; text-decoration:underline; font-size:0.95rem; display:inline-block; margin-bottom:6px;">👉 Click Here To Reset Password Now</a><br><span style="font-size:0.85rem; color:#e2e8f0;">Verification OTP: <strong style="color:#ff5a1f; letter-spacing:2px; font-size:1rem;">${data.otp || ''}</strong></span></div>`, true);
          } else {
            showAlert(data.message, true);
          }
        } catch (err) {
          showAlert('Unable to send reset link.');
        }
      };
    }

    // Dashboard Drawer Links
    document.querySelectorAll('.drawer-dash-link').forEach(link => {
      link.onclick = (e) => {
        closeDrawer();
        const href = link.getAttribute('href');
        if (window.location.pathname.includes('dashboard')) {
          e.preventDefault();
          const hash = href.split('#')[1];
          if (hash) {
            window.location.hash = hash;
            const tabBtn = document.querySelector(`.dash-menu-btn[data-tab="tab-${hash}"]`);
            if (tabBtn) tabBtn.click();
          }
        }
      };
    });

    // Logout button inside drawer
    const logoutBtn = document.getElementById('btn-user-logout');
    if (logoutBtn) {
      logoutBtn.onclick = async () => {
        await fetch('/accounts/api/logout/', {
          method: 'POST',
          headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });
        currentUser = null;
        currentWishlist = [];
        localStorage.removeItem('sneaker_squad_user');
        localStorage.removeItem('sneaker_squad_wishlist');
        updateHeaderUserState();
        syncWishlistHeartsUI();
        showView('login');
        closeDrawer();
        if (typeof showToast === 'function') {
          showToast('Signed out successfully. Come back soon!', 'fa-right-from-bracket');
        }
        if (window.location.pathname.includes('dashboard')) {
          window.location.href = '/';
        }
      };
    }
  }

  // Update Header User Profile Icon & Tooltips
  function updateHeaderUserState() {
    const authBtn = document.getElementById('auth-btn');
    const headerIcon = document.getElementById('header-user-icon');
    const wishBadge = document.getElementById('header-wishlist-badge');
    const drawerWishCount = document.getElementById('drawer-wishlist-count');
    const dashWishCount = document.getElementById('dash-wish-count');

    const count = currentWishlist.length;

    if (currentUser) {
      if (authBtn) {
        authBtn.title = `Signed in as ${currentUser.displayName} (Click for Dashboard)`;
        authBtn.setAttribute('aria-label', `Account: ${currentUser.displayName}`);
      }
      if (headerIcon) {
        headerIcon.className = 'fa-solid fa-user-check';
        headerIcon.style.color = 'var(--primary)';
      }
      const pName = document.getElementById('profile-user-name');
      const pEmail = document.getElementById('profile-user-email');
      const pAvatar = document.getElementById('profile-avatar-img');
      if (pName) pName.textContent = currentUser.displayName;
      if (pEmail) pEmail.textContent = currentUser.email;
      if (pAvatar && currentUser.avatar) pAvatar.src = currentUser.avatar;

      if (wishBadge) {
        wishBadge.textContent = count;
        wishBadge.style.display = count > 0 ? 'flex' : 'none';
      }
      if (drawerWishCount) drawerWishCount.textContent = count;
      if (dashWishCount) dashWishCount.textContent = count;
    } else {
      if (authBtn) {
        authBtn.title = 'Account Login / Sign Up';
        authBtn.setAttribute('aria-label', 'Account');
      }
      if (headerIcon) {
        headerIcon.className = 'fa-regular fa-user';
        headerIcon.style.color = '';
      }
      if (wishBadge) {
        wishBadge.textContent = count;
        wishBadge.style.display = count > 0 ? 'flex' : 'none';
      }
      if (drawerWishCount) drawerWishCount.textContent = count;
      if (dashWishCount) dashWishCount.textContent = count;
    }
  }

  // Sync filled heart status across all shoe cards on the page
  function syncWishlistHeartsUI() {
    document.querySelectorAll('.wishlist-btn').forEach(btn => {
      const card = btn.closest('.product-card') || btn.closest('.product-gallery-sticky');
      let prodId = null;
      if (card) {
        prodId = card.getAttribute('data-id');
      }
      if (!prodId) {
        const urlParams = new URLSearchParams(window.location.search);
        prodId = urlParams.get('id');
      }

      if (prodId && currentWishlist.map(s => String(s).toLowerCase()).includes(String(prodId).toLowerCase())) {
        btn.classList.add('active');
        const icon = btn.querySelector('i');
        if (icon) {
          icon.className = 'fa-solid fa-heart';
          icon.style.color = '#ec4899';
        }
      } else {
        btn.classList.remove('active');
        const icon = btn.querySelector('i');
        if (icon) {
          icon.className = 'fa-regular fa-heart';
          icon.style.color = '';
        }
      }
    });
  }

  // Core Wishlist Toggle Engine
  async function handleWishlistToggle(prodId, prodName, prodPrice, prodImg) {
    if (!currentUser) {
      openDrawer('login');
      showAlert('Please log in to save kicks to your permanent squad wishlist!');
      return;
    }

    if (!prodId) return;

    try {
      const res = await fetch('/accounts/api/wishlist/toggle/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
          product_id: prodId,
          product_name: prodName,
          product_price: prodPrice,
          product_image: prodImg
        })
      });
      const data = await res.json();
      if (data.success) {
        currentWishlist = data.wishlist || [];
        localStorage.setItem('sneaker_squad_wishlist', JSON.stringify(currentWishlist));
        updateHeaderUserState();
        syncWishlistHeartsUI();
        if (typeof showToast === 'function') {
          showToast(data.message, data.action === 'added' ? 'fa-heart' : 'fa-trash');
        }
      } else if (data.requireLogin) {
        openDrawer('login');
        showAlert(data.message);
      }
    } catch (err) {
      console.error('Wishlist error:', err);
    }
  }

  // Global Wishlist Button Click Event Listener
  document.addEventListener('click', (e) => {
    const wishBtn = e.target.closest('.wishlist-btn');
    if (!wishBtn) return;
    e.preventDefault();
    e.stopPropagation();

    const card = wishBtn.closest('.product-card') || wishBtn.closest('.product-gallery-sticky');
    let prodId = null;
    let prodName = '';
    let prodPrice = 0;
    let prodImg = '';

    if (card) {
      prodId = card.getAttribute('data-id');
      const titleEl = card.querySelector('.product-title a') || card.querySelector('#product-title');
      if (titleEl) prodName = titleEl.textContent;
      const priceEl = card.querySelector('.current-price') || card.querySelector('#product-current-price');
      if (priceEl) {
        prodPrice = parseFloat(priceEl.textContent.replace(/[^0-9.]/g, '')) || 0;
      }
      const imgEl = card.querySelector('img');
      if (imgEl) prodImg = imgEl.src;
    }
    if (!prodId) {
      const urlParams = new URLSearchParams(window.location.search);
      prodId = urlParams.get('id');
      const titleEl = document.getElementById('product-title');
      if (titleEl) prodName = titleEl.textContent;
      const priceEl = document.getElementById('product-current-price');
      if (priceEl) prodPrice = parseFloat(priceEl.textContent.replace(/[^0-9.]/g, '')) || 0;
      const imgEl = document.getElementById('main-product-img');
      if (imgEl) prodImg = imgEl.src;
    }

    handleWishlistToggle(prodId, prodName, prodPrice, prodImg);
  });

  // Global Auth Trigger Button Click Delegate
  document.addEventListener('click', (e) => {
    const authBtn = e.target.closest('#auth-btn, .auth-trigger-btn');
    if (authBtn) {
      e.preventDefault();
      openDrawer();
    }
  });

  // Fetch initial user state on page load and sync with Django backend
  document.addEventListener('DOMContentLoaded', async () => {
    setupAuthDrawer();
    updateHeaderUserState();
    syncWishlistHeartsUI();

    try {
      const res = await fetch('/accounts/api/user-state/');
      const data = await res.json();
      if (data.isAuthenticated) {
        currentUser = data.user;
        currentWishlist = data.wishlist || [];
        localStorage.setItem('sneaker_squad_user', JSON.stringify(currentUser));
        localStorage.setItem('sneaker_squad_wishlist', JSON.stringify(currentWishlist));
        updateHeaderUserState();
        syncWishlistHeartsUI();
      } else {
        // If server says unauthenticated, clear local state
        currentUser = null;
        currentWishlist = [];
        localStorage.removeItem('sneaker_squad_user');
        localStorage.removeItem('sneaker_squad_wishlist');
        updateHeaderUserState();
        syncWishlistHeartsUI();
      }
    } catch (err) {
      console.warn('User state server hydration offline.');
    }
  });

  window.openAuthDrawer = openDrawer;
  window.closeAuthDrawer = closeDrawer;
  window.handleWishlistToggle = handleWishlistToggle;
  window.syncWishlistHeartsUI = syncWishlistHeartsUI;
})();
