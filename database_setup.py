# ===== STRUGGLE AI - DATABASE SYSTEM =====
# JSON-based Database with Force Trade support
# database_setup.py

import json
import os
import datetime
from threading import Lock


class Database:
    """
    JSON-based Database
    - Users, Licenses, Notices
    - Strategies with Force Trade
    - Analytics tracking
    - Thread-safe
    """

    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.lock = Lock()

        os.makedirs(data_dir, exist_ok=True)

        self.files = {
            'users': os.path.join(data_dir, 'users.json'),
            'licenses': os.path.join(data_dir, 'licenses.json'),
            'notices': os.path.join(data_dir, 'notices.json'),
            'strategies': os.path.join(data_dir, 'strategies.json'),
            'owner': os.path.join(data_dir, 'owner.json'),
            'signals': os.path.join(data_dir, 'signals.json'),
            'analytics': os.path.join(data_dir, 'analytics.json')
        }

        self._init_files()

    def _init_files(self):
        """Initialize database files with defaults"""
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
                'exhaustion': True,
                'force_trade': False  # Default OFF
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
            else:
                # Ensure force_trade exists in strategies
                if key == 'strategies':
                    data = self._read(filepath) or {}
                    if 'force_trade' not in data:
                        data['force_trade'] = False
                        self._write(filepath, data)

    # ============================================
    # ===== FILE OPERATIONS =====
    # ============================================

    def _read(self, filepath):
        with self.lock:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return None

    def _write(self, filepath, data):
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
        users = self._read(self.files['users']) or []
        users.append(user_data)
        self._write(self.files['users'], users)

    def get_user(self, user_id):
        users = self._read(self.files['users']) or []
        for user in users:
            if user.get('id') == user_id:
                return user
        return None

    def get_user_by_username(self, username):
        users = self._read(self.files['users']) or []
        for user in users:
            if user.get('username', '').lower() == username.lower():
                return user
        return None

    def get_user_by_license(self, license_key):
        users = self._read(self.files['users']) or []
        for user in users:
            if user.get('license_key') == license_key:
                return user
        return None

    def username_exists(self, username):
        users = self._read(self.files['users']) or []
        for user in users:
            if user.get('username', '').lower() == username.lower():
                return True
        return False

    def update_user(self, user_id, updates):
        users = self._read(self.files['users']) or []
        for i, user in enumerate(users):
            if user.get('id') == user_id:
                users[i].update(updates)
                self._write(self.files['users'], users)
                return True
        return False

    def delete_user(self, user_id):
        users = self._read(self.files['users']) or []
        users = [u for u in users if u.get('id') != user_id]
        self._write(self.files['users'], users)

    def get_all_users(self, role=None):
        users = self._read(self.files['users']) or []
        if role:
            return [u for u in users if u.get('role') == role]
        return users

    # ============================================
    # ===== LICENSE OPERATIONS =====
    # ============================================

    def save_license(self, license_data):
        licenses = self._read(self.files['licenses']) or []
        licenses.append(license_data)
        self._write(self.files['licenses'], licenses)

    def get_license(self, license_key):
        licenses = self._read(self.files['licenses']) or []
        for lic in licenses:
            if lic.get('key') == license_key:
                return lic
        return None

    def license_exists(self, license_key):
        licenses = self._read(self.files['licenses']) or []
        for lic in licenses:
            if lic.get('key') == license_key:
                return True
        return False

    def update_license(self, license_key, updates):
        licenses = self._read(self.files['licenses']) or []
        for i, lic in enumerate(licenses):
            if lic.get('key') == license_key:
                licenses[i].update(updates)
                self._write(self.files['licenses'], licenses)
                return True
        return False

    def delete_license(self, license_key):
        licenses = self._read(self.files['licenses']) or []
        licenses = [l for l in licenses if l.get('key') != license_key]
        self._write(self.files['licenses'], licenses)

    def get_all_licenses(self):
        return self._read(self.files['licenses']) or []

    # ============================================
    # ===== ANALYSIS OPERATIONS =====
    # ============================================

    def add_analysis(self, user_id, analysis_data):
        users = self._read(self.files['users']) or []
        for i, user in enumerate(users):
            if user.get('id') == user_id:
                if 'analysis_history' not in users[i]:
                    users[i]['analysis_history'] = []

                users[i]['analysis_history'].insert(0, analysis_data)
                users[i]['analysis_history'] = users[i]['analysis_history'][:100]
                users[i]['analysis_count'] = users[i].get('analysis_count', 0) + 1

                self._write(self.files['users'], users)
                break

        self._update_analytics(analysis_data)

    def _update_analytics(self, analysis_data):
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
        signals = self._read(self.files['signals']) or {}
        signals[user_id] = signal_data
        self._write(self.files['signals'], signals)

    def get_last_signal(self, user_id):
        signals = self._read(self.files['signals']) or {}
        return signals.get(user_id)

    # ============================================
    # ===== STATS =====
    # ============================================

    def get_user_stats(self, user_id):
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
            'history': history[:20]
        }

    def get_global_stats(self):
        analytics = self._read(self.files['analytics']) or {}
        users = self._read(self.files['users']) or []

        today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        month = datetime.datetime.utcnow().strftime('%Y-%m')

        today_date = datetime.datetime.utcnow()
        week_start = (today_date - datetime.timedelta(days=today_date.weekday())).strftime('%Y-%m-%d')

        daily = analytics.get('daily', {})
        monthly = analytics.get('monthly', {})

        today_stats = daily.get(today, {'total': 0})
        month_stats = monthly.get(month, {'total': 0})

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
        notices = self._read(self.files['notices']) or []

        for i in range(len(notices)):
            notices[i]['active'] = False

        notices.insert(0, notice_data)
        notices = notices[:50]

        self._write(self.files['notices'], notices)

    def get_active_notice(self):
        notices = self._read(self.files['notices']) or []
        for notice in notices:
            if notice.get('active', False):
                return notice
        return None

    def get_all_notices(self):
        notices = self._read(self.files['notices']) or []
        return notices[:20]

    # ============================================
    # ===== STRATEGY OPERATIONS =====
    # ============================================

    def get_strategies(self):
        strategies = self._read(self.files['strategies']) or {}
        # Ensure force_trade key exists
        if 'force_trade' not in strategies:
            strategies['force_trade'] = False
            self._write(self.files['strategies'], strategies)
        return strategies

    def save_strategies(self, strategies):
        # Ensure force_trade is included
        current = self._read(self.files['strategies']) or {}
        current.update(strategies)
        if 'force_trade' not in current:
            current['force_trade'] = False
        self._write(self.files['strategies'], current)

    # ============================================
    # ===== OWNER DATA =====
    # ============================================

    def get_owner_data(self):
        return self._read(self.files['owner']) or {'nickname': 'Owner', 'avatar': ''}

    def update_owner_data(self, updates):
        data = self._read(self.files['owner']) or {}
        data.update(updates)
        self._write(self.files['owner'], data)


# ============================================
# ===== INIT FUNCTION =====
# ============================================

def init_db():
    """Initialize database"""
    db = Database()
    print("✅ Struggle AI Database initialized!")
    return db
