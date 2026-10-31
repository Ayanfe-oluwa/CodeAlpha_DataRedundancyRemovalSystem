
const API_URL = "";

// Dashboard elements
const form = document.getElementById("record-form");
const resultBox = document.getElementById("result");
const submitButton = document.getElementById("submit-button");

// Track duplicate and conflict attempts in this browser
function getCount(key) {
    return Number(localStorage.getItem(key) || 0);
}

function updateCounters() {
    document.getElementById("duplicate-count").textContent =
        getCount("duplicates_detected");

    document.getElementById("conflict-count").textContent =
        getCount("conflicts_detected");
}

// Display submission results
function showResult(message, type) {
    resultBox.textContent = message;
    resultBox.className = type;
    resultBox.hidden = false;
}

// Check backend connection
async function checkAPI() {
    const status = document.querySelector(".connection");

    try {
        const response = await fetch("/health");

        if (!response.ok) {
            throw new Error("Connection failed");
        }

        status.innerHTML =
            '<span class="dot"></span> System Online';

    } catch (error) {
        status.innerHTML =
            '<span style="color:red">●</span> System Offline';
    }
}

// Safely display text in HTML
function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}

// Load database records
async function loadRecords() {
    try {
        const response = await fetch("/records?limit=500");

        if (!response.ok) {
            throw new Error("Unable to load records");
        }

        const records = await response.json();

        document.getElementById("total-records").textContent =
            records.length;

        document.getElementById("unique-records").textContent =
            records.length;

        displayRecords(records);

    } catch (error) {
        document.getElementById("records-body").innerHTML =
            `<tr><td colspan="5">${escapeHTML(error.message)}</td></tr>`;
    }

    updateCounters();
}

// Display records with Delete buttons
function displayRecords(records) {
    const tableBody = document.getElementById("records-body");

    if (records.length === 0) {
        tableBody.innerHTML =
            '<tr><td colspan="5">No records found.</td></tr>';
        return;
    }

    tableBody.innerHTML = records.map(record => `
        <tr>
            <td>${escapeHTML(record.id)}</td>
            <td>${escapeHTML(record.name)}</td>
            <td>${escapeHTML(record.email)}</td>
            <td>${escapeHTML(record.description || "")}</td>
            <td>
                <button
                    class="delete-button"
                    onclick="deleteRecord(${Number(record.id)})">
                    Delete
                </button>
            </td>
        </tr>
    `).join("");
}

// Delete a selected record
async function deleteRecord(recordId) {
    const confirmed = confirm(
        `Are you sure you want to permanently delete record ${recordId}?`
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(`/records/${recordId}`, {
            method: "DELETE"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Unable to delete record.");
        }

        showResult(data.message, "success");

        // Refresh records and dashboard
        await loadRecords();

    } catch (error) {
        showResult(error.message, "error");
    }
}

// Submit and validate a new record
form.addEventListener("submit", async function(event) {
    event.preventDefault();

    submitButton.disabled = true;
    submitButton.textContent = "Processing...";

    resultBox.hidden = true;

    const record = {
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        description: document.getElementById("description").value.trim()
    };

    try {
        const response = await fetch("/records", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(record)
        });

        const data = await response.json();

        if (!response.ok) {
            const detail = Array.isArray(data.detail)
                ? data.detail.map(item => item.msg).join("; ")
                : data.detail || "Submission failed.";

            throw new Error(detail);
        }

        if (data.status === "unique") {
            showResult(
                "SUCCESS: " + data.message,
                "success"
            );

            form.reset();

        } else if (data.status === "duplicate") {
            localStorage.setItem(
                "duplicates_detected",
                getCount("duplicates_detected") + 1
            );

            showResult(
                "DUPLICATE DETECTED: " + data.message,
                "duplicate"
            );

        } else if (data.status === "potential_conflict") {
            localStorage.setItem(
                "conflicts_detected",
                getCount("conflicts_detected") + 1
            );

            showResult(
                "POTENTIAL CONFLICT: " + data.message,
                "conflict"
            );
        } else {
            showResult(
                data.message || "Submission processed.",
                "success"
            );
        }

        await loadRecords();

    } catch (error) {
        showResult(error.message, "error");

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Validate and Save Record";
    }
});

// Search stored records
document.getElementById("search").addEventListener("input", async function() {
    const searchTerm = this.value.toLowerCase();

    try {
        const response = await fetch("/records?limit=500");

        if (!response.ok) {
            throw new Error("Unable to search records");
        }

        const records = await response.json();

        const filteredRecords = records.filter(record =>
            String(record.name || "").toLowerCase().includes(searchTerm) ||
            String(record.email || "").toLowerCase().includes(searchTerm) ||
            String(record.description || "").toLowerCase().includes(searchTerm)
        );

        displayRecords(filteredRecords);

    } catch (error) {
        document.getElementById("records-body").innerHTML =
            `<tr><td colspan="5">${escapeHTML(error.message)}</td></tr>`;
    }
});

// Initialize dashboard
async function initializeDashboard() {
    await checkAPI();
    await loadRecords();
}

initializeDashboard();
