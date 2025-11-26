/* UrbanVista Home - All Improvements */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    initScrollProgress();
    initFloatingCTA();
    initSectionNavDots();
    initHeroSearch();
    initLiveChat();
    initNotifications();
    initMobileBottomNav();
    initHeroVideoControls();
    initHeroStatsCounter();
    initMap();
    initTabs();
    initCounters();
    initContactForm();
    initScrollReveal();
    initPageAnimations();
    initTestimonialsCarousel();
    initSmoothScroll();
    initFormAutoSave();
    initFormValidation();
  });

  // ============== 1. HERO SECTION IMPROVEMENTS ==============

  function initHeroStatsCounter() {
    const stats = document.querySelectorAll('.hero-stats .stat[data-count]');
    if (!stats.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const stat = entry.target;
        const count = parseInt(stat.dataset.count || '0', 10);
        const suffix = stat.dataset.suffix || '';
        const counter = stat.querySelector('.stat-counter');
        if (!counter) return;

        let current = 0;
        const step = Math.max(1, Math.floor(count / 60));
        const tick = () => {
          current += step;
          if (current < count) {
            counter.textContent = current.toLocaleString() + suffix;
            requestAnimationFrame(tick);
          } else {
            counter.textContent = count.toLocaleString() + suffix;
          }
        };
        tick();
        observer.unobserve(stat);
      });
    }, { threshold: 0.5 });

    stats.forEach(stat => observer.observe(stat));
  }

  function initHeroVideoControls() {
    const video = document.getElementById('hero-video');
    const playPauseBtn = document.getElementById('video-play-pause');
    const muteBtn = document.getElementById('video-mute');
    if (!video || !playPauseBtn || !muteBtn) return;

    playPauseBtn.addEventListener('click', () => {
      if (video.paused) {
        video.play();
        playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
      } else {
        video.pause();
        playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
      }
    });

    muteBtn.addEventListener('click', () => {
      video.muted = !video.muted;
      muteBtn.innerHTML = video.muted 
        ? '<i class="fas fa-volume-mute"></i>' 
        : '<i class="fas fa-volume-up"></i>';
    });
  }

  // ============== 2. FEATURES SECTION ==============
  // Handled by CSS hover effects

  // ============== 3. HOW IT WORKS ==============
  function initStepDemos() {
    document.querySelectorAll('.step-demo-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const demo = btn.dataset.demo;
        if (typeof window.showToast === 'function') {
          window.showToast(`Demo for "${demo}" coming soon!`, 'info');
        }
      });
    });
  }

  // ============== 4. SOLUTIONS TABS ==============
  function initTabs() {
    const buttons = document.querySelectorAll('.tab-btn');
    const panes = document.querySelectorAll('.tab-pane');
    if (!buttons.length) return;

    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.tab;
        buttons.forEach(b => b.classList.remove('active'));
        panes.forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const pane = document.getElementById(id);
        if (pane) {
          pane.classList.add('active');
          // Smooth transition
          pane.style.opacity = '0';
          setTimeout(() => {
            pane.style.opacity = '1';
          }, 50);
        }
      });
    });
  }

  // ============== 5. STATS SECTION ==============
  function initCounters() {
    const section = document.querySelector('.stats-section');
    if (!section) return;

    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        
        // Animate counters
        entry.target.querySelectorAll('.stat-number').forEach(counter => {
          const target = parseInt(counter.dataset.count || '0', 10);
          const step = Math.max(1, Math.floor(target / 180));
          let cur = 0;
          const tick = () => {
            cur += step;
            if (cur < target) {
              counter.textContent = cur.toLocaleString();
              requestAnimationFrame(tick);
            } else {
              counter.textContent = target.toLocaleString();
            }
          };
          tick();
        });

        // Animate progress bars
        entry.target.querySelectorAll('.stat-progress-bar').forEach(bar => {
          const progress = parseInt(bar.dataset.progress || '0', 10);
          bar.style.setProperty('--progress-width', progress + '%');
          setTimeout(() => {
            bar.style.width = progress + '%';
          }, 200);
        });

        obs.unobserve(entry.target);
      });
    }, { threshold: 0.5 });

    obs.observe(section);
  }

  // ============== 6. MAP SECTION ==============
  function initMap() {
    const el = document.getElementById('mapid');
    const loadingEl = document.getElementById('map-loading');
    if (!el || typeof L === 'undefined') return;

    // Show loading state
    if (loadingEl) {
      loadingEl.style.display = 'grid';
    }

    // Initialize map after a short delay to show loading
    setTimeout(() => {
    const map = L.map('mapid').setView([28.6139, 77.2090], 5);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);

    const markers = [
        { lat: 28.6139, lng: 77.2090, popup: 'New Delhi - Capital Region', type: 'places' },
        { lat: 19.0760, lng: 72.8777, popup: 'Mumbai - Financial Hub', type: 'places' },
        { lat: 13.0827, lng: 80.2707, popup: 'Chennai - Tech Center', type: 'activities' },
        { lat: 22.5726, lng: 88.3639, popup: 'Kolkata - Cultural Capital', type: 'stories' },
        { lat: 12.9716, lng: 77.5946, popup: 'Bangalore - Silicon Valley', type: 'places' }
      ];

      const markerObjects = markers.map(m => {
        const marker = L.marker([m.lat, m.lng]).addTo(map);
        marker.bindPopup(`<strong>${m.popup}</strong>`);
        marker.type = m.type;
        return marker;
      });

      // Map filters
      const filterBtns = document.querySelectorAll('.map-filter-btn');
      filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
          filterBtns.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          const filter = btn.dataset.filter;
          
          markerObjects.forEach(marker => {
            if (filter === 'all' || marker.type === filter) {
              marker.addTo(map);
            } else {
              map.removeLayer(marker);
            }
          });
        });
      });

    // Controls
    const zi = document.getElementById('zoom-in');
    const zo = document.getElementById('zoom-out');
    const fs = document.getElementById('full-screen');
    const wrap = document.querySelector('.map-wrapper');

    zi && zi.addEventListener('click', () => map.zoomIn());
    zo && zo.addEventListener('click', () => map.zoomOut());

    function requestFS(el) {
      (el.requestFullscreen || el.webkitRequestFullscreen || el.mozRequestFullScreen || el.msRequestFullscreen)?.call(el);
    }
    function exitFS() {
      (document.exitFullscreen || document.webkitExitFullscreen || document.mozCancelFullScreen || document.msExitFullscreen)?.call(document);
    }
    function isFS() {
      return document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement;
    }

    fs && wrap && fs.addEventListener('click', () => (!isFS() ? requestFS(wrap) : exitFS()));

    ['fullscreenchange', 'webkitfullscreenchange', 'mozfullscreenchange', 'MSFullscreenChange']
      .forEach(evt => document.addEventListener(evt, () => setTimeout(() => map.invalidateSize(), 60)));

    window.addEventListener('resize', () => {
      clearTimeout(window.__mapResizeTimer);
      window.__mapResizeTimer = setTimeout(() => map.invalidateSize(), 120);
    });

      // Hide loading, show map
      if (loadingEl) {
        loadingEl.style.display = 'none';
      }
      el.style.display = 'block';
      map.invalidateSize();

      // Update last updated time
      updateMapTimestamp();
      setInterval(updateMapTimestamp, 30000); // Update every 30 seconds
    }, 500);
  }

  function updateMapTimestamp() {
    const el = document.getElementById('map-last-updated');
    if (!el) return;
    const now = new Date();
    const seconds = Math.floor((Date.now() - now.getTime()) / 1000);
    if (seconds < 60) {
      el.textContent = 'Just now';
    } else if (seconds < 3600) {
      el.textContent = `${Math.floor(seconds / 60)} min ago`;
    } else {
      el.textContent = `${Math.floor(seconds / 3600)} hour${Math.floor(seconds / 3600) > 1 ? 's' : ''} ago`;
    }
  }

  // ============== 7. TESTIMONIALS CAROUSEL ==============
  function initTestimonialsCarousel() {
    const carousel = document.getElementById('testimonials-carousel');
    const items = carousel?.querySelectorAll('.testimonial-item');
    const prevBtn = document.querySelector('.carousel-prev');
    const nextBtn = document.querySelector('.carousel-next');
    const dots = document.querySelectorAll('.carousel-dot');
    if (!carousel || !items.length) return;

    let currentIndex = 0;
    const totalItems = items.length;
    let autoRotateInterval = null;

    function showSlide(index) {
      items.forEach((item, i) => {
        item.classList.toggle('active', i === index);
      });
      dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
      });
      currentIndex = index;
    }

    function nextSlide() {
      showSlide((currentIndex + 1) % totalItems);
    }

    function prevSlide() {
      showSlide((currentIndex - 1 + totalItems) % totalItems);
    }

    function startAutoRotate() {
      if (carousel.dataset.rotate === 'true') {
        autoRotateInterval = setInterval(nextSlide, 5000);
      }
    }

    function stopAutoRotate() {
      if (autoRotateInterval) {
        clearInterval(autoRotateInterval);
        autoRotateInterval = null;
      }
    }

    nextBtn?.addEventListener('click', () => {
      nextSlide();
      stopAutoRotate();
      startAutoRotate();
    });

    prevBtn?.addEventListener('click', () => {
      prevSlide();
      stopAutoRotate();
      startAutoRotate();
    });

    dots.forEach((dot, index) => {
      dot.addEventListener('click', () => {
        showSlide(index);
        stopAutoRotate();
        startAutoRotate();
      });
    });

    // Swipe gestures for mobile
    let touchStartX = 0;
    let touchEndX = 0;
    carousel.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
    });
    carousel.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    });

    function handleSwipe() {
      if (touchEndX < touchStartX - 50) nextSlide();
      if (touchEndX > touchStartX + 50) prevSlide();
    }

    startAutoRotate();
  }

  // ============== 8. CTA SECTION ==============
  // Handled by CSS

  // ============== 9. CONTACT FORM ==============
  function initContactForm() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    const feedback = document.getElementById('contact-feedback');
    const btn = document.getElementById('contact-submit');
    
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!btn) return;
      
      feedback.className = 'form-feedback';
      feedback.textContent = '';

      try {
        const { response, data } = await window.ajaxForm(form, btn);
        
        if (response.ok && (data?.ok || data?.success)) {
          // Success animation
          btn.classList.add('success');
          feedback.className = 'form-feedback success';
          feedback.textContent = data.message || 'Thanks! Your message has been sent.';
          
          // Confetti effect (simple)
          createSuccessEffect(btn);
          
          // Clear autosave
          if (form.dataset.autosave === 'true') {
            clearFormAutoSave();
          }
          
          form.reset();
          updateCharCount();
          setTimeout(() => {
          form.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 500);
        } else {
          feedback.className = 'form-feedback error';
          feedback.textContent = data?.message || 'Please check the form and try again.';
        }
      } catch (err) {
        feedback.className = 'form-feedback error';
        feedback.textContent = err.message || 'Something went wrong. Please try again.';
      }
    });
  }

  function createSuccessEffect(element) {
    const checkmark = document.createElement('div');
    checkmark.style.cssText = `
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: #22c55e;
      display: grid;
      place-items: center;
      color: white;
      font-size: 32px;
      z-index: 1000;
      animation: pop-in 0.5s ease;
    `;
    checkmark.innerHTML = '<i class="fas fa-check"></i>';
    element.style.position = 'relative';
    element.appendChild(checkmark);
    setTimeout(() => checkmark.remove(), 1000);
  }

  function initFormValidation() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    const fields = form.querySelectorAll('[data-validate]');
    fields.forEach(field => {
      field.addEventListener('blur', () => validateField(field));
      field.addEventListener('input', () => {
        if (field.classList.contains('is-invalid')) {
          validateField(field);
        }
      });
    });
  }

  function validateField(field) {
    const errorEl = field.closest('.form-field-wrapper')?.querySelector('.field-error');
    if (!errorEl) return;

    let isValid = true;
    let errorMsg = '';

    if (field.dataset.validate === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      isValid = emailRegex.test(field.value);
      errorMsg = isValid ? '' : 'Please enter a valid email address';
    } else if (field.dataset.validate === 'name') {
      isValid = field.value.trim().length >= 2;
      errorMsg = isValid ? '' : 'Name must be at least 2 characters';
    } else if (field.dataset.validate === 'select') {
      isValid = field.value !== '';
      errorMsg = isValid ? '' : 'Please select a subject';
    } else if (field.dataset.validate === 'message') {
      isValid = field.value.trim().length >= 10;
      errorMsg = isValid ? '' : 'Message must be at least 10 characters';
    }

    if (isValid) {
      field.classList.remove('is-invalid');
      field.classList.add('is-valid');
      errorEl.textContent = '';
    } else {
      field.classList.remove('is-valid');
      field.classList.add('is-invalid');
      errorEl.textContent = errorMsg;
    }
  }

  function initFormAutoSave() {
    const form = document.getElementById('contact-form');
    if (!form || form.dataset.autosave !== 'true') return;

    const fields = ['name', 'email', 'subject', 'message'];
    const storageKey = 'contact-form-draft';

    // Load saved data
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const data = JSON.parse(saved);
        fields.forEach(field => {
          const el = form.querySelector(`[name="${field}"]`);
          if (el && data[field]) {
            el.value = data[field];
            updateCharCount();
          }
        });
      }
    } catch (e) {}

    // Auto-save on input
    form.addEventListener('input', () => {
      const data = {};
      fields.forEach(field => {
        const el = form.querySelector(`[name="${field}"]`);
        if (el) data[field] = el.value;
      });
      try {
        localStorage.setItem(storageKey, JSON.stringify(data));
      } catch (e) {}
    });

    // Clear on successful submit
    form.addEventListener('submit', () => {
      setTimeout(() => {
        try {
          localStorage.removeItem(storageKey);
        } catch (e) {}
      }, 1000);
    });
  }

  function clearFormAutoSave() {
    try {
      localStorage.removeItem('contact-form-draft');
    } catch (e) {}
  }

  function updateCharCount() {
    const textarea = document.getElementById('contact-message');
    const counter = document.getElementById('char-count');
    if (textarea && counter) {
      counter.textContent = textarea.value.length;
    }
  }

  // Initialize character counter
  const messageField = document.getElementById('contact-message');
  if (messageField) {
    messageField.addEventListener('input', updateCharCount);
    updateCharCount();
  }

  // ============== 10. GENERAL IMPROVEMENTS ==============

  function initScrollProgress() {
    const progressBar = document.querySelector('.scroll-progress-bar');
    if (!progressBar) return;

    function updateProgress() {
      const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (window.scrollY / windowHeight) * 100;
      progressBar.style.width = scrolled + '%';
      document.getElementById('scroll-progress')?.setAttribute('aria-valuenow', Math.round(scrolled));
    }

    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
  }

  function initFloatingCTA() {
    const floatingCTA = document.getElementById('floating-cta');
    if (!floatingCTA) return;

    function checkScroll() {
      if (window.scrollY > 400) {
        floatingCTA.classList.add('show');
      } else {
        floatingCTA.classList.remove('show');
      }
    }

    window.addEventListener('scroll', checkScroll, { passive: true });
    checkScroll();
  }

  function initSectionNavDots() {
    const navDots = document.querySelector('.section-nav-dots');
    const sections = document.querySelectorAll('section[id]');
    if (!navDots || !sections.length) return;

    // Show nav dots after scroll
    function showNavDots() {
      if (window.scrollY > 300) {
        navDots.classList.add('show');
      } else {
        navDots.classList.remove('show');
      }
    }

    // Update active dot based on scroll position
    function updateActiveDot() {
      const scrollPos = window.scrollY + 200;
      let activeSection = '';

      sections.forEach(section => {
        const top = section.offsetTop;
        const bottom = top + section.offsetHeight;
        if (scrollPos >= top && scrollPos < bottom) {
          activeSection = section.id;
        }
      });

      navDots.querySelectorAll('.nav-dot').forEach(dot => {
        dot.classList.toggle('active', dot.dataset.section === activeSection);
      });
    }

    window.addEventListener('scroll', () => {
      showNavDots();
      updateActiveDot();
    }, { passive: true });

    // Smooth scroll on click
    navDots.querySelectorAll('.nav-dot').forEach(dot => {
      dot.addEventListener('click', (e) => {
        e.preventDefault();
        const sectionId = dot.dataset.section;
        const section = document.getElementById(sectionId);
        if (section) {
          section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#' || href === '#!') return;
        
        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  function initHeroSearch() {
    const searchToggle = document.querySelector('[data-search-toggle]');
    const searchPanel = document.getElementById('hero-search');
    const searchClose = document.getElementById('search-close');
    const searchInput = document.getElementById('global-search');
    const searchResults = document.getElementById('search-results');

    // Toggle search (can be triggered by keyboard shortcut '/')
    function toggleSearch() {
      if (searchPanel) {
        searchPanel.classList.toggle('show');
        if (searchPanel.classList.contains('show') && searchInput) {
          setTimeout(() => searchInput.focus(), 100);
        }
      }
    }

    searchToggle?.addEventListener('click', toggleSearch);
    searchClose?.addEventListener('click', () => {
      searchPanel?.classList.remove('show');
    });

    // Search functionality
    if (searchInput) {
      let searchTimeout;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
          searchResults?.classList.remove('show');
          return;
        }

        searchTimeout = setTimeout(() => {
          // Simulate search results
          performSearch(query);
        }, 300);
      });

      // Close on Escape
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          searchPanel?.classList.remove('show');
        }
      });
    }
  }

  function performSearch(query) {
    const results = document.getElementById('search-results');
    if (!results) return;

    // Simulate search - in real app, this would be an API call
    const mockResults = [
      { title: 'Contribution: New Park', type: 'place', url: '#' },
      { title: 'Activity: Food Festival', type: 'activity', url: '#' },
      { title: 'Story: City Transformation', type: 'story', url: '#' }
    ].filter(item => item.title.toLowerCase().includes(query.toLowerCase()));

    if (mockResults.length > 0) {
      results.innerHTML = mockResults.map(item => `
        <div class="search-result-item">
          <i class="fas fa-${item.type === 'place' ? 'map-marker-alt' : item.type === 'activity' ? 'star' : 'book'}" style="color: var(--uv-c-link);"></i>
          <div>
            <strong>${item.title}</strong>
            <span>${item.type}</span>
          </div>
        </div>
      `).join('');
      results.classList.add('show');
    } else {
      results.innerHTML = '<div class="search-result-item">No results found</div>';
      results.classList.add('show');
    }
  }

  function initLiveChat() {
    const chatToggle = document.querySelector('.chat-toggle');
    const chatWindow = document.getElementById('chat-window');
    const chatClose = document.querySelector('.chat-close');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.querySelector('.chat-send');
    const chatMessages = document.getElementById('chat-messages');

    chatToggle?.addEventListener('click', () => {
      chatWindow?.classList.toggle('show');
    });

    chatClose?.addEventListener('click', () => {
      chatWindow?.classList.remove('show');
    });

    function sendMessage() {
      const message = chatInput?.value.trim();
      if (!message || !chatMessages) return;

      // Add user message
      const userMsg = document.createElement('div');
      userMsg.className = 'chat-message user';
      userMsg.innerHTML = `<p>${message}</p>`;
      chatMessages.appendChild(userMsg);

      // Clear input
      if (chatInput) chatInput.value = '';

      // Simulate bot response
      setTimeout(() => {
        const botMsg = document.createElement('div');
        botMsg.className = 'chat-message bot';
        botMsg.innerHTML = '<p>Thanks for your message! Our team will get back to you soon.</p>';
        chatMessages.appendChild(botMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
      }, 1000);

      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    chatSend?.addEventListener('click', sendMessage);
    chatInput?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMessage();
    });
  }

  function initNotifications() {
    const bellToggle = document.querySelector('.bell-toggle');
    const notificationPanel = document.getElementById('notification-panel');
    const notificationClose = document.querySelector('.notification-close');

    bellToggle?.addEventListener('click', () => {
      notificationPanel?.classList.toggle('show');
    });

    notificationClose?.addEventListener('click', () => {
      notificationPanel?.classList.remove('show');
    });

    // Mark as read on click
    document.querySelectorAll('.notification-item').forEach(item => {
      item.addEventListener('click', () => {
        item.classList.remove('unread');
        updateNotificationBadge();
      });
    });
  }

  function updateNotificationBadge() {
    const unreadCount = document.querySelectorAll('.notification-item.unread').length;
    const badge = document.querySelector('.notification-badge');
    if (badge) {
      if (unreadCount > 0) {
        badge.textContent = unreadCount;
        badge.style.display = 'grid';
      } else {
        badge.style.display = 'none';
      }
    }
  }

  // Social proof banner removed

  function initMobileBottomNav() {
    const navItems = document.querySelectorAll('.mobile-nav-item');
    if (!navItems.length) return;

    // Update active item on scroll
    function updateActiveNav() {
      const scrollPos = window.scrollY + 200;
      const sections = ['home', 'features', 'map', 'contact'];
      
      sections.forEach((sectionId, index) => {
        const section = document.getElementById(sectionId);
        if (section) {
          const top = section.offsetTop;
          const bottom = top + section.offsetHeight;
          if (scrollPos >= top && scrollPos < bottom) {
            navItems.forEach(item => item.classList.remove('active'));
            navItems[index]?.classList.add('active');
          }
        }
      });
    }

    window.addEventListener('scroll', updateActiveNav, { passive: true });
    updateActiveNav();

    // Smooth scroll on click
    navItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const href = item.getAttribute('href');
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  function initScrollReveal() {
    if (typeof IntersectionObserver === 'undefined') {
      document.querySelectorAll('.reveal').forEach(el => {
        el.classList.add('is-visible');
        el.style.opacity = '1';
        el.style.transform = 'none';
      });
      return;
    }
    
    const reveals = document.querySelectorAll('.reveal');
    if (!reveals.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          entry.target.style.opacity = '1';
          entry.target.style.transform = entry.target.style.transform || 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.05,
      rootMargin: '0px 0px -20px 0px'
    });

    reveals.forEach(el => {
      observer.observe(el);
      setTimeout(() => {
        if (!el.classList.contains('is-visible')) {
          el.classList.add('is-visible');
          el.style.opacity = '1';
          el.style.transform = 'translateY(0)';
        }
      }, 2000);
    });
  }

  function initPageAnimations() {
    // Hero animation
    const hero = document.querySelector('.hero-alt');
    if (hero) {
      hero.classList.add('fade-in');
      const heroLeft = hero.querySelector('.hero-left');
      const heroRight = hero.querySelector('.hero-right');
      if (heroLeft) {
        setTimeout(() => heroLeft.classList.add('slide-right'), 50);
      }
      if (heroRight) {
        setTimeout(() => heroRight.classList.add('slide-left'), 150);
      }
    }

    // Animate chips
    const chips = document.querySelectorAll('.chip');
    chips.forEach((chip, i) => {
      setTimeout(() => {
        chip.classList.add('pop-in');
        chip.style.opacity = '1';
        chip.style.transform = 'scale(1)';
      }, 800 + (i * 100));
    });

    // Stagger animations
    setTimeout(() => {
      const featuresGrid = document.querySelector('.features-grid');
      if (featuresGrid) {
        featuresGrid.classList.add('stagger');
        const cards = featuresGrid.querySelectorAll('.feature-card');
        cards.forEach((card, index) => {
          setTimeout(() => {
            card.classList.add('animated');
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, index * 80);
        });
      }
      
      const stepsWrapper = document.querySelector('.steps-wrapper');
      if (stepsWrapper) {
        stepsWrapper.classList.add('stagger');
        const steps = stepsWrapper.querySelectorAll('.step-item');
        steps.forEach((step, index) => {
          setTimeout(() => {
            step.classList.add('animated');
            step.style.opacity = '1';
            step.style.transform = 'translateY(0)';
          }, index * 80);
        });
      }

      initStepDemos();
    }, 100);
  }

  // Keyboard shortcut for search
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
      e.preventDefault();
      const searchPanel = document.getElementById('hero-search');
      if (searchPanel) {
        searchPanel.classList.add('show');
        const searchInput = document.getElementById('global-search');
        setTimeout(() => searchInput?.focus(), 100);
      }
    }
  });
})();
