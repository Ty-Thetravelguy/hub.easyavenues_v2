// Activity Details Module
document.addEventListener('DOMContentLoaded', function() {
    console.log('Activity details module loaded - VERSION 7'); // Version marker to confirm new code is loaded
    
    // Add special handling for modal close button clicks
    document.addEventListener('click', function(e) {
        // Check if the clicked element is a modal close button
        if (e.target.closest('.modal .btn-close') || 
            (e.target.closest('.modal .btn-secondary') && 
             e.target.closest('.modal-footer'))) {
            
            console.log('Modal close button clicked - managing focus');
            
            // Prevent default button behavior
            e.preventDefault();
            
            // First move focus outside the modal
            document.querySelector('body').setAttribute('tabindex', '-1');
            document.querySelector('body').focus();
            
            // Then close the modal after a tiny delay to ensure focus has moved
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('activityDetailModal'));
                if (modal) {
                    modal.hide();
                }
            }, 10);
        }
    });
    
    // Add focus management for modal events
    const activityModal = document.getElementById('activityDetailModal');
    if (activityModal) {
        // When modal is about to be hidden
        activityModal.addEventListener('hide.bs.modal', function(event) {
            console.log('Modal hide event - fixing focus management');
            
            // Ensure no element inside the modal has focus
            const activeElement = document.activeElement;
            if (this.contains(activeElement)) {
                // Move focus to body
                document.body.setAttribute('tabindex', '-1');
                document.body.focus();
            }
        });
        
        // After modal is hidden
        activityModal.addEventListener('hidden.bs.modal', function(event) {
            console.log('Modal hidden completely');
            // Remove the tabindex from body when done
            document.body.removeAttribute('tabindex');
        });
    }
    
    // Use event delegation to handle clicks on activity items that are loaded dynamically
    document.addEventListener('click', function(e) {
        // Find the closest activity list item ancestor of the clicked element
        const activityItem = e.target.closest('.activity-list .list-group-item');
        if (!activityItem) return; // Not clicking on an activity item
        
        const activityId = activityItem.getAttribute('data-activity-id');
        console.log('Activity item clicked via delegation:', activityId);
        
        // Show modal manually
        const modal = document.getElementById('activityDetailModal');
        if (!modal) {
            console.error('Modal element not found');
            return;
        }
            
        // Only prevent default if we're handling the click
        e.preventDefault();
        
        console.log('Opening modal for activity:', activityId);
        
        // Let Bootstrap handle the modal
        const bsModal = bootstrap.Modal.getInstance(modal) || new bootstrap.Modal(modal);
        
        // Show loading indicator
        const loadingElement = document.getElementById('activity-detail-loading');
        const contentElement = document.getElementById('activity-detail-content');
        
        if (loadingElement) loadingElement.style.display = 'block';
        if (contentElement) {
            contentElement.style.display = 'none';
            // Clear previous content to avoid confusion
            contentElement.innerHTML = '';
        }
        
        // Fetch activity details
        fetchActivityDetailsSimple(activityId);
        
        // Show the modal
        bsModal.show();
    });
});

/**
 * Simplified version of fetch function to directly get activity details
 */
function fetchActivityDetailsSimple(activityId) {
    if (!activityId) {
        console.error('No activity ID provided');
        return;
    }
    
    console.log('Fetching activity details for ID:', activityId);
    
    // Use the URL pattern from urls.py
    const url = `/crm/activity/${activityId}/details/`;
    
    fetch(url)
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            console.log('Received HTML, length:', html.length);
            
            // Update modal content
            const contentElement = document.getElementById('activity-detail-content');
            const loadingElement = document.getElementById('activity-detail-loading');
            
            if (loadingElement) loadingElement.style.display = 'none';
            if (contentElement) {
                contentElement.style.display = 'block';
                contentElement.innerHTML = html;
                
                // Set up any delete buttons or other interactive elements
                setupDeleteButtonListeners();
            }
        })
        .catch(error => {
            console.error('Error fetching activity details:', error);
            
            // Show error in modal
            const contentElement = document.getElementById('activity-detail-content');
            const loadingElement = document.getElementById('activity-detail-loading');
            
            if (loadingElement) loadingElement.style.display = 'none';
            if (contentElement) {
                contentElement.style.display = 'block';
                contentElement.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error loading activity details: ${error.message}
                    </div>
                `;
            }
        });
}

/**
 * Get the display name for an activity type
 * @param {string} type - The activity type code
 * @returns {string} The display name for the activity type
 */
function getActivityTypeDisplay(type) {
    const typeMap = {
        'email': 'Email',
        'call': 'Call',
        'meeting': 'Meeting',
        'note': 'Note',
        'waiver_favour': 'Waiver & Favour',
        'task': 'Task',
        'document': 'Document',
        'status_change': 'Status Change',
        'policy_update': 'Policy Update',
        'update': 'Update'
    };
    
    return typeMap[type] || 'Activity';
}

/**
 * Format an ISO datetime string to a friendly format
 * @param {string} isoString - The ISO datetime string
 * @returns {string} Formatted date and time
 */
function formatDateTime(isoString) {
    if (!isoString) return 'N/A';
    
    const date = new Date(isoString);
    return date.toLocaleString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Keep the original functions for compatibility
function initActivityDetailsModal() {
    console.log('Original initActivityDetailsModal called - this is no longer used');
}

function fetchActivityDetails(activityId) {
    console.log('Original fetchActivityDetails called with ID:', activityId);
    fetchActivityDetailsSimple(activityId);
}

function setupDeleteButtonListeners() {
    console.log('Setting up delete button listeners');
    const deleteButtons = document.querySelectorAll('.delete-activity-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const activityId = this.getAttribute('data-activity-id');
            
            if (confirm('Are you sure you want to delete this activity? This action cannot be undone.')) {
                // Redirect to the delete URL
                window.location.href = `/crm/activity/${activityId}/delete/`;
            }
        });
    });
} 