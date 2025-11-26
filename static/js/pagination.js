/* UrbanVista • Pagination with Loading States */
(function() {
  'use strict';

  function initPagination() {
    // Handle pagination links with loading states
    document.addEventListener('click', async function(e) {
      const link = e.target.closest('a[href*="?page="], a[data-pagination]');
      if (!link) return;

      // Check if it's a pagination link
      const url = new URL(link.href, window.location.origin);
      if (!url.searchParams.has('page') && !link.hasAttribute('data-pagination')) return;

      e.preventDefault();

      // Find the container to update
      const container = document.querySelector('[data-pagination-container]') || 
                       link.closest('.pagination')?.parentElement ||
                       document.querySelector('main, .container');

      if (!container) return;

      // Show loading state
      const loadingEl = document.createElement('div');
      loadingEl.className = 'pagination-loading';
      loadingEl.innerHTML = '<div class="spinner"></div><span>Loading...</span>';
      
      // Insert loading indicator
      const paginationEl = link.closest('.pagination');
      if (paginationEl) {
        paginationEl.insertAdjacentElement('afterend', loadingEl);
      } else {
        container.insertAdjacentElement('beforeend', loadingEl);
      }

      try {
        // Fetch the new page
        const response = await fetch(link.href, {
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          }
        });

        if (!response.ok) throw new Error('Failed to load page');

        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Find the content to replace
        const newContent = doc.querySelector('[data-pagination-container]') || 
                          doc.querySelector('main, .container') ||
                          doc.body;

        // Update URL without reload
        window.history.pushState({}, '', link.href);

        // Replace content
        if (container) {
          container.innerHTML = newContent.innerHTML;
        }

        // Re-initialize any scripts
        if (typeof window.initPageComponents === 'function') {
          window.initPageComponents();
        }

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });

      } catch (error) {
        if (typeof window.showToast === 'function') {
          window.showToast('Failed to load page. Please try again.', 'error');
        }
        console.error('Pagination error:', error);
      } finally {
        loadingEl.remove();
      }
    });

    // Handle browser back/forward buttons
    window.addEventListener('popstate', function() {
      window.location.reload();
    });
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPagination);
  } else {
    initPagination();
  }
})();

