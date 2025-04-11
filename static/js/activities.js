// Consolidated activities functionality for Easy Avenues CRM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Easy Avenues CRM - Initializing activities.js');
    
    // Initialize activity tabs
    initializeActivityTabs();
    
    // Set up activity card click handlers
    setupActivityCardHandlers();
    
    // Initialize activity filtering
    initializeActivityFiltering();
    
    // Initialize date/time pickers for activities
    initializeDateTimePickers();
    
    // Initialize To-do toggles
    initializeToDoToggles();
    
    // Directly load all activities when on a company page
    const companyIdField = document.getElementById('company_id');
    const activitiesTab = document.getElementById('activities');
    
    if (companyIdField && activitiesTab) {
        console.log('Company page detected, will load activities...');
        
        // Check if we're on the activities tab or another tab
        const activitiesTabLink = document.getElementById('activities-tab');
        
        // Initial load of all activities
        setTimeout(function() {
            console.log('Initial load of activities...');
            loadActivitiesByType('all');
            
            // Also preload other activity types
            const activityTypes = ['email', 'call', 'meeting', 'note', 'waiver', 'task'];
            for (const type of activityTypes) {
                setTimeout(() => loadActivitiesByType(type), 500);
            }
        }, 500);
        
        // Manual trigger for activities tab
        if (activitiesTabLink) {
            activitiesTabLink.addEventListener('click', function() {
                console.log('Activities tab clicked, loading all activities...');
                // Force reload activities after a small delay
                setTimeout(() => loadActivitiesByType('all'), 300);
            });
        }
    }
});

// ======================================================
// Activity Tabs and Side Panel
// ======================================================

/**
 * Initialize activity tabs
 */
function initializeActivityTabs() {
    // Log activity buttons for each type
    setupActivityTypeButtons();
    
    // Setup tab activation handlers to load data
    setupTabActivationHandlers();
}

/**
 * Setup activity type buttons
 */
function setupActivityTypeButtons() {
    // Email activity button
    const emailButton = document.getElementById('log-email-btn');
    if (emailButton) {
        emailButton.addEventListener('click', function() {
            openActivitySidePanel('email');
        });
    }
    
    // Call activity button
    const callButton = document.getElementById('log-call-btn');
    if (callButton) {
        callButton.addEventListener('click', function() {
            openActivitySidePanel('call');
        });
    }
    
    // Meeting activity button
    const meetingButton = document.getElementById('log-meeting-btn');
    if (meetingButton) {
        meetingButton.addEventListener('click', function() {
            openActivitySidePanel('meeting');
        });
    }
    
    // Note activity button
    const noteButton = document.getElementById('log-note-btn');
    if (noteButton) {
        noteButton.addEventListener('click', function() {
            openActivitySidePanel('note');
        });
    }
    
    // Waiver activity button
    const waiverButton = document.getElementById('log-waiver-btn');
    if (waiverButton) {
        waiverButton.addEventListener('click', function() {
            openActivitySidePanel('waiver');
        });
    }
    
    // Task activity button
    const taskButton = document.getElementById('log-task-btn');
    if (taskButton) {
        taskButton.addEventListener('click', function() {
            openActivitySidePanel('task');
        });
    }
}

/**
 * Setup tab activation handlers to load data
 */
function setupTabActivationHandlers() {
    // Listen for bootstrap tab show events
    const activityTabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    
    console.log(`Found ${activityTabs.length} tabs with data-bs-toggle="tab"`);
    
    activityTabs.forEach(tab => {
        const tabTarget = tab.getAttribute('href');
        console.log(`Tab target: ${tabTarget}`);
        
        tab.addEventListener('shown.bs.tab', function(event) {
            const tabId = event.target.getAttribute('href');
            console.log(`Tab activated: ${tabId}`);
            
            // Load data based on which tab was activated
            if (tabId === '#email-activities') {
                console.log('Loading email activities...');
                loadActivitiesByType('email');
            } else if (tabId === '#call-activities') {
                console.log('Loading call activities...');
                loadActivitiesByType('call');
            } else if (tabId === '#meeting-activities') {
                console.log('Loading meeting activities...');
                loadActivitiesByType('meeting');
            } else if (tabId === '#note-activities') {
                console.log('Loading note activities...');
                loadActivitiesByType('note');
            } else if (tabId === '#waiver-activities') {
                console.log('Loading waiver activities...');
                loadActivitiesByType('waiver');
            } else if (tabId === '#task-activities') {
                console.log('Loading task activities...');
                loadActivitiesByType('task');
            } else if (tabId === '#activity-overview') {
                console.log('Loading all activities...');
                loadActivitiesByType('all');
            } else if (tabId === '#activities') {
                console.log('Activities main tab activated, loading all activities...');
                loadActivitiesByType('all');
            }
        });
    });
    
    // Also check for direct navigation to the activities tab
    if (window.location.hash === '#activities') {
        console.log('Direct navigation to #activities detected');
        setTimeout(() => loadActivitiesByType('all'), 500);
    }
}

