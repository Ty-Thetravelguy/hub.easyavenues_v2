// Activity Details Module
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the activity details modal functionality
    initActivityDetailsModal();
});

/**
 * Initialize activity details modal
 */
function initActivityDetailsModal() {
    // Get the modal element
    const modal = document.getElementById('activityDetailModal');
    if (!modal) return;
    
    // Add event listener for when the modal is shown
    modal.addEventListener('show.bs.modal', function(event) {
        // Get the activity ID from the clicked element
        const button = event.relatedTarget;
        const activityId = button.getAttribute('data-activity-id');
        
        if (activityId) {
            // Show loading indicator
            document.getElementById('activity-detail-loading').style.display = 'block';
            document.getElementById('activity-detail-content').style.display = 'none';
            
            // Fetch the activity details
            fetchActivityDetails(activityId);
        }
    });
}

/**
 * Fetch activity details from the server
 * @param {string} activityId - The ID of the activity to fetch
 */
function fetchActivityDetails(activityId) {
    fetch(`/crm/activity/${activityId}/details/json/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator and show content
            document.getElementById('activity-detail-loading').style.display = 'none';
            const contentElement = document.getElementById('activity-detail-content');
            contentElement.style.display = 'block';
            
            // Display activity details
            if (data.status === 'success') {
                renderActivityDetails(data.data);
            } else {
                contentElement.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        ${data.message || 'Error loading activity details'}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching activity details:', error);
            
            // Hide loading indicator and show error
            document.getElementById('activity-detail-loading').style.display = 'none';
            document.getElementById('activity-detail-content').style.display = 'block';
            document.getElementById('activity-detail-content').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error loading activity details: ${error.message}
                </div>
            `;
        });
}

/**
 * Render activity details in the modal
 * @param {Object} activity - The activity data from the server
 */
