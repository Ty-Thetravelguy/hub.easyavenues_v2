// Form functionality for Easy Avenues CRM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Easy Avenues CRM - Initializing forms.js');
    
    // Initialize company form
    initializeCompanyForm();
    
    // Initialize travel policy form
    initializeTravelPolicyForm();
    
    // Initialize wizard form
    initializeWizardForm();
    
    // Initialize invoice reference selection
    initializeInvoiceReferenceSelection();
    
    // Initialize team selection
    initializeTeamSelection();
});

// ======================================================
// Company Form
// ======================================================

/**
 * Initialize company form
 */
function initializeCompanyForm() {
    const companyForm = document.getElementById('company-form');
    if (!companyForm) return;
    
    console.log('🔄 Initializing company form');
    
    // Initialize any Select2 elements
    if (typeof jQuery !== 'undefined' && typeof jQuery.fn.select2 !== 'undefined') {
        jQuery('.select2-field').select2({
            width: '100%',
            placeholder: 'Select an option'
        });
    }
    
    // Handle dynamic address fields
    const addressSameCheckbox = document.getElementById('address_same');
    const billingAddressFields = document.getElementById('billing-address-fields');
    
    if (addressSameCheckbox && billingAddressFields) {
        // Initialize visibility based on current state
        billingAddressFields.style.display = addressSameCheckbox.checked ? 'none' : 'block';
        
        // Add change handler
        addressSameCheckbox.addEventListener('change', function() {
            billingAddressFields.style.display = this.checked ? 'none' : 'block';
        });
    }
    
    // Handle form submission
    companyForm.addEventListener('submit', function(e) {
        // Perform custom validation if needed
        const isValid = validateCompanyForm();
        
        if (!isValid) {
            e.preventDefault();
            return false;
        }
        
        // If address_same is checked, copy shipping address to billing address
        if (addressSameCheckbox && addressSameCheckbox.checked) {
            const shippingAddress1 = document.getElementById('shipping_address_line1');
            const shippingAddress2 = document.getElementById('shipping_address_line2');
            const shippingCity = document.getElementById('shipping_city');
            const shippingPostalCode = document.getElementById('shipping_postal_code');
            const shippingCountry = document.getElementById('shipping_country');
            
            const billingAddress1 = document.getElementById('billing_address_line1');
            const billingAddress2 = document.getElementById('billing_address_line2');
            const billingCity = document.getElementById('billing_city');
            const billingPostalCode = document.getElementById('billing_postal_code');
            const billingCountry = document.getElementById('billing_country');
            
            if (shippingAddress1 && billingAddress1) billingAddress1.value = shippingAddress1.value;
            if (shippingAddress2 && billingAddress2) billingAddress2.value = shippingAddress2.value;
            if (shippingCity && billingCity) billingCity.value = shippingCity.value;
            if (shippingPostalCode && billingPostalCode) billingPostalCode.value = shippingPostalCode.value;
            if (shippingCountry && billingCountry) billingCountry.value = shippingCountry.value;
        }
    });
}

/**
 * Validate company form
 */
function validateCompanyForm() {
    const companyForm = document.getElementById('company-form');
    if (!companyForm) return true;
    
    let isValid = true;
    
    // Reset previous error messages
    const errorMsgs = companyForm.querySelectorAll('.invalid-feedback');
    errorMsgs.forEach(function(msg) {
        msg.style.display = 'none';
    });
    
    // Reset previous invalid fields
    const invalidFields = companyForm.querySelectorAll('.is-invalid');
    invalidFields.forEach(function(field) {
        field.classList.remove('is-invalid');
    });
    
    // Required fields validation
    const requiredFields = companyForm.querySelectorAll('[required]');
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            
            // Show custom error message if it exists
            const customError = document.getElementById(`${field.id}-error`);
            if (customError) {
                customError.style.display = 'block';
            }
            
            isValid = false;
        }
    });
    
    // Email validation
    const emailField = document.getElementById('email');
    if (emailField && emailField.value.trim()) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailField.value.trim())) {
            emailField.classList.add('is-invalid');
            
            // Show custom error message if it exists
            const customError = document.getElementById('email-error');
            if (customError) {
                customError.style.display = 'block';
                customError.textContent = 'Please enter a valid email address.';
            }
            
            isValid = false;
        }
    }
    
    return isValid;
}

// ======================================================
// Travel Policy Form
// ======================================================

/**
 * Initialize travel policy form
 */
