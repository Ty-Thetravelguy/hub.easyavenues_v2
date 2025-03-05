document.addEventListener('DOMContentLoaded', function () {
    // Function to show message
    function showMessage(message, type = 'success') {
        const messageContainer = document.getElementById('message-container');
        if (messageContainer) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show shadow`;
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            messageContainer.appendChild(alertDiv);

            // Auto-remove after 3 seconds
            setTimeout(() => {
                alertDiv.remove();
            }, 3000);
        }
    }

    // Existing alert code
    setTimeout(function () {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 3000);

    // DateTime update code
    function updateDateTime() {
        const dateTimeElement = document.getElementById('current-datetime');
        if (dateTimeElement) {
            const now = new Date();
            const months = ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'];
            const day = now.getDate();
            const month = months[now.getMonth()];
            const year = now.getFullYear();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            dateTimeElement.textContent = `${day} ${month} ${year} - ${hours}:${minutes}`;
        }
    }

    updateDateTime();
    setInterval(updateDateTime, 60000);

    // Function to refresh bookmark list
    function refreshBookmarkList() {
        const bookmarkersContent = document.getElementById('bookmarkersContent');
        if (!bookmarkersContent) return;

        fetch('/users/get-bookmarks/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            bookmarkersContent.innerHTML = html;
            // Reattach event listeners to new remove buttons
            document.querySelectorAll('.remove-bookmark').forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    handleRemoveBookmark(this);
                });
            });
        })
        .catch(error => {
            console.error('Error refreshing bookmarks:', error);
        });
    }

    // Bookmark code
    const bookmarkButtons = document.querySelectorAll('.bookmark-btn');
    bookmarkButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.url;
            const icon = this.querySelector('i');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/users/toggle-bookmark/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `url=${encodeURIComponent(url)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'added') {
                    icon.classList.replace('far', 'fas');
                } else {
                    icon.classList.replace('fas', 'far');
                }
                
                // Show success message
                if (data.message) {
                    showMessage(data.message);
                }

                // Refresh the bookmark list
                refreshBookmarkList();
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error updating bookmark', 'danger');
            });
        });
    });

    // Add handler for existing remove buttons
    function handleRemoveBookmark(button) {
        const url = button.dataset.url;
        const bookmarkBtn = document.querySelector(`.bookmark-btn[data-url="${url}"]`);
        if (bookmarkBtn) {
            bookmarkBtn.click(); // Reuse the existing toggle functionality
        }
    }

    document.querySelectorAll('.remove-bookmark').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            handleRemoveBookmark(this);
        });
    });
});