document.addEventListener('DOMContentLoaded', function() {
    const companyTypeSelect = document.querySelector('.company-type-select');
    if (!companyTypeSelect) return;

    const clientFields = companyTypeSelect.dataset.clientFields.split(',');
    const supplierFields = companyTypeSelect.dataset.supplierFields.split(',');

    function toggleFields(type) {
        // Hide all specific fields first
        [...clientFields, ...supplierFields].forEach(field => {
            const fieldElement = document.querySelector(`[name="${field}"]`);
            if (fieldElement) {
                const formGroup = fieldElement.closest('.form-group');
                if (formGroup) {
                    formGroup.style.display = 'none';
                }
            }
        });

        // Show fields based on selected type
        const fieldsToShow = type === 'Client' ? clientFields : supplierFields;
        fieldsToShow.forEach(field => {
            const fieldElement = document.querySelector(`[name="${field}"]`);
            if (fieldElement) {
                const formGroup = fieldElement.closest('.form-group');
                if (formGroup) {
                    formGroup.style.display = 'block';
                }
            }
        });
    }

    // Initial toggle based on current value
    toggleFields(companyTypeSelect.value);

    // Toggle on change
    companyTypeSelect.addEventListener('change', (e) => {
        toggleFields(e.target.value);
    });

    // Add Bootstrap validation classes to form fields
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            // Check if the clicked button was the Previous button
            const submitButton = document.activeElement;
            if (submitButton && submitButton.name === 'wizard_goto_step') {
                return; // Skip validation for Previous button
            }
            
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Add Bootstrap classes to form fields
    const formControls = document.querySelectorAll('input:not([type="checkbox"]), select, textarea');
    formControls.forEach(element => {
        if (!element.classList.contains('form-check-input')) {
            element.classList.add('form-control');
        }
    });

    // Configure the select user button with the correct target elements
    const selectUserBtn = document.getElementById('selectUserBtn');
    const selectUserBtns = document.querySelectorAll('[data-bs-target="#teamSelectionModal"]');
    
    selectUserBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            selectUserBtn.dataset.targetInput = btn.dataset.targetInput;
            selectUserBtn.dataset.targetDisplay = btn.dataset.targetDisplay;
        });
    });

    // Handle invoice reference selection
    const referenceCheckboxes = document.querySelectorAll('input[name="invoice_reference_options"]');
    referenceCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const mandatoryCheckbox = document.getElementById('mandatory_' + this.id);
            if (mandatoryCheckbox) {
                mandatoryCheckbox.disabled = !this.checked;
                if (!this.checked) {
                    mandatoryCheckbox.checked = false;
                }
            }
        });
    });

    // Initialize mandatory checkboxes state
    referenceCheckboxes.forEach(checkbox => {
        const mandatoryCheckbox = document.getElementById('mandatory_' + checkbox.id);
        if (mandatoryCheckbox) {
            mandatoryCheckbox.disabled = !checkbox.checked;
        }
    });
}); 