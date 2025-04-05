// Consolidated activities functionality for Easy Avenues CRM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Easy Avenues CRM - Initializing activities.js');
    
    // Set up activity section buttons
    setupActivityButtons();
    
    // Set up activity card click handlers
    setupActivityCardHandlers();
    
    // Initialize activity details modal
    setupActivityDetailsModal();
    
    // Initialize activity filtering
    initializeActivityFiltering();
    
    // Initialize date/time pickers for activities
    initializeDateTimePickers();
    
    // Initialize To-do toggles
    initializeToDoToggles();
    
    // Initialize Select2 for recipient selectors
    initializeRecipientSelect();
});

// ======================================================
// Activity Section and Card Handlers
// ======================================================

/**
 * Setup buttons in the activity section
 */
function setupActivityButtons() {
    // Log activity button handler
    const logActivityButton = document.getElementById('log-activity-btn');
    if (logActivityButton) {
        logActivityButton.addEventListener('click', function() {
            const modal = document.getElementById('logActivityModal');
            if (modal) {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            }
        });
    }
    
    // Activity type card handlers (email, call, note, etc.)
    const activityTypeCards = document.querySelectorAll('.activity-type-card');
    activityTypeCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove active class from all cards
            activityTypeCards.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked card
            this.classList.add('active');
            
            // Get activity type
            const activityType = this.dataset.activityType;
            
            // Hide all forms
            document.querySelectorAll('.activity-form').forEach(form => {
                form.classList.add('d-none');
            });
            
            // Show selected form
            const selectedForm = document.getElementById(`${activityType}-form`);
            if (selectedForm) {
                selectedForm.classList.remove('d-none');
            }
        });
    });
}

/**
 * Set up activity card click handlers for expanding/collapsing
 */
function setupActivityCardHandlers() {
    const activityCards = document.querySelectorAll('.activity-card');
    
    activityCards.forEach(card => {
        // Find the toggle element within this card
        const toggle = card.querySelector('.activity-toggle');
        const content = card.querySelector('.activity-content');
        
        if (toggle && content) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Toggle the expand/collapse state
                const isExpanded = content.classList.contains('show');
                
                if (isExpanded) {
                    content.classList.remove('show');
                    toggle.innerHTML = '<i class="fas fa-chevron-down"></i>';
                } else {
                    content.classList.add('show');
                    toggle.innerHTML = '<i class="fas fa-chevron-up"></i>';
                }
            });
        }
    });
}

/**
 * Initialize date and time pickers
 */
function initializeDateTimePickers() {
    // Find all date inputs that need datepicker
    const dateInputs = document.querySelectorAll('input[data-datepicker]');
    
    if (dateInputs.length && typeof flatpickr !== 'undefined') {
        dateInputs.forEach(input => {
            flatpickr(input, {
                dateFormat: "Y-m-d",
                allowInput: true
            });
        });
    }
    
    // Find all time inputs that need timepicker
    const timeInputs = document.querySelectorAll('input[data-timepicker]');
    
    if (timeInputs.length && typeof flatpickr !== 'undefined') {
        timeInputs.forEach(input => {
            flatpickr(input, {
                enableTime: true,
                noCalendar: true,
                dateFormat: "H:i",
                time_24hr: true,
                allowInput: true
            });
        });
    }
}

// ======================================================
// Activity Details Modal
// ======================================================

/**
 * Set up activity details modal
 */
function setupActivityDetailsModal() {
    const modal = document.getElementById('activity-details-modal');
    if (!modal) return;
    
    // Track current activity data
    let currentActivityId = null;
    let currentActivityData = null;
    let currentActivityType = null;
    
    // Setup modal show event
    jQuery('#activity-details-modal').on('show.bs.modal', function(event) {
        const button = jQuery(event.relatedTarget);
        const activityId = button.data('activity-id');
        const activityType = button.data('activity-type');
        currentActivityId = activityId;
        currentActivityType = activityType;
        
        const modal = jQuery(this);
        
        // Set loading state
        modal.find('.modal-title').text(getActivityTypeTitle(activityType) + ' Details');
        modal.find('#activity-details-content').html(getLoadingHTML());
        
        // Fetch activity details
        fetchActivityDetails(activityId, modal);
    });
    
    // Setup edit button
    setupEditButton();
    
    // Setup delete button
    setupDeleteButton();
}

