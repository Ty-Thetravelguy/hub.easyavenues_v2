$(document).ready(function() {
    // Function to activate tab based on hash
    function activateTabFromHash() {
        let hash = window.location.hash;
        if (hash) {
            hash = hash.substring(1);  // remove the # symbol
            
            // Remove active class from all tabs and panes
            $('.nav-link').removeClass('active');
            $('.tab-pane').removeClass('show active');

            // Find and activate the target tab
            const targetTab = $(`#${hash}-tab`);
            const targetPane = $(`#${hash}`);
            
            if (targetTab.length && targetPane.length) {
                targetTab.addClass('active');
                targetPane.addClass('show active');
            }
        }
    }

    // Activate tab on page load
    activateTabFromHash();

    // Listen for hash changes
    $(window).on('hashchange', activateTabFromHash);

    // Update hash when tab is clicked
    $('a[data-bs-toggle="tab"]').on('click', function (event) {
        const hash = $(this).attr('href');
        if (history.pushState) {
            history.pushState(null, null, hash);
        } else {
            window.location.hash = hash;
        }
    });
}); 