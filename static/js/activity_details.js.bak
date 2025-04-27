// Activity Details Module - VERSION 8 (Side Panel Implementation)
document.addEventListener('DOMContentLoaded', function() {
    console.log('Activity details module loaded - VERSION 8 (Side Panel)'); 
    
    // Get side panel elements
    const activitySidePanel = document.getElementById('activity-side-panel');
    const activityPanelTitle = document.getElementById('activitySidePanelLabel');
    const activityPanelLoading = document.getElementById('activity-panel-loading');
    const activityPanelFormContainer = document.getElementById('activity-panel-form-container');
    
    // Check if Bootstrap's Offcanvas is available for the side panel
    let sidePanelInstance = null;
    if (activitySidePanel) {
        sidePanelInstance = new bootstrap.Offcanvas(activitySidePanel);
        
        // Add event listener for when panel is hidden to clean up backdrop
        activitySidePanel.addEventListener('hidden.bs.offcanvas', function() {
            // Clean up any leftover backdrop elements
            const backdrop = document.querySelector('.offcanvas-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
            
            // Reset body classes and styles
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        });
    }
    
    // Use event delegation to handle clicks on activity items that are loaded dynamically
    document.addEventListener('click', function(e) {
        // Find the closest activity list item ancestor of the clicked element
        const activityItem = e.target.closest('.activity-list .list-group-item');
        if (!activityItem) return; // Not clicking on an activity item
        
        const activityId = activityItem.getAttribute('data-activity-id');
        console.log('Activity item clicked via delegation:', activityId);
        
        // Only prevent default if we're handling the click
        e.preventDefault();
        
        // Load activity details into side panel
        loadActivityDetailsIntoPanel(activityId);
    });
    
    // Function to load activity details into side panel
    function loadActivityDetailsIntoPanel(activityId) {
        if (!sidePanelInstance) {
            console.error('Side panel instance not found');
            return;
        }
        
        // Change panel title
        if (activityPanelTitle) {
            activityPanelTitle.textContent = 'Activity Details';
        }
        
        // Show loading state, hide form container
        if (activityPanelLoading) {
            activityPanelLoading.style.display = 'block';
        }
        if (activityPanelFormContainer) {
            activityPanelFormContainer.style.display = 'none';
            activityPanelFormContainer.innerHTML = '';
        }
        
        // Show the panel
        sidePanelInstance.show();
        
        // Fetch activity details
        fetch(`/crm/activity/${activityId}/detail/sidepanel/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(html => {
                // Hide loading, show content
                if (activityPanelLoading) {
                    activityPanelLoading.style.display = 'none';
                }
                if (activityPanelFormContainer) {
                    activityPanelFormContainer.innerHTML = html;
                    activityPanelFormContainer.style.display = 'block';
                }
                
                // Bind event handlers for edit/delete buttons
                bindDetailPanelEventHandlers();
            })
            .catch(error => {
                console.error('Error loading activity details:', error);
                if (activityPanelLoading) {
                    activityPanelLoading.style.display = 'none';
                }
                if (activityPanelFormContainer) {
                    activityPanelFormContainer.innerHTML = '<div class="alert alert-danger">Error loading activity details. Please try again.</div>';
                    activityPanelFormContainer.style.display = 'block';
                }
            });
    }
    
    // Function to bind event handlers within the loaded details
    function bindDetailPanelEventHandlers() {
        // Edit button - opens the edit form in the same panel
        const editButtons = document.querySelectorAll('.edit-activity-btn');
        editButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const activityId = this.getAttribute('data-activity-id');
                
                // Update panel title
                if (activityPanelTitle) {
                    activityPanelTitle.textContent = 'Edit Activity';
                }
                
                // Show loading, hide content
                if (activityPanelLoading) {
                    activityPanelLoading.style.display = 'block';
                }
                if (activityPanelFormContainer) {
                    activityPanelFormContainer.style.display = 'none';
                }
                
                // Load edit form
                fetch(`/crm/activity/${activityId}/edit/sidepanel/`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.text();
                    })
                    .then(html => {
                        // Hide loading, show form
                        if (activityPanelLoading) {
                            activityPanelLoading.style.display = 'none';
                        }
                        if (activityPanelFormContainer) {
                            activityPanelFormContainer.innerHTML = html;
                            activityPanelFormContainer.style.display = 'block';
                        }
                    })
                    .catch(error => {
                        console.error('Error loading edit form:', error);
                        if (activityPanelLoading) {
                            activityPanelLoading.style.display = 'none';
                        }
                        if (activityPanelFormContainer) {
                            activityPanelFormContainer.innerHTML = '<div class="alert alert-danger">Error loading edit form. Please try again.</div>';
                            activityPanelFormContainer.style.display = 'block';
                        }
                    });
            });
        });
        
        // Delete button
        const deleteButtons = document.querySelectorAll('.delete-activity-btn');
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const activityId = this.getAttribute('data-activity-id');
                if (confirm('Are you sure you want to delete this activity? This action cannot be undone.')) {
                    fetch(`/crm/activity/${activityId}/delete/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCsrfToken(),
                            'Content-Type': 'application/json'
                        }
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            // Close panel and refresh activity list
                            sidePanelInstance.hide();
                            
                            // Refresh the activities list if available
                            if (typeof refreshActivitiesList === 'function') {
                                refreshActivitiesList();
                            } else {
                                // Fallback to page reload
                                window.location.reload();
                            }
                        } else {
                            alert('Error deleting activity: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting activity:', error);
                        alert('Error deleting activity. Please try again.');
                    });
                }
            });
        });
    }
    
    // Helper function to get CSRF token
    function getCsrfToken() {
        return document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    }
    
    // Attach click event to activity links/buttons that should open the side panel
    function attachActivityDetailClickHandlers() {
        const activityDetailLinks = document.querySelectorAll('.activity-detail-link');
        activityDetailLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const activityId = this.getAttribute('data-activity-id');
                loadActivityDetailsIntoPanel(activityId);
            });
        });
    }
    
    // Initialize event handlers
    attachActivityDetailClickHandlers();
    
    // Expose functions globally for other components
    window.loadActivityDetailsIntoPanel = loadActivityDetailsIntoPanel;
    window.attachActivityDetailClickHandlers = attachActivityDetailClickHandlers;
});

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