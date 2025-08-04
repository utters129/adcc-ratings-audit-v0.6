/**
 * ADCC Analysis Engine - Main JavaScript
 * 
 * This file contains the main JavaScript functionality for the web interface,
 * including authentication, API calls, and common utilities.
 */

// Global variables
let currentUser = null;
let authToken = localStorage.getItem('authToken');

// API Base URL
const API_BASE = '/api';

// Utility functions
const utils = {
    /**
     * Show loading spinner
     */
    showLoading: function() {
        document.getElementById('loadingSpinner').style.display = 'block';
    },

    /**
     * Hide loading spinner
     */
    hideLoading: function() {
        document.getElementById('loadingSpinner').style.display = 'none';
    },

    /**
     * Show alert message
     */
    showAlert: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the main content
        const main = document.querySelector('main');
        main.insertBefore(alertDiv, main.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },

    /**
     * Format date
     */
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    /**
     * Format number with commas
     */
    formatNumber: function(num) {
        return num.toLocaleString();
    },

    /**
     * Debounce function
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// API functions
const api = {
    /**
     * Make API request
     */
    request: async function(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };

        // Add auth token if available
        if (authToken) {
            defaultOptions.headers['Authorization'] = `Bearer ${authToken}`;
        }

        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired or invalid
                    auth.logout();
                    throw new Error('Authentication required');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    /**
     * GET request
     */
    get: function(endpoint) {
        return this.request(endpoint);
    },

    /**
     * POST request
     */
    post: function(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * PUT request
     */
    put: function(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    /**
     * DELETE request
     */
    delete: function(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
};

// Authentication functions
const auth = {
    /**
     * Login user
     */
    login: async function(username, password) {
        try {
            utils.showLoading();
            
            const response = await api.post('/auth/login', {
                username: username,
                password: password
            });
            
            // Store token and user info
            authToken = response.access_token;
            localStorage.setItem('authToken', authToken);
            
            // Get user info
            await this.getCurrentUser();
            
            // Update UI
            this.updateUI();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            if (modal) {
                modal.hide();
            }
            
            utils.showAlert('Login successful!', 'success');
            
        } catch (error) {
            console.error('Login failed:', error);
            utils.showAlert('Login failed. Please check your credentials.', 'danger');
        } finally {
            utils.hideLoading();
        }
    },

    /**
     * Logout user
     */
    logout: function() {
        // Clear token and user info
        authToken = null;
        currentUser = null;
        localStorage.removeItem('authToken');
        
        // Update UI
        this.updateUI();
        
        // Redirect to home if not already there
        if (window.location.pathname !== '/') {
            window.location.href = '/';
        }
        
        utils.showAlert('Logged out successfully.', 'info');
    },

    /**
     * Get current user info
     */
    getCurrentUser: async function() {
        if (!authToken) return null;
        
        try {
            const user = await api.get('/auth/me');
            currentUser = user;
            return user;
        } catch (error) {
            console.error('Failed to get user info:', error);
            this.logout();
            return null;
        }
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated: function() {
        return authToken !== null;
    },

    /**
     * Check if user has admin role
     */
    isAdmin: function() {
        return currentUser && (currentUser.role === 'admin' || currentUser.role === 'developer');
    },

    /**
     * Check if user has developer role
     */
    isDeveloper: function() {
        return currentUser && currentUser.role === 'developer';
    },

    /**
     * Update UI based on authentication status
     */
    updateUI: function() {
        const loginNav = document.getElementById('login-nav');
        const userNav = document.getElementById('user-nav');
        const adminNav = document.getElementById('admin-nav');
        const developerNav = document.getElementById('developer-nav');
        const usernameSpan = document.getElementById('username');
        
        if (this.isAuthenticated() && currentUser) {
            // Show user nav, hide login nav
            if (loginNav) loginNav.style.display = 'none';
            if (userNav) userNav.style.display = 'block';
            if (usernameSpan) usernameSpan.textContent = currentUser.username;
            
            // Show admin nav if user is admin
            if (this.isAdmin() && adminNav) {
                adminNav.style.display = 'block';
            }
            
            // Show developer nav if user is developer
            if (this.isDeveloper() && developerNav) {
                developerNav.style.display = 'block';
            }
        } else {
            // Show login nav, hide user nav
            if (loginNav) loginNav.style.display = 'block';
            if (userNav) userNav.style.display = 'none';
            if (adminNav) adminNav.style.display = 'none';
            if (developerNav) developerNav.style.display = 'none';
        }
    }
};

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize authentication
    if (authToken) {
        auth.getCurrentUser().then(() => {
            auth.updateUI();
        });
    }
    
    // Login form handler
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    
    if (loginBtn) {
        loginBtn.addEventListener('click', function() {
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
            if (!username || !password) {
                utils.showAlert('Please enter both username and password.', 'warning');
                return;
            }
            
            auth.login(username, password);
        });
    }
    
    // Logout button handler
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            auth.logout();
        });
    }
    
    // Login form enter key handler
    if (loginForm) {
        loginForm.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                loginBtn.click();
            }
        });
    }
    
    // Clear login form when modal is hidden
    const loginModal = document.getElementById('loginModal');
    if (loginModal) {
        loginModal.addEventListener('hidden.bs.modal', function() {
            const errorDiv = document.getElementById('loginError');
            if (errorDiv) {
                errorDiv.style.display = 'none';
                errorDiv.textContent = '';
            }
        });
    }
});

// Export for use in other scripts
window.ADCC = {
    api: api,
    auth: auth,
    utils: utils
}; 