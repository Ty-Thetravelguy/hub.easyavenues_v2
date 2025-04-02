$(document).ready(function() {
    console.log('🔍 COMPANY DETAIL JS LOADED');
    
    // Initialize DataTable for company contacts
    var contactsTable = $('#company-contacts-table');
    if (contactsTable.length) {
        try {
            console.log('📊 Company contacts table found');
            initializeContactsTable(contactsTable);
        } catch (e) {
            console.error('❌ Error initializing contacts table:', e);
        }
    }

    // Initialize DataTable for company activities
    var activitiesTable = $('#company-activities-table');
    if (activitiesTable.length) {
        try {
            console.log('📊 Company activities table found');
            initializeActivitiesTable(activitiesTable);
        } catch (e) {
            console.error('❌ Error initializing activities table:', e);
        }
    }

    // Initialize DataTable for company documents
    var documentsTable = $('#company-documents-table');
    if (documentsTable.length) {
        try {
            console.log('📊 Company documents table found - skipping initialization (using Django rendering)');
            // Removed DataTables initialization to rely on Django template rendering
            // initializeDocumentsTable(documentsTable);
        } catch (e) {
            console.error('❌ Error initializing documents table:', e);
        }
    }
    
    // Initialize DataTable for travel policies
    var travelPoliciesTable = $('#company-travel-policies-table');
    if (travelPoliciesTable.length) {
        try {
            console.log('📊 Company travel policies table found - skipping initialization (using static HTML)');
            // Skipping initialization as we're now using a static HTML table
            // initializeTravelPoliciesTable(travelPoliciesTable);
        } catch (e) {
            console.error('❌ Error initializing travel policies table:', e);
        }
    }
    
    // Initialize Activity Details Modal
    try {
        console.log('🔍 Initializing Activity Details Modal');
        initializeActivityDetailsModal();
    } catch (e) {
        console.error('❌ Error initializing activity details modal:', e);
    }

    // Initialize Activity Filtering System
    try {
        console.log('🔍 Initializing Activity Filtering');
        initializeActivityFiltering();
    } catch (e) {
        console.error('❌ Error initializing activity filtering:', e);
    }
});

