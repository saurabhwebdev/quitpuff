// Fetch stats every 5 minutes
chrome.alarms.create('fetchStats', { periodInMinutes: 5 });

// Listen for cookie changes
chrome.cookies.onChanged.addListener((changeInfo) => {
    if (changeInfo.cookie.domain === 'quitpuff.onrender.com') {
        fetchAndCacheStats();
    }
});

chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'fetchStats') {
        fetchAndCacheStats();
    }
});

async function fetchAndCacheStats() {
    try {
        const response = await fetch('https://quitpuff.onrender.com/api/stats', {
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Origin': chrome.runtime.getURL('')
            }
        });
        
        if (!response.ok) throw new Error('Failed to fetch stats');
        
        const stats = await response.json();
        chrome.storage.local.set({ stats });
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
} 