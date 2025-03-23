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
  
  // Setup CSRF token for all AJAX requests
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
  
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });

  let currentActivityId = null;
  let currentActivityData = null;
  let currentActivityType = null;

  $(document).ready(function() {
    // Activity Details Modal Event Handlers
    $('#activity-details-modal').on('show.bs.modal', function(event) {
      const button = $(event.relatedTarget);
      const activityId = button.data('activity-id');
      const activityType = button.data('activity-type');
      currentActivityId = activityId;
      currentActivityType = activityType;
      
      const modal = $(this);
      
      // Set loading state
      modal.find('.modal-title').text('Loading...');
      modal.find('#activity-details-content').html(
        '<div class="text-center py-4">' +
        '<div class="spinner-border text-primary" role="status"></div>' +
        '<p class="mt-2">Loading activity details...</p>' +
        '</div>'
      );
      
      // Set title based on activity type
      if (activityType === 'email') {
        modal.find('.modal-title').text('Email Details');
      } else if (activityType === 'call') {
        modal.find('.modal-title').text('Call Details');
      } else if (activityType === 'note') {
        modal.find('.modal-title').text('Note Details');
      } else if (activityType === 'meeting') {
        modal.find('.modal-title').text('Meeting Details');
      } else if (activityType === 'exception') {
        modal.find('.modal-title').text('Waiver/Favor Details');
      }
      
      // Fetch activity details from API
      $.ajax({
        url: '/crm/activity/' + activityId + '/details/',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
          let contentHtml = '';
          
          // Store the current activity data for edit/delete modals
          currentActivityData = data;
          
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
                <div class="p-3 bg-light rounded">${data.data.content || 'No content'}</div>
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
          
          modal.find('#activity-details-content').html(contentHtml);
        },
        error: function(xhr, status, error) {
          modal.find('#activity-details-content').html(
            '<div class="alert alert-danger">' +
            '<i class="fas fa-exclamation-triangle me-2"></i>' +
            'Unable to load activity details.' +
            '</div>'
          );
        }
      });
    });
    
    // Edit button handler
    $('#edit-activity-btn').on('click', function() {
      // Hide activity details modal
      $('#activity-details-modal').modal('hide');
      
      // Open edit modal
      setTimeout(function() {
        const editModal = $('#edit-activity-modal');
        
        // Set modal title
        if (currentActivityType === 'email') {
          editModal.find('.modal-title').text('Edit Email');
        } else if (currentActivityType === 'call') {
          editModal.find('.modal-title').text('Edit Call');
        } else if (currentActivityType === 'note') {
          editModal.find('.modal-title').text('Edit Note');
        } else if (currentActivityType === 'meeting') {
          editModal.find('.modal-title').text('Edit Meeting');
        } else if (currentActivityType === 'exception') {
          editModal.find('.modal-title').text('Edit Waiver/Favor');
        }
        
        // Build the edit form based on activity type
        let formHtml = `
          <form id="edit-activity-form">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
            <input type="hidden" name="activity_id" value="${currentActivityId}">
            
            <div class="mb-3">
              <label for="description" class="form-label">Description</label>
              <input type="text" class="form-control" id="description" name="description" value="${currentActivityData.description}" required>
            </div>
        `;
        
        // Add fields based on activity type
        if (currentActivityType === 'note') {
          formHtml += `
            <div class="mb-3">
              <label for="content" class="form-label">Content</label>
              <textarea class="form-control" id="content" name="content" rows="5" required>${currentActivityData.data.content || ''}</textarea>
            </div>
          `;
        } else if (currentActivityType === 'call') {
          formHtml += `
            <div class="mb-3">
              <label for="contact_id" class="form-label">Contact</label>
              <select class="form-select" id="contact_id" name="contact_id">
                <option value="">No specific contact</option>
                <!-- Contacts will be loaded dynamically -->
              </select>
            </div>
            
            <div class="mb-3">
              <label for="duration" class="form-label">Duration (minutes)</label>
              <input type="number" class="form-control" id="duration" name="duration" value="${currentActivityData.data.duration || ''}">
            </div>
            
            <div class="mb-3">
              <label for="summary" class="form-label">Summary</label>
              <textarea class="form-control" id="summary" name="summary" rows="4">${currentActivityData.data.summary || ''}</textarea>
            </div>
          `;
        } else if (currentActivityType === 'email') {
          formHtml += `
            <div class="mb-3">
              <label for="subject" class="form-label">Subject</label>
              <input type="text" class="form-control" id="subject" name="subject" value="${currentActivityData.data.subject || ''}">
            </div>
            
            <div class="mb-3">
              <label for="recipients" class="form-label">Recipients</label>
              <select class="form-select" id="recipients" name="recipients" multiple>
                <!-- Recipients will be loaded dynamically -->
              </select>
              <small class="form-text text-muted">Hold Ctrl (or Cmd on Mac) to select multiple contacts</small>
            </div>
            
            <div class="mb-3">
              <label for="content" class="form-label">Content</label>
              <textarea class="form-control" id="content" name="content" rows="5">${currentActivityData.data.content || ''}</textarea>
            </div>
          `;
        } else if (currentActivityType === 'meeting') {
          formHtml += `
            <div class="mb-3">
              <label for="title" class="form-label">Title</label>
              <input type="text" class="form-control" id="title" name="title" value="${currentActivityData.data.title || ''}">
            </div>
            
            <div class="mb-3">
              <label for="date" class="form-label">Date</label>
              <input type="date" class="form-control" id="date" name="date" value="${currentActivityData.data.date || ''}">
            </div>
            
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="start_time" class="form-label">Start Time</label>
                  <input type="time" class="form-control" id="start_time" name="start_time" value="${currentActivityData.data.start_time || ''}">
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <label for="end_time" class="form-label">End Time</label>
                  <input type="time" class="form-control" id="end_time" name="end_time" value="${currentActivityData.data.end_time || ''}">
                </div>
              </div>
            </div>
            
            <div class="mb-3">
              <label for="location" class="form-label">Location</label>
              <input type="text" class="form-control" id="location" name="location" value="${currentActivityData.data.location || ''}">
            </div>
            
            <div class="mb-3">
              <label for="attendees" class="form-label">Attendees</label>
              <select class="form-select" id="attendees" name="attendees" multiple>
                <!-- Attendees will be loaded dynamically -->
              </select>
              <small class="form-text text-muted">Hold Ctrl (or Cmd on Mac) to select multiple attendees</small>
            </div>
            
            <div class="mb-3">
              <label for="notes" class="form-label">Notes</label>
              <textarea class="form-control" id="notes" name="notes" rows="4">${currentActivityData.data.notes || ''}</textarea>
            </div>
          `;
        } else if (currentActivityType === 'exception') {
          formHtml += `
            <div class="mb-3">
              <label for="exception_type" class="form-label">Type</label>
              <select class="form-select" id="exception_type" name="exception_type">
                <option value="refund_waiver" ${currentActivityData.data.exception_type === 'refund_waiver' ? 'selected' : ''}>Refund Waiver</option>
                <option value="fee_waiver" ${currentActivityData.data.exception_type === 'fee_waiver' ? 'selected' : ''}>Fee Waiver</option>
                <option value="loyalty_points" ${currentActivityData.data.exception_type === 'loyalty_points' ? 'selected' : ''}>Loyalty Points</option>
                <option value="rate_match" ${currentActivityData.data.exception_type === 'rate_match' ? 'selected' : ''}>Rate Match</option>
                <option value="other" ${currentActivityData.data.exception_type === 'other' ? 'selected' : ''}>Other</option>
              </select>
            </div>
            
            <div class="mb-3">
              <label for="value_amount" class="form-label">Value Amount (£)</label>
              <input type="number" step="0.01" class="form-control" id="value_amount" name="value_amount" value="${currentActivityData.data.value_amount || ''}">
            </div>
            
            <div class="mb-3">
              <label for="contact_id" class="form-label">For Contact</label>
              <select class="form-select" id="contact_id" name="contact_id">
                <option value="">No specific contact</option>
                <!-- Contacts will be loaded dynamically -->
              </select>
            </div>
            
            <div class="mb-3">
              <label for="approved_by" class="form-label">Approved By</label>
              <select class="form-select" id="approved_by" name="approved_by">
                <option value="manager" ${currentActivityData.data.approved_by === 'manager' ? 'selected' : ''}>Manager</option>
                <option value="director" ${currentActivityData.data.approved_by === 'director' ? 'selected' : ''}>Director</option>
                <option value="operations" ${currentActivityData.data.approved_by === 'operations' ? 'selected' : ''}>Operations</option>
                <option value="account_manager" ${currentActivityData.data.approved_by === 'account_manager' ? 'selected' : ''}>Account Manager</option>
              </select>
            </div>
            
            <div class="mb-3">
              <label for="exception_description" class="form-label">Description</label>
              <textarea class="form-control" id="exception_description" name="exception_description" rows="4">${currentActivityData.data.description || ''}</textarea>
            </div>
          `;
        }
        
        // Add form footer and close the form
        formHtml += `
            <div class="d-flex justify-content-between mt-4">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary">Save Changes</button>
            </div>
          </form>
        `;
        
        // Set form in the modal
        editModal.find('#edit-activity-form-container').html(formHtml);
        
        // Load contacts for dropdown selects if needed
        if (['call', 'email', 'meeting', 'exception'].includes(currentActivityType)) {
          $.ajax({
            url: window.location.pathname,
            data: { 'get_contacts': 'true' },
            type: 'GET',
            dataType: 'json',
            success: function(data) {
              if (data.contacts && data.contacts.length > 0) {
                let contactOptions = '';
                data.contacts.forEach(function(contact) {
                  const contactId = contact.id.toString();
                  
                  // For call and exception contact fields
                  if (['call', 'exception'].includes(currentActivityType)) {
                    const selected = contactId === (currentActivityData.data.contact_id || '').toString() ? 'selected' : '';
                    contactOptions += `<option value="${contactId}" ${selected}>${contact.first_name} ${contact.last_name}</option>`;
                  }
                });
                
                // Update contact select options
                if (['call', 'exception'].includes(currentActivityType)) {
                  $('#contact_id').append(contactOptions);
                }
                
                // For email recipients
                if (currentActivityType === 'email' && data.contacts.length > 0) {
                  let recipientOptions = '';
                  data.contacts.forEach(function(contact) {
                    const contactId = contact.id.toString();
                    const selected = currentActivityData.data.recipients && currentActivityData.data.recipients.includes(contactId) ? 'selected' : '';
                    recipientOptions += `<option value="${contactId}" ${selected}>${contact.first_name} ${contact.last_name}</option>`;
                  });
                  $('#recipients').append(recipientOptions);
                }
                
                // For meeting attendees
                if (currentActivityType === 'meeting' && data.contacts.length > 0) {
                  let attendeeOptions = '';
                  data.contacts.forEach(function(contact) {
                    const contactId = contact.id.toString();
                    const selected = currentActivityData.data.attendees && currentActivityData.data.attendees.includes(contactId) ? 'selected' : '';
                    attendeeOptions += `<option value="${contactId}" ${selected}>${contact.first_name} ${contact.last_name}</option>`;
                  });
                  $('#attendees').append(attendeeOptions);
                }
              }
            }
          });
        }
        
        // Initialize Select2 for multiple selects if needed
        if (['email', 'meeting'].includes(currentActivityType)) {
          setTimeout(function() {
            if ($.fn.select2) {
              $('#recipients, #attendees').select2({
                placeholder: 'Select contacts',
                width: '100%'
              });
            }
          }, 100);
        }
        
        // Handle form submission
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
              
              // Refresh the activities list without delay
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
        
        // Show edit modal
        editModal.modal('show');
      }, 500);
    });
    
    // Delete button handler
    $('#delete-activity-btn').on('click', function() {
      // Hide activity details modal
      $('#activity-details-modal').modal('hide');
      
      // Open delete confirmation modal
      setTimeout(function() {
        const deleteModal = $('#delete-activity-modal');
        
        // Set activity description in confirmation
        const activityDescription = currentActivityData.description;
        const activityPerformedAt = currentActivityData.performed_at;
        
        $('#delete-activity-details').html(`
          <strong>Activity:</strong> ${activityDescription}<br>
          <strong>Date:</strong> ${activityPerformedAt}
        `);
        
        // Handle delete confirmation
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
              
              // Refresh the activities list without delay
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
        
        // Show delete modal
        deleteModal.modal('show');
      }, 500);
    });
  });

  // Add the activity type selection handling
  // Handle activity type selection in logActivityModal
  const activityTypeCards = document.querySelectorAll('.activity-type-card');
  const formContainer = document.getElementById('activity-form-container');
  let activityTypeForForm = null;

  // Reset the form container when modal is closed
  $('#logActivityModal').on('hidden.bs.modal', function() {
    formContainer.innerHTML = `
      <div class="text-center py-4">
        <p>Please select an activity type above to start logging.</p>
      </div>
    `;
    // Remove active class from all cards
    activityTypeCards.forEach(card => {
      card.classList.remove('active');
    });
  });

  // Function to show the selected form
  function showSelectedForm(activityType) {
    // Remove active class from all cards
    activityTypeCards.forEach(card => {
      card.classList.remove('active');
    });
    
    // Add active class to selected card
    const selectedCard = document.querySelector(`.activity-type-card[data-activity-type="${activityType}"]`);
    if (selectedCard) {
      selectedCard.classList.add('active');
    }
    
    // Show loading indicator
    formContainer.innerHTML = `
      <div class="text-center py-4">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2">Loading form...</p>
      </div>
    `;
    
    // Clear any previous form elements
    while (formContainer.firstChild) {
      formContainer.removeChild(formContainer.firstChild);
    }
    
    // Create the form HTML based on activity type
    let formHtml = `
      <form id="log-activity-form" method="post">
        <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
    `;
    
    // Build different forms based on activity type
    if (activityType === 'email') {
      formHtml += `
        <div class="mb-3">
          <label for="subject" class="form-label">Subject</label>
          <input type="text" class="form-control" id="subject" name="subject" required>
        </div>
        
        <div class="mb-3">
          <label for="recipients" class="form-label">Recipients</label>
          <select class="form-select" id="recipients" name="recipients" multiple>
            <!-- Will be populated dynamically -->
          </select>
        </div>
        
        <div class="mb-3">
          <label for="content" class="form-label">Email Content</label>
          <textarea class="form-control" id="content" name="content" rows="5" required></textarea>
        </div>
      `;
    } else if (activityType === 'call') {
      formHtml += `
        <div class="mb-3">
          <label for="contact" class="form-label">Contact</label>
          <select class="form-select" id="contact" name="contact">
            <option value="">No specific contact</option>
            <!-- Will be populated dynamically -->
          </select>
        </div>
        
        <div class="mb-3">
          <label for="duration" class="form-label">Duration (minutes)</label>
          <input type="number" class="form-control" id="duration" name="duration">
        </div>
        
        <div class="mb-3">
          <label for="summary" class="form-label">Call Summary</label>
          <textarea class="form-control" id="summary" name="summary" rows="4" required></textarea>
        </div>
      `;
    } else if (activityType === 'note') {
      formHtml += `
        <div class="mb-3">
          <label for="content" class="form-label">Note Content</label>
          <textarea class="form-control" id="content" name="content" rows="5" required></textarea>
        </div>
      `;
    } else if (activityType === 'meeting') {
      formHtml += `
        <div class="mb-3">
          <label for="title" class="form-label">Meeting Title</label>
          <input type="text" class="form-control" id="title" name="title" required>
        </div>
        
        <div class="mb-3">
          <label for="date" class="form-label">Date</label>
          <input type="date" class="form-control" id="date" name="date" required>
        </div>
        
        <div class="row">
          <div class="col-md-6">
            <div class="mb-3">
              <label for="start_time" class="form-label">Start Time</label>
              <input type="time" class="form-control" id="start_time" name="start_time" required>
            </div>
          </div>
          <div class="col-md-6">
            <div class="mb-3">
              <label for="end_time" class="form-label">End Time</label>
              <input type="time" class="form-control" id="end_time" name="end_time" required>
            </div>
          </div>
        </div>
        
        <div class="mb-3">
          <label for="location" class="form-label">Location</label>
          <input type="text" class="form-control" id="location" name="location">
        </div>
        
        <div class="mb-3">
          <label for="attendees" class="form-label">Attendees</label>
          <select class="form-select" id="attendees" name="attendees" multiple>
            <!-- Will be populated dynamically -->
          </select>
        </div>
        
        <div class="mb-3">
          <label for="notes" class="form-label">Meeting Notes</label>
          <textarea class="form-control" id="notes" name="notes" rows="4"></textarea>
        </div>
      `;
    } else if (activityType === 'exception') {
      formHtml += `
        <div class="mb-3">
          <label for="exception_type" class="form-label">Type</label>
          <select class="form-select" id="exception_type" name="exception_type" required>
            <option value="refund_waiver">Refund Waiver</option>
            <option value="fee_waiver">Fee Waiver</option>
            <option value="loyalty_points">Loyalty Points</option>
            <option value="rate_match">Rate Match</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <div class="mb-3">
          <label for="value_amount" class="form-label">Value Amount (£)</label>
          <input type="number" step="0.01" class="form-control" id="value_amount" name="value_amount">
        </div>
        
        <div class="mb-3">
          <label for="contact" class="form-label">For Contact</label>
          <select class="form-select" id="contact" name="contact">
            <option value="">No specific contact</option>
            <!-- Will be populated dynamically -->
          </select>
        </div>
        
        <div class="mb-3">
          <label for="approved_by" class="form-label">Approved By</label>
          <select class="form-select" id="approved_by" name="approved_by" required>
            <option value="manager">Manager</option>
            <option value="director">Director</option>
            <option value="operations">Operations</option>
            <option value="account_manager">Account Manager</option>
          </select>
        </div>
        
        <div class="mb-3">
          <label for="description" class="form-label">Description</label>
          <textarea class="form-control" id="description" name="description" rows="4" required></textarea>
        </div>
      `;
    }
    
    // Add submit button and close form
    formHtml += `
        <div class="d-flex justify-content-between mt-4">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary">Save Activity</button>
        </div>
      </form>
    `;
    
    // Update the form container
    formContainer.innerHTML = formHtml;
    
    // Load contacts for form fields
    $.ajax({
      url: window.location.pathname,
      data: { 'get_contacts': 'true' },
      type: 'GET',
      dataType: 'json',
      success: function(data) {
        if (data.contacts && data.contacts.length > 0) {
          let contactOptions = '';
          data.contacts.forEach(function(contact) {
            contactOptions += `<option value="${contact.id}">${contact.first_name} ${contact.last_name}</option>`;
          });
          
          if (['call', 'exception'].includes(activityType)) {
            $('#contact').append(contactOptions);
          }
          
          if (activityType === 'email') {
            $('#recipients').append(contactOptions);
          }
          
          if (activityType === 'meeting') {
            $('#attendees').append(contactOptions);
          }
        }
      }
    });
    
    // Set up form submission
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
          
          $(formContainer).prepend(`
            <div class="alert alert-danger">
              <i class="fas fa-exclamation-triangle me-2"></i>
              ${errorMessage}
            </div>
          `);
        }
      });
    });
    
    // Initialize Select2 for multiple selects if needed
    if (window.jQuery && $.fn.select2 && ['email', 'meeting'].includes(activityType)) {
      setTimeout(function() {
        $('#recipients, #attendees').select2({
          width: '100%',
          placeholder: 'Select contacts'
        });
      }, 100);
    }
    
    // Store the current activity type
    activityTypeForForm = activityType;
  }
  
  // Add click handlers to activity type cards if they exist
  if (activityTypeCards.length) {
    activityTypeCards.forEach(card => {
      card.addEventListener('click', function() {
        const activityType = this.dataset.activityType;
        showSelectedForm(activityType);
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
}); 