import streamlit as st
from frontend.pages import add_record, search_records, last_records
from backend.auth import check_password

st.set_page_config(page_title="💰 KuberX", layout="wide")

if not check_password():
    st.stop()

st.sidebar.success(f"👤 Logged in as: **{st.session_state['logged_in_user']}**")

if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.markdown("---")

    # Add after the existing page radio
if st.session_state['logged_in_user'] == 'admin':
    page = st.sidebar.radio("📋 Navigation", ["🔍 Search Records", "➕ Add Record", "📚 Last 10 Records", "📊 Analytics"])
else:
    page = st.sidebar.radio("📋 Navigation", ["🔍 Search Records", "➕ Add Record", "📚 Last 10 Records"])

if page == "➕ Add Record":
    add_record.render()
elif page == "🔍 Search Records":
    search_records.render()
elif page == "📚 Last 10 Records":
    last_records.render()
# Then add this in the page routing section
elif page == "📊 Analytics":
    from frontend.pages import metrics
    metrics.render()

# Custom CSS to hide elements
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stToolbar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)