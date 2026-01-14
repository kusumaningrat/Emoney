// Global variables
let currentTask = null;
let eventSource = null;
let currentPage = 0;
let pageSize = 10;
let autoRefreshEnabled = false;
let autoRefreshInterval = null;
let refreshIntervalSeconds = 20;

// DOM elements
document.addEventListener("DOMContentLoaded", function () {
  // Create header with refresh controls
  const header = document.createElement("div");
  header.className = "dashboard-header";

  header.innerHTML = `
        <div class="header-title">
            <h1><i class="data-icon"></i>eMoney Service Extraction Dashboard</h1>
            <span class="subtitle">Monitor and manage eMoney service extraction tasks</span>
        </div>
        <div class="header-controls">
            <button id="refresh-btn" class="control-btn">
                <i class="refresh-icon"></i> Refresh Now
            </button>
            <button id="auto-refresh-btn" class="control-btn">
                <i class="refresh-icon"></i> Auto-refresh OFF
            </button>
        </div>
    `;

  // Insert the header before the task-list
  const taskList = document.getElementById("task-list");
  taskList.parentNode.insertBefore(header, taskList);

  // Initialize click handlers
  document.getElementById("refresh-btn").addEventListener("click", function () {
    const pageSizeSelector = document.getElementById("list-page-size");
    const limit = pageSizeSelector ? parseInt(pageSizeSelector.value, 10) : 10;

    // If there's a next button, get the current offset from it
    const prevBtn = document.getElementById("prev-list-btn");
    let offset = 0;

    if (prevBtn && !prevBtn.disabled) {
      const nextBtn = document.getElementById("next-list-btn");
      if (nextBtn) {
        offset =
          parseInt(prevBtn.getAttribute("data-offset"), 10) +
          parseInt(prevBtn.getAttribute("data-limit"), 10);
      }
    }

    // Refresh both tasks and stats
    fetchTasks(offset, limit);
    fetchStats();
  });

  // Auto-refresh toggle
  document
    .getElementById("auto-refresh-btn")
    .addEventListener("click", toggleAutoRefresh);

  document.querySelector(".close").addEventListener("click", closeModal);
  document
    .getElementById("start-stream-btn")
    .addEventListener("click", startStreaming);

  // Tab navigation
  const tabButtons = document.querySelectorAll(".tablinks");
  tabButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      openTab(e, this.getAttribute("data-tab"));
    });
  });

  // Initial data fetch for both tasks and stats
  fetchTasks();
  fetchStats();
});

// Add the start scan button to the header after the auto-refresh button
document.addEventListener("DOMContentLoaded", function () {
  // Find the auto-refresh button in the header
  const headerControls = document.querySelector(".header-controls");
  if (headerControls) {
    // Create the start scan button
    const startScanBtn = document.createElement("button");
    startScanBtn.id = "start-scan-btn";
    startScanBtn.className = "control-btn";
    startScanBtn.innerHTML = '<i class="plus-icon"></i> Start Extraction';

    // Add the button to the header controls
    headerControls.appendChild(startScanBtn);

    // Add event listener
    startScanBtn.addEventListener("click", openStartScanModal);
  }

  // Create the modal for start scan
  createStartScanModal();
});

// Function to toggle auto-refresh
function toggleAutoRefresh() {
  autoRefreshEnabled = !autoRefreshEnabled;
  const autoRefreshBtn = document.getElementById("auto-refresh-btn");

  if (autoRefreshEnabled) {
    // Start the refresh interval
    autoRefreshInterval = setInterval(() => {
      // Get current pagination state
      const pageSizeSelector = document.getElementById("list-page-size");
      const limit = pageSizeSelector
        ? parseInt(pageSizeSelector.value, 10)
        : 10;

      // Try to get current offset
      const prevBtn = document.getElementById("prev-list-btn");
      let offset = 0;

      if (prevBtn && !prevBtn.disabled) {
        const nextBtn = document.getElementById("next-list-btn");
        if (nextBtn) {
          offset =
            parseInt(prevBtn.getAttribute("data-offset"), 10) +
            parseInt(prevBtn.getAttribute("data-limit"), 10);
        }
      }

      // Perform the refresh of both tasks and stats
      fetchTasks(offset, limit);
      fetchStats();

      // Update the button with countdown
      updateRefreshCountdown(refreshIntervalSeconds);
    }, refreshIntervalSeconds * 1000);

    autoRefreshBtn.classList.add("active");
    autoRefreshBtn.innerHTML = `<i class="refresh-icon"></i> Auto-refresh ON (${refreshIntervalSeconds}s)`;

    // Start the countdown
    updateRefreshCountdown(refreshIntervalSeconds);
  } else {
    // Clear the interval
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;

    autoRefreshBtn.classList.remove("active");
    autoRefreshBtn.innerHTML = `<i class="refresh-icon"></i> Auto-refresh OFF`;
  }
}

// Function to update the countdown
function updateRefreshCountdown(initialSeconds) {
  let seconds = initialSeconds;
  const autoRefreshBtn = document.getElementById("auto-refresh-btn");

  if (!autoRefreshBtn || !autoRefreshEnabled) return;

  const countdownInterval = setInterval(() => {
    seconds--;

    if (seconds <= 0) {
      clearInterval(countdownInterval);
      autoRefreshBtn.innerHTML = `<i class="refresh-icon"></i> Auto-refresh ON (${refreshIntervalSeconds}s)`;
      return;
    }

    autoRefreshBtn.innerHTML = `<i class="refresh-icon"></i> Auto-refresh ON (${seconds}s)`;
  }, 1000);
}

