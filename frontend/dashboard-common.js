// ===== DASHBOARD COMMON FUNCTIONS =====
// Fixed all functions + Fast Analysis (18-20 sec)

// ===== SIDEBAR TOGGLE =====
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar) sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('show');
}

// ===== PAGE NAVIGATION =====
function showPage(pageId, element) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    const page = document.getElementById(`page-${pageId}`);
    if (page) page.classList.add('active');
    if (element) element.classList.add('active');

    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        if (sidebar) sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('show');
    }
}

// ===== LOGOUT =====
function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('token');
        localStorage.removeItem('userMode');
        localStorage.removeItem('username');
        window.location.href = 'index.html';
    }
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

// ===== FILE UPLOAD VARIABLES =====
let selectedFile = null;
let lastAnalyzedHash = null;

// ===== INIT UPLOAD SYSTEM =====
document.addEventListener('DOMContentLoaded', () => {
    initUploadSystem();
});

function initUploadSystem() {
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('fileInput');

    if (uploadBox && fileInput) {
        // Click to upload
        uploadBox.addEventListener('click', (e) => {
            if (e.target.closest('.remove-img')) return;
            if (e.target.closest('.upload-preview')) return;
            fileInput.click();
        });
    }

    // Paste support
    document.addEventListener('paste', (e) => {
        if (!document.getElementById('page-analyzer')?.classList.contains('active')) return;
        
        const items = e.clipboardData?.items;
        if (!items) return;
        
        for (let item of items) {
            if (item.type.indexOf('image') !== -1) {
                const file = item.getAsFile();
                processFile(file);
                break;
            }
        }
    });
}

// ===== FILE HANDLERS =====
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) processFile(file);
}

function handleDrop(event) {
    event.preventDefault();
    const uploadBox = document.getElementById('uploadBox');
    if (uploadBox) uploadBox.classList.remove('drag-over');

    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        processFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    const uploadBox = document.getElementById('uploadBox');
    if (uploadBox) uploadBox.classList.add('drag-over');
}

function handleDragLeave(event) {
    const uploadBox = document.getElementById('uploadBox');
    if (uploadBox) uploadBox.classList.remove('drag-over');
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
        const uploadContent = document.getElementById('uploadContent');
        const uploadPreview = document.getElementById('uploadPreview');
        const previewImg = document.getElementById('previewImg');
        const analyzeBtn = document.getElementById('analyzeBtn');

        if (uploadContent) uploadContent.style.display = 'none';
        if (uploadPreview) uploadPreview.style.display = 'block';
        if (previewImg) previewImg.src = e.target.result;
        if (analyzeBtn) analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

function removeImage(event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    selectedFile = null;
    
    const uploadContent = document.getElementById('uploadContent');
    const uploadPreview = document.getElementById('uploadPreview');
    const previewImg = document.getElementById('previewImg');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const fileInput = document.getElementById('fileInput');

    if (uploadContent) uploadContent.style.display = 'block';
    if (uploadPreview) uploadPreview.style.display = 'none';
    if (previewImg) previewImg.src = '';
    if (analyzeBtn) analyzeBtn.disabled = true;
    if (fileInput) fileInput.value = '';
}

// ===== ANALYSIS - FAST 18 SEC =====
async function startAnalysis() {
    if (!selectedFile) {
        showToast('Please upload a chart screenshot!', 'error');
        return;
    }

    // Hide upload, show processing
    document.getElementById('uploadContainer').style.display = 'none';
    document.getElementById('resultContainer').style.display = 'none';
    document.getElementById('warningContainer').style.display = 'none';
    document.getElementById('processingContainer').style.display = 'block';

    // Start processing animation (18 sec) AND backend call in parallel
    const animationPromise = animateProcessing();
    const analysisPromise = performAnalysis();

    // Wait for both
    const [_, data] = await Promise.all([animationPromise, analysisPromise]);

    document.getElementById('processingContainer').style.display = 'none';

    if (!data) {
        showToast('Analysis failed! Please try again.', 'error');
        resetAnalysis();
        return;
    }

    if (data.warning) {
        showWarning(data.warning_title, data.warning_message);
    } else if (data.success) {
        lastAnalyzedHash = data.chart_hash;
        showResult(data);
        
        // Reload stats/profile after analysis
        if (typeof loadUserProfile === 'function') loadUserProfile();
        if (typeof loadUserStats === 'function') loadUserStats();
    } else {
        showToast(data.message || 'Analysis failed!', 'error');
        resetAnalysis();
    }
}

async function performAnalysis() {
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

        return await response.json();
    } catch (error) {
        console.error('Analysis error:', error);
        return null;
    }
}

