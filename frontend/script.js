// ===== CONFIGURATION =====
const API_URL = 'https://trading-analyzer-hm0g.onrender.com'; // Replace after deploy

// ===== LOGIN MODE =====
let currentMode = 'user';

function setMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-mode="${mode}"]`).classList.add('active');

    const titles = {
        user: { title: 'User Login', subtitle: 'Welcome back! Please login to continue' },
        admin: { title: 'Admin Login', subtitle: 'Admin access only' },
        owner: { title: 'Owner Login', subtitle: 'Full system control access' }
    };

    document.getElementById('loginTitle').textContent = titles[mode].title;
    document.getElementById('loginSubtitle').textContent = titles[mode].subtitle;
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
    loginBtn.querySelector('.btn-text').style.display = 'none';
    loginBtn.querySelector('.btn-loader').style.display = 'block';
    loginBtn.querySelector('.btn-arrow').style.display = 'none';
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
            }, 1500);
        } else {
            showToast(data.message || 'Invalid credentials!', 'error');
        }
    } catch (error) {
        showToast('Connection error! Please try again.', 'error');
    } finally {
        loginBtn.querySelector('.btn-text').style.display = 'block';
        loginBtn.querySelector('.btn-loader').style.display = 'none';
        loginBtn.querySelector('.btn-arrow').style.display = 'block';
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

    registerBtn.querySelector('.btn-text').style.display = 'none';
    registerBtn.querySelector('.btn-loader').style.display = 'block';
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
            }, 2000);
        } else {
            showToast(data.message || 'Registration failed!', 'error');
        }
    } catch (error) {
        showToast('Connection error! Please try again.', 'error');
    } finally {
        registerBtn.querySelector('.btn-text').style.display = 'block';
        registerBtn.querySelector('.btn-loader').style.display = 'none';
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
        showToast('Connection error!', 'error');
    }
}

// ===== TOAST NOTIFICATION =====
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️'
    };

    toast.className = `toast ${type}`;
    toastIcon.textContent = icons[type];
    toastMessage.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3500);
}

// ===== PARTICLES =====
function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;

    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 3 + 1}px;
            height: ${Math.random() * 3 + 1}px;
            background: rgba(108, 99, 255, ${Math.random() * 0.5 + 0.2});
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: particleFloat ${Math.random() * 10 + 5}s ease-in-out infinite;
            animation-delay: ${Math.random() * 5}s;
        `;
        container.appendChild(particle);
    }
}

// Add particle animation to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes particleFloat {
        0%, 100% { transform: translateY(0) translateX(0); opacity: 0.5; }
        25% { transform: translateY(-20px) translateX(10px); opacity: 1; }
        75% { transform: translateY(20px) translateX(-10px); opacity: 0.3; }
    }
`;
document.head.appendChild(style);

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    createParticles();

    // Check if already logged in
    const token = localStorage.getItem('token');
    const mode = localStorage.getItem('userMode');
    if (token && mode && window.location.pathname.includes('index.html')) {
        if (mode === 'user') window.location.href = 'user-dashboard.html';
        else if (mode === 'admin') window.location.href = 'admin-dashboard.html';
        else if (mode === 'owner') window.location.href = 'owner-dashboard.html';
    }
});