// Fetch all tasks with pagination
function fetchTasks(offset = 0, limit = 10) {
  document.getElementById("task-list").innerHTML =
    '<div class="loading-indicator"><div class="spinner"></div><p>Loading tasks...</p></div>';

  fetch(`/api/scan/list?offset=${offset}&limit=${limit}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayTasks(data.data.scans || [], data.data.pagination);
      } else {
        document.getElementById(
          "task-list"
        ).innerHTML = `<div class="error-message"><p>Error loading tasks: ${
          data.message || "Unknown error"
        }</p></div>`;
      }
    })
    .catch((error) => {
      console.error("Error fetching tasks:", error);
      document.getElementById(
        "task-list"
      ).innerHTML = `<div class="error-message"><p>Error loading tasks: ${
        error.message || "Network error"
      }</p></div>`;
    });
}

// Calculate and display task statistics
function displayTaskStats(tasks) {
  // Count tasks by status
  const stats = {
    running: 0,
    completed: 0,
    failed: 0,
    pending: 0,
    total: tasks.length,
  };

  tasks.forEach((task) => {
    if (task.status === "running") stats.running++;
    else if (task.status === "completed") stats.completed++;
    else if (task.status === "failed" || task.status === "crashed")
      stats.failed++;
    else if (task.status === "pending" || task.status === "paused")
      stats.pending++;
  });

  // Create HTML for stats
  let statsHtml = `
        <div class="task-stats">
            <div class="stat-card total">
                <span class="stat-value">${stats.total}</span>
                <span class="stat-label">Total Tasks</span>
            </div>
            <div class="stat-card running">
                <span class="stat-value">${stats.running}</span>
                <span class="stat-label">Running</span>
            </div>
            <div class="stat-card completed">
                <span class="stat-value">${stats.completed}</span>
                <span class="stat-label">Completed</span>
            </div>
            <div class="stat-card failed">
                <span class="stat-value">${stats.failed}</span>
                <span class="stat-label">Failed</span>
            </div>
        </div>
    `;

  // Add the stats before the table
  const statsContainer = document.createElement("div");
  statsContainer.id = "task-stats-container";
  statsContainer.innerHTML = statsHtml;

  // Find the table container
  const resultsHeader = document.querySelector(".results-header");
  if (resultsHeader) {
    resultsHeader.parentNode.insertBefore(statsContainer, resultsHeader);
  }
}

// Display tasks in a table with pagination
function displayTasks(tasks, pagination) {
  if (!tasks.length) {
    document.getElementById("task-list").innerHTML =
      '<div class="no-data-message"><p>No tasks found.</p></div>';
    return;
  }

  // Default pagination if not provided
  pagination = pagination || {
    total: tasks.length,
    limit: 10,
    offset: 0,
    hasMore: false,
    returned: tasks.length,
  };

  // Calculate page information
  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;
  const totalPages = Math.ceil(pagination.total / pagination.limit);

  let html = `
    <div class="results-header">
        <h4>eMoney Service Extraction Tasks</h4>
        <p class="pagination-info">
            Showing ${pagination.offset + 1} to ${
    pagination.offset + pagination.returned
  } 
            of ${pagination.total} tasks
        </p>
    </div>
    
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Scan ID</th>
                    <th>Status</th>
                    <th>Organization</th>
                    <th>Entity Type</th>
                    <th>Records</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Last Heartbeat</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

  tasks.forEach((task) => {
    const status = getStatusBadge(task.status);
    const startTime = task.startTime
      ? new Date(task.startTime).toLocaleString()
      : "N/A";
    const endTime = task.endTime
      ? new Date(task.endTime).toLocaleString()
      : "N/A";
    const lastHeartbeat = task.lastHeartbeat
      ? new Date(task.lastHeartbeat).toLocaleString()
      : "N/A";
    const taskType =
      task.type ||
      (task.config && task.config.type
        ? Array.isArray(task.config.type)
          ? task.config.type.join(", ")
          : task.config.type
        : "N/A");

    html += `
        <tr>
            <td>${task.scanId}</td>
            <td>${status}</td>
            <td>${task.organizationId || "N/A"}</td>
            <td>${taskType}</td>
            <td>${task.recordsExtracted || 0}</td>
            <td>${startTime}</td>
            <td>${endTime}</td>
            <td>${lastHeartbeat}</td>
            <td>${getActionButtons(task)}</td>
        </tr>
        `;
  });

  html += `</tbody></table></div>`;

  // Add pagination controls
  html += `
        <div class="pagination-controls">
            <button 
                id="prev-list-btn" 
                ${pagination.offset <= 0 ? "disabled" : ""} 
                class="pagination-btn"
                data-offset="${Math.max(
                  0,
                  pagination.offset - pagination.limit
                )}"
                data-limit="${pagination.limit}">
                &laquo; Previous
            </button>
            <span class="page-info">Page ${currentPage} of ${
    totalPages || 1
  }</span>
            <button 
                id="next-list-btn" 
                ${!pagination.hasMore ? "disabled" : ""} 
                class="pagination-btn"
                data-offset="${pagination.offset + pagination.limit}"
                data-limit="${pagination.limit}">
                Next &raquo;
            </button>
            
            <div class="page-size-selector">
                <label for="list-page-size">Tasks per page:</label>
                <select id="list-page-size">
                    <option value="5" ${
                      pagination.limit === 5 ? "selected" : ""
                    }>5</option>
                    <option value="10" ${
                      pagination.limit === 10 ? "selected" : ""
                    }>10</option>
                    <option value="20" ${
                      pagination.limit === 20 ? "selected" : ""
                    }>20</option>
                    <option value="50" ${
                      pagination.limit === 50 ? "selected" : ""
                    }>50</option>
                </select>
            </div>
        </div>
    `;

  document.getElementById("task-list").innerHTML = html;

  // Add task statistics
  displayTaskStats(tasks);

  // Attach event listeners to buttons
  document.querySelectorAll(".view-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      viewTask(this.getAttribute("data-id"));
    });
  });

  document.querySelectorAll(".remove-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      removeTask(this.getAttribute("data-id"));
    });
  });

  document.querySelectorAll(".cancel-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      cancelTask(this.getAttribute("data-id"));
    });
  });

  document.querySelectorAll(".pause-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      pauseTask(this.getAttribute("data-id"));
    });
  });

  document.querySelectorAll(".resume-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      resumeTask(this.getAttribute("data-id"));
    });
  });

  document.querySelectorAll(".stream-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const taskId = this.getAttribute("data-id");

      fetch(`/api/scan/${taskId}/status`)
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            currentTask = data.data;
            const streamTab = document.querySelector('[data-tab="stream"]');
            if (streamTab) {
              streamTab.click();
            }
            document.getElementById("task-modal").style.display = "block";
            setTimeout(() => {
              startStreaming();
            }, 100);
          } else {
            alert(`Error: ${data.message || "Unknown error"}`);
          }
        })
        .catch((error) => {
          console.error("Error fetching task details:", error);
          alert(
            `Error fetching task details: ${error.message || "Network error"}`
          );
        });
    });
  });

  // Attach pagination event listeners
  const prevButton = document.getElementById("prev-list-btn");
  if (prevButton) {
    prevButton.addEventListener("click", function () {
      if (!this.disabled) {
        const newOffset = parseInt(this.getAttribute("data-offset"), 10);
        const pageLimit = parseInt(this.getAttribute("data-limit"), 10);
        fetchTasks(newOffset, pageLimit);
      }
    });
  }

  const nextButton = document.getElementById("next-list-btn");
  if (nextButton) {
    nextButton.addEventListener("click", function () {
      if (!this.disabled) {
        const newOffset = parseInt(this.getAttribute("data-offset"), 10);
        const pageLimit = parseInt(this.getAttribute("data-limit"), 10);
        fetchTasks(newOffset, pageLimit);
      }
    });
  }

  // Handle page size changes
  const pageSizeSelector = document.getElementById("list-page-size");
  if (pageSizeSelector) {
    pageSizeSelector.addEventListener("change", function () {
      const newLimit = parseInt(this.value, 10);
      fetchTasks(0, newLimit);
    });
  }
}

