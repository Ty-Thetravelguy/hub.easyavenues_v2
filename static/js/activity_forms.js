// ======================================================
// DIRECT AJAX TEST - REMOVE AFTER DEBUGGING
// This tests the AJAX endpoint directly to identify issues
// ======================================================
(function debugAjaxEndpoint() {
    document.addEventListener('DOMContentLoaded', function() {
        // Add debug code to find who's adding select2-styles
        console.log('⚠️ TRACKING: Looking for select2-styles element');
        const element = document.getElementById('select2-styles');
        if (element) {
            console.log('⚠️ TRACKING: select2-styles element found!');
            console.trace('Stack trace for debugging');
        } else {
            console.log('⚠️ TRACKING: select2-styles element not found on initial load');
            
            // Set up a mutation observer to catch it being added
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.addedNodes) {
                        mutation.addedNodes.forEach(function(node) {
                            if (node.id === 'select2-styles') {
                                console.log('⚠️ TRACKING: select2-styles was added to the DOM!');
                                console.log('Added by:', node.parentNode);
                                console.trace('Stack trace for debugging');
                                observer.disconnect();
                            }
                        });
                    }
                });
            });
            
            observer.observe(document.head, { 
                childList: true, 
                subtree: true 
            });
            
            console.log('⚠️ TRACKING: Observer set up to detect select2-styles');
        }
        
        // Only run on pages with the email form
        if (!document.getElementById('company_id')) {
            console.log('⚠️ DEBUG: No company_id field found, skipping AJAX test');
            return;
        }
        
        const companyId = document.getElementById('company_id').value;
        console.log('⚠️ DEBUG: Running direct test of AJAX endpoint with company_id:', companyId);
        
        // Get CSRF token
        function getCsrfToken() {
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
        
        // Log all contacts in this company as a sanity check
        console.log('⚠️ DEBUG: Testing contact search for company:', companyId);
        
        // Make a direct AJAX request to test the endpoint
        jQuery.ajax({
            url: '/crm/api/search-recipients/',
            method: 'GET',
            data: { 
                term: 'a',  // Very generic search term that should match most contacts
                company_id: companyId
            },
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(data) {
                console.log('✅ DEBUG: AJAX generic search test:', data);
                if (data.results && data.results.length > 0) {
                    console.log(`✅ DEBUG: Found ${data.results.length} results with generic search`);
                    // Log each contact/user found
                    data.results.forEach(result => {
                        console.log(`- ${result.type}: ${result.text} (ID: ${result.id})`);
                    });
                } else {
                    console.warn('⚠️ DEBUG: No results found with generic search - possible data issue');
                }
            },
            error: function(xhr, status, error) {
                console.error('❌ DEBUG: AJAX generic search test failed:', status, error);
            }
        });
        
        // Make a direct AJAX request to test the endpoint with specific search
        jQuery.ajax({
            url: '/crm/api/search-recipients/',
            method: 'GET',
            data: { 
                term: 'test',  // Simple test term
                company_id: companyId
            },
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(data) {
                console.log('✅ DEBUG: AJAX endpoint is working!', data);
            },
            error: function(xhr, status, error) {
                console.error('❌ DEBUG: AJAX endpoint error:', status, error);
                console.error('Response:', xhr.responseText);
                if (xhr.status === 404) {
                    console.error('❌ DEBUG: AJAX endpoint not found! Check URL path is correct.');
                } else if (xhr.status === 403) {
                    console.error('❌ DEBUG: CSRF token missing or permission denied!');
                } else if (xhr.status === 500) {
                    console.error('❌ DEBUG: Server error! Check Django logs for details.');
                    try {
                        const responseObj = JSON.parse(xhr.responseText);
                        console.error('Server error details:', responseObj.error);
                    } catch (e) {
                        console.error('Could not parse error response');
                    }
                }
            }
        });
        
        // Try an additional test with a more realistic search term
        jQuery.ajax({
            url: '/crm/api/search-recipients/',
            method: 'GET',
            data: { 
                term: 'julie',  // More specific term
                company_id: companyId
            },
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(data) {
                console.log('✅ DEBUG: AJAX endpoint specific search test successful!', data);
            },
            error: function(xhr, status, error) {
                console.error('❌ DEBUG: AJAX endpoint specific search test failed:', status, error);
            }
        });
    });
})();

