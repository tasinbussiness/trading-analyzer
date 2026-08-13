# ===== TRADING ANALYZER BACKEND =====
# Main Server - app.py

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import jwt
import hashlib
import datetime
import uuid
import json
import base64
from functools import wraps

# Import modules
from database_setup import init_db
from license_system import LicenseManager
from vision_ai import VisionAI
from strategies import StrategyEngine

app = Flask(__name__, static_folder='frontend')
CORS(app)

# ===== CONFIG =====
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'trading-analyzer-secret-key-2024')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ===== INIT =====
database = init_db()
license_manager = LicenseManager(database)
vision_ai = VisionAI()
strategy_engine = StrategyEngine()

# ===== OWNER CONFIG =====
OWNER_USERNAME = os.environ.get('OWNER_USERNAME', 'owner')
OWNER_PASSWORD = os.environ.get('OWNER_PASSWORD', 'owner123')

SUPPORT_LINKS = {
    'owner': os.environ.get('OWNER_TELEGRAM', 'https://t.me/owner'),
    'alt_owner': os.environ.get('ALT_OWNER_TELEGRAM', 'https://t.me/alt_owner'),
    'admin': os.environ.get('ADMIN_TELEGRAM', 'https://t.me/admin')
}

# ===== HELPER FUNCTIONS =====
def generate_token(user_id, username, role):
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except:
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.json.get('token') if request.is_json else request.form.get('token')
        if not token:
            return jsonify({'success': False, 'message': 'Token required'}), 401
        
        decoded = decode_token(token)
        if not decoded:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401
        
        # Check if user is paused/banned
        user = database.get_user(decoded['user_id'])
        if user and user.get('status') in ['paused', 'banned']:
            return jsonify({'success': False, 'message': 'Account is suspended'}), 403
        
        request.user = decoded
        return f(*args, **kwargs)
    return decorated

# ===== SERVE FRONTEND =====
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

