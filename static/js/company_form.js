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
    const formControls = document.querySelectorAll('input:not(.btn-check), select, textarea');
    formControls.forEach(element => {
        if (!element.classList.contains('form-check-input')) {
            element.classList.add('form-control');
        }
    });

    // Configure the select user button with the correct target elements
    const selectUserBtn = document.getElementById('selectUserBtn');
    const selectManagerBtn = document.querySelector('[data-bs-target="#teamSelectionModal"]');
    
    if (selectManagerBtn) {
        selectManagerBtn.addEventListener('click', () => {
            selectUserBtn.dataset.targetInput = selectManagerBtn.dataset.targetInput;
            selectUserBtn.dataset.targetDisplay = selectManagerBtn.dataset.targetDisplay;
        });
    }
}); 