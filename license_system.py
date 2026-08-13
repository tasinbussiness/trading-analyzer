# ===== LICENSE MANAGEMENT SYSTEM =====
# license_system.py

import uuid
import string
import random
import datetime


class LicenseManager:
    """
    Secure License Key Management
    - Generate unique license keys
    - Validate licenses
    - Track usage
    - Different license types (user/admin)
    """

    def __init__(self, database):
        self.db = database
        self.prefix = {
            'user': 'USR',
            'admin': 'ADM'
        }

    # ============================================
    # ===== GENERATE LICENSE =====
    # ============================================

    def generate_license(self, license_type='user', credits=50):
        """
        Generate a unique license key
        Format: TYPE-XXXX-XXXX-XXXX-XXXX
        """
        prefix = self.prefix.get(license_type, 'USR')

        # Generate random segments
        segments = []
        chars = string.ascii_uppercase + string.digits
        for _ in range(4):
            segment = ''.join(random.choices(chars, k=4))
            segments.append(segment)

        license_key = f"{prefix}-{'-'.join(segments)}"

        # Ensure unique
        while self.db.license_exists(license_key):
            segments = []
            for _ in range(4):
                segment = ''.join(random.choices(chars, k=4))
                segments.append(segment)
            license_key = f"{prefix}-{'-'.join(segments)}"

        # Save to database
        license_data = {
            'key': license_key,
            'type': license_type,
            'status': 'unused',
            'credits': credits,
            'used_by': None,
            'created_at': datetime.datetime.utcnow().isoformat(),
            'used_at': None
        }

        self.db.save_license(license_data)
        return license_key

    # ============================================
    # ===== VALIDATE LICENSE =====
    # ============================================

    def validate_license(self, license_key):
        """
        Validate a license key
        Returns license info or None
        """
        if not license_key:
            return None

        # Check format
        if not self._validate_format(license_key):
            return None

        # Check in database
        license_data = self.db.get_license(license_key)
        if not license_data:
            return None

        return license_data

    def _validate_format(self, license_key):
        """Check if license key format is valid"""
        parts = license_key.split('-')

        # Should have 5 parts: PREFIX-XXXX-XXXX-XXXX-XXXX
        if len(parts) != 5:
            return False

        # First part should be prefix
        if parts[0] not in ['USR', 'ADM']:
            return False

        # Each segment should be 4 characters
        for part in parts[1:]:
            if len(part) != 4:
                return False
            if not all(c in string.ascii_uppercase + string.digits for c in part):
                return False

        return True

    # ============================================
    # ===== USE LICENSE =====
    # ============================================

    def use_license(self, license_key, username):
        """Mark a license as used"""
        self.db.update_license(license_key, {
            'status': 'used',
            'used_by': username,
            'used_at': datetime.datetime.utcnow().isoformat()
        })

    # ============================================
    # ===== GET ALL LICENSES =====
    # ============================================

    def get_all_licenses(self):
        """Get all licenses"""
        return self.db.get_all_licenses()

    # ============================================
    # ===== DELETE LICENSE =====
    # ============================================

    def delete_license(self, license_key):
        """Delete a license"""
        self.db.delete_license(license_key)

    # ============================================
    # ===== BATCH GENERATE =====
    # ============================================

    def batch_generate(self, license_type='user', credits=50, count=5):
        """Generate multiple license keys at once"""
        keys = []
        for _ in range(count):
            key = self.generate_license(license_type, credits)
            keys.append(key)
        return keys