/**
 * Admin Dashboard Animations and Chart Interactions
 */
(function() {
  'use strict';

  function initChartAnimations() {
    // Animate bar charts
    const chartBars = document.querySelectorAll('.chart-bar[data-value]');
    chartBars.forEach(bar => {
      const value = parseInt(bar.getAttribute('data-value'), 10);
      const fill = bar.querySelector('.chart-fill');
      if (fill && value > 0) {
        // Set CSS variable for animation
        bar.style.setProperty('--chart-width', Math.min(value, 100) + '%');
        // Trigger animation
        setTimeout(() => {
          fill.style.width = Math.min(value, 100) + '%';
        }, 100);
      }
    });

    // Animate multiple bar charts
    const barFills = document.querySelectorAll('.bar-fill[data-percent]');
    barFills.forEach(bar => {
      const percent = parseInt(bar.getAttribute('data-percent'), 10);
      if (percent > 0) {
        setTimeout(() => {
          bar.style.width = percent + '%';
        }, 300);
      }
    });

    // Animate pie charts
    const pieCharts = document.querySelectorAll('.pie-fill[data-percent]');
    pieCharts.forEach(pie => {
      const percent = parseInt(pie.getAttribute('data-percent'), 10);
      if (percent > 0) {
        const circumference = 2 * Math.PI * 40; // radius is 40
        const offset = circumference - (percent / 100) * circumference;
        setTimeout(() => {
          pie.style.strokeDashoffset = offset;
        }, 200);
      }
    });

    // Animate full pie charts
    const fullPieCharts = document.querySelectorAll('.pie-fill-full[data-percent]');
    fullPieCharts.forEach(pie => {
      const percent = parseInt(pie.getAttribute('data-percent'), 10);
      if (percent > 0) {
        const circumference = 2 * Math.PI * 90; // radius is 90
        const offset = circumference - (percent / 100) * circumference;
        setTimeout(() => {
          pie.style.strokeDashoffset = offset;
        }, 400);
      }
    });

    // Trigger animations on scroll
    if ('IntersectionObserver' in window) {
      const observerOptions = {
        threshold: 0.2,
        rootMargin: '0px'
      };

      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate');
            observer.unobserve(entry.target);
          }
        });
      }, observerOptions);

      document.querySelectorAll('.chart-wrapper, .chart-module').forEach(chart => {
        observer.observe(chart);
      });
    } else {
      // Fallback for browsers without IntersectionObserver
      document.querySelectorAll('.chart-wrapper, .chart-module').forEach(chart => {
        chart.classList.add('animate');
      });
    }
  }

  // Mobile menu toggle
  function initMobileMenu() {
    const toggle = document.getElementById('mobile-menu-toggle');
    const sidebar = document.getElementById('sidebar');
    
    if (toggle && sidebar) {
      toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
      });
      
      // Close sidebar when clicking outside on mobile
      document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
          if (!sidebar.contains(e.target) && !toggle.contains(e.target) && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
          }
        }
      });
    }
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initChartAnimations();
      initMobileMenu();
    });
  } else {
    initChartAnimations();
    initMobileMenu();
  }
})();
