/* UrbanVista Nav (company-ready) */
(function () {
  'use strict';

  if (window.__uvNavInit) return; // prevent double-binding if base.js also wires nav
  window.__uvNavInit = true;

  const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    const navToggle = document.getElementById('navToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const themeBtn = document.querySelector('#themeToggle, [data-theme-toggle]');

    // Theme toggle wiring
    if (themeBtn && typeof window.toggleTheme === 'function') {
      const sync = () => {
        const t = document.documentElement.getAttribute('data-theme');
        themeBtn.setAttribute('aria-pressed', String(t === 'light'));
      };
      themeBtn.addEventListener('click', () => { window.toggleTheme(); sync(); });
      sync();
    }

    if (!navToggle || !mobileMenu) return;

    let closingTimeout = null;
    let lastFocused = null;
    let trapped = false;
    const MQ_BREAK = 880;

    function focusables(scope) {
      return Array.from(scope.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )).filter(el => el.offsetParent !== null || el === document.activeElement);
    }

    // Scroll lock helpers
    function lockScroll() {
      if (document.body.dataset.scrollLocked === 'true') return;
      const y = window.scrollY || window.pageYOffset;
      document.body.dataset.scrollLocked = 'true';
      document.body.dataset.scrollY = String(y);
      document.body.style.position = 'fixed';
      document.body.style.top = `-${y}px`;
      document.body.style.left = '0';
      document.body.style.right = '0';
      document.body.style.width = '100%';
    }
    function unlockScroll() {
      if (document.body.dataset.scrollLocked !== 'true') return;
      const y = parseInt(document.body.dataset.scrollY || '0', 10) || 0;
      document.body.style.position = '';
      document.body.style.top = '';
      document.body.style.left = '';
      document.body.style.right = '';
      document.body.style.width = '';
      delete document.body.dataset.scrollLocked;
      delete document.body.dataset.scrollY;
      window.scrollTo(0, y);
    }

    function trapFocus(e) {
      if (mobileMenu.hidden) return;
      if (e.key !== 'Tab') return;
      const nodes = focusables(mobileMenu);
      if (!nodes.length) return;

      const first = nodes[0];
      const last = nodes[nodes.length - 1];
      const active = document.activeElement;

      if (e.shiftKey) {
        if (active === first || !mobileMenu.contains(active)) {
          e.preventDefault();
          last.focus({ preventScroll: true });
        }
      } else {
        if (active === last) {
          e.preventDefault();
          first.focus({ preventScroll: true });
        }
      }
    }

    function openMenu() {
      clearTimeout(closingTimeout);
      lastFocused = document.activeElement;

      navToggle.setAttribute('aria-expanded', 'true');
      mobileMenu.hidden = false;
      mobileMenu.classList.remove('animate-out');
      mobileMenu.classList.add('animate-in');
      document.body.dataset.menuOpen = 'true';
      lockScroll();

      const first = focusables(mobileMenu)[0] || mobileMenu.querySelector('a,button');
      if (first) first.focus({ preventScroll: true });

      if (!trapped) {
        document.addEventListener('keydown', onKeydown, true);
        document.addEventListener('click', onDocClick, true);
        trapped = true;
      }
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
      unlockScroll();

      if (trapped) {
        document.removeEventListener('keydown', onKeydown, true);
        document.removeEventListener('click', onDocClick, true);
        trapped = false;
      }

      const toFocus = lastFocused && lastFocused instanceof HTMLElement ? lastFocused : navToggle;
      if (toFocus) toFocus.focus({ preventScroll: true });
    }

    function toggleMenu() {
      const expanded = navToggle.getAttribute('aria-expanded') === 'true';
      expanded ? closeMenu() : openMenu();
    }

    function onKeydown(e) {
      if (e.key === 'Escape') {
        e.preventDefault();
        closeMenu();
        return;
      }
      // Focus trap when open
      if (navToggle.getAttribute('aria-expanded') === 'true') {
        trapFocus(e);
      }
    }

    function onDocClick(e) {
      if (mobileMenu.hidden) return;
      const t = e.target;
      const inside = mobileMenu.contains(t) || navToggle.contains(t);
      if (!inside) closeMenu();
    }

    navToggle.addEventListener('click', toggleMenu);

    mobileMenu.addEventListener('click', (e) => {
      const el = e.target;
      if (el && (el.matches('a[href]') || el.matches('[data-close]'))) {
        closeMenu();
      }
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > MQ_BREAK && navToggle.getAttribute('aria-expanded') === 'true') {
        closeMenu();
      }
    }, { passive: true });

    // Safety: close menu when page is hidden (navigate away, PWA routes, etc.)
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden' && navToggle.getAttribute('aria-expanded') === 'true') {
        closeMenu();
      }
    });
  });
})();