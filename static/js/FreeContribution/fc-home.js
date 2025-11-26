/* ==========================================================
   UrbanVista • FreeContribution Home (company-ready JS)
   - Hero video toggle (a11y)
   - Gallery lightbox (<dialog>)
   - Leaflet map + live markers + type filters
   - Upvote toggle (CSRF-safe + login redirect)
   - Filters dropdown (Create)
   - Optional stat counters (data-count-to)
   ========================================================== */

(function(){
  'use strict';

  // ---------- Helpers ----------
  const ready = (fn) => {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  };

  function getCookie(name){
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

  function delegate(root, evt, selector, handler){
    root.addEventListener(evt, (e) => {
      const el = e.target.closest(selector);
      if (el && root.contains(el)) handler(e, el);
    });
  }

  function onEsc(handler){
    function keyHandler(e){ if (e.key === 'Escape') handler(e); }
    document.addEventListener('keydown', keyHandler);
    return () => document.removeEventListener('keydown', keyHandler);
  }

  function clickOutside(node, onOutside){
    function handler(e){ if (!node.contains(e.target)) onOutside(); }
    document.addEventListener('click', handler);
    return () => document.removeEventListener('click', handler);
  }

  function escapeHTML(s){
    return String(s || '').replace(/[<>&"]/g, ch => ({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[ch]));
  }

  // ---------- Hero video toggle ----------
  function initHero(){
    const video = document.getElementById('heroVideo');
    const toggle = document.getElementById('heroToggle');
    if (!video || !toggle) return;

    const icon = toggle.querySelector('i');
    const setBtn = () => {
      const playing = !video.paused;
      if (icon) {
        icon.className = playing ? 'fas fa-pause' : 'fas fa-play';
      }
      toggle.setAttribute('aria-pressed', playing ? 'true' : 'false');
      toggle.setAttribute('aria-label', playing ? 'Pause video' : 'Play video');
    };
    const tryPlay = () => video.play().catch(()=>{});

    setBtn();
    toggle.addEventListener('click', () => {
      if (video.paused) { tryPlay(); } else { video.pause(); }
      setBtn();
    });
    ['play','pause'].forEach(ev => video.addEventListener(ev, setBtn));
  }
  
  // ---------- Scroll reveal animation ----------
  window.initScrollReveal = function initScrollReveal(){
    if (!('IntersectionObserver' in window)) {
      document.querySelectorAll('.reveal').forEach(el => el.classList.add('is-visible'));
      return;
    }
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }

  // ---------- Gallery lightbox (<dialog>) ----------
  function initLightbox(){
    const dlg = document.getElementById('lightbox');
    const img = document.getElementById('lightboxImg');
    if (!dlg || !img || typeof dlg.showModal !== 'function') return;

    delegate(document, 'click', '[data-lightbox]', (e, a) => {
      e.preventDefault();
      img.src = a.getAttribute('href');
      img.alt = a.getAttribute('data-title') || '';
      dlg.showModal();
    });

    dlg.addEventListener('click', (e) => {
      if (e.target.hasAttribute('data-close') || e.target === dlg) dlg.close();
    });
    document.addEventListener('keydown', (e)=>{ if(e.key === 'Escape') dlg.close(); });
  }

  // ---------- Leaflet map + marker filters ----------
  function initMap(){
    const mapEl = document.getElementById('fcMap');
    const mapLoading = document.getElementById('map-loading');
    const mapUpdateIndicator = document.getElementById('map-update-indicator');
    const mapLastUpdated = document.getElementById('map-last-updated');
    
    if (!mapEl) {
      console.warn('Map element not found');
      return;
    }

    // Wait for Leaflet to be available
    if (typeof L === 'undefined') {
      console.warn('Leaflet not loaded. Waiting for library...');
      // Retry after a short delay
      setTimeout(() => {
        if (typeof L !== 'undefined') {
          initMap();
        } else {
          console.error('Leaflet library failed to load');
          if (mapLoading) {
            mapLoading.innerHTML = '<span>Map library not available. Please refresh the page.</span>';
          }
        }
      }, 500);
      return;
    }

    const apiBase = mapEl.dataset.api || '/free-contribution/api/map/';

    // Initialize map - element must be visible for Leaflet to work
    const map = L.map('fcMap', { 
      scrollWheelZoom: true,
      zoomControl: true
    });
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Hide loading overlay when map is ready
    map.whenReady(() => {
      // Small delay to ensure tiles are loading
      setTimeout(() => {
        if (mapLoading) {
          mapLoading.style.display = 'none';
        }
        mapEl.classList.add('loaded');
        // Trigger map resize to ensure proper rendering
        map.invalidateSize();
        if (mapUpdateIndicator) {
          mapUpdateIndicator.style.display = 'flex';
          updateMapTimestamp();
        }
      }, 300);
    });

    // Default center; attempt geolocation
    map.setView([20, 0], 2);
    if (navigator.geolocation){
      navigator.geolocation.getCurrentPosition(
        (pos) => map.setView([pos.coords.latitude, pos.coords.longitude], 12),
        () => {}, { enableHighAccuracy: true, timeout: 6000 }
      );
    }
    
    function updateMapTimestamp() {
      if (mapLastUpdated) {
        const now = new Date();
        mapLastUpdated.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }
    }

    const typeColors = { 
      place: '#4dabf7', 
      activity: '#ffd166', 
      story: '#40c057', 
      tip: '#ff6b6b' 
    };
    const markers = [];

    function clearMarkers(){
      markers.forEach(m => map.removeLayer(m));
      markers.length = 0;
    }

    function addMarkers(data){
      if (!data || !data.markers) return;
      const bounds = [];
      data.markers.forEach(m => {
        const color = typeColors[m.type] || '#999';
        const icon = L.divIcon({
          className: 'uv-pin',
          html: `<span style="display:inline-block;width:12px;height:12px;border-radius:999px;background:${color};box-shadow:0 0 0 2px rgba(0,0,0,.3);"></span>`,
          iconSize: [12, 12],
          iconAnchor: [6, 6]
        });
        const marker = L.marker([m.lat, m.lng], { icon }).addTo(map);
        const title = escapeHTML(m.title || 'Contribution');
        const desc = m.desc ? `<div style="color:#9aa0aa;font-size:13px;margin-bottom:6px;">${escapeHTML(m.desc)}</div>` : '';
        const html = `
          <div style="min-width: 220px;">
            <strong style="display:block;margin-bottom:4px;">${title}</strong>
            ${desc}
            <a href="${m.url}" class="btn" style="padding:6px 10px;display:inline-block;border:1px solid var(--border, #242a36);border-radius:8px;text-decoration:none;">Open</a>
          </div>`;
        marker.bindPopup(html, { closeButton: true });
        markers.push(marker);
        bounds.push([m.lat, m.lng]);
      });
      if (bounds.length) {
        try { map.fitBounds(bounds, { padding: [30, 30] }); } catch(e){}
      }
    }

    async function loadMarkers(type){
      const url = type ? `${apiBase}?type=${encodeURIComponent(type)}` : apiBase;
      try {
        const res = await fetch(url, { headers: { 'Accept': 'application/json' }});
        const data = await res.json();
        clearMarkers(); 
        addMarkers(data);
        if (mapUpdateIndicator) {
          updateMapTimestamp();
        }
      } catch(e){ 
        console.warn('Map data load failed', e);
        if (window.showToast) {
          window.showToast('Failed to load map data. Please try again.', 'error');
        }
      }
    }
    
    function updateMapTimestamp() {
      if (mapLastUpdated) {
        const now = new Date();
        mapLastUpdated.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }
    }

    // Filter buttons ('btn-primary' + aria-pressed)
    const btns = document.querySelectorAll('[data-map-filter]');
    function setActive(btn){
      btns.forEach(b => {
        b.classList.remove('btn-primary');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('btn-primary');
      btn.setAttribute('aria-pressed', 'true');
    }
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        setActive(btn);
        loadMarkers(btn.value || '');
      });
    });

    // Initial state (All)
    const first = btns[0];
    if (first){ setActive(first); }
    loadMarkers('');
  }

  // ---------- Upvotes (fetch + CSRF + login redirect) ----------
  function initUpvotes(){
    delegate(document, 'click', '[data-upvote-btn]', async (e, btn) => {
      e.preventDefault();
      const url = btn.getAttribute('data-url');
      if (!url || btn.disabled) return;

      try {
        const { response, data } = await window.ajaxRequest(url, {
          method: 'POST',
          credentials: 'same-origin',
          redirect: 'follow'
        }, btn);

        // If not logged in, server may redirect to login
        if (response.redirected) {
          window.location = response.url;
          return;
        }

        if (data && data.success){
          const up = !!data.upvoted;
          btn.classList.toggle('is-active', up);
          btn.setAttribute('aria-pressed', up ? 'true' : 'false');
          const cnt = btn.querySelector('[data-count]');
          if (cnt && typeof data.count === 'number') cnt.textContent = data.count;
        }
      } catch (err) {
        console.error('Upvote failed:', err);
      }
    });
  }

  // ---------- Filters: "Create" dropdown (used by _filters.html) ----------
  function initFiltersDropdown(){
    const holders = document.querySelectorAll('.filters .dropdown');
    holders.forEach((holder) => {
      const toggle = holder.querySelector('[data-dropdown-toggle]') || holder.querySelector('button');
      const menu = holder.querySelector('[data-dropdown-menu]') || holder.querySelector('.menu');
      if (!toggle || !menu) return;

      const close = () => holder.setAttribute('aria-expanded', 'false');
      const open  = () => holder.setAttribute('aria-expanded', 'true');

      holder.setAttribute('aria-expanded', 'false');

      toggle.addEventListener('click', (e) => {
        e.preventDefault();
        holder.getAttribute('aria-expanded') === 'true' ? close() : open();
      });

      const offOutside = clickOutside(holder, close);
      const offEsc = onEsc(close);

      window.addEventListener('unload', () => { offOutside(); offEsc(); });
    });
  }

  // ---------- Optional: stat counters (data-count-to or data-count) ----------
  window.initCounters = function initCounters(){
    const counters = document.querySelectorAll('[data-count-to], .stat-number[data-count]');
    if (!counters.length) return;

    if ('IntersectionObserver' in window){
      const animate = (el) => {
        const to = parseInt(el.getAttribute('data-count-to') || el.getAttribute('data-count') || '0', 10);
        const start = 0;
        const suffix = el.getAttribute('data-suffix') || '';
        const dur = 800 + Math.min(1400, to * 10);
        const t0 = performance.now();
        const step = (t) => {
          const p = Math.min(1, (t - t0) / dur);
          const ease = 1 - Math.pow(1 - p, 3); // easeOutCubic
          const current = Math.round(start + (to - start) * ease);
          el.textContent = current + suffix;
          if (p < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      };
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting){ animate(entry.target); io.unobserve(entry.target); }
        });
      }, { threshold: 0.5 });
      counters.forEach(el => io.observe(el));
    } else {
      counters.forEach(el => {
        const val = el.getAttribute('data-count-to') || el.getAttribute('data-count') || '0';
        el.textContent = val + (el.getAttribute('data-suffix') || '');
      });
    }
  }

  // ---------- Scroll Progress Bar ----------
  window.initScrollProgress = function initScrollProgress(){
    const progressBar = document.querySelector('.scroll-progress-bar');
    if (!progressBar) return;

    function updateProgress(){
      const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (window.scrollY / windowHeight) * 100;
      progressBar.style.width = scrolled + '%';
      document.getElementById('scroll-progress')?.setAttribute('aria-valuenow', Math.round(scrolled));
    }

    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
  }

  // ---------- Floating CTA ----------
  window.initFloatingCTA = function initFloatingCTA(){
    const floatingCTA = document.getElementById('floating-cta');
    if (!floatingCTA) return;

    function checkScroll(){
      if (window.scrollY > 400) {
        floatingCTA.classList.add('show');
      } else {
        floatingCTA.classList.remove('show');
      }
    }

    window.addEventListener('scroll', checkScroll, { passive: true });
    checkScroll();
  }

  // ---------- Section Navigation Dots ----------
  window.initSectionNavDots = function initSectionNavDots(){
    const navDots = document.querySelector('.section-nav-dots');
    if (!navDots) return;

    const sections = document.querySelectorAll('section[id], [id^="map"]');
    const dots = navDots.querySelectorAll('.nav-dot');

    function updateActiveDot(){
      const scrollPos = window.scrollY + 200;
      let current = '';

      sections.forEach(section => {
        const top = section.offsetTop;
        const height = section.offsetHeight;
        if (scrollPos >= top && scrollPos < top + height) {
          current = section.id;
        }
      });

      dots.forEach(dot => {
        const href = dot.getAttribute('href');
        if (href === `#${current}` || (current === '' && href === '#hero')) {
          dot.classList.add('active');
        } else {
          dot.classList.remove('active');
        }
      });

      // Show/hide nav dots based on scroll
      if (window.scrollY > 300) {
        navDots.classList.add('show');
      } else {
        navDots.classList.remove('show');
      }
    }

    window.addEventListener('scroll', updateActiveDot, { passive: true });
    updateActiveDot();

    // Smooth scroll on click
    dots.forEach(dot => {
      dot.addEventListener('click', (e) => {
        e.preventDefault();
        const href = dot.getAttribute('href');
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  // ---------- Mobile Bottom Navigation ----------
  window.initMobileBottomNav = function initMobileBottomNav(){
    const navItems = document.querySelectorAll('.mobile-nav-item');
    if (!navItems.length) return;

    function updateActiveNav(){
      const scrollPos = window.scrollY + 300;
      const sections = document.querySelectorAll('section[id], [id^="map"]');
      let current = 'hero';

      sections.forEach(section => {
        const top = section.offsetTop;
        const height = section.offsetHeight;
        if (scrollPos >= top && scrollPos < top + height) {
          current = section.id;
        }
      });

      navItems.forEach(item => {
        const section = item.getAttribute('data-section');
        if (section === current || (current === '' && section === 'hero')) {
          item.classList.add('active');
        } else {
          item.classList.remove('active');
        }
      });
    }

    window.addEventListener('scroll', updateActiveNav, { passive: true });
    updateActiveNav();

    // Smooth scroll for section links
    navItems.forEach(item => {
      const href = item.getAttribute('href');
      if (href && href.startsWith('#')) {
        item.addEventListener('click', (e) => {
          const target = document.querySelector(href);
          if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        });
      }
    });
  }

  // ---------- Init ----------
  ready(() => {
    initHero();
    initLightbox();
    initScrollProgress();
    initFloatingCTA();
    initSectionNavDots();
    initMobileBottomNav();
    // Initialize map after a small delay to ensure Leaflet is fully loaded
    if (typeof L !== 'undefined') {
      initMap();
    } else {
      // Wait for Leaflet if it's still loading
      const checkLeaflet = setInterval(() => {
        if (typeof L !== 'undefined') {
          clearInterval(checkLeaflet);
          initMap();
        }
      }, 100);
      // Timeout after 5 seconds
      setTimeout(() => {
        clearInterval(checkLeaflet);
        if (typeof L === 'undefined') {
          console.error('Leaflet failed to load after 5 seconds');
        }
      }, 5000);
    }
    initUpvotes();
    initFiltersDropdown();
    initCounters();
    initScrollReveal();
  });
})();