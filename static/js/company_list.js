$(document).ready(function() {
    console.log('🔍 COMPANY LIST JS LOADED');
    
    // Check if we're on the correct page by looking for the data attribute
    var container = $('.container-fluid[data-show-contacts]');
    
    // Only run if we're on the company list page
    if (container.length) {
        var showContacts = container.data('show-contacts');
        console.log('🔍 Showing contacts?', showContacts);
        
        if (!showContacts) {
            // Companies table
            initializeTable('#companies-table', 'Companies');
        } else {
            // Contacts table within company view
            initializeTable('#contacts-table', 'Contacts');
        }
    } else {
        console.log('⚠️ Not on company list page - skipping initialization');
    }
    
    // Function to initialize a table with sorting
    function initializeTable(tableSelector, tableType) {
        var table = $(tableSelector);
        console.log('📊 ' + tableType + ' table found?', table.length > 0);
        
        if (table.length) {
            console.log('⚙️ Configuring ' + tableType + ' table');
            
            // Add the custom styles for the table first
            $('head').append(`
                <style id="datatable-custom-styles-${tableType.toLowerCase()}">
                    /* Force correct table layout */
                    ${tableSelector} {
                        width: 100% !important;
                        table-layout: fixed !important;
                    }
                    
                    /* Header styles */
                    ${tableSelector} th {
                        position: relative !important;
                        padding-left: 28px !important;
                        text-align: left !important;
                        white-space: nowrap !important;
                        overflow: hidden !important;
                        text-overflow: ellipsis !important;
                    }
                    
                    /* Sort icon styles */
                    ${tableSelector} th .sort-icon {
                        position: absolute !important;
                        left: 10px !important;
                        top: 50% !important;
                        transform: translateY(-50%) !important;
                        color: #aaa !important;
                    }
                    
                    /* Active sort color */
                    ${tableSelector} th.sorting_asc .sort-icon,
                    ${tableSelector} th.sorting_desc .sort-icon {
                        color: #000 !important;
                    }
                    
                    /* Hide DataTables sort indicators */
                    ${tableSelector} thead .sorting:before,
                    ${tableSelector} thead .sorting:after,
                    ${tableSelector} thead .sorting_asc:before,
                    ${tableSelector} thead .sorting_asc:after,
                    ${tableSelector} thead .sorting_desc:before,
                    ${tableSelector} thead .sorting_desc:after {
                        display: none !important;
                    }
                    
                    /* Custom column widths for Contacts table */
                    ${tableSelector === '#contacts-table' ? `
                        #contacts-table th:nth-child(1) { width: 15% !important; } /* Name */
                        #contacts-table th:nth-child(2) { width: 12% !important; } /* Company */
                        #contacts-table th:nth-child(3) { width: 10% !important; } /* Job Role */
                        #contacts-table th:nth-child(4) { width: 18% !important; } /* Tags */
                        #contacts-table th:nth-child(5) { width: 15% !important; } /* Email */
                        #contacts-table th:nth-child(6) { width: 10% !important; } /* Phone */
                        #contacts-table th:nth-child(7) { width: 10% !important; } /* Created */
                        #contacts-table th:nth-child(8) { width: 10% !important; } /* Actions */
                        
                        #contacts-table td:nth-child(1) { width: 15% !important; }
                        #contacts-table td:nth-child(2) { width: 12% !important; }
                        #contacts-table td:nth-child(3) { width: 10% !important; }
                        #contacts-table td:nth-child(4) { width: 18% !important; }
                        #contacts-table td:nth-child(5) { width: 15% !important; }
                        #contacts-table td:nth-child(6) { width: 10% !important; }
                        #contacts-table td:nth-child(7) { width: 10% !important; }
                        #contacts-table td:nth-child(8) { width: 10% !important; }
                    ` : ''}
                </style>
            `);
            
            // First, remove any existing sort icons to prevent duplicates
            table.find('th .sort-icon').remove();
            
            // Initialize DataTable with all features BEFORE adding icons
            var dataTable = table.DataTable({
                "pageLength": 25,
                "order": [[0, "asc"]],
                "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
                "autoWidth": true, // Allow auto width to ensure proper column size calculations
                "scrollX": true,
                "ordering": true,
                "orderCellsTop": true,
                "columnDefs": [
                    {
                        "targets": "_all",
                        "orderable": true
                    },
                    {
                        "targets": -1,
                        "orderable": false,
                        "searchable": false,
                        "width": "100px"
                    }
                ],
                "order": [[0, 'asc']],
                "orderClasses": false,  // Disable classes on rows
                "language": {
                    "lengthMenu": "Show _MENU_ entries per page",
                    "info": "Showing _START_ to _END_ of _TOTAL_ entries",
                    "infoEmpty": "No entries available",
                    "infoFiltered": "(filtered from _MAX_ total entries)",
                    "zeroRecords": "No matching entries found",
                    "search": "Search:",
                    "sortAscending": "",   // Empty string to remove default arrows
                    "sortDescending": ""   // Empty string to remove default arrows
                },
                "drawCallback": function() {
                    // Update sort icons after each draw
                    updateSortIcons(table);
                }
            });
            
            // Add icons AFTER DataTable initialization
            table.find('thead th').each(function(index) {
                // Skip the last column (Actions)
                if (index < table.find('thead th').length - 1) {
                    // prepend the icon (don't replace the content)
                    $(this).prepend('<i class="fas fa-sort sort-icon"></i>');
                }
            });
            
            // Add click handlers to headers for immediate icon update
            table.find('th').each(function(index) {
                if (index < table.find('th').length - 1) { // Skip last column (Actions)
                    $(this).on('click', function() {
                        setTimeout(function() {
                            updateSortIcons(table);
                        }, 50);
                    });
                }
            });
            
            // Initial update of the sort icons
            updateSortIcons(table);
            
            // Force column widths to recalculate
            dataTable.columns.adjust().draw();
            
            console.log('✅ ' + tableType + ' table sorting initialized');
        } else {
            console.warn('⚠️ ' + tableType + ' table not found on this page');
        }
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
                console.log('Sort ascending on column', columnIndex);
            } else {
                sortedHeader.find('.sort-icon').removeClass('fa-sort').addClass('fa-sort-down');
                sortedHeader.find('.sort-icon').css('color', '#000'); // Set to black when active
                console.log('Sort descending on column', columnIndex);
            }
            
            console.log('🔄 Sort icons updated successfully');
        } catch (e) {
            console.error('❌ Error updating sort icons:', e);
        }
    }
}); 