// Create status badge HTML
function getStatusBadge(status) {
  let badgeClass = "";

  switch (status) {
    case "running":
      badgeClass = "status-running";
      break;
    case "completed":
      badgeClass = "status-completed";
      break;
    case "failed":
      badgeClass = "status-failed";
      break;
    case "pending":
      badgeClass = "status-pending";
      break;
    case "cancelled":
      badgeClass = "status-cancelled";
      break;
    case "paused":
      badgeClass = "status-paused";
      break;
    case "crashed":
      badgeClass = "status-crashed";
      break;
    default:
      badgeClass = "";
  }

  return `<span class="status-badge ${badgeClass}">${status}</span>`;
}

// Create action buttons based on task status
function getActionButtons(task) {
  let buttons = `<button class="button view-btn" data-id="${task.scanId}">View</button> `;

  if (task.status === "running") {
    buttons += `
            <button class="button pause-btn" data-id="${task.scanId}">Pause</button>
            <button class="button cancel-btn" data-id="${task.scanId}">Cancel</button>
        `;
  } else if (task.status === "paused") {
    buttons += `<button class="button resume-btn" data-id="${task.scanId}">Resume</button>`;
  }

  if (task.status === "completed") {
    buttons += `
            <button class="button stream-btn" data-id="${task.scanId}">Stream</button>
            <button class="button remove-btn" data-id="${task.scanId}">Remove</button>
        `;
  } else if (["failed", "cancelled", "crashed"].includes(task.status)) {
    buttons += `<button class="button remove-btn" data-id="${task.scanId}">Remove</button>`;
  }

  return buttons;
}

// View task details
function viewTask(taskId) {
  fetch(`/api/scan/${taskId}/status`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        currentTask = data.data;
        currentPage = 0;
        showTaskDetails(data.data);
      } else {
        alert(`Error: ${data.message || "Unknown error"}`);
      }
    })
    .catch((error) => {
      console.error("Error fetching task details:", error);
      alert(`Error fetching task details: ${error.message || "Network error"}`);
    });
}