// Main Activity Forms Module - Consolidated code for email form and activity modals
(function() {
    console.log('⚙️ ACTIVITY FORMS - Initialization starting');
    
    // Wait for DOM to be fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        console.log('⚙️ ACTIVITY FORMS - DOM Content Loaded');
        
        // Check for jQuery
        if (typeof jQuery === 'undefined') {
            console.error('❌ jQuery not found - cannot initialize forms');
            return;
        }
        
        // Check for Select2
        if (typeof jQuery.fn.select2 === 'undefined') {
            console.error('❌ Select2 plugin not found');
            return;
        }
        
        // Setup CSRF token for all AJAX requests
        setupCsrfToken();
        
        // Handle activity section buttons
        setupActivityButtons();
        
        // Set up activity card click handlers
        setupActivityCardHandlers();
        
        // Initialize all Select2 elements
        initializeAllSelect2();
        
        // Initialize To-do toggles
        initializeToDoToggles();
        
        // Initialize date/time pickers
        initializeDateTimePickers();
        
        // Handle modal shown event to ensure Select2 is properly initialized
        jQuery('#logActivityModal').on('shown.bs.modal', function () {
            console.log('⚙️ Activity modal shown, initializing Select2');
            
            // Make sure the cards have proper click handlers to show/hide forms
            setupActivityCardHandlers();
            
            // Allow a moment for the DOM to update
            setTimeout(function() {
                // Only reinitialize if not already initialized
                jQuery('.select2-multiple').not('.select2-hidden-accessible').each(function() {
                    // Mark for initialization
                    jQuery(this).data('needs-init', true);
                });
                
                // Initialize only the ones that need it
                initializeAllSelect2();
            }, 100);
        });
    });
    
    // Set up CSRF token for all AJAX requests
    function setupCsrfToken() {
        // Get CSRF token from cookie or DOM
        function getCsrfToken() {
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
        
        // Set jQuery AJAX defaults to always include the CSRF token
        jQuery.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', getCsrfToken());
                }
                xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            }
        });
        
        console.log('⚙️ ACTIVITY FORMS - CSRF token setup complete');
    }
    
    // Set up activity button handlers
    function setupActivityButtons() {
        // Map from modal IDs to form IDs
        const modalToFormMap = {
            '#logEmailModal': 'email-form',
            '#logCallModal': 'call-form',
            '#logMeetingModal': 'meeting-form',
            '#logNoteModal': 'note-form',
            '#logWaiverModal': 'waiver-form'
        };
        
        // Handle all activity buttons
        Object.keys(modalToFormMap).forEach(modalId => {
            const formId = modalToFormMap[modalId];
            jQuery(document).on('click', `button[data-bs-target="${modalId}"]`, function(e) {
                e.preventDefault();
                
                // Find the activity type card that corresponds to this form
                const card = jQuery(`.activity-type-card[data-form-target="${formId}"]`);
                if (card.length) {
                    // Show the actual logActivityModal
                    jQuery('#logActivityModal').modal('show');
                    
                    // Trigger a click on the corresponding card
                    setTimeout(() => {
                        card.click();
                    }, 100);
                } else {
                    console.error(`❌ Could not find activity card for form: ${formId}`);
                }
            });
        });
        
        console.log('⚙️ ACTIVITY FORMS - Activity buttons initialized');
    }
    
    // Initialize all Select2 elements on the page
    function initializeAllSelect2() {
        // Find all contact select elements
        const selectElements = jQuery('.contact-select, .contact-input');
        console.log(`⚙️ ACTIVITY FORMS - Found ${selectElements.length} contact select elements`);
        
        if (selectElements.length === 0) {
            return;
        }

        selectElements.each(function() {
            const $element = jQuery(this);
            
            // Skip if already properly initialized
            if ($element.hasClass('select2-hidden-accessible')) {
                return;
            }
            
            const modalParent = $element.closest('.modal');
            const companyId = $element.closest('form').find('#company_id').val() || '';
            
            console.log(`⚙️ Initializing Select2 for ${$element.attr('name')} with company_id: ${companyId}`);
            
            try {
                // First destroy if already initialized
                if ($element.hasClass('select2-hidden-accessible')) {
                    $element.select2('destroy');
                }
                
                // Find the actual scrollable container in the modal
                const scrollableContainer = $element.closest('.modal-body');
                
                // Initialize with Bootstrap classes only
                $element.select2({
                    theme: 'bootstrap-5',
                    ajax: {
                        url: '/crm/api/search-recipients/',
                        dataType: 'json',
                        data: function(params) {
                            return {
                                term: params.term || '',
                                company_id: jQuery('#company_id').val() || ''
                            };
                        },
                        processResults: function(data) {
                            console.log('Search results:', data);
                            // Fix: Return the expected format with results array
                            if (!data.results) {
                                return { results: [] };
                            }
                            return data; // Server already returns correct format with results property
                        }
                    },
                    templateResult: function(data) {
                        if (data.loading) return data.text;
                        if (!data.id) return data.text;
                        
                        // Format the dropdown items with custom colors
                        const icon = data.type === 'contact' ? 'fa-address-card' : 'fa-user';
                        const colorClass = data.type === 'contact' ? 'icon-contact' : 'icon-user';
                        
                        return jQuery(
                            `<div class="d-flex align-items-center p-1">
                                <i class="fas ${icon} ${colorClass} me-2"></i>
                                <div>
                                    <span class="d-block">${data.text}</span>
                                    <small class="text-muted">${data.type === 'contact' ? 'Contact' : 'User'}</small>
                                </div>
                            </div>`
                        );
                    },
                    templateSelection: function(data) {
                        if (!data.id) return data.text;
                        
                        // Format selected items with custom colored icons and more explicit structure
                        const icon = data.type === 'contact' ? 'fa-address-card' : 'fa-user';
                        const colorClass = data.type === 'contact' ? 'icon-contact' : 'icon-user';
                        
                        return jQuery(
                            `<span class="d-inline-flex align-items-center select2-selection-item">
                                <i class="fas ${icon} ${colorClass} me-1" style="color: ${data.type === 'contact' ? '#444a9f' : '#9c85db'} !important;"></i>
                                <span>${data.text}</span>
                            </span>`
                        );
                    },
                    tags: false,
                    tokenSeparators: [','],
                    minimumInputLength: 2,
                    width: '100%',
                    dropdownPosition: 'below',
                    dropdownParent: $('body'),
                    language: {
                        noResults: function() {
                            return "No contacts or users found";
                        }
                    }
                }).on('select2:open', function() {
                    // Get references to the elements
                    const $select = $(this);
                    const $dropdown = $('.select2-dropdown');
                    
                    // Get more precise measurements
                    const selectRect = $select[0].getBoundingClientRect();
                    const modalBodyScroll = $select.closest('.modal-body').scrollTop();
                    
                    // Apply fixed positioning with precise coordinates
                    $dropdown.css({
                        'position': 'fixed',
                        'top': (selectRect.bottom) + 'px',  // Position directly under the input
                        'left': (selectRect.left) + 'px',   // Align left edges
                        'width': (selectRect.width) + 'px'  // Match width exactly
                    });
                    
                    // Force width on the search field too
                    $('.select2-search__field').css('width', '100%');
                });
                
                console.log(`✅ Select2 initialized for ${$element.attr('name')}`);
            } catch (error) {
                console.error(`❌ Error initializing Select2:`, error);
            }
        });
    }
    
    // Simplified formatRecipientResult function
    function formatRecipientResult(data) {
        if (data.loading) return data.text;
        return data.text || 'Unknown';
    }
    
    // Simplified formatRecipientSelection function
    function formatRecipientSelection(data) {
        return data.text || 'Unknown';
    }
    
    // Initialize To-do toggles
    function initializeToDoToggles() {
        try {
            jQuery('#addTodoToggle').change(function() {
                jQuery('#todoSection').toggle(this.checked);
            });
        } catch (error) {
            console.error('Error initializing To-do toggles:', error);
        }
    }
    
    // Initialize date/time pickers
    function initializeDateTimePickers() {
        try {
            // Add form-control class to date and time inputs
            jQuery('input[type="date"], input[type="time"]').addClass('form-control');
        } catch (error) {
            console.error('Error initializing date/time pickers:', error);
        }
    }
    
    // Set up the activity type cards to show/hide the right forms
    function setupActivityCardHandlers() {
        const activityTypeCards = document.querySelectorAll('.activity-type-card');
        const activityForms = document.querySelectorAll('.activity-form');
        const initialMessage = document.getElementById('initial-message');
        
        // First check if the handlers are already bound
        if (activityTypeCards.length === 0) {
            console.log('⚙️ No activity type cards found');
            return;
        }
        
        console.log(`⚙️ Found ${activityTypeCards.length} activity cards and ${activityForms.length} forms`);
        
        // Add click handlers to each card
        activityTypeCards.forEach(card => {
            // Check if handler is already attached
            if (card.dataset.handlerAttached === 'true') {
                return;
            }
            
            // Add the click handler
            card.addEventListener('click', function() {
                console.log('⚙️ Activity card clicked:', this.dataset.formTarget);
                
                // Remove active class from all cards
                activityTypeCards.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked card
                this.classList.add('active');
                
                // Hide all forms and initial message
                activityForms.forEach(form => {
                    form.style.display = 'none';
                });
                
                if (initialMessage) {
                    initialMessage.style.display = 'none';
                }
                
                // Show the selected form
                const formId = this.dataset.formTarget;
                const selectedForm = document.getElementById(formId);
                if (selectedForm) {
                    console.log('⚙️ Displaying form:', formId);
                    
                    // Log the form's contents
                    console.log('⚙️ Form fields:', selectedForm.elements ? selectedForm.elements.length : 'No elements property');
                    console.log('⚙️ Form HTML:', selectedForm.innerHTML.substring(0, 100) + '...');
                    
                    // Make sure the form is visible
                    selectedForm.style.display = 'block';
                    
                    // Initialize select2 elements in the form without recreating already initialized ones
                    setTimeout(function() {
                        // Check if the form is actually visible
                        console.log(`⚙️ Form ${formId} display style:`, selectedForm.style.display);
                        
                        // Force the form to be visible
                        selectedForm.style.display = 'block';
                        selectedForm.classList.remove('d-none');
                        
                        // Count select2 elements that need initialization
                        const select2Elements = selectedForm.querySelectorAll('.select2-multiple:not(.select2-hidden-accessible)');
                        console.log(`⚙️ Found ${select2Elements.length} select2 elements in form ${formId} that need initialization`);
                        
                        if (select2Elements.length > 0) {
                            // Mark them for initialization
                            select2Elements.forEach(el => {
                                jQuery(el).data('needs-init', true);
                            });
                            
                            // Initialize only if needed
                            initializeAllSelect2();
                        }
                    }, 100);
                } else {
                    console.error(`❌ Could not find form with ID: ${formId}`);
                }
            });
            
            // Mark as handler attached
            card.dataset.handlerAttached = 'true';
        });
        
        console.log('⚙️ Activity card handlers set up');
    }
})();

