/* UrbanVista • AJAX Helper with Loading States */
(function() {
  'use strict';

  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  }

  function getCSRFToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    return input ? input.value : getCookie('csrftoken');
  }

  /**
   * Enhanced AJAX request with automatic loading states
   * @param {string} url - Request URL
   * @param {Object} options - Fetch options
   * @param {HTMLElement|string} loadingButton - Button element or selector to show loading state
   * @param {HTMLElement|string} loadingContainer - Container to show skeleton loader
   * @returns {Promise<Response>}
   */
  window.ajaxRequest = async function(url, options = {}, loadingButton = null, loadingContainer = null) {
    const defaultOptions = {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      credentials: 'same-origin',
    };

    // Add CSRF token for non-GET requests
    if (options.method && options.method !== 'GET') {
      const token = getCSRFToken();
      if (token) {
        defaultOptions.headers['X-CSRFToken'] = token;
      }
    }

    // Merge options
    const finalOptions = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...(options.headers || {}),
      },
    };

    // Handle loading button
    let buttonElement = null;
    if (loadingButton) {
      buttonElement = typeof loadingButton === 'string' 
        ? document.querySelector(loadingButton) 
        : loadingButton;
      if (buttonElement && typeof window.setButtonLoading === 'function') {
        window.setButtonLoading(buttonElement, true);
      }
    }

    // Handle loading container (skeleton loader)
    let containerElement = null;
    let originalContent = null;
    if (loadingContainer) {
      containerElement = typeof loadingContainer === 'string'
        ? document.querySelector(loadingContainer)
        : loadingContainer;
      if (containerElement) {
        originalContent = containerElement.innerHTML;
        containerElement.innerHTML = '<div class="skeleton-loader skeleton-card"><div class="skeleton-text"></div><div class="skeleton-text short"></div><div class="skeleton-text medium"></div></div>';
        containerElement.classList.add('loading');
      }
    }

    try {
      const response = await fetch(url, finalOptions);

      // Handle redirects (e.g., login redirect)
      if (response.redirected) {
        window.location.href = response.url;
        return response;
      }

      // Check if response is JSON
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const data = await response.json();
        
        // Show error toast if request failed
        if (!response.ok) {
          const errorMsg = data.message || data.error || 'An error occurred';
          if (typeof window.showToast === 'function') {
            window.showToast(errorMsg, 'error');
          }
          throw new Error(errorMsg);
        }

        return { response, data };
      }

      return { response, data: null };
    } catch (error) {
      // Show error toast
      if (typeof window.showToast === 'function') {
        window.showToast(error.message || 'Request failed. Please try again.', 'error');
      }
      throw error;
    } finally {
      // Restore button state
      if (buttonElement && typeof window.setButtonLoading === 'function') {
        window.setButtonLoading(buttonElement, false);
      }

      // Restore container content
      if (containerElement && originalContent !== null) {
        containerElement.innerHTML = originalContent;
        containerElement.classList.remove('loading');
      }
    }
  };

  /**
   * Convenience method for GET requests
   */
  window.ajaxGet = function(url, loadingContainer = null) {
    return window.ajaxRequest(url, { method: 'GET' }, null, loadingContainer);
  };

  /**
   * Convenience method for POST requests
   */
  window.ajaxPost = function(url, data = {}, loadingButton = null, loadingContainer = null) {
    const options = {
      method: 'POST',
      body: typeof data === 'string' ? data : JSON.stringify(data),
    };
    return window.ajaxRequest(url, options, loadingButton, loadingContainer);
  };

  /**
   * Convenience method for form submissions
   */
  window.ajaxForm = function(form, loadingButton = null) {
    const formData = new FormData(form);
    const url = form.action || window.location.href;
    const method = form.method || 'POST';

    const options = {
      method: method.toUpperCase(),
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    };

    return window.ajaxRequest(url, options, loadingButton);
  };
})();