/**
 * Open activity side panel
 */
function openActivitySidePanel(activityType) {
    // Get the side panel element
    const sidePanel = document.getElementById('activity-side-panel');
    if (!sidePanel) {
        console.error('Activity side panel not found');
        return;
    }
    
    // Update panel title and appearance
    updateSidePanelHeader(activityType);
    
    // Show loading state
    const loadingElement = document.getElementById('activity-panel-loading');
    const formContainer = document.getElementById('activity-panel-form-container');
    
    if (loadingElement && formContainer) {
        loadingElement.style.display = 'block';
        formContainer.style.display = 'none';
    }
    
    // Initialize Bootstrap offcanvas and show
    const offcanvas = new bootstrap.Offcanvas(sidePanel);
    offcanvas.show();
    
    // Load the appropriate form
    loadActivityForm(activityType);
}

/**
 * Update side panel header based on activity type
 */
function updateSidePanelHeader(activityType) {
    const panelTitle = document.getElementById('activitySidePanelLabel');
    if (!panelTitle) return;
    
    // Set title based on activity type
    const titleMap = {
        'email': 'Log Email',
        'call': 'Log Call',
        'meeting': 'Log Meeting',
        'note': 'Log Note',
        'waiver': 'Log Waiver/Favor',
        'task': 'Log Task'
    };
    
    const iconMap = {
        'email': 'envelope',
        'call': 'phone-alt',
        'meeting': 'users',
        'note': 'sticky-note',
        'waiver': 'exclamation-triangle',
        'task': 'tasks'
    };
    
    // Update title with icon
    panelTitle.innerHTML = `<i class="fas fa-${iconMap[activityType] || 'file-alt'} me-2"></i> ${titleMap[activityType] || 'Log Activity'}`;
    
    // Add appropriate class for styling
    panelTitle.className = 'offcanvas-title activity-header-' + activityType;
}

/**
 * Load activity form into side panel
 */
