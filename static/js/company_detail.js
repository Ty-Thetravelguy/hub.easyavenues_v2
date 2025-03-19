$(document).ready(function() {
    // Initialize DataTable for company contacts
    $('#company-contacts-table').DataTable({
        "pageLength": 10,
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
            "lengthMenu": "Show _MENU_ contacts per page",
            "info": "Showing _START_ to _END_ of _TOTAL_ contacts",
            "infoEmpty": "No contacts available",
            "infoFiltered": "(filtered from _MAX_ total contacts)",
            "zeroRecords": "No matching contacts found"
        }
    });

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
}); 