// Function to initialize contacts table
function initializeContactsTable(contactsTable) {
    // First, remove any existing sort icons to prevent duplicates
    contactsTable.find('th .sort-icon').remove();
    
    // Remove all extra styles that might be interfering
    $('#datatable-company-contacts-styles').remove();
    
    // Add very specific styles for this table with !important on all properties
    $('head').append(`
        <style id="datatable-company-contacts-styles">
            /* Core table styles */
            #company-contacts-table {
                width: 100% !important;
                table-layout: auto !important;
                border-collapse: separate !important;
                border-spacing: 0 !important;
            }
            
            /* Force column widths */
            #company-contacts-table th:nth-child(1) { width: 20% !important; }  /* Name */
            #company-contacts-table th:nth-child(2) { width: 15% !important; }  /* Job Role */
            #company-contacts-table th:nth-child(3) { width: 15% !important; }  /* Tags */
            #company-contacts-table th:nth-child(4) { width: 15% !important; }  /* Email */
            #company-contacts-table th:nth-child(5) { width: 15% !important; }  /* Phone */
            #company-contacts-table th:nth-child(6) { width: 10% !important; }  /* Created */
            #company-contacts-table th:nth-child(7) { width: 10% !important; }  /* Actions */
            
            /* Force column widths on cells too */
            #company-contacts-table td:nth-child(1) { width: 20% !important; }
            #company-contacts-table td:nth-child(2) { width: 15% !important; }
            #company-contacts-table td:nth-child(3) { width: 15% !important; }
            #company-contacts-table td:nth-child(4) { width: 15% !important; }
            #company-contacts-table td:nth-child(5) { width: 15% !important; }
            #company-contacts-table td:nth-child(6) { width: 10% !important; }
            #company-contacts-table td:nth-child(7) { width: 10% !important; }
            
            /* Header styling */
            #company-contacts-table th {
                position: relative !important;
                padding-left: 28px !important;
                text-align: left !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
                vertical-align: middle !important;
            }
            
            /* Sort icon positioning */
            #company-contacts-table th .sort-icon {
                position: absolute !important;
                left: 8px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
                color: #aaa !important;
                margin: 0 !important;
            }
            
            /* Active sort icon color */
            #company-contacts-table th.sorting_asc .sort-icon,
            #company-contacts-table th.sorting_desc .sort-icon {
                color: #000 !important;
            }
            
            /* Hide all default DataTables sort indicators */
            #company-contacts-table thead .sorting:before,
            #company-contacts-table thead .sorting:after,
            #company-contacts-table thead .sorting_asc:before,
            #company-contacts-table thead .sorting_asc:after,
            #company-contacts-table thead .sorting_desc:before,
            #company-contacts-table thead .sorting_desc:after,
            table.dataTable thead .sorting:before,
            table.dataTable thead .sorting:after,
            table.dataTable thead .sorting_asc:before,
            table.dataTable thead .sorting_asc:after,
            table.dataTable thead .sorting_desc:before,
            table.dataTable thead .sorting_desc:after {
                display: none !important;
                content: none !important;
                opacity: 0 !important;
            }
        </style>
    `);
    
    // Initialize DataTable with explicit column widths
    var dataTable = contactsTable.DataTable({
        "destroy": true, // In case it was already initialized
        "pageLength": 10,
        "order": [[0, "asc"]],
        "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
        "autoWidth": false, // Disable autoWidth to use our custom widths
        "scrollX": false, // Disable horizontal scrolling
        "ordering": true,
        "columnDefs": [
            { "orderable": true, "targets": "_all" },
            { "width": "20%", "targets": 0 }, // Name
            { "width": "15%", "targets": 1 }, // Job Role
            { "width": "15%", "targets": 2 }, // Tags
            { "width": "15%", "targets": 3 }, // Email
            { "width": "15%", "targets": 4 }, // Phone
            { "width": "10%", "targets": 5 }, // Created
            { "width": "10%", "orderable": false, "searchable": false, "targets": 6 } // Actions
        ],
        "language": {
            "lengthMenu": "Show _MENU_ contacts per page",
            "info": "Showing _START_ to _END_ of _TOTAL_ contacts",
            "infoEmpty": "No contacts available",
            "infoFiltered": "(filtered from _MAX_ total contacts)",
            "zeroRecords": "No matching contacts found",
            "search": "Search:",
            "sortAscending": "",
            "sortDescending": ""
        },
        "drawCallback": function() {
            updateSortIcons(contactsTable);
        }
    });
    
    // Now add the sort icons after DataTable initialization
    contactsTable.find('thead th').each(function(index) {
        // Skip the Actions column
        if (index < 6) {
            $(this).prepend('<i class="fas fa-sort sort-icon"></i>');
        }
    });
    
    // Add click handlers for immediate icon updates
    contactsTable.find('thead th').each(function(index) {
        if (index < 6) {
            $(this).on('click', function() {
                setTimeout(function() {
                    updateSortIcons(contactsTable);
                }, 50);
            });
        }
    });
    
    // Initial update of sort icons
    updateSortIcons(contactsTable);
    
    console.log('✅ Company contacts table initialized');
}

// Function to initialize activities table
function initializeActivitiesTable(activitiesTable) {
    activitiesTable.DataTable({
        "pageLength": 10,
        "order": [[0, "desc"]],
        "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
        "autoWidth": false,
        "scrollX": true,
        "ordering": true,
        "columnDefs": [
            { "targets": "_all", "orderable": true },
            { "targets": -1, "orderable": false, "searchable": false, "width": "100px" }
        ],
        "language": {
            "lengthMenu": "Show _MENU_ activities per page",
            "info": "Showing _START_ to _END_ of _TOTAL_ activities",
            "infoEmpty": "No activities available",
            "infoFiltered": "(filtered from _MAX_ total activities)",
            "zeroRecords": "No matching activities found"
        }
    });
    console.log('✅ Company activities table initialized');
}