function loadActivityForm(activityType) {
    const formContainer = document.getElementById('activity-panel-form-container');
    const loadingElement = document.getElementById('activity-panel-loading');
    
    if (!formContainer) return;
    
    // Get company ID
    const companyIdField = document.getElementById('company_id');
    const companyId = companyIdField ? companyIdField.value : null;
    
    if (!companyId) {
        console.error('No company ID found');
        formContainer.innerHTML = '<div class="alert alert-danger">Error: Company ID not found</div>';
        if (loadingElement) loadingElement.style.display = 'none';
        formContainer.style.display = 'block';
        return;
    }
    
    // Build URL for the form
    const url = `/crm/activity/${activityType}/form/?company_id=${companyId}`;
    
    // Fetch the form via AJAX
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            // Hide loading, show form
            if (loadingElement) loadingElement.style.display = 'none';
            formContainer.innerHTML = html;
            formContainer.style.display = 'block';
            
            console.log(`🏁 Form HTML loaded for ${activityType}. Initializing elements...`);
            // Initialize form elements
            initializeFormElements(activityType);
        })
        .catch(error => {
            console.error('Error loading form:', error);
            formContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error loading form: ${error.message}
                </div>
            `;
            if (loadingElement) loadingElement.style.display = 'none';
            formContainer.style.display = 'block';
        });
}

/**
 * Initialize form elements after loading
 */
function initializeFormElements(activityType) {
    const formContainer = document.getElementById('activity-panel-form-container');
    if (!formContainer) {
        console.error('Form container not found for initialization');
        return;
    }

    const form = formContainer.querySelector('form');
    if (form) {
        form.classList.add('activity-form', `${activityType}-form`);
        
        // Initialize common elements
        initializeDateTimePickers(form);
        
        // Initialize type-specific elements
        if (activityType === 'email') {
            initializeRecipientSelectForForm(form); // Uses #email_recipients (multi-select)
            initializeTinyMCEForForm(form);
            setupFollowUpTaskToggle(form);
        } else if (activityType === 'call') {
            initializeCallContactSelect(form); // Uses #call_contact (single-select)
            setupFollowUpTaskToggle(form);
        } else if (activityType === 'meeting') {
            // Use the same multi-select init function as email, just target a different ID
            initializeRecipientSelectForForm(form, '#meeting_attendees'); 
            setupFollowUpTaskToggle(form);
        } else if (activityType === 'note') {
            setupFollowUpTaskToggle(form); // Initialize follow-up toggle for notes
        }
        // Add other else if blocks for other activity types if needed
        
        // Add submit handler
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitActivityForm(form, activityType);
        });
    } else {
        console.error('Form element not found inside container');
    }
}

/**
 * Sets up the toggle for showing/hiding follow-up task details in a form
 */
function setupFollowUpTaskToggle(formElement) {
    const checkbox = formElement.querySelector('#create_follow_up_task');
    const detailsDiv = formElement.querySelector('#follow_up_task_details');

    if (checkbox && detailsDiv) {
        console.log('Setting up follow-up task toggle listener.');
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                detailsDiv.style.display = 'block';
                console.log('Follow-up task details shown.');
            } else {
                detailsDiv.style.display = 'none';
                console.log('Follow-up task details hidden.');
            }
        });
    } else {
        console.warn('Could not find follow-up task checkbox or details div for toggle setup.');
    }
}

/**
 * Initialize recipient/attendee selection with Tom Select for a specific form
 * @param {HTMLElement} formElement - The form containing the select.
 * @param {string} [selectorId='#email_recipients'] - The ID of the select element.
 */
function initializeRecipientSelectForForm(formElement, selectorId = '#email_recipients') {
    // Only run if Tom Select is available
    if (typeof TomSelect === 'undefined') {
        console.error('❌ Tom Select not available');
        return;
    }

    const selector = formElement.querySelector(selectorId);
    if (!selector) {
        console.warn(`⚠️ Recipient/Attendee selector (${selectorId}) not found in the form.`);
        return;
    }
    
    // Get company ID from the form's hidden input or data attribute
    const companyId = formElement.querySelector('input[name="company_id"]')?.value || 
                      selector.dataset.companyId;
    
    if (!companyId) {
        console.warn(`⚠️ No company ID found for selector ${selectorId} in the form`);
        return;
    }
    
    // Prevent re-initialization
    if (selector.tomselect) {
        console.log(`Tom Select already initialized for ${selectorId}.`);
        return;
    }
    
    // Initialize Tom Select
    const tomSelectInstance = new TomSelect(selector, {
        plugins: ['remove_button'],
        maxItems: null, // Allow multiple items
        valueField: 'id',
        labelField: 'text',
        searchField: ['text', 'email'], 
        create: false,
        placeholder: 'Type to search for contacts or users...',
        load: function(query, callback) {
             if (!query.length || query.length < 2) return callback();
            this.loading = true;
            const url = '/crm/api/search-recipients/';
            const params = new URLSearchParams({ q: query, company_id: companyId });
            fetch(`${url}?${params.toString()}`)
                .then(response => response.json())
                .then(json => {
                    this.loading = false;
                    if (json.results) {
                        callback(json.results);
                    } else {
                        console.error('Invalid JSON response from server', json);
                        callback();
                    }
                })
                .catch(error => {
                    console.error(`Error fetching recipients/attendees for ${selectorId}:`, error);
                    this.loading = false;
                    callback();
                });
        },
        render: {
             option: function(data, escape) {
                const icon = data.type === 'contact' ? 'user-tie' : 'user';
                const email = data.email ? `<small class="text-muted ms-2">(${escape(data.email)})</small>` : '';
                return `<div class="tom-select-result d-flex align-items-center">
                         <i class="fas fa-${icon} me-2"></i>
                         <div>
                           <span>${escape(data.text)}</span>
                           ${email}
                         </div>
                       </div>`;
            },
            item: function(data, escape) {
                const icon = data.type === 'contact' ? 'user-tie' : 'user';
                 return `<div class="d-flex align-items-center">
                         <i class="fas fa-${icon} me-2"></i>
                         <span>${escape(data.text)}</span>
                       </div>`;
            },
            no_results: function(data, escape) {
                return '<div class="no-results p-2">No results found for "' + escape(data.input) + '"</div>';
            }
        },
        onItemAdd: (value, $item) => { 
            console.log(`✅ onItemAdd triggered! Value: ${value} for ${selectorId}`);
            try {
                const wrapper = selector.tomselect?.wrapper;
                const controlInput = wrapper?.querySelector('.ts-control input');
                if (controlInput) {
                    controlInput.value = '';
                    console.log(`   Control input value cleared directly via DOM traversal for ${selectorId}.`);
                } else {
                    console.warn(`   Could not find control input via DOM traversal for ${selectorId}.`);
                }
            } catch (e) {
                console.error(`   Error clearing input via DOM traversal for ${selectorId}:`, e);
            }
        }
    });
    
    console.log(`✅ Tom Select (Multi) initialized for ${selectorId} in the loaded form.`);
}

/**
 * Initialize contact selection with Tom Select for the call form (Single Select)
 */
function initializeCallContactSelect(formElement) {
    // Only run if Tom Select is available
    if (typeof TomSelect === 'undefined') {
        console.error('❌ Tom Select not available for call form');
        return;
    }

    const selector = formElement.querySelector('.tom-select-single#call_contact');
    if (!selector) {
        console.warn('⚠️ Call Contact selector (.tom-select-single#call_contact) not found in the form.');
        return;
    }
    
    const companyId = formElement.querySelector('input[name="company_id"]')?.value || 
                      selector.dataset.companyId;
    
    if (!companyId) {
        console.warn('⚠️ No company ID found for call contact selector in the form');
        return;
    }
    
    if (selector.tomselect) {
        console.log('Tom Select already initialized for #call_contact.');
        return;
    }
    
    // Initialize Tom Select for Single Selection
    const tomSelectInstance = new TomSelect(selector, {
        // No plugins needed for single select by default
        maxItems: 1, // Allow only one selection
        valueField: 'id', 
        labelField: 'text',
        searchField: ['text', 'email'], // Search by name and email
        create: false,
        placeholder: 'Type to search for a contact...',
        load: function(query, callback) {
            if (!query.length || query.length < 2) return callback();
            
            this.loading = true;
            const url = '/crm/api/search-recipients/'; // Reuse the same endpoint
            const params = new URLSearchParams({ q: query, company_id: companyId });
            
            fetch(`${url}?${params.toString()}`)
                .then(response => response.json())
                .then(json => {
                    this.loading = false;
                    // Filter results to only include contacts for this selector
                    const contactsOnly = json.results ? json.results.filter(item => item.type === 'contact') : [];
                    callback(contactsOnly);
                })
                .catch(error => {
                    console.error('Error fetching call contacts:', error);
                    this.loading = false;
                    callback();
                });
        },
        render: {
            option: function(data, escape) {
                const email = data.email ? `<small class="text-muted ms-2">(${escape(data.email)})</small>` : '';
                return `<div class="tom-select-result d-flex align-items-center">
                         <i class="fas fa-user-tie me-2"></i> 
                         <div>
                           <span>${escape(data.text)}</span>
                           ${email}
                         </div>
                       </div>`;
            },
            item: function(data, escape) {
                 return `<div class="d-flex align-items-center">
                         <i class="fas fa-user-tie me-2"></i>
                         <span>${escape(data.text)}</span>
                       </div>`;
            },
            no_results: function(data, escape) {
                return '<div class="no-results p-2">No contacts found for "' + escape(data.input) + '"</div>';
            }
        },
        onItemAdd: (value, $item) => {
            console.log('✅ onItemAdd (Call Contact) triggered! Value:', value);
            try {
                const wrapper = selector.tomselect?.wrapper;
                const controlInput = wrapper?.querySelector('.ts-control input');
                if (controlInput) {
                    controlInput.value = ''; 
                    console.log('   Call Control input value cleared directly via DOM traversal.');
                } else {
                    console.warn('   Could not find call control input via DOM traversal.');
                }
            } catch (e) {
                console.error('   Error clearing call input via DOM traversal:', e);
            }
        }
    });
    
    console.log(`✅ Tom Select (Single) initialized for #call_contact in the loaded form.`);
}

/**
 * Submit activity form
 */
function submitActivityForm(form, activityType) {
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Saving...';
    }
    
    // Use FormData to gather all form fields
    const formData = new FormData(form);
    
    // Use fetch to submit the form
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Show success message
            showMessage(data.message || 'Activity logged successfully', 'success');
            
            // Close side panel
            const sidePanel = bootstrap.Offcanvas.getInstance(document.getElementById('activity-side-panel'));
            if (sidePanel) {
                sidePanel.hide();
            }
            
            // Reload activities
            loadActivitiesByType(activityType);
            
            // Reload all activities if on the overview tab
            const overviewTab = document.querySelector('.nav-link.active[href="#activity-overview"]');
            if (overviewTab) {
                loadActivitiesByType('all');
            }
        } else {
            // Show error message from server
            showMessage(data.message || 'Error saving activity', 'danger');
            
            // Re-enable submit button
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Save';
            }
        }
    })
    .catch(error => {
        console.error('Error submitting form:', error);
        showMessage('Error saving activity: ' + error.message, 'danger');
        
        // Re-enable submit button
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Save';
        }
    });
}

