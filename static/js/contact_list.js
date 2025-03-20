$(document).ready(function() {
    console.log('🔍 CONTACT LIST JS LOADED');
    
    // Attempt to find the table
    var contactsTable = $('#contacts-table');
    console.log('📊 Contact table found?', contactsTable.length > 0);
    
    if (contactsTable.length) {
        console.log('⚙️ Configuring contact DataTable');
        
        // Add the custom styles for the table first
        $('head').append(`
            <style id="datatable-contact-styles">
                /* Force correct table layout */
                #contacts-table {
                    width: 100% !important;
                    table-layout: fixed !important;
                }
                
                /* Header styles */
                #contacts-table th {
                    position: relative !important;
                    padding-left: 28px !important;
                    text-align: left !important;
                    white-space: nowrap !important;
                    overflow: hidden !important;
                    text-overflow: ellipsis !important;
                }
                
                /* Sort icon styles */
                #contacts-table th .sort-icon {
                    position: absolute !important;
                    left: 10px !important;
                    top: 50% !important;
                    transform: translateY(-50%) !important;
                    color: #aaa !important;
                }
                
                /* Active sort color */
                #contacts-table th.sorting_asc .sort-icon,
                #contacts-table th.sorting_desc .sort-icon {
                    color: #000 !important;
                }
                
                /* Hide DataTables sort indicators */
                #contacts-table thead .sorting:before,
                #contacts-table thead .sorting:after,
                #contacts-table thead .sorting_asc:before,
                #contacts-table thead .sorting_asc:after,
                #contacts-table thead .sorting_desc:before,
                #contacts-table thead .sorting_desc:after {
                    display: none !important;
                }
            </style>
        `);
        
        // First, remove any existing sort icons to prevent duplicates
        contactsTable.find('th .sort-icon').remove();
        
        // Initialize DataTable with all features BEFORE adding icons
        var dataTable = contactsTable.DataTable({
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
                updateSortIcons(contactsTable);
            }
        });
        
        // Add icons AFTER DataTable initialization
        contactsTable.find('thead th').each(function(index) {
            // Skip the last column (Actions)
            if (index < contactsTable.find('thead th').length - 1) {
                // prepend the icon (don't replace the content)
                $(this).prepend('<i class="fas fa-sort sort-icon"></i>');
            }
        });
        
        // Add click handlers to headers for immediate icon update
        contactsTable.find('th').each(function(index) {
            if (index < contactsTable.find('th').length - 1) { // Skip last column (Actions)
                $(this).on('click', function() {
                    setTimeout(function() {
                        updateSortIcons(contactsTable);
                    }, 50);
                });
            }
        });
        
        // Initial update of the sort icons
        updateSortIcons(contactsTable);
        
        // Force column widths to recalculate
        dataTable.columns.adjust().draw();
        
        console.log('✅ Contact table sorting initialized');
    } else {
        console.error('❌ Contact table not found!');
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