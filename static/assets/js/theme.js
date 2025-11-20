/**
 * Theme management for the MediTracked application
 */

document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const rootElement = document.documentElement;
    const bodyElement = document.body;
    const isAuthenticated = bodyElement?.dataset?.userAuth === 'true';

    const initialMode = rootElement.getAttribute('data-bs-theme') || 'light';
    localStorage.setItem('data-bs-theme', initialMode);
    updateThemeIcon(initialMode);

    if (isAuthenticated) {
        fetchThemePreference();
    }

    if (themeToggle && isAuthenticated) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    function fetchThemePreference() {
        fetch('/theme/preference/', {
            method: 'GET',
            credentials: 'same-origin'
        })
            .then(response => {
                if (response.status === 403 || response.status === 401) {
                    return null;
                }
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (!data) {
                    return;
                }
                applyThemeMode(Boolean(data.dark_mode));
            })
            .catch(error => {
                console.error('Error fetching theme preference:', error);
            });
    }

    function toggleTheme() {
        fetch('/theme/toggle/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({})
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    applyThemeMode(Boolean(data.dark_mode));
                }
            })
            .catch(error => {
                console.error('Error toggling theme:', error);
            });
    }

    function applyThemeMode(isDark) {
        const mode = isDark ? 'dark' : 'light';
        if (rootElement.getAttribute('data-bs-theme') !== mode) {
            rootElement.setAttribute('data-bs-theme', mode);
        }
        localStorage.setItem('data-bs-theme', mode);
        updateThemeIcon(mode);
    }

    function updateThemeIcon(explicitMode) {
        const currentMode = explicitMode || rootElement.getAttribute('data-bs-theme') || 'light';
        const isDarkMode = currentMode === 'dark';
        const moonIcon = document.querySelector('.theme-toggle .fa-moon');
        const sunIcon = document.querySelector('.theme-toggle .fa-sun');

        if (moonIcon) {
            moonIcon.style.display = isDarkMode ? 'none' : 'inline-block';
        }

        if (sunIcon) {
            sunIcon.style.display = isDarkMode ? 'inline-block' : 'none';
        }
    }
    
    /**
     * Get CSRF token from cookies
     */
    function getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
