/* UrbanVista • Tooltip System */
(function() {
  'use strict';

  let activeTooltip = null;
  let hideTimeout = null;

  function createTooltip(text, position = 'top') {
    const tooltip = document.createElement('div');
    tooltip.className = `tooltip tooltip-${position}`;
    tooltip.textContent = text;
    tooltip.setAttribute('role', 'tooltip');
    document.body.appendChild(tooltip);
    return tooltip;
  }

  function showTooltip(element, text, position = 'top') {
    if (activeTooltip) {
      hideTooltip();
    }

    const tooltip = createTooltip(text, position);
    activeTooltip = { element, tooltip };

    // Position tooltip
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    const scrollY = window.scrollY;
    const scrollX = window.scrollX;

    let top, left;

    switch (position) {
      case 'top':
        top = rect.top + scrollY - tooltipRect.height - 8;
        left = rect.left + scrollX + (rect.width / 2) - (tooltipRect.width / 2);
        break;
      case 'bottom':
        top = rect.bottom + scrollY + 8;
        left = rect.left + scrollX + (rect.width / 2) - (tooltipRect.width / 2);
        break;
      case 'left':
        top = rect.top + scrollY + (rect.height / 2) - (tooltipRect.height / 2);
        left = rect.left + scrollX - tooltipRect.width - 8;
        break;
      case 'right':
        top = rect.top + scrollY + (rect.height / 2) - (tooltipRect.height / 2);
        left = rect.right + scrollX + 8;
        break;
    }

    // Keep tooltip within viewport
    const padding = 8;
    if (left < padding) left = padding;
    if (left + tooltipRect.width > window.innerWidth - padding) {
      left = window.innerWidth - tooltipRect.width - padding;
    }
    if (top < scrollY + padding) {
      top = scrollY + padding;
      if (position === 'top') {
        tooltip.className = 'tooltip tooltip-bottom';
      }
    }

    tooltip.style.top = `${top}px`;
    tooltip.style.left = `${left}px`;

    // Show tooltip
    requestAnimationFrame(() => {
      tooltip.classList.add('show');
    });
  }

  function hideTooltip() {
    if (activeTooltip) {
      activeTooltip.tooltip.classList.remove('show');
      setTimeout(() => {
        if (activeTooltip && activeTooltip.tooltip.parentNode) {
          activeTooltip.tooltip.parentNode.removeChild(activeTooltip.tooltip);
        }
        activeTooltip = null;
      }, 200);
    }
    if (hideTimeout) {
      clearTimeout(hideTimeout);
      hideTimeout = null;
    }
  }

  function initTooltips() {
    // Handle [data-tooltip] attributes
    document.addEventListener('mouseenter', function(e) {
      const element = e.target.closest('[data-tooltip]');
      if (!element) return;

      const text = element.getAttribute('data-tooltip');
      const position = element.getAttribute('data-tooltip-position') || 'top';
      
      if (hideTimeout) clearTimeout(hideTimeout);
      hideTimeout = setTimeout(() => {
        showTooltip(element, text, position);
      }, 300);
    }, true);

    document.addEventListener('mouseleave', function(e) {
      const element = e.target.closest('[data-tooltip]');
      if (element && activeTooltip && activeTooltip.element === element) {
        hideTooltip();
      }
    }, true);

    // Handle focus for keyboard navigation
    document.addEventListener('focusin', function(e) {
      const element = e.target.closest('[data-tooltip]');
      if (!element) return;

      const text = element.getAttribute('data-tooltip');
      const position = element.getAttribute('data-tooltip-position') || 'top';
      showTooltip(element, text, position);
    });

    document.addEventListener('focusout', function(e) {
      const element = e.target.closest('[data-tooltip]');
      if (element && activeTooltip && activeTooltip.element === element) {
        hideTooltip();
      }
    });

    // Hide on scroll
    document.addEventListener('scroll', hideTooltip, true);
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTooltips);
  } else {
    initTooltips();
  }

  // Export for programmatic use
  window.showTooltip = showTooltip;
  window.hideTooltip = hideTooltip;
})();

