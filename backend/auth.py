import streamlit as st
from backend.config import USERS, SECRET_KEY
import hashlib
from datetime import datetime, timedelta
import base64
import json

# Secret key for token generation (IMPORTANT: Change this to a random string)
SECRET_KEY = "CHANGE_THIS_TO_RANDOM_STRING_IN_PRODUCTION"

# Token expiry: 200 days
TOKEN_EXPIRY_DAYS = 200

def generate_secure_token(username):
    """Generate a secure token with timestamp"""
    expiry_date = datetime.now() + timedelta(days=TOKEN_EXPIRY_DAYS)
    
    # Create token data
    token_data = {
        "username": username,
        "expiry": expiry_date.isoformat()
    }
    
    # Encode token data
    token_json = json.dumps(token_data)
    token_b64 = base64.b64encode(token_json.encode()).decode()
    
    # Create signature
    signature = hashlib.sha256(f"{token_b64}_{SECRET_KEY}".encode()).hexdigest()
    
    return f"{token_b64}.{signature}"

def verify_token(token):
    """Verify token is valid and not expired"""
    try:
        # Split token and signature
        token_b64, signature = token.split(".")
        
        # Verify signature
        expected_signature = hashlib.sha256(f"{token_b64}_{SECRET_KEY}".encode()).hexdigest()
        if signature != expected_signature:
            return None
        
        # Decode token data
        token_json = base64.b64decode(token_b64).decode()
        token_data = json.loads(token_json)
        
        # Check expiry
        expiry_date = datetime.fromisoformat(token_data["expiry"])
        if datetime.now() > expiry_date:
            return None
        
        # Check if user still exists
        username = token_data["username"]
        if username not in USERS:
            return None
        
        return username
    except:
        return None

def set_login_cookie(username):
    """Set login cookie in query params (Streamlit Cloud compatible)"""
    token = generate_secure_token(username)
    st.query_params["auth_token"] = token

def get_login_from_cookie():
    """Get login info from query params"""
    query_params = st.query_params
    
    if "auth_token" in query_params:
        token = query_params["auth_token"]
        username = verify_token(token)
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