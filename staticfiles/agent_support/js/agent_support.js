document.addEventListener('DOMContentLoaded', function() {
    // Websites handling
    const websitesContainer = document.getElementById('websites-container');
    const addWebsiteButton = websitesContainer.querySelector('.add-website');

    addWebsiteButton.addEventListener('click', function() {
        const newEntry = document.createElement('div');
        newEntry.className = 'website-entry mb-2';
        newEntry.innerHTML = `
            <div class="row">
                <div class="col-md-5">
                    <input type="url" class="form-control website-url" 
                           placeholder="Enter website URL">
                    <div class="form-text">Enter the website URL (e.g., https://example.com)</div>
                </div>
                <div class="col-md-5">
                    <input type="text" class="form-control website-description" 
                           placeholder="Enter description">
                    <div class="form-text">Enter a description for this website</div>
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-website">
                        <i class="fas fa-minus"></i>
                    </button>
                </div>
            </div>
        `;
        websitesContainer.appendChild(newEntry);
    });

    // Phone numbers handling
    const phonesContainer = document.getElementById('phones-container');
    const addPhoneButton = phonesContainer.querySelector('.add-phone');

    addPhoneButton.addEventListener('click', function() {
        const newEntry = document.createElement('div');
        newEntry.className = 'phone-entry mb-2';
        newEntry.innerHTML = `
            <div class="row">
                <div class="col-md-5">
                    <input type="tel" class="form-control phone-number" 
                           placeholder="Enter phone number">
                    <div class="form-text">Enter the phone number (e.g., +44 123 456 7890)</div>
                </div>
                <div class="col-md-5">
                    <input type="text" class="form-control phone-description" 
                           placeholder="Enter description">
                    <div class="form-text">Enter a description for this number</div>
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-phone">
                        <i class="fas fa-minus"></i>
                    </button>
                </div>
            </div>
        `;
        phonesContainer.appendChild(newEntry);
    });

    // Email addresses handling
    const emailsContainer = document.getElementById('emails-container');
    const addEmailButton = emailsContainer.querySelector('.add-email');

    addEmailButton.addEventListener('click', function() {
        const newEntry = document.createElement('div');
        newEntry.className = 'email-entry mb-2';
        newEntry.innerHTML = `
            <div class="row">
                <div class="col-md-5">
                    <input type="email" class="form-control email-address" 
                           placeholder="Enter email address">
                    <div class="form-text">Enter the email address</div>
                </div>
                <div class="col-md-5">
                    <input type="text" class="form-control email-description" 
                           placeholder="Enter description">
                    <div class="form-text">Enter a description for this email</div>
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-email">
                        <i class="fas fa-minus"></i>
                    </button>
                </div>
            </div>
        `;
        emailsContainer.appendChild(newEntry);
    });

    // Remove handlers
    document.addEventListener('click', function(e) {
        if (e.target.closest('.remove-website')) {
            e.target.closest('.website-entry').remove();
        }
        if (e.target.closest('.remove-phone')) {
            e.target.closest('.phone-entry').remove();
        }
        if (e.target.closest('.remove-email')) {
            e.target.closest('.email-entry').remove();
        }
    });

    // Form submission
    document.querySelector('form').addEventListener('submit', function(e) {
        e.preventDefault();

        // Collect websites
        const websites = [];
        document.querySelectorAll('.website-entry').forEach(entry => {
            const url = entry.querySelector('.website-url').value;
            const description = entry.querySelector('.website-description').value;
            if (url && description) {
                websites.push({ url, description });
            }
        });

        // Collect phone numbers
        const phones = [];
        document.querySelectorAll('.phone-entry').forEach(entry => {
            const number = entry.querySelector('.phone-number').value;
            const description = entry.querySelector('.phone-description').value;
            if (number && description) {
                phones.push({ number, description });
            }
        });

        // Collect email addresses
        const emails = [];
        document.querySelectorAll('.email-entry').forEach(entry => {
            const email = entry.querySelector('.email-address').value;
            const description = entry.querySelector('.email-description').value;
            if (email && description) {
                emails.push({ email, description });
            }
        });

        // Add to hidden fields
        const websitesInput = document.createElement('input');
        websitesInput.type = 'hidden';
        websitesInput.name = 'agent_websites';
        websitesInput.value = JSON.stringify(websites);
        this.appendChild(websitesInput);

        const phonesInput = document.createElement('input');
        phonesInput.type = 'hidden';
        phonesInput.name = 'contact_phone';
        phonesInput.value = JSON.stringify(phones);
        this.appendChild(phonesInput);

        const emailsInput = document.createElement('input');
        emailsInput.type = 'hidden';
        emailsInput.name = 'general_email';
        emailsInput.value = JSON.stringify(emails);
        this.appendChild(emailsInput);

        this.submit();
    });
});