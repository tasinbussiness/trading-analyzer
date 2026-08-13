// ===== DASHBOARD COMMON FUNCTIONS =====

// ===== SIDEBAR TOGGLE =====
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('show');
}

// ===== PAGE NAVIGATION =====
function showPage(pageId, element) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    document.getElementById(`page-${pageId}`).classList.add('active');
    if (element) element.classList.add('active');

    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
        toggleSidebar();
    }
}

// ===== LOGOUT =====
function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userMode');
    localStorage.removeItem('username');
    window.location.href = 'index.html';
}

// ===== AUTH CHECK =====
function checkAuth(requiredMode) {
    const token = localStorage.getItem('token');
    const mode = localStorage.getItem('userMode');

    if (!token || mode !== requiredMode) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// ===== IMAGE UPLOAD HANDLING =====
let selectedFile = null;
let lastAnalyzedHash = null;

// Click to upload
document.addEventListener('DOMContentLoaded', () => {
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('fileInput');

    if (uploadBox && fileInput) {
        uploadBox.addEventListener('click', (e) => {
            if (e.target.closest('.remove-img')) return;
            fileInput.click();
        });
    }

    // Paste support
    document.addEventListener('paste', (e) => {
        const items = e.clipboardData.items;
        for (let item of items) {
            if (item.type.indexOf('image') !== -1) {
                const file = item.getAsFile();
                processFile(file);
                break;
            }
        }
    });
});

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) processFile(file);
}

function handleDrop(event) {
    event.preventDefault();
    const uploadBox = document.getElementById('uploadBox');
    uploadBox.classList.remove('drag-over');

    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        processFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    document.getElementById('uploadBox').classList.add('drag-over');
}

function handleDragLeave(event) {
    document.getElementById('uploadBox').classList.remove('drag-over');
}

function processFile(file) {
    if (!file.type.startsWith('image/')) {
        showToast('Please upload an image file!', 'error');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showToast('File too large! Max 10MB', 'error');
        return;
    }

    selectedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('uploadContent').style.display = 'none';
        document.getElementById('uploadPreview').style.display = 'block';
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('analyzeBtn').disabled = false;
    };
    reader.readAsDataURL(file);
}

function removeImage() {
    selectedFile = null;
    document.getElementById('uploadContent').style.display = 'block';
    document.getElementById('uploadPreview').style.display = 'none';
    document.getElementById('previewImg').src = '';
    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('fileInput').value = '';
}

