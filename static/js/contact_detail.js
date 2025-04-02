document.addEventListener('DOMContentLoaded', function() {
    console.log('Contact detail JS loaded');
    
    // Function to show specific tab
    function showTab(tabName) {
        const tab = document.querySelector(`#${tabName}-tab`);
        if (tab) {
            const bsTab = new bootstrap.Tab(tab);
            bsTab.show();
        }
    }

    // Check URL parameters for tab
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    if (tabParam) {
        showTab(tabParam);
    }

    // Update URL when tab changes
    const tabs = document.querySelectorAll('a[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (event) {
            const tabId = event.target.id.replace('-tab', '');
            const url = new URL(window.location.href);
            url.searchParams.set('tab', tabId);
            window.history.pushState({}, '', url);
        });
    });
    
    // Initialize activity filtering when jQuery is ready
    if (typeof jQuery !== 'undefined') {
        initActivityFilters();
    } else {
        console.error('jQuery not found - activity filtering will not work');
    }
});

/**
 * Activity filtering functionality using jQuery
 */
function initActivityFilters() {
    console.log('Activity filtering initialized');
    
    // Set initial date values (last 30 days)
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    // Format dates for input fields
    function formatDateForInput(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    // Set default values for date fields
    jQuery('#date-from').val(formatDateForInput(thirtyDaysAgo));
    jQuery('#date-to').val(formatDateForInput(today));
    
    // Simple filter function
    function filterActivities() {
        const searchTerm = jQuery('#activity-search').val().toLowerCase();
        const activityType = jQuery('#activity-type-filter').val();
        const fromDate = jQuery('#date-from').val() ? new Date(jQuery('#date-from').val()) : null;
        const toDate = jQuery('#date-to').val() ? new Date(jQuery('#date-to').val()) : null;
        
        // If toDate is provided, set it to end of day
        if (toDate) {
            toDate.setHours(23, 59, 59, 999);
        }
        
        let visibleCount = 0;
        
        // Loop through all timeline items
        jQuery('.timeline-item').each(function() {
            const $item = jQuery(this);
            const itemText = $item.text().toLowerCase();
            const badgeText = $item.find('.badge').text().trim();
            
            // Determine activity type
            let itemType = '';
            if ($item.hasClass('border-top-primary-ea') && itemText.includes('email')) {
                itemType = 'email';
            } else if ($item.hasClass('border-top-secondary-ea') && itemText.includes('call')) {
                itemType = 'call';
            } else if ($item.hasClass('border-top-tertiary-ea') && itemText.includes('note')) {
                itemType = 'note';
            } else if ($item.hasClass('border-top-purple') && itemText.includes('exception')) {
                itemType = 'exception';
            } else if (itemText.includes('meeting')) {
                itemType = 'meeting';
            } else if ($item.find('p.mb-0').length && !$item.find('.activity-card').length) {
                itemType = 'system';
            }
            
            // Parse date
            let itemDate = null;
            const dateParts = badgeText.match(/(\d+)\s+(\w+)\s+(\d+),\s+(\d+):(\d+)/);
            if (dateParts && dateParts.length >= 6) {
                const months = {
                    'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
                    'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
                };
                
                const day = parseInt(dateParts[1]);
                const month = months[dateParts[2].substring(0, 3)] || 0;
                const year = parseInt(dateParts[3]);
                const hours = parseInt(dateParts[4]);
                const minutes = parseInt(dateParts[5]);
                
                itemDate = new Date(year, month, day, hours, minutes);
            }
            
            // Apply filters
            let matchesSearch = true;
            let matchesType = true;
            let matchesDateRange = true;
            
            if (searchTerm && !itemText.includes(searchTerm)) {
                matchesSearch = false;
            }
            
            if (activityType && itemType !== activityType) {
                matchesType = false;
            }
            
            if ((fromDate && itemDate && itemDate < fromDate) || 
                (toDate && itemDate && itemDate > toDate)) {
                matchesDateRange = false;
            }
            
            // Show or hide based on filters
            const shouldShow = matchesSearch && matchesType && matchesDateRange;
            $item.toggle(shouldShow);
            
            if (shouldShow) {
                visibleCount++;
            }
        });
        
        // Handle empty results
        if (visibleCount === 0 && jQuery('.timeline-item').length > 0) {
            // Remove existing "no results" message if it exists
            jQuery('#no-filter-match').remove();
            
            // Create a "no results" message
            const $emptyState = jQuery('.activity-timeline .text-center.text-muted.py-4');
            
            if ($emptyState.length) {
                // Clone and modify the empty state
                const $noMatchElement = $emptyState.clone();
                $noMatchElement.attr('id', 'no-filter-match');
                $noMatchElement.find('i').attr('class', 'fas fa-filter fa-3x mb-3');
                $noMatchElement.find('p').text('No activities match your filters.');
                $noMatchElement.find('span').text('Try adjusting your search criteria or click Reset.');
                
                jQuery('.activity-timeline').append($noMatchElement);
                $emptyState.hide();
            } else {
                // Create a new empty state
                const $noMatchElement = jQuery('<div>')
                    .attr('id', 'no-filter-match')
                    .addClass('text-center text-muted py-4')
                    .append(jQuery('<i>').addClass('fas fa-filter fa-3x mb-3'))
                    .append(jQuery('<p>').text('No activities match your filters.'))
                    .append(jQuery('<span>').addClass('text-secondary small').text('Try adjusting your search criteria or click Reset.'));
                
                jQuery('.activity-timeline').append($noMatchElement);
            }
        } else {
            // Hide the "no results" message if we have results
            jQuery('#no-filter-match').hide();
            jQuery('.activity-timeline .text-center.text-muted.py-4').not('#no-filter-match').hide();
        }
    }
    
    // Add event listeners using jQuery
    jQuery('#activity-search').on('input', filterActivities);
    jQuery('#activity-type-filter').on('change', filterActivities);
    jQuery('#date-from, #date-to').on('change', filterActivities);
    
    // Reset button
    jQuery('#reset-filters').on('click', function() {
        jQuery('#activity-search').val('');
        jQuery('#activity-type-filter').val('');
        jQuery('#date-from').val(formatDateForInput(thirtyDaysAgo));
        jQuery('#date-to').val(formatDateForInput(today));
        filterActivities();
    });
    
    // Apply initial filtering
    filterActivities();
} 