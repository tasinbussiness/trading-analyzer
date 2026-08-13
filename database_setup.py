# ===== DATABASE SYSTEM =====
# JSON-based database (works without external DB)
# Can be replaced with Supabase later
# database_setup.py

import json
import os
import datetime
from threading import Lock


class Database:
    """
    Simple JSON-based Database
    - Users management
    - License storage
    - Analysis records
    - Notices
    - Strategy settings
    - Thread-safe operations
    """

    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.lock = Lock()

        # Create data directory
        os.makedirs(data_dir, exist_ok=True)

        # Database files
        self.files = {
            'users': os.path.join(data_dir, 'users.json'),
            'licenses': os.path.join(data_dir, 'licenses.json'),
            'notices': os.path.join(data_dir, 'notices.json'),
            'strategies': os.path.join(data_dir, 'strategies.json'),
            'owner': os.path.join(data_dir, 'owner.json'),
            'signals': os.path.join(data_dir, 'signals.json'),
            'analytics': os.path.join(data_dir, 'analytics.json')
        }

        # Initialize files
        self._init_files()

    def _init_files(self):
        """Initialize database files if they don't exist"""
        defaults = {
            'users': [],
            'licenses': [],
            'notices': [],
            'strategies': {
                'trend_following': True,
                'rsi_reversal': True,
                'momentum': True,
                'pattern_recognition': True,
                'volume_strength': True,
                'ma_crossover': True,
                'support_resistance': True,
                'breakout': True,
                'liquidity_grab': True,
                'trend_pullback': True,
                'multi_timeframe': True,
                'candle_rejection': True,
                'range_scalping': True,
                'volatility_filter': True,
                'smart_doji': True,
                'exhaustion': True
            },
            'owner': {
                'nickname': 'Owner',
                'avatar': ''
            },
            'signals': {},
            'analytics': {
                'total_analysis': 0,
                'total_buy': 0,
                'total_sell': 0,
                'total_avoid': 0,
                'daily': {},
                'monthly': {}
            }
        }

        for key, filepath in self.files.items():
            if not os.path.exists(filepath):
                self._write(filepath, defaults.get(key, {}))

    # ============================================
    # ===== FILE OPERATIONS =====
    # ============================================

    def _read(self, filepath):
        """Read JSON file"""
        with self.lock:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return None

    def _write(self, filepath, data):
        """Write JSON file"""
        with self.lock:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"Database write error: {e}")
                return False

    # ============================================
    # ===== USER OPERATIONS =====
    # ============================================

    def create_user(self, user_data):
        """Create a new user"""
        users = self._read(self.files['users']) or []
        users.append(user_data)
        self._write(self.files['users'], users)

    def get_user(self, user_id):
        """Get user by ID"""
        users = self._read(self.files['users']) or []
        for user in users:
            if user.get('id') == user_id:
                return user
        return None

    def get_user_by_username(self, username):
        """Get user by username"""
        users = self._read(self.files['users']) or []
        for user in users:
            if user.get('username', '').lower() == username.lower():
                return user
        return None

    def get_user_by_license(self, license_key):
        """Get user by license key"""
        users = self._read(self.files['users']) or []
        for user in users:
            if user.get('license_key') == license_key:
                return user
        return None

    def username_exists(self, username):
        """Check if username already exists"""
        users = self._read(self.files['users']) or []
        for user in users:
            if user.get('username', '').lower() == username.lower():
                return True
        return False

    def update_user(self, user_id, updates):
        """Update user data"""
        users = self._read(self.files['users']) or []
        for i, user in enumerate(users):
            if user.get('id') == user_id:
                users[i].update(updates)
                self._write(self.files['users'], users)
                return True
        return False

    def delete_user(self, user_id):
        """Delete a user"""
        users = self._read(self.files['users']) or []
        users = [u for u in users if u.get('id') != user_id]
        self._write(self.files['users'], users)

    def get_all_users(self, role=None):
        """Get all users, optionally filtered by role"""
        users = self._read(self.files['users']) or []
        if role:
            return [u for u in users if u.get('role') == role]
        return users

    # ============================================
    # ===== LICENSE OPERATIONS =====
    # ============================================

    def save_license(self, license_data):
        """Save a new license"""
        licenses = self._read(self.files['licenses']) or []
        licenses.append(license_data)
        self._write(self.files['licenses'], licenses)

    def get_license(self, license_key):
        """Get license by key"""
        licenses = self._read(self.files['licenses']) or []
        for lic in licenses:
            if lic.get('key') == license_key:
                return lic
        return None

    def license_exists(self, license_key):
        """Check if license key exists"""
        licenses = self._read(self.files['licenses']) or []
        for lic in licenses:
            if lic.get('key') == license_key:
                return True
        return False

    def update_license(self, license_key, updates):
        """Update license data"""
        licenses = self._read(self.files['licenses']) or []
        for i, lic in enumerate(licenses):
            if lic.get('key') == license_key:
                licenses[i].update(updates)
                self._write(self.files['licenses'], licenses)
                return True
        return False

    def delete_license(self, license_key):
        """Delete a license"""
        licenses = self._read(self.files['licenses']) or []
        licenses = [l for l in licenses if l.get('key') != license_key]
        self._write(self.files['licenses'], licenses)

    def get_all_licenses(self):
        """Get all licenses"""
        return self._read(self.files['licenses']) or []

    # ============================================
    # ===== ANALYSIS OPERATIONS =====
    # ============================================

    def add_analysis(self, user_id, analysis_data):
        """Add analysis record for a user"""
        # Update user history
        users = self._read(self.files['users']) or []
        for i, user in enumerate(users):
            if user.get('id') == user_id:
                if 'analysis_history' not in users[i]:
                    users[i]['analysis_history'] = []

                users[i]['analysis_history'].insert(0, analysis_data)

                # Keep last 100 records
                users[i]['analysis_history'] = users[i]['analysis_history'][:100]

                # Update count
                users[i]['analysis_count'] = users[i].get('analysis_count', 0) + 1

                self._write(self.files['users'], users)
                break

        # Update global analytics
        self._update_analytics(analysis_data)

    def _update_analytics(self, analysis_data):
        """Update global analytics"""
        analytics = self._read(self.files['analytics']) or {
            'total_analysis': 0,
            'total_buy': 0,
            'total_sell': 0,
            'total_avoid': 0,
            'daily': {},
            'monthly': {}
        }

        analytics['total_analysis'] += 1

        signal = analysis_data.get('signal', 'AVOID')
        if 'BUY' in signal:
            analytics['total_buy'] += 1
        elif 'SELL' in signal:
            analytics['total_sell'] += 1
        else:
            analytics['total_avoid'] += 1

        # Daily tracking
        today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        if today not in analytics['daily']:
            analytics['daily'][today] = {'total': 0, 'buy': 0, 'sell': 0, 'avoid': 0}

        analytics['daily'][today]['total'] += 1
        if 'BUY' in signal:
            analytics['daily'][today]['buy'] += 1
        elif 'SELL' in signal:
            analytics['daily'][today]['sell'] += 1
        else:
            analytics['daily'][today]['avoid'] += 1

        # Monthly tracking
        month = datetime.datetime.utcnow().strftime('%Y-%m')
        if month not in analytics['monthly']:
            analytics['monthly'][month] = {'total': 0, 'buy': 0, 'sell': 0, 'avoid': 0}

        analytics['monthly'][month]['total'] += 1
        if 'BUY' in signal:
            analytics['monthly'][month]['buy'] += 1
        elif 'SELL' in signal:
            analytics['monthly'][month]['sell'] += 1
        else:
            analytics['monthly'][month]['avoid'] += 1

        self._write(self.files['analytics'], analytics)

    # ============================================
    # ===== SIGNAL CACHE =====
    # ============================================

    def save_last_signal(self, user_id, signal_data):
        """Save last signal for same-chart detection"""
        signals = self._read(self.files['signals']) or {}
        signals[user_id] = signal_data
        self._write(self.files['signals'], signals)

    def get_last_signal(self, user_id):
        """Get last signal for a user"""
        signals = self._read(self.files['signals']) or {}
        return signals.get(user_id)

    # ============================================
    # ===== STATS =====
    # ============================================

    def get_user_stats(self, user_id):
        """Get stats for a specific user"""
        user = self.get_user(user_id)
        if not user:
            return {
                'total': 0, 'today': 0, 'month': 0,
                'avoid': 0, 'up': 0, 'down': 0,
                'history': []
            }

        history = user.get('analysis_history', [])
        today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        month = datetime.datetime.utcnow().strftime('%Y-%m')

        today_count = sum(1 for h in history if h.get('date', '').startswith(today))
        month_count = sum(1 for h in history if h.get('date', '').startswith(month))
        avoid_count = sum(1 for h in history if 'AVOID' in h.get('signal', ''))
        up_count = sum(1 for h in history if 'BUY' in h.get('signal', ''))
        down_count = sum(1 for h in history if 'SELL' in h.get('signal', ''))

        return {
            'total': user.get('analysis_count', 0),
            'today': today_count,
            'month': month_count,
            'avoid': avoid_count,
            'up': up_count,
            'down': down_count,
            'history': history[:20]  # Last 20
        }

    def get_global_stats(self):
        """Get global stats for owner"""
        analytics = self._read(self.files['analytics']) or {}
        users = self._read(self.files['users']) or []

        today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        month = datetime.datetime.utcnow().strftime('%Y-%m')

        # Calculate week
        today_date = datetime.datetime.utcnow()
        week_start = (today_date - datetime.timedelta(days=today_date.weekday())).strftime('%Y-%m-%d')

        daily = analytics.get('daily', {})
        monthly = analytics.get('monthly', {})

        today_stats = daily.get(today, {'total': 0})
        month_stats = monthly.get(month, {'total': 0})

        # Week calculation
        week_total = 0
        for date_str, data in daily.items():
            if date_str >= week_start:
                week_total += data.get('total', 0)

        return {
            'total': analytics.get('total_analysis', 0),
            'today': today_stats.get('total', 0),
            'week': week_total,
            'month': month_stats.get('total', 0),
            'up': analytics.get('total_buy', 0),
            'down': analytics.get('total_sell', 0),
            'avoid': analytics.get('total_avoid', 0),
            'total_users': len(users)
        }

    # ============================================
    # ===== NOTICE OPERATIONS =====
    # ============================================

    def save_notice(self, notice_data):
        """Save a new notice"""
        notices = self._read(self.files['notices']) or []

        # Deactivate old notices
        for i in range(len(notices)):
            notices[i]['active'] = False

        notices.insert(0, notice_data)

        # Keep last 50 notices
        notices = notices[:50]

        self._write(self.files['notices'], notices)

    def get_active_notice(self):
        """Get the current active notice"""
        notices = self._read(self.files['notices']) or []
        for notice in notices:
            if notice.get('active', False):
                return notice
        return None

    def get_all_notices(self):
        """Get all notices"""
        notices = self._read(self.files['notices']) or []
        return notices[:20]  # Last 20

    # ============================================
    # ===== STRATEGY OPERATIONS =====
    # ============================================

    def get_strategies(self):
        """Get current strategy settings"""
        return self._read(self.files['strategies']) or {}

    def save_strategies(self, strategies):
        """Save strategy settings"""
        self._write(self.files['strategies'], strategies)

    # ============================================
    # ===== OWNER DATA =====
    # ============================================

    def get_owner_data(self):
        """Get owner profile data"""
        return self._read(self.files['owner']) or {'nickname': 'Owner', 'avatar': ''}

    def update_owner_data(self, updates):
        """Update owner data"""
        data = self._read(self.files['owner']) or {}
        data.update(updates)
        self._write(self.files['owner'], data)


# ============================================
# ===== INIT FUNCTION =====
# ============================================

def init_db():
    """Initialize and return database instance"""
    db = Database()
    print("✅ Database initialized successfully!")
    return db