// Function to initialize documents table
function initializeDocumentsTable(documentsTable) {
    // Check if the table has any data rows
    const hasRows = documentsTable.find('tbody tr').length > 0;
    const emptyMessageRow = documentsTable.find('tbody tr td[colspan="5"]').length > 0;
    
    // If there are no data rows or just an empty message row, use simpler initialization
    if (!hasRows || emptyMessageRow) {
        console.log('📊 Empty documents table detected, using simple initialization');
        documentsTable.DataTable({
            "destroy": true,
            "paging": false,
            "searching": false,
            "info": false,
            "ordering": false,
            "dom": '' // Hide all DataTables UI elements
        });
    } else {
        // Regular initialization for tables with data
        documentsTable.DataTable({
            "destroy": true,
            "pageLength": 10,
            "order": [[0, "desc"]],
            "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
            "autoWidth": false,
            "scrollX": true,
            "ordering": true,
            "responsive": true,
            "columnDefs": [
                { "targets": "_all", "orderable": true },
                { "targets": -1, "orderable": false, "searchable": false, "width": "100px" },
                { "responsivePriority": 1, "targets": 0 },
                { "responsivePriority": 2, "targets": 4 }
            ],
            "language": {
                "lengthMenu": "Show _MENU_ documents per page",
                "info": "Showing _START_ to _END_ of _TOTAL_ documents",
                "infoEmpty": "No documents available",
                "infoFiltered": "(filtered from _MAX_ total documents)",
                "zeroRecords": "No matching documents found",
                "search": "_INPUT_",
                "searchPlaceholder": "Search documents..."
            }
        });
    }
    console.log('✅ Company documents table initialized');
}

// Function to initialize travel policies table
function initializeTravelPoliciesTable(travelPoliciesTable) {
    // Check if the table has any data rows
    const hasRows = travelPoliciesTable.find('tbody tr').length > 0;
    const emptyMessageRow = travelPoliciesTable.find('tbody tr td[colspan]').length > 0;
    
    // If there are no data rows or just an empty message row, use simpler initialization
    if (!hasRows || emptyMessageRow) {
        console.log('📊 Empty travel policies table detected, using simple initialization');
        travelPoliciesTable.DataTable({
            "destroy": true,
            "paging": false,
            "searching": false,
            "info": false,
            "ordering": false,
            "dom": '' // Hide all DataTables UI elements
        });
    } else {
        // Regular initialization for tables with data
        travelPoliciesTable.DataTable({
            "destroy": true,
            "pageLength": 10,
            "order": [[0, "desc"]],
            "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
            "autoWidth": false,
            "scrollX": true,
            "ordering": true,
            "responsive": true,
            "columnDefs": [
                { "targets": "_all", "orderable": true },
                { "targets": -1, "orderable": false, "searchable": false, "width": "100px" },
                { "responsivePriority": 1, "targets": 0 },
                { "responsivePriority": 2, "targets": 4 }
            ],
            "language": {
                "lengthMenu": "Show _MENU_ policies per page",
                "info": "Showing _START_ to _END_ of _TOTAL_ policies",
                "infoEmpty": "No policies available",
                "infoFiltered": "(filtered from _MAX_ total policies)",
                "zeroRecords": "No matching policies found",
                "search": "_INPUT_",
                "searchPlaceholder": "Search policies..."
            }
        });
    }
    console.log('✅ Company travel policies table initialized');
}

// Function to update sort icons based on current sort state
function updateSortIcons(table) {
    try {
        var dataTable = table.DataTable();
        var order = dataTable.order()[0];
        var columnIndex = order[0];
        var direction = order[1];
        
        // Reset all sort icons to default
        table.find('th .sort-icon').removeClass('fa-sort-up fa-sort-down').addClass('fa-sort');
        table.find('th .sort-icon').css('color', '#aaa'); // Reset color to gray
        
        // Get the header cell being sorted
        var sortedHeader = table.find('th').eq(columnIndex);
        
        // Update the sort icon and its color
        if (direction === 'asc') {
            sortedHeader.find('.sort-icon').removeClass('fa-sort').addClass('fa-sort-up');
            sortedHeader.find('.sort-icon').css('color', '#000'); // Set to black when active
        } else {
            sortedHeader.find('.sort-icon').removeClass('fa-sort').addClass('fa-sort-down');
            sortedHeader.find('.sort-icon').css('color', '#000'); // Set to black when active
        }
    } catch (e) {
        console.error('❌ Error updating sort icons:', e);
    }
}

