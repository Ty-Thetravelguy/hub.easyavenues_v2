// Table functionality for Easy Avenues CRM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔄 Easy Avenues CRM - Initializing tables.js');
    
    // Initialize DataTable for company list
    var companyListTable = document.getElementById('company-list-table');
    if (companyListTable) {
        try {
            console.log('📊 Company list table found');
            initializeCompanyListTable(jQuery(companyListTable));
        } catch (e) {
            console.error('❌ Error initializing company list table:', e);
        }
    }
    
    // Initialize DataTable for contact list
    var contactListTable = document.getElementById('contact-list-table');
    if (contactListTable) {
        try {
            console.log('📊 Contact list table found');
            initializeContactListTable(jQuery(contactListTable));
        } catch (e) {
            console.error('❌ Error initializing contact list table:', e);
        }
    }
    
    // Initialize DataTable for company contacts
    var companyContactsTable = document.getElementById('company-contacts-table');
    if (companyContactsTable) {
        try {
            console.log('📊 Company contacts table found');
            initializeContactsTable(jQuery(companyContactsTable));
        } catch (e) {
            console.error('❌ Error initializing company contacts table:', e);
        }
    }

    // Initialize DataTable for company activities
    var activitiesTable = document.getElementById('company-activities-table');
    if (activitiesTable) {
        try {
            console.log('📊 Company activities table found');
            initializeActivitiesTable(jQuery(activitiesTable));
        } catch (e) {
            console.error('❌ Error initializing activities table:', e);
        }
    }
});

// ======================================================
// Common table utilities
// ======================================================

/**
 * Update sort icons in a DataTable
 */
function updateSortIcons(table) {
    table.find('thead th').each(function(index) {
        const sortIcon = jQuery(this).find('.sort-icon');
        if (sortIcon.length) {
            // Check if this column is sorted
            if (jQuery(this).hasClass('sorting_asc')) {
                sortIcon.attr('class', 'fas fa-sort-up sort-icon');
            } else if (jQuery(this).hasClass('sorting_desc')) {
                sortIcon.attr('class', 'fas fa-sort-down sort-icon');
            } else {
                sortIcon.attr('class', 'fas fa-sort sort-icon');
            }
        }
    });
}

/**
 * Get common DataTable configuration
 */
function getCommonDataTableConfig(config = {}) {
    return {
        "pageLength": 10,
        "order": [[0, "asc"]],
        "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
        "autoWidth": false,
        "scrollX": false,
        "ordering": true,
        "language": {
            "lengthMenu": "Show _MENU_ entries per page",
            "info": "Showing _START_ to _END_ of _TOTAL_ entries",
            "infoEmpty": "No entries available",
            "infoFiltered": "(filtered from _MAX_ total entries)",
            "zeroRecords": "No matching entries found",
            "search": "Search:",
            "sortAscending": "",
            "sortDescending": ""
        },
        "drawCallback": function() {
            updateSortIcons(jQuery(this));
        },
        ...config
    };
}

// ======================================================
// Company List Table
// ======================================================

/**
 * Initialize company list table
 */
function initializeCompanyListTable(table) {
    // Remove existing sort icons to prevent duplicates
    table.find('th .sort-icon').remove();
    
    // Add sort icons to sortable columns
    table.find('thead th').each(function(index) {
        // Skip the actions column (typically last column)
        if (!jQuery(this).hasClass('no-sort')) {
            jQuery(this).prepend('<i class="fas fa-sort sort-icon"></i>');
        }
    });
    
    // Initialize DataTable
    var dataTable = table.DataTable(getCommonDataTableConfig({
        "columnDefs": [
            { "orderable": false, "targets": '.no-sort' }
        ],
        "language": {
            "lengthMenu": "Show _MENU_ companies per page",
            "info": "Showing _START_ to _END_ of _TOTAL_ companies",
            "infoEmpty": "No companies available",
            "infoFiltered": "(filtered from _MAX_ total companies)",
            "zeroRecords": "No matching companies found"
        }
    }));
    
    // Add click handlers for immediate icon updates
    table.find('thead th').on('click', function() {
        setTimeout(function() {
            updateSortIcons(table);
        }, 50);
    });
}

// ======================================================
// Contact List Table
// ======================================================

/**
 * Initialize contact list table
 */
function initializeContactListTable(table) {
    // Remove existing sort icons to prevent duplicates
    table.find('th .sort-icon').remove();
    
    // Add sort icons to sortable columns
    table.find('thead th').each(function(index) {
        // Skip the actions column (typically last column)
        if (!jQuery(this).hasClass('no-sort')) {
            jQuery(this).prepend('<i class="fas fa-sort sort-icon"></i>');
        }
    });
    
    // Initialize DataTable
    var dataTable = table.DataTable(getCommonDataTableConfig({
        "columnDefs": [
            { "orderable": false, "targets": '.no-sort' }
        ],
        "language": {
            "lengthMenu": "Show _MENU_ contacts per page",
            "info": "Showing _START_ to _END_ of _TOTAL_ contacts",
            "infoEmpty": "No contacts available",
            "infoFiltered": "(filtered from _MAX_ total contacts)",
            "zeroRecords": "No matching contacts found"
        }
    }));
    
    // Add click handlers for immediate icon updates
    table.find('thead th').on('click', function() {
        setTimeout(function() {
            updateSortIcons(table);
        }, 50);
    });
}

// ======================================================
// Company Contacts Table
// ======================================================

/**
 * Initialize company contacts table
 */
function initializeContactsTable(contactsTable) {
    // First, remove any existing sort icons to prevent duplicates
    contactsTable.find('th .sort-icon').remove();
    
    // Remove all extra styles that might be interfering
    jQuery('#datatable-company-contacts-styles').remove();
    
    // Add very specific styles for this table with !important on all properties
    jQuery('head').append(`
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
            jQuery(this).prepend('<i class="fas fa-sort sort-icon"></i>');
        }
    });
    
    // Add click handlers for immediate icon updates
    contactsTable.find('thead th').each(function(index) {
        if (index < 6) {
            jQuery(this).on('click', function() {
                setTimeout(function() {
                    updateSortIcons(contactsTable);
                }, 50);
            });
        }
    });
}

// ======================================================
// Company Activities Table
// ======================================================

/**
 * Initialize company activities table
 */
function initializeActivitiesTable(activitiesTable) {
    // Initialize DataTable with basic settings
    var dataTable = activitiesTable.DataTable({
        "destroy": true, // In case it was already initialized
        "pageLength": 10,
        "order": [[0, "desc"]], // Order by date desc by default
        "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
        "autoWidth": false,
        "scrollX": false,
        "columnDefs": [
            { "orderable": false, "targets": [3] } // Actions column is not sortable
        ],
        "language": {
            "lengthMenu": "Show _MENU_ activities per page",
            "info": "Showing _START_ to _END_ of _TOTAL_ activities",
            "infoEmpty": "No activities available",
            "infoFiltered": "(filtered from _MAX_ total activities)",
            "zeroRecords": "No matching activities found",
            "search": "Search:"
        }
    });
} 