/**
 * Load activities by type
 */
function loadActivitiesByType(activityType) {
    // Get company ID
    const companyIdField = document.getElementById('company_id');
    const companyId = companyIdField ? companyIdField.value : null;
    
    if (!companyId) {
        console.error('No company ID found');
        return;
    }
    
    // Determine which container to update
    let container;
    
    if (activityType === 'all') {
        container = document.getElementById('all-activities-list');
    } else {
        container = document.getElementById(`${activityType}-activities-list`);
    }
    
    if (!container) {
        console.error(`Container for ${activityType} activities not found`);
        return;
    }
    
    // Clear any existing content completely
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
    
    // Show loading state
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'text-center py-4';
    loadingDiv.innerHTML = `
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2">Loading activities...</p>
    `;
    container.appendChild(loadingDiv);
    
    // First try loading activities from the JSON endpoint
    const jsonUrl = `/crm/company/${companyId}/activities-json/?type=${activityType}&_=${new Date().getTime()}`;
    console.log(`Loading activities from JSON: ${jsonUrl}`);
    
    fetch(jsonUrl)
        .then(response => {
            console.log(`JSON response status: ${response.status} ${response.statusText}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`Received JSON data with ${data.count} activities`);
            
            if (data.status === 'success') {
                // Clear container completely
                while (container.firstChild) {
                    container.removeChild(container.firstChild);
                }
                
                // Render activities from JSON data
                const activitiesHtml = renderActivitiesFromJson(data);
                container.innerHTML = activitiesHtml;
                console.log('Successfully rendered activities from JSON');
            } else {
                throw new Error(`Error in JSON response: ${data.message || 'Unknown error'}`);
            }
        })
        .catch(error => {
            console.error('Error loading activities from JSON:', error);
            console.log('Falling back to HTML endpoint...');
            
            // Fallback to original HTML endpoint
            const htmlUrl = `/crm/company/${companyId}/activities/?type=${activityType}&_=${new Date().getTime()}`;
            
            fetch(htmlUrl)
                .then(response => {
                    console.log(`HTML response status: ${response.status} ${response.statusText}`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.text();
                })
                .then(html => {
                    console.log(`Received HTML response (${html.length} characters)`);
                    
                    if (!html || html.trim().length < 10) {
                        throw new Error('Response is empty or too short');
                    }
                    
                    // Clear container completely
                    while (container.firstChild) {
                        container.removeChild(container.firstChild);
                    }
                    
                    container.innerHTML = html;
                    console.log('Successfully updated container with HTML response');
                })
                .catch(htmlError => {
                    console.error('Error loading activities from HTML endpoint:', htmlError);
                    
                    // Clear container completely
                    while (container.firstChild) {
                        container.removeChild(container.firstChild);
                    }
                    
                    container.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error loading activities: ${htmlError.message}
                        </div>
                    `;
                });
        });
}