// ===== ANALYSIS FUNCTIONS =====
async function startAnalysis() {
    if (!selectedFile) {
        showToast('Please upload a chart screenshot!', 'error');
        return;
    }

    // Hide upload, show processing
    document.querySelector('.upload-container').style.display = 'none';
    document.getElementById('resultContainer').style.display = 'none';
    document.getElementById('warningContainer').style.display = 'none';
    document.getElementById('processingContainer').style.display = 'block';

    // Start processing animation
    await animateProcessing();

    // Send to backend
    try {
        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('token', localStorage.getItem('token'));

        if (lastAnalyzedHash) {
            formData.append('last_hash', lastAnalyzedHash);
        }

        const response = await fetch(`${API_URL}/api/analyze`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        document.getElementById('processingContainer').style.display = 'none';

        if (data.warning) {
            // Show warning
            showWarning(data.warning_title, data.warning_message);
        } else if (data.success) {
            lastAnalyzedHash = data.chart_hash;
            showResult(data);
        } else {
            showToast(data.message || 'Analysis failed!', 'error');
            resetAnalysis();
        }
    } catch (error) {
        document.getElementById('processingContainer').style.display = 'none';
        showToast('Connection error! Please try again.', 'error');
        resetAnalysis();
    }
}

// ===== PROCESSING ANIMATION =====
function animateProcessing() {
    return new Promise((resolve) => {
        const progressCircle = document.getElementById('progressCircle');
        const processPercent = document.getElementById('processPercent');
        const steps = ['step1', 'step2', 'step3', 'step4'];
        const texts = ['Reading Chart...', 'Detecting Patterns...', 'Applying Strategies...', 'Generating Signal...'];
        const processingText = document.getElementById('processingText');

        let progress = 0;
        const circumference = 2 * Math.PI * 45;
        progressCircle.style.strokeDasharray = circumference;

        const interval = setInterval(() => {
            progress += 1;
            const offset = circumference - (progress / 100) * circumference;
            progressCircle.style.strokeDashoffset = offset;
            processPercent.textContent = `${progress}%`;

            // Step updates
            if (progress === 20) {
                steps.forEach((s, i) => {
                    document.getElementById(s).className = i === 0 ? 'step done' : 'step';
                    document.getElementById(s).querySelector('i').className = i === 0 ? 'fas fa-check-circle' : 'fas fa-circle';
                });
                document.getElementById('step2').className = 'step active';
                processingText.textContent = texts[1];
            }
            if (progress === 50) {
                document.getElementById('step2').className = 'step done';
                document.getElementById('step2').querySelector('i').className = 'fas fa-check-circle';
                document.getElementById('step3').className = 'step active';
                processingText.textContent = texts[2];
            }
            if (progress === 80) {
                document.getElementById('step3').className = 'step done';
                document.getElementById('step3').querySelector('i').className = 'fas fa-check-circle';
                document.getElementById('step4').className = 'step active';
                processingText.textContent = texts[3];
            }
            if (progress >= 100) {
                clearInterval(interval);
                document.getElementById('step4').className = 'step done';
                document.getElementById('step4').querySelector('i').className = 'fas fa-check-circle';
                processingText.textContent = 'Analysis Complete!';
                setTimeout(resolve, 500);
            }
        }, 120); // ~12 seconds total
    });
}

// ===== SHOW RESULT =====
function showResult(data) {
    const resultContainer = document.getElementById('resultContainer');
    const resultHeader = document.getElementById('resultHeader');

    // Signal
    let signalClass, signalIcon, signalText;
    if (data.signal === 'BUY' || data.signal === 'STRONG BUY') {
        signalClass = 'buy';
        signalIcon = '📈';
        signalText = data.signal === 'STRONG BUY' ? '🟢 STRONG BUY' : '🟢 BUY';
    } else if (data.signal === 'SELL' || data.signal === 'STRONG SELL') {
        signalClass = 'sell';
        signalIcon = '📉';
        signalText = data.signal === 'STRONG SELL' ? '🔴 STRONG SELL' : '🔴 SELL';
    } else {
        signalClass = 'avoid';
        signalIcon = '⚠️';
        signalText = '🟡 AVOID TRADE';
    }

    resultHeader.className = `result-header ${signalClass}`;
    document.getElementById('signalIcon').textContent = signalIcon;
    document.getElementById('signalText').textContent = signalText;

    // Confidence
    document.getElementById('resultConfidence').textContent = `${data.confidence}%`;
    const confBar = document.getElementById('confidenceBar');
    confBar.style.width = `${data.confidence}%`;
    confBar.style.background = data.confidence >= 80 ? '#00d084' : data.confidence >= 60 ? '#ffb800' : '#ff4757';

    // Risk
    document.getElementById('resultRisk').textContent = data.risk;
    const riskBar = document.getElementById('riskBar');
    const riskPercent = data.risk === 'Low' ? 30 : data.risk === 'Medium' ? 60 : 90;
    riskBar.style.width = `${riskPercent}%`;
    riskBar.style.background = data.risk === 'Low' ? '#00d084' : data.risk === 'Medium' ? '#ffb800' : '#ff4757';

    // Market Strength
    document.getElementById('resultStrength').textContent = `${data.market_strength}%`;
    const strBar = document.getElementById('strengthBar');
    strBar.style.width = `${data.market_strength}%`;
    strBar.style.background = data.market_strength >= 70 ? '#00d084' : data.market_strength >= 50 ? '#ffb800' : '#ff4757';

    // Strategy Tags
    const strategyTags = document.getElementById('strategyTags');
    strategyTags.innerHTML = '';
    if (data.strategies && data.strategies.length > 0) {
        data.strategies.forEach(s => {
            const tag = document.createElement('span');
            tag.className = 'strategy-tag matched';
            tag.textContent = s;
            strategyTags.appendChild(tag);
        });
    }

    // Note
    document.getElementById('resultNote').textContent = data.note || '';

    resultContainer.style.display = 'block';
}

// ===== SHOW WARNING =====
function showWarning(title, message) {
    document.getElementById('warningTitle').textContent = title;
    document.getElementById('warningMessage').textContent = message;
    document.getElementById('warningContainer').style.display = 'block';
}

// ===== RESET ANALYSIS =====
function resetAnalysis() {
    document.querySelector('.upload-container').style.display = 'block';
    document.getElementById('processingContainer').style.display = 'none';
    document.getElementById('resultContainer').style.display = 'none';
    document.getElementById('warningContainer').style.display = 'none';
    removeImage();

    // Reset processing steps
    ['step1', 'step2', 'step3', 'step4'].forEach((s, i) => {
        const step = document.getElementById(s);
        step.className = i === 0 ? 'step active' : 'step';
        step.querySelector('i').className = i === 0 ? 'fas fa-check-circle' : 'fas fa-circle';
    });
}

// ===== SUPPORT =====
function showSupport() {
    document.getElementById('supportModal').style.display = 'flex';
}

function closeSupport() {
    document.getElementById('supportModal').style.display = 'none';
}

// ===== NOTICE =====
function dismissNotice() {
    document.getElementById('noticeBanner').style.display = 'none';
}

// ===== UPLOAD AVATAR =====
async function uploadAvatar(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('avatar', file);
    formData.append('token', localStorage.getItem('token'));

    try {
        const response = await fetch(`${API_URL}/api/upload-avatar`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.success) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const avatarImg = document.getElementById('profileAvatarImg');
                const avatarIcon = document.getElementById('profileAvatarIcon');
                avatarImg.src = e.target.result;
                avatarImg.style.display = 'block';
                if (avatarIcon) avatarIcon.style.display = 'none';

                // Update topbar avatar
                const topAvatarImg = document.getElementById('avatarImg');
                const topAvatarIcon = document.getElementById('avatarIcon');
                if (topAvatarImg) {
                    topAvatarImg.src = e.target.result;
                    topAvatarImg.style.display = 'block';
                }
                if (topAvatarIcon) topAvatarIcon.style.display = 'none';
            };
            reader.readAsDataURL(file);
            showToast('Avatar updated!', 'success');
        } else {
            showToast('Upload failed!', 'error');
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

// ===== SAVE NICKNAME =====
async function saveNickname() {
    const nickname = document.getElementById('nickname').value.trim();
    if (!nickname) {
        showToast('Please enter a nickname!', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/update-nickname`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: localStorage.getItem('token'),
                nickname: nickname
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast('Nickname saved!', 'success');
            document.getElementById('profileName').textContent = nickname;
        } else {
            showToast('Failed to save nickname!', 'error');
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

// ===== CHANGE PASSWORD =====
async function changePassword() {
    const license = document.getElementById('changeLicense').value.trim();
    const newPass = document.getElementById('changeNewPass').value;
    const confirmPass = document.getElementById('changeConfirmPass').value;

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
        const response = await fetch(`${API_URL}/api/change-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: localStorage.getItem('token'),
                license_key: license,
                new_password: newPass
            })
        });

        const data = await response.json();
        if (data.success) {
            showToast('Password updated!', 'success');
            document.getElementById('changeLicense').value = '';
            document.getElementById('changeNewPass').value = '';
            document.getElementById('changeConfirmPass').value = '';
        } else {
            showToast(data.message || 'Failed!', 'error');
        }
    } catch (error) {
        showToast('Connection error!', 'error');
    }
}

// ===== CREDIT COLOR =====
function updateCreditBar(current, max) {
    const fill = document.getElementById('creditBarFill');
    const text = document.getElementById('creditText');
    const percent = (current / max) * 100;

    if (fill) {
        fill.style.width = `${percent}%`;
        fill.className = 'credit-bar-fill';
        if (percent <= 30) fill.classList.add('low');
        else if (percent <= 60) fill.classList.add('medium');
    }

    if (text) text.textContent = `${current} / ${max}`;

    const creditCount = document.getElementById('creditCount');
    if (creditCount) creditCount.textContent = current;
}