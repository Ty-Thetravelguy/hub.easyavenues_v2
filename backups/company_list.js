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
            
            // Add sort icons to each header before initialization
            table.find('th').each(function(index) {
                // Skip the last column (Actions)
                if (index < table.find('th').length - 1) {
                    // Only add icon if it doesn't already exist
                    if ($(this).find('.sort-icon').length === 0) {
                        $(this).prepend('<i class="fas fa-sort sort-icon"></i>');
                    }
                }
            });
            
            // Initialize DataTable with all features
            var dataTable = table.DataTable({
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
                    updateSortIcons(table);
                    
                    // IMPORTANT: Fix for double arrows - remove any DataTables generated arrow elements
                    // This is a more aggressive approach since CSS isn't working
                    setTimeout(function() {
                        table.find('th').each(function() {
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
            
            // Direct removal of any existing sort indicators after initialization
            // Some browsers or DataTables versions may still add the indicators despite CSS
            setTimeout(function() {
                // Add a style element to force hide any content in pseudo-elements
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
            }, 100);
            
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