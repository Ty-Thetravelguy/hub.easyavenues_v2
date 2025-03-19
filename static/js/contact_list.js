$(document).ready(function() {
    console.log('🔍 CONTACT LIST JS LOADED');
    
    // Attempt to find the table
    var contactsTable = $('#contacts-table');
    console.log('📊 Contact table found?', contactsTable.length > 0);
    
    if (contactsTable.length) {
        console.log('⚙️ Configuring contact DataTable');
        
        // Initialize DataTable with all features
        var dataTable = contactsTable.DataTable({
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
        
        console.log('✅ Contact table initialized');
    } else {
        console.error('❌ Contact table not found!');
    }
}); 