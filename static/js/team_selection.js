document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const teamSelect = document.getElementById('teamSelect');
    const teamMembersSection = document.getElementById('teamMembersSection');
    const teamMembersTableBody = document.getElementById('teamMembersTableBody');
    const selectUserBtn = document.getElementById('selectUserBtn');
    const teamMemberRowTemplate = document.getElementById('teamMemberRowTemplate');
    const modal = document.getElementById('teamSelectionModal');

    // Function to fetch team members from the API
    async function fetchTeamMembers(teamId) {
        try {
            const response = await fetch(`/accounts/api/teams/${teamId}/members/`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching team members:', error);
            return [];
        }
    }

    // Function to update the team members table
    function updateTeamMembersTable(members) {
        // Clear existing table body
        teamMembersTableBody.innerHTML = '';

        // Add new rows for each member
        members.forEach(member => {
            const template = teamMemberRowTemplate.content.cloneNode(true);
            const row = template.querySelector('tr');
            const radio = template.querySelector('input[type="radio"]');
            const nameCell = template.querySelector('.member-name');
            const roleCell = template.querySelector('.member-role');

            // Set data attributes and values
            radio.value = member.id;
            radio.dataset.name = member.full_name;
            nameCell.textContent = member.full_name;
            roleCell.textContent = member.role;

            // Add event listener to radio button
            radio.addEventListener('change', () => {
                selectUserBtn.disabled = false;
            });

            teamMembersTableBody.appendChild(template);
        });
    }

    // Event listener for team selection
    teamSelect.addEventListener('change', async (event) => {
        const teamId = event.target.value;
        if (teamId) {
            const members = await fetchTeamMembers(teamId);
            updateTeamMembersTable(members);
            teamMembersSection.classList.remove('d-none');
        } else {
            teamMembersSection.classList.add('d-none');
            teamMembersTableBody.innerHTML = '';
            selectUserBtn.disabled = true;
        }
    });

    // Event listener for user selection button
    selectUserBtn.addEventListener('click', () => {
        const selectedRadio = document.querySelector('input[name="selectedUser"]:checked');
        if (selectedRadio) {
            const userId = selectedRadio.value;
            const userName = selectedRadio.dataset.name;

            // Update the hidden input and display field
            const targetInput = document.querySelector(selectUserBtn.dataset.targetInput);
            const targetDisplay = document.querySelector(selectUserBtn.dataset.targetDisplay);
            if (targetInput && targetDisplay) {
                targetInput.value = userId;
                targetDisplay.value = userName;
            }

            // Close the modal
            const modalInstance = bootstrap.Modal.getInstance(modal);
            modalInstance.hide();
        }
    });

    // Store target elements when modal is opened
    modal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const targetInput = button.getAttribute('data-target-input');
        const targetDisplay = button.getAttribute('data-target-display');
        
        // Store these values in the modal's save button
        selectUserBtn.dataset.targetInput = targetInput;
        selectUserBtn.dataset.targetDisplay = targetDisplay;
    });
}); 