// Activity details modal handler
function initializeActivityDetailsModal() {
    console.log('🔄 Initializing activity details modal');
    
    // When the activity details modal is about to be shown
    $('#activity-details-modal').on('show.bs.modal', function (event) {
        console.log('🔄 Activity modal being shown');
        
        // Button that triggered the modal
        var button = $(event.relatedTarget);
        
        // Extract activity id from data attributes
        var activityId = button.data('activity-id');
        var activityType = button.data('activity-type');
        
        console.log('🔄 Showing activity:', activityId, activityType);
        
        // Hide all activity details sections
        $('.activity-detail-section').hide();
        
        // Hide the no activity selected message
        $('#no-activity-selected').hide();
        
        // Show the selected activity details
        var detailsSelector = '#activity-' + activityId + '-details';
        if ($(detailsSelector).length) {
            console.log('✅ Found activity details element, showing:', detailsSelector);
            $(detailsSelector).show();
        } else {
            console.error('❌ Activity details element not found for ID:', activityId);
            // Show the no activity selected message if details not found
            $('#no-activity-selected').show();
        }
    });
    
    // When the modal is hidden, reset all detail visibility
    $('#activity-details-modal').on('hidden.bs.modal', function () {
        $('.activity-detail-section').hide();
        $('#no-activity-selected').show();
    });
    
    console.log('✅ Activity details modal initialized');
}

// Initialize simple document search functionality
$(document).ready(function() {
    // Simple document search
    $('#document-search').on('keyup', function() {
        var searchText = $(this).val().toLowerCase();
        $('.table-responsive table tbody tr').each(function() {
            var rowText = $(this).text().toLowerCase();
            $(this).toggle(rowText.indexOf(searchText) > -1);
        });
        
        // Show/hide "no results" message
        if ($('.table-responsive table tbody tr:visible').length === 0) {
            if ($('.table-responsive table tbody .no-results').length === 0) {
                $('.table-responsive table tbody').append(
                    '<tr class="no-results"><td colspan="5" class="text-center py-3">' +
                    '<i class="fas fa-search me-2"></i>No documents match your search.' +
                    '</td></tr>'
                );
            }
        } else {
            $('.no-results').remove();
        }
    });
    
    // Documents per page selector
    $('#documents-per-page').on('change', function() {
        var perPage = parseInt($(this).val());
        var rows = $('.table-responsive table tbody tr:not(.no-results)');
        
        rows.each(function(index) {
            $(this).toggle(index < perPage);
        });
        
        // Update pagination info
        var totalRows = rows.length;
        var visibleRows = $('.table-responsive table tbody tr:visible').length;
        
        if (totalRows > 0) {
            $('.col-md-6 .text-muted').text('Showing 1 to ' + visibleRows + ' of ' + totalRows + ' documents');
        }
    });
});

