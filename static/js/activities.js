// Consolidated activities functionality for Easy Avenues CRM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Easy Avenues CRM - Initializing activities.js with DEBUG (v9.1)');
    
    // Debug: Log all side panel elements 
    console.log('Side Panel Elements:');
    console.log('- activity-side-panel:', document.getElementById('activity-side-panel'));
    console.log('- activitySidePanelLabel:', document.getElementById('activitySidePanelLabel'));
    console.log('- activity-panel-loading:', document.getElementById('activity-panel-loading'));
    console.log('- activity-panel-form-container:', document.getElementById('activity-panel-form-container'));
    
    // Side Panel Elements (shared between create and details)
    const activitySidePanel = document.getElementById('activity-side-panel');
    const activityPanelTitle = document.getElementById('activitySidePanelLabel');
    const activityPanelLoading = document.getElementById('activity-panel-loading');
    const activityPanelFormContainer = document.getElementById('activity-panel-form-container');
    
    // Make side panel elements globally accessible 
    window.activitySidePanel = activitySidePanel;
    window.activityPanelTitle = activityPanelTitle;
    window.activityPanelLoading = activityPanelLoading;
    window.activityPanelFormContainer = activityPanelFormContainer;
    
    // Initialize Bootstrap Offcanvas instance
    let sidePanelInstance = null;
    if (activitySidePanel) {
        try {
            sidePanelInstance = new bootstrap.Offcanvas(activitySidePanel);
            window.sidePanelInstance = sidePanelInstance; // Make it globally accessible
            console.log('✅ Bootstrap Offcanvas instance created successfully');
            
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
        } catch (error) {
            console.error('⚠️ Error initializing Bootstrap Offcanvas:', error);
        }
    } else {
        console.error("⚠️ Activity side panel element not found!");
    }
    
    // Initialize activity tabs
    initializeActivityTabs();
    
    // Set up activity card click handlers
    setupActivityCardHandlers();
    
    // Initialize activity filtering (if available)
    if (typeof initializeActivityFiltering === 'function') {
        initializeActivityFiltering();
    } else {
        console.log('Activity filtering not initialized (function not found)');
    }
    
    // Initialize date/time pickers for activities
    initializeDateTimePickers();
    
    // Initialize To-do toggles (if available)
    if (typeof initializeToDoToggles === 'function') {
        initializeToDoToggles();
    } else {
        console.log('To-do toggles not initialized (function not found)');
    }
    
    // Attach click handlers to activity detail links
    attachActivityDetailClickHandlers();
    
    // Also set up direct handlers for email activities as a failsafe
    setupEmailActivityClickHandlers();
    
    // Debug: Log all activity items visible on the page
    const activityItems = document.querySelectorAll('.activity-list .list-group-item');
    console.log(`Found ${activityItems.length} activity items on page load`);
    activityItems.forEach((item, index) => {
        const id = item.getAttribute('data-activity-id');
        const type = item.getAttribute('data-activity-type');
        const hasDetailLinkClass = item.classList.contains('activity-detail-link');
        console.log(`Item ${index}: ID=${id}, Type=${type}, Has activity-detail-link class=${hasDetailLinkClass}`);
    });
    
    // Use event delegation to handle clicks on activity items that are loaded dynamically
    document.addEventListener('click', function(e) {
        console.log("⚡ Click event captured on:", e.target);
        
        // Find the closest activity list item ancestor of the clicked element
        const activityItem = e.target.closest('.activity-list .list-group-item');
        if (!activityItem) {
            console.log("❌ No activity item found in the clicked element's ancestors");
            return; // Not clicking on an activity item
        }
        
        const activityId = activityItem.getAttribute('data-activity-id');
        if (!activityId) {
            console.log("❌ No activity ID found on the clicked element");
            return;
        }
        
        const activityType = activityItem.getAttribute('data-activity-type');
        const isEmailActivity = activityType === 'email';
        
        console.log(`✅ Activity item clicked: ID=${activityId}, Type=${activityType}, Is Email=${isEmailActivity}`);
        
        // Only prevent default if we're handling the click
        e.preventDefault();
        e.stopPropagation(); // Stop event from bubbling to prevent double handling
        
        // Load activity details into side panel
        loadActivityDetailsIntoPanel(activityId);
    });
    
    // Function to load activity details into side panel
    function loadActivityDetailsIntoPanel(activityId) {
        console.log(`🔍 Loading activity details for ID: ${activityId}`);
        
        if (!activityId) {
            console.error("❌ No activity ID provided to loadActivityDetailsIntoPanel");
            return;
        }
        
        if (!sidePanelInstance) {
            console.error('❌ Side panel instance not found - attempting to create it');
            const sidePanel = document.getElementById('activity-side-panel');
            if (sidePanel) {
                try {
                    sidePanelInstance = new bootstrap.Offcanvas(sidePanel);
                    console.log('✅ Created new Offcanvas instance');
                } catch (error) {
                    console.error('⚠️ Error creating Offcanvas instance:', error);
                    return;
                }
            } else {
                console.error('❌ Side panel element not found in the DOM');
                return;
            }
        }
        
        // Change panel title
        if (activityPanelTitle) {
            activityPanelTitle.textContent = 'Activity Details';
        } else {
            console.warn('⚠️ Activity panel title element not found');
        }
        
        // Show loading state, hide form container
        if (activityPanelLoading) {
            activityPanelLoading.style.display = 'block';
        } else {
            console.warn('⚠️ Activity panel loading element not found');
        }
        
        if (activityPanelFormContainer) {
            activityPanelFormContainer.style.display = 'none';
            activityPanelFormContainer.innerHTML = '';
        } else {
            console.warn('⚠️ Activity panel form container element not found');
        }
        
        // Show the panel
        try {
            sidePanelInstance.show();
            console.log('✅ Side panel shown successfully');
        } catch(err) {
            console.error('❌ Error showing side panel:', err);
            // Try to create a new instance and show it
            try {
                sidePanelInstance = new bootstrap.Offcanvas(activitySidePanel);
                sidePanelInstance.show();
                console.log('✅ Created new instance and showed panel successfully');
            } catch(retryErr) {
                console.error('❌ Failed to create and show panel even after retry:', retryErr);
                return;
            }
        }
        
        // Fetch activity details
        const url = `/crm/activity/${activityId}/detail/sidepanel/`;
        console.log(`🔄 Fetching activity details from: ${url}`);
        
        fetch(url)
            .then(response => {
                console.log(`📊 Response status: ${response.status} ${response.statusText}`);
                if (!response.ok) {
                    throw new Error(`Network response error: ${response.status} ${response.statusText}`);
                }
                return response.text();
            })
            .then(html => {
                console.log(`📝 Received HTML response (${html.length} characters)`);
                
                if (!html || html.trim().length === 0) {
                    throw new Error('Empty response received from server');
                }
                
                // For debugging - check for specific email activity issues
                if (html.includes('EmailActivity') || html.includes('activity_type == \'email\'')) {
                    console.log('Email activity references found in HTML');
                }
                
                // Hide loading, show content
                if (activityPanelLoading) {
                    activityPanelLoading.style.display = 'none';
                }
                if (activityPanelFormContainer) {
                    activityPanelFormContainer.innerHTML = html;
                    activityPanelFormContainer.style.display = 'block';
                    console.log('✅ Content loaded into side panel successfully');
                    
                    // Bind event handlers for edit/delete buttons
                    bindDetailPanelEventHandlers();
                } else {
                    console.error('❌ Cannot find form container to display content');
                }
            })
            .catch(error => {
                console.error('❌ Error loading activity details:', error);
                if (activityPanelLoading) {
                    activityPanelLoading.style.display = 'none';
                }
                if (activityPanelFormContainer) {
                    activityPanelFormContainer.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error loading activity details: ${error.message}. Please try again.
                        </div>`;
                    activityPanelFormContainer.style.display = 'block';
                }
            });
    }
    
    // Attach click event to activity links/buttons that should open the side panel
    function attachActivityDetailClickHandlers() {
        console.log("🔄 Re-attaching activity detail click handlers");
        const activityDetailLinks = document.querySelectorAll('.activity-list .list-group-item');
        console.log(`Found ${activityDetailLinks.length} activity items to attach handlers to`);
        
        activityDetailLinks.forEach((link, index) => {
            const id = link.getAttribute('data-activity-id');
            const type = link.getAttribute('data-activity-type');
            if (!id) return; // Skip items without ID
            
            console.log(`Item ${index}: ID=${id}, Type=${type}`);
            
            // Remove existing handler to prevent duplicates
            const newLink = link.cloneNode(true);
            link.parentNode.replaceChild(newLink, link);
            
            // Add click handler
            newLink.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log(`Activity item clicked directly: ${id}`);
                loadActivityDetailsIntoPanel(id);
                return false;
            });
        });
    }
    
    // Set up direct handlers on all email activity items as a failsafe
    function setupEmailActivityClickHandlers() {
        const emailItems = document.querySelectorAll('.list-group-item[data-activity-type="email"]');
        console.log(`Setting up direct handlers for ${emailItems.length} email activity items`);
        
        emailItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const activityId = this.getAttribute('data-activity-id');
                console.log(`Direct email activity click handler called: ${activityId}`);
                loadActivityDetailsIntoPanel(activityId);
            });
        });
    }
    
    // Call function to set up direct email handlers
    setupEmailActivityClickHandlers();
    
    // Attach click event to activity links/buttons that should open the side panel
    attachActivityDetailClickHandlers();
    
    // Expose functions globally for other components
    window.loadActivityDetailsIntoPanel = loadActivityDetailsIntoPanel;
    window.attachActivityDetailClickHandlers = attachActivityDetailClickHandlers;
    window.setupEmailActivityClickHandlers = setupEmailActivityClickHandlers;
    
    // Fix for dropdown menu display issues
    fixActivityDropdown();
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
    // This will also handle loading the default 'all' tab content
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
            openActivitySidePanel('waiver_favour');
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
    const activityTabsContainer = document.querySelector('.activity-tabs');
    if (!activityTabsContainer) {
        console.warn("Activity tabs container (.activity-tabs) not found.");
        return;
    }

    // Use event delegation on the container
    activityTabsContainer.addEventListener('click', function(event) {
        // Check if the clicked element is a tab button
        const tabButton = event.target.closest('button[data-bs-toggle="tab"]');
        if (!tabButton) return; // Exit if the click wasn't on a tab button

        // Get the activity type from the data attribute
        const activityType = tabButton.dataset.activityType;
        if (!activityType) {
            console.warn("Clicked tab button is missing data-activity-type attribute.");
            return;
        }

        console.log(`Tab button clicked: ${activityType}`);

        // Load activities for the clicked tab's type
        // We add a small delay to ensure the tab pane is visible before loading
        setTimeout(() => {
            console.log(`Loading activities for type: ${activityType}`);
            loadActivitiesByType(activityType);
        }, 150); // 150ms delay
    });

    // Find active tab on page load and load activities for it
    const activeTab = activityTabsContainer.querySelector('.nav-link.active');
    if (activeTab && activeTab.dataset.activityType) {
        console.log(`Found active tab on page load: ${activeTab.dataset.activityType}`);
        // Trigger click on the active tab to load its content
        activeTab.click();
    } else {
        // Fallback: Load 'all' activities if no active tab is found
        console.log('No active tab found, defaulting to "all" activities');
        loadActivitiesByType('all');
    }

    // Handle direct navigation with hash
    if (window.location.hash) {
        const targetTabButton = document.querySelector(`button[data-bs-target="${window.location.hash}"]`);
        if (targetTabButton && targetTabButton.dataset.activityType) {
            const initialActivityType = targetTabButton.dataset.activityType;
            console.log(`Direct navigation to tab detected, loading type: ${initialActivityType}`);
            // Trigger a click on the tab button
            targetTabButton.click();
        }
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
    
    // Make sure backdrop is cleaned up when panel closes
    sidePanel.addEventListener('hidden.bs.offcanvas', function() {
        const backdrop = document.querySelector('.offcanvas-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }, { once: true }); // Use once:true so we don't keep adding listeners
    
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
        'waiver_favour': 'Log Waiver & Favour',
        'task': 'Log Task'
    };
    
    const iconMap = {
        'email': 'envelope',
        'call': 'phone-alt',
        'meeting': 'users',
        'note': 'sticky-note',
        'waiver_favour': 'handshake',
        'task': 'tasks'
    };
    
    // Update title with icon
    panelTitle.innerHTML = `<i class="fas fa-${iconMap[activityType] || 'file-alt'} me-2"></i> ${titleMap[activityType] || 'Log Activity'}`;
    
    // Add appropriate class for styling
    panelTitle.className = 'offcanvas-title activity-header-' + (activityType || 'default');
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
        } else if (activityType === 'waiver_favour') {
            console.log("Initializing waiver/favour form elements");
            
            initializeRecipientSelectForForm(form, '#waiver_favour_contacts', true);

            // No need to initialize the hidden field, it's handled by the form directly
            
            // Show the Send Email checkbox only for the waiver form
            const sendEmailDiv = form.querySelector('.send-email-option');
            if (sendEmailDiv) {
                sendEmailDiv.style.display = 'block';
            }
        } else if (activityType === 'task') {
            console.log("Initializing task form elements");
            
            // Initialize the contacts/users TomSelect
            initializeRecipientSelectForForm(form, '#task_related_contacts', false);
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
 * @param {boolean} [contactsOnly=false] - Whether to only include contacts (no users).
 */
function initializeRecipientSelectForForm(formElement, selectorId = '#email_recipients', contactsOnly = false) {
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
    
    console.log(`Setting up TomSelect for ${selectorId} with company ID: ${companyId}`);
    
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
        placeholder: contactsOnly ? 'Type to search for contacts...' : 'Type to search for contacts or users...',
        load: function(query, callback) {
            // Only allow non-empty queries with minimum length of 2
            if (query.length < 2) {
                return callback();
            }
            
            console.log(`🔍 TomSelect search: "${query}" for ${selectorId} (company ID: ${companyId})`);
            this.loading = true;
            
            const url = '/crm/api/search-recipients/';
            const params = new URLSearchParams({ 
                q: query, 
                company_id: companyId,
                contacts_only: contactsOnly ? '1' : '0',
                limit: '10'
            });
            
            fetch(`${url}?${params.toString()}`)
                .then(response => response.json())
                .then(json => {
                    this.loading = false;
                    console.log(`✅ Search results received for "${query}":`, json);
                    
                    // If contacts_only parameter isn't supported by the backend, filter here
                    let results = json.results || [];
                    
                    if (contactsOnly) {
                        const beforeCount = results.length;
                        results = results.filter(item => item.type === 'contact');
                        console.log(`Filtered ${beforeCount} results to ${results.length} contacts only`);
                    }
                    
                    callback(results);
                })
                .catch(error => {
                    console.error(`❌ Error fetching data for ${selectorId}:`, error);
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
            console.log(`✅ Item added! Value: ${value} for ${selectorId}`);
            try {
                const wrapper = selector.tomselect?.wrapper;
                const controlInput = wrapper?.querySelector('.ts-control input');
                if (controlInput) {
                    controlInput.value = '';
                    console.log(`Control input value cleared for ${selectorId}`);
                }
            } catch (e) {
                console.error(`Error clearing input for ${selectorId}:`, e);
            }
        }
    });
    
    console.log(`✅ Tom Select initialized for ${selectorId}. Contacts only: ${contactsOnly}`);
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
 * Initialize TinyMCE for rich text editing in a specific form
 * @param {HTMLElement} formElement - The form containing the textarea to initialize with TinyMCE
 */
function initializeTinyMCEForForm(formElement) {
    // Only run if TinyMCE is available
    if (typeof tinymce === 'undefined') {
        console.error('❌ TinyMCE not available');
        return;
    }

    // Find the textarea element(s) to initialize
    const textareas = formElement.querySelectorAll('textarea.rich-text-editor');
    if (!textareas || textareas.length === 0) {
        console.warn('⚠️ No rich text editor textarea found in the form');
        return;
    }
    
    console.log(`Initializing TinyMCE for ${textareas.length} textareas in form`);
    
    // Initialize TinyMCE for each textarea found
    textareas.forEach((textarea, index) => {
        // Generate a unique ID if one doesn't exist
        if (!textarea.id) {
            textarea.id = `richtext-editor-${Date.now()}-${index}`;
        }
        
        // Check if this textarea is already initialized
        if (tinymce.get(textarea.id)) {
            console.log(`TinyMCE already initialized for textarea with ID: ${textarea.id}`);
            return;
        }
        
        // Initialize TinyMCE with appropriate configuration
        tinymce.init({
            selector: `#${textarea.id}`,
            height: 250,
            menubar: false,
            plugins: 'lists link autolink',
            toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | link',
            content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; }',
            setup: function(editor) {
                // Add any additional setup here if needed
                editor.on('change', function() {
                    editor.save(); // Save content back to textarea on change
                });
            }
        });
        
        console.log(`✅ TinyMCE initialized for textarea with ID: ${textarea.id}`);
    });
}

