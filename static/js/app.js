// ============================================================
// PR Test Scenario Generator — Frontend Logic
// ============================================================

// Test case field constants
const VALID_PRIORITIES = ['high', 'medium', 'low'];
const VALID_TYPES = ['functional', 'regression', 'e2e'];

// Mapping status colours (must match CSS classes)
const STATUS_CLASSES = {
    'MAPPED':         'status-mapped',
    'POSSIBLE MATCH': 'status-possible',
    'NOT COVERED':    'status-notcovered',
    'NEW':            'status-new',
};

// Module-level state
let uploadedExcelFile = null;       // File object from input
let currentMappingResult = null;    // Last mapping response data

// DOM references
const prForm = document.getElementById('prForm');
const inputSection = document.getElementById('inputSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

// ============================================================
// On page load: check Jira health
// ============================================================
(async function initJiraBadge() {
    try {
        const res = await fetch('/api/jira/health');
        const data = await res.json();
        const badge = document.getElementById('jiraBadge');
        if (data.enabled) {
            badge.classList.remove('hidden');
            document.getElementById('jiraDot').className = data.connected
                ? 'jira-dot jira-dot-connected'
                : 'jira-dot jira-dot-disconnected';
            document.getElementById('jiraBadgeText').textContent = data.connected ? 'Jira Connected' : 'Jira Error';
        }
    } catch (_) { /* Jira badge is purely informational — ignore errors */ }
})();

// ============================================================
// Tab switching
// ============================================================
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
    });
});

// ============================================================
// Excel file upload — drag-and-drop + click-to-browse
// ============================================================
const uploadZone = document.getElementById('uploadZone');
const excelFileInput = document.getElementById('excelFile');
const uploadPreview = document.getElementById('uploadPreview');
const uploadFileName = document.getElementById('uploadFileName');
const removeFileBtn = document.getElementById('removeFile');

uploadZone.addEventListener('click', () => excelFileInput.click());
uploadZone.querySelector('.upload-browse').addEventListener('click', (e) => {
    e.stopPropagation();
    excelFileInput.click();
});

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) setExcelFile(file);
});

excelFileInput.addEventListener('change', () => {
    if (excelFileInput.files[0]) setExcelFile(excelFileInput.files[0]);
});

removeFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    clearExcelFile();
});

function setExcelFile(file) {
    if (!file.name.match(/\.(xlsx|xls)$/i)) {
        showError('Please upload an Excel file (.xlsx or .xls)');
        return;
    }
    uploadedExcelFile = file;
    uploadFileName.textContent = file.name;
    uploadZone.classList.add('hidden');
    uploadPreview.classList.remove('hidden');
}

function clearExcelFile() {
    uploadedExcelFile = null;
    excelFileInput.value = '';
    uploadZone.classList.remove('hidden');
    uploadPreview.classList.add('hidden');
}

// ============================================================
// Form submission
// ============================================================
prForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
    const generateCode = document.getElementById('generateCode').checked;

    if (activeTab === 'pr-url') {
        const prUrl = document.getElementById('prUrl').value.trim();
        if (!prUrl) { showError('Please enter a GitHub PR URL'); return; }
        await analyzePR(prUrl, generateCode);
    } else {
        const diffText = document.getElementById('diffText').value.trim();
        if (!diffText) { showError('Please enter git diff content'); return; }
        await analyzeDiff(diffText, generateCode);
    }
});

// ============================================================
// Analyze PR
// ============================================================
async function analyzePR(prUrl, generateCode) {
    showLoading();
    try {
        updateLoadingStep(1, 'Fetching PR data from GitHub...');

        const response = await fetch('/api/analyze-pr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pr_url: prUrl, generate_code: generateCode })
        });

        const result = await response.json();
        if (!result.success) { showError(result.error || 'An error occurred'); return; }

        updateLoadingStep(2, 'Analyzing code changes...');
        await sleep(300);
        updateLoadingStep(3, 'Generating test scenarios with AI...');
        await sleep(300);

        await runMappingIfNeeded(result.data);
        showResults(result.data, true);

    } catch (error) {
        showError(`Network error: ${error.message}`);
    }
}