function renderActivityDetails(activity) {
    const contentElement = document.getElementById('activity-detail-content');
    
    // Set the modal title based on whether it's a system or manual activity
    const modalTitle = document.getElementById('activityDetailModalLabel');
    if (modalTitle) {
        if (activity.is_system_activity) {
            modalTitle.innerHTML = `<i class="fas fa-cog me-2"></i> System Activity`;
        } else {
            modalTitle.innerHTML = `<i class="fas fa-clipboard-list me-2"></i> ${getActivityTypeDisplay(activity.type)}`;
        }
    }
    
    // Build the activity details HTML
    let detailsHTML = '';
    
    // Add specific content based on activity type
    if (activity.is_system_activity) {
        // For system activities, focus on the description which contains the changes
        detailsHTML += `
            <div class="card mb-3">
                <div class="card-header bg-light">
                    <strong>System Update</strong>
                </div>
                <div class="card-body">
                    <p class="card-text">${formatSystemActivityDescription(activity.description)}</p>
                </div>
            </div>
        `;
    } else {
        // Add type-specific fields for manual activities
        detailsHTML += renderManualActivityDetails(activity);
    }
    
    // Add common metadata for all activity types
    detailsHTML += `
        <div class="card mb-3">
            <div class="card-header bg-light">
                <strong>Activity Details</strong>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Date & Time:</strong> ${formatDateTime(activity.performed_at)}</p>
                        <p><strong>Type:</strong> ${getActivityTypeDisplay(activity.type)}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Performed By:</strong> ${activity.performed_by?.name || 'System'}</p>
                        <p><strong>Company:</strong> ${activity.company?.name || 'N/A'}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    contentElement.innerHTML = detailsHTML;
}

/**
 * Format a system activity description with proper formatting for change lists
 * @param {string} description - The system activity description
 * @returns {string} HTML-formatted description
 */
function formatSystemActivityDescription(description) {
    if (!description) return 'No description available';
    
    // Check if the description has bullet points (changes)
    if (description.includes('•')) {
        // Split by newlines and format as a list
        const parts = description.split('\n');
        let formattedDesc = '';
        
        // The first line is the main description
        if (parts.length > 0) {
            formattedDesc = `<p>${parts[0]}</p>`;
        }
        
        // The rest are changes
        if (parts.length > 1) {
            formattedDesc += '<ul class="mb-0">';
            for (let i = 1; i < parts.length; i++) {
                if (parts[i].trim()) {
                    formattedDesc += `<li>${parts[i].trim().replace('• ', '')}</li>`;
                }
            }
            formattedDesc += '</ul>';
        }
        
        return formattedDesc;
    }
    
    // If no bullet points, just return the formatted description
    return description.replace(/\n/g, '<br>');
}

/**
 * Render manual activity details based on activity type
 * @param {Object} activity - The activity data from the server
 * @returns {string} HTML content for manual activity details
 */
function renderManualActivityDetails(activity) {
    let detailsHTML = '';
    
    switch (activity.type) {
        case 'email':
            detailsHTML += `
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <strong>Email Details</strong>
                    </div>
                    <div class="card-body">
                        <p><strong>Subject:</strong> ${activity.subject || 'N/A'}</p>
                        <p><strong>Recipients:</strong> ${activity.recipients || 'N/A'}</p>
                        <div class="mt-3">
                            <strong>Content:</strong>
                            <div class="p-3 bg-light rounded mt-2">${activity.body || activity.description || 'No content'}</div>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'call':
            detailsHTML += `
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <strong>Call Details</strong>
                    </div>
                    <div class="card-body">
                        <p><strong>Contact:</strong> ${activity.contact_name || 'N/A'}</p>
                        <p><strong>Duration:</strong> ${activity.duration || 'N/A'}</p>
                        <div class="mt-3">
                            <strong>Summary:</strong>
                            <div class="p-3 bg-light rounded mt-2">${activity.summary || activity.description || 'No summary'}</div>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'meeting':
            detailsHTML += `
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <strong>Meeting Details</strong>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Date:</strong> ${activity.meeting_date || 'N/A'}</p>
                                <p><strong>Time:</strong> ${activity.start_time || 'N/A'} - ${activity.end_time || 'N/A'}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Location:</strong> ${activity.location || 'N/A'}</p>
                                <p><strong>Attendees:</strong> ${activity.attendees || 'N/A'}</p>
                            </div>
                        </div>
                        <div class="mt-3">
                            <strong>Notes:</strong>
                            <div class="p-3 bg-light rounded mt-2">${activity.notes || activity.description || 'No notes'}</div>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'note':
            detailsHTML += `
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <strong>Note Details</strong>
                    </div>
                    <div class="card-body">
                        <div class="p-3 bg-light rounded">${activity.content || activity.description || 'No content'}</div>
                    </div>
                </div>
            `;
            break;
            
        case 'waiver_favour':
            detailsHTML += `
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <strong>Waiver & Favour Details</strong>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Type:</strong> ${activity.waiver_type || 'N/A'}</p>
                                <p><strong>Value:</strong> ${activity.value_amount ? '£' + activity.value_amount : 'N/A'}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Contact:</strong> ${activity.contact_name || 'N/A'}</p>
                                <p><strong>Approved By:</strong> ${activity.approved_by || 'N/A'}</p>
                            </div>
                        </div>
                        <div class="mt-3">
                            <strong>Reason:</strong>
                            <div class="p-3 bg-light rounded mt-2">${activity.reason || activity.description || 'No reason provided'}</div>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'task':
            detailsHTML += `
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <strong>Task Details</strong>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Title:</strong> ${activity.title || 'N/A'}</p>
                                <p><strong>Status:</strong> ${activity.status || 'N/A'}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Due Date:</strong> ${activity.due_date || 'N/A'}</p>
                                <p><strong>Priority:</strong> ${activity.priority || 'N/A'}</p>
                            </div>
                        </div>
                        <div class="mt-3">
                            <strong>Description:</strong>
                            <div class="p-3 bg-light rounded mt-2">${activity.description || 'No description'}</div>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        default:
            detailsHTML += `
                <div class="card mb-3">
                    <div class="card-header bg-light">
                        <strong>Activity Details</strong>
                    </div>
                    <div class="card-body">
                        <div class="p-3 bg-light rounded">${activity.description || 'No details available'}</div>
                    </div>
                </div>
            `;
    }
    
    return detailsHTML;
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