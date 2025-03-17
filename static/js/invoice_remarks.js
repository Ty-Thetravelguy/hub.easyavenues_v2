document.addEventListener('DOMContentLoaded', function() {
    // Handle checkbox changes
    document.querySelectorAll('.remark-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const remarkId = this.value;
            const typeSelect = document.getElementById(`type_${remarkId}`);
            typeSelect.disabled = !this.checked;
        });
    });

    // Handle save button click
    document.getElementById('saveInvoiceRemarks').addEventListener('click', function() {
        const selectedRemarks = [];
        document.querySelectorAll('.remark-checkbox:checked').forEach(checkbox => {
            const remarkId = checkbox.value;
            const typeSelect = document.getElementById(`type_${remarkId}`);
            selectedRemarks.push({
                id: remarkId,
                is_mandatory: typeSelect.value === 'mandatory'
            });
        });

        // Update hidden input with selected remarks data
        document.getElementById('selectedRemarksInput').value = JSON.stringify(selectedRemarks);
        
        // Submit the form
        document.getElementById('invoiceRemarksForm').submit();
    });
}); 