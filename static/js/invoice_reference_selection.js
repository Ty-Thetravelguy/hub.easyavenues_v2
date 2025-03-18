document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('invoiceReferenceModal');
    
    // Only proceed if the modal exists (should only be for client forms)
    if (!modal) return;
    
    const form = document.getElementById('invoiceReferencesForm');
    const saveButton = document.getElementById('saveInvoiceReferences');
    const displayContainer = document.getElementById('selectedReferencesDisplay');

    // Pre-select existing references when modal opens
    modal.addEventListener('show.bs.modal', function() {
        // Get all existing references from the display container
        const existingRefs = Array.from(displayContainer.querySelectorAll('.badge')).map(badge => {
            const refName = badge.childNodes[0].textContent.trim();
            const isMandatory = badge.querySelector('.badge').textContent.trim() === 'Mandatory';
            return { name: refName, mandatory: isMandatory };
        });

        // Select checkboxes and set dropdown values
        document.querySelectorAll('.reference-checkbox').forEach(checkbox => {
            const row = checkbox.closest('tr');
            const refName = row.querySelector('td:nth-child(2)').textContent.trim();
            const existingRef = existingRefs.find(ref => ref.name === refName);
            
            if (existingRef) {
                checkbox.checked = true;
                const typeSelect = document.getElementById('type_' + checkbox.value);
                typeSelect.disabled = false;
                typeSelect.value = existingRef.mandatory ? 'mandatory' : 'optional';
            } else {
                checkbox.checked = false;
                const typeSelect = document.getElementById('type_' + checkbox.value);
                typeSelect.disabled = true;
                typeSelect.value = 'optional';
            }
        });
    });

    // Enable/disable type dropdown when checkbox is clicked
    document.querySelectorAll('.reference-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const typeSelect = document.getElementById('type_' + this.value);
            typeSelect.disabled = !this.checked;
        });
    });

    // Handle save button click
    saveButton.addEventListener('click', function() {
        const selectedReferences = [];
        const mandatoryReferences = [];
        
        // Remove any existing hidden inputs first
        document.querySelectorAll('input[name="invoice_references"]').forEach(el => el.remove());
        document.querySelectorAll('input[name="mandatory_references"]').forEach(el => el.remove());
        
        // Create new hidden inputs for each selected reference
        document.querySelectorAll('.reference-checkbox:checked').forEach(checkbox => {
            const referenceId = parseInt(checkbox.value);
            const typeSelect = document.getElementById('type_' + referenceId);
            
            // Create hidden input for selected reference
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'invoice_references';
            hiddenInput.value = referenceId;
            document.querySelector('form').appendChild(hiddenInput);
            
            selectedReferences.push(referenceId);
            
            if (typeSelect.value === 'mandatory') {
                // Create hidden input for mandatory reference
                const mandatoryInput = document.createElement('input');
                mandatoryInput.type = 'hidden';
                mandatoryInput.name = 'mandatory_references';
                mandatoryInput.value = referenceId;
                document.querySelector('form').appendChild(mandatoryInput);
                
                mandatoryReferences.push(referenceId);
            }
        });

        // Update the display
        updateDisplay(selectedReferences, mandatoryReferences);

        // Close modal
        const modalInstance = bootstrap.Modal.getInstance(modal);
        modalInstance.hide();
    });

    function updateDisplay(selectedReferences, mandatoryReferences) {
        // Clear current display
        displayContainer.innerHTML = '';
        
        // Add new badges
        selectedReferences.forEach(refId => {
            const referenceElement = document.querySelector(`#reference_${refId}`).closest('tr').querySelector('td:nth-child(2)').textContent;
            const badge = document.createElement('div');
            badge.className = 'badge bg-primary me-1 mb-1';
            badge.innerHTML = `
                ${referenceElement.trim()}
                <span class="badge ${mandatoryReferences.includes(refId) ? 'bg-danger' : 'bg-secondary'} ms-1">
                    ${mandatoryReferences.includes(refId) ? 'Mandatory' : 'Optional'}
                </span>
            `;
            displayContainer.appendChild(badge);
        });
    }
}); 