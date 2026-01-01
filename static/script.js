// Theme Management
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    const btn = document.getElementById('themeToggle');
    btn.textContent = newTheme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
}

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const btn = document.getElementById('themeToggle');
    if (btn) {
        btn.textContent = savedTheme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
    }

    // Form handling
    const form = document.getElementById('atsForm');
    const fileInput = document.getElementById('resume');
    const submitBtn = form.querySelector('.btn-primary');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');

    // File input validation and feedback
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file type
            const validTypes = ['.txt', '.pdf', '.docx'];
            const fileExt = '.' + file.name.split('.').pop().toLowerCase();
            
            if (!validTypes.includes(fileExt)) {
                alert('Please upload a TXT, PDF, or DOCX file');
                e.target.value = '';
                return;
            }
            
            // Validate file size (5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('File size should be less than 5MB');
                e.target.value = '';
                return;
            }
            
            // Visual feedback
            e.target.style.borderColor = '#00b894';
            e.target.style.background = 'rgba(0, 184, 148, 0.1)';
        }
    });

    // Form submission
    form.addEventListener('submit', function(e) {
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';
        submitBtn.style.cursor = 'not-allowed';
    });

    // Smooth scroll to results
    const resultsCard = document.querySelector('.results-container');
    if (resultsCard) {
        setTimeout(() => {
            resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
    }

    // Textarea auto-resize
    const textarea = document.getElementById('job_desc');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }

    // Render section chart if data exists
    if (window.sectionScoresData) {
        const ctx = document.getElementById('sectionChart');
        if (ctx) {
            new Chart(ctx.getContext('2d'), {
                type: 'radar',
                data: {
                    labels: window.sectionScoresData.labels,
                    datasets: [{
                        label: 'Section Match Score',
                        data: window.sectionScoresData.values,
                        backgroundColor: 'rgba(102, 126, 234, 0.2)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(102, 126, 234, 1)'
                    }]
                },
                options: {
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                stepSize: 20
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
    }
});

// Export Results Function
function exportResults() {
    const resultsData = {
        timestamp: new Date().toISOString(),
        similarity: document.querySelector('.score-number')?.textContent || 'N/A',
        sections: [],
        keywords: {
            matching: [],
            missing: []
        }
    };

    // Collect section scores
    document.querySelectorAll('.section-item').forEach(item => {
        const name = item.querySelector('.section-name')?.textContent;
        const score = item.querySelector('.section-score')?.textContent;
        if (name && score) {
            resultsData.sections.push({ name, score });
        }
    });

    // Collect keywords
    document.querySelectorAll('.keyword-tag.match').forEach(tag => {
        resultsData.keywords.matching.push(tag.textContent);
    });
    
    document.querySelectorAll('.keyword-tag.missing').forEach(tag => {
        resultsData.keywords.missing.push(tag.textContent);
    });

    // Create and download JSON file
    const dataStr = JSON.stringify(resultsData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `resume-analysis-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    alert('✓ Results exported successfully!');
}

// Clear History Function
async function clearHistory() {
    if (!confirm('Are you sure you want to clear all analysis history?')) {
        return;
    }
    
    try {
        const response = await fetch('/clear-history', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            alert('✓ History cleared successfully!');
            location.reload();
        } else {
            alert('❌ Error clearing history: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        alert('❌ Error clearing history: ' + error.message);
    }
}

// Print optimization
window.addEventListener('beforeprint', function() {
    document.body.classList.add('printing');
});

window.addEventListener('afterprint', function() {
    document.body.classList.remove('printing');
});