// ===== PROCESSING ANIMATION (18 SEC) =====
function animateProcessing() {
    return new Promise((resolve) => {
        const progressCircle = document.getElementById('progressCircle');
        const processPercent = document.getElementById('processPercent');
        const processingText = document.getElementById('processingText');
        const texts = ['Reading Chart...', 'Detecting Patterns...', 'Applying Strategies...', 'Generating Signal...'];

        let progress = 0;
        const circumference = 2 * Math.PI * 45;
        
        if (progressCircle) {
            progressCircle.style.strokeDasharray = circumference;
        }

        // Reset all steps
        ['step1', 'step2', 'step3', 'step4'].forEach((s) => {
            const step = document.getElementById(s);
            if (step) {
                step.className = 'step';
                const icon = step.querySelector('i');
                if (icon) icon.className = 'fas fa-circle';
            }
        });

        // Activate step 1
        const step1 = document.getElementById('step1');
        if (step1) step1.className = 'step active';
        if (processingText) processingText.textContent = texts[0];

        const totalTime = 18000; // 18 seconds
        const intervalTime = 100;
        const totalSteps = totalTime / intervalTime;
        const increment = 100 / totalSteps;

        const interval = setInterval(() => {
            progress += increment;
            
            if (progress > 100) progress = 100;
            
            const offset = circumference - (progress / 100) * circumference;
            if (progressCircle) progressCircle.style.strokeDashoffset = offset;
            if (processPercent) processPercent.textContent = `${Math.round(progress)}%`;

            // Step transitions
            if (progress >= 25 && progress < 50) {
                markStepDone('step1');
                activateStep('step2');
                if (processingText) processingText.textContent = texts[1];
            } else if (progress >= 50 && progress < 75) {
                markStepDone('step2');
                activateStep('step3');
                if (processingText) processingText.textContent = texts[2];
            } else if (progress >= 75 && progress < 100) {
                markStepDone('step3');
                activateStep('step4');
                if (processingText) processingText.textContent = texts[3];
            } else if (progress >= 100) {
                clearInterval(interval);
                markStepDone('step4');
                if (processingText) processingText.textContent = 'Analysis Complete!';
                setTimeout(resolve, 300);
            }
        }, intervalTime);
    });
}

function activateStep(stepId) {
    const step = document.getElementById(stepId);
    if (step && !step.classList.contains('done')) {
        step.className = 'step active';
    }
}

function markStepDone(stepId) {
    const step = document.getElementById(stepId);
    if (step) {
        step.className = 'step done';
        const icon = step.querySelector('i');
        if (icon) icon.className = 'fas fa-check-circle';
    }
}

// ===== SHOW RESULT =====
function showResult(data) {
    const resultContainer = document.getElementById('resultContainer');
    const resultHeader = document.getElementById('resultHeader');

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

    if (resultHeader) resultHeader.className = `result-header ${signalClass}`;
    
    const signalIconEl = document.getElementById('signalIcon');
    const signalTextEl = document.getElementById('signalText');
    if (signalIconEl) signalIconEl.textContent = signalIcon;
    if (signalTextEl) signalTextEl.textContent = signalText;

    // Confidence
    const confidenceEl = document.getElementById('resultConfidence');
    const confBar = document.getElementById('confidenceBar');
    if (confidenceEl) confidenceEl.textContent = `${data.confidence}%`;
    if (confBar) {
        confBar.style.width = `${data.confidence}%`;
        confBar.style.background = data.confidence >= 80 ? '#00ff88' : data.confidence >= 60 ? '#ffb800' : '#ff3b5c';
    }

    // Risk
    const riskEl = document.getElementById('resultRisk');
    const riskBar = document.getElementById('riskBar');
    if (riskEl) riskEl.textContent = data.risk;
    if (riskBar) {
        const riskPercent = data.risk === 'Low' ? 30 : data.risk === 'Medium' ? 60 : 90;
        riskBar.style.width = `${riskPercent}%`;
        riskBar.style.background = data.risk === 'Low' ? '#00ff88' : data.risk === 'Medium' ? '#ffb800' : '#ff3b5c';
    }

    // Market Strength
    const strengthEl = document.getElementById('resultStrength');
    const strBar = document.getElementById('strengthBar');
    if (strengthEl) strengthEl.textContent = `${data.market_strength}%`;
    if (strBar) {
        strBar.style.width = `${data.market_strength}%`;
        strBar.style.background = data.market_strength >= 70 ? '#00ff88' : data.market_strength >= 50 ? '#ffb800' : '#ff3b5c';
    }

    // Strategy Tags
    const strategyTags = document.getElementById('strategyTags');
    if (strategyTags) {
        strategyTags.innerHTML = '';
        if (data.strategies && data.strategies.length > 0) {
            data.strategies.forEach(s => {
                const tag = document.createElement('span');
                tag.className = 'strategy-tag matched';
                tag.textContent = s;
                strategyTags.appendChild(tag);
            });
        } else {
            strategyTags.innerHTML = '<span style="color: rgba(200,220,255,0.5); font-size: 12px;">No strategies matched</span>';
        }
    }

    // Note
    const noteEl = document.getElementById('resultNote');
    if (noteEl) noteEl.textContent = data.note || '';

    if (resultContainer) resultContainer.style.display = 'block';
}

