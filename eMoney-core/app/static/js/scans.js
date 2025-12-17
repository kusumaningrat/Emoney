document.addEventListener('DOMContentLoaded', function () {
    // Constants and state
    const REFRESH_INTERVAL = 10; // seconds
    let refreshTimer;
    let countdown = REFRESH_INTERVAL;
    let scanStats = {
        running: 0,
        completed: 0,
        failed: 0,
        pending: 0,
        paused: 0
    };

    // Entity types for each EMoney scan type
    const entityTypesByService = {
        account: ["account", "accounttype", "asset", "assetclass", "liability"],
        client: ["client", "contact", "household", "relationship", "spouse"],
        financial_planning: ["plan", "goal", "net_worth", "scenario", "cashflow"],
        identity: ["user", "office", "role", "permission", "sharingrule", "logon"]
    };

    // Map entity types to required IDs (EMoney specific - could be extended later)
    const entityRequiredFilters = {
        // Examples of EMoney-specific filters if needed:
        // plan: { field: "client_ids", label: "Client IDs", help: "Comma-separated list of client IDs" },
        // scenario: { field: "plan_ids", label: "Plan IDs", help: "Comma-separated list of plan IDs" }
    };

    // DOM elements
    const scanTableBody = document.getElementById('scans-table-body');
    const refreshBtn = document.getElementById('refresh-btn');
    const newScanBtn = document.getElementById('new-scan-btn');
    const modal = document.getElementById('new-scan-modal');
    const closeModalBtn = document.querySelector('.modal-content .close');
    const cancelBtn = document.querySelector('.cancel-btn');
    const scanTypeSelect = document.getElementById('service-type');
    const entityTypesContainer = document.getElementById('entity-types-container');
    const entitySpecificFiltersContainer = document.getElementById('entity-specific-filters');
    const scanForm = document.getElementById('scan-form');
    const countdownEl = document.getElementById('countdown');
    const sidebarToggle = document.getElementById('sidebar-toggle');

    // Stat counters
    const runningCountEl = document.getElementById('running-count');
    const completedCountEl = document.getElementById('completed-count');
    const failedCountEl = document.getElementById('failed-count');
    const pendingCountEl = document.getElementById('pending-count');
    const pausedCountEl = document.getElementById('paused-count');

    // Initialize the page
    initializePage();

    function initializePage() {
        // Debug: Check if all required elements exist
        console.log('Initializing EMoney scan interface...');
        console.log('scanTypeSelect:', scanTypeSelect);
        console.log('entityTypesContainer:', entityTypesContainer);

        if (!scanTypeSelect) {
            console.error('ERROR: scan-type select element not found!');
            return;
        }

        if (!entityTypesContainer) {
            console.error('ERROR: entity-types-container element not found!');
            return;
        }

        loadScans();
        startRefreshTimer();
        setupEventListeners();
        initializeFormDefaults();
    }

    function setupEventListeners() {
        // Refresh button
        refreshBtn.addEventListener('click', function () {
            loadScans();
            resetRefreshTimer();
        });

        // New scan button
        newScanBtn.addEventListener('click', openNewScanModal);

        // Close modal
        closeModalBtn.addEventListener('click', closeNewScanModal);
        cancelBtn.addEventListener('click', closeNewScanModal);

        // Handle outside click
        window.addEventListener('click', function (e) {
            if (e.target === modal) {
                closeNewScanModal();
            }
        });

        // Scan type change
        scanTypeSelect.addEventListener('change', updateEntityTypeOptions);

        // Form submission
        scanForm.addEventListener('submit', startNewScan);

        // Sidebar toggle
        sidebarToggle.addEventListener('click', function () {
            document.querySelector('.sidebar').classList.toggle('active');
        });

        // Listen for entity type checkbox changes
        entityTypesContainer.addEventListener('change', function (event) {
            if (event.target.type === 'checkbox') {
                updateEntitySpecificFilters();
            }
        });
    }

    function initializeFormDefaults() {
        // Initialize entity type checkboxes when the page loads
        updateEntityTypeOptions();
    }

    function updateEntityTypeOptions() {
        const scanType = scanTypeSelect.value;
        const entityTypes = entityTypesByService[scanType] || [];

        console.log('EMoney scan type selected:', scanType);
        console.log('EMoney entity types found:', entityTypes);
        console.log('Entity container:', entityTypesContainer);

        // Clear existing checkboxes
        entityTypesContainer.innerHTML = '';

        if (entityTypes.length === 0) {
            entityTypesContainer.innerHTML = '<p style="color: #666;">Please select an EMoney scan type to see available entity types.</p>';
            return;
        }

        // Add checkboxes for each EMoney entity type
        entityTypes.forEach(type => {
            const checkboxItem = document.createElement('div');
            checkboxItem.className = 'checkbox-item';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `entity-${type}`;
            checkbox.name = 'entity_types';
            checkbox.value = type;

            // Set default selections for EMoney services
            if (scanType === 'account') {
                checkbox.checked = type === 'account' || type === 'asset';
            } else if (scanType === 'client') {
                checkbox.checked = type === 'client' || type === 'contact';
            } else if (scanType === 'financial_planning') {
                checkbox.checked = type === 'plan' || type === 'goal';
            } else if (scanType === 'identity') {
                checkbox.checked = type === 'user' || type === 'permission';
            } else {
                checkbox.checked = entityTypes.indexOf(type) === 0;
            }

            const label = document.createElement('label');
            label.htmlFor = `entity-${type}`;
            label.textContent = type.charAt(0).toUpperCase() + type.slice(1).replace(/_/g, ' ');

            checkboxItem.appendChild(checkbox);
            checkboxItem.appendChild(label);

            entityTypesContainer.appendChild(checkboxItem);
        });

        // Update entity-specific filters based on initial selection
        updateEntitySpecificFilters();
    }

    function updateEntitySpecificFilters() {
        // Get selected entity types
        const selectedEntities = Array.from(
            document.querySelectorAll('input[name="entity_types"]:checked')
        ).map(cb => cb.value);

        // Clear existing entity-specific filters
        entitySpecificFiltersContainer.innerHTML = '';

        // Check if any selected entity requires specific filters
        const requiredFilters = new Set();

        selectedEntities.forEach(entity => {
            if (entityRequiredFilters[entity]) {
                requiredFilters.add(entityRequiredFilters[entity].field);
            }
        });

        // Add required filter fields
        requiredFilters.forEach(filterField => {
            // Find all entities that require this filter
            const entitiesRequiringFilter = Object.entries(entityRequiredFilters)
                .filter(([_, config]) => config.field === filterField)
                .map(([entity, _]) => entity);

            // Find the matching filter config
            const filterConfig = entityRequiredFilters[entitiesRequiringFilter[0]];

            // Create the filter field
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';

            const label = document.createElement('label');
            label.htmlFor = filterField;
            label.textContent = filterConfig.label;

            const input = document.createElement('input');
            input.type = 'text';
            input.id = filterField;
            input.name = filterField;
            input.placeholder = filterConfig.help;

            const helpText = document.createElement('small');
            helpText.className = 'help-text';
            helpText.textContent = `Required for: ${entitiesRequiringFilter.map(e =>
                e.charAt(0).toUpperCase() + e.slice(1).replace(/_/g, ' ')
            ).join(', ')}`;

            formGroup.appendChild(label);
            formGroup.appendChild(input);
            formGroup.appendChild(helpText);

            entitySpecificFiltersContainer.appendChild(formGroup);
        });

        // Show or hide the container based on whether there are any filters
        if (requiredFilters.size > 0) {
            entitySpecificFiltersContainer.style.display = 'block';

            // Add a heading if there isn't one
            if (!document.getElementById('entity-specific-filters-heading')) {
                const heading = document.createElement('h3');
                heading.id = 'entity-specific-filters-heading';
                heading.textContent = 'Entity-Specific Filters';
                heading.className = 'filter-section-heading';
                entitySpecificFiltersContainer.prepend(heading);
            }
        } else {
            entitySpecificFiltersContainer.style.display = 'none';
        }
    }

    function startRefreshTimer() {
        countdown = REFRESH_INTERVAL;
        countdownEl.textContent = `(${countdown})`;

        refreshTimer = setInterval(function () {
            countdown--;
            countdownEl.textContent = `(${countdown})`;

            if (countdown <= 0) {
                loadScans();
                countdown = REFRESH_INTERVAL;
                countdownEl.textContent = `(${countdown})`;
            }
        }, 1000);
    }

    function resetRefreshTimer() {
        clearInterval(refreshTimer);
        startRefreshTimer();
    }

    async function loadScans() {
        scanTableBody.innerHTML = `
            <tr>
                <td colspan="8" class="loading">
                    <div class="loader"></div>
                    <span>Loading EMoney scans...</span>
                </td>
            </tr>
        `;

        try {
            const response = await fetch('/api/v1/scans/?limit=50');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.items && data.items.length > 0) {
                // Reset stat counters
                scanStats = {
                    running: 0,
                    completed: 0,
                    failed: 0,
                    pending: 0,
                    paused: 0
                };

                // Process stats
                data.items.forEach(scan => {
                    if (scan.status === "RUNNING") scanStats.running++;
                    else if (scan.status === "COMPLETED") scanStats.completed++;
                    else if (scan.status === "FAILED") scanStats.failed++;
                    else if (scan.status === "PENDING") scanStats.pending++;
                    else if (scan.status === "PAUSED") scanStats.paused++;
                });

                // Update stat counters
                runningCountEl.textContent = scanStats.running;
                completedCountEl.textContent = scanStats.completed;
                failedCountEl.textContent = scanStats.failed;
                pendingCountEl.textContent = scanStats.pending;
                pausedCountEl.textContent = scanStats.paused;

                renderScansTable(data.items);
            } else {
                scanTableBody.innerHTML = `
                    <tr>
                        <td colspan="8" class="loading">
                            <i class="fas fa-info-circle"></i>
                            <span>No EMoney scans found</span>
                        </td>
                    </tr>
                `;
            }
        } catch (error) {
            console.error('Error loading EMoney scans:', error);
            scanTableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="loading">
                        <i class="fas fa-exclamation-triangle" style="color: #e74c3c;"></i>
                        <span>Error loading EMoney scans: ${error.message}</span>
                    </td>
                </tr>
            `;
        }
    }

    function renderScansTable(scans) {
        scanTableBody.innerHTML = '';

        scans.forEach(scan => {
            const row = document.createElement('tr');

            // Calculate duration
            let duration = 'N/A';
            if (scan.started_at && (scan.completed_at || scan.status === 'RUNNING' || scan.status === 'PAUSED')) {
                const startTime = new Date(scan.started_at);
                const endTime = scan.completed_at ? new Date(scan.completed_at) : new Date();
                const durationMs = endTime - startTime;
                duration = formatDuration(durationMs);
            }

            // Format dates
            const createdAt = new Date(scan.created_at).toLocaleString();

            // Format entity types
            const entityTypes = scan.entity_types.join(', ');

            // Add EMoney service label for clarity
            const serviceLabel = getEMoneyServiceLabel(scan.scan_type);

            // Create the row content
            row.innerHTML = `
                <td>
                    <a href="/api/v1/scans/${scan.id}/status" target="_blank" title="${scan.id}">
                        ${scan.id.slice(0, 8)}...
                    </a>
                </td>
                <td>
                    <span class="service-badge emoney-${scan.scan_type}">${serviceLabel}</span>
                </td>
                <td><span class="status ${scan.status.toLowerCase()}">${scan.status}</span></td>
                <td>${entityTypes}</td>
                <td>${scan.organization_id || 'N/A'}</td>
                <td>${createdAt}</td>
                <td>${duration}</td>
                <td>
                    <button class="action-btn view-btn" data-id="${scan.id}">
                        <i class="fas fa-eye"></i> View
                    </button>
                    ${scan.status === 'RUNNING' ? `
                        <button class="action-btn pause-scan-btn" data-id="${scan.id}">
                            <i class="fas fa-pause"></i> Pause
                        </button>
                        <button class="action-btn cancel-scan-btn" data-id="${scan.id}">
                            <i class="fas fa-stop"></i> Cancel
                        </button>
                    ` : ''}
                    ${scan.status === 'PAUSED' ? `
                        <button class="action-btn resume-scan-btn" data-id="${scan.id}">
                            <i class="fas fa-play"></i> Resume
                        </button>
                        <button class="action-btn cancel-scan-btn" data-id="${scan.id}">
                            <i class="fas fa-stop"></i> Cancel
                        </button>
                    ` : ''}
                    <button class="action-btn remove-scan-btn" data-id="${scan.id}">
                        <i class="fas fa-trash"></i> Remove
                    </button>
                </td>
            `;

            scanTableBody.appendChild(row);
        });

        // Add event listeners for action buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const scanId = this.getAttribute('data-id');
                showScanDetails(scanId);
            });
        });

        document.querySelectorAll('.cancel-scan-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const scanId = this.getAttribute('data-id');
                cancelScan(scanId);
            });
        });

        document.querySelectorAll('.pause-scan-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const scanId = this.getAttribute('data-id');
                pauseScan(scanId);
            });
        });

        document.querySelectorAll('.resume-scan-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const scanId = this.getAttribute('data-id');
                resumeScan(scanId);
            });
        });

        document.querySelectorAll('.remove-scan-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const scanId = this.getAttribute('data-id');
                removeScan(scanId);
            });
        });
    }

    function getEMoneyServiceLabel(scanType) {
        const labels = {
            'account': 'Account',
            'client': 'Client',
            'financial_planning': 'Planning',
            'identity': 'Identity'
        };
        return labels[scanType] || scanType;
    }

    function formatDuration(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);

        if (hours > 0) {
            return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds % 60}s`;
        } else {
            return `${seconds}s`;
        }
    }

    function openNewScanModal() {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    function closeNewScanModal() {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }

    async function startNewScan(e) {
        e.preventDefault();

        // Get form data
        const scanType = scanTypeSelect.value;

        // Get selected entity types
        const entityTypeCheckboxes = document.querySelectorAll('input[name="entity_types"]:checked');
        const entityTypes = Array.from(entityTypeCheckboxes).map(cb => cb.value);

        if (entityTypes.length === 0) {
            alert('Please select at least one entity type');
            return;
        }

        const organizationId = document.getElementById('organization-id').value;
        const includeInactive = document.getElementById('include-inactive').checked;
        const batchSize = parseInt(document.getElementById('batch-size').value) || 100;
        const filterProperties = document.getElementById('filter-properties').value;
        
        // Get EMoney JWT authentication fields
        const apiKey = document.getElementById('api-key').value;
        const clientId = document.getElementById('client-id').value;
        const firmId = document.getElementById('firm-id').value;
        const jwtToken = document.getElementById('jwt-token').value;
        const scope = document.getElementById('scope').value || 'API';

        // Get EMoney filters
        const filters = {
            includeInactive: includeInactive,
            batchSize: batchSize
        };

        // Add filter properties if specified
        if (filterProperties) {
            filters.properties = filterProperties.split(',').map(prop => prop.trim()).filter(prop => prop.length > 0);
        }

        // Add entity-specific filters if they exist
        Object.values(entityRequiredFilters).forEach(filter => {
            const filterElement = document.getElementById(filter.field);
            if (filterElement && filterElement.value) {
                // Convert comma-separated string to array and trim whitespace
                filters[filter.field] = filterElement.value
                    .split(',')
                    .map(id => id.trim())
                    .filter(id => id.length > 0);
            }
        });

        // Construct request body with EMoney JWT credentials
        const requestBody = {
            scan_type: scanType,
            entity_types: entityTypes,
            organizationId: organizationId,
            auth: {
                api_key: apiKey,
                client_id: clientId,
                firm_id: firmId,
                jwt_token: jwtToken,
                scope: scope
            },
            filters: filters
        };

        try {
            // Show loading state
            const submitBtn = scanForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting EMoney Scan...';
            submitBtn.disabled = true;

            const response = await fetch('/api/v1/scans/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('EMoney scan started:', data);

            closeNewScanModal();
            loadScans();

            // Show success notification
            showNotification(`EMoney ${getEMoneyServiceLabel(scanType)} scan started successfully`, 'success');

        } catch (error) {
            console.error('Error starting EMoney scan:', error);
            showNotification(`Error starting EMoney scan: ${error.message}`, 'error');
        } finally {
            // Reset button state
            const submitBtn = scanForm.querySelector('button[type="submit"]');
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async function cancelScan(scanId) {
        if (!confirm(`Are you sure you want to cancel EMoney scan ${scanId}?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/v1/scans/${scanId}/cancel`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('EMoney scan cancelled:', data);

            loadScans();
            showNotification('EMoney scan cancelled successfully', 'success');

        } catch (error) {
            console.error('Error cancelling EMoney scan:', error);
            showNotification(`Error cancelling EMoney scan: ${error.message}`, 'error');
        }
    }

    async function pauseScan(scanId) {
        if (!confirm(`Are you sure you want to pause EMoney scan ${scanId}?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/v1/scans/${scanId}/pause`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('EMoney scan paused:', data);

            loadScans();
            showNotification('EMoney scan paused successfully', 'success');

        } catch (error) {
            console.error('Error pausing EMoney scan:', error);
            showNotification(`Error pausing EMoney scan: ${error.message}`, 'error');
        }
    }

    async function resumeScan(scanId) {
        if (!confirm(`Are you sure you want to resume EMoney scan ${scanId}?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/v1/scans/${scanId}/resume`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('EMoney scan resumed:', data);

            loadScans();
            showNotification('EMoney scan resumed successfully', 'success');

        } catch (error) {
            console.error('Error resuming EMoney scan:', error);
            showNotification(`Error resuming EMoney scan: ${error.message}`, 'error');
        }
    }

    async function removeScan(scanId) {
        if (!confirm(`Are you sure you want to remove EMoney scan ${scanId} and all its data? This action cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch(`/api/v1/scans/${scanId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('EMoney scan removed:', data);

            loadScans();
            showNotification('EMoney scan removed successfully', 'success');

        } catch (error) {
            console.error('Error removing EMoney scan:', error);
            showNotification(`Error removing EMoney scan: ${error.message}`, 'error');
        }
    }

    // Add notification system
    function showNotification(message, type = 'info') {
        // Check if notification container exists, create if not
        let notifContainer = document.querySelector('.notification-container');
        if (!notifContainer) {
            notifContainer = document.createElement('div');
            notifContainer.className = 'notification-container';
            document.body.appendChild(notifContainer);

            // Add styles
            const style = document.createElement('style');
            style.textContent = `
                .notification-container {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                .notification {
                    padding: 12px 20px;
                    border-radius: 6px;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.15);
                    max-width: 350px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    animation: slideIn 0.3s ease, fadeOut 0.5s ease 2.5s forwards;
                    position: relative;
                }
                .notification.success {
                    background-color: rgba(46, 204, 113, 0.95);
                    color: white;
                }
                .notification.error {
                    background-color: rgba(231, 76, 60, 0.95);
                    color: white;
                }
                .notification.info {
                    background-color: rgba(67, 97, 238, 0.95);
                    color: white;
                }
                .help-text {
                    display: block;
                    font-size: 0.8rem;
                    color: var(--text-secondary);
                    margin-top: 4px;
                }
                .filter-section-heading {
                    font-size: 1rem;
                    margin: 1.2rem 0 0.8rem 0;
                    color: var(--text-primary);
                    font-weight: 600;
                }
                .service-badge {
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 0.85rem;
                    font-weight: 500;
                    text-transform: uppercase;
                }
                .service-badge.emoney-account {
                    background-color: rgba(52, 152, 219, 0.15);
                    color: #2980b9;
                    border: 1px solid rgba(52, 152, 219, 0.3);
                }
                .service-badge.emoney-client {
                    background-color: rgba(46, 204, 113, 0.15);
                    color: #27ae60;
                    border: 1px solid rgba(46, 204, 113, 0.3);
                }
                .service-badge.emoney-financial_planning {
                    background-color: rgba(155, 89, 182, 0.15);
                    color: #8e44ad;
                    border: 1px solid rgba(155, 89, 182, 0.3);
                }
                .service-badge.emoney-identity {
                    background-color: rgba(230, 126, 34, 0.15);
                    color: #d35400;
                    border: 1px solid rgba(230, 126, 34, 0.3);
                }
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes fadeOut {
                    from { opacity: 1; }
                    to { opacity: 0; transform: translateY(-10px); }
                }
            `;
            document.head.appendChild(style);
        }

        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;

        // Add icon based on type
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-circle';

        notification.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span>${message}</span>
        `;

        notifContainer.appendChild(notification);

        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Make these functions accessible to the global scope
    window.loadScans = loadScans;
    window.formatDuration = formatDuration;
    window.cancelScan = cancelScan;
    window.pauseScan = pauseScan;
    window.resumeScan = resumeScan;
    window.removeScan = removeScan;
    window.showNotification = showNotification;
});

async function showScanDetails(scanId) {
    // Get modal elements
    const modal = document.getElementById('scan-details-modal');
    const modalContent = document.getElementById('scan-details-content');

    // Show modal with loading spinner
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';

    modalContent.innerHTML = `
        <div class="loading-spinner">
            <div class="loader"></div>
            <p>Loading EMoney scan details...</p>
        </div>
    `;

    // Close button handler
    modal.querySelector('.close').addEventListener('click', function () {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    });

    // Outside click handler
    window.addEventListener('click', function (e) {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    });

    try {
        // Fetch EMoney scan details
        const response = await fetch(`/api/v1/scans/${scanId}/status`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const scanData = await response.json();

        // Format timestamps
        const createdAt = new Date(scanData.created_at).toLocaleString();
        const startedAt = scanData.started_at ? new Date(scanData.started_at).toLocaleString() : 'N/A';
        const completedAt = scanData.completed_at ? new Date(scanData.completed_at).toLocaleString() : 'N/A';

        // Calculate overall duration
        let duration = 'N/A';
        if (scanData.started_at) {
            const startTime = new Date(scanData.started_at);
            const endTime = scanData.completed_at ? new Date(scanData.completed_at) : new Date();
            const durationMs = endTime - startTime;
            duration = formatDuration(durationMs);
        }

        // Calculate total records
        const totalRecords = scanData.entity_results.reduce((sum, result) => sum + (result.record_count || 0), 0);

        // Calculate overall progress
        const completedEntities = scanData.entity_results.filter(r =>
            r.status === 'completed' || r.status === 'failed' || r.status === 'cancelled').length;
        const totalEntities = scanData.entity_results.length;
        const progressPercent = totalEntities > 0 ? Math.round((completedEntities / totalEntities) * 100) : 0;

        // Get applied filters
        const appliedFilters = scanData.filters || {};
        let filtersHtml = '';

        if (Object.keys(appliedFilters).length > 0) {
            filtersHtml = `
                <div class="scan-details-section">
                    <h3>EMoney Applied Filters</h3>
                    <div class="scan-info">
            `;

            // Date range filters
            if (appliedFilters.dateRange) {
                filtersHtml += `
                    <div class="info-item">
                        <label>Date Range:</label>
                        <span>${appliedFilters.dateRange.startDate || 'N/A'} to ${appliedFilters.dateRange.endDate || 'N/A'}</span>
                    </div>
                `;
            }

            // EMoney batch size
            if (appliedFilters.batchSize) {
                filtersHtml += `
                    <div class="info-item">
                        <label>Batch Size:</label>
                        <span>${appliedFilters.batchSize}</span>
                    </div>
                `;
            }

            // Include inactive flag
            if (appliedFilters.includeInactive !== undefined) {
                filtersHtml += `
                    <div class="info-item">
                        <label>Include Inactive:</label>
                        <span>${appliedFilters.includeInactive ? 'Yes' : 'No'}</span>
                    </div>
                `;
            }

            // Entity specific filters
            const knownFilters = ['dateRange', 'batchSize', 'includeInactive'];
            Object.entries(appliedFilters).forEach(([key, value]) => {
                if (!knownFilters.includes(key)) {
                    let displayValue;
                    if (Array.isArray(value)) {
                        displayValue = value.join(', ');
                    } else if (typeof value === 'object') {
                        displayValue = JSON.stringify(value);
                    } else {
                        displayValue = value;
                    }

                    filtersHtml += `
                        <div class="info-item">
                            <label>${key.replace(/_/g, ' ')}:</label>
                            <span>${displayValue}</span>
                        </div>
                    `;
                }
            });

            filtersHtml += `
                    </div>
                </div>
            `;
        }

        // Get service label
        function getEMoneyServiceLabel(scanType) {
            const labels = {
                'account': 'Account & Assets',
                'client': 'Client Management',
                'financial_planning': 'Financial Planning',
                'identity': 'Identity & Access'
            };
            return labels[scanType] || scanType;
        }

        // Render EMoney scan details
        modalContent.innerHTML = `
            <div class="scan-details-section">
                <h3>EMoney Scan Information</h3>
                <div class="scan-info">
                    <div class="info-item">
                        <label>ID:</label>
                        <span>${scanData.id}</span>
                    </div>
                    <div class="info-item">
                        <label>Service:</label>
                        <span><span class="service-badge emoney-${scanData.scan_type}">${getEMoneyServiceLabel(scanData.scan_type)}</span></span>
                    </div>
                    <div class="info-item">
                        <label>Status:</label>
                        <span><span class="status ${scanData.status.toLowerCase()}">${scanData.status}</span></span>
                    </div>
                    <div class="info-item">
                        <label>Organization:</label>
                        <span>${scanData.organization_id || 'N/A'}</span>
                    </div>
                    <div class="info-item">
                        <label>Created At:</label>
                        <span>${createdAt}</span>
                    </div>
                    <div class="info-item">
                        <label>Started At:</label>
                        <span>${startedAt}</span>
                    </div>
                    <div class="info-item">
                        <label>Completed At:</label>
                        <span>${completedAt}</span>
                    </div>
                    <div class="info-item">
                        <label>Duration:</label>
                        <span>${duration}</span>
                    </div>
                    <div class="info-item">
                        <label>Entity Types:</label>
                        <span>${scanData.entity_types.join(', ')}</span>
                    </div>
                    <div class="info-item">
                        <label>Total Records:</label>
                        <span>${totalRecords}</span>
                    </div>
                </div>
            </div>
            
            ${filtersHtml}
            
            <div class="scan-details-section">
                <h3>EMoney Entity Results</h3>
                <table class="entity-results-table">
                    <thead>
                        <tr>
                            <th>Entity Type</th>
                            <th>Status</th>
                            <th>Records</th>
                            <th>Duration</th>
                            <th>Progress</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${scanData.entity_results.map(result => {
            // Calculate entity duration
            let entityDuration = 'N/A';
            if (result.start_time) {
                if (result.processing_time) {
                    entityDuration = formatDuration(result.processing_time * 1000);
                } else if (result.end_time) {
                    const startTime = new Date(result.start_time);
                    const endTime = new Date(result.end_time);
                    entityDuration = formatDuration(endTime - startTime);
                } else {
                    const startTime = new Date(result.start_time);
                    entityDuration = formatDuration(new Date() - startTime);
                }
            }

            // Determine progress class
            let progressClass = '';
            if (result.status === 'completed') progressClass = 'complete';
            if (result.status === 'failed') progressClass = 'failed';

            // Determine progress percentage
            let progressPercent = 0;
            if (result.status === 'completed' || result.status === 'failed' || result.status === 'cancelled') {
                progressPercent = 100;
            } else if (result.status === 'processing') {
                progressPercent = 50;
            } else if (result.status === 'paused') {
                progressPercent = 30;
            }

            return `
                                <tr>
                                    <td>${result.entity_type}</td>
                                    <td><span class="status ${result.status}">${result.status}</span></td>
                                    <td>${result.record_count || 0}</td>
                                    <td>${entityDuration}</td>
                                    <td>
                                        <div class="entity-progress">
                                            <div class="entity-progress-bar ${progressClass}" style="width: ${progressPercent}%"></div>
                                        </div>
                                    </td>
                                </tr>
                            `;
        }).join('')}
                    </tbody>
                </table>
            </div>
            
            <div class="scan-details-section">
                <h3>EMoney Actions</h3>
                <div class="action-buttons">
                    ${scanData.status === 'RUNNING' ? `
                        <button class="btn btn-primary pause-detail-scan-btn" data-id="${scanData.id}">
                            <i class="fas fa-pause"></i> Pause EMoney Scan
                        </button>
                        <button class="btn btn-danger cancel-detail-scan-btn" data-id="${scanData.id}">
                            <i class="fas fa-stop"></i> Cancel EMoney Scan
                        </button>
                    ` : ''}
                    ${scanData.status === 'PAUSED' ? `
                        <button class="btn btn-primary resume-detail-scan-btn" data-id="${scanData.id}">
                            <i class="fas fa-play"></i> Resume EMoney Scan
                        </button>
                        <button class="btn btn-danger cancel-detail-scan-btn" data-id="${scanData.id}">
                            <i class="fas fa-stop"></i> Cancel EMoney Scan
                        </button>
                    ` : ''}
                    <button class="btn btn-danger remove-detail-scan-btn" data-id="${scanData.id}">
                        <i class="fas fa-trash"></i> Remove EMoney Scan
                    </button>
                    <button class="btn btn-secondary close-details-btn">Close</button>
                </div>
            </div>
        `;

        // Add event listeners for action buttons
        modalContent.querySelector('.close-details-btn').addEventListener('click', function () {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        });

        // Add pause button handler if present
        const pauseBtn = modalContent.querySelector('.pause-detail-scan-btn');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', function () {
                const scanId = this.getAttribute('data-id');
                pauseScan(scanId);
                modal.style.display = 'none';
                document.body.style.overflow = '';
            });
        }

        // Add resume button handler if present
        const resumeBtn = modalContent.querySelector('.resume-detail-scan-btn');
        if (resumeBtn) {
            resumeBtn.addEventListener('click', function () {
                const scanId = this.getAttribute('data-id');
                resumeScan(scanId);
                modal.style.display = 'none';
                document.body.style.overflow = '';
            });
        }

        // Add cancel button handler if present
        const cancelBtn = modalContent.querySelector('.cancel-detail-scan-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', function () {
                const scanId = this.getAttribute('data-id');
                cancelScan(scanId);
                modal.style.display = 'none';
                document.body.style.overflow = '';
            });
        }

        // Add remove button handler
        const removeBtn = modalContent.querySelector('.remove-detail-scan-btn');
        if (removeBtn) {
            removeBtn.addEventListener('click', function () {
                const scanId = this.getAttribute('data-id');
                removeScan(scanId);
                modal.style.display = 'none';
                document.body.style.overflow = '';
            });
        }

    } catch (error) {
        console.error('Error fetching EMoney scan details:', error);
        modalContent.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>Error loading EMoney scan details: ${error.message}</p>
                <button class="btn btn-secondary close-details-btn">Close</button>
            </div>
        `;

        modalContent.querySelector('.close-details-btn').addEventListener('click', function () {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        });
    }
}