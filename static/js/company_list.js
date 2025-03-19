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
            
            // Initialize DataTable with all features
            var dataTable = table.DataTable({
                "pageLength": 25,
                "order": [[0, "asc"]],
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
                    "lengthMenu": "Show _MENU_ entries per page",
                    "info": "Showing _START_ to _END_ of _TOTAL_ entries",
                    "infoEmpty": "No entries available",
                    "infoFiltered": "(filtered from _MAX_ total entries)",
                    "zeroRecords": "No matching entries found",
                    "search": "Search:"
                }
            });
            
            console.log('✅ ' + tableType + ' table initialized');
        } else {
            console.warn('⚠️ ' + tableType + ' table not found on this page');
        }
    }
}); 