// Helper function to get selected text from a textarea
function getSelectedText(textarea) {
    try {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    return textarea.value.substring(start, end);
    } catch (error) {
        console.error('Error getting selected text:', error);
        return '';
    }
}

// Helper function to insert text at cursor position
function insertText(elementId, text) {
    try {
        const textarea = document.getElementById(elementId);
        if (!textarea) return;
        
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const scrollTop = textarea.scrollTop;

    textarea.value = textarea.value.substring(0, start) + 
                    text + 
                    textarea.value.substring(end);
    
    // Set cursor position after inserted text
    const newPos = start + text.length;
    textarea.focus();
    textarea.selectionStart = newPos;
    textarea.selectionEnd = newPos;
    textarea.scrollTop = scrollTop;
    } catch (error) {
        console.error('Error inserting text:', error);
    }
}

// Initialize activity form handling
function init() {
    console.log('⚙️ ACTIVITY FORMS - Initialization starting');
    
    // Check if we have the required jQuery and Select2
    if (!window.jQuery || !jQuery.fn.select2) {
        console.error('⚠️ jQuery or Select2 not available, skipping initialization');
        return;
    }
    
    // Set up activity types
    setupActivityTypeCards();
    
    // Initialize CSRF token for AJAX
    setupCSRFToken();
    
    // Initialize all select2 elements
    initializeAllSelect2();
    
    // Initialize activity buttons
    initializeActivityButtons();
    
    // Initialize any to-do toggles
    initializeToDoToggles();
    
    console.log('⚙️ ACTIVITY FORMS - Initialization complete');
}

