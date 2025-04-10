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
    
    // Handle invoice reference selection
    const saveInvoiceReferencesBtn = document.getElementById('saveInvoiceReferences');
    if (saveInvoiceReferencesBtn) {
        saveInvoiceReferencesBtn.addEventListener('click', function() {
            const selectedReferences = [];
            const checkboxes = document.querySelectorAll('.reference-checkbox:checked');
            
            checkboxes.forEach(checkbox => {
                const referenceId = checkbox.value;
                const typeSelect = document.getElementById(`type_${referenceId}`);
                const isMandatory = typeSelect.value === 'mandatory';
                
                selectedReferences.push({
                    id: referenceId,
                    is_mandatory: isMandatory
                });
            });
            
            // Update the hidden input
            const selectedReferencesInput = document.getElementById('selectedReferencesInput');
            if (selectedReferencesInput) {
                selectedReferencesInput.value = JSON.stringify(selectedReferences);
            }
            
            // Submit the form
            const form = document.getElementById('invoiceReferencesForm');
            if (form) {
                form.submit();
            }
        });
    }
    
    // Handle reference checkbox changes
    const referenceCheckboxes = document.querySelectorAll('.reference-checkbox');
    referenceCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const referenceId = this.value;
            const typeSelect = document.getElementById(`type_${referenceId}`);
            
            if (typeSelect) {
                typeSelect.disabled = !this.checked;
            }
        });
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
    
    const teamSelect = document.getElementById('teamSelect');
    const teamMembersSection = document.getElementById('teamMembersSection');
    const teamMembersTableBody = document.getElementById('teamMembersTableBody');
    const teamMemberRowTemplate = document.getElementById('teamMemberRowTemplate');
    const selectedUserIdInput = document.getElementById('selected_user_id');
    const selectUserBtn = document.getElementById('selectUserBtn');
    
    // Target input and display elements for the user selection
    let targetInputId = null;
    let targetDisplayId = null;
    
    // Handle team selection
    if (teamSelect) {
        teamSelect.addEventListener('change', function() {
            const teamId = this.value;
            
            if (!teamId) {
                teamMembersSection.classList.add('d-none');
                selectUserBtn.disabled = true;
                return;
            }
            
            // Fetch team members
            fetch(`/accounts/api/teams/${teamId}/members/`)
                .then(response => response.json())
                .then(data => {
                    // Clear existing rows
                    teamMembersTableBody.innerHTML = '';
                    
                    // Add new rows
                    data.forEach(member => {
                        const template = teamMemberRowTemplate.content.cloneNode(true);
                        const row = template.querySelector('tr');
                        const radio = row.querySelector('input[type="radio"]');
                        const nameCell = row.querySelector('.member-name');
                        const roleCell = row.querySelector('.member-role');
                        
                        radio.value = member.id;
                        nameCell.textContent = member.full_name;
                        roleCell.textContent = member.role;
                        
                        // Add event listener to radio button
                        radio.addEventListener('change', function() {
                            if (this.checked) {
                                selectedUserIdInput.value = this.value;
                                selectUserBtn.disabled = false;
                            }
                        });
                        
                        teamMembersTableBody.appendChild(row);
                    });
                    
                    // Show the team members section
                    teamMembersSection.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('Error fetching team members:', error);
                    teamMembersSection.classList.add('d-none');
                });
        });
    }
    
    // Handle user selection button
    if (selectUserBtn) {
        selectUserBtn.addEventListener('click', function() {
            const userId = selectedUserIdInput.value;
            if (!userId) return;
            
            // Get the selected user's name from the table
            const selectedRadio = teamMembersTableBody.querySelector('input[type="radio"]:checked');
            if (selectedRadio) {
                const userName = selectedRadio.closest('tr').querySelector('.member-name').textContent;
                
                // Update the target input and display
                if (targetInputId && targetDisplayId) {
                    const targetInput = document.getElementById(targetInputId);
                    const targetDisplay = document.getElementById(targetDisplayId);
                    
                    if (targetInput && targetDisplay) {
                        targetInput.value = userId;
                        targetDisplay.value = userName;
                    }
                }
            }
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('teamSelectionModal'));
            if (modal) {
                modal.hide();
            }
        });
    }
    
    // Handle modal open event to set target elements
    const teamSelectionModal = document.getElementById('teamSelectionModal');
    if (teamSelectionModal) {
        teamSelectionModal.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            if (button) {
                targetInputId = button.getAttribute('data-target-input');
                targetDisplayId = button.getAttribute('data-target-display');
                
                // Reset form
                teamSelect.value = '';
                teamMembersSection.classList.add('d-none');
                selectedUserIdInput.value = '';
                selectUserBtn.disabled = true;
            }
        });
    }
} 