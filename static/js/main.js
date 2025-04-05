// Common utility functions and page initialization for Easy Avenues CRM
document.addEventListener('DOMContentLoaded', function () {
    console.log('🔄 Easy Avenues CRM - Initializing main.js');
    
    // Initialize alerts
    initializeAlerts();
    
    // Initialize datetime display
    initializeDateTimeDisplay();
    
    // Initialize bookmarks
    initializeBookmarks();
    
    // Initialize any tab handlers
    initializeTabHandlers();
});

// ======================================================
// Core utility functions
// ======================================================

/**
 * Get CSRF token from cookie or input field
 */
function getCsrfToken() {
    // Try to get token from cookie
    const csrfCookie = document.cookie
        .split(';')
        .map(cookie => cookie.trim())
        .find(cookie => cookie.startsWith('csrftoken='));
        
    if (csrfCookie) {
        return csrfCookie.split('=')[1];
    }
    
    // Fallback to getting it from the DOM
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return csrfInput ? csrfInput.value : '';
}

/**
 * Set up CSRF token for all AJAX requests
 */
function setupCsrfToken() {
    const csrftoken = getCsrfToken();
    
    // Set up jQuery AJAX defaults if jQuery is available
    if (typeof jQuery !== 'undefined') {
        jQuery.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }
}

/**
 * Show temporary message to user
 */
function showMessage(message, type = 'success') {
    const messageContainer = document.getElementById('message-container');
    if (messageContainer) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show shadow`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        messageContainer.appendChild(alertDiv);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }
}

/**
 * Format a date in a friendly format
 */
function formatDate(date) {
    if (!date) return '';
    
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    if (isNaN(date.getTime())) {
        return '';
    }
    
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    // Format for today and yesterday
    if (date.toDateString() === today.toDateString()) {
        return 'Today ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    } else {
        // Regular date format
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
}

// ======================================================
// Feature initialization functions
// ======================================================

/**
 * Initialize alerts that auto-dismiss
 */
function initializeAlerts() {
    setTimeout(function () {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            if (typeof bootstrap !== 'undefined') {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                alert.style.display = 'none';
            }
        });
    }, 3000);
}

/**
 * Initialize datetime display in header
 */
function initializeDateTimeDisplay() {
    const dateTimeElement = document.getElementById('current-datetime');
    
    if (!dateTimeElement) return;
    
    function updateDateTime() {
        const now = new Date();
        const months = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'];
        const day = now.getDate();
        const month = months[now.getMonth()];
        const year = now.getFullYear();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        dateTimeElement.textContent = `${day} ${month} ${year} - ${hours}:${minutes}`;
    }

    updateDateTime();
    setInterval(updateDateTime, 60000);
}

/**
 * Initialize bookmark functionality
 */
function initializeBookmarks() {
    // Function to refresh bookmark list
    function refreshBookmarkList() {
        const bookmarkersContent = document.getElementById('bookmarkersContent');
        if (!bookmarkersContent) return;

        fetch('/users/get-bookmarks/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            bookmarkersContent.innerHTML = html;
            // Reattach event listeners to new remove buttons
            document.querySelectorAll('.remove-bookmark').forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    handleRemoveBookmark(this);
                });
            });
        })
        .catch(error => {
            console.error('Error refreshing bookmarks:', error);
        });
    }

    // Handle bookmark button clicks
    const bookmarkButtons = document.querySelectorAll('.bookmark-btn');
    bookmarkButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.url;
            const icon = this.querySelector('i');
            const csrfToken = getCsrfToken();

            fetch('/users/toggle-bookmark/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `url=${encodeURIComponent(url)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'added') {
                    icon.classList.replace('far', 'fas');
                } else {
                    icon.classList.replace('fas', 'far');
                }
                
                // Show success message
                if (data.message) {
                    showMessage(data.message);
                }

                // Refresh the bookmark list
                refreshBookmarkList();
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error updating bookmark', 'danger');
            });
        });
    });

    // Add handler for existing remove buttons
    function handleRemoveBookmark(button) {
        const url = button.dataset.url;
        const bookmarkBtn = document.querySelector(`.bookmark-btn[data-url="${url}"]`);
        if (bookmarkBtn) {
            bookmarkBtn.click(); // Reuse the existing toggle functionality
        }
    }

    document.querySelectorAll('.remove-bookmark').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            handleRemoveBookmark(this);
        });
    });
}

/**
 * Initialize tab handling and persistence
 */
function initializeTabHandlers() {
    // Find all tab containers
    const tabContainers = document.querySelectorAll('[data-tab-container]');
    
    tabContainers.forEach(container => {
        const containerId = container.dataset.tabContainer;
        
        // Find all tabs in this container
        const tabs = container.querySelectorAll('[data-tab-target]');
        
        // Check if we have any active tabs in localStorage
        const activeTabId = localStorage.getItem(`activeTab_${containerId}`);
        
        if (activeTabId) {
            // Try to activate the saved tab
            const savedTab = container.querySelector(`[data-tab-target="${activeTabId}"]`);
            if (savedTab) {
                // Deactivate all tabs first
                tabs.forEach(tab => {
                    const targetId = tab.dataset.tabTarget;
                    const targetPane = document.getElementById(targetId);
                    
                    tab.classList.remove('active');
                    if (targetPane) {
                        targetPane.classList.remove('show', 'active');
                    }
                });
                
                // Activate the saved tab
                savedTab.classList.add('active');
                const targetPane = document.getElementById(activeTabId);
                if (targetPane) {
                    targetPane.classList.add('show', 'active');
                }
            }
        }
        
        // Add click handlers to tabs to save active tab
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const targetId = this.dataset.tabTarget;
                localStorage.setItem(`activeTab_${containerId}`, targetId);
                
                // Additional navigation code if needed
            });
        });
    });
}

// Set up CSRF token globally on load
setupCsrfToken();