function initializeTravelPolicyForm() {
    const travelPolicyForm = document.getElementById('travel-policy-form');
    if (!travelPolicyForm) return;
    
    console.log('🔄 Initializing travel policy form');
    
    // Initialize Select2 for service type
    if (typeof jQuery !== 'undefined' && typeof jQuery.fn.select2 !== 'undefined') {
        jQuery('#service_type').select2({
            width: '100%',
            placeholder: 'Select service type'
        });
        
        // Update form fields based on service type
        jQuery('#service_type').on('change', function() {
            const serviceType = jQuery(this).val();
            updateTravelPolicyFormFields(serviceType);
        });
        
        // Initialize form fields for current service type
        const currentServiceType = jQuery('#service_type').val();
        if (currentServiceType) {
            updateTravelPolicyFormFields(currentServiceType);
        }
    }
    
    // Add datepicker to date fields
    const dateFields = document.querySelectorAll('input[data-datepicker]');
    if (dateFields.length && typeof flatpickr !== 'undefined') {
        dateFields.forEach(input => {
            flatpickr(input, {
                dateFormat: "Y-m-d",
                allowInput: true
            });
        });
    }
}

/**
 * Update travel policy form fields based on service type
 */
function updateTravelPolicyFormFields(serviceType) {
    // Hide all service-specific fields first
    document.querySelectorAll('.service-field').forEach(field => {
        field.style.display = 'none';
    });
    
    // Show fields relevant to selected service type
    if (serviceType === 'air') {
        document.querySelectorAll('.air-field').forEach(field => {
            field.style.display = 'block';
        });
    } else if (serviceType === 'rail') {
        document.querySelectorAll('.rail-field').forEach(field => {
            field.style.display = 'block';
        });
    } else if (serviceType === 'hotel') {
        document.querySelectorAll('.hotel-field').forEach(field => {
            field.style.display = 'block';
        });
    } else if (serviceType === 'car') {
        document.querySelectorAll('.car-field').forEach(field => {
            field.style.display = 'block';
        });
    }
}

// ======================================================
// Wizard Form
// ======================================================

/**
 * Initialize wizard form
 */
function initializeWizardForm() {
    const wizardForm = document.getElementById('wizard-form');
    if (!wizardForm) return;
    
    console.log('🔄 Initializing wizard form');
    
    // Track current step
    let currentStep = 1;
    const totalSteps = document.querySelectorAll('.wizard-step').length;
    
    // Initialize step indicators
    updateStepIndicators(currentStep);
    
    // Handle next button clicks
    const nextButtons = document.querySelectorAll('.wizard-next');
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Validate current step
            if (validateWizardStep(currentStep)) {
                // Hide current step
                document.querySelector(`.wizard-step[data-step="${currentStep}"]`).style.display = 'none';
                
                // Show next step
                currentStep++;
                document.querySelector(`.wizard-step[data-step="${currentStep}"]`).style.display = 'block';
                
                // Update step indicators
                updateStepIndicators(currentStep);
                
                // Scroll to top of form
                wizardForm.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Handle previous button clicks
    const prevButtons = document.querySelectorAll('.wizard-prev');
    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Hide current step
            document.querySelector(`.wizard-step[data-step="${currentStep}"]`).style.display = 'none';
            
            // Show previous step
            currentStep--;
            document.querySelector(`.wizard-step[data-step="${currentStep}"]`).style.display = 'block';
            
            // Update step indicators
            updateStepIndicators(currentStep);
            
            // Scroll to top of form
            wizardForm.scrollIntoView({ behavior: 'smooth' });
        });
    });
    
    // Handle form submission
    wizardForm.addEventListener('submit', function(e) {
        // Validate final step
        if (!validateWizardStep(currentStep)) {
            e.preventDefault();
            return false;
        }
    });
}

/**
 * Update wizard step indicators
 */
function updateStepIndicators(currentStep) {
    const indicators = document.querySelectorAll('.wizard-indicator');
    
    indicators.forEach((indicator, index) => {
        const stepNum = index + 1;
        
        if (stepNum < currentStep) {
            // Completed steps
            indicator.classList.remove('active', 'upcoming');
            indicator.classList.add('completed');
        } else if (stepNum === currentStep) {
            // Current step
            indicator.classList.remove('completed', 'upcoming');
            indicator.classList.add('active');
        } else {
            // Upcoming steps
            indicator.classList.remove('completed', 'active');
            indicator.classList.add('upcoming');
        }
    });
}

/**
 * Validate wizard form step
 */
function validateWizardStep(step) {
    const stepElement = document.querySelector(`.wizard-step[data-step="${step}"]`);
    if (!stepElement) return true;
    
    let isValid = true;
    
    // Reset previous error messages
    const errorMsgs = stepElement.querySelectorAll('.invalid-feedback');
    errorMsgs.forEach(function(msg) {
        msg.style.display = 'none';
    });
    
    // Reset previous invalid fields
    const invalidFields = stepElement.querySelectorAll('.is-invalid');
    invalidFields.forEach(function(field) {
        field.classList.remove('is-invalid');
    });
    
    // Required fields validation for this step
    const requiredFields = stepElement.querySelectorAll('[required]');
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            
            // Show custom error message if it exists
            const customError = document.getElementById(`${field.id}-error`);
            if (customError) {
                customError.style.display = 'block';
            }
            
            isValid = false;
        }
    });
    
    // Email validation
    const emailFields = stepElement.querySelectorAll('input[type="email"]');
    emailFields.forEach(function(field) {
        if (field.value.trim()) {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(field.value.trim())) {
                field.classList.add('is-invalid');
                
                // Show custom error message if it exists
                const customError = document.getElementById(`${field.id}-error`);
                if (customError) {
                    customError.style.display = 'block';
                    customError.textContent = 'Please enter a valid email address.';
                }
                
                isValid = false;
            }
        }
    });
    
    return isValid;
}