// Show task details in modal
function showTaskDetails(task) {
  document.getElementById(
    "modal-title"
  ).textContent = `Task Details: ${task.scanId}`;

  document.getElementById("stream-tab").style.display =
    task.status === "completed" ? "block" : "none";
  document.getElementById("results-tab").style.display =
    task.status === "completed" ? "block" : "none";

  document
    .querySelectorAll(".tablinks")
    .forEach((tab) => tab.classList.remove("active"));
  document.querySelector('[data-tab="details"]').classList.add("active");

  document.querySelectorAll(".tabcontent").forEach((content) => {
    content.style.display = "none";
  });
  document.getElementById("details").style.display = "block";

  const startTime = task.startTime
    ? new Date(task.startTime).toLocaleString()
    : "N/A";
  const endTime = task.endTime
    ? new Date(task.endTime).toLocaleString()
    : "N/A";

  let detailsHtml = `
        <div>
            <p><strong>Status:</strong> ${getStatusBadge(task.status)}</p>
            <p><strong>Organization ID:</strong> ${
              task.organizationId || "N/A"
            }</p>
            <p><strong>Start Time:</strong> ${startTime}</p>
            <p><strong>End Time:</strong> ${endTime}</p>
            <p><strong>Records Extracted:</strong> ${
              task.recordsExtracted || 0
            }</p>
            <p><strong>Duration:</strong> ${
              task.duration ? `${task.duration.toFixed(2)}s` : "N/A"
            }</p>
        </div>
    `;

  if (task.errorMessage) {
    detailsHtml += `
            <div style="background-color: #ffebee; padding: 10px; border-radius: 4px; margin-top: 15px;">
                <strong>Error:</strong> ${task.errorMessage}
            </div>
        `;
  }

  document.getElementById("details-content").innerHTML = detailsHtml;

  displayConfigDetails();

  document.getElementById("config-content").textContent = JSON.stringify(
    task.config || {},
    null,
    2
  );

  if (task.status === "completed") {
    fetchTableData(task.scanId, 0, pageSize);
  }

  document.getElementById("task-modal").style.display = "block";
}

// Display configuration details in a readable format
function displayConfigDetails() {
  if (!currentTask || !currentTask.config) return;

  const config = currentTask.config;
  let html = "<h4>Configuration Details</h4>";

  if (config.type) {
    const types = Array.isArray(config.type)
      ? config.type.join(", ")
      : config.type;
    html += `<p><strong>Entity Type:</strong> ${types}</p>`;
  }

  if (config.auth) {
    html += `<p><strong>Authentication:</strong> `;
    if (config.auth.client_id && config.auth.jwt_token) {
      html += `OAuth2 (Client ID + JWT Token)`;
    } else if (config.auth.apiKey) {
      html += `API Key (secured)`;
    } else {
      html += `Custom auth configuration`;
    }
    html += `</p>`;
  }

  if (config.filters) {
    html += `<div><strong>Filters:</strong><ul>`;

    if (config.filters.includeArchived !== undefined) {
      html += `<li>Include Archived: ${
        config.filters.includeArchived ? "Yes" : "No"
      }</li>`;
    }

    if (config.filters.dateRange) {
      const dateRange = config.filters.dateRange;
      html += `<li>Date Range: ${dateRange.startDate || "N/A"} to ${
        dateRange.endDate || "N/A"
      }</li>`;
    }

    if (config.filters.batchSize) {
      html += `<li>Batch Size: ${config.filters.batchSize}</li>`;
    }

    html += `</ul></div>`;
  }

  const detailsContent = document.getElementById("details-content");
  if (detailsContent) {
    detailsContent.innerHTML += `
            <div style="margin-top: 20px; border-top: 1px solid #ddd; padding-top: 15px;">
                ${html}
            </div>
        `;
  }
}

// Close modal
function closeModal() {
  document.getElementById("task-modal").style.display = "none";

  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
}

// Tab navigation
function openTab(evt, tabName) {
  document.querySelectorAll(".tabcontent").forEach((tab) => {
    tab.style.display = "none";
  });

  document.querySelectorAll(".tablinks").forEach((tab) => {
    tab.classList.remove("active");
  });

  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.classList.add("active");
}

// Fetch table data with pagination
function fetchTableData(taskId, offset = 0, limit = 10) {
  if (!currentTask || !currentTask.config || !currentTask.config.type) {
    document.getElementById("results").innerHTML =
      "<p>Error: Cannot determine task type</p>";
    return;
  }

  let tableName = currentTask.config.type;
  if (Array.isArray(tableName)) {
    tableName = tableName[0];
  }

  document.getElementById("results").innerHTML =
    '<div class="loading-indicator"><div class="spinner"></div><p>Loading data...</p></div>';

  fetch(
    `/api/results/${taskId}/result?tableName=${tableName}&offset=${offset}&limit=${limit}`
  )
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayTableData(data.data, offset, limit);
      } else {
        document.getElementById(
          "results"
        ).innerHTML = `<div class="error-message"><p>Error loading data: ${
          data.message || "Unknown error"
        }</p></div>`;
      }
    })
    .catch((error) => {
      console.error("Error fetching table data:", error);
      document.getElementById(
        "results"
      ).innerHTML = `<div class="error-message"><p>Error loading data: ${
        error.message || "Network error"
      }</p></div>`;
    });
}