// ============================================================
// Analyze manual diff
// ============================================================
async function analyzeDiff(diffText, generateCode) {
    showLoading();
    try {
        updateLoadingStep(2, 'Analyzing code changes...');

        const response = await fetch('/api/analyze-diff', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ diff_text: diffText, generate_code: generateCode })
        });

        const result = await response.json();
        if (!result.success) { showError(result.error || 'An error occurred'); return; }

        updateLoadingStep(3, 'Generating test scenarios with AI...');
        await sleep(300);

        await runMappingIfNeeded(result.data);
        showResults(result.data, false);

    } catch (error) {
        showError(`Network error: ${error.message}`);
    }
}

// ============================================================
// Mapping — called after analysis if Excel was uploaded
// ============================================================
async function runMappingIfNeeded(analysisData) {
    if (!uploadedExcelFile) return;

    const step4 = document.getElementById('step4');
    step4.classList.remove('hidden');
    updateLoadingStep(4, 'Mapping with your existing test cases...');

    try {
        const formData = new FormData();
        formData.append('excel_file', uploadedExcelFile, uploadedExcelFile.name);
        formData.append('structured_test_cases', JSON.stringify(analysisData.structured_test_cases || []));

        const res = await fetch('/api/map-excel', { method: 'POST', body: formData });
        const result = await res.json();

        if (result.success) {
            // Attach mapping data to analysisData for showResults to pick up
            analysisData._mappingResult = result.data;
        } else {
            console.warn('Mapping failed:', result.error);
            // Non-fatal — continue showing analysis results without mapping
        }
    } catch (err) {
        console.warn('Mapping request failed:', err.message);
    }
}

// ============================================================
// Show loading state
// ============================================================
function showLoading() {
    inputSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');

    // Hide step4 until needed
    document.getElementById('step4').classList.add('hidden');
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
}

function updateLoadingStep(stepNum, text) {
    document.getElementById('loadingText').textContent = text;
    const stepEl = document.getElementById(`step${stepNum}`);
    if (stepEl) stepEl.classList.add('active');
}

