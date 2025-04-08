/**
 * Company Detail Page JavaScript
 * Handles activities loading and DataTables initialization
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize DataTables for company contacts
    if ($.fn.DataTable && document.getElementById('company-contacts-table')) {
        $('#company-contacts-table').DataTable({
            responsive: true,
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search contacts..."
            },
            columnDefs: [
                { orderable: false, targets: -1 } // Disable sorting on actions column
            ]
        });
    }

    // Handle activities tab loading
    setupActivitiesTabLoading();
});

/**
 * Sets up event listeners for loading activities when the tab is shown
 */
function setupActivitiesTabLoading() {
    const activitiesTab = document.getElementById('activities-tab');
    
    if (activitiesTab) {
        // Use both event binding methods for better cross-browser support
        activitiesTab.addEventListener('shown.bs.tab', function() {
            loadActivitiesByType('all');
        });
        
        // jQuery event binding as fallback
        $(document).ready(function() {
            $('#activities-tab').on('shown.bs.tab', function() {
                setTimeout(function() {
                    loadActivitiesByType('all');
                }, 200);
            });
        });
        
        // If URL has #activities hash, load activities immediately
        if (window.location.hash === '#activities') {
            setTimeout(function() {
                loadActivitiesByType('all');
            }, 500);
        }
    }
}

/**
 * Loads activities of specified type for the current company
 * @param {string} type - Type of activities to load (all, email, call, etc.)
 */
function loadActivitiesByType(type) {
    const companyId = document.getElementById('company_id').value;
    const activityContainer = document.getElementById(`${type}-activities-list`);
    
    if (!companyId || !activityContainer) return;
    
    // Show loading indicator
    activityContainer.innerHTML = '<div class="text-center p-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading activities...</p></div>';
    
    // Build URL with cache-busting
    const url = `/crm/company/${companyId}/activities/?type=${type}&_=${new Date().getTime()}`;
    
    // Fetch activities
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            activityContainer.innerHTML = html;
            
            // Initialize any UI components in the loaded content
            initializeActivityUI();
        })
        .catch(error => {
            activityContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error loading activities: ${error.message}
                </div>`;
        });
}

/**
 * Initializes UI components for loaded activity content
 */
function initializeActivityUI() {
    // Initialize tooltips, popovers, or other UI components
    // that might be in the dynamically loaded content
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
    
    // Add event listeners to activity detail links
    document.querySelectorAll('.view-activity-details').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const activityId = this.getAttribute('data-activity-id');
            showActivityDetails(activityId);
        });
    });
}

/**
 * Shows activity details in modal
 * @param {string} activityId - ID of the activity to show
 */
function showActivityDetails(activityId) {
    const modal = document.getElementById('activity-details-modal');
    
    if (modal) {
        // Hide all activity details
        document.querySelectorAll('.activity-detail-section').forEach(section => {
            section.style.display = 'none';
        });
        
        // Show selected activity details
        const selectedSection = document.getElementById(`activity-${activityId}-details`);
        if (selectedSection) {
            selectedSection.style.display = 'block';
            document.getElementById('no-activity-selected').style.display = 'none';
        } else {
            document.getElementById('no-activity-selected').style.display = 'block';
        }
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
} 