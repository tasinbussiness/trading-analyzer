// ===== ADMIN DASHBOARD =====

let selectedLicenseType = 'user';

document.addEventListener('DOMContentLoaded', () => {
    if (!checkAuth('admin')) return;

    loadAdminProfile();
    loadUsers();
    loadLicenses();
    loadCreditUsers();
});

async function loadAdminProfile() {
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
        console.error('Profile load error:', error);
    }
}

async function loadUsers() {
    try {
        const response = await fetch(`${API_URL}/api/admin/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success) {
            renderUsers(data.users);
        }
    } catch (error) {
        console.error('Users load error:', error);
    }
}

function renderUsers(users) {
    const grid = document.getElementById('usersGrid');
    if (!grid) return;
    
    grid.innerHTML = '';

    if (users.length === 0) {
        grid.innerHTML = '<p style="color: rgba(200,220,255,0.5); text-align: center; grid-column: 1/-1;">No users found</p>';
        return;
    }

    users.forEach(user => {
        const card = document.createElement('div');
        card.className = 'user-card';
        
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

function searchUsers() {
    const query = document.getElementById('userSearch')?.value.toLowerCase() || '';
    const cards = document.querySelectorAll('#usersGrid .user-card');

    cards.forEach(card => {
        const name = card.querySelector('h4').textContent.toLowerCase();
        card.style.display = name.includes(query) ? 'flex' : 'none';
    });
}

function selectLicenseType(type, element) {
    selectedLicenseType = type;
    document.querySelectorAll('.license-type-btn').forEach(b => b.classList.remove('active'));
    if (element) element.classList.add('active');
}

async function generateLicense() {
    const credits = document.getElementById('licenseCredits')?.value || 50;

    try {
        const response = await fetch(`${API_URL}/api/admin/generate-license`, {
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
            loadLicenses();
        } else {
            showToast(data.message || 'Failed!', 'error');
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

async function loadLicenses() {
    try {
        const response = await fetch(`${API_URL}/api/admin/licenses`, {
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
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: rgba(200,220,255,0.5);">No licenses yet</td></tr>';
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
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (error) {
        console.error('Licenses error:', error);
    }
}

async function loadCreditUsers() {
    try {
        const response = await fetch(`${API_URL}/api/admin/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: localStorage.getItem('token') })
        });

        const data = await response.json();
        if (data.success) {
            const select = document.getElementById('creditUserSelect');
            if (!select) return;
            
            select.innerHTML = '<option value="">Select a user</option>';

            data.users.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = `${user.username} (Credits: ${user.credits})`;
                option.dataset.credits = user.credits;
                select.appendChild(option);
            });

            select.onchange = () => {
                const selected = select.options[select.selectedIndex];
                const currentEl = document.getElementById('currentCredits');
                if (currentEl) currentEl.value = selected.dataset.credits || 0;
            };
        }
    } catch (error) {
        console.error('Credit users error:', error);
    }
}

async function addCredits() {
    const userId = document.getElementById('creditUserSelect')?.value;
    const amount = document.getElementById('addCreditsAmount')?.value;

    if (!userId || !amount) {
        showToast('Select user and enter amount!', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/admin/add-credits`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: localStorage.getItem('token'),
                user_id: userId,
                amount: parseInt(amount)
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast('Credits added!', 'success');
            document.getElementById('addCreditsAmount').value = '';
            loadCreditUsers();
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

async function setCredits() {
    const userId = document.getElementById('creditUserSelect')?.value;
    const amount = document.getElementById('setCreditsAmount')?.value;

    if (!userId || amount === '') {
        showToast('Select user and enter amount!', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/admin/set-credits`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: localStorage.getItem('token'),
                user_id: userId,
                credits: parseInt(amount)
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast('Credits updated!', 'success');
            document.getElementById('setCreditsAmount').value = '';
            loadCreditUsers();
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}