# ============================================
# ===== AUTH ROUTES =====
# ============================================

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    license_key = data.get('license_key', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not license_key or not username or not password:
        return jsonify({'success': False, 'message': 'All fields are required!'})

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters!'})

    if len(username) < 3:
        return jsonify({'success': False, 'message': 'Username must be at least 3 characters!'})

    # Check username exists
    if database.username_exists(username):
        return jsonify({'success': False, 'message': 'Username already taken!'})

    # Validate license
    license_info = license_manager.validate_license(license_key)
    if not license_info:
        return jsonify({'success': False, 'message': 'Invalid license key!'})

    if license_info['status'] == 'used':
        return jsonify({'success': False, 'message': 'License already used!'})

    # Create user
    user_id = str(uuid.uuid4())
    user_data = {
        'id': user_id,
        'username': username,
        'password': hash_password(password),
        'role': license_info['type'],  # 'user' or 'admin'
        'license_key': license_key,
        'credits': license_info.get('credits', 50),
        'max_credits': license_info.get('credits', 50),
        'nickname': '',
        'avatar': '',
        'status': 'active',
        'created_at': datetime.datetime.utcnow().isoformat(),
        'analysis_count': 0,
        'analysis_history': []
    }

    database.create_user(user_data)
    license_manager.use_license(license_key, username)

    return jsonify({'success': True, 'message': 'Account created successfully!'})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    mode = data.get('mode', 'user')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Please fill in all fields!'})

    # Owner login
    if mode == 'owner':
        if username == OWNER_USERNAME and password == OWNER_PASSWORD:
            token = generate_token('owner', OWNER_USERNAME, 'owner')
            return jsonify({'success': True, 'token': token, 'message': 'Welcome Owner!'})
        else:
            return jsonify({'success': False, 'message': 'Invalid owner credentials!'})

    # User/Admin login
    user = database.get_user_by_username(username)
    if not user:
        return jsonify({'success': False, 'message': 'User not found!'})

    if user['password'] != hash_password(password):
        return jsonify({'success': False, 'message': 'Wrong password!'})

    if user.get('status') in ['paused', 'banned']:
        return jsonify({'success': False, 'message': 'Your account is suspended!'})

    # Check role matches mode
    if mode == 'admin' and user['role'] != 'admin':
        return jsonify({'success': False, 'message': 'You are not an admin!'})

    if mode == 'user' and user['role'] != 'user':
        return jsonify({'success': False, 'message': 'Please use admin login!'})

    token = generate_token(user['id'], user['username'], user['role'])
    return jsonify({'success': True, 'token': token, 'message': 'Login successful!'})


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    license_key = data.get('license_key', '').strip()
    new_password = data.get('new_password', '')

    if not license_key or not new_password:
        return jsonify({'success': False, 'message': 'All fields required!'})

    user = database.get_user_by_license(license_key)
    if not user:
        return jsonify({'success': False, 'message': 'Invalid license key!'})

    database.update_user(user['id'], {'password': hash_password(new_password)})
    return jsonify({'success': True, 'message': 'Password reset successful!'})


# ============================================
# ===== PROFILE ROUTES =====
# ============================================

@app.route('/api/profile', methods=['POST'])
@require_auth
def get_profile():
    user_id = request.user['user_id']

    if user_id == 'owner':
        return jsonify({
            'success': True,
            'username': OWNER_USERNAME,
            'nickname': database.get_owner_data().get('nickname', ''),
            'avatar': database.get_owner_data().get('avatar', ''),
            'role': 'owner'
        })

    user = database.get_user(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found!'})

    return jsonify({
        'success': True,
        'username': user['username'],
        'nickname': user.get('nickname', ''),
        'avatar': user.get('avatar', ''),
        'credits': user.get('credits', 0),
        'max_credits': user.get('max_credits', 50),
        'role': user['role']
    })


@app.route('/api/update-nickname', methods=['POST'])
@require_auth
def update_nickname():
    data = request.json
    nickname = data.get('nickname', '').strip()

    if request.user['user_id'] == 'owner':
        database.update_owner_data({'nickname': nickname})
    else:
        database.update_user(request.user['user_id'], {'nickname': nickname})

    return jsonify({'success': True})


@app.route('/api/upload-avatar', methods=['POST'])
@require_auth
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': 'No file!'})

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected!'})

    # Save avatar
    filename = f"{request.user['user_id']}_{uuid.uuid4().hex[:8]}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Convert to base64 for storage
    with open(filepath, 'rb') as f:
        avatar_b64 = base64.b64encode(f.read()).decode()
    avatar_url = f"data:image/jpeg;base64,{avatar_b64}"

    if request.user['user_id'] == 'owner':
        database.update_owner_data({'avatar': avatar_url})
    else:
        database.update_user(request.user['user_id'], {'avatar': avatar_url})

    # Cleanup file
    os.remove(filepath)

    return jsonify({'success': True, 'avatar': avatar_url})


@app.route('/api/change-password', methods=['POST'])
@require_auth
def change_password():
    data = request.json
    license_key = data.get('license_key', '')
    new_password = data.get('new_password', '')

    user = database.get_user(request.user['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found!'})

    if user.get('license_key') != license_key:
        return jsonify({'success': False, 'message': 'Invalid license key!'})

    database.update_user(user['id'], {'password': hash_password(new_password)})
    return jsonify({'success': True, 'message': 'Password updated!'})


# ============================================
# ===== ANALYZER ROUTE =====
# ============================================

@app.route('/api/analyze', methods=['POST'])
def analyze():
    token = request.form.get('token')
    if not token:
        return jsonify({'success': False, 'message': 'Token required!'})

    decoded = decode_token(token)
    if not decoded:
        return jsonify({'success': False, 'message': 'Invalid token!'})

    user_id = decoded['user_id']
    
    # Check credits (skip for owner/admin)
    if user_id != 'owner' and decoded.get('role') != 'admin':
        user = database.get_user(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found!'})
        if user.get('status') in ['paused', 'banned']:
            return jsonify({'success': False, 'message': 'Account suspended!'})

    # Get image
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image uploaded!'})

    file = request.files['image']
    last_hash = request.form.get('last_hash', '')

    # Save temp image
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{uuid.uuid4().hex}.jpg")
    file.save(temp_path)

    try:
        # Read image bytes
        with open(temp_path, 'rb') as f:
            image_bytes = f.read()

        # Generate hash for same chart detection
        current_hash = hashlib.md5(image_bytes).hexdigest()

        # ===== VISION AI ANALYSIS =====
        # Step 1: Validate if it's a chart
        is_chart = vision_ai.is_valid_chart(image_bytes)
        
        if not is_chart:
            return jsonify({
                'warning': True,
                'warning_title': '⚠️ Invalid Image!',
                'warning_message': 'This is not a valid trading chart! Please upload a proper chart screenshot with candlesticks.'
            })

        # Step 2: Check if same chart
        if last_hash and current_hash == last_hash:
            # Same chart - check for new candles
            has_new_candle = vision_ai.detect_new_candle(image_bytes, last_hash)
            
            if not has_new_candle:
                # Return previous signal
                prev_signal = database.get_last_signal(user_id)
                if prev_signal:
                    return jsonify({
                        'warning': True,
                        'warning_title': '⚠️ Same Chart Detected!',
                        'warning_message': f"Same chart detected! Previous signal: {prev_signal['signal']}. Wait for a new candle to get a new signal."
                    })

        # Step 3: Full chart analysis
        chart_data = vision_ai.analyze_chart(image_bytes)

        # Step 4: Apply strategies
        enabled_strategies = database.get_strategies()
        result = strategy_engine.analyze(chart_data, enabled_strategies)

        # Step 5: Determine signal
        signal = result['signal']
        confidence = result['confidence']
        risk = result['risk']
        market_strength = result['market_strength']
        strategies_matched = result['strategies']
        note = result['note']

        # Don't use credits for AVOID signals
        if signal != 'AVOID' and user_id != 'owner' and decoded.get('role') != 'admin':
            user = database.get_user(user_id)
            if user['credits'] <= 0:
                return jsonify({'success': False, 'message': 'No credits remaining!'})
            database.update_user(user_id, {'credits': user['credits'] - 1})

        # Save analysis record
        analysis_record = {
            'date': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
            'signal': signal,
            'confidence': confidence,
            'risk': risk,
            'market_strength': market_strength,
            'strategies': strategies_matched
        }

        database.add_analysis(user_id, analysis_record)
        database.save_last_signal(user_id, {
            'signal': signal,
            'hash': current_hash,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })

        return jsonify({
            'success': True,
            'signal': signal,
            'confidence': confidence,
            'risk': risk,
            'market_strength': market_strength,
            'strategies': strategies_matched,
            'note': note,
            'chart_hash': current_hash
        })

    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return jsonify({'success': False, 'message': 'Analysis failed! Please try again.'})
    
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================
# ===== USER STATS =====
# ============================================

@app.route('/api/user-stats', methods=['POST'])
@require_auth
def user_stats():
    user_id = request.user['user_id']
    stats = database.get_user_stats(user_id)
    return jsonify({'success': True, **stats})


# ============================================
# ===== SUPPORT & NOTICE =====
# ============================================

@app.route('/api/support-links', methods=['GET'])
def support_links():
    return jsonify({'success': True, **SUPPORT_LINKS})

@app.route('/api/get-notice', methods=['POST'])
@require_auth
def get_notice():
    notice = database.get_active_notice()
    if notice:
        return jsonify({'success': True, 'notice': notice['message']})
    return jsonify({'success': True, 'notice': None})


# ============================================
# ===== ADMIN ROUTES =====
# ============================================

@app.route('/api/admin/users', methods=['POST'])
@require_auth
def admin_get_users():
    if request.user['role'] not in ['admin', 'owner']:
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    users = database.get_all_users(role='user')
    safe_users = []
    for u in users:
        safe_users.append({
            'id': u['id'],
            'username': u['username'],
            'nickname': u.get('nickname', ''),
            'credits': u.get('credits', 0),
            'status': u.get('status', 'active'),
            'avatar': u.get('avatar', '')
        })

    return jsonify({'success': True, 'users': safe_users})


@app.route('/api/admin/generate-license', methods=['POST'])
@require_auth
def admin_generate_license():
    if request.user['role'] not in ['admin', 'owner']:
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    data = request.json
    license_type = data.get('type', 'user')
    credits = data.get('credits', 50)

    # Admin can only generate user licenses
    if request.user['role'] == 'admin' and license_type != 'user':
        return jsonify({'success': False, 'message': 'Admin can only generate user licenses!'})

    license_key = license_manager.generate_license(license_type, credits)
    return jsonify({'success': True, 'license_key': license_key})


@app.route('/api/admin/licenses', methods=['POST'])
@require_auth
def admin_get_licenses():
    if request.user['role'] not in ['admin', 'owner']:
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    licenses = license_manager.get_all_licenses()
    return jsonify({'success': True, 'licenses': licenses})


@app.route('/api/admin/add-credits', methods=['POST'])
@require_auth
def admin_add_credits():
    if request.user['role'] not in ['admin', 'owner']:
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount', 0)

    user = database.get_user(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found!'})

    new_credits = user.get('credits', 0) + amount
    database.update_user(user_id, {
        'credits': new_credits,
        'max_credits': max(user.get('max_credits', 50), new_credits)
    })

    return jsonify({'success': True})


@app.route('/api/admin/set-credits', methods=['POST'])
@require_auth
def admin_set_credits():
    if request.user['role'] not in ['admin', 'owner']:
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    data = request.json
    user_id = data.get('user_id')
    credits = data.get('credits', 0)

    database.update_user(user_id, {'credits': credits})
    return jsonify({'success': True})


# ============================================
# ===== OWNER ROUTES =====
# ============================================

@app.route('/api/owner/admins', methods=['POST'])
@require_auth
def owner_get_admins():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    admins = database.get_all_users(role='admin')
    safe_admins = []
    for a in admins:
        safe_admins.append({
            'id': a['id'],
            'username': a['username'],
            'nickname': a.get('nickname', ''),
            'status': a.get('status', 'active'),
            'avatar': a.get('avatar', '')
        })

    return jsonify({'success': True, 'admins': safe_admins})


@app.route('/api/owner/generate-admin-license', methods=['POST'])
@require_auth
def owner_generate_admin_license():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    license_key = license_manager.generate_license('admin', 999999)
    return jsonify({'success': True, 'license_key': license_key})


@app.route('/api/owner/generate-license', methods=['POST'])
@require_auth
def owner_generate_license():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    data = request.json
    license_type = data.get('type', 'user')
    credits = data.get('credits', 50)

    license_key = license_manager.generate_license(license_type, credits)
    return jsonify({'success': True, 'license_key': license_key})


@app.route('/api/owner/all-users', methods=['POST'])
@require_auth
def owner_get_all_users():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    users = database.get_all_users()
    safe_users = []
    for u in users:
        safe_users.append({
            'id': u['id'],
            'username': u['username'],
            'nickname': u.get('nickname', ''),
            'credits': u.get('credits', 0),
            'status': u.get('status', 'active'),
            'avatar': u.get('avatar', ''),
            'role': u.get('role', 'user')
        })

    return jsonify({'success': True, 'users': safe_users})


@app.route('/api/owner/user-action', methods=['POST'])
@require_auth
def owner_user_action():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    data = request.json
    user_id = data.get('user_id')
    action = data.get('action')

    if action == 'pause':
        database.update_user(user_id, {'status': 'paused'})
    elif action == 'resume':
        database.update_user(user_id, {'status': 'active'})
    elif action == 'delete':
        database.delete_user(user_id)
    else:
        return jsonify({'success': False, 'message': 'Invalid action!'})

    return jsonify({'success': True})


@app.route('/api/owner/set-credits', methods=['POST'])
@require_auth
def owner_set_credits():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    data = request.json
    user_id = data.get('user_id')
    credits = data.get('credits', 0)

    database.update_user(user_id, {'credits': credits})
    return jsonify({'success': True})


@app.route('/api/owner/licenses', methods=['POST'])
@require_auth
def owner_get_licenses():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    licenses = license_manager.get_all_licenses()
    return jsonify({'success': True, 'licenses': licenses})


@app.route('/api/owner/delete-license', methods=['POST'])
@require_auth
def owner_delete_license():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    data = request.json
    license_key = data.get('license_key')
    license_manager.delete_license(license_key)
    return jsonify({'success': True})


@app.route('/api/owner/stats', methods=['POST'])
@require_auth
def owner_stats():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    stats = database.get_global_stats()
    return jsonify({'success': True, **stats})


@app.route('/api/owner/send-notice', methods=['POST'])
@require_auth
def owner_send_notice():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    data = request.json
    notice = {
        'id': str(uuid.uuid4()),
        'title': data.get('title', ''),
        'message': data.get('message', ''),
        'date': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
        'active': True
    }

    database.save_notice(notice)
    return jsonify({'success': True})


@app.route('/api/owner/notices', methods=['POST'])
@require_auth
def owner_notices():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    notices = database.get_all_notices()
    return jsonify({'success': True, 'notices': notices})


@app.route('/api/owner/strategies', methods=['POST'])
@require_auth
def owner_get_strategies():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    strategies = database.get_strategies()
    return jsonify({'success': True, 'strategies': strategies})


@app.route('/api/owner/save-strategies', methods=['POST'])
@require_auth
def owner_save_strategies():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    data = request.json
    database.save_strategies(data.get('strategies', {}))
    return jsonify({'success': True})


@app.route('/api/owner/change-password', methods=['POST'])
@require_auth
def owner_change_password():
    if request.user['role'] != 'owner':
        return jsonify({'success': False, 'message': 'Unauthorized!'})

    data = request.json
    current = data.get('current_password', '')
    new_pass = data.get('new_password', '')

    global OWNER_PASSWORD
    if current != OWNER_PASSWORD:
        return jsonify({'success': False, 'message': 'Current password is wrong!'})

    OWNER_PASSWORD = new_pass
    os.environ['OWNER_PASSWORD'] = new_pass
    return jsonify({'success': True})


# ===== RUN =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
