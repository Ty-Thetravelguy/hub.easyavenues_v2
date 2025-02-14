document.addEventListener('DOMContentLoaded', function () {
    // Initialize Sortable
    const grid = document.querySelector('.bookmark-grid');
    if (grid) {
        new Sortable(grid, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            onEnd: function (evt) {
                updateBookmarkOrder(evt);
            }
        });
    }

    // Add click handler for bookmarks
    document.querySelectorAll('.bookmark-item').forEach(item => {
        item.addEventListener('click', function (e) {
            // Don't open URL if clicking edit/delete buttons
            if (e.target.closest('.bookmark-actions')) {
                return;
            }

            const url = this.dataset.url;
            if (url) {
                let finalUrl = url;
                if (!/^https?:\/\//i.test(finalUrl)) {
                    finalUrl = 'https://' + finalUrl;
                }
                window.open(finalUrl, '_blank');
            }
        });
    });

    // Handle form submission
    const saveButton = document.getElementById('saveBookmark');
    if (saveButton) {
        saveButton.addEventListener('click', handleSaveBookmark);
    }

    // Add form submit handler for Enter key
    const bookmarkForm = document.getElementById('bookmarkForm');
    if (bookmarkForm) {
        bookmarkForm.addEventListener('submit', function (e) {
            e.preventDefault(); // Prevent default form submission
            handleSaveBookmark();
        });

        // Add enter key handler for URL and Title inputs
        const urlInput = bookmarkForm.querySelector('#bookmarkUrl');
        const titleInput = bookmarkForm.querySelector('#bookmarkTitle');

        [urlInput, titleInput].forEach(input => {
            input.addEventListener('keypress', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleSaveBookmark();
                }
            });
        });
    }

    // Setup edit and delete handlers
    setupBookmarkActions();

    // Add click handlers for update cards
    document.querySelectorAll('.update-card').forEach(card => {
        card.addEventListener('click', handleUpdateClick);
    });
});

async function handleSaveBookmark() {
    const form = document.getElementById('bookmarkForm');
    const bookmarkId = form.querySelector('#bookmarkId').value;
    const url = form.querySelector('#bookmarkUrl').value;
    const title = form.querySelector('#bookmarkTitle').value;

    const isEdit = bookmarkId !== '';
    const endpoint = isEdit ? `/dashboard/bookmark/${bookmarkId}/update/` : '/dashboard/bookmark/add/';
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const response = await fetch(endpoint, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ url, title })
        });

        if (response.ok) {
            window.location.reload();
        } else {
            const errorData = await response.json();
            console.error('Server error:', errorData);
            alert('Error saving bookmark: ' + (errorData.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Network error:', error);
        alert('Error saving bookmark: ' + error.message);
    }
}

function setupBookmarkActions() {
    // Edit buttons
    document.querySelectorAll('.btn-edit').forEach(button => {
        button.addEventListener('click', handleEdit);
    });

    // Delete buttons
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', handleDelete);
    });
}

async function handleEdit(event) {
    event.preventDefault();
    event.stopPropagation();  // Prevent the bookmark click event

    const bookmarkId = event.currentTarget.dataset.id;
    const bookmarkItem = event.currentTarget.closest('.bookmark-item');

    try {
        // Fetch current bookmark data
        const response = await fetch(`/dashboard/bookmark/${bookmarkId}/`, {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            const data = await response.json();

            // Update modal title
            const modalTitle = document.querySelector('#addBookmarkModal .modal-title');
            modalTitle.textContent = 'Edit Page';

            // Fill form with current data
            const form = document.getElementById('bookmarkForm');
            form.querySelector('#bookmarkId').value = bookmarkId;
            form.querySelector('#bookmarkUrl').value = data.url;
            form.querySelector('#bookmarkTitle').value = data.title;

            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('addBookmarkModal'));
            modal.show();
        } else {
            const errorData = await response.json();
            console.error('Server error:', errorData);
            alert('Error fetching bookmark: ' + (errorData.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Network error:', error);
        alert('Error fetching bookmark: ' + error.message);
    }
}

async function handleDelete(event) {
    event.preventDefault();
    event.stopPropagation();  // Prevent the bookmark click event

    if (!confirm('Are you sure you want to delete this bookmark?')) return;

    const bookmarkId = event.currentTarget.dataset.id;
    const bookmarkItem = event.currentTarget.closest('.bookmark-item');

    // Check if we found the bookmark item
    if (!bookmarkItem) {
        console.error('Could not find bookmark item element');
        return;
    }

    try {
        const response = await fetch(`/dashboard/bookmark/${bookmarkId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            // Remove the element from the DOM
            bookmarkItem.remove();

            // Show success message
            const successMessage = document.createElement('div');
            successMessage.className = 'alert alert-success position-fixed top-0 end-0 m-3';
            successMessage.textContent = 'Bookmark deleted successfully';
            document.body.appendChild(successMessage);
            setTimeout(() => successMessage.remove(), 3000);
        } else {
            const errorData = await response.json();
            console.error('Server error:', errorData);
            alert('Error deleting bookmark: ' + (errorData.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Network error:', error);
        alert('Error deleting bookmark: ' + error.message);
    }
}

async function handleUpdateClick(event) {
    event.preventDefault();
    const updateId = this.dataset.id;

    try {
        const response = await fetch(`/dashboard/update/${updateId}/`, {
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            const data = await response.json();

            // Update modal content
            const modal = document.getElementById('updateModal');
            modal.querySelector('.modal-title').textContent = data.title;
            modal.querySelector('.update-content').innerHTML = data.content;

            // Handle attachments if they exist
            const attachmentsContainer = modal.querySelector('.update-attachments');
            attachmentsContainer.innerHTML = ''; // Clear existing attachments

            if (data.attachments && data.attachments.length > 0) {
                const attachmentsList = document.createElement('ul');
                attachmentsList.className = 'list-unstyled';

                data.attachments.forEach(attachment => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <a href="${attachment.file}" target="_blank" class="text-decoration-none">
                            <i class="fas fa-paperclip me-2"></i>${attachment.filename}
                        </a>
                    `;
                    attachmentsList.appendChild(li);
                });

                attachmentsContainer.appendChild(attachmentsList);
            }

            // Update timestamps
            modal.querySelector('.created-at').textContent = new Date(data.created_at).toLocaleString();
            modal.querySelector('.modified-at').textContent = new Date(data.modified_at).toLocaleString();

            // Show modal
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        } else {
            const errorData = await response.json();
            console.error('Server error:', errorData);
            alert('Error fetching update details: ' + (errorData.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Network error:', error);
        alert('Error fetching update details: ' + error.message);
    }
}

// Utility function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Reset modal when it's hidden
document.getElementById('addBookmarkModal').addEventListener('hidden.bs.modal', function () {
    // Reset form
    const form = document.getElementById('bookmarkForm');
    form.reset();
    form.querySelector('#bookmarkId').value = '';

    // Reset title
    const modalTitle = document.querySelector('#addBookmarkModal .modal-title');
    modalTitle.textContent = 'Add New Page';
});