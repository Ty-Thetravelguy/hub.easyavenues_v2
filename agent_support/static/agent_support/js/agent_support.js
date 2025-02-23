document.addEventListener('DOMContentLoaded', function() {
    // Add new entry (updated to include notes)
    document.querySelectorAll('.add-phone, .add-email, .add-website, .add-note').forEach(button => {
        button.addEventListener('click', function() {
            const container = this.closest('div');
            const type = this.classList.contains('add-phone') ? 'phone' : 
                        this.classList.contains('add-email') ? 'email' : 
                        this.classList.contains('add-website') ? 'website' : 'note';
            
            const newEntry = document.createElement('div');
            newEntry.className = `${type}-entry mb-2`;
            newEntry.innerHTML = getEntryHTML(type);
            
            container.insertBefore(newEntry, this);
        });
    });

    // Remove entry (updated to include notes)
    document.addEventListener('click', function(e) {
        if (e.target.closest('.remove-entry')) {
            const entry = e.target.closest('.note-entry');
            if (entry) {
                const textarea = entry.querySelector('.tinymce-editor');
                if (textarea) {
                    const editor = tinymce.get(textarea.id);
                    if (editor) {
                        editor.remove();
                    }
                }
            }
            e.target.closest('.phone-entry, .email-entry, .website-entry, .note-entry').remove();
        }
    });
});

function getEntryHTML(type) {
    const templates = {
        phone: `
            <div class="row">
                <div class="col-md-5">
                    <input type="tel" name="phone_number[]" class="form-control" placeholder="Enter phone number">
                    <div class="form-text">Enter the phone number (e.g., +44 123 456 7890)</div>
                </div>
                <div class="col-md-5">
                    <input type="text" name="phone_description[]" class="form-control" placeholder="Enter description">
                    <div class="form-text">Enter a description for this number</div>
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-entry">
                        <i class="fas fa-minus"></i>
                    </button>
                </div>
            </div>
        `,
        email: `
            <div class="row">
                <div class="col-md-5">
                    <input type="email" name="email_address[]" class="form-control" placeholder="Enter email address">
                    <div class="form-text">Enter the email address</div>
                </div>
                <div class="col-md-5">
                    <input type="text" name="email_description[]" class="form-control" placeholder="Enter description">
                    <div class="form-text">Enter a description for this email</div>
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-entry">
                        <i class="fas fa-minus"></i>
                    </button>
                </div>
            </div>
        `,
        website: `
            <div class="row">
                <div class="col-md-5">
                    <input type="url" name="website_url[]" class="form-control" placeholder="Enter website URL">
                    <div class="form-text">Enter the website URL (e.g., https://example.com)</div>
                </div>
                <div class="col-md-5">
                    <input type="text" name="website_description[]" class="form-control" placeholder="Enter description">
                    <div class="form-text">Enter a description for this website</div>
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-entry">
                        <i class="fas fa-minus"></i>
                    </button>
                </div>
            </div>
        `,
        note: `
            <div class="row">
                <div class="col-md-11">
                    <textarea name="note_text[]" class="tinymce-editor" 
                        placeholder="Enter additional note about the supplier"
                        rows="3"></textarea>
                    <div class="form-text">Add any relevant information about this supplier</div>
                </div>
                <div class="col-md-1">
                    <button type="button" class="btn btn-danger remove-entry">
                        <i class="fas fa-minus"></i>
                    </button>
                </div>
            </div>
        `
    };
    return templates[type];
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize TinyMCE for existing textareas
    tinymce.init({
        selector: '.tinymce-editor',
        height: 200,
        menubar: false,
        plugins: 'lists link autolink',
        toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | link',
        content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; }',
    });

    // Initialize TinyMCE for dynamically added textareas
    document.querySelectorAll('.add-note').forEach(button => {
        button.addEventListener('click', function() {
            setTimeout(() => {
                tinymce.init({
                    selector: '.tinymce-editor:not(.tinymce-active)',
                    height: 200,
                    menubar: false,
                    plugins: 'lists link autolink',
                    toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | link',
                    content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; }',
                    setup: function(editor) {
                        editor.on('init', function() {
                            editor.getElement().classList.add('tinymce-active');
                        });
                    }
                });
            }, 0);
        });
    });
});