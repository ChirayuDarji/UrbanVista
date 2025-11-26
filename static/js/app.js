/* UrbanVista • App JS (company-ready, aligned with your base.html) */
(function () {
  'use strict';

  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  // ============== Toasts ==============
  // Create or get the UL container matching your base.html markup
  function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container') || document.querySelector('ul.toasts');
    if (!container) {
      container = document.createElement('ul');
      container.className = 'toasts';
      container.id = 'toast-container';
      container.setAttribute('role', 'status');
      container.setAttribute('aria-live', 'polite');
      container.setAttribute('aria-atomic', 'true');
      const main = document.getElementById('main') || document.querySelector('main');
      if (main) {
        main.insertAdjacentElement('afterbegin', container);
      } else {
        document.body.appendChild(container);
      }
    }
    return container;
  }

  // Helper to remove a toast with a small fade-out
  function dismissToast(el) {
    if (!el) return;
    el.classList.add('toast-fade-out'); // CSS optional; removal still occurs
    setTimeout(() => {
      el.remove();
      const container = document.getElementById('toast-container') || document.querySelector('ul.toasts');
      if (container && !container.children.length) container.remove();
    }, 250);
  }

  // Define showToast if missing (uses LI structure matching your base)
  if (typeof window.showToast !== 'function') {
    window.showToast = function (message, type) {
      type = type || 'info';
      const container = getOrCreateToastContainer();

      const li = document.createElement('li');
      li.className = 'toast toast-' + type;

      const isAssertive = type === 'error' || type === 'danger' || type === 'warning';
      li.setAttribute('role', isAssertive ? 'alert' : 'status');
      li.setAttribute('aria-live', isAssertive ? 'assertive' : 'polite');

      const body = document.createElement('div');
      body.className = 'toast-body';
      body.textContent = String(message);

      const btn = document.createElement('button');
      btn.className = 'toast-close';
      btn.setAttribute('aria-label', 'Dismiss');
      btn.textContent = '×';

      li.appendChild(body);
      li.appendChild(btn);
      container.appendChild(li);

      const timer = prefersReduced ? null : setTimeout(() => dismissToast(li), 5000);
      btn.addEventListener('click', () => {
        if (timer) clearTimeout(timer);
        dismissToast(li);
      });

      return li;
    };
  }

  function initToasts() {
    // Wire existing toasts already rendered by Django messages
    const toasts = document.querySelectorAll('.toasts .toast, [data-toast]');
    toasts.forEach((toast) => {
      const closeBtn = toast.querySelector('.toast-close, [data-dismiss="toast"]');
      const timer = prefersReduced ? null : setTimeout(() => dismissToast(toast), 5000);
      if (closeBtn) {
        closeBtn.addEventListener('click', () => {
          if (timer) clearTimeout(timer);
          dismissToast(toast);
        });
      }
    });
  }

  // ============== Back to Top ==============
  function initBackToTop() {
    const btn = document.getElementById('back-to-top');
    if (!btn) return;

    // Sentinel placed at top of body to detect when top is visible
    let sentinel = document.getElementById('top-sentinel');
    if (!sentinel) {
      sentinel = document.createElement('div');
      sentinel.id = 'top-sentinel';
      sentinel.setAttribute('aria-hidden', 'true');
      document.body.insertBefore(sentinel, document.body.firstChild);
    }

    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        const topVisible = entries[0].isIntersecting;
        btn.classList.toggle('show', !topVisible);
      }, { threshold: 0, rootMargin: '-64px 0px 0px 0px' });
      io.observe(sentinel);
    } else {
      const onScroll = () => {
        if (window.pageYOffset > 300) btn.classList.add('show'); else btn.classList.remove('show');
      };
      onScroll();
      window.addEventListener('scroll', onScroll, { passive: true });
    }

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ============== Page Loader (optional element) ==============
  function initPageLoader() {
    const loader = document.getElementById('page-loader');
    if (!loader) return;
    setTimeout(() => {
      loader.classList.add('hidden');
      setTimeout(() => (loader.style.display = 'none'), 300);
    }, 500);
  }

  // ============== CSRF Setup ==============
  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  }

  function initCSRF() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    const token = input ? input.value : getCookie('csrftoken');
    if (!token) return;

    if (typeof axios !== 'undefined') {
      axios.defaults.headers.common['X-CSRFToken'] = token;
    }
    window.csrfToken = token;
    window.fetchWithCSRF = function (url, options) {
      options = options || {};
      options.headers = Object.assign({}, options.headers, { 'X-CSRFToken': token });
      return fetch(url, options);
    };
  }

  // ============== Network Status ==============
  function initNetworkStatus() {
    let wasOffline = !navigator.onLine;
    if (wasOffline) window.showToast('You are offline. Some features may not work.', 'warning');

    window.addEventListener('offline', () => {
      wasOffline = true;
      window.showToast('You are offline. Some features may not work.', 'warning');
    });
    window.addEventListener('online', () => {
      if (wasOffline) {
        window.showToast('Back online! Connection restored.', 'success');
        wasOffline = false;
      }
    });
  }

  // ============== Header Scroll Effect ==============
  function initHeaderScrollEffect() {
    const handler = () => {
      if (window.scrollY > 4) document.body.classList.add('header-scrolled');
      else document.body.classList.remove('header-scrolled');
    };
    handler();
    window.addEventListener('scroll', handler, { passive: true });
  }

  // ============== Theme Toggle Wiring (matches #themeToggle in base) ==============
  function initThemeToggle() {
    const btn = document.getElementById('themeToggle');
    if (!btn || typeof window.toggleTheme !== 'function') return;

    const sync = () => {
      const t = document.documentElement.getAttribute('data-theme');
      // aria-pressed true when light is active (matches your previous pattern)
      btn.setAttribute('aria-pressed', String(t === 'light'));
    };

    btn.addEventListener('click', () => {
      window.toggleTheme();
      sync();
    });

    sync();
  }

  // ============== Mobile Nav (matches #navToggle and #mobileMenu) ==============
  function initMobileNav() {
    const navToggle = document.getElementById('navToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    if (!navToggle || !mobileMenu) return;

    let closingTimeout = null;

    function openMenu() {
      clearTimeout(closingTimeout);
      navToggle.setAttribute('aria-expanded', 'true');
      mobileMenu.hidden = false;
      mobileMenu.classList.remove('animate-out');
      mobileMenu.classList.add('animate-in');
      document.body.dataset.menuOpen = 'true';
      const first = mobileMenu.querySelector('a,button,[tabindex]:not([tabindex="-1"])');
      if (first) first.focus({ preventScroll: true });
    }

    function closeMenu() {
      navToggle.setAttribute('aria-expanded', 'false');
      mobileMenu.classList.remove('animate-in');
      mobileMenu.classList.add('animate-out');
      closingTimeout = setTimeout(() => {
        mobileMenu.hidden = true;
        mobileMenu.classList.remove('animate-out');
      }, prefersReduced ? 0 : 180);
      delete document.body.dataset.menuOpen;
      navToggle.focus({ preventScroll: true });
    }

    function toggleMenu() {
      const expanded = navToggle.getAttribute('aria-expanded') === 'true';
      expanded ? closeMenu() : openMenu();
    }

    navToggle.addEventListener('click', toggleMenu);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && navToggle.getAttribute('aria-expanded') === 'true') {
        e.preventDefault();
        closeMenu();
      }
    });

    document.addEventListener('click', (e) => {
      if (mobileMenu.hidden) return;
      const clickedInside = mobileMenu.contains(e.target) || navToggle.contains(e.target);
      if (!clickedInside) closeMenu();
    });

    mobileMenu.addEventListener('click', (e) => {
      const el = e.target;
      if (el.matches('a[href], button[data-close]')) closeMenu();
    });

    // Close on resize to desktop
    window.addEventListener('resize', () => {
      if (window.innerWidth > 880 && navToggle.getAttribute('aria-expanded') === 'true') {
        closeMenu();
      }
    }, { passive: true });
  }

  // ============== Button Loading States ==============
  function initButtonLoading() {
    // Helper to set button loading state
    window.setButtonLoading = function(button, isLoading) {
      if (!button) return;
      if (isLoading) {
        button.classList.add('loading');
        button.setAttribute('aria-busy', 'true');
        button.disabled = true;
      } else {
        button.classList.remove('loading');
        button.removeAttribute('aria-busy');
        button.disabled = false;
      }
    };

    // Auto-handle form submissions
    document.addEventListener('submit', function(e) {
      const form = e.target;
      if (!form || form.dataset.noLoading === 'true') return;
      const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn) {
        window.setButtonLoading(submitBtn, true);
        // Re-enable on error (form won't submit)
        setTimeout(() => {
          if (form.checkValidity && !form.checkValidity()) {
            window.setButtonLoading(submitBtn, false);
          }
        }, 100);
      }
    });
  }

  // ============== Image Lazy Loading ==============
  function initLazyImages() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    if (!images.length) return;

    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
            }
            img.classList.add('loaded');
            imageObserver.unobserve(img);
          }
        });
      }, { rootMargin: '50px' });

      images.forEach(img => {
        if (img.complete && img.naturalHeight !== 0) {
          img.classList.add('loaded');
        } else {
          imageObserver.observe(img);
        }
      });
    } else {
      // Fallback for older browsers
      images.forEach(img => {
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
        }
        img.classList.add('loaded');
      });
    }
  }

  // ============== Mouse Detection (for focus management) ==============
  function initMouseDetection() {
    document.addEventListener('mousedown', function() {
      document.body.classList.add('js-using-mouse');
    });
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Tab') {
        document.body.classList.remove('js-using-mouse');
      }
    });
  }

  // ============== Init ==============
  ready(function () {
    initMouseDetection();
    initToasts();
    initBackToTop();
    initPageLoader();
    initCSRF();
    initNetworkStatus();
    initHeaderScrollEffect();
    initThemeToggle();
    initMobileNav();
    initButtonLoading();
    initLazyImages();
  });

  // ============== Global error hooks (optional) ==============
  window.addEventListener('error', function (e) {
    // console.error('Global error:', e.error || e.message);
  });
  window.addEventListener('unhandledrejection', function (e) {
    // console.error('Unhandled promise rejection:', e.reason);
  });
})();