// Function to initialize activity filtering
function initializeActivityFiltering() {
    console.log('🔍 ACTIVITY FILTERING: Initialization started');
    
    // Activity filtering variables
    const activitySearch = $('#activity-search');
    const activitySearchBtn = $('#activity-search-btn');
    const activityTypeFilter = $('#activity-type-filter');
    const dateFrom = $('#date-from');
    const dateTo = $('#date-to');
    const resetFiltersBtn = $('#reset-filters');
    const noResultsMessage = $('<div class="alert alert-info text-center my-4">No activities match your filter criteria.</div>').hide();
    
    // Debug the found elements
    console.log('🔍 ACTIVITY FILTERING: Found elements:', {
        activitySearch: activitySearch.length > 0,
        activitySearchBtn: activitySearchBtn.length > 0,
        activityTypeFilter: activityTypeFilter.length > 0,
        dateFrom: dateFrom.length > 0,
        dateTo: dateTo.length > 0,
        resetFiltersBtn: resetFiltersBtn.length > 0
    });
    
    // Helper function to format dates
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    // Don't set default date values - leave fields empty
    if (dateFrom.length && dateTo.length) {
        // Clear any existing values
        dateFrom.val('');
        dateTo.val('');
        console.log('📅 Date filters initialized with empty values');
    } else {
        console.warn('⚠️ Date filter elements not found');
    }
    
    // Add no results message after the timeline
    $('.timeline').after(noResultsMessage);
    
    // Function to filter activities
    function filterActivities() {
        console.log('🔍 ACTIVITY FILTERING: Filtering started');
        
        // Update filter status
        $('#filter-status').html('<i class="fas fa-sync-alt fa-spin me-1"></i>Filtering...');
        
        // Get filter values
        const searchTerm = activitySearch.val() ? activitySearch.val().toLowerCase() : '';
        const activityType = activityTypeFilter.val() ? activityTypeFilter.val().toLowerCase() : '';
        const fromDate = dateFrom.val() ? new Date(dateFrom.val() + 'T00:00:00') : null;
        const toDate = dateTo.val() ? new Date(dateTo.val() + 'T23:59:59') : null;
        
        console.log('🔍 ACTIVITY FILTERING: Filter values:', {
            searchTerm: searchTerm,
            activityType: activityType,
            fromDate: fromDate ? fromDate.toISOString() : 'not set',
            toDate: toDate ? toDate.toISOString() : 'not set'
        });
        
        // Track visible items
        let visibleItems = 0;
        const allItems = $('.timeline-item, .system-activity-item');
        
        console.log('🔍 ACTIVITY FILTERING: Found', allItems.length, 'items to filter');
        
        // Loop through all activity items
        allItems.each(function() {
            const $item = $(this);
            const itemText = $item.text().toLowerCase();
            let showItem = true;
            
            // Check for search term
            if (searchTerm && !itemText.includes(searchTerm)) {
                showItem = false;
            }
            
            // Check for activity type
            if (activityType && activityType !== '') {
                // Handle system updates filter separately
                if (activityType === 'system') {
                    if (!$item.hasClass('system-activity-item')) {
                        showItem = false;
                    }
                } else {
                    // For specific activity types, check text content
                    if (!itemText.includes(activityType)) {
                        showItem = false;
                    }
                }
            }
            
            // Check date range only if both dates are provided
            if (fromDate && toDate) {
                // Extract date from the item
                const dateText = $item.find('.text-muted:contains("202")').last().text().trim(); // Assumes dates contain year 202x
                
                console.log('🔍 ACTIVITY FILTERING: Date text from item:', dateText);
                
                if (dateText) {
                    try {
                        // Parse date from format: "dd MMM YYYY HH:mm"
                        const parts = dateText.split(/[\s:]/);
                        if (parts.length >= 5) {
                            const day = parseInt(parts[0], 10);
                            const months = {'Jan':0,'Feb':1,'Mar':2,'Apr':3,'May':4,'Jun':5,'Jul':6,'Aug':7,'Sep':8,'Oct':9,'Nov':10,'Dec':11};
                            const month = months[parts[1]];
                            const year = parseInt(parts[2], 10);
                            const hour = parseInt(parts[3], 10);
                            const minute = parseInt(parts[4], 10);
                            
                            // Create a date object and check validity
                            if (!isNaN(day) && month !== undefined && !isNaN(year) && !isNaN(hour) && !isNaN(minute)) {
                                const itemDate = new Date(year, month, day, hour, minute);
                                
                                console.log('🔍 ACTIVITY FILTERING: Parsed item date:', itemDate.toISOString());
                                
                                // Check if the item date is within the range
                                if (itemDate < fromDate || itemDate > toDate) {
                                    showItem = false;
                                    console.log('🔍 ACTIVITY FILTERING: Item date outside range');
                                }
                            } else {
                                console.warn('⚠️ ACTIVITY FILTERING: Invalid date parts:', parts);
                            }
                        }
                    } catch (e) {
                        console.warn('⚠️ ACTIVITY FILTERING: Error parsing date:', dateText, e);
                    }
                }
            }
            
            // Show or hide the item
            $item.toggle(showItem);
            
            // Count visible items
            if (showItem) {
                visibleItems++;
            }
        });
        
        console.log('🔍 ACTIVITY FILTERING: Results:', visibleItems, 'out of', allItems.length, 'items visible');
        
        // Show/hide no results message
        if (visibleItems === 0 && allItems.length > 0) {
            noResultsMessage.show();
        } else {
            noResultsMessage.hide();
        }
        
        // Update filter status and visible count
        let statusHtml = 'Showing <span class="badge bg-primary">' + visibleItems + '</span> of <span class="badge bg-secondary">' + allItems.length + '</span> activities';
        
        // Add active filter info
        let activeFilters = [];
        if (searchTerm) activeFilters.push('Search: <span class="badge bg-info">' + searchTerm + '</span>');
        if (activityType) {
            let typeLabel = activityType.charAt(0).toUpperCase() + activityType.slice(1);
            activeFilters.push('Type: <span class="badge bg-success">' + typeLabel + '</span>');
        }
        if (fromDate && toDate) {
            let dateLabel = formatDate(fromDate) + ' to ' + formatDate(toDate);
            activeFilters.push('Dates: <span class="badge bg-warning text-dark">' + dateLabel + '</span>');
        }
        
        if (activeFilters.length > 0) {
            statusHtml += '<br><small>Filters: ' + activeFilters.join(', ') + '</small>';
        }
        
        $('#filter-status').html(statusHtml);
        $('#total-activities').text(visibleItems);
    }
    
    // Attach event listeners for filtering
    if (activitySearch.length) {
        console.log('🔄 ACTIVITY FILTERING: Attaching search input event listener');
        activitySearch.on('input', function() {
            console.log('🔄 ACTIVITY FILTERING: Search input changed to:', $(this).val());
            filterActivities();
        });
    }
    
    if (activitySearchBtn.length) {
        console.log('🔄 ACTIVITY FILTERING: Attaching search button event listener');
        activitySearchBtn.on('click', function() {
            console.log('🔄 ACTIVITY FILTERING: Search button clicked');
            filterActivities();
        });
    }
    
    if (activityTypeFilter.length) {
        console.log('🔄 ACTIVITY FILTERING: Attaching activity type filter event listener');
        activityTypeFilter.on('change', function() {
            console.log('🔄 ACTIVITY FILTERING: Type filter changed to:', $(this).val());
            filterActivities();
        });
    }
    
    if (dateFrom.length && dateTo.length) {
        console.log('🔄 ACTIVITY FILTERING: Attaching date filter event listeners');
        
        dateFrom.on('change', function() {
            console.log('🔄 ACTIVITY FILTERING: From date changed to:', $(this).val());
            filterActivities();
        });
        
        dateTo.on('change', function() {
            console.log('🔄 ACTIVITY FILTERING: To date changed to:', $(this).val());
            filterActivities();
        });
    }
    
    // Reset filters
    if (resetFiltersBtn.length) {
        console.log('🔄 ACTIVITY FILTERING: Attaching reset button event listener');
        
        resetFiltersBtn.on('click', function() {
            console.log('🔄 ACTIVITY FILTERING: Reset button clicked');
            
            // Clear search and type filter
            if (activitySearch.length) activitySearch.val('');
            if (activityTypeFilter.length) activityTypeFilter.val('');
            
            // Clear dates too
            if (dateFrom.length) dateFrom.val('');
            if (dateTo.length) dateTo.val('');
            
            // Apply the filter reset
            filterActivities();
            
            console.log('🔄 ACTIVITY FILTERING: Filters have been reset');
        });
    }
    
    // Run initial filtering
    console.log('🔍 ACTIVITY FILTERING: Running initial filtering');
    
    // Add a small delay to ensure the DOM is ready
    setTimeout(function() {
        filterActivities();
    }, 300);
    
    console.log('✅ ACTIVITY FILTERING: Initialization complete');
} 