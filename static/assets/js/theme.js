/**
 * Theme management for the MediTracked application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    
    // Check if there's a saved preference in the server
    fetchThemePreference();
    
    // Add event listener to the theme toggle button
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            toggleTheme();
        });
    }
    
    /**
     * Fetch the user's theme preference from the server
     */
    function fetchThemePreference() {
        fetch('/theme/preference/', {
            method: 'GET',
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.dark_mode) {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
            updateThemeIcon();
        })
        .catch(error => {
            console.error('Error fetching theme preference:', error);
        });
    }
    
    /**
     * Toggle between light and dark theme
     */
    function toggleTheme() {
        // Send request to the server to toggle theme
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
                if (data.dark_mode) {
                    document.body.classList.add('dark-mode');
                } else {
                    document.body.classList.remove('dark-mode');
                }
                updateThemeIcon();
            }
        })
        .catch(error => {
            console.error('Error toggling theme:', error);
        });
    }
    
    /**
     * Update the theme toggle icon based on current theme
     */
    function updateThemeIcon() {
        const moonIcon = document.querySelector('.theme-toggle .fa-moon');
        const sunIcon = document.querySelector('.theme-toggle .fa-sun');
        
        if (document.body.classList.contains('dark-mode')) {
            if (moonIcon) moonIcon.style.display = 'none';
            if (sunIcon) sunIcon.style.display = 'inline-block';
        } else {
            if (moonIcon) moonIcon.style.display = 'inline-block';
            if (sunIcon) sunIcon.style.display = 'none';
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
