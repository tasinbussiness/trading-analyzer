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
            const nameEl = document.getElementById('profileName');
            const usernameEl = document.getElementById('profileUsername');
            const creditsEl = document.getElementById('profileCredits');
            const nicknameEl = document.getElementById('nickname');
            
            if (nameEl) nameEl.textContent = data.nickname || data.username;
            if (usernameEl) usernameEl.value = data.username;
            if (creditsEl) creditsEl.value = data.credits;
            if (nicknameEl) nicknameEl.value = data.nickname || '';

            updateCreditBar(data.credits, data.max_credits);

            if (data.avatar) {
                const profileImg = document.getElementById('profileAvatarImg');
                const profileIcon = document.getElementById('profileAvatarIcon');
                const topImg = document.getElementById('avatarImg');
                const topIcon = document.getElementById('avatarIcon');
                
                if (profileImg) {
                    profileImg.src = data.avatar;
                    profileImg.style.display = 'block';
                }
                if (profileIcon) profileIcon.style.display = 'none';
                if (topImg) {
                    topImg.src = data.avatar;
                    topImg.style.display = 'block';
                }
                if (topIcon) topIcon.style.display = 'none';
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
            const els = {
                totalAnalysis: data.total || 0,
                todayAnalysis: data.today || 0,
                monthAnalysis: data.month || 0,
                avoidCount: data.avoid || 0,
                upCount: data.up || 0,
                downCount: data.down || 0
            };
            
            for (const [id, val] of Object.entries(els)) {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            }

            loadAnalysisHistory(data.history || []);
        }
    } catch (error) {
        console.error('Stats load error:', error);
    }
}

function loadAnalysisHistory(history) {
    const tbody = document.getElementById('analysisHistory');
    if (!tbody) return;
    
    tbody.innerHTML = '';

    if (history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: rgba(200,220,255,0.5);">No analysis yet</td></tr>';
        return;
    }

    history.forEach((item, index) => {
        const tr = document.createElement('tr');
        const signalColor = item.signal.includes('BUY') ? '#00ff88' :
                           item.signal.includes('SELL') ? '#ff3b5c' : '#ffb800';

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

async function loadNotice() {
    try {
        const response = await fetch(`${API_URL}/api/get-notice`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success && data.notice) {
            const banner = document.getElementById('noticeBanner');
            const text = document.getElementById('noticeText');
            if (banner) banner.style.display = 'flex';
            if (text) text.textContent = data.notice;
        }
    } catch (error) {
        console.error('Notice load error:', error);
    }
}