// Display table data with pagination
function displayTableData(data, currentOffset, limit) {
  if (!data || !data.records || !data.records.length) {
    document.getElementById("results").innerHTML =
      '<div class="no-data-message"><p>No records available for this entity type.</p></div>';
    return;
  }

  const pagination = data.pagination || {
    total: data.records.length,
    limit: limit,
    offset: currentOffset,
    hasMore: false,
  };

  const pageNum = Math.floor(pagination.offset / pagination.limit) + 1;
  const totalPages = Math.ceil(pagination.total / pagination.limit);

  let html = `
        <div class="results-header">
            <h4>${data.tableName || "Results"}</h4>
            <p class="pagination-info">
                Showing ${pagination.offset + 1} to ${Math.min(
    pagination.offset + data.records.length,
    pagination.total
  )} 
                of ${pagination.total} records
            </p>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
    `;

  const columns = data.columns || Object.keys(data.records[0]);

  columns.forEach((column) => {
    html += `<th>${column}</th>`;
  });

  html += `</tr></thead><tbody>`;

  data.records.forEach((record) => {
    html += `<tr>`;
    columns.forEach((column) => {
      let value = record[column];
      if (typeof value === "object") {
        value = JSON.stringify(value);
      } else if (value === null || value === undefined) {
        value = "";
      }
      html += `<td>${value}</td>`;
    });
    html += `</tr>`;
  });

  html += `</tbody></table></div>`;

  html += `
        <div class="pagination-controls">
            <button 
                id="prev-page-btn" 
                ${pagination.offset <= 0 ? "disabled" : ""} 
                class="pagination-btn"
                data-offset="${Math.max(
                  0,
                  pagination.offset - pagination.limit
                )}"
                data-limit="${pagination.limit}">
                &laquo; Previous
            </button>
            <span class="page-info">Page ${pageNum} of ${totalPages || 1}</span>
            <button 
                id="next-page-btn" 
                ${!pagination.hasMore ? "disabled" : ""} 
                class="pagination-btn"
                data-offset="${pagination.offset + pagination.limit}"
                data-limit="${pagination.limit}">
                Next &raquo;
            </button>
            
            <div class="page-size-selector">
                <label for="page-size">Records per page:</label>
                <select id="page-size">
                    <option value="5" ${
                      limit === 5 ? "selected" : ""
                    }>5</option>
                    <option value="10" ${
                      limit === 10 ? "selected" : ""
                    }>10</option>
                    <option value="20" ${
                      limit === 20 ? "selected" : ""
                    }>20</option>
                    <option value="50" ${
                      limit === 50 ? "selected" : ""
                    }>50</option>
                    <option value="100" ${
                      limit === 100 ? "selected" : ""
                    }>100</option>
                </select>
            </div>
        </div>
    `;

  document.getElementById("results").innerHTML = html;

  const prevButton = document.getElementById("prev-page-btn");
  if (prevButton) {
    prevButton.addEventListener("click", function () {
      if (!this.disabled) {
        const newOffset = parseInt(this.getAttribute("data-offset"), 10);
        const pageLimit = parseInt(this.getAttribute("data-limit"), 10);
        fetchTableData(currentTask.scanId, newOffset, pageLimit);
      }
    });
  }

  const nextButton = document.getElementById("next-page-btn");
  if (nextButton) {
    nextButton.addEventListener("click", function () {
      if (!this.disabled) {
        const newOffset = parseInt(this.getAttribute("data-offset"), 10);
        const pageLimit = parseInt(this.getAttribute("data-limit"), 10);
        fetchTableData(currentTask.scanId, newOffset, pageLimit);
      }
    });
  }

  const pageSizeSelector = document.getElementById("page-size");
  if (pageSizeSelector) {
    pageSizeSelector.addEventListener("change", function () {
      const newLimit = parseInt(this.value, 10);
      fetchTableData(currentTask.scanId, 0, newLimit);
    });
  }
}

// Start streaming data
function startStreaming() {
  if (!currentTask) return;

  const streamContainer = document.getElementById("stream-container");
  streamContainer.innerHTML =
    '<div class="loading-indicator"><div class="spinner"></div><p>Loading stream data...</p></div>';

  document.getElementById("start-stream-btn").disabled = true;
  document.getElementById("start-stream-btn").textContent = "Loading...";

  fetch(`/api/stream/${currentTask.scanId}?offset=0&limit=100`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayStreamData(data);
      } else {
        streamContainer.innerHTML = `
                    <div class="error-message">
                        <p>Error loading stream data: ${
                          data.message || "Unknown error"
                        }</p>
                    </div>
                `;
        resetStreamButton();
      }
    })
    .catch((error) => {
      console.error("Error fetching stream data:", error);
      streamContainer.innerHTML = `
                <div class="error-message">
                    <p>Error loading stream data: ${
                      error.message || "Network error"
                    }</p>
                </div>
            `;
      resetStreamButton();
    });
}

