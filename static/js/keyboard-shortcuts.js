/* UrbanVista • Keyboard Shortcuts */
(function() {
  'use strict';

  const shortcuts = {
    // Navigation
    'g h': () => window.location.href = '/',
    'g c': () => window.location.href = '/free-contribution/',
    'g r': () => window.location.href = '/reports/',
    'g n': () => window.location.href = '/news/',
    'g a': () => window.location.href = '/about/',

    // Actions
    'c': () => {
      const createBtn = document.querySelector('[href*="/create/"], [data-create-btn]');
      if (createBtn) createBtn.click();
    },
    '?': () => {
      // Show keyboard shortcuts help
      if (typeof window.showToast === 'function') {
        window.showToast('Keyboard shortcuts: g+h (home), g+c (contribute), g+r (reports), g+n (news), c (create), / (search), ? (help)', 'info');
      }
    },
    '/': (e) => {
      // Focus search if available
      const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i], #search');
      if (searchInput) {
        e.preventDefault();
        searchInput.focus();
      }
    },
  };

  let pressedKeys = new Set();
  let sequence = '';

  function handleKeyDown(e) {
    // Ignore if typing in input/textarea
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
      if (e.key !== 'Escape' && e.key !== '/') return;
    }

    // Ignore modifier-only keys
    if (['Control', 'Shift', 'Alt', 'Meta'].includes(e.key)) return;

    pressedKeys.add(e.key.toLowerCase());
    sequence = Array.from(pressedKeys).sort().join(' ');

    // Check for sequence shortcuts (e.g., 'g h')
    for (const [key, handler] of Object.entries(shortcuts)) {
      if (sequence === key) {
        e.preventDefault();
        handler(e);
        pressedKeys.clear();
        sequence = '';
        return;
      }
    }

    // Single key shortcuts
    if (pressedKeys.size === 1) {
      const key = Array.from(pressedKeys)[0];
      if (shortcuts[key]) {
        e.preventDefault();
        shortcuts[key](e);
        pressedKeys.clear();
        sequence = '';
      }
    }

    // Reset after 1 second of no activity
    clearTimeout(window.shortcutTimeout);
    window.shortcutTimeout = setTimeout(() => {
      pressedKeys.clear();
      sequence = '';
    }, 1000);
  }

  function handleKeyUp(e) {
    pressedKeys.delete(e.key.toLowerCase());
    if (pressedKeys.size === 0) {
      sequence = '';
    }
  }

  // Initialize
  document.addEventListener('keydown', handleKeyDown);
  document.addEventListener('keyup', handleKeyUp);

  // Show help on first visit
  if (!localStorage.getItem('keyboard-shortcuts-shown')) {
    setTimeout(() => {
      if (typeof window.showToast === 'function') {
        window.showToast('Press ? to see keyboard shortcuts', 'info');
      }
      localStorage.setItem('keyboard-shortcuts-shown', 'true');
    }, 3000);
  }
})();

