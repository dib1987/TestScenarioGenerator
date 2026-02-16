// DOM Elements
const prForm = document.getElementById('prForm');
const inputSection = document.getElementById('inputSection');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

// Tab switching
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;

        // Update tab buttons
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update tab content
        tabContents.forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabId).classList.add('active');
    });
});

// Form submission
prForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
    const generateCode = document.getElementById('generateCode').checked;

    if (activeTab === 'pr-url') {
        const prUrl = document.getElementById('prUrl').value.trim();
        if (!prUrl) {
            showError('Please enter a GitHub PR URL');
            return;
        }
        await analyzePR(prUrl, generateCode);
    } else {
        const diffText = document.getElementById('diffText').value.trim();
        if (!diffText) {
            showError('Please enter git diff content');
            return;
        }
        await analyzeDiff(diffText, generateCode);
    }
});

// Analyze PR
async function analyzePR(prUrl, generateCode) {
    showLoading();

    try {
        updateLoadingStep(1, 'Fetching PR data from GitHub...');

        const response = await fetch('/api/analyze-pr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pr_url: prUrl,
                generate_code: generateCode
            })
        });

        const result = await response.json();

        if (!result.success) {
            showError(result.error || 'An error occurred');
            return;
        }

        updateLoadingStep(2, 'Analyzing code changes...');
        await sleep(500);

        updateLoadingStep(3, 'Generating test scenarios with AI...');
        await sleep(500);

        showResults(result.data);

    } catch (error) {
        console.error('Error:', error);
        showError(`Network error: ${error.message}`);
    }
}

// Analyze manual diff
async function analyzeDiff(diffText, generateCode) {
    showLoading();

    try {
        updateLoadingStep(2, 'Analyzing code changes...');

        const response = await fetch('/api/analyze-diff', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                diff_text: diffText,
                generate_code: generateCode
            })
        });

        const result = await response.json();

        if (!result.success) {
            showError(result.error || 'An error occurred');
            return;
        }

        updateLoadingStep(3, 'Generating test scenarios with AI...');
        await sleep(500);

        showResults(result.data, false);

    } catch (error) {
        console.error('Error:', error);
        showError(`Network error: ${error.message}`);
    }
}

// Show loading state
function showLoading() {
    inputSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');

    // Reset progress steps
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
}

// Update loading step
function updateLoadingStep(stepNum, text) {
    document.getElementById('loadingText').textContent = text;
    document.getElementById(`step${stepNum}`).classList.add('active');
}

// Show results
function showResults(data, isPR = true) {
    inputSection.classList.add('hidden');
    loadingSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // Show/hide PR info card
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

    // Populate summary
    document.getElementById('totalFiles').textContent = data.summary.total_files;
    document.getElementById('totalAdditions').textContent = data.summary.total_additions;
    document.getElementById('totalDeletions').textContent = data.summary.total_deletions;

    // Populate file changes
    const fileChangesContainer = document.getElementById('fileChanges');
    fileChangesContainer.innerHTML = '';

    if (data.file_analyses && data.file_analyses.length > 0) {
        const heading = document.createElement('h3');
        heading.textContent = 'Modified Files';
        heading.style.marginBottom = '1rem';
        heading.style.fontSize = '1.125rem';
        fileChangesContainer.appendChild(heading);

        data.file_analyses.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <span class="file-path">${escapeHtml(file.file_path)}</span>
                <div class="file-stats">
                    <span class="additions">+${file.additions}</span>
                    <span class="deletions">-${file.deletions}</span>
                </div>
            `;
            fileChangesContainer.appendChild(fileItem);
        });
    }

    // Populate test scenarios
    const testScenariosContainer = document.getElementById('testScenarios');
    testScenariosContainer.innerHTML = data.test_scenarios_html || data.test_scenarios;

    // Store raw markdown for download
    window.currentTestScenarios = data.test_scenarios;

    // Show test code if available
    const testCodeCard = document.getElementById('testCodeCard');
    if (data.test_code) {
        testCodeCard.classList.remove('hidden');
        document.getElementById('testCode').textContent = data.test_code;
        window.currentTestCode = data.test_code;
    } else {
        testCodeCard.classList.add('hidden');
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Show error
function showError(message) {
    inputSection.classList.add('hidden');
    loadingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.remove('hidden');

    document.getElementById('errorMessage').textContent = message;
}

// Utility functions
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Download markdown
document.getElementById('downloadMdBtn').addEventListener('click', () => {
    if (!window.currentTestScenarios) return;

    const blob = new Blob([window.currentTestScenarios], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `test-scenarios-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
});

// Copy markdown
document.getElementById('copyBtn').addEventListener('click', async () => {
    if (!window.currentTestScenarios) return;

    try {
        await navigator.clipboard.writeText(window.currentTestScenarios);

        // Show feedback
        const btn = document.getElementById('copyBtn');
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.style.background = 'var(--success-color)';
        btn.style.color = 'white';

        setTimeout(() => {
            btn.innerHTML = originalHtml;
            btn.style.background = '';
            btn.style.color = '';
        }, 2000);
    } catch (error) {
        alert('Failed to copy to clipboard');
    }
});

// Download test code
document.getElementById('downloadCodeBtn').addEventListener('click', () => {
    if (!window.currentTestCode) return;

    const blob = new Blob([window.currentTestCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `test_code_${Date.now()}.py`;
    a.click();
    URL.revokeObjectURL(url);
});

// Copy test code
document.getElementById('copyCodeBtn').addEventListener('click', async () => {
    if (!window.currentTestCode) return;

    try {
        await navigator.clipboard.writeText(window.currentTestCode);

        const btn = document.getElementById('copyCodeBtn');
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.style.background = 'var(--success-color)';
        btn.style.color = 'white';

        setTimeout(() => {
            btn.innerHTML = originalHtml;
            btn.style.background = '';
            btn.style.color = '';
        }, 2000);
    } catch (error) {
        alert('Failed to copy to clipboard');
    }
});

// Analyze another PR
document.getElementById('analyzeAnotherBtn').addEventListener('click', () => {
    resultsSection.classList.add('hidden');
    inputSection.classList.remove('hidden');

    // Reset form
    document.getElementById('prUrl').value = '';
    document.getElementById('diffText').value = '';
    document.getElementById('generateCode').checked = false;

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Try again button
document.getElementById('tryAgainBtn').addEventListener('click', () => {
    errorSection.classList.add('hidden');
    inputSection.classList.remove('hidden');
});
