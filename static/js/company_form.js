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
}); 