/**
 * Submit an activity form via AJAX
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
    let url = '';
    switch (activityType) {
        case 'email': url = form.action || '{% url "crm:log_email_activity" %}'; break;
        case 'call': url = form.action || '{% url "crm:log_call_activity" %}'; break;
        case 'meeting': url = form.action || '{% url "crm:log_meeting_activity" %}'; break;
        case 'note': url = form.action || '{% url "crm:log_note_activity" %}'; break;
        case 'waiver_favour': url = form.action || '{% url "crm:log_waiver_favour_activity" %}'; break;
        case 'task': url = form.action || '{% url "crm:log_task_activity" %}'; break;
        // Add other types here
        default:
            console.error(`Unknown activity type for submission: ${activityType}`);
            // No need for JavaScript alerts - Django messages will handle it
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Save';
            return;
    }
    
    fetch(url, {
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
            // Django messages will handle success notifications - no need for JavaScript alerts
            
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
            
            // Refresh the page to show Django messages
            window.location.reload();
        } else {
            // Error messages will be handled by Django messages - no need for JavaScript alerts
            console.error('Error from server:', data.message);
            
            // Re-enable submit button
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Save';
            }
        }
    })
    .catch(error => {
        console.error('Error submitting form:', error);
        // Error messages will be handled by Django messages - no need for JavaScript alerts
        
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
    
    // Determine which container to update based on activity type
    let container;
    
    if (activityType === 'all') {
        container = document.getElementById('all-activities-list');
    } else if (activityType === 'email') {
        container = document.getElementById('email-activities-list');
    } else if (activityType === 'call') {
        container = document.getElementById('call-activities-list');
    } else if (activityType === 'meeting') {
        container = document.getElementById('meeting-activities-list');
    } else if (activityType === 'note') {
        container = document.getElementById('note-activities-list');
    } else if (activityType === 'waiver_favour') {
        container = document.getElementById('waiver-activities-list');
    } else if (activityType === 'task') {
        container = document.getElementById('task-activities-list');
    } else {
        console.error(`Unknown activity type: ${activityType}`);
        return;
    }
    
    if (!container) {
        console.error(`Container for ${activityType} activities not found`);
        return;
    }
    
    // Log what we're doing
    console.log(`Loading activities of type "${activityType}" into container #${container.id}`);
    
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
    
    // Build URL for fetching activities - include timestamp to prevent caching
    const url = `/crm/company/${companyId}/activities/?type=${activityType}&_=${new Date().getTime()}`;
    
    // Fetch activities
    fetch(url)
        .then(response => {
            console.log(`Response status: ${response.status} ${response.statusText}`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            console.log(`Received HTML response (${html.length} characters) for ${activityType}`);
            if (!html || html.trim().length < 10) {
                throw new Error('Response is empty or too short');
            }
            
            // Clear container and update with new content
            while (container.firstChild) { 
                container.removeChild(container.firstChild); 
            }
            container.innerHTML = html;
            console.log(`Successfully updated ${activityType} container with activities`);
            
            // Re-attach click handlers to newly loaded activity items
            attachActivityDetailClickHandlers();
            setupEmailActivityClickHandlers();
        })
        .catch(error => {
            console.error(`Error loading ${activityType} activities:`, error);
            
            // Clear container and show error
            while (container.firstChild) { 
                container.removeChild(container.firstChild); 
            }
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error loading activities: ${error.message}
                </div>
            `;
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
 * Show a message to the user
 * @deprecated This function is kept for backward compatibility, but new code should use Django messages
 * instead of client-side alerts.
 * @param {string} message - The message to show
 * @param {string} type - The type of message (success, danger, etc.)
 */
