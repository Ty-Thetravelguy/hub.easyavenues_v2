// Initialize PDF.js worker
if (typeof pdfjsLib !== 'undefined') {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
}

// Helper function to return the entry HTML templates
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
                    <input type="hidden" name="note_created_by[]" value="${document.querySelector('input[name="note_created_by[]"]')?.value || ''}">
                    <input type="hidden" name="note_created_at[]" value="">
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
    /* --- Add New Entry Functionality --- */
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

            // Initialize TinyMCE for new note entries
            if (type === 'note') {
                const textarea = newEntry.querySelector('.tinymce-editor');
                if (textarea) {
                    tinymce.init({
                        target: textarea,
                        height: 200,
                        menubar: false,
                        plugins: 'lists link autolink',
                        toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | link',
                        content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; }'
                    });
                }
            }
        });
    });

    /* --- Remove Entry Functionality --- */
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

    /* --- Form Submission --- */
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // Collect websites
            const websites = [];
            document.querySelectorAll('.website-entry').forEach(entry => {
                const url = entry.querySelector('input[name="website_url[]"]')?.value;
                const description = entry.querySelector('input[name="website_description[]"]')?.value;
                if (url && description) {
                    websites.push({ url, description });
                }
            });

            // Collect phone numbers
            const phones = [];
            document.querySelectorAll('.phone-entry').forEach(entry => {
                const number = entry.querySelector('input[name="phone_number[]"]')?.value;
                const description = entry.querySelector('input[name="phone_description[]"]')?.value;
                if (number && description) {
                    phones.push({ number, description });
                }
            });

            // Collect email addresses
            const emails = [];
            document.querySelectorAll('.email-entry').forEach(entry => {
                const email = entry.querySelector('input[name="email_address[]"]')?.value;
                const description = entry.querySelector('input[name="email_description[]"]')?.value;
                if (email && description) {
                    emails.push({ email, description });
                }
            });

            // Collect notes
            const notes = [];
            document.querySelectorAll('.note-entry').forEach(entry => {
                const textarea = entry.querySelector('.tinymce-editor');
                if (textarea) {
                    const editor = tinymce.get(textarea.id);
                    if (editor) {
                        const note = editor.getContent();
                        if (note) {
                            const createdBy = entry.querySelector('input[name="note_created_by[]"]')?.value;
                            const createdAt = entry.querySelector('input[name="note_created_at[]"]')?.value;
                            
                            // Format the date if it exists, otherwise use current date
                            const date = createdAt ? new Date(createdAt) : new Date();
                            const formattedDate = date.toLocaleDateString('en-GB', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            });

                            notes.push({
                                note: note,
                                created_by: createdBy || document.querySelector('input[name="note_created_by[]"]')?.value || '',
                                created_at: formattedDate
                            });
                        }
                    }
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

            const notesInput = document.createElement('input');
            notesInput.type = 'hidden';
            notesInput.name = 'other_notes';
            notesInput.value = JSON.stringify(notes);
            this.appendChild(notesInput);

            // Submit the form
            this.submit();
        });
    }

    /* --- TinyMCE Initialization for Existing Textareas --- */
    if (typeof tinymce !== 'undefined') {
        tinymce.init({
            selector: '.tinymce-editor',
            height: 200,
            menubar: false,
            plugins: 'lists link autolink',
            toolbar: 'undo redo | formatselect | bold italic | alignleft aligncenter alignright | bullist numlist | link',
            content_style: 'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 14px; }'
        });
    }

    /* --- Supplier Filtering Functionality --- */
    const nameFilter = document.getElementById("supplierNameFilter");
    const typeFilter = document.getElementById("supplierTypeFilter");

    if (nameFilter && typeFilter) {
        const accordionItems = document.querySelectorAll(".accordion-item");

        function filterSuppliers() {
            const searchTerm = nameFilter.value.toLowerCase();
            const selectedType = typeFilter.value.toLowerCase();

            accordionItems.forEach((item) => {
                const supplierName = item.querySelector(".col-md-4").textContent.toLowerCase();
                const supplierType = item.querySelector(".col-md-4:nth-child(2)").textContent.toLowerCase();

                const nameMatch = supplierName.includes(searchTerm);
                const typeMatch = selectedType === "" || supplierType.includes(selectedType);

                item.style.display = (nameMatch && typeMatch) ? "" : "none";
            });

            // Show/hide "no results" message
            const allHidden = Array.from(accordionItems).every(item => item.style.display === "none");
            let noResultsMsg = document.getElementById("noResultsMessage");

            if (allHidden) {
                if (!noResultsMsg) {
                    noResultsMsg = document.createElement("div");
                    noResultsMsg.id = "noResultsMessage";
                    noResultsMsg.className = "alert alert-info mt-3";
                    noResultsMsg.textContent = "No suppliers found matching your filters.";
                    document.getElementById("supplierAccordion").appendChild(noResultsMsg);
                }
                noResultsMsg.style.display = "";
            } else if (noResultsMsg) {
                noResultsMsg.style.display = "none";
            }
        }

        nameFilter.addEventListener("input", filterSuppliers);
        typeFilter.addEventListener("change", filterSuppliers);
    }


    /* --- PDF Rendering Functionality --- */
    if (typeof pdfjsLib !== 'undefined') {
        const pdfInstances = {};

        function renderPage(pdfDoc, pageNum, canvas, scale = 1.5) {
            if (!pdfDoc || !canvas) return;

            pdfDoc.getPage(pageNum).then(function(page) {
                const viewport = page.getViewport({ scale: scale });
                const context = canvas.getContext('2d');
                canvas.height = viewport.height;
                canvas.width = viewport.width;

                const renderContext = {
                    canvasContext: context,
                    viewport: viewport
                };
                page.render(renderContext);
            }).catch(function(error) {
                console.error('Error rendering PDF page:', error);
            });
        }

        // Initialize PDF viewers
        document.querySelectorAll('.pdf-container').forEach(function(container) {
            if (!container) return;

            const attachmentId = container.id.split('-').pop();
            const canvas = document.getElementById(`pdf-canvas-${attachmentId}`);
            const url = canvas.closest('.tab-pane').querySelector('a[href$=".pdf"]').href;

            pdfjsLib.getDocument(url).promise.then(function(pdf) {
                pdfInstances[attachmentId] = {
                    doc: pdf,
                    currentPage: 1,
                    scale: 1.5
                };
                
                const pageCount = container.closest('.tab-pane').querySelector('.page-count');
                if (pageCount) pageCount.textContent = pdf.numPages;
                
                renderPage(pdf, 1, canvas, 1.5);
            }).catch(function(error) {
                console.error('Error loading PDF:', error);
                container.innerHTML = `
                    <div class="alert alert-warning">
                        Error loading PDF. Please try downloading it instead.
                    </div>
                `;
            });
        });

        // Handle page navigation
        document.querySelectorAll('.prev-page, .next-page').forEach(button => {
            if (!button) return;

            button.addEventListener('click', function() {
                const attachmentId = this.dataset.pdfId;
                const instance = pdfInstances[attachmentId];
                if (!instance) return;

                const isNext = this.classList.contains('next-page');
                
                if (isNext && instance.currentPage < instance.doc.numPages) {
                    instance.currentPage++;
                } else if (!isNext && instance.currentPage > 1) {
                    instance.currentPage--;
                }

                const canvas = document.getElementById(`pdf-canvas-${attachmentId}`);
                if (canvas) {
                    renderPage(instance.doc, instance.currentPage, canvas, instance.scale);
                    const pageNum = this.closest('.tab-pane').querySelector('.page-num');
                    if (pageNum) pageNum.textContent = instance.currentPage;
                }
            });
        });

        // Handle zoom
        document.querySelectorAll('.zoom-in, .zoom-out').forEach(button => {
            if (!button) return;

            button.addEventListener('click', function() {
                const attachmentId = this.dataset.pdfId;
                const instance = pdfInstances[attachmentId];
                if (!instance) return;

                const isZoomIn = this.classList.contains('zoom-in');
                instance.scale = isZoomIn ? instance.scale * 1.2 : instance.scale / 1.2;

                const canvas = document.getElementById(`pdf-canvas-${attachmentId}`);
                if (canvas) {
                    renderPage(instance.doc, instance.currentPage, canvas, instance.scale);
                }
            });
        });
    }

    // Error handling for PDF loading
    window.addEventListener('error', function(e) {
        if (e.target.tagName === 'CANVAS') {
            console.error('Error loading PDF:', e);
            const container = e.target.closest('.pdf-container');
            if (container) {
                container.innerHTML = `
                    <div class="alert alert-warning">
                        Error loading PDF. Please try downloading it instead.
                    </div>
                `;
            }
        }
    }, true);
});