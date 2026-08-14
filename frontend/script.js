// ===== STRUGGLE AI - MAIN SCRIPT =====
// Fixed all functions + Auto backend URL detection

// ===== AUTO API URL DETECTION =====
const API_URL = window.location.origin;

// ===== LOGIN MODE =====
let currentMode = 'user';

function setMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const activeBtn = document.querySelector(`[data-mode="${mode}"]`);
    if (activeBtn) activeBtn.classList.add('active');

    const titles = {
        user: 'Secure Login',
        admin: 'Admin Login',
        owner: 'Owner Login'
    };

    const titleEl = document.getElementById('loginTitle');
    if (titleEl) titleEl.textContent = titles[mode];
}

// ===== HANDLE LOGIN =====
async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('loginBtn');

    if (!username || !password) {
        showToast('Please fill in all fields!', 'error');
        return;
    }

    // Show loader
    const btnText = loginBtn.querySelector('.btn-text');
    const btnLoader = loginBtn.querySelector('.btn-loader');
    if (btnText) btnText.style.display = 'none';
    if (btnLoader) btnLoader.style.display = 'block';
    loginBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                password: password,
                mode: currentMode
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Login successful! Redirecting...', 'success');
            localStorage.setItem('token', data.token);
            localStorage.setItem('userMode', currentMode);
            localStorage.setItem('username', username);

            setTimeout(() => {
                if (currentMode === 'user') window.location.href = 'user-dashboard.html';
                else if (currentMode === 'admin') window.location.href = 'admin-dashboard.html';
                else if (currentMode === 'owner') window.location.href = 'owner-dashboard.html';
            }, 1000);
        } else {
            showToast(data.message || 'Invalid credentials!', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Connection error! Please try again.', 'error');
    } finally {
        if (btnText) btnText.style.display = 'flex';
        if (btnLoader) btnLoader.style.display = 'none';
        loginBtn.disabled = false;
    }
}

// ===== HANDLE REGISTER =====
async function handleRegister(event) {
    event.preventDefault();

    const license = document.getElementById('licenseKey').value.trim();
    const username = document.getElementById('regUsername').value.trim();
    const password = document.getElementById('regPassword').value;
    const registerBtn = document.getElementById('registerBtn');

    if (!license || !username || !password) {
        showToast('Please fill in all fields!', 'error');
        return;
    }

    if (password.length < 6) {
        showToast('Password must be at least 6 characters!', 'error');
        return;
    }

    if (username.length < 3) {
        showToast('Username must be at least 3 characters!', 'error');
        return;
    }

    const btnText = registerBtn.querySelector('.btn-text');
    const btnLoader = registerBtn.querySelector('.btn-loader');
    if (btnText) btnText.style.display = 'none';
    if (btnLoader) btnLoader.style.display = 'block';
    registerBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/api/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                license_key: license,
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Account created successfully!', 'success');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1500);
        } else {
            showToast(data.message || 'Registration failed!', 'error');
        }
    } catch (error) {
        console.error('Register error:', error);
        showToast('Connection error! Please try again.', 'error');
    } finally {
        if (btnText) btnText.style.display = 'flex';
        if (btnLoader) btnLoader.style.display = 'none';
        registerBtn.disabled = false;
    }
}

// ===== TOGGLE PASSWORD =====
function togglePassword() {
    const input = document.getElementById('password');
    const icon = document.getElementById('eyeIcon');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

function toggleRegPassword() {
    const input = document.getElementById('regPassword');
    const icon = document.getElementById('regEyeIcon');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

// ===== FORGOT PASSWORD =====
function showForgotPassword() {
    document.getElementById('forgotModal').style.display = 'flex';
}

function closeForgotModal() {
    document.getElementById('forgotModal').style.display = 'none';
}

async function resetPassword() {
    const license = document.getElementById('resetLicense').value.trim();
    const newPass = document.getElementById('newPassword').value;
    const confirmPass = document.getElementById('confirmPassword').value;

    if (!license || !newPass || !confirmPass) {
        showToast('Please fill in all fields!', 'error');
        return;
    }

    if (newPass !== confirmPass) {
        showToast('Passwords do not match!', 'error');
        return;
    }

    if (newPass.length < 6) {
        showToast('Password must be at least 6 characters!', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                license_key: license,
                new_password: newPass
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Password reset successful!', 'success');
            closeForgotModal();
        } else {
            showToast(data.message || 'Reset failed!', 'error');
        }
    } catch (error) {
        console.error('Reset error:', error);
        showToast('Connection error!', 'error');
    }
}

// ===== TOAST NOTIFICATION =====
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');

    if (!toast) return;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️'
    };

    toast.className = `toast ${type}`;
    if (toastIcon) toastIcon.textContent = icons[type];
    if (toastMessage) toastMessage.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3500);
}

// ===== AUTO REDIRECT IF LOGGED IN =====
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const mode = localStorage.getItem('userMode');
    const path = window.location.pathname;

    // Only redirect on index.html or register.html
    if (token && mode && (path.includes('index.html') || path.endsWith('/') || path.includes('register.html'))) {
        if (mode === 'user') window.location.href = 'user-dashboard.html';
        else if (mode === 'admin') window.location.href = 'admin-dashboard.html';
        else if (mode === 'owner') window.location.href = 'owner-dashboard.html';
    }
});