// Display stream data
function displayStreamData(data) {
  const streamContainer = document.getElementById("stream-container");

  let html = `
        <div class="stream-summary">
            <h4>Stream Summary</h4>
            <div class="stream-stats">
                <div class="stat-item">
                    <span class="stat-value">${data.data.total_count}</span>
                    <span class="stat-label">Records Streamed</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${data.data.total_batches}</span>
                    <span class="stat-label">Batches</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${data.data.entity_type}</span>
                    <span class="stat-label">Entity Type</span>
                </div>
            </div>
            
            <div class="stream-details">
                <p><strong>Topic:</strong> ${data.data.topic}</p>
                <p><strong>Organization ID:</strong> ${data.data.organization_id}</p>
                <p><strong>Scan ID:</strong> ${data.data.scan_id}</p>
                <p><strong>Message:</strong> ${data.message}</p>
            </div>
        </div>
    `;

  streamContainer.innerHTML = html;

  document.getElementById("start-stream-btn").disabled = false;
  document.getElementById("start-stream-btn").textContent = "Refresh Stream";
}

// Display statistics from API data
function displayStatsFromAPI(data) {
  const jobStats = data.jobs;
  const serviceInfo = data.service || {};
  const statusBreakdown = jobStats.status_breakdown || {};

  let uptimeDisplay = "N/A";
  if (serviceInfo.uptime) {
    uptimeDisplay = new Date(serviceInfo.uptime).toLocaleString();
  }

  let statsHtml = `
        <div class="task-stats">
            <div class="stat-card total">
                <span class="stat-value">${jobStats.total_jobs || 0}</span>
                <span class="stat-label">Total Tasks</span>
            </div>
            <div class="stat-card running">
                <span class="stat-value">${statusBreakdown.running || 0}</span>
                <span class="stat-label">Running</span>
            </div>
            <div class="stat-card completed">
                <span class="stat-value">${
                  statusBreakdown.completed || 0
                }</span>
                <span class="stat-label">Completed</span>
            </div>
            <div class="stat-card failed">
                <span class="stat-value">${
                  (statusBreakdown.failed || 0) + (statusBreakdown.crashed || 0)
                }</span>
                <span class="stat-label">Failed</span>
            </div>
        </div>
        <div class="service-info">
            <div class="service-header">
                <h4>Service Information</h4>
                <span class="service-uptime">Started: ${uptimeDisplay}</span>
            </div>
            <div class="extra-stats">
                <div class="extra-stat-item">
                    <span class="extra-stat-label">Service Name</span>
                    <span class="extra-stat-value">${
                      serviceInfo.name || "N/A"
                    }</span>
                </div>
                <div class="extra-stat-item">
                    <span class="extra-stat-label">Source Type</span>
                    <span class="extra-stat-value">${
                      serviceInfo.source_type || "N/A"
                    }</span>
                </div>
                <div class="extra-stat-item">
                    <span class="extra-stat-label">Total Records Extracted</span>
                    <span class="extra-stat-value">${
                      jobStats.total_records_extracted?.toLocaleString() || 0
                    }</span>
                </div>
                <div class="extra-stat-item">
                    <span class="extra-stat-label">Recent Jobs (7 Days)</span>
                    <span class="extra-stat-value">${
                      jobStats.recent_jobs_7_days || 0
                    }</span>
                </div>
                <div class="extra-stat-item">
                    <span class="extra-stat-label">Database</span>
                    <span class="extra-stat-value">${
                      data.database?.database || "N/A"
                    }</span>
                </div>
                <div class="extra-stat-item">
                    <span class="extra-stat-label">Database Size</span>
                    <span class="extra-stat-value">${
                      data.database?.size_pretty || "N/A"
                    }</span>
                </div>
                <div class="extra-stat-item">
                    <span class="extra-stat-label">Database Status</span>
                    <span class="extra-stat-value ${
                      data.database?.connected
                        ? "status-completed"
                        : "status-failed"
                    }">
                        ${
                          data.database?.connected
                            ? "Connected"
                            : "Disconnected"
                        }
                    </span>
                </div>
                <div class="extra-stat-item">
                    <span class="extra-stat-label">Last Updated</span>
                    <span class="extra-stat-value">${new Date().toLocaleTimeString()}</span>
                </div>
            </div>
        </div>
    `;

  let statsContainer = document.getElementById("task-stats-container");
  if (!statsContainer) {
    statsContainer = document.createElement("div");
    statsContainer.id = "task-stats-container";

    const resultsHeader = document.querySelector(".results-header");
    if (resultsHeader) {
      resultsHeader.parentNode.insertBefore(statsContainer, resultsHeader);
    } else {
      const taskList = document.getElementById("task-list");
      if (taskList) {
        taskList.insertAdjacentElement("afterbegin", statsContainer);
      }
    }
  }

  statsContainer.innerHTML = statsHtml;
}

// Reset the stream button
function resetStreamButton() {
  const streamButton = document.getElementById("start-stream-btn");
  if (streamButton) {
    streamButton.disabled = false;
    streamButton.textContent = "Start Streaming";
  }
}

// Task management functions
function removeTask(taskId) {
  if (confirm("Are you sure you want to remove this task?")) {
    fetch(`/api/scan/${taskId}/remove`, {
      method: "DELETE",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("Task removed successfully");
          fetchTasks();
          closeModal();
        } else {
          alert(`Error: ${data.message || "Unknown error"}`);
        }
      })
      .catch((error) => {
        console.error("Error removing task:", error);
        alert(`Error removing task: ${error.message || "Network error"}`);
      });
  }
}

