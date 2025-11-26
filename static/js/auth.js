/* UrbanVista • Auth interactions */
(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    // Password visibility toggle
    document.querySelectorAll('.input-pass').forEach(function (wrap) {
      const input = wrap.querySelector('input[type="password"], input[type="text"]');
      const btn = wrap.querySelector('.pass-toggle');
      if (!input || !btn) return;

      btn.addEventListener('click', function () {
        const isPw = input.getAttribute('type') === 'password';
        input.setAttribute('type', isPw ? 'text' : 'password');
        btn.setAttribute('aria-label', isPw ? 'Hide password' : 'Show password');
      });
    });

    // Optional: lock submit to avoid double posts
    const form = document.querySelector('.auth-form');
    if (form) {
      form.addEventListener('submit', function () {
        const btn = form.querySelector('button[type="submit"]');
        if (btn) {
          btn.disabled = true;
          btn.dataset.originalText = btn.textContent;
          btn.textContent = 'Signing in...';
        }
      });
    }
  });
})();


/* Subtle tilt on the glass card */
(function () {
  'use strict';
  function ready(fn){ if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',fn); else fn(); }

  ready(function(){
    const card = document.querySelector('.glass-card[data-tilt]');
    if(!card) return;
    const strength = 10; // degrees
    let raf = null;

    function onMove(e){
      const rect = card.getBoundingClientRect();
      const cx = rect.left + rect.width/2;
      const cy = rect.top + rect.height/2;
      const dx = (e.clientX - cx) / (rect.width/2);
      const dy = (e.clientY - cy) / (rect.height/2);
      const rotX = (+dy * strength);
      const rotY = (-dx * strength);
      if(raf) cancelAnimationFrame(raf);
      raf = requestAnimationFrame(()=> {
        card.style.transform = `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateZ(0)`;
      });
    }
    function reset(){
      if(raf) cancelAnimationFrame(raf);
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0)';
    }
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseleave', reset);
  });
})();