function showMessage(message, type = 'info') {
    // If the project uses Bootstrap toasts, create and show one
    const toastContainer = document.querySelector('.toast-container');
    if (toastContainer) {
        const toastHTML = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = toastContainer.querySelector('.toast:last-child');
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    } else {
        // Fallback to console log instead of alert - Django messages will handle user notifications
        console.log(`Message (${type}): ${message}`);
    }
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
    // Function code removed as it's no longer used
}
*/

// ======================================================
// Helper Functions (Added from activity_details.js)
// ======================================================

/**
 * Helper function to get CSRF token
 * @returns {string} The CSRF token value
 */
function getCsrfToken() {
    return document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || 
           document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
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

// ======================================================
// Compatibility Functions (from activity_details.js)
// ======================================================

/**
 * Compatibility wrapper for the older activity details modal
 * @deprecated Use loadActivityDetailsIntoPanel instead
 */
function initActivityDetailsModal() {
    console.log('Original initActivityDetailsModal called - this is no longer used');
}

/**
 * Compatibility wrapper for the older fetch activity details function
 * @param {string} activityId - The ID of the activity to load
 * @deprecated Use loadActivityDetailsIntoPanel instead
 */
function fetchActivityDetails(activityId) {
    console.log('Original fetchActivityDetails called with ID:', activityId);
    // In the original code, this called fetchActivityDetailsSimple, but we'll use our new function
    if (typeof loadActivityDetailsIntoPanel === 'function') {
        loadActivityDetailsIntoPanel(activityId);
    } else {
        console.error('loadActivityDetailsIntoPanel function not available');
    }
}

/**
 * Compatibility wrapper for the older setup delete button listeners
 * @deprecated Delete buttons are now handled by bindDetailPanelEventHandlers
 */
function setupDeleteButtonListeners() {
    console.log('Setting up delete button listeners (compatibility function)');
    const deleteButtons = document.querySelectorAll('.delete-activity-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const activityId = this.getAttribute('data-activity-id');
            
            if (confirm('Are you sure you want to delete this activity? This action cannot be undone.')) {
                // Use the new fetch-based deletion method instead of redirect
                if (typeof getCsrfToken === 'function') {
                    fetch(`/crm/activity/${activityId}/delete/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCsrfToken(),
                            'X-Requested-With': 'XMLHttpRequest',
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
                            // Close side panel if open
                            const sidePanel = bootstrap.Offcanvas.getInstance(document.getElementById('activity-side-panel'));
                            if (sidePanel) {
                                sidePanel.hide();
                            }
                            
                            // Reload the page to show Django messages
                            window.location.reload();
                        } else {
                            console.error('Error deleting activity:', data.message);
                            // Reload the page to show Django error messages
                            window.location.reload();
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting activity:', error);
                        // Reload the page to show Django error messages
                        window.location.reload();
                    });
                } else {
                    // Fall back to the old redirect method
                    window.location.href = `/crm/activity/${activityId}/delete/`;
                }
            }
        });
    });
}

// Function to bind event handlers within the loaded details
function bindDetailPanelEventHandlers() {
    // Edit button - opens the edit form in the same panel
    const editButtons = document.querySelectorAll('.edit-activity-btn');
    console.log(`Found ${editButtons.length} edit buttons to bind handlers to`);
    
    editButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const activityId = this.getAttribute('data-activity-id');
            console.log(`Edit button clicked for activity ID: ${activityId}`);
            
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
    console.log(`Found ${deleteButtons.length} delete buttons to bind handlers to`);
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const activityId = this.getAttribute('data-activity-id');
            console.log(`Delete button clicked for activity ID: ${activityId}`);
            
            if (confirm('Are you sure you want to delete this activity? This action cannot be undone.')) {
                fetch(`/crm/activity/${activityId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'X-Requested-With': 'XMLHttpRequest',
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
                        // Close panel 
                        sidePanelInstance.hide();
                        
                        // Reload page to show Django messages and refresh all activities
                        window.location.reload();
                    } else {
                        console.error('Error deleting activity:', data.message);
                        // Reload page to show Django error messages
                        window.location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error deleting activity:', error);
                    // Reload page to show Django error messages
                    window.location.reload();
                });
            }
        });
    });
}

