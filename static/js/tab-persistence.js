/**
 * Tab Persistence Module
 * Maintains main company tab state through page reloads using URL parameters
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize tab persistence when DOM is ready
  initializeTabPersistence();
});

/**
 * Sets up tab persistence based on URL parameters
 */
function initializeTabPersistence() {
  const tabLinks = document.querySelectorAll('#companyTabs a[data-bs-toggle="tab"]');
  if (!tabLinks.length) return;
  
  // Get URL parameters and activate tab if needed
  const urlParams = new URLSearchParams(window.location.search);
  const tabParam = urlParams.get('tab');
  
  if (tabParam) {
    activateTab(tabParam);
  }
  
  // Add event listeners to update URL when tabs change
  tabLinks.forEach(tab => {
    tab.addEventListener('shown.bs.tab', handleTabChange);
  });
}

/**
 * Event handler for tab change events
 * @param {Event} event - The tab change event
 */
function handleTabChange(event) {
  const tabId = event.target.getAttribute('href').substring(1);
  updateUrlParameter('tab', tabId);
}

/**
 * Activates a specific tab by ID
 * @param {string} tabId - The ID of the tab to activate
 */
function activateTab(tabId) {
  const tabElement = document.querySelector(`#companyTabs a[href="#${tabId}"]`);
  if (!tabElement) return;
  
  try {
    const bsTab = new bootstrap.Tab(tabElement);
    bsTab.show();
  } catch (error) {
    console.warn('Tab activation error:', error);
  }
}

/**
 * Updates a URL parameter without page reload
 * @param {string} key - The parameter key to update
 * @param {string} value - The value to set
 */
function updateUrlParameter(key, value) {
  // Create URL object for easy parameter manipulation
  const url = new URL(window.location.href);
  
  // Update the parameter
  url.searchParams.set(key, value);
  
  // Clear activity_type when not on Activities tab
  if (key === 'tab' && value !== 'activities') {
    url.searchParams.delete('activity_type');
  }
  
  // Update history without reloading the page
  window.history.replaceState({ path: url.toString() }, '', url.toString());
} 