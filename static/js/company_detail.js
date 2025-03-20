$(document).ready(function() {
    console.log('🔍 COMPANY DETAIL JS LOADED');
    
    // Initialize DataTable for company contacts
    var contactsTable = $('#company-contacts-table');
    
    if (contactsTable.length) {
        console.log('📊 Company contacts table found');
        
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

    // Initialize DataTable for company activities
    $('#company-activities-table').DataTable({
        "pageLength": 10,
        "order": [[0, "desc"]],
        "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
        "autoWidth": false,
        "scrollX": true,
        "ordering": true,
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
        "language": {
            "lengthMenu": "Show _MENU_ activities per page",
            "info": "Showing _START_ to _END_ of _TOTAL_ activities",
            "infoEmpty": "No activities available",
            "infoFiltered": "(filtered from _MAX_ total activities)",
            "zeroRecords": "No matching activities found"
        }
    });

    // Initialize DataTable for company documents
    $('#company-documents-table').DataTable({
        "pageLength": 10,
        "order": [[0, "desc"]],
        "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
        "autoWidth": false,
        "scrollX": true,
        "ordering": true,
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
        "language": {
            "lengthMenu": "Show _MENU_ documents per page",
            "info": "Showing _START_ to _END_ of _TOTAL_ documents",
            "infoEmpty": "No documents available",
            "infoFiltered": "(filtered from _MAX_ total documents)",
            "zeroRecords": "No matching documents found"
        }
    });
    
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
}); 