// Also add back the initial load of activities
// Directly load all activities when on a company page
const companyIdField = document.getElementById('company_id');
const activitiesTab = document.getElementById('activities');

if (companyIdField && activitiesTab) {
    console.log('🏢 Company page detected, will load initial activities...');
    
    // Check if we're on the activities tab or another tab
    const activitiesTabLink = document.getElementById('activities-tab');
    
    // Initial load ONLY for the default active tab ('all')
    setTimeout(function() {
        console.log('🔄 Initial load of activities...');
        loadActivitiesByType('all'); 
    }, 500);
    
    // Manual trigger for activities tab
    if (activitiesTabLink) {
        activitiesTabLink.addEventListener('click', function() {
            console.log('📋 Activities tab clicked, loading all activities...');
            // Force reload activities after a small delay
            setTimeout(() => loadActivitiesByType('all'), 300);
        });
    }
}

// Add a basic implementation of the missing functions
function initializeActivityFiltering() {
    console.log('Activity filtering initialization stub (placeholder)');
    
    // Add actual filtering implementation if needed
    const filterInputs = document.querySelectorAll('.activity-filter-input');
    filterInputs.forEach(input => {
        input.addEventListener('keyup', function() {
            const filterValue = this.value.toLowerCase();
            const activityItems = document.querySelectorAll('.activity-list .list-group-item');
            
            activityItems.forEach(item => {
                const textContent = item.textContent.toLowerCase();
                if (textContent.includes(filterValue)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
}

function initializeToDoToggles() {
    console.log('To-do toggles initialization stub (placeholder)');
    
    // Add actual to-do toggle implementation if needed
    const todoCheckboxes = document.querySelectorAll('.todo-checkbox');
    todoCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const todoId = this.getAttribute('data-todo-id');
            if (todoId) {
                console.log(`Todo ${todoId} toggled to ${this.checked ? 'completed' : 'not completed'}`);
                // Add AJAX call here to update the todo status if needed
            }
        });
    });
}

// Fix for dropdown menu display issues
function fixActivityDropdown() {
    // Get the Log Activity dropdown button
    const dropdownBtn = document.querySelector('.activity-tabs-header .dropdown-toggle');
    if (!dropdownBtn) return;
    
    console.log('🔧 Fixing activity dropdown menu display');
    
    // Ensure proper Bootstrap initialization
    dropdownBtn.addEventListener('click', function(e) {
        console.log('Activity dropdown button clicked');
        
        // Ensure the dropdown menu is properly positioned
        const dropdownMenu = this.nextElementSibling;
        if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
            // Force dropdown to be visible when open
            if (this.getAttribute('aria-expanded') === 'true') {
                dropdownMenu.style.maxHeight = 'none';
                dropdownMenu.style.overflow = 'visible';
                console.log('Dropdown should be open with all items visible');
            }
        }
    });
}