/**
 * Render activities from JSON data
 */
function renderActivitiesFromJson(data) {
    if (!data.activities || data.activities.length === 0) {
        return `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                No activities found for type "${data.activity_type}"
            </div>
        `;
    }
    
    let html = `
        <div class="alert alert-info mb-3">
            Found ${data.count} activities of type "${data.activity_type}"
        </div>
        <ul class="list-group">
    `;
    
    data.activities.forEach(activity => {
        html += `
            <li class="list-group-item">
                <div>
                    <strong>Type:</strong> ${activity.type_display || activity.activity_type}
                    ${activity.description ? `<br><strong>Description:</strong> ${activity.description}` : ''}
                    <br><strong>Date:</strong> ${activity.performed_at}
                    <br><strong>By:</strong> ${activity.performed_by}
                </div>
            </li>
        `;
    });
    
    html += `</ul>`;
    return html;
}

// ======================================================
// Activity Section and Card Handlers
// ======================================================

/**
 * Setup buttons in the activity section
 */
function setupActivityButtons() {
    // Log activity button handler - DISABLED FOR NEW ACTIVITY UI
    /*
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
    */
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
function initializeDateTimePickers(form) {
    // Determine the search context: the provided form or the whole document
    const searchContext = form || document;
    const contextType = form ? 'Specific form' : 'Document';
    console.log(`⚙️ Initializing DateTimePickers. Search context: ${contextType}`);

    // --- Date Pickers --- 
    const datePickerSelector = 'input[data-datepicker]';
    const dateInputs = searchContext.querySelectorAll(datePickerSelector);
    console.log(`   Found ${dateInputs.length} elements with selector '${datePickerSelector}' in ${contextType}`);
    
    if (dateInputs.length > 0) {
        if (typeof flatpickr !== 'undefined') {
            dateInputs.forEach(input => {
                console.log(`   Processing date input: #${input.id || input.name || 'no-id'}`);
                // Check if flatpickr is already initialized
                if (!input._flatpickr) {
                    flatpickr(input, {
                        dateFormat: "Y-m-d",
                        altInput: true,
                        altFormat: "F j, Y", // More user-friendly display format
                        allowInput: true // Allows manual typing if needed
                    });
                    console.log(`     ✅ Flatpickr DATE initialized for: #${input.id || input.name || 'no-id'}`);
                } else {
                    console.log(`     ⚠️ Flatpickr DATE already initialized for: #${input.id || input.name || 'no-id'}`);
                }
            });
        } else {
            console.warn('   ⚠️ Flatpickr library not loaded, cannot initialize date pickers.');
        }
    }

    // --- Time Pickers --- 
    const timePickerSelector = 'input[data-timepicker]';
    const timeInputs = searchContext.querySelectorAll(timePickerSelector);
    console.log(`   Found ${timeInputs.length} elements with selector '${timePickerSelector}' in ${contextType}`);
    
    if (timeInputs.length > 0) {
        if (typeof flatpickr !== 'undefined') {
            timeInputs.forEach(input => {
                console.log(`   Processing time input: #${input.id || input.name || 'no-id'}`);
                // Check if flatpickr is already initialized
                if (!input._flatpickr) {
                    flatpickr(input, {
                        enableTime: true,
                        noCalendar: true,
                        dateFormat: "H:i", // Use H:i for 24-hour format
                        time_24hr: true,
                        allowInput: true // Allows manual typing if needed
                    });
                    console.log(`     ✅ Flatpickr TIME initialized for: #${input.id || input.name || 'no-id'}`);
                } else {
                    console.log(`     ⚠️ Flatpickr TIME already initialized for: #${input.id || input.name || 'no-id'}`);
                }
            });
        } else {
            console.warn('   ⚠️ Flatpickr library not loaded, cannot initialize time pickers.');
        }
    }
    console.log(`🏁 Finished DateTimePicker initialization for context: ${contextType}`);
}

// ======================================================
// Activity Details Modal - DISABLED FOR NEW ACTIVITY UI
// ======================================================

/**
 * Set up activity details modal
 */
/*
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
*/

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
 * Fetch activity details via AJAX - DISABLED FOR NEW ACTIVITY UI
 */
/*
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
*/

/**
 * Format activity details based on type - DISABLED FOR NEW ACTIVITY UI
 */
/*
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
*/

/**
 * Setup edit button on activity details modal - DISABLED FOR NEW ACTIVITY UI
 */
/*
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
*/

/**
 * Setup delete button on activity details modal - DISABLED FOR NEW ACTIVITY UI
 */
/*
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
*/

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
 * Initialize recipient selection with Tom Select
 */
function initializeRecipientSelect() {
    // Only run if Tom Select is available
    if (typeof TomSelect === 'undefined') {
        console.error('❌ Tom Select not available');
        return;
    }

    const recipientSelectors = document.querySelectorAll('.tom-select');
    
    recipientSelectors.forEach(selector => {
        // Get company ID from the form or data attribute
        const companyId = selector.closest('form')?.querySelector('input[name="company_id"]')?.value || 
                          selector.dataset.companyId || 
                          document.getElementById('company_id')?.value;
        
        if (!companyId) {
            console.warn('⚠️ No company ID found for recipient selector');
            return;
        }
        
        // Initialize Tom Select
        const tomSelect = new TomSelect(selector, {
            plugins: ['remove_button'],
            maxItems: null,
            valueField: 'id',
            labelField: 'text',
            searchField: ['text'],
            create: false,
            placeholder: 'Search for contacts or users...',
            load: function(query, callback) {
                // Show loading indicator
                this.loading = true;
                
                // Build URL with parameters
                const url = '/crm/api/search-recipients/';
                const params = new URLSearchParams({
                    q: query,
                    company_id: companyId
                });
                
                // Fetch results
                fetch(`${url}?${params.toString()}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(json => {
                        this.loading = false;
                        callback(json.results);
                    })
                    .catch(error => {
                        console.error('Error fetching recipients:', error);
                        this.loading = false;
                        callback();
                    });
            },
            render: {
                option: function(data, escape) {
                    const icon = data.type === 'contact' ? 'user-tie' : 'user';
                    const email = data.email ? `<small class="text-muted ms-2">(${escape(data.email)})</small>` : '';
                    return `<div class="tom-select-result">
                             <i class="fas fa-${icon} me-2"></i>
                             <span>${escape(data.text)}</span>
                             ${email}
                           </div>`;
                },
                item: function(data, escape) {
                    return `<div>${escape(data.text)}</div>`;
                },
                no_results: function(data, escape) {
                    return `<div class="no-results">No results found for "${escape(data.input)}"</div>`;
                }
            },
            onLoad: function() {
                // This is called after the load function completes
                console.log('Recipients loaded successfully');
            },
            onDropdownOpen: function() {
                // Focus the search input when dropdown opens
                this.focus();
            }
        });
        
        // Log initialization
        console.log(`Tom Select initialized for ${selector.id || 'recipient selector'}`);
    });
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

/**
 * Initialize TinyMCE for the email content textarea within a specific form
 */
function initializeTinyMCEForForm(formElement) {
    const selectorId = 'email_content';
    const textarea = formElement.querySelector(`#${selectorId}`);

    if (!textarea) {
        console.warn(`⚠️ TinyMCE target textarea (#${selectorId}) not found in the form.`);
        return;
    }

    console.log(`🔍 Attempting to initialize TinyMCE for #${selectorId}...`);

    // Check if TinyMCE library is loaded
    if (typeof tinymce === 'undefined') {
        console.error('❌ TinyMCE library not loaded.');
        return;
    }

    // Remove previous instances if they exist for this ID to prevent issues
    const existingEditor = tinymce.get(selectorId);
    if (existingEditor) {
        console.log(`   ⚠️ Removing existing TinyMCE instance for #${selectorId}.`);
        existingEditor.remove();
    }

    // Initialize TinyMCE
    tinymce.init({
        selector: `#${selectorId}`,
        plugins: 'autoresize link lists image media table wordcount',
        toolbar: 'undo redo | blocks | bold italic underline | bullist numlist | link image media table | removeformat',
        menubar: false,
        statusbar: true,
        min_height: 250, // Set a minimum height
        autoresize_bottom_margin: 20,
        content_style: 'body { font-family: Roboto, sans-serif; font-size: 14px; }',
        setup: function (editor) {
            editor.on('init', function () {
                console.log(`   ✅ TinyMCE initialized successfully for #${selectorId}`);
            });
            editor.on('change keyup', function () {
                // Ensure the underlying textarea value is updated for form submission
                editor.save(); 
            });
        }
    }).then(editors => {
        // Initialization promise resolved
        if (!editors || editors.length === 0) {
             console.error(`   ❌ TinyMCE initialization failed for #${selectorId}.`);
        }
    }).catch(error => {
        console.error(`   ❌ Error during TinyMCE initialization for #${selectorId}:`, error);
    });
} 