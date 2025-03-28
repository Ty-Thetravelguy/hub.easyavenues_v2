document.addEventListener('DOMContentLoaded', function() {
  // Fix activity type card icons color styling
  const styleFixElement = document.createElement('style');
  styleFixElement.textContent = `
    .activity-type-card .fa-envelope { color: #444a9f !important; }
    .activity-type-card .fa-phone-alt { color: #9c85db !important; }
    .activity-type-card .fa-sticky-note { color: #f9f871 !important; }
    .activity-type-card .fa-users { color: #a44493 !important; }
    .activity-type-card .fa-exclamation-triangle { color: #ff8568 !important; }
  `;
  document.head.appendChild(styleFixElement);
  
  // CSRF token handling - use a function that doesn't duplicate base.js if possible
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  
  const csrftoken = getCookie('csrftoken');
  
  // Set up AJAX defaults once
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  // Track current activity being viewed/edited
  let currentActivityId = null;
  let currentActivityData = null;
  let currentActivityType = null;

  // Activity Details Modal Handler
  function setupActivityDetailsModal() {
    $('#activity-details-modal').on('show.bs.modal', function(event) {
      const button = $(event.relatedTarget);
      const activityId = button.data('activity-id');
      const activityType = button.data('activity-type');
      currentActivityId = activityId;
      currentActivityType = activityType;
      
      const modal = $(this);
      
      // Set loading state
      modal.find('.modal-title').text(getActivityTypeTitle(activityType) + ' Details');
      modal.find('#activity-details-content').html(getLoadingHTML());
      
      // Fetch activity details
      fetchActivityDetails(activityId, modal);
    });
  }
  
  // Helper function to get type-specific title
  function getActivityTypeTitle(type) {
    const titles = {
      'email': 'Email',
      'call': 'Call',
      'note': 'Note',
      'meeting': 'Meeting',
      'exception': 'Waiver/Favor'
    };
    return titles[type] || 'Activity';
  }
  
  // Loading HTML helper
  function getLoadingHTML() {
    return `
      <div class="text-center py-4">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2">Loading activity details...</p>
      </div>
    `;
  }
  
  // Fetch activity details via AJAX
  function fetchActivityDetails(activityId, modal) {
    $.ajax({
      url: '/crm/activity/' + activityId + '/details/',
      type: 'GET',
      dataType: 'json',
      success: function(data) {
        currentActivityData = data;
        const contentHtml = formatActivityDetails(currentActivityType, data);
        modal.find('#activity-details-content').html(contentHtml);
      },
      error: function(xhr, status, error) {
        modal.find('#activity-details-content').html(`
          <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            Unable to load activity details.
          </div>
        `);
      }
    });
  }
  
  // Format activity details based on type
  function formatActivityDetails(activityType, data) {
    let contentHtml = '';
    
    // Format based on activity type
    if (activityType === 'email') {
      contentHtml = `
        <div class="mb-3">
          <strong>Subject:</strong> ${data.data.subject || 'N/A'}
        </div>
        <div class="mb-3">
          <strong>Recipients:</strong> ${data.data.recipient_names ? data.data.recipient_names.join(', ') : 'No recipients'}
        </div>
        <div class="mb-3">
          <strong>Message:</strong>
          <div class="p-3 bg-light rounded">${data.data.content || 'No content'}</div>
        </div>
      `;
    } else if (activityType === 'call') {
      contentHtml = `
        <div class="mb-3">
          <strong>Contact:</strong> ${data.data.contact_name || 'N/A'}
        </div>
        <div class="mb-3">
          <strong>Duration:</strong> ${data.data.duration ? data.data.duration + ' minutes' : 'N/A'}
        </div>
        <div class="mb-3">
          <strong>Summary:</strong>
          <div class="p-3 bg-light rounded">${data.data.summary || 'No summary'}</div>
        </div>
      `;
    } else if (activityType === 'note') {
      contentHtml = `
        <div class="mb-3">
          <strong>Note:</strong>
          <div class="p-3 bg-light rounded">${data.content || 'No content'}</div>
        </div>
      `;
    } else if (activityType === 'meeting') {
      contentHtml = `
        <div class="mb-3">
          <strong>Title:</strong> ${data.data.title || 'N/A'}
        </div>
        <div class="mb-3">
          <strong>Date:</strong> ${data.data.date || 'N/A'}
        </div>
        <div class="mb-3">
          <strong>Time:</strong> ${data.data.start_time || 'N/A'} - ${data.data.end_time || 'N/A'}
        </div>
        <div class="mb-3">
          <strong>Location:</strong> ${data.data.location || 'N/A'}
        </div>
        <div class="mb-3">
          <strong>Attendees:</strong> ${data.data.attendee_names ? data.data.attendee_names.join(', ') : 'None specified'}
        </div>
        <div class="mb-3">
          <strong>Notes:</strong>
          <div class="p-3 bg-light rounded">${data.data.notes || 'No notes'}</div>
        </div>
      `;
    } else if (activityType === 'exception') {
      contentHtml = `
        <div class="mb-3">
          <strong>Type:</strong> ${data.data.exception_type ? data.data.exception_type.replace('_', ' ').toUpperCase() : 'N/A'}
        </div>
        <div class="mb-3">
          <strong>Value:</strong> ${data.data.value_amount ? '£' + data.data.value_amount : 'N/A'}
        </div>
        <div class="mb-3">
          <strong>For Contact:</strong> ${data.data.contact_name || 'N/A'}
        </div>
        <div class="mb-3">
          <strong>Approved By:</strong> ${data.data.approved_by ? data.data.approved_by.replace('_', ' ').toUpperCase() : 'N/A'}
        </div>
        <div class="mb-3">
          <strong>Description:</strong>
          <div class="p-3 bg-light rounded">${data.data.description || 'No description'}</div>
        </div>
      `;
    }
    
    // Add meta information
    contentHtml += `
      <div class="mt-4 pt-3 border-top text-muted small">
        <div><i class="far fa-clock me-1"></i> ${data.performed_at}</div>
        <div><i class="far fa-user me-1"></i> ${data.performed_by}</div>
      </div>
    `;
    
    return contentHtml;
  }

  // Set up edit button handler
  function setupEditButton() {
    $('#edit-activity-btn').on('click', function() {
      $('#activity-details-modal').modal('hide');
      
      setTimeout(function() {
        const editModal = $('#edit-activity-modal');
        editModal.find('.modal-title').text('Edit ' + getActivityTypeTitle(currentActivityType));
        
        // Load the edit form via AJAX or use existing form structure
        // This avoids building complex HTML in JavaScript
        $.ajax({
          url: '/crm/activity/' + currentActivityId + '/edit-form/',
          type: 'GET',
          success: function(response) {
            $('#edit-activity-form-container').html(response);
            
            // Initialize any needed functionality
            setupEditFormSubmission();
            
            // Show edit modal
            editModal.modal('show');
          },
          error: function() {
            alert('Error loading edit form');
          }
        });
      }, 300);
    });
  }
  
  // Set up edit form submission
  function setupEditFormSubmission() {
    $('#edit-activity-form').on('submit', function(e) {
      e.preventDefault();
      
      const formData = $(this).serialize();
      
      $.ajax({
        url: '/crm/activity/' + currentActivityId + '/edit/',
        type: 'POST',
        data: formData,
        dataType: 'json',
        success: function(response) {
          $('#edit-activity-modal').modal('hide');
          location.reload();
        },
        error: function(xhr, status, error) {
          let errorMessage = 'An error occurred while updating the activity.';
          if (xhr.responseJSON && xhr.responseJSON.error) {
            errorMessage = xhr.responseJSON.error;
          }
          
          $('#edit-activity-form-container').prepend(`
            <div class="alert alert-danger">
              <i class="fas fa-exclamation-triangle me-2"></i>
              ${errorMessage}
            </div>
          `);
        }
      });
    });
  }
  
  // Set up delete button
  function setupDeleteButton() {
    $('#delete-activity-btn').on('click', function() {
      $('#activity-details-modal').modal('hide');
      
      setTimeout(function() {
        const deleteModal = $('#delete-activity-modal');
        
        $('#delete-activity-details').html(`
          <strong>Activity:</strong> ${currentActivityData.description}<br>
          <strong>Date:</strong> ${currentActivityData.performed_at}
        `);
        
        $('#confirm-delete-btn').off('click').on('click', function() {
          $.ajax({
            url: '/crm/activity/' + currentActivityId + '/delete/',
            type: 'POST',
            data: {
              'csrfmiddlewaretoken': csrftoken
            },
            dataType: 'json',
            success: function(response) {
              deleteModal.modal('hide');
              location.reload();
            },
            error: function(xhr, status, error) {
              let errorMessage = 'An error occurred while deleting the activity.';
              if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
              }
              
              deleteModal.find('.modal-body').prepend(`
                <div class="alert alert-danger">
                  <i class="fas fa-exclamation-triangle me-2"></i>
                  ${errorMessage}
                </div>
              `);
            }
          });
        });
        
        deleteModal.modal('show');
      }, 300);
    });
  }
  
  // Activity type selection in log activity modal
  function setupActivityTypeSelection() {
    const activityTypeCards = document.querySelectorAll('.activity-type-card');
    const formContainer = document.getElementById('activity-form-container');
    
    // Reset form container when modal is closed
    $('#logActivityModal').on('hidden.bs.modal', function() {
      formContainer.innerHTML = `
        <div class="text-center py-4">
          <p>Please select an activity type above to start logging.</p>
        </div>
      `;
      activityTypeCards.forEach(card => {
        card.classList.remove('active');
      });
    });
    
    // Handle activity type card clicks
    activityTypeCards.forEach(card => {
      card.addEventListener('click', function() {
        const activityType = this.dataset.activityType;
        
        // Remove active class from all cards
        activityTypeCards.forEach(c => c.classList.remove('active'));
        
        // Add active class to clicked card
        this.classList.add('active');
        
        // Show loading indicator
        formContainer.innerHTML = getLoadingHTML();
        
        // Load form via AJAX
        $.ajax({
          url: `/crm/activity-form/${activityType}/`,
          type: 'GET',
          success: function(response) {
            formContainer.innerHTML = response;
            setupActivityFormSubmission(activityType);
          },
          error: function() {
            formContainer.innerHTML = `
              <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error loading form.
              </div>
            `;
          }
        });
      });
    });
    
    // Show email form by default when modal is opened
    $('#logActivityModal').on('shown.bs.modal', function() {
      const emailCard = document.querySelector('.activity-type-card[data-activity-type="email"]');
      if (emailCard) {
        emailCard.click();
      }
    });
  }
  
  // Set up activity form submission
  function setupActivityFormSubmission(activityType) {
    $('#log-activity-form').on('submit', function(e) {
      e.preventDefault();
      
      const formData = $(this).serialize();
      const companyId = window.location.pathname.split('/').filter(Boolean).pop();
      
      $.ajax({
        url: `/crm/companies/${companyId}/log-activity/${activityType}/`,
        type: 'POST',
        data: formData,
        dataType: 'json',
        success: function(response) {
          $('#logActivityModal').modal('hide');
          location.reload();
        },
        error: function(xhr, status, error) {
          let errorMessage = 'An error occurred while saving the activity.';
          if (xhr.responseJSON && xhr.responseJSON.error) {
            errorMessage = xhr.responseJSON.error;
          }
          
          $('#log-activity-form').prepend(`
            <div class="alert alert-danger">
              <i class="fas fa-exclamation-triangle me-2"></i>
              ${errorMessage}
            </div>
          `);
        }
      });
    });
  }
  
  // Initialize all functionality
  $(document).ready(function() {
    setupActivityDetailsModal();
    setupEditButton();
    setupDeleteButton();
    setupActivityTypeSelection();
  });
}); 