// ===== SHOW WARNING =====
function showWarning(title, message) {
    const titleEl = document.getElementById('warningTitle');
    const msgEl = document.getElementById('warningMessage');
    const container = document.getElementById('warningContainer');
    
    if (titleEl) titleEl.textContent = title;
    if (msgEl) msgEl.textContent = message;
    if (container) container.style.display = 'block';
}

// ===== RESET ANALYSIS =====
function resetAnalysis() {
    document.getElementById('uploadContainer').style.display = 'block';
    document.getElementById('processingContainer').style.display = 'none';
    document.getElementById('resultContainer').style.display = 'none';
    document.getElementById('warningContainer').style.display = 'none';
    removeImage();

    // Reset processing steps
    ['step1', 'step2', 'step3', 'step4'].forEach((s) => {
        const step = document.getElementById(s);
        if (step) {
            step.className = 'step';
            const icon = step.querySelector('i');
            if (icon) icon.className = 'fas fa-circle';
        }
    });
    
    // Reset progress
    const progressCircle = document.getElementById('progressCircle');
    const processPercent = document.getElementById('processPercent');
    if (progressCircle) progressCircle.style.strokeDashoffset = 283;
    if (processPercent) processPercent.textContent = '0%';
}

// ===== SUPPORT =====
function showSupport() {
    const modal = document.getElementById('supportModal');
    if (modal) {
        modal.style.display = 'flex';
        loadSupportLinks();
    }
}

function closeSupport() {
    const modal = document.getElementById('supportModal');
    if (modal) modal.style.display = 'none';
}

async function loadSupportLinks() {
    try {
        const response = await fetch(`${API_URL}/api/support-links`);
        const data = await response.json();

        if (data.success) {
            const ownerBtn = document.getElementById('ownerSupport');
            const altBtn = document.getElementById('altOwnerSupport');
            const adminBtn = document.getElementById('adminSupport');
            
            if (ownerBtn) ownerBtn.href = data.owner || '#';
            if (altBtn) altBtn.href = data.alt_owner || '#';
            if (adminBtn) adminBtn.href = data.admin || '#';
        }
    } catch (error) {
        console.error('Support links error:', error);
    }
}

// ===== NOTICE =====
function dismissNotice() {
    const banner = document.getElementById('noticeBanner');
    if (banner) banner.style.display = 'none';
}

// ===== UPLOAD AVATAR =====
async function uploadAvatar(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
        showToast('Avatar too large! Max 5MB', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('avatar', file);
    formData.append('token', localStorage.getItem('token'));

    try {
        showToast('Uploading avatar...', 'success');
        
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
                if (avatarImg) {
                    avatarImg.src = e.target.result;
                    avatarImg.style.display = 'block';
                }
                if (avatarIcon) avatarIcon.style.display = 'none';

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
        console.error('Avatar upload error:', error);
        showToast('Connection error!', 'error');
    }
}

// ===== SAVE NICKNAME =====
async function saveNickname() {
    const nicknameInput = document.getElementById('nickname');
    if (!nicknameInput) return;
    
    const nickname = nicknameInput.value.trim();
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
            const nameEl = document.getElementById('profileName');
            if (nameEl) nameEl.textContent = nickname;
        } else {
            showToast('Failed to save nickname!', 'error');
        }
    } catch (error) {
        console.error('Nickname error:', error);
        showToast('Connection error!', 'error');
    }
}

// ===== CHANGE PASSWORD =====
async function changePassword() {
    const license = document.getElementById('changeLicense')?.value.trim();
    const newPass = document.getElementById('changeNewPass')?.value;
    const confirmPass = document.getElementById('changeConfirmPass')?.value;

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
        console.error('Password error:', error);
        showToast('Connection error!', 'error');
    }
}

// ===== CREDIT BAR UPDATE =====
function updateCreditBar(current, max) {
    const fill = document.getElementById('creditBarFill');
    const text = document.getElementById('creditText');
    const percent = max > 0 ? (current / max) * 100 : 0;

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