// Initialize activity buttons
function initializeActivityButtons() {
    const activityTypeCards = document.querySelectorAll('.activity-type-card');
    if (activityTypeCards.length === 0) {
        console.warn('⚠️ No activity type cards found');
        return;
    }
    
    console.log('⚙️ ACTIVITY FORMS - Activity buttons initialized');
    
    // Modal show event handlers
    jQuery('#logActivityModal').on('shown.bs.modal', function() {
        console.log('⚙️ Activity modal shown, initializing Select2');
        initializeAllSelect2();
        setupActivityCardHandlers();
    });
    
    // Initialize activity card handlers right away
    setupActivityCardHandlers();
}

// Document ready function
jQuery(document).ready(function() {
    console.log('Activity forms JS loaded');
    
    // Debug: Check form elements on document ready
    console.log('================== DOCUMENT READY DEBUG ==================');
    console.log('Input elements at document ready:', jQuery('input').length);
    console.log('Select elements at document ready:', jQuery('select').length);
    console.log('Elements with select2-multiple class at document ready:', jQuery('.select2-multiple').length);
    console.log('Elements with name="recipients" at document ready:', jQuery('[name="recipients"]').length);
    
    // If we find an email form, log its structure
    if (jQuery('#email-form').length) {
        console.log('Email form found on page, content:');
        console.log('Fields:', jQuery('#email-form').find('input, select, textarea').length);
        
        jQuery('#email-form').find('input, select, textarea').each(function(index) {
            console.log(`Form field #${index+1}:`, {
                name: jQuery(this).attr('name'),
                id: jQuery(this).attr('id'),
                type: this.type,
                tagName: this.tagName,
                classes: jQuery(this).attr('class')
            });
        });
    }
    console.log('=================== END DEBUG ===================');
    
    // Initialize Select2 for every form
    initBasicSelect2();
    
    // Initialize after any modal is shown
    jQuery('.modal').on('shown.bs.modal', function() {
        console.log('Modal shown, id:', jQuery(this).attr('id'));
        
        // Debug: Check modal contents
        console.log('================== MODAL SHOWN DEBUG ==================');
        console.log('Input elements in modal:', jQuery(this).find('input').length);
        console.log('Select elements in modal:', jQuery(this).find('select').length);
        console.log('Elements with select2-multiple class in modal:', jQuery(this).find('.select2-multiple').length);
        console.log('Elements with name="recipients" in modal:', jQuery(this).find('[name="recipients"]').length);
        
        // Check each form in the modal
        jQuery(this).find('form').each(function(index) {
            console.log(`Form #${index+1} in modal:`, jQuery(this).attr('id'));
            console.log(`Fields in form #${index+1}:`, jQuery(this).find('input, select, textarea').length);
            
            jQuery(this).find('input, select, textarea').each(function(i) {
                console.log(`Field #${i+1} in form #${index+1}:`, {
                    name: jQuery(this).attr('name'),
                    id: jQuery(this).attr('id'),
                    type: this.type,
                    tagName: this.tagName,
                    classes: jQuery(this).attr('class')
                });
            });
        });
        console.log('=================== END MODAL DEBUG ===================');
        
        setTimeout(initBasicSelect2, 100);
    });
    
    // Initialize when activity cards are clicked
    jQuery('.activity-card, .activity-type-card').on('click', function() {
        const formTarget = jQuery(this).data('form-target');
        console.log('Activity card clicked, form target:', formTarget);
        
        // Debug: Check target form 
        console.log('================== CARD CLICK DEBUG ==================');
        if (formTarget && jQuery('#' + formTarget).length) {
            const $form = jQuery('#' + formTarget);
            console.log('Form found:', formTarget);
            console.log('Input elements in form:', $form.find('input').length);
            console.log('Select elements in form:', $form.find('select').length);
            console.log('Elements with select2-multiple class in form:', $form.find('.select2-multiple').length);
            console.log('Elements with name="recipients" in form:', $form.find('[name="recipients"]').length);
            
            // Look at all form fields
            $form.find('input, select, textarea').each(function(i) {
                console.log(`Field #${i+1} in ${formTarget}:`, {
                    name: jQuery(this).attr('name'),
                    id: jQuery(this).attr('id'),
                    type: this.type,
                    tagName: this.tagName,
                    classes: jQuery(this).attr('class')
                });
            });
            
            // Handle form submission to ensure Select2 multiple values are properly included
            $form.off('submit').on('submit', function() {
                console.log('Form is being submitted, ensuring Select2 values are included');
                
                // Make sure Select2 values are in the form data
                jQuery(this).find('.select2-hidden-accessible').each(function() {
                    console.log('Processing Select2 field for form submission:', jQuery(this).attr('name'));
                    console.log('Current value:', jQuery(this).val());
                    
                    // Selected data should already be in the field value
                    // Just log it to confirm
                    const selectedData = jQuery(this).select2('data');
                    if (selectedData && selectedData.length) {
                        console.log('Selected items:', selectedData.length);
                        selectedData.forEach(function(item, index) {
                            console.log(`Item ${index+1}:`, item.id, item.text);
                        });
                    } else {
                        console.log('No items selected');
                    }
                });
                
                return true; // Allow form submission to proceed
            });
        } else {
            console.log('Form not found:', formTarget);
        }
        console.log('=================== END CARD DEBUG ===================');
        
        setTimeout(initBasicSelect2, 100);
    });
});

