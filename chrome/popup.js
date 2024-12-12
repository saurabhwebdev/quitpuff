async function fetchStats() {
    try {
        console.log("Fetching stats...");
        const response = await fetch('https://quitpuff.onrender.com/api/stats', {
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        });
        
        console.log("Response status:", response.status);
        
        if (!response.ok) {
            if (response.status === 401) {
                console.log("User not authenticated");
                showLoginPrompt();
                return;
            } else {
                throw new Error('Failed to fetch stats');
            }
        }
        
        const stats = await response.json();
        console.log("Parsed stats:", stats);
        updateUI(stats);
    } catch (error) {
        console.error('Error fetching stats:', error);
        showLoginPrompt();
    }
}

function updateUI(stats) {
    // Update Longest Break
    const longestBreakValue = document.querySelector('#longestBreak .stat-value');
    longestBreakValue.textContent = formatDuration(stats.max_time_between);

    // Update Average Time
    const averageTimeValue = document.querySelector('#averageTime .stat-value');
    averageTimeValue.textContent = formatDuration(stats.avg_time_between);

    // Update Total Cigarettes
    const totalCigsValue = document.querySelector('#totalCigs .stat-value');
    totalCigsValue.textContent = stats.total_cigarettes;

    // Update Money Saved
    const moneySavedValue = document.querySelector('#moneySaved .stat-value');
    moneySavedValue.textContent = formatMoney(stats.total_money_saved, stats.currency);
}

function formatDuration(hours) {
    if (hours >= 24) {
        return `${(hours / 24).toFixed(1)} days`;
    }
    return `${hours.toFixed(1)} hours`;
}

function formatMoney(amount, currency) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency || 'USD'
    }).format(amount);
}

function showError(message = "Not available") {
    const containers = document.querySelectorAll('.stat-value');
    containers.forEach(container => {
        container.textContent = message;
        container.style.color = '#ef4444';
    });
}

function showLoginPrompt() {
    const container = document.querySelector('.stats-container');
    container.innerHTML = `
        <div class="login-prompt">
            <p class="text-gray-600 text-center mb-4">Please log in to view your stats</p>
            <p class="text-sm text-gray-500 mb-4">After logging in, click the refresh button below</p>
            <a href="https://quitpuff.onrender.com/login" 
               target="_blank" 
               class="view-more"
               onclick="window.open('https://quitpuff.onrender.com/login', '_blank').focus();">
                Login to QuitPuff
            </a>
            <button onclick="fetchStats()" 
                    class="mt-4 px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg text-sm">
                Refresh Stats
            </button>
        </div>
    `;
}

// Fetch stats when popup opens
document.addEventListener('DOMContentLoaded', fetchStats); 