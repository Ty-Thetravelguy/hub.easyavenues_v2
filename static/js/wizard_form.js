document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Handle form submission
        form.addEventListener('submit', function(event) {
            // Don't validate if it's the previous button
            if (event.submitter && event.submitter.name === 'wizard_goto_step') {
                return;
            }

            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });

        // Add Bootstrap classes to form fields
        const formControls = form.querySelectorAll('input:not([type="radio"]), select, textarea');
        formControls.forEach(element => {
            element.classList.add('form-control');
        });

        // Handle radio button changes
        const radioButtons = form.querySelectorAll('input[type="radio"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                // Remove any validation styling when a selection is made
                form.classList.remove('was-validated');
                const feedback = radio.closest('.mb-3').querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.style.display = 'none';
                }
            });
        });
    });
}); 