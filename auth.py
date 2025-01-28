import streamlit as st
import hashlib
import hmac
from database import Database

class Auth:
    def __init__(self):
        self.db = Database()

    def hash_password(self, password):
        """Create a secure hash of the password"""
        salt = b"secure_salt_value"  # In production, use a proper salt
        return hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt, 
            100000
        ).hex()

    def login_user(self, username, password):
        """Verify user credentials and log them in"""
        user = self.db.get_user(username)
        if user and hmac.compare_digest(
            user['password_hash'],
            self.hash_password(password)
        ):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            return True
        return False

    def register_user(self, username, password):
        """Register a new user"""
        if not username or not password:
            return False, "Username and password are required"
        
        try:
            password_hash = self.hash_password(password)
            self.db.add_user(username, password_hash)
            return True, "Registration successful"
        except Exception as e:
            return False, "Username already exists"

    def logout_user(self):
        """Log out the current user"""
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
