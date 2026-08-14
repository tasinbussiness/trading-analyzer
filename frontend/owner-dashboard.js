// ===== OWNER DASHBOARD =====

let selectedLicenseType = 'user';
let selectedUserId = null;
let selectedUserType = null;

document.addEventListener('DOMContentLoaded', () => {
    if (!checkAuth('owner')) return;

    loadOwnerProfile();
    loadAdmins();
    loadAllUsers();
    loadAllStats();
    loadAllLicenses();
    loadNoticeHistory();
    loadStrategySettings();
});

async function loadOwnerProfile() {
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
            const nicknameEl = document.getElementById('nickname');
            
            if (nameEl) nameEl.textContent = data.nickname || data.username;
            if (usernameEl) usernameEl.value = data.username;
            if (nicknameEl) nicknameEl.value = data.nickname || '';

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
        console.error('Profile error:', error);
    }
}

async function loadAdmins() {
    try {
        const response = await fetch(`${API_URL}/api/owner/admins`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success) renderAdmins(data.admins);
    } catch (error) {
        console.error('Admins error:', error);
    }
}

function renderAdmins(admins) {
    const grid = document.getElementById('adminsGrid');
    if (!grid) return;
    
    grid.innerHTML = '';

    if (!admins || admins.length === 0) {
        grid.innerHTML = '<p style="color: rgba(200,220,255,0.5); text-align: center; grid-column: 1/-1;">No admins found</p>';
        return;
    }

    admins.forEach(admin => {
        const card = document.createElement('div');
        card.className = 'user-card';
        card.onclick = () => showUserActionModal(admin, 'admin');

        card.innerHTML = `
            <div class="user-card-avatar">
                ${admin.avatar ? `<img src="${admin.avatar}" alt="">` : '<i class="fas fa-user-shield"></i>'}
            </div>
            <div class="user-card-info">
                <h4>${admin.nickname || admin.username}</h4>
                <p>🔧 Admin • ${admin.status || 'active'}</p>
            </div>
            <div class="user-card-status ${admin.status === 'paused' ? 'paused' : ''}"></div>
        `;
        grid.appendChild(card);
    });
}

function searchAdmins(query) {
    const cards = document.getElementById('adminsGrid')?.querySelectorAll('.user-card') || [];
    cards.forEach(card => {
        const name = card.querySelector('h4').textContent.toLowerCase();
        card.style.display = name.includes(query.toLowerCase()) ? 'flex' : 'none';
    });
}

