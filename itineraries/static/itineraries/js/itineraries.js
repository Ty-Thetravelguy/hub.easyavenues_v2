document.addEventListener('DOMContentLoaded', function() {
    // Auto-show PNR import modal if no segments exist
    const timeline = document.querySelector('.timeline');
    if (!timeline) {
        const importModal = document.getElementById('importPNRModal');
        if (importModal) {
            new bootstrap.Modal(importModal).show();
        }
    }

    // Setup PNR import handler
    const importButton = document.getElementById('importPNRButton');
    if (importButton) {
        importButton.addEventListener('click', handlePNRImport);
    }
});

function handlePNRImport() {
    const pnrLocator = document.getElementById('pnrLocator').value;
    if (!pnrLocator) return;

    const tripId = document.querySelector('[data-trip-id]').dataset.tripId;

    fetch(`/itineraries/import-pnr/${tripId}/${pnrLocator}/`)
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                window.location.reload();  // Reload to show new segments
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            alert('Error importing PNR: ' + error);
        });
}