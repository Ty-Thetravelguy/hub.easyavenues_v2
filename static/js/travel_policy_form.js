$(document).ready(function() {
    // Initialize Select2 with minimal custom options first
    $('.select2').select2({
        placeholder: "🔍 Search and select travelers...",
        allowClear: true,
        width: '100%',
        theme: 'bootstrap4',
        templateResult: formatContact,
        templateSelection: formatContactSelection,
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

    // Default Select2 styling adjustments
    setTimeout(function() {
        $('.select2-search__field').css({
            'margin': '0',
            'padding': '0.5rem',
            'height': '34px',
            'line-height': '34px'
        });
    }, 300);

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

    // Format dropdown options
    function formatContact(contact) {
        if (!contact.id) {
            return contact.text;
        }
        
        var isVip = $(contact.element).data('is-vip');
        var vipLabel = isVip ? '<span class="badge bg-warning ms-2">VIP</span>' : '';
        
        // Get initials safely
        var nameParts = contact.text.split('-')[0].trim().split(' ');
        var firstInitial = nameParts.length > 0 ? nameParts[0].charAt(0) : '';
        var secondInitial = nameParts.length > 1 ? nameParts[1].charAt(0) : '';
        
        // Create HTML representation
        var $contact = $(
            '<div class="select2-result-contact d-flex align-items-center p-1 '+ (isVip ? 'select2-vip-contact' : '') +'">' +
                '<div class="select2-result-contact__avatar me-2">' +
                    '<div class="avatar-circle avatar-circle-sm bg-primary">' +
                        '<span class="initials">' + firstInitial + secondInitial + '</span>' +
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

    // Make the label and icon clickable 
    $('label[for="vip_travelers"], .fa-search').css('cursor', 'pointer').click(function() {
        $('#vip_travelers').select2('open');
    });
    
    // ESSENTIAL FIX: Override Select2's search to make it work with our data
    $(document).on('keyup', '.select2-search__field', function() {
        var searchText = $(this).val().toLowerCase();
        
        if (searchText.length > 0) {
            // Show/hide options based on simple text search
            $('#vip_travelers option').each(function() {
                var optionText = $(this).text().toLowerCase();
                var optionElement = $(this);
                
                // Check if the search text appears anywhere in the option
                if (optionText.indexOf(searchText) > -1) {
                    // Make this option visible in the dropdown
                    var optionId = $(this).val();
                    var matchingDropdownItem = $('.select2-results__option[aria-selected] li').filter(function() {
                        return $(this).text().toLowerCase().indexOf(optionText) > -1;
                    });
                    
                    if (matchingDropdownItem.length) {
                        matchingDropdownItem.show();
                        matchingDropdownItem.closest('.select2-results__option').show();
                    }
                }
            });
        }
    });
}); 