$(document).ready(function() {
    console.log('🔍 CONTACT LIST JS LOADED');
    
    // Attempt to find the table
    var contactsTable = $('#contacts-table');
    console.log('📊 Contact table found?', contactsTable.length > 0);
    
    if (contactsTable.length) {
        console.log('⚙️ Configuring contact DataTable');
        
        // Add sort icons to each header before initialization
        contactsTable.find('th').each(function(index) {
            // Skip the last column (Actions)
            if (index < contactsTable.find('th').length - 1) {
                // Only add icon if it doesn't already exist
                if ($(this).find('.sort-icon').length === 0) {
                    $(this).prepend('<i class="fas fa-sort sort-icon"></i>');
                }
            }
        });
        
        // Initialize DataTable with all features
        var dataTable = contactsTable.DataTable({
            "pageLength": 25,
            "order": [[0, "asc"]],
            "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
            "autoWidth": false,
            "scrollX": true,
            "ordering": true,
            "orderCellsTop": true,
            "fixedHeader": true,
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
                
                // IMPORTANT: Fix for double arrows - remove any DataTables generated arrow elements
                // This is a more aggressive approach since CSS isn't working
                setTimeout(function() {
                    contactsTable.find('th').each(function() {
                        // Check if this header has any generated pseudo-elements for sorting
                        var $th = $(this);
                        var computedStyle = window.getComputedStyle($th[0], ':before');
                        
                        // If we detect any content in the pseudo-elements, add a special class
                        if (computedStyle && computedStyle.content && computedStyle.content !== 'none') {
                            $th.addClass('dt-arrow-removed');
                            $th.attr('style', $th.attr('style') + '; content: none !important; background-image: none !important;');
                        }
                        
                        // Also check :after pseudo-element
                        computedStyle = window.getComputedStyle($th[0], ':after');
                        if (computedStyle && computedStyle.content && computedStyle.content !== 'none') {
                            $th.addClass('dt-arrow-removed');
                            $th.attr('style', $th.attr('style') + '; content: none !important; background-image: none !important;');
                        }
                    });
                }, 0);
            },
            // Additional option to completely disable DataTables styling
            "bSortClasses": false
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
        
        // Direct removal of any existing sort indicators after initialization
        // Some browsers or DataTables versions may still add the indicators despite CSS
        setTimeout(function() {
            // Add a style element to force hide any content in pseudo-elements
            if (!$('#dt-force-hide-arrows').length) {
                $('head').append(
                    '<style id="dt-force-hide-arrows">' +
                    'table.dataTable thead th:before, ' +
                    'table.dataTable thead th:after { ' +
                    '   content: none !important; ' +
                    '   display: none !important; ' +
                    '   opacity: 0 !important; ' +
                    '   visibility: hidden !important; ' +
                    '} ' +
                    '</style>'
                );
            }
        }, 100);
        
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
            table.find('th').removeClass('sorting_asc sorting_desc').addClass('sorting');
            
            // Get the header cell being sorted
            var sortedHeader = table.find('th').eq(columnIndex);
            
            // Update the sort icon and header class
            if (direction === 'asc') {
                sortedHeader.find('.sort-icon').removeClass('fa-sort').addClass('fa-sort-up');
                sortedHeader.removeClass('sorting').addClass('sorting_asc');
                console.log('Sort ascending on column', columnIndex);
            } else {
                sortedHeader.find('.sort-icon').removeClass('fa-sort').addClass('fa-sort-down');
                sortedHeader.removeClass('sorting').addClass('sorting_desc');
                console.log('Sort descending on column', columnIndex);
            }
            
            console.log('🔄 Sort icons updated successfully');
        } catch (e) {
            console.error('❌ Error updating sort icons:', e);
        }
    }
}); 