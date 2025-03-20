$(document).ready(function() {
    $('.select2').select2({
        placeholder: "🔍 Search and select travelers...",
        allowClear: true,
        width: '100%',
        theme: 'bootstrap4',
        escapeMarkup: function(markup) {
            return markup;
        },
        templateResult: formatContact,
        templateSelection: formatContactSelection,
        matcher: customMatcher,
        minimumInputLength: 0,  // Start showing options immediately
        language: {
            inputTooShort: function() {
                return "Start typing to search travelers";
            },
            searching: function() {
                return "Searching...";
            },
            noResults: function() {
                return "No travelers found with that name";
            }
        }
    });

    // Force placeholder to be properly positioned on load
    setTimeout(function() {
        // Adjust placeholder position and styling
        $('.select2-search__field').css({
            'margin': '0',
            'padding': '0.5rem',
            'height': '34px',
            'line-height': '34px'
        });
        
        // Focus on the placeholder text field so it's immediately visible
        $('.select2-search__field').focus().blur();
    }, 200);

    // Focus on the search box when clicking the search hint
    $('.search-hint').click(function() {
        $('#vip_travelers').select2('open');
        setTimeout(function() {
            $('.select2-search__field').focus();
        }, 100);
    });

    // Select all VIP travelers button
    $('#select-all-vips').click(function(e) {
        e.preventDefault();
        
        // Get all options with data-is-vip=true
        var vipOptions = $('#vip_travelers option[data-is-vip="true"]');
        
        // Create an array of VIP option values
        var vipValues = vipOptions.map(function() {
            return this.value;
        }).get();
        
        // Set the select value to include all VIP travelers
        $('#vip_travelers').val(vipValues).trigger('change');
        
        // Show a temporary success message
        var $btn = $(this);
        var originalText = $btn.html();
        $btn.html('<i class="fas fa-check me-1"></i>Selected');
        $btn.removeClass('btn-outline-warning').addClass('btn-success');
        
        setTimeout(function() {
            $btn.html(originalText);
            $btn.removeClass('btn-success').addClass('btn-outline-warning');
        }, 1500);
    });

    // Custom matcher to improve search functionality
    function customMatcher(params, data) {
        // If there are no search terms, return all of the data
        if ($.trim(params.term) === '') {
            return data;
        }
        
        // Search through first name, last name and job role
        var searchParts = params.term.toLowerCase().split(' ');
        var text = data.text.toLowerCase();
        
        // Check if all search parts are found in the text
        var allPartsFound = searchParts.every(function(part) {
            return text.indexOf(part) > -1;
        });
        
        if (allPartsFound) {
            return data;
        }
        
        // Return null to indicate no match
        return null;
    }

    // Format dropdown options
    function formatContact(contact) {
        if (!contact.id) {
            return contact.text;
        }
        
        var isVip = $(contact.element).data('is-vip');
        var vipLabel = isVip ? '<span class="badge bg-warning ms-2">VIP</span>' : '';
        
        // Create HTML representation
        var $contact = $(
            '<div class="select2-result-contact d-flex align-items-center p-1 '+ (isVip ? 'select2-vip-contact' : '') +'">' +
                '<div class="select2-result-contact__avatar me-2">' +
                    '<div class="avatar-circle avatar-circle-sm bg-primary">' +
                        '<span class="initials">' + 
                            contact.text.split(' ')[0].charAt(0) + 
                            (contact.text.split(' ').length > 1 ? contact.text.split(' ')[1].charAt(0) : '') +
                        '</span>' +
                    '</div>' +
                '</div>' +
                '<div class="select2-result-contact__info">' +
                    '<div class="select2-result-contact__title">' + contact.text + vipLabel + '</div>' +
                '</div>' +
            '</div>'
        );
        
        return $contact;
    }

    // Format selected option
    function formatContactSelection(contact) {
        if (!contact.id) {
            return contact.text;
        }
        
        var isVip = $(contact.element).data('is-vip');
        if (isVip) {
            return contact.text + ' ⭐';
        }
        return contact.text;
    }

    // Also open the dropdown when clicking on the label
    $('label:contains("VIP Travelers")').css('cursor', 'pointer').click(function() {
        $('#vip_travelers').select2('open');
        setTimeout(function() {
            $('.select2-search__field').focus();
        }, 100);
    });
}); 