document.addEventListener('DOMContentLoaded', function () {
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

    // Bookmark code - MOVED INSIDE the same DOMContentLoaded
    const bookmarkButtons = document.querySelectorAll('.bookmark-btn');
    bookmarkButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.url;
            const icon = this.querySelector('i');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/users/bookmark/toggle/', {
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
            });
        });
    });
});