function cancelTask(taskId) {
  if (confirm("Are you sure you want to cancel this task?")) {
    fetch(`/api/scan/${taskId}/cancel`, {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("Task cancelled successfully");
          fetchTasks();
          closeModal();
        } else {
          alert(`Error: ${data.message || "Unknown error"}`);
        }
      })
      .catch((error) => {
        console.error("Error cancelling task:", error);
        alert(`Error cancelling task: ${error.message || "Network error"}`);
      });
  }
}

function pauseTask(taskId) {
  fetch(`/api/scan/${taskId}/pause`, {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Task paused successfully");
        fetchTasks();
        closeModal();
      } else {
        alert(`Error: ${data.message || "Unknown error"}`);
      }
    })
    .catch((error) => {
      console.error("Error pausing task:", error);
      alert(`Error pausing task: ${error.message || "Network error"}`);
    });
}

function resumeTask(taskId) {
  fetch(`/api/scan/${taskId}/resume`, {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Task resumed successfully");
        fetchTasks();
        closeModal();
      } else {
        alert(`Error: ${data.message || "Unknown error"}`);
      }
    })
    .catch((error) => {
      console.error("Error resuming task:", error);
      alert(`Error resuming task: ${error.message || "Network error"}`);
    });
}

function fetchStats() {
  fetch("/api/stats")
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayStatsFromAPI(data.data);
      } else {
        console.error("Error fetching stats:", data.message);
      }
    })
    .catch((error) => {
      console.error("Error fetching stats:", error);
    });
}

// Window events
window.onclick = function (event) {
  const modal = document.getElementById("task-modal");
  if (event.target === modal) {
    closeModal();
  }
  const scanModal = document.getElementById("start-scan-modal");
  if (event.target === scanModal) {
    closeStartScanModal();
  }
};

// Cleanup on page unload
window.addEventListener("beforeunload", function () {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
  }
});

// Function to create the start scan modal
function createStartScanModal() {
  const modal = document.createElement("div");
  modal.id = "start-scan-modal";
  modal.className = "modal";

  const currentYear = new Date().getFullYear();
  const defaultStartDate = `${currentYear}-01-01`;
  const defaultEndDate = `${currentYear}-12-31`;

  modal.innerHTML = `
        <div class="modal-content">
            <span class="close" id="close-scan-modal">&times;</span>
            <h2>Start New eMoney Service Extraction</h2>
            
            <div class="scan-form-container">
                <form id="start-scan-form">
                    <div class="form-section">
                        <h3>Basic Information</h3>
                        <div class="form-group">
                            <label for="scanId">Scan ID</label>
                            <input type="text" id="scanId" name="scanId" value="emoney-service-${currentYear}-001" placeholder="e.g., emoney-service-2025-001" required>
                            <span class="form-hint">Unique identifier for this extraction</span>
                        </div>
                        
                        <div class="form-group">
                            <label for="organizationId">Organization ID</label>
                            <input type="text" id="organizationId" name="organizationId" value="org-12345" placeholder="e.g., org-12345" required>
                            <span class="form-hint">ID of the organization</span>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h3>Entity Type</h3>
                        <div class="form-group radio-group">
                            <p class="radio-label">Select the eMoney service entity to extract:</p>
                            
                            <div class="radio-options">
                                <div class="radio-option">
                                    <input type="radio" id="type-user" name="type" value="user" checked required>
                                    <label for="type-user">User</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-role" name="type" value="role">
                                    <label for="type-role">Role</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-permission" name="type" value="permission">
                                    <label for="type-permission">Permission</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-office" name="type" value="office">
                                    <label for="type-office">Office</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-logon" name="type" value="logon">
                                    <label for="type-logon">Logon</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-sharingrule" name="type" value="sharingrule">
                                    <label for="type-sharingrule">Sharing Rule</label>
                                </div>

                                <div class="radio-option">
                                    <input type="radio" id="type-plan" name="type" value="plan" checked required>
                                    <label for="type-plan">Plan</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-goal" name="type" value="goal">
                                    <label for="type-goal">Goal</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-scenario" name="type" value="scenario">
                                    <label for="type-scenario">Scenario</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-cashflow" name="type" value="cashflow">
                                    <label for="type-cashflow">Cash Flow</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-networth" name="type" value="networth">
                                    <label for="type-networth">Net Worth</label>
                                </div>

                                 <div class="radio-option">
                                    <input type="radio" id="type-household" name="type" value="household" checked required>
                                    <label for="type-household">Household</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-client" name="type" value="client">
                                    <label for="type-client">Client</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-contact" name="type" value="contact">
                                    <label for="type-contact">Contact</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-relationship" name="type" value="relationship">
                                    <label for="type-relationship">Relationship</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-spouse" name="type" value="spouse">
                                    <label for="type-spouse">Spouse</label>
                                </div>

                                <div class="radio-option">
                                    <input type="radio" id="type-account" name="type" value="account" checked required>
                                    <label for="type-account">Account</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-accounttype" name="type" value="accounttype">
                                    <label for="type-accounttype">Account Type</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-liability" name="type" value="liability">
                                    <label for="type-liability">Liability</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-asset" name="type" value="asset">
                                    <label for="type-asset">Asset</label>
                                </div>
                                
                                <div class="radio-option">
                                    <input type="radio" id="type-assetclass" name="type" value="assetclass">
                                    <label for="type-assetclass">Asset Class</label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h3>Authentication</h3>
                        <div class="form-group">
                            <label for="clientId">Client ID</label>
                            <input type="text" id="clientId" name="clientId" value="emoney-client-id-12345" placeholder="Enter client ID" required>
                            <span class="form-hint">Your eMoney client ID</span>
                        </div>
                        
                        <div class="form-group">
                            <label for="jwtToken">JWT Token</label>
                            <input type="password" id="jwtToken" name="jwtToken" value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." placeholder="Enter JWT token" required>
                            <span class="form-hint">Your eMoney JWT token</span>
                        </div>
                        
                        <div class="form-group">
                            <label for="apiKey">API Key</label>
                            <input type="password" id="apiKey" name="apiKey" value="emoney-api-key-67890" placeholder="Enter API key" required>
                            <span class="form-hint">Your eMoney API key</span>
                        </div>
                        
                        <div class="form-group">
                            <label for="firmId">Firm ID</label>
                            <input type="text" id="firmId" name="firmId" value="firm-12345" placeholder="Enter firm ID" required>
                            <span class="form-hint">Your eMoney firm ID</span>
                        </div>
                        
                        <div class="form-group">
                            <label for="scope">Scope</label>
                            <input type="text" id="scope" name="scope" value="API" placeholder="Enter scope" required>
                            <span class="form-hint">Access scope (default: API)</span>
                        </div>
                        
                        <div class="auth-notice">
                            <p>Uses Client ID, JWT token, API key, Firm ID, and Scope for authentication</p>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h3>Filters</h3>
                        <div class="form-group checkbox-group">
                            <input type="checkbox" id="includeArchived" name="includeArchived">
                            <label for="includeArchived">Include archived items</label>
                        </div>
                        
                        <div class="form-group date-range">
                            <label>Date Range</label>
                            <div class="date-inputs">
                                <div class="date-input">
                                    <label for="startDate">Start Date</label>
                                    <input type="date" id="startDate" name="startDate" value="${defaultStartDate}">
                                </div>
                                <div class="date-input">
                                    <label for="endDate">End Date</label>
                                    <input type="date" id="endDate" name="endDate" value="${defaultEndDate}">
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="batchSize">Batch Size</label>
                            <input type="number" id="batchSize" name="batchSize" value="100" min="1" max="1000" placeholder="Enter batch size">
                            <span class="form-hint">Number of records per batch (default: 100)</span>
                        </div>
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" id="cancel-scan-btn" class="cancel-action-btn">Cancel</button>
                        <button type="submit" class="submit-action-btn">Start Extraction</button>
                    </div>
                </form>
            </div>
        </div>
    `;

  document.body.appendChild(modal);

  document
    .getElementById("close-scan-modal")
    .addEventListener("click", closeStartScanModal);
  document
    .getElementById("cancel-scan-btn")
    .addEventListener("click", closeStartScanModal);
  document
    .getElementById("start-scan-form")
    .addEventListener("submit", submitScanForm);
}

