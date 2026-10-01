/**
 * SNEAKERS SQUAD - PWA INSTALL & SERVICE WORKER REGISTRATION (pwa-install.js)
 * Manages service worker lifecycle, handles mobile install prompts,
 * and provides custom iOS / Android install guidance.
 */

(function () {
  let deferredPrompt = null;
  const isIos = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;

  // 1. Register Service Worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js', { scope: '/' })
        .then((reg) => {
          console.log('[SneakerSquad PWA] Service Worker registered successfully! Scope:', reg.scope);
        })
        .catch((err) => {
          console.warn('[SneakerSquad PWA] Service Worker registration failed:', err);
        });
    });
  }

  // If already installed and launched as standalone app, don't show install banner
  if (isStandalone) {
    console.log('[SneakerSquad PWA] Running as installed standalone app 🚀');
    return;
  }

  document.addEventListener('DOMContentLoaded', () => {
    initPwaInstallUI();
  });

  function initPwaInstallUI() {
    // 2. Build and Inject PWA Install Banner in DOM
    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.className = 'pwa-install-banner';
    banner.innerHTML = `
      <div class="pwa-banner-left">
        <div class="pwa-banner-icon">
          <img src="/static/img/pwa-icon-192.png" alt="Sneakers Squad App Icon" onerror="this.onerror=null;this.src='/static/img/shoe-1.jpg'">
        </div>
        <div class="pwa-banner-info">
          <div class="pwa-banner-title">
            <span>Sneakers Squad</span>
            <span class="pwa-banner-badge">APP</span>
          </div>
          <p class="pwa-banner-desc">Install App for 2x Faster Checkout & VIP Drops 🔥</p>
        </div>
      </div>
      <div class="pwa-banner-actions">
        <button type="button" class="btn-pwa-install" id="btn-pwa-install-action">
          <i class="fa-solid fa-download"></i> Install
        </button>
        <button type="button" class="btn-pwa-dismiss" id="btn-pwa-dismiss-action" title="Dismiss">&times;</button>
      </div>
    `;
    document.body.appendChild(banner);

    // 2B. Build and Inject Floating Pill Button
    const floatBtn = document.createElement('button');
    floatBtn.type = 'button';
    floatBtn.id = 'pwa-floating-btn';
    floatBtn.className = 'pwa-floating-btn';
    floatBtn.innerHTML = '<i class="fa-solid fa-mobile-screen-button"></i> <span>Install App</span>';
    floatBtn.title = 'Install Sneakers Squad Mobile App';
    floatBtn.onclick = () => triggerPwaInstall(banner);
    document.body.appendChild(floatBtn);

    // 3. Auto-show Banner after 1 second
    setTimeout(() => {
      if (!isStandalone) {
        banner.classList.add('show');
      }
    }, 800);

    // 4. Capture native beforeinstallprompt
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      console.log('[SneakerSquad PWA] beforeinstallprompt captured');
      banner.classList.add('show');
    });

    // 4. Handle Install Button Click
    const installBtn = document.getElementById('btn-pwa-install-action');
    if (installBtn) {
      installBtn.addEventListener('click', () => {
        triggerPwaInstall(banner);
      });
    }

    // 5. Handle Dismiss Button Click
    const dismissBtn = document.getElementById('btn-pwa-dismiss-action');
    if (dismissBtn) {
      dismissBtn.addEventListener('click', () => {
        banner.classList.remove('show');
        localStorage.setItem('pwa_install_dismissed', Date.now().toString());
      });
    }

    // iOS Safari fallback trigger
    if (isIos && !isStandalone) {
      const lastDismissed = localStorage.getItem('pwa_install_dismissed');
      const twelveHours = 12 * 60 * 60 * 1000;
      if (!lastDismissed || (Date.now() - parseInt(lastDismissed, 10)) > twelveHours) {
        setTimeout(() => {
          banner.classList.add('show');
        }, 3000);
      }
    }

    // Listen to app installed event
    window.addEventListener('appinstalled', () => {
      console.log('[SneakerSquad PWA] App successfully installed on device!');
      banner.classList.remove('show');
      deferredPrompt = null;
      if (typeof showToastNotification === 'function') {
        showToastNotification('🎉 SNEAKERS SQUAD App installed on your home screen!');
      }
    });
  }

  /**
   * Trigger install flow or display iOS Instructions
   */
  window.installSneakerSquadPWA = function () {
    const banner = document.getElementById('pwa-install-banner');
    triggerPwaInstall(banner);
  };

  function triggerPwaInstall(banner) {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('[SneakerSquad PWA] User accepted installation prompt');
        } else {
          console.log('[SneakerSquad PWA] User dismissed installation');
        }
        deferredPrompt = null;
        if (banner) banner.classList.remove('show');
      });
    } else if (isIos) {
      showIosInstallModal();
    } else {
      showDesktopInstallModal();
    }
  }

  /**
   * Show Desktop / Android Browser interactive guide
   */
  function showDesktopInstallModal() {
    let existingModal = document.getElementById('pwa-desktop-modal');
    if (existingModal) existingModal.remove();

    const deskModal = document.createElement('div');
    deskModal.id = 'pwa-desktop-modal';
    deskModal.className = 'pwa-ios-modal';
    deskModal.innerHTML = `
      <div class="pwa-ios-card">
        <button type="button" class="pwa-ios-close" id="btn-pwa-desk-close">&times;</button>
        <div style="font-size:2.4rem; color:#ff5a1f; margin-bottom:8px;"><i class="fa-solid fa-mobile-screen-button"></i></div>
        <h3 style="font-size:1.3rem; font-weight:800; margin:0 0 6px 0;">Install Sneakers Squad App</h3>
        <p style="color:#94a3b8; font-size:0.86rem; margin:0 0 16px 0;">Get 2x faster access directly from your Desktop / Phone:</p>
        
        <div class="pwa-ios-steps">
          <div class="pwa-ios-step-item">
            <span class="pwa-ios-step-num">1</span>
            <span>Check your browser address bar (top-right) for the <strong>Install Icon <i class="fa-solid fa-circle-down" style="color:#ff5a1f;"></i></strong></span>
          </div>
          <div class="pwa-ios-step-item">
            <span class="pwa-ios-step-num">2</span>
            <span>Or click browser menu (<strong>⋮</strong> / <strong>⋯</strong>) & choose <strong>'Install Sneakers Squad'</strong> or <strong>'Add to Home screen'</strong>.</span>
          </div>
        </div>

        <button type="button" id="btn-pwa-desk-gotit" style="background:linear-gradient(135deg, #ff5a1f, #ff7844); color:#fff; border:none; padding:12px 24px; border-radius:10px; font-weight:bold; width:100%; cursor:pointer; font-size:0.95rem;">
          Got it, Install Now! 🚀
        </button>
      </div>
    `;
    document.body.appendChild(deskModal);

    const closeBtn = document.getElementById('btn-pwa-desk-close');
    const gotItBtn = document.getElementById('btn-pwa-desk-gotit');
    const closeModal = () => deskModal.remove();

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (gotItBtn) gotItBtn.addEventListener('click', closeModal);
    deskModal.addEventListener('click', (e) => {
      if (e.target === deskModal) closeModal();
    });
  }

  /**
   * Show iOS Safari specific step-by-step instructions
   */
  function showIosInstallModal() {
    let existingModal = document.getElementById('pwa-ios-modal');
    if (existingModal) existingModal.remove();

    const iosModal = document.createElement('div');
    iosModal.id = 'pwa-ios-modal';
    iosModal.className = 'pwa-ios-modal';
    iosModal.innerHTML = `
      <div class="pwa-ios-card">
        <button type="button" class="pwa-ios-close" id="btn-pwa-ios-close">&times;</button>
        <div style="font-size:2.4rem; color:#ff5a1f; margin-bottom:8px;">👟</div>
        <h3 style="font-size:1.25rem; font-weight:800; margin:0 0 6px 0;">Install Sneakers Squad on iPhone / iPad</h3>
        <p style="color:#94a3b8; font-size:0.85rem; margin:0;">Follow these 2 simple steps to add the app icon to your home screen:</p>
        
        <div class="pwa-ios-steps">
          <div class="pwa-ios-step-item">
            <span class="pwa-ios-step-num">1</span>
            <span>Tap the <strong>Share button <i class="fa-solid fa-arrow-up-from-bracket" style="color:#38bdf8;"></i></strong> at the bottom of Safari.</span>
          </div>
          <div class="pwa-ios-step-item">
            <span class="pwa-ios-step-num">2</span>
            <span>Scroll down and tap <strong>'Add to Home Screen' <i class="fa-solid fa-square-plus" style="color:#22c55e;"></i></strong>.</span>
          </div>
        </div>

        <button type="button" id="btn-pwa-ios-gotit" style="background:#ff5a1f; color:#fff; border:none; padding:12px 24px; border-radius:10px; font-weight:bold; width:100%; cursor:pointer;">
          Got it, let's go! 🚀
        </button>
      </div>
    `;
    document.body.appendChild(iosModal);

    const closeBtn = document.getElementById('btn-pwa-ios-close');
    const gotItBtn = document.getElementById('btn-pwa-ios-gotit');
    const closeModal = () => iosModal.remove();

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (gotItBtn) gotItBtn.addEventListener('click', closeModal);
    iosModal.addEventListener('click', (e) => {
      if (e.target === iosModal) closeModal();
    });
  }
})();