/**
 * Helper function to get activity type title
 */
function getActivityTypeTitle(type) {
    const titles = {
        'email': 'Email',
        'call': 'Call',
        'note': 'Note',
        'meeting': 'Meeting',
        'exception': 'Waiver/Favor'
    };
    return titles[type] || 'Activity';
}

/**
 * Get loading HTML for spinners
 */
function getLoadingHTML() {
    return `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">Loading activity details...</p>
        </div>
    `;
}

/**
 * Fetch activity details via AJAX
 */
function fetchActivityDetails(activityId, modal) {
    jQuery.ajax({
        url: '/crm/activity/' + activityId + '/details/',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            currentActivityData = data;
            const contentHtml = formatActivityDetails(currentActivityType, data);
            modal.find('#activity-details-content').html(contentHtml);
        },
        error: function(xhr, status, error) {
            modal.find('#activity-details-content').html(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Unable to load activity details.
                </div>
            `);
        }
    });
}

/**
 * Format activity details based on type
 */
function formatActivityDetails(activityType, data) {
    let contentHtml = '';
    
    // Format based on activity type
    if (activityType === 'email') {
        contentHtml = `
            <div class="mb-3">
                <strong>Subject:</strong> ${data.data.subject || 'N/A'}
            </div>
            <div class="mb-3">
                <strong>Recipients:</strong> ${data.data.recipient_names ? data.data.recipient_names.join(', ') : 'No recipients'}
            </div>
            <div class="mb-3">
                <strong>Message:</strong>
                <div class="p-3 bg-light rounded">${data.data.content || 'No content'}</div>
            </div>
        `;
    } else if (activityType === 'call') {
        contentHtml = `
            <div class="mb-3">
                <strong>Contact:</strong> ${data.data.contact_name || 'N/A'}
            </div>
            <div class="mb-3">
                <strong>Duration:</strong> ${data.data.duration ? data.data.duration + ' minutes' : 'N/A'}
            </div>
            <div class="mb-3">
                <strong>Summary:</strong>
                <div class="p-3 bg-light rounded">${data.data.summary || 'No summary'}</div>
            </div>
        `;
    } else if (activityType === 'note') {
        contentHtml = `
            <div class="mb-3">
                <strong>Note:</strong>
                <div class="p-3 bg-light rounded">${data.content || 'No content'}</div>
            </div>
        `;
    } else if (activityType === 'meeting') {
        contentHtml = `
            <div class="mb-3">
                <strong>Title:</strong> ${data.data.title || 'N/A'}
            </div>
            <div class="mb-3">
                <strong>Date:</strong> ${data.data.date || 'N/A'}
            </div>
            <div class="mb-3">
                <strong>Time:</strong> ${data.data.start_time || 'N/A'} - ${data.data.end_time || 'N/A'}
            </div>
            <div class="mb-3">
                <strong>Location:</strong> ${data.data.location || 'N/A'}
            </div>
            <div class="mb-3">
                <strong>Attendees:</strong> ${data.data.attendee_names ? data.data.attendee_names.join(', ') : 'None specified'}
            </div>
            <div class="mb-3">
                <strong>Notes:</strong>
                <div class="p-3 bg-light rounded">${data.data.notes || 'No notes'}</div>
            </div>
        `;
    } else if (activityType === 'exception') {
        contentHtml = `
            <div class="mb-3">
                <strong>Type:</strong> ${data.data.exception_type ? data.data.exception_type.replace('_', ' ').toUpperCase() : 'N/A'}
            </div>
            <div class="mb-3">
                <strong>Value:</strong> ${data.data.value_amount ? '£' + data.data.value_amount : 'N/A'}
            </div>
            <div class="mb-3">
                <strong>For Contact:</strong> ${data.data.contact_name || 'N/A'}
            </div>
            <div class="mb-3">
                <strong>Approved By:</strong> ${data.data.approved_by ? data.data.approved_by.replace('_', ' ').toUpperCase() : 'N/A'}
            </div>
            <div class="mb-3">
                <strong>Description:</strong>
                <div class="p-3 bg-light rounded">${data.data.description || 'No description'}</div>
            </div>
        `;
    }
    
    // Add meta information
    contentHtml += `
        <div class="mt-4 pt-3 border-top text-muted small">
            <div><i class="far fa-clock me-1"></i> ${data.performed_at}</div>
            <div><i class="far fa-user me-1"></i> ${data.performed_by}</div>
        </div>
    `;
    
    return contentHtml;
}

/**
 * Setup edit button on activity details modal
 */
function setupEditButton() {
    const editButton = document.getElementById('activity-edit-btn');
    if (!editButton) return;
    
    editButton.addEventListener('click', function() {
        // Code to handle edit functionality
        if (!currentActivityId) return;
        
        // Redirect to edit page or show edit form
        window.location.href = `/crm/activity/${currentActivityId}/edit/`;
    });
}

/**
 * Setup delete button on activity details modal
 */
function setupDeleteButton() {
    const deleteButton = document.getElementById('activity-delete-btn');
    if (!deleteButton) return;
    
    deleteButton.addEventListener('click', function() {
        if (!currentActivityId) return;
        
        if (confirm('Are you sure you want to delete this activity? This action cannot be undone.')) {
            // Send delete request
            jQuery.ajax({
                url: '/crm/activity/' + currentActivityId + '/delete/',
                type: 'POST',
                data: {
                    csrfmiddlewaretoken: getCsrfToken()
                },
                success: function(response) {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('activity-details-modal'));
                    if (modal) {
                        modal.hide();
                    }
                    
                    // Show success message
                    showMessage('Activity deleted successfully.');
                    
                    // Refresh activity list if on company detail page
                    if (window.location.pathname.includes('/company/')) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 500);
                    }
                },
                error: function() {
                    showMessage('Error deleting activity.', 'danger');
                }
            });
        }
    });
}

// ======================================================
// Activity Filtering
// ======================================================

/**
 * Initialize activity filtering
 */
function initializeActivityFiltering() {
    const filterForm = document.getElementById('activity-filter-form');
    if (!filterForm) return;
    
    // Add event listeners to form controls
    const typeFilters = document.querySelectorAll('input[name="activity_type"]');
    const dateFilter = document.getElementById('date-filter');
    
    // Add change event listeners
    typeFilters.forEach(filter => {
        filter.addEventListener('change', filterActivities);
    });
    
    if (dateFilter) {
        dateFilter.addEventListener('change', filterActivities);
    }
    
    // Initial filtering
    filterActivities();
}

/**
 * Filter activities based on selected filters
 */
function filterActivities() {
    const activities = document.querySelectorAll('.activity-item');
    if (!activities.length) return;
    
    // Get selected filters
    const selectedTypes = Array.from(
        document.querySelectorAll('input[name="activity_type"]:checked')
    ).map(input => input.value);
    
    const dateFilter = document.getElementById('date-filter');
    const dateValue = dateFilter ? dateFilter.value : 'all';
    
    let visibleCount = 0;
    
    // Filter activities
    activities.forEach(activity => {
        const activityType = activity.dataset.activityType;
        const activityDate = new Date(activity.dataset.activityDate);
        let typeMatch = selectedTypes.length === 0 || selectedTypes.includes(activityType);
        let dateMatch = true;
        
        // Apply date filtering
        if (dateValue === 'today') {
            const today = new Date();
            dateMatch = activityDate.toDateString() === today.toDateString();
        } else if (dateValue === 'week') {
            const today = new Date();
            const weekAgo = new Date();
            weekAgo.setDate(today.getDate() - 7);
            dateMatch = activityDate >= weekAgo;
        } else if (dateValue === 'month') {
            const today = new Date();
            const monthAgo = new Date();
            monthAgo.setMonth(today.getMonth() - 1);
            dateMatch = activityDate >= monthAgo;
        }
        
        // Show/hide based on filter match
        if (typeMatch && dateMatch) {
            activity.style.display = '';
            visibleCount++;
        } else {
            activity.style.display = 'none';
        }
    });
    
    // Show/hide empty state message
    const emptyState = document.getElementById('activities-empty-state');
    if (emptyState) {
        emptyState.style.display = visibleCount === 0 ? '' : 'none';
    }
}

// ======================================================
// To-Do functionality
// ======================================================

/**
 * Initialize To-Do toggles
 */
function initializeToDoToggles() {
    const todoToggles = document.querySelectorAll('.todo-complete-toggle');
    
    todoToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const todoId = this.dataset.todoId;
            const isComplete = this.checked;
            
            // Send AJAX request to update todo status
            jQuery.ajax({
                url: '/crm/todo/' + todoId + '/toggle/',
                type: 'POST',
                data: {
                    is_complete: isComplete,
                    csrfmiddlewaretoken: getCsrfToken()
                },
                success: function(response) {
                    // Update UI
                    const todoItem = document.querySelector(`.todo-item[data-todo-id="${todoId}"]`);
                    if (todoItem) {
                        if (isComplete) {
                            todoItem.classList.add('completed');
                        } else {
                            todoItem.classList.remove('completed');
                        }
                    }
                    
                    // Show success message
                    showMessage(response.message || 'To-do updated successfully.');
                },
                error: function() {
                    // Revert checkbox state on error
                    toggle.checked = !isComplete;
                    showMessage('Error updating to-do status.', 'danger');
                }
            });
        });
    });
}

// ======================================================
// Recipient selection and forms
// ======================================================

/**
 * Initialize recipient selection with Select2
 */
function initializeRecipientSelect() {
    // Only run if Select2 is available
    if (typeof jQuery === 'undefined' || typeof jQuery.fn.select2 === 'undefined') {
        console.error('❌ jQuery or Select2 not available');
        return;
    }
    
    // Initialize recipient selectors
    const recipientSelectors = document.querySelectorAll('.recipient-select');
    
    recipientSelectors.forEach(selector => {
        const companyId = selector.dataset.companyId || document.getElementById('company_id')?.value;
        
        if (!companyId) {
            console.warn('⚠️ No company ID found for recipient selector');
            return;
        }
        
        jQuery(selector).select2({
            placeholder: 'Search for contacts or users...',
            allowClear: true,
            width: '100%',
            ajax: {
                url: '/crm/api/search-recipients/',
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        term: params.term || '',
                        company_id: companyId
                    };
                },
                processResults: function(data) {
                    return {
                        results: data.results
                    };
                },
                cache: true
            },
            templateResult: formatRecipientResult,
            templateSelection: formatRecipientSelection
        });
    });
}

/**
 * Format recipient search result
 */
function formatRecipientResult(data) {
    if (data.loading) return data.text;
    
    const icon = data.type === 'contact' ? 'user-tie' : 'user';
    
    return jQuery(`
        <div class="select2-result-item">
            <i class="fas fa-${icon} me-2"></i>
            <span>${data.text}</span>
            <small class="text-muted ms-2">(${data.type})</small>
        </div>
    `);
}

/**
 * Format recipient selection
 */
function formatRecipientSelection(data) {
    return data.text || data.id;
}

/**
 * Insert text at cursor position or replace selection
 */
function insertText(elementId, text) {
    const textarea = document.getElementById(elementId);
    if (!textarea) return;
    
    const startPos = textarea.selectionStart;
    const endPos = textarea.selectionEnd;
    const scrollTop = textarea.scrollTop;
    
    textarea.value = textarea.value.substring(0, startPos) + text + textarea.value.substring(endPos, textarea.value.length);
    textarea.focus();
    textarea.selectionStart = startPos + text.length;
    textarea.selectionEnd = startPos + text.length;
    textarea.scrollTop = scrollTop;
}

/**
 * Get selected text from textarea
 */
function getSelectedText(textarea) {
    if (!textarea) return '';
    return textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
} 