// Function to open the start scan modal
function openStartScanModal() {
  document.getElementById("start-scan-modal").style.display = "block";
}

// Function to close the start scan modal
function closeStartScanModal() {
  document.getElementById("start-scan-modal").style.display = "none";
  document.getElementById("start-scan-form").reset();
}

// Function to submit the scan form
function submitScanForm(event) {
  event.preventDefault();

  const scanId = document.getElementById("scanId").value;
  const organizationId = document.getElementById("organizationId").value;
  const type = document.querySelector('input[name="type"]:checked').value;
  const clientId = document.getElementById("clientId").value;
  const jwtToken = document.getElementById("jwtToken").value;
  const apiKey = document.getElementById("apiKey").value;
  const firmId = document.getElementById("firmId").value;
  const scope = document.getElementById("scope").value;
  const includeArchived = document.getElementById("includeArchived").checked;
  const startDate = document.getElementById("startDate").value;
  const endDate = document.getElementById("endDate").value;
  const batchSize = document.getElementById("batchSize").value;

  if (!scanId || !organizationId || !type) {
    alert("Please fill in all required fields");
    return;
  }

  if (!clientId || !jwtToken || !apiKey || !firmId || !scope) {
    alert("Please provide all authentication fields");
    return;
  }

  const config = {
    scanId: scanId,
    organizationId: organizationId,
    type: [type],
    auth: {
      client_id: clientId,
      jwt_token: jwtToken,
      api_key: apiKey,
      firm_id: firmId,
      scope: scope,
    },
  };

  if (includeArchived || startDate || endDate || batchSize) {
    config.filters = {};

    if (includeArchived) {
      config.filters.includeArchived = true;
    }

    if (startDate || endDate) {
      config.filters.dateRange = {};

      if (startDate) {
        config.filters.dateRange.startDate = startDate;
      }

      if (endDate) {
        config.filters.dateRange.endDate = endDate;
      }
    }

    if (batchSize) {
      config.filters.batchSize = parseInt(batchSize, 10);
    }
  }

  fetch("/api/scan/start", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ config }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("eMoney service extraction started successfully!");
        closeStartScanModal();
        fetchTasks();
      } else {
        alert(`Error starting extraction: ${data.message || "Unknown error"}`);
      }
    })
    .catch((error) => {
      console.error("Error starting extraction:", error);
      alert(`Error starting extraction: ${error.message || "Network error"}`);
    });
}