// ============================================================
// Show results
// ============================================================
function showResults(data, isPR = true) {
    inputSection.classList.add('hidden');
    loadingSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // PR info card
    const prInfoCard = document.getElementById('prInfoCard');
    if (isPR && data.pr_info) {
        prInfoCard.classList.remove('hidden');
        document.getElementById('prTitle').textContent = data.pr_info.title || '-';
        document.getElementById('prAuthor').textContent = data.pr_info.author || '-';
        document.getElementById('prBranches').textContent =
            `${data.pr_info.base_branch || 'base'} ← ${data.pr_info.head_branch || 'head'}`;
    } else {
        prInfoCard.classList.add('hidden');
    }

    // Summary stats
    document.getElementById('totalFiles').textContent = data.summary.total_files;
    document.getElementById('totalAdditions').textContent = data.summary.total_additions;
    document.getElementById('totalDeletions').textContent = data.summary.total_deletions;

    // File changes
    const fileChangesContainer = document.getElementById('fileChanges');
    fileChangesContainer.innerHTML = '';
    if (data.file_analyses && data.file_analyses.length > 0) {
        const heading = document.createElement('h3');
        heading.textContent = 'Modified Files';
        heading.style.cssText = 'margin-bottom:1rem;font-size:1.125rem';
        fileChangesContainer.appendChild(heading);
        data.file_analyses.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <span class="file-path">${escapeHtml(file.file_path)}</span>
                <div class="file-stats">
                    <span class="additions">+${file.additions}</span>
                    <span class="deletions">-${file.deletions}</span>
                </div>`;
            fileChangesContainer.appendChild(fileItem);
        });
    }

    // Test scenarios (HTML)
    document.getElementById('testScenarios').innerHTML = data.test_scenarios_html || data.test_scenarios;
    window.currentTestScenarios = data.test_scenarios;

    // Structured test cases
    const testCasesCard = document.getElementById('testCasesCard');
    const downloadScenariosCsvBtn = document.getElementById('downloadScenariosCsvBtn');
    if (data.structured_test_cases && data.structured_test_cases.length > 0) {
        window.currentTestCases = data.structured_test_cases;
        populateTestCases(data.structured_test_cases);
        testCasesCard.classList.remove('hidden');
        downloadScenariosCsvBtn.classList.remove('hidden');
    } else {
        testCasesCard.classList.add('hidden');
        downloadScenariosCsvBtn.classList.add('hidden');
    }

    // Coverage mapping
    const mappingCard = document.getElementById('mappingCard');
    if (data._mappingResult) {
        currentMappingResult = data._mappingResult;
        renderMappingResults(data._mappingResult, data.structured_test_cases || []);
        mappingCard.classList.remove('hidden');
    } else {
        mappingCard.classList.add('hidden');
        currentMappingResult = null;
    }

    // Test code
    const testCodeCard = document.getElementById('testCodeCard');
    if (data.test_code) {
        testCodeCard.classList.remove('hidden');
        document.getElementById('testCode').textContent = data.test_code;
        window.currentTestCode = data.test_code;
    } else {
        testCodeCard.classList.add('hidden');
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================================
// Populate structured test cases grid
// ============================================================
function populateTestCases(cases) {
    const grid = document.getElementById('testCasesGrid');
    const countBadge = document.getElementById('testCasesCount');

    grid.innerHTML = '';
    countBadge.textContent = `${cases.length} Test Cases`;

    cases.forEach(tc => {
        const priority = (tc.priority || 'medium').toLowerCase();
        const type = (tc.type || 'functional').toLowerCase();

        const stepsHtml = Array.isArray(tc.steps) && tc.steps.length > 0
            ? `<ol>${tc.steps.map(s => `<li>${escapeHtml(s)}</li>`).join('')}</ol>`
            : '<p>No steps provided</p>';

        const card = document.createElement('div');
        card.className = 'test-case-card';
        card.dataset.priority = priority;
        card.dataset.type = type;
        card.innerHTML = `
            <div class="tc-header">
                <span class="tc-id">${escapeHtml(tc.id || 'TC-?')}</span>
                <span class="tc-priority priority-${priority}">${priority.toUpperCase()}</span>
                <span class="tc-type">${escapeHtml(type)}</span>
            </div>
            <h4 class="tc-title">${escapeHtml(tc.title || 'Untitled')}</h4>
            ${tc.category ? `<div class="tc-category"><i class="fas fa-tag"></i> ${escapeHtml(tc.category)}</div>` : ''}
            <div class="tc-steps"><strong>Steps:</strong>${stepsHtml}</div>
            <div class="tc-expected"><strong>Expected:</strong> ${escapeHtml(tc.expected_result || 'N/A')}</div>`;
        grid.appendChild(card);
    });

    // Reset filter to "All"
    document.querySelectorAll('#testCasesFilters .filter-btn').forEach(b => b.classList.remove('active'));
    const allBtn = document.querySelector('#testCasesFilters .filter-btn[data-filter="all"]');
    if (allBtn) allBtn.classList.add('active');
}

// Filter: test cases
document.getElementById('testCasesFilters').addEventListener('click', (e) => {
    const btn = e.target.closest('.filter-btn');
    if (!btn || !btn.dataset.filter) return;

    document.querySelectorAll('#testCasesFilters .filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const filter = btn.dataset.filter;
    document.querySelectorAll('.test-case-card').forEach(card => {
        if (filter === 'all') {
            card.classList.remove('hidden');
        } else if (VALID_PRIORITIES.includes(filter)) {
            card.classList.toggle('hidden', card.dataset.priority !== filter);
        } else {
            card.classList.toggle('hidden', card.dataset.type !== filter);
        }
    });
});

// ============================================================
// Render mapping results
// ============================================================
function renderMappingResults(mappingData, generatedCases) {
    const { mappings = [], new_generated = [], stats = {} } = mappingData;

    // Stats bar
    const statsEl = document.getElementById('mappingStats');
    statsEl.innerHTML = `
        <div class="mapping-stat-item status-mapped">
            <span class="mapping-stat-count">${stats.mapped || 0}</span>
            <span class="mapping-stat-label">Mapped</span>
        </div>
        <div class="mapping-stat-item status-possible">
            <span class="mapping-stat-count">${stats.possible_match || 0}</span>
            <span class="mapping-stat-label">Possible Match</span>
        </div>
        <div class="mapping-stat-item status-notcovered">
            <span class="mapping-stat-count">${stats.not_covered || 0}</span>
            <span class="mapping-stat-label">Not Covered</span>
        </div>
        <div class="mapping-stat-item status-new">
            <span class="mapping-stat-count">${stats.new_generated || 0}</span>
            <span class="mapping-stat-label">New</span>
        </div>`;

    document.getElementById('mappingBadge').textContent =
        `${stats.total_excel || 0} existing · ${stats.total_generated || 0} generated`;

    // Build a quick lookup for generated TC titles
    const generatedById = {};
    generatedCases.forEach(tc => { if (tc.id) generatedById[tc.id] = tc; });

    const tbody = document.getElementById('mappingTableBody');
    tbody.innerHTML = '';

    // Existing rows
    mappings.forEach(m => {
        const tr = document.createElement('tr');
        tr.dataset.mstatus = m.status;
        const statusClass = STATUS_CLASSES[m.status] || '';
        const confBar = m.confidence
            ? `<div class="conf-bar-wrap"><div class="conf-bar" style="width:${m.confidence}%"></div><span>${m.confidence}%</span></div>`
            : '—';
        tr.innerHTML = `
            <td>${escapeHtml(m.raw_id || String(m.excel_row_index))}</td>
            <td><span class="status-badge ${statusClass}">${escapeHtml(m.status)}</span></td>
            <td>${m.generated_tc_id
                ? `<span class="tc-ref">${escapeHtml(m.generated_tc_id)}</span> ${escapeHtml(m.generated_title || '')}`
                : '—'}</td>
            <td>${confBar}</td>
            <td>${escapeHtml(m.notes || '')}</td>`;
        tbody.appendChild(tr);
    });

    // NEW generated rows
    new_generated.forEach(tc => {
        const tr = document.createElement('tr');
        tr.dataset.mstatus = 'NEW';
        tr.innerHTML = `
            <td>—</td>
            <td><span class="status-badge status-new">NEW</span></td>
            <td><span class="tc-ref">${escapeHtml(tc.id || '')}</span> ${escapeHtml(tc.title || '')}</td>
            <td>—</td>
            <td>Not present in existing test suite</td>`;
        tbody.appendChild(tr);
    });

    // Reset mapping filter
    document.querySelectorAll('#mappingFilters .filter-btn').forEach(b => b.classList.remove('active'));
    const allMBtn = document.querySelector('#mappingFilters .filter-btn[data-mfilter="all"]');
    if (allMBtn) allMBtn.classList.add('active');
}

// Filter: mapping table
document.getElementById('mappingFilters').addEventListener('click', (e) => {
    const btn = e.target.closest('.filter-btn');
    if (!btn || !btn.dataset.mfilter) return;

    document.querySelectorAll('#mappingFilters .filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const filter = btn.dataset.mfilter;
    document.querySelectorAll('#mappingTableBody tr').forEach(row => {
        row.classList.toggle('hidden', filter !== 'all' && row.dataset.mstatus !== filter);
    });
});

// Download mapped Excel
document.getElementById('downloadMappedExcelBtn').addEventListener('click', async () => {
    if (!uploadedExcelFile || !currentMappingResult) return;

    try {
        const btn = document.getElementById('downloadMappedExcelBtn');
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Preparing...';
        btn.disabled = true;

        const formData = new FormData();
        formData.append('excel_file', uploadedExcelFile, uploadedExcelFile.name);
        formData.append('mapping_result', JSON.stringify(currentMappingResult));

        const res = await fetch('/api/download-mapped-excel', { method: 'POST', body: formData });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || 'Download failed');
        }

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `mapped_test_cases_${Date.now()}.xlsx`;
        a.click();
        setTimeout(() => URL.revokeObjectURL(url), 100);

    } catch (err) {
        alert(`Download failed: ${err.message}`);
    } finally {
        const btn = document.getElementById('downloadMappedExcelBtn');
        btn.innerHTML = '<i class="fas fa-file-excel" style="color:#1d6f42"></i> Download Mapped Excel';
        btn.disabled = false;
    }
});

// ============================================================
// Download / copy buttons
// ============================================================
document.getElementById('downloadMdBtn').addEventListener('click', () => {
    if (!window.currentTestScenarios) return;
    downloadBlob(window.currentTestScenarios, 'text/markdown', `test-scenarios-${Date.now()}.md`);
});

document.getElementById('downloadScenariosCsvBtn').addEventListener('click', () => {
    if (!window.currentTestCases || !window.currentTestCases.length) return;
    downloadBlob(buildTestCasesCsv(window.currentTestCases), 'text/csv', `test-scenarios-${Date.now()}.csv`);
});

document.getElementById('downloadCasesBtn').addEventListener('click', () => {
    if (!window.currentTestCases || !window.currentTestCases.length) return;
    downloadBlob(buildTestCasesCsv(window.currentTestCases), 'text/csv', `test-cases-${Date.now()}.csv`);
});

document.getElementById('copyBtn').addEventListener('click', async () => {
    if (!window.currentTestScenarios) return;
    await copyToClipboard(window.currentTestScenarios, document.getElementById('copyBtn'));
});

document.getElementById('downloadCodeBtn').addEventListener('click', () => {
    if (!window.currentTestCode) return;
    downloadBlob(window.currentTestCode, 'text/plain', `test_code_${Date.now()}.py`);
});

document.getElementById('copyCodeBtn').addEventListener('click', async () => {
    if (!window.currentTestCode) return;
    await copyToClipboard(window.currentTestCode, document.getElementById('copyCodeBtn'));
});

// ============================================================
// Analyze Another PR / Try Again
// ============================================================
document.getElementById('analyzeAnotherBtn').addEventListener('click', () => {
    resultsSection.classList.add('hidden');
    inputSection.classList.remove('hidden');
    document.getElementById('prUrl').value = '';
    document.getElementById('diffText').value = '';
    document.getElementById('generateCode').checked = false;
    clearExcelFile();
    currentMappingResult = null;
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

document.getElementById('tryAgainBtn').addEventListener('click', () => {
    errorSection.classList.add('hidden');
    inputSection.classList.remove('hidden');
});

// ============================================================
// Error display
// ============================================================
function showError(message) {
    inputSection.classList.add('hidden');
    loadingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.remove('hidden');
    document.getElementById('errorMessage').textContent = message;
}

// ============================================================
// Utilities
// ============================================================
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

function downloadBlob(content, mimeType, filename) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 100);
}

async function copyToClipboard(text, btn) {
    try {
        await navigator.clipboard.writeText(text);
        const orig = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.style.cssText = 'background:var(--success-color);color:white';
        setTimeout(() => { btn.innerHTML = orig; btn.style.cssText = ''; }, 2000);
    } catch (_) {
        alert('Failed to copy to clipboard');
    }
}

function buildTestCasesCsv(cases) {
    const headers = ['ID', 'Title', 'Type', 'Priority', 'Category', 'Steps', 'Expected Result'];
    const rows = cases.map(tc => [
        tc.id || '', tc.title || '', tc.type || '', tc.priority || '', tc.category || '',
        Array.isArray(tc.steps) ? tc.steps.join(' | ') : '',
        tc.expected_result || ''
    ].map(cell => `"${String(cell).replace(/"/g, '""')}"`));
    return [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
}
