// ===== ADMIN DASHBOARD =====

let selectedLicenseType = 'user';

document.addEventListener('DOMContentLoaded', () => {
    if (!checkAuth('admin')) return;

    loadAdminProfile();
    loadUsers();
    loadLicenses();
    loadCreditUsers();
});

// ===== LOAD ADMIN PROFILE =====
async function loadAdminProfile() {
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
            document.getElementById('nickname').value = data.nickname || '';

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

// ===== LOAD USERS =====
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
    grid.innerHTML = '';

    if (users.length === 0) {
        grid.innerHTML = '<p style="color: var(--text-muted); text-align: center;">No users found</p>';
        return;
    }

    users.forEach(user => {
        const card = document.createElement('div');
        card.className = 'user-card';
        card.onclick = () => showUserInfo(user);

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
    const query = document.getElementById('userSearch').value.toLowerCase();
    const cards = document.querySelectorAll('.user-card');

    cards.forEach(card => {
        const name = card.querySelector('h4').textContent.toLowerCase();
        card.style.display = name.includes(query) ? 'flex' : 'none';
    });
}

// ===== LICENSE GENERATOR =====
function selectLicenseType(type, element) {
    selectedLicenseType = type;
    document.querySelectorAll('.license-type-btn').forEach(b => b.classList.remove('active'));
    element.classList.add('active');
}

async function generateLicense() {
    const credits = document.getElementById('licenseCredits').value;

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
    navigator.clipboard.writeText(key);
    showToast('License copied!', 'success');
}

// ===== LOAD LICENSES =====
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
            tbody.innerHTML = '';

            data.licenses.forEach(license => {
                const statusColor = license.status === 'used' ? '#00d084' :
                                   license.status === 'unused' ? '#ffb800' : '#ff4757';

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><code style="color: #6c63ff;">${license.key}</code></td>
                    <td>${license.type}</td>
                    <td style="color: ${statusColor};">${license.status}</td>
                    <td>${license.credits}</td>
                    <td>${license.used_by || '-'}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (error) {
        console.error('Licenses load error:', error);
    }
}

// ===== USER CREDITS =====
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
                document.getElementById('currentCredits').value = selected.dataset.credits || 0;
            };
        }
    } catch (error) {
        console.error('Credit users load error:', error);
    }
}

async function addCredits() {
    const userId = document.getElementById('creditUserSelect').value;
    const amount = document.getElementById('addCreditsAmount').value;

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
            loadCreditUsers();
        } else {
            showToast(data.message || 'Failed!', 'error');
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

async function setCredits() {
    const userId = document.getElementById('creditUserSelect').value;
    const amount = document.getElementById('setCreditsAmount').value;

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
            loadCreditUsers();
        } else {
            showToast(data.message || 'Failed!', 'error');
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

function showUserInfo(user) {
    showToast(`${user.username} - Credits: ${user.credits}`, 'success');
}