// ======================================================
// Invoice Reference Selection
// ======================================================

/**
 * Initialize invoice reference selection
 */
function initializeInvoiceReferenceSelection() {
    const invoiceReferenceForm = document.getElementById('invoice-reference-form');
    if (!invoiceReferenceForm) return;
    
    console.log('🔄 Initializing invoice reference selection');
    
    // Initialize Select2 for reference selection
    if (typeof jQuery !== 'undefined' && typeof jQuery.fn.select2 !== 'undefined') {
        jQuery('#reference_type').select2({
            width: '100%',
            placeholder: 'Select reference type'
        });
        
        // Update form fields based on reference type
        jQuery('#reference_type').on('change', function() {
            const referenceType = jQuery(this).val();
            updateReferenceFields(referenceType);
        });
        
        // Initialize fields for current reference type
        const currentReferenceType = jQuery('#reference_type').val();
        if (currentReferenceType) {
            updateReferenceFields(currentReferenceType);
        }
    }
    
    // Handle form submission
    invoiceReferenceForm.addEventListener('submit', function(e) {
        const isValid = validateReferenceForm();
        
        if (!isValid) {
            e.preventDefault();
            return false;
        }
    });
}

/**
 * Update invoice reference fields based on type
 */
function updateReferenceFields(referenceType) {
    // Hide all reference fields first
    document.querySelectorAll('.reference-field').forEach(field => {
        field.style.display = 'none';
    });
    
    // Show fields relevant to selected reference type
    if (referenceType === 'po') {
        document.querySelectorAll('.po-field').forEach(field => {
            field.style.display = 'block';
        });
    } else if (referenceType === 'cost_center') {
        document.querySelectorAll('.cost-center-field').forEach(field => {
            field.style.display = 'block';
        });
    } else if (referenceType === 'project') {
        document.querySelectorAll('.project-field').forEach(field => {
            field.style.display = 'block';
        });
    }
}

/**
 * Validate invoice reference form
 */
function validateReferenceForm() {
    const form = document.getElementById('invoice-reference-form');
    if (!form) return true;
    
    const referenceType = document.getElementById('reference_type').value;
    if (!referenceType) {
        document.getElementById('reference_type').classList.add('is-invalid');
        return false;
    }
    
    let isValid = true;
    
    // Reset previous error states
    form.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    // Validate visible required fields
    const visibleFields = form.querySelectorAll('.reference-field[style*="block"] [required]');
    visibleFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    return isValid;
}

// ======================================================
// Team Selection
// ======================================================

/**
 * Initialize team selection
 */
function initializeTeamSelection() {
    const teamSelectionForm = document.getElementById('team-selection-form');
    if (!teamSelectionForm) return;
    
    console.log('🔄 Initializing team selection');
    
    // Initialize Select2 for team members
    if (typeof jQuery !== 'undefined' && typeof jQuery.fn.select2 !== 'undefined') {
        jQuery('#team_members').select2({
            width: '100%',
            placeholder: 'Select team members',
            tags: false,
            multiple: true,
            ajax: {
                url: '/users/search/',
                dataType: 'json',
                delay: 250,
                data: function(params) {
                    return {
                        q: params.term || '',
                        page: params.page || 1
                    };
                },
                processResults: function(data, params) {
                    params.page = params.page || 1;
                    
                    return {
                        results: data.results,
                        pagination: {
                            more: (params.page * 10) < data.count
                        }
                    };
                },
                cache: true
            },
            templateResult: formatUserResult,
            templateSelection: formatUserSelection
        });
    }
    
    // Handle form submission
    teamSelectionForm.addEventListener('submit', function(e) {
        const isValid = validateTeamForm();
        
        if (!isValid) {
            e.preventDefault();
            return false;
        }
    });
}

/**
 * Format user search result
 */
function formatUserResult(user) {
    if (user.loading) return user.text;
    
    return jQuery(`
        <div class="select2-result-user">
            <div>
                <strong>${user.name}</strong>
            </div>
            <div class="text-muted small">
                <i class="fas fa-envelope me-1"></i> ${user.email}
                ${user.department ? `<span class="ms-2"><i class="fas fa-building me-1"></i> ${user.department}</span>` : ''}
            </div>
        </div>
    `);
}

/**
 * Format user selection
 */
function formatUserSelection(user) {
    return user.name || user.text;
}

/**
 * Validate team selection form
 */
function validateTeamForm() {
    const form = document.getElementById('team-selection-form');
    if (!form) return true;
    
    const teamMembers = document.getElementById('team_members');
    if (teamMembers && teamMembers.required && !teamMembers.value) {
        teamMembers.classList.add('is-invalid');
        return false;
    }
    
    return true;
} 