// ===== USER DASHBOARD =====

document.addEventListener('DOMContentLoaded', () => {
    if (!checkAuth('user')) return;

    loadUserProfile();
    loadUserStats();
    loadNotice();
});

// ===== LOAD PROFILE =====
async function loadUserProfile() {
    try {
        const response = await fetch(`${API_URL}/api/profile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success) {
            document.getElementById('profileName').textContent = data.nickname || data.username;
            document.getElementById('profileUsername').value = data.username;
            document.getElementById('profileCredits').value = data.credits;
            document.getElementById('nickname').value = data.nickname || '';

            updateCreditBar(data.credits, data.max_credits);

            if (data.avatar) {
                document.getElementById('profileAvatarImg').src = data.avatar;
                document.getElementById('profileAvatarImg').style.display = 'block';
                document.getElementById('profileAvatarIcon').style.display = 'none';

                document.getElementById('avatarImg').src = data.avatar;
                document.getElementById('avatarImg').style.display = 'block';
                document.getElementById('avatarIcon').style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Profile load error:', error);
    }
}

// ===== LOAD STATS =====
async function loadUserStats() {
    try {
        const response = await fetch(`${API_URL}/api/user-stats`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success) {
            document.getElementById('totalAnalysis').textContent = data.total || 0;
            document.getElementById('todayAnalysis').textContent = data.today || 0;
            document.getElementById('monthAnalysis').textContent = data.month || 0;
            document.getElementById('avoidCount').textContent = data.avoid || 0;
            document.getElementById('upCount').textContent = data.up || 0;
            document.getElementById('downCount').textContent = data.down || 0;

            // Load history
            loadAnalysisHistory(data.history || []);
        }
    } catch (error) {
        console.error('Stats load error:', error);
    }
}

// ===== LOAD HISTORY =====
function loadAnalysisHistory(history) {
    const tbody = document.getElementById('analysisHistory');
    tbody.innerHTML = '';

    if (history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: var(--text-muted);">No analysis yet</td></tr>';
        return;
    }

    history.forEach((item, index) => {
        const tr = document.createElement('tr');
        const signalColor = item.signal.includes('BUY') ? '#00d084' :
                           item.signal.includes('SELL') ? '#ff4757' : '#ffb800';

        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>${item.date}</td>
            <td style="color: ${signalColor}; font-weight: 600;">${item.signal}</td>
            <td>${item.confidence}%</td>
            <td>${item.risk}</td>
        `;
        tbody.appendChild(tr);
    });
}

// ===== LOAD NOTICE =====
async function loadNotice() {
    try {
        const response = await fetch(`${API_URL}/api/get-notice`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success && data.notice) {
            document.getElementById('noticeBanner').style.display = 'flex';
            document.getElementById('noticeText').textContent = data.notice;
        }
    } catch (error) {
        console.error('Notice load error:', error);
    }
}

// ===== LOAD SUPPORT LINKS =====
async function loadSupportLinks() {
    try {
        const response = await fetch(`${API_URL}/api/support-links`);
        const data = await response.json();

        if (data.success) {
            document.getElementById('ownerSupport').href = data.owner || '#';
            document.getElementById('altOwnerSupport').href = data.alt_owner || '#';
            document.getElementById('adminSupport').href = data.admin || '#';
        }
    } catch (error) {
        console.error('Support links error:', error);
    }
}