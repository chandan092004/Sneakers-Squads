/**
 * SNEAKER SQUAD - PERMANENT USER AUTH & DRAWER ENGINE (auth-drawer.js)
 * Persistent Login across sessions, AJAX Login/Register/Forgot,
 * Live Header User State, and Permanent MySQL Wishlist (❤️).
 */

(function() {
  let currentUser = JSON.parse(localStorage.getItem('sneaker_squad_user') || 'null');
  let currentWishlist = JSON.parse(localStorage.getItem('sneaker_squad_wishlist') || '[]');
  let currentAuthToken = localStorage.getItem('sneaker_squad_auth_token') || '';

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
    let overlay = document.getElementById('auth-drawer-overlay');
    if (drawer && !document.getElementById('form-newpass-view')) {
      drawer.remove();
      if (overlay) overlay.remove();
      drawer = null;
    }
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

            <!-- View 3: Step 1 - Forgot Password (Request OTP) -->
            <form class="auth-form-view" id="form-forgot-view">
              <div class="auth-welcome-text">
                <h3>Forgot Password</h3>
                <p>Enter your registered <strong>Email Address</strong> to receive a 6-digit verification OTP.</p>
              </div>

              <div class="auth-input-group">
                <label for="forgot-identifier">Registered Email Address</label>
                <div class="auth-input-wrapper">
                  <i class="fa-solid fa-envelope input-icon"></i>
                  <input type="email" id="forgot-identifier" class="auth-input-field" placeholder="name@domain.com" required autocomplete="email">
                </div>
              </div>

              <button type="submit" class="btn-auth-submit" id="btn-submit-forgot">
                <i class="fa-solid fa-paper-plane"></i> Send OTP
              </button>

              <div style="text-align:center; margin-top:16px;">
                <a href="#" id="forgot-back-to-login" style="color:var(--primary); font-size:0.88rem; font-weight:700; text-decoration:none;">
                  <i class="fa-solid fa-arrow-left"></i> Back to Login
                </a>
              </div>
            </form>

            <!-- View 5: Step 2 - Verify 6-Digit OTP -->
            <form class="auth-form-view" id="form-otp-view">
              <div class="auth-welcome-text">
                <h3 style="color:#ffffff !important; font-weight:800; font-size:1.45rem;"><i class="fa-solid fa-shield-halved" style="color:var(--primary);"></i> Verify OTP</h3>
                <p id="otp-instruction-text" style="color:#cbd5e1;">OTP sent to your email.</p>
              </div>

              <input type="hidden" id="otp-hidden-identifier">
              <input type="hidden" id="otp-hidden-token">

              <div class="auth-input-group">
                <label for="otp-code-input">6-Digit Verification Code</label>
                <div class="auth-input-wrapper">
                  <i class="fa-solid fa-key input-icon"></i>
                  <input type="text" id="otp-code-input" class="auth-input-field" placeholder="------" maxlength="6" style="letter-spacing: 6px; font-size: 1.35rem; font-weight: 900; text-align: center; color: var(--primary); font-family: monospace;" required autocomplete="one-time-code">
                </div>
              </div>

              <button type="submit" class="btn-auth-submit" id="btn-submit-otp-verify">
                <i class="fa-solid fa-circle-check"></i> Verify OTP
              </button>

              <div style="display:flex; justify-content:space-between; align-items:center; margin-top:16px; font-size:0.85rem;">
                <a href="#" id="otp-back-to-forgot" style="color:#94a3b8; text-decoration:none; font-weight:600;">
                  <i class="fa-solid fa-arrow-left"></i> Change Email
                </a>
                <a href="#" id="otp-resend-link" style="color:var(--primary); text-decoration:none; font-weight:700; cursor:pointer;">
                  <i class="fa-solid fa-rotate-right"></i> Resend OTP<span id="otp-resend-timer"></span>
                </a>
              </div>
            </form>

            <!-- View 6: Step 3 - Reset Password -->
            <form class="auth-form-view" id="form-newpass-view">
              <div class="auth-welcome-text">
                <h3 style="color:#ffffff !important; font-weight:800; font-size:1.45rem;"><i class="fa-solid fa-lock" style="color:var(--primary);"></i> Reset Password</h3>
                <p style="color:#cbd5e1;">OTP Verified! Enter your new password below.</p>
              </div>

              <input type="hidden" id="newpass-hidden-token">

              <div class="auth-input-group">
                <label for="reset-new-pass">New Password (Min. 8 characters)</label>
                <div class="auth-input-wrapper">
                  <i class="fa-solid fa-lock input-icon"></i>
                  <input type="password" id="reset-new-pass" class="auth-input-field" placeholder="At least 8 characters (letters & numbers)" required minlength="8" autocomplete="new-password">
                  <button type="button" class="toggle-password-btn" id="btn-toggle-newpass-1">
                    <i class="fa-solid fa-eye" id="icon-newpass-1"></i>
                  </button>
                </div>
                <div style="font-size:0.75rem; color:#94a3b8; margin-top:4px;">Minimum 8 characters with at least one letter & one number.</div>
              </div>

              <div class="auth-input-group">
                <label for="reset-confirm-pass">Confirm Password</label>
                <div class="auth-input-wrapper">
                  <i class="fa-solid fa-shield-halved input-icon"></i>
                  <input type="password" id="reset-confirm-pass" class="auth-input-field" placeholder="Re-enter new password" required minlength="8" autocomplete="new-password">
                  <button type="button" class="toggle-password-btn" id="btn-toggle-newpass-2">
                    <i class="fa-solid fa-eye" id="icon-newpass-2"></i>
                  </button>
                </div>
              </div>

              <button type="submit" class="btn-auth-submit" id="btn-submit-newpass" style="background: linear-gradient(135deg, #ff5a1f, #22c55e);">
                <i class="fa-solid fa-key"></i> Update Password
              </button>
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
                  <a href="/dashboard#overview" class="btn btn-primary drawer-dash-link" style="width:100%; justify-content:flex-start; text-decoration:none; padding:12px 16px; font-weight:800; gap:12px; box-sizing:border-box;">
                    <i class="fa-solid fa-gauge-high" style="font-size:1.1rem; width:20px; text-align:center;"></i> My Dashboard Overview
                  </a>
                  <a href="/dashboard#orders" class="btn btn-secondary drawer-dash-link" style="width:100%; justify-content:flex-start; text-decoration:none; padding:12px 16px; gap:12px; box-sizing:border-box; color:#fff;">
                    <i class="fa-solid fa-box-open" style="color:var(--primary); font-size:1.1rem; width:20px; text-align:center;"></i> My Orders & Tracking
                  </a>
                  <a href="/dashboard#wishlist" class="btn btn-secondary drawer-dash-link" style="width:100%; justify-content:flex-start; text-decoration:none; padding:12px 16px; gap:12px; box-sizing:border-box; color:#fff;">
                    <i class="fa-solid fa-heart" style="color:#ec4899; font-size:1.1rem; width:20px; text-align:center;"></i> My Wishlist (<span id="drawer-wishlist-count">0</span>)
                  </a>
                  <a href="/dashboard#addresses" class="btn btn-secondary drawer-dash-link" style="width:100%; justify-content:flex-start; text-decoration:none; padding:12px 16px; gap:12px; box-sizing:border-box; color:#fff;">
                    <i class="fa-solid fa-map-location-dot" style="color:#38bdf8; font-size:1.1rem; width:20px; text-align:center;"></i> Saved Addresses
                  </a>
                  <a href="/dashboard#profile" class="btn btn-secondary drawer-dash-link" style="width:100%; justify-content:flex-start; text-decoration:none; padding:12px 16px; gap:12px; box-sizing:border-box; color:#fff;">
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
    const formOtp = document.getElementById('form-otp-view');
    const formNewpass = document.getElementById('form-newpass-view');
    const formProfile = document.getElementById('form-profile-view');

    const allForms = [formLogin, formSignup, formForgot, formOtp, formNewpass, formProfile];
    allForms.forEach(f => {
      if (f) {
        f.classList.remove('active');
        f.style.setProperty('display', 'none', 'important');
      }
    });

    if (viewName === 'profile') {
      if (tabsRow) tabsRow.style.display = 'none';
      if (formProfile) {
        formProfile.classList.add('active');
        formProfile.style.setProperty('display', 'block', 'important');
      }
    } else {
      if (viewName === 'login') {
        if (tabsRow) tabsRow.style.display = 'flex';
        if (tabLogin) tabLogin.classList.add('active');
        if (tabSignup) tabSignup.classList.remove('active');
        if (formLogin) {
          formLogin.classList.add('active');
          formLogin.style.setProperty('display', 'block', 'important');
        }
      } else if (viewName === 'signup') {
        if (tabsRow) tabsRow.style.display = 'flex';
        if (tabSignup) tabSignup.classList.add('active');
        if (tabLogin) tabLogin.classList.remove('active');
        if (formSignup) {
          formSignup.classList.add('active');
          formSignup.style.setProperty('display', 'block', 'important');
        }
      } else if (viewName === 'forgot') {
        if (tabsRow) tabsRow.style.display = 'none';
        if (formForgot) {
          formForgot.classList.add('active');
          formForgot.style.setProperty('display', 'block', 'important');
        }
      } else if (viewName === 'otp') {
        if (tabsRow) tabsRow.style.display = 'none';
        if (formOtp) {
          formOtp.classList.add('active');
          formOtp.style.setProperty('display', 'block', 'important');
        }
      } else if (viewName === 'newpass') {
        if (tabsRow) tabsRow.style.display = 'none';
        if (formNewpass) {
          formNewpass.classList.add('active');
          formNewpass.style.setProperty('display', 'block', 'important');
        }
      }
    }
  }


  let authOtpCountdownTimer = null;
  function startAuthOtpCountdown(seconds = 60) {
    if (authOtpCountdownTimer) clearInterval(authOtpCountdownTimer);
    let remaining = seconds;
    const resendBtn = document.getElementById('otp-resend-link');
    const timerSpan = document.getElementById('otp-resend-timer');
    if (!resendBtn) return;

    resendBtn.style.pointerEvents = 'none';
    resendBtn.style.opacity = '0.5';
    if (timerSpan) timerSpan.textContent = ` (${remaining}s)`;

    authOtpCountdownTimer = setInterval(() => {
      remaining--;
      if (remaining > 0) {
        if (timerSpan) timerSpan.textContent = ` (${remaining}s)`;
      } else {
        clearInterval(authOtpCountdownTimer);
        authOtpCountdownTimer = null;
        resendBtn.style.pointerEvents = 'auto';
        resendBtn.style.opacity = '1';
        if (timerSpan) timerSpan.textContent = '';
      }
    }, 1000);
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

    // OTP Navigation triggers (Back / Resend)
    const otpBack = document.getElementById('otp-back-to-forgot');
    if (otpBack) {
      otpBack.onclick = (e) => {
        e.preventDefault();
        hideAlert();
        showView('forgot');
      };
    }
    const otpResend = document.getElementById('otp-resend-link');
    if (otpResend) {
      otpResend.onclick = async (e) => {
        e.preventDefault();
        const email = document.getElementById('otp-hidden-identifier').value.trim();
        if (!email) {
          showView('forgot');
          return;
        }
        hideAlert();
        try {
          const res = await fetch('/accounts/api/forgot-password/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ email: email, identifier: email })
          });
          const data = await res.json();
          if (data.success) {
            if (data.token) {
              document.getElementById('otp-hidden-token').value = data.token;
            }
            showAlert(`<i class="fa-solid fa-paper-plane"></i> Fresh 6-digit OTP sent to your email (${data.masked_email || email})!`, true);
            startAuthOtpCountdown(60);
          } else {
            showAlert(data.message || 'Failed to resend OTP.');
          }
        } catch (err) {
          showAlert('Network error while resending OTP.');
        }
      };
    }

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

    const toggleOtpPass = document.getElementById('btn-toggle-otp-pass');
    const inputOtpPass = document.getElementById('otp-new-password');
    const iconOtpPass = document.getElementById('icon-otp-pass');
    if (toggleOtpPass && inputOtpPass) {
      toggleOtpPass.onclick = () => {
        if (inputOtpPass.type === 'password') {
          inputOtpPass.type = 'text';
          iconOtpPass.className = 'fa-solid fa-eye-slash';
        } else {
          inputOtpPass.type = 'password';
          iconOtpPass.className = 'fa-solid fa-eye';
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
            credentials: 'include',
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
            if (data.token) {
              currentAuthToken = data.token;
              localStorage.setItem('sneaker_squad_auth_token', data.token);
              try {
                var maxAge = 315360000;
                var exp = new Date(Date.now() + maxAge * 1000).toUTCString();
                var isHttps = window.location.protocol === 'https:';
                var sec = isHttps ? '; Secure' : '';
                document.cookie = 'squad_auth_token=' + encodeURIComponent(data.token) + '; path=/; max-age=' + maxAge + '; expires=' + exp + '; SameSite=Lax' + sec;
              } catch(e) {}
            }
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
            credentials: 'include',
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
            if (data.token) {
              currentAuthToken = data.token;
              localStorage.setItem('sneaker_squad_auth_token', data.token);
              try {
                var maxAge = 315360000;
                var exp = new Date(Date.now() + maxAge * 1000).toUTCString();
                var isHttps = window.location.protocol === 'https:';
                var sec = isHttps ? '; Secure' : '';
                document.cookie = 'squad_auth_token=' + encodeURIComponent(data.token) + '; path=/; max-age=' + maxAge + '; expires=' + exp + '; SameSite=Lax' + sec;
              } catch(e) {}
            }
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

    // Step 1: Request OTP Form
    const formForgot = document.getElementById('form-forgot-view');
    if (formForgot) {
      formForgot.onsubmit = async (e) => {
        e.preventDefault();
        hideAlert();
        const identifier = document.getElementById('forgot-identifier').value.trim();
        const submitBtn = document.getElementById('btn-submit-forgot');

        if (!identifier || !identifier.includes('@')) {
          showAlert('Please enter your registered email address.');
          return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending OTP...';

        try {
          const res = await fetch('/accounts/api/forgot-password/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ email: identifier, identifier: identifier })
          });
          const data = await res.json();
          if (data.success) {
            document.getElementById('otp-hidden-identifier').value = identifier;
            document.getElementById('otp-hidden-token').value = data.token || '';
            showView('otp');

            const otpInstr = document.getElementById('otp-instruction-text');
            if (otpInstr) {
              otpInstr.innerHTML = `OTP sent to your email (<strong>${data.masked_email || identifier}</strong>).`;
            }

            showAlert(`<i class="fa-solid fa-circle-check"></i> OTP sent to your email (${data.masked_email || identifier})! Valid for 10 minutes.`, true);
            startAuthOtpCountdown(60);

            setTimeout(() => {
              const otpInp = document.getElementById('otp-code-input');
              if (otpInp) {
                otpInp.value = '';
                otpInp.focus();
              }
            }, 200);
          } else {
            showAlert(data.message || 'No registered account found with this email.');
          }
        } catch (err) {
          showAlert('Unable to send verification OTP. Please try again.');
        } finally {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Send OTP';
        }
      };
    }

    // Step 2: Verify 6-digit OTP
    const formOtpView = document.getElementById('form-otp-view');
    if (formOtpView) {
      formOtpView.onsubmit = async (e) => {
        e.preventDefault();
        hideAlert();
        const identifier = document.getElementById('otp-hidden-identifier').value.trim();
        const token = document.getElementById('otp-hidden-token').value.trim();
        const otp = document.getElementById('otp-code-input').value.trim();
        const submitBtn = document.getElementById('btn-submit-otp-verify');

        if (otp.length !== 6 || !/^\d{6}$/.test(otp)) {
          showAlert('Please enter the 6-digit numeric OTP code sent to your email.');
          return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Verifying OTP...';

        try {
          const res = await fetch('/accounts/api/verify-otp/', {
            method: 'POST',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ email: identifier, identifier: identifier, token: token, otp: otp })
          });
          const data = await res.json();
          if (data.success) {
            if (authOtpCountdownTimer) {
              clearInterval(authOtpCountdownTimer);
              authOtpCountdownTimer = null;
            }
            document.getElementById('newpass-hidden-token').value = data.token || token;
            const newPassInp = document.getElementById('reset-new-pass');
            const confPassInp = document.getElementById('reset-confirm-pass');
            if (newPassInp) newPassInp.value = '';
            if (confPassInp) confPassInp.value = '';

            showAlert('<i class="fa-solid fa-circle-check"></i> OTP verified successfully! Now create your new password.', true);
            showView('newpass');
            setTimeout(() => {
              if (newPassInp) newPassInp.focus();
            }, 200);
          } else {
            showAlert(data.message || 'Invalid or expired OTP code. Please check your email.');
          }
        } catch (err) {
          showAlert('Network error while verifying OTP.');
        } finally {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Verify OTP';
        }
      };
    }

    // Step 3: Create & Submit New Password
    const formNewpassView = document.getElementById('form-newpass-view');
    if (formNewpassView) {
      formNewpassView.onsubmit = async (e) => {
        e.preventDefault();
        hideAlert();
        const token = document.getElementById('newpass-hidden-token').value;
        const new_password = document.getElementById('reset-new-pass').value.trim();
        const confirm_password = document.getElementById('reset-confirm-pass').value.trim();
        const identifier = document.getElementById('otp-hidden-identifier').value.trim();
        const submitBtn = document.getElementById('btn-submit-newpass');

        // Form validation: minimum 8 characters & basic strength requirements
        if (new_password.length < 8) {
          showAlert('Password must be at least 8 characters long.');
          return;
        }
        if (!/[A-Za-z]/.test(new_password) || !/\d/.test(new_password)) {
          showAlert('Password must contain at least one letter and one number.');
          return;
        }
        if (new_password !== confirm_password) {
          showAlert('Passwords do not match! Please check and re-enter.');
          return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Updating Password...';

        try {
          const res = await fetch('/accounts/api/reset-password/submit/', {
            method: 'POST',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ token, new_password, confirm_password })
          });
          const data = await res.json();
          if (data.success) {
            // Step 4: Display Success message and redirect to login
            showAlert('<i class="fa-solid fa-circle-check"></i> Password updated successfully! Redirecting to login...', true);
            formNewpassView.reset();
            const loginEmailInp = document.getElementById('login-email');
            if (loginEmailInp && identifier) {
              loginEmailInp.value = identifier;
            }
            const loginPassInp = document.getElementById('login-password');
            if (loginPassInp) {
              loginPassInp.value = '';
            }
            setTimeout(() => {
              showView('login');
              hideAlert();
              showAlert('<i class="fa-solid fa-circle-check"></i> Password updated! You can now log in with your new password.', true);
              if (loginPassInp) loginPassInp.focus();
            }, 1800);
          } else {
            showAlert(data.message || 'Error updating password. Please try requesting a new OTP.');
          }
        } catch (err) {
          showAlert('Network error while updating password.');
        } finally {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="fa-solid fa-key"></i> Update Password';
        }
      };
    }

    // Toggle Eye Icons for Step 3
    const btnToggleNp1 = document.getElementById('btn-toggle-newpass-1');
    if (btnToggleNp1) {
      btnToggleNp1.onclick = () => {
        const inp = document.getElementById('reset-new-pass');
        const icon = document.getElementById('icon-newpass-1');
        if (inp.type === 'password') {
          inp.type = 'text';
          icon.className = 'fa-solid fa-eye-slash';
        } else {
          inp.type = 'password';
          icon.className = 'fa-solid fa-eye';
        }
      };
    }

    const btnToggleNp2 = document.getElementById('btn-toggle-newpass-2');
    if (btnToggleNp2) {
      btnToggleNp2.onclick = () => {
        const inp = document.getElementById('reset-confirm-pass');
        const icon = document.getElementById('icon-newpass-2');
        if (inp.type === 'password') {
          inp.type = 'text';
          icon.className = 'fa-solid fa-eye-slash';
        } else {
          inp.type = 'password';
          icon.className = 'fa-solid fa-eye';
        }
      };
    }

    const otpBackBtn = document.getElementById('otp-back-to-forgot');
    if (otpBackBtn) otpBackBtn.onclick = (e) => { e.preventDefault(); showView('forgot'); };


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
        try {
          await fetch('/accounts/api/logout/', {
            method: 'POST',
            credentials: 'include',
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
          });
        } catch (e) {}
        currentUser = null;
        currentWishlist = [];
        currentAuthToken = '';
        localStorage.removeItem('sneaker_squad_user');
        localStorage.removeItem('sneaker_squad_wishlist');
        localStorage.removeItem('sneaker_squad_auth_token');
        try {
          document.cookie = 'squad_auth_token=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
          document.cookie = 'squad_admin_token=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
          document.cookie = 'sessionid=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
        } catch(e) {}
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

    const drawerName = document.getElementById('drawer-user-name');
    const drawerSub = document.getElementById('drawer-user-sub');
    const drawerAuthBtn = document.getElementById('drawer-auth-btn');
    const drawerAvatarIcon = document.getElementById('drawer-avatar-icon');

    if (currentUser) {
      if (authBtn) {
        authBtn.title = `Signed in as ${currentUser.displayName} (Click for Dashboard)`;
        authBtn.setAttribute('aria-label', `Account: ${currentUser.displayName}`);
      }
      if (headerIcon) {
        headerIcon.className = 'fa-solid fa-user-check';
        headerIcon.style.color = 'var(--primary)';
      }
      if (drawerName) drawerName.textContent = currentUser.displayName || 'Squad Member';
      if (drawerSub) drawerSub.textContent = currentUser.email || 'View orders & profile';
      if (drawerAvatarIcon) {
        drawerAvatarIcon.className = 'fa-solid fa-user-check';
        drawerAvatarIcon.style.color = 'var(--primary)';
      }
      if (drawerAuthBtn) {
        drawerAuthBtn.innerHTML = '<i class="fa-solid fa-gauge-high"></i> <span>My Dashboard & Orders</span>';
        drawerAuthBtn.onclick = (e) => {
          e.preventDefault();
          window.location.href = '/dashboard';
        };
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
      if (drawerName) drawerName.textContent = 'Welcome, Sneakerhead!';
      if (drawerSub) drawerSub.textContent = 'Sign in for exclusive drops & orders';
      if (drawerAvatarIcon) {
        drawerAvatarIcon.className = 'fa-regular fa-user';
        drawerAvatarIcon.style.color = 'var(--primary)';
      }
      if (drawerAuthBtn) {
        drawerAuthBtn.innerHTML = '<i class="fa-solid fa-arrow-right-to-bracket"></i> <span>Sign In / Register</span>';
        drawerAuthBtn.onclick = null;
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

  function isUserAuthenticated() {
    if (typeof window.DJANGO_USER !== 'undefined' && typeof window.DJANGO_USER.isAuthenticated === 'boolean') {
      if (window.DJANGO_USER.isAuthenticated) return true;
    }
    if (currentUser && (currentUser.id || currentUser.username || currentUser.email)) return true;
    try {
      const u = JSON.parse(localStorage.getItem('sneaker_squad_user'));
      const t = localStorage.getItem('sneaker_squad_auth_token');
      return !!((u && (u.username || u.email || u.id)) || t);
    } catch(e) {
      return false;
    }
  }

  // Core Wishlist Toggle Engine
  async function handleWishlistToggle(prodId, prodName, prodPrice, prodImg) {
    if (!isUserAuthenticated()) {
      openDrawer('login');
      showAlert('Please log in to save kicks to your wishlist!');
      if (typeof showToast === 'function') {
        showToast('Please log in first to save kicks to your wishlist! 🔒', 'fa-lock');
      }
      return;
    }

    if (!prodId) return;

    try {
      const res = await fetch('/accounts/api/wishlist/toggle/', {
        method: 'POST',
        credentials: 'include',
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

  // Fetch initial user state on page load and sync with Django backend
  document.addEventListener('DOMContentLoaded', async () => {
    setupAuthDrawer();
    updateHeaderUserState();
    syncWishlistHeartsUI();

    const storedToken = localStorage.getItem('sneaker_squad_auth_token') || '';
    const storedUser = localStorage.getItem('sneaker_squad_user');

    try {
      const headers = {};
      if (storedToken) {
        headers['X-Squad-Auth-Token'] = storedToken;
      }
      const url = '/accounts/api/user-state/?_t=' + Date.now() + (storedToken ? '&auth_token=' + encodeURIComponent(storedToken) : '');
      const res = await fetch(url, {
        method: 'GET',
        credentials: 'include',
        cache: 'no-store',
        headers: headers
      });
      const data = await res.json();
      if (data.isAuthenticated && data.user) {
        currentUser = data.user;
        currentWishlist = data.wishlist || [];
        if (data.token) {
          currentAuthToken = data.token;
          localStorage.setItem('sneaker_squad_auth_token', data.token);
        }
        localStorage.setItem('sneaker_squad_user', JSON.stringify(currentUser));
        localStorage.setItem('sneaker_squad_wishlist', JSON.stringify(currentWishlist));
        updateHeaderUserState();
        syncWishlistHeartsUI();
      } else {
        // Only clear state if neither session NOR persistent auth token exists (user explicitly signed out)
        if (!storedToken) {
          currentUser = null;
          currentWishlist = [];
          localStorage.removeItem('sneaker_squad_user');
          localStorage.removeItem('sneaker_squad_wishlist');
          localStorage.removeItem('sneaker_squad_auth_token');
          updateHeaderUserState();
          syncWishlistHeartsUI();
        }
      }
    } catch (err) {
      console.warn('User state server hydration offline, preserving persistent squad user profile.');
    }
  });

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

  window.isUserAuthenticated = isUserAuthenticated;
  window.openAuthDrawer = openDrawer;
  window.closeAuthDrawer = closeDrawer;
  window.handleWishlistToggle = handleWishlistToggle;
  window.syncWishlistHeartsUI = syncWishlistHeartsUI;
})();
