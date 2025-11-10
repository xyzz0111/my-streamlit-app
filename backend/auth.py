import streamlit as st
from backend.config import USERS

def check_password():
    def password_entered():
        # Add safety check for USERS
        if USERS is None:
            st.error("⚠️ Configuration error: User database not loaded")
            st.session_state["password_correct"] = False
            return
            
        if st.session_state["username"] in USERS and USERS[st.session_state["username"]] == st.session_state["password"]:
            st.session_state["password_correct"] = True
            st.session_state["logged_in_user"] = st.session_state["username"]
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.markdown("<h2 style='text-align: center;'>🔐 Login to KuberX</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.text_input("Username", key="username", max_chars=50)
        st.text_input("Password", type="password", key="password", max_chars=50)
        st.button("Login", on_click=password_entered, use_container_width=True, type="primary")
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Username or password incorrect")
    
    return False