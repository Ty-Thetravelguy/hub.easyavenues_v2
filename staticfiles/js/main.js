document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            // Create a Bootstrap alert instance
            var bsAlert = new bootstrap.Alert(alert);
            // Trigger the close action
            bsAlert.close();
        });
    }, 3000); // 3000 milliseconds = 3 seconds

    // Update date and time function
    function updateDateTime() {
        const dateTimeElement = document.getElementById('current-datetime');
        if (dateTimeElement) {
            const now = new Date();

            // Format date
            const months = ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'];
            const day = now.getDate();
            const month = months[now.getMonth()];
            const year = now.getFullYear();

            // Format time
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');

            // Update the content
            dateTimeElement.textContent = `${day} ${month} ${year} - ${hours}:${minutes}`;
        }
    }

    // Initial update
    updateDateTime();

    // Update every minute (60000 milliseconds)
    setInterval(updateDateTime, 60000);
});    