// Super basic Select2 initialization that works with any select field
function initBasicSelect2() {
    console.log('Running basic Select2 initialization');
    
    // Log all form input elements to help debug
    console.log('All input elements found:', jQuery('input').length);
    console.log('All input[name="recipients"] elements:', jQuery('input[name="recipients"]').length);
    console.log('Any elements with name="recipients":', jQuery('[name="recipients"]').length);
    
    // Check for any elements with select2-multiple class
    console.log('Elements with select2-multiple class:', jQuery('.select2-multiple').length);
    if (jQuery('.select2-multiple').length > 0) {
        jQuery('.select2-multiple').each(function(index) {
            console.log(`Select2 element #${index+1}:`, {
                name: jQuery(this).attr('name'),
                id: jQuery(this).attr('id'),
                type: this.type,
                tagName: this.tagName
            });
        });
    }
    
    // Try to initialize using multiple selectors for maximum coverage
    const $recipientsField = jQuery('input[name="recipients"], select[name="recipients"], .select2-multiple');
    
    if ($recipientsField.length > 0) {
        console.log(`Found ${$recipientsField.length} potential recipients fields to initialize`);
        
        $recipientsField.each(function() {
            try {
                // Skip if already initialized
                if (jQuery(this).hasClass('select2-hidden-accessible')) {
                    console.log('Skipping already initialized element:', jQuery(this).attr('name'));
                    return;
                }
                
                console.log('Initializing element:', {
                    name: jQuery(this).attr('name'),
                    id: jQuery(this).attr('id'),
                    type: this.type,
                    tagName: this.tagName
                });
                
                // First destroy if already attached
                if (jQuery(this).data('select2')) {
                    jQuery(this).select2('destroy');
                }
                
                const $element = jQuery(this);
                const modalParent = $element.closest('.modal');
                
                // Initialize with Bootstrap theme
                $element.select2({
                    theme: 'bootstrap-5',
                    ajax: {
                        url: '/crm/api/search-recipients/',
                        dataType: 'json',
                        data: function(params) {
                            return {
                                term: params.term || '',
                                company_id: jQuery('#company_id').val() || ''
                            };
                        },
                        processResults: function(data) {
                            console.log('Search results:', data);
                            // Fix: Return the expected format with results array
                            if (!data.results) {
                                return { results: [] };
                            }
                            return data; // Server already returns correct format with results property
                        }
                    },
                    templateResult: function(data) {
                        if (data.loading) return data.text;
                        if (!data.id) return data.text;
                        
                        // Format the dropdown items with custom colors
                        const icon = data.type === 'contact' ? 'fa-address-card' : 'fa-user';
                        const colorClass = data.type === 'contact' ? 'icon-contact' : 'icon-user';
                        
                        return jQuery(
                            `<div class="d-flex align-items-center p-1">
                                <i class="fas ${icon} ${colorClass} me-2"></i>
                                <div>
                                    <span class="d-block">${data.text}</span>
                                    <small class="text-muted">${data.type === 'contact' ? 'Contact' : 'User'}</small>
                                </div>
                            </div>`
                        );
                    },
                    templateSelection: function(data) {
                        if (!data.id) return data.text;
                        
                        // Format selected items with custom colored icons and more explicit structure
                        const icon = data.type === 'contact' ? 'fa-address-card' : 'fa-user';
                        const colorClass = data.type === 'contact' ? 'icon-contact' : 'icon-user';
                        
                        return jQuery(
                            `<span class="d-inline-flex align-items-center select2-selection-item">
                                <i class="fas ${icon} ${colorClass} me-1" style="color: ${data.type === 'contact' ? '#444a9f' : '#9c85db'} !important;"></i>
                                <span>${data.text}</span>
                            </span>`
                        );
                    },
                    tags: false,
                    tokenSeparators: [','],
                    minimumInputLength: 2,
                    width: '100%',
                    dropdownPosition: 'below',
                    dropdownParent: modalParent.length ? modalParent : jQuery('body'),
                    language: {
                        noResults: function() {
                            return "No contacts or users found";
                        }
                    }
                }).on('select2:open', function() {
                    // Fix dropdown position after it opens
                    const selectPosition = $(this).offset();
                    const modalScrollTop = $(this).closest('.modal-body').scrollTop();
                    
                    $('.select2-dropdown').css({
                        top: (selectPosition.top - modalScrollTop + $(this).outerHeight()) + 'px',
                        left: selectPosition.left + 'px',
                        width: $(this).outerWidth() + 'px'
                    });
                });
                
                // Add debug event handlers
                $element.on('select2:select', function(e) {
                    console.log('✅ Item selected:', e.params.data);
                    console.log('Current selections:', $element.val());
                    console.log('Raw selection data:', $element.select2('data'));
                });
                
                $element.on('select2:unselect', function(e) {
                    console.log('❌ Item unselected:', e.params.data);
                });
                
                $element.on('select2:opening', function(e) {
                    console.log('⚙️ Dropdown opening');
                });
                
                $element.on('select2:close', function(e) {
                    console.log('⚙️ Dropdown closed');
                });
                
                console.log('Successfully initialized Select2 for:', jQuery(this).attr('name') || 'unnamed element');
            } catch (error) {
                console.error('Error initializing Select2:', error);
            }
        });
    } else {
        console.log('No recipients fields found with any selector');
    }
} 