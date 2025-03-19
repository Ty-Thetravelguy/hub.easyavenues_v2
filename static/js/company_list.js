$(document).ready(function() {
    var showContacts = $('.container-fluid').data('show-contacts');
    
    var commonConfig = {
        "pageLength": 25,
        "order": [[0, "asc"]],
        "dom": '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6">>rt<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
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
        ]
    };

    if (!showContacts) {
        commonConfig.language = {
            "lengthMenu": "Show _MENU_ companies per page",
            "info": "Showing _START_ to _END_ of _TOTAL_ companies",
            "infoEmpty": "No companies available",
            "infoFiltered": "(filtered from _MAX_ total companies)",
            "zeroRecords": "No matching companies found"
        };
        $('#companies-table').DataTable(commonConfig);
    } else {
        commonConfig.language = {
            "lengthMenu": "Show _MENU_ contacts per page",
            "info": "Showing _START_ to _END_ of _TOTAL_ contacts",
            "infoEmpty": "No contacts available",
            "infoFiltered": "(filtered from _MAX_ total contacts)",
            "zeroRecords": "No matching contacts found"
        };
        $('#contacts-table').DataTable(commonConfig);
    }
}); 