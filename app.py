import streamlit as st
from frontend.pages import add_record, search_records, last_records
from backend.auth import check_password

st.set_page_config(page_title="💰 KuberX", layout="wide")

if not check_password():
    st.stop()

st.sidebar.success(f"👤 Logged in as: **{st.session_state['logged_in_user']}**")

if st.sidebar.button("🚪 Logout"):
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Clear authentication token
    if "auth_token" in st.query_params:
        del st.query_params["auth_token"]
    
    st.rerun()

st.sidebar.markdown("---")

# Navigation based on user role
if st.session_state['logged_in_user'] == 'admin':
    page = st.sidebar.radio(
        "📋 Navigation", 
        ["🔍 Search Records", "➕ Add Record", "📚 Last 10 Records", "📊 Analytics", "📈 Interest Stats"]
    )
else:
    page = st.sidebar.radio(
        "📋 Navigation", 
        ["🔍 Search Records", "➕ Add Record", "📚 Last 10 Records"]
    )

# Page routing
if page == "➕ Add Record":
    add_record.render()
elif page == "🔍 Search Records":
    search_records.render()
elif page == "📚 Last 10 Records":
    last_records.render()
elif page == "📊 Analytics":
    from frontend.pages import metrics
    metrics.render()
elif page == "📈 Interest Stats":
    from frontend.pages import stats
    stats.render()