async function showAddAdmin() {
    try {
        const response = await fetch(`${API_URL}/api/owner/generate-admin-license`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success) {
            document.getElementById('adminLicenseKey').textContent = data.license_key;
            document.getElementById('addAdminModal').style.display = 'flex';
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

function closeAddAdmin() {
    document.getElementById('addAdminModal').style.display = 'none';
}

function copyAdminLicense() {
    const key = document.getElementById('adminLicenseKey').textContent;
    navigator.clipboard.writeText(key).then(() => {
        showToast('Admin license copied!', 'success');
    });
}

async function loadAllUsers() {
    try {
        const response = await fetch(`${API_URL}/api/owner/all-users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success) renderAllUsers(data.users);
    } catch (error) {
        console.error('Users error:', error);
    }
}

function renderAllUsers(users) {
    const grid = document.getElementById('usersGrid');
    if (!grid) return;
    
    grid.innerHTML = '';

    if (!users || users.length === 0) {
        grid.innerHTML = '<p style="color: rgba(200,220,255,0.5); text-align: center; grid-column: 1/-1;">No users found</p>';
        return;
    }

    users.forEach(user => {
        const card = document.createElement('div');
        card.className = 'user-card';
        card.onclick = () => showUserActionModal(user, 'user');

        const statusClass = user.status === 'paused' ? 'paused' : user.status === 'banned' ? 'banned' : '';

        card.innerHTML = `
            <div class="user-card-avatar">
                ${user.avatar ? `<img src="${user.avatar}" alt="">` : '<i class="fas fa-user"></i>'}
            </div>
            <div class="user-card-info">
                <h4>${user.nickname || user.username}</h4>
                <p>Credits: ${user.credits} • ${user.status || 'active'}</p>
            </div>
            <div class="user-card-status ${statusClass}"></div>
        `;
        grid.appendChild(card);
    });
}

function searchUsers(query) {
    const cards = document.getElementById('usersGrid')?.querySelectorAll('.user-card') || [];
    cards.forEach(card => {
        const name = card.querySelector('h4').textContent.toLowerCase();
        card.style.display = name.includes(query.toLowerCase()) ? 'flex' : 'none';
    });
}

function showUserActionModal(user, type) {
    selectedUserId = user.id;
    selectedUserType = type;
    
    document.getElementById('userActionInfo').innerHTML = `
        <div class="user-card-avatar" style="width:60px;height:60px;margin:0 auto 10px;border-radius:15px;background:linear-gradient(135deg,#0077ff,#00b4ff);display:flex;align-items:center;justify-content:center;font-size:24px;color:white;overflow:hidden;">
            ${user.avatar ? `<img src="${user.avatar}" style="width:100%;height:100%;object-fit:cover;">` : `<i class="fas fa-${type === 'admin' ? 'user-shield' : 'user'}"></i>`}
        </div>
        <h3 style="color:white;margin-bottom:5px;">${user.nickname || user.username}</h3>
        <p style="color:rgba(200,220,255,0.6);font-size:13px;">Credits: ${user.credits || 0} • Status: ${user.status || 'active'}</p>
    `;
    document.getElementById('modalCredits').value = user.credits || 0;
    document.getElementById('creditModify').style.display = 'none';
    document.getElementById('userActionModal').style.display = 'flex';
}

function closeUserAction() {
    document.getElementById('userActionModal').style.display = 'none';
    selectedUserId = null;
}

async function pauseUser() { await userAction('pause'); }
async function resumeUser() { await userAction('resume'); }

async function deleteUser() {
    if (!confirm('Are you sure you want to delete this user?')) return;
    await userAction('delete');
}

function modifyCredits() {
    document.getElementById('creditModify').style.display = 'block';
}

async function saveModalCredits() {
    const credits = document.getElementById('modalCredits').value;
    try {
        const response = await fetch(`${API_URL}/api/owner/set-credits`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: localStorage.getItem('token'),
                user_id: selectedUserId,
                credits: parseInt(credits)
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast('Credits updated!', 'success');
            closeUserAction();
            loadAllUsers();
            loadAdmins();
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

async function userAction(action) {
    try {
        const response = await fetch(`${API_URL}/api/owner/user-action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: localStorage.getItem('token'),
                user_id: selectedUserId,
                action: action
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast(`User ${action}d successfully!`, 'success');
            closeUserAction();
            loadAllUsers();
            loadAdmins();
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

async function loadAllStats() {
    try {
        const response = await fetch(`${API_URL}/api/owner/stats`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success) {
            const els = {
                totalAnalysis: data.total || 0,
                todayAnalysis: data.today || 0,
                weekAnalysis: data.week || 0,
                monthAnalysis: data.month || 0,
                upCount: data.up || 0,
                downCount: data.down || 0,
                avoidCount: data.avoid || 0,
                totalUsers: data.total_users || 0
            };
            
            for (const [id, val] of Object.entries(els)) {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            }
        }
    } catch (error) {
        console.error('Stats error:', error);
    }
}

function selectLicenseType(type, element) {
    selectedLicenseType = type;
    document.querySelectorAll('.license-type-btn').forEach(b => b.classList.remove('active'));
    if (element) element.classList.add('active');
}

async function generateLicense() {
    const credits = document.getElementById('licenseCredits')?.value || 50;

    try {
        const response = await fetch(`${API_URL}/api/owner/generate-license`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: localStorage.getItem('token'),
                type: selectedLicenseType,
                credits: parseInt(credits)
            })
        });

        const data = await response.json();
        if (data.success) {
            document.getElementById('generatedLicense').style.display = 'block';
            document.getElementById('licenseKeyOutput').textContent = data.license_key;
            showToast('License generated!', 'success');
            loadAllLicenses();
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

function copyLicense() {
    const key = document.getElementById('licenseKeyOutput').textContent;
    navigator.clipboard.writeText(key).then(() => {
        showToast('License copied!', 'success');
    });
}

async function loadAllLicenses() {
    try {
        const response = await fetch(`${API_URL}/api/owner/licenses`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success) {
            const tbody = document.getElementById('licenseList');
            if (!tbody) return;
            
            tbody.innerHTML = '';
            
            if (data.licenses.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color: rgba(200,220,255,0.5);">No licenses yet</td></tr>';
                return;
            }

            data.licenses.forEach(license => {
                const statusColor = license.status === 'used' ? '#00ff88' :
                                   license.status === 'unused' ? '#ffb800' : '#ff3b5c';
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><code style="color: #00b4ff;">${license.key}</code></td>
                    <td>${license.type}</td>
                    <td style="color: ${statusColor};">${license.status}</td>
                    <td>${license.credits}</td>
                    <td>${license.used_by || '-'}</td>
                    <td>
                        <button onclick="deleteLicense('${license.key}')" style="background:rgba(255,59,92,0.15);border:none;color:#ff3b5c;padding:6px 12px;border-radius:8px;cursor:pointer;">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (error) {
        console.error('Licenses error:', error);
    }
}

async function deleteLicense(key) {
    if (!confirm('Delete this license?')) return;

    try {
        const response = await fetch(`${API_URL}/api/owner/delete-license`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: localStorage.getItem('token'),
                license_key: key
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast('License deleted!', 'success');
            loadAllLicenses();
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

async function sendNotice() {
    const title = document.getElementById('noticeTitle')?.value.trim();
    const message = document.getElementById('noticeMessage')?.value.trim();

    if (!title || !message) {
        showToast('Please fill in title and message!', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/owner/send-notice`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: localStorage.getItem('token'),
                title: title,
                message: message,
                all: document.getElementById('noticeAll')?.checked || false,
                admins_only: document.getElementById('noticeAdmins')?.checked || false
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast('Notice sent!', 'success');
            document.getElementById('noticeTitle').value = '';
            document.getElementById('noticeMessage').value = '';
            loadNoticeHistory();
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

async function loadNoticeHistory() {
    try {
        const response = await fetch(`${API_URL}/api/owner/notices`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success) {
            const container = document.getElementById('noticeHistory');
            if (!container) return;
            
            container.innerHTML = '';

            if (!data.notices || data.notices.length === 0) {
                container.innerHTML = '<p style="color:rgba(200,220,255,0.5);text-align:center;">No notices sent yet</p>';
                return;
            }

            data.notices.forEach(notice => {
                const item = document.createElement('div');
                item.className = 'notice-item';
                item.innerHTML = `
                    <h4>${notice.title}</h4>
                    <p>${notice.message}</p>
                    <div class="notice-date">${notice.date}</div>
                `;
                container.appendChild(item);
            });
        }
    } catch (error) {
        console.error('Notices error:', error);
    }
}

async function loadStrategySettings() {
    try {
        const response = await fetch(`${API_URL}/api/owner/strategies`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success && data.strategies) {
            Object.keys(data.strategies).forEach(key => {
                const toggle = document.querySelector(`[data-strategy="${key}"]`);
                if (toggle) toggle.checked = data.strategies[key];
            });
        }
    } catch (error) {
        console.error('Strategies error:', error);
    }
}

async function saveStrategies() {
    const strategies = {};
    document.querySelectorAll('[data-strategy]').forEach(toggle => {
        strategies[toggle.dataset.strategy] = toggle.checked;
    });

    try {
        const response = await fetch(`${API_URL}/api/owner/save-strategies`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: localStorage.getItem('token'),
                strategies: strategies
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast('Strategy settings saved!', 'success');
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

async function changeOwnerPassword() {
    const currentPass = document.getElementById('currentPass')?.value;
    const newPass = document.getElementById('changeNewPass')?.value;
    const confirmPass = document.getElementById('changeConfirmPass')?.value;

    if (!currentPass || !newPass || !confirmPass) {
        showToast('Please fill in all fields!', 'error');
        return;
    }

    if (newPass !== confirmPass) {
        showToast('Passwords do not match!', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/owner/change-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: localStorage.getItem('token'),
                current_password: currentPass,
                new_password: newPass
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast('Password updated!', 'success');
            document.getElementById('currentPass').value = '';
            document.getElementById('changeNewPass').value = '';
            document.getElementById('changeConfirmPass').value = '';
        } else {
            showToast(data.message || 'Failed!', 'error');
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}
