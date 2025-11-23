import streamlit as st
from backend.config import USERS, SECRET_KEY
import hashlib
import secrets
from datetime import datetime, timedelta

SECRET_KEY = SECRET_KEY

def generate_secure_token(username):
    """Generate a secure token with timestamp"""
    timestamp = datetime.now().isoformat()
    data = f"{username}_{timestamp}_{SECRET_KEY}"
    return hashlib.sha256(data.encode()).hexdigest()

def verify_token(username, token, max_age_hours=24):
    """Verify token is valid and not expired"""
    try:
        # Simple verification (you can enhance this with actual timestamp checking)
        expected_token = hashlib.sha256(f"{username}_{SECRET_KEY}".encode()).hexdigest()
        return token == expected_token
    except:
        return False

def set_login_cookie(username):
    """Set login cookie in query params (Streamlit Cloud compatible)"""
    token = hashlib.sha256(f"{username}_{SECRET_KEY}".encode()).hexdigest()
    st.query_params["auth_user"] = username
    st.query_params["auth_token"] = token

def get_login_from_cookie():
    """Get login info from query params"""
    query_params = st.query_params
    
    if "auth_user" in query_params and "auth_token" in query_params:
        username = query_params["auth_user"]
        token = query_params["auth_token"]
        
        # Verify user exists and token is valid
        if username in USERS and verify_token(username, token):
            return username
    return None

def check_password():
    """Main authentication check"""
    
    # First check if already logged in via query params
    username = get_login_from_cookie()
    if username:
        st.session_state["password_correct"] = True
        st.session_state["logged_in_user"] = username
        return True
    
    # Then check session state
    if st.session_state.get("password_correct", False):
        # Session is valid but query params are missing, restore them
        if "logged_in_user" in st.session_state:
            set_login_cookie(st.session_state["logged_in_user"])
        return True

    # Show login form
    st.markdown("<h2 style='text-align: center;'>🔐 Login to KuberX</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        username_input = st.text_input("Username", key="username_input", max_chars=50)
        password_input = st.text_input("Password", type="password", key="password_input", max_chars=50)
        
        if st.button("Login", use_container_width=True, type="primary"):
            if username_input in USERS and USERS[username_input] == password_input:
                # Successful login
                st.session_state["password_correct"] = True
                st.session_state["logged_in_user"] = username_input
                
                # Set persistent cookie
                set_login_cookie(username_input)
                
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("😕 Username or password incorrect")
                return False
    
    if "login_error" in st.session_state:
        st.error(st.session_state["login_error"])
